import csv
import os

CSV_FILE = r"Структура _Ultimate.csv"


def main():
    if not os.path.exists(CSV_FILE):
        print("CSV not found.")
        return

    # Read all rows
    with open(CSV_FILE, encoding="utf-8") as f:
        reader = csv.reader(f)
        list(reader)

    # We will build a simple state machine to process rows
    # But since we just need to move items around, maybe parsing to objects is better again?
    # No, let's use the object approach from previous script but refined for this specific fix.
    # Actually, reusing the previous script's logic is best, just adding the granular keyword moving.

    # ... Or I can just write a specific patch using the Node class again.
    # It's cleaner. Copy-paste the Node/Parse logic.
    pass


class Node:
    def __init__(self, type, name, info=""):
        self.type = type
        self.name = name.strip()
        self.info = info
        self.children = []
        self.parent = None
        self.volume = ""

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def remove_child(self, node):
        if node in self.children:
            self.children.remove(node)
            node.parent = None


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
            col1, col2, col3 = (
                (row[0].strip(), row[1].strip(), row[2].strip())
                if len(row) >= 3
                else (row[0] if len(row) > 0 else "", row[1] if len(row) > 1 else "", "")
            )

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
                if is_kw:
                    kw = Node("Keyword", col1, col3)
                    if current_block:
                        current_block.add_child(kw)
                    elif current_l2:
                        current_l2.add_child(kw)
                else:
                    # Cluster Header
                    if col1:
                        current_block = Node("Cluster", col1, col2)
                        if current_l2:
                            current_l2.add_child(current_block)

    return root


def find_node(root, type, name):
    if root.type == type and root.name == name:
        return root
    for c in root.children:
        res = find_node(c, type, name)
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
                # Write special clusters at root level or similar
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


def refine(root):
    # 1. Clean Empty Clusters in Equipment (Главная, Опт)
    equip = find_node(root, "L2", "Оборудование")
    if equip:
        to_remove = []
        for c in equip.children:
            if c.type == "Cluster" and c.name in ["Главная", "Опт"] and not c.children:
                to_remove.append(c)
        for c in to_remove:
            equip.remove_child(c)
            print(f"Removed empty cluster: {c.name}")

    # 2. Distribute 'Наборы' keywords
    # Target L2
    acc_l1 = find_node(root, "L1", "Аксессуары")
    nabor_l2 = find_node(acc_l1, "L2", "Наборы") if acc_l1 else None

    if equip and nabor_l2:
        nabor_cluster = find_node(equip, "Cluster", "Наборы")
        if nabor_cluster:
            keywords = [k for k in nabor_cluster.children if k.type == "Keyword"]

            # Map targets in L2 Sets
            targets = {
                "химчист": find_node(nabor_l2, "L3", "Наборы для химчистки"),
                "полиров": find_node(nabor_l2, "L3", "Наборы для полировки"),
                "кож": find_node(nabor_l2, "L3", "Наборы для ухода за кожей"),
                "подаро": find_node(nabor_l2, "L3", "Подарочные наборы"),
                "детейл": find_node(nabor_l2, "L3", "Наборы для салона"),  # or separate?
                "default": find_node(nabor_l2, "L3", "Наборы для мойки"),
            }

            # Create if missing (simplified, assuming they exist from previous script)
            # Actually some might be L3, some Patterns.

            count = 0
            for kw in keywords:
                text = kw.name.lower()
                target_node = targets["default"]

                if "химчист" in text:
                    target_node = targets["химчист"]
                elif "полиров" in text:
                    target_node = targets["полиров"]
                elif "кож" in text:
                    target_node = targets["кож"]
                elif "подаро" in text:
                    target_node = targets["подаро"]
                elif "салон" in text or "детейл" in text:
                    target_node = targets["детейл"]

                if target_node:
                    nabor_cluster.remove_child(kw)
                    target_node.add_child(kw)
                    count += 1

            print(f"Moved {count} keywords from Equipment/Наборы to Accessories/Sets")

            if not nabor_cluster.children:
                equip.remove_child(nabor_cluster)
                print("Removed empty Equipment/Наборы cluster")


if __name__ == "__main__":
    print("Patching...")
    root = parse_csv(CSV_FILE)
    refine(root)
    write_csv(root, CSV_FILE)
    print("Done.")
