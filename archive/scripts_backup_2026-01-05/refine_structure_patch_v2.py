import csv

CSV_FILE = r"Структура _Ultimate.csv"


class Node:
    def __init__(self, type, name, info=""):
        self.type = type
        self.name = name.strip()
        self.info = info
        self.children = []
        self.parent = None

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def remove_child(self, node):
        if node in self.children:
            self.children.remove(node)
            node.parent = None

    def get_all_keywords(self):
        kws = []
        if self.type == "Keyword":
            kws.append(self)
        for c in self.children:
            kws.extend(c.get_all_keywords())
        return kws


def parse_csv(filepath):
    root = Node("Root", "Root")
    current_l1 = None
    current_l2 = None
    current_block = None

    with open(filepath, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if not row:
                continue
            col1 = row[0].strip() if len(row) > 0 else ""
            col2 = row[1].strip() if len(row) > 1 else ""
            col3 = row[2].strip() if len(row) > 2 else ""

            if not col1 and not col2 and not col3:
                continue

            if col1.startswith("L1:"):
                current_l1 = Node("L1", col1[3:].strip(), col2)
                root.add_child(current_l1)
                current_l2 = None
                current_block = None
            elif col1.startswith("L2:"):
                current_l2 = Node("L2", col1[3:].strip(), col2)
                if current_l1:
                    current_l1.add_child(current_l2)
                current_block = current_l2
            elif col1.startswith("L3:"):
                current_block = Node("L3", col1[3:].strip(), col2)
                if current_l2:
                    current_l2.add_child(current_block)
            elif col1.startswith("SEO-Фильтр:") or col1.startswith("Filter:"):
                current_block = Node("Filter", col1.split(":")[1].strip(), col2)
                if current_l2:
                    current_l2.add_child(current_block)
            else:
                # Keyword or Cluster
                # If col3 has digit or (col1 and not col2 and current_block is L3/Filter/Cluster)
                is_kw = col3 and any(c.isdigit() for c in col3)

                # Special case: if line has text in col1, nothing else, and next lines are keywords -> Cluster Header
                # But here we parse line by line.
                # Heuristic: If col3 is empty and col1 is present -> likely Cluster or L3/Filter without prefix if we missed it.
                # But if it's a keyword with 0 volume?
                # Let's assume if col2 has 'Cluster' info or implicit.
                # The file format usually has volume in col2 for clusters? No, col2 for nodes is Info/Count.

                if is_kw:
                    kw = Node("Keyword", col1, col3)
                    if current_block:
                        current_block.add_child(kw)
                    elif current_l2:
                        current_l2.add_child(kw)
                else:
                    # Likely a Cluster Header
                    if col1:
                        current_block = Node("Cluster", col1, col2)
                        if current_l2:
                            current_l2.add_child(current_block)
    return root


def find_node_recursive(root, type=None, name=None):
    if (type is None or root.type == type) and (name is None or root.name == name):
        return root
    for c in root.children:
        res = find_node_recursive(c, type, name)
        if res:
            return res
    return None


def write_csv(root, filepath):
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Фраза", "кол-во", "Запросы сред. [GA]"])

        for l1 in root.children:
            if l1.type == "L1":
                writer.writerow([])
                writer.writerow([f"L1: {l1.name}", l1.info, ""])
                writer.writerow([])
                write_children(writer, l1)
            elif l1.type == "Special":
                writer.writerow([])
                writer.writerow([l1.name, l1.info, ""])
                for k in l1.children:
                    writer.writerow([k.name, "", k.info])


def write_children(writer, node):
    for child in node.children:
        if child.type == "L2":
            writer.writerow([f"L2: {child.name}", child.info, ""])
            writer.writerow([])
            write_children(writer, child)
        elif child.type in ["L3", "Filter", "Cluster"]:
            prefix = "L3: " if child.type == "L3" else ("SEO-Фильтр: " if child.type == "Filter" else "")
            writer.writerow([f"{prefix}{child.name}", child.info, ""])
            write_children(writer, child)
        elif child.type == "Keyword":
            writer.writerow([child.name, "", child.info])


def main():
    print("Parsing CSV...")
    root = parse_csv(CSV_FILE)

    # Debug: Print structure of Equipment
    equip = find_node_recursive(root, "L2", "Оборудование")
    if equip:
        print(f"Found L2: Оборудование. Children: {[c.name for c in equip.children]}")
        # Identify the 'Наборы' cluster
        nabor_cluster = None
        for c in equip.children:
            if c.name.lower() == "наборы":
                nabor_cluster = c
                break

        if nabor_cluster:
            print(f"Found Cluster: Наборы with {len(nabor_cluster.children)} items")

            # Find destination L2: Наборы (or Наборы для детейлинга)
            sets_l2 = find_node_recursive(root, "L2", "Наборы")
            if not sets_l2:
                sets_l2 = find_node_recursive(root, "L2", "Наборы для детейлинга")
                if sets_l2:
                    print("Renaming 'Наборы для детейлинга' to 'Наборы'")
                    sets_l2.name = "Наборы"

            if sets_l2:
                # Distribute keywords
                keywords = nabor_cluster.get_all_keywords()
                print(f"Distributing {len(keywords)} keywords from Equipment/Наборы...")

                targets = {
                    "химчист": "Наборы для химчистки",
                    "полиров": "Наборы для полировки",
                    "кож": "Наборы для ухода за кожей",
                    "подаро": "Подарочные наборы",
                    "детейл": "Наборы для салона",
                    "салон": "Наборы для салона",
                    "default": "Наборы для мойки",
                }

                # Helper to get or create L3
                def get_or_create_l3(parent, name):
                    for c in parent.children:
                        if c.type == "L3" and c.name == name:
                            return c
                    node = Node("L3", name)
                    parent.add_child(node)
                    return node

                moved_count = 0
                for kw in keywords:
                    text = kw.name.lower()
                    target_name = targets["default"]  # default

                    if "химчист" in text:
                        target_name = targets["химчист"]
                    elif "полиров" in text:
                        target_name = targets["полиров"]
                    elif "кож" in text:
                        target_name = targets["кож"]
                    elif "подаро" in text:
                        target_name = targets["подаро"]
                    elif "детейл" in text or "салон" in text:
                        target_name = targets["детейл"]

                    target_node = get_or_create_l3(sets_l2, target_name)

                    # Remove from old parent
                    kw.parent.remove_child(kw)
                    # Add to new
                    target_node.add_child(kw)
                    moved_count += 1

                print(f"Moved {moved_count} keywords.")

                # Check if cluster is empty and remove
                if not nabor_cluster.children:
                    equip.remove_child(nabor_cluster)
                    print("Removed empty source cluster")
            else:
                print("Error: Target L2: Наборы not found.")
        else:
            print("Cluster 'Наборы' not found in Equipment.")

    print("Writing CSV...")
    write_csv(root, CSV_FILE)
    print("Done.")


if __name__ == "__main__":
    main()
