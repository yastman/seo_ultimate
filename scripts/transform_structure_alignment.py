import csv
import os
import re

INPUT_FILE = r"Структура _Ultimate.csv"
BACKUP_FILE = r"Структура _Ultimate_backup.csv"
OUTPUT_FILE = r"Структура _Ultimate.csv"


class Node:
    def __init__(self, type, name, info=""):
        self.type = type  # 'L1', 'L2', 'L3', 'Filter', 'Cluster', 'Keyword', 'Special'
        self.name = name.strip()
        self.info = info  # Col2 value for headers, Volume for keywords
        self.children = []  # List of Nodes or Keywords (as Nodes)
        self.parent = None
        self.volume = ""  # Helper

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def remove_child(self, node):
        if node in self.children:
            self.children.remove(node)
            node.parent = None

    def __repr__(self):
        return f"<{self.type}: {self.name}>"


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

            # Check for L1
            if col1.startswith("L1:"):
                current_l1 = Node("L1", col1[3:].strip(), col2)
                root.add_child(current_l1)
                current_l2 = None
                current_block = None
                continue

            # Check for L2
            if col1.startswith("L2:"):
                current_l2 = Node("L2", col1[3:].strip(), col2)
                if current_l1:
                    current_l1.add_child(current_l2)
                else:
                    root.add_child(current_l2)
                current_block = current_l2
                continue

            # Check for L3
            if col1.startswith("L3:"):
                node = Node("L3", col1[3:].strip(), col2)
                if current_l2:
                    current_l2.add_child(node)
                current_block = node
                continue

            # Check for Filter
            if col1.startswith("SEO-Фильтр:") or col1.startswith("Filter:"):
                name = col1.replace("SEO-Фильтр:", "").replace("Filter:", "").strip()
                node = Node("Filter", name, col2)
                if current_l2:
                    current_l2.add_child(node)
                current_block = node
                continue

            # Check for Keyword (Empty Col2, Val in Col3)
            # OR Check for Cluster Header (Val in Col2 OR Col1 has text and Col3 empty)
            is_keyword = False
            if col3 and any(c.isdigit() for c in col3):
                is_keyword = True
            elif (
                col1 and not col2 and not col3 and current_block and current_block.type == "Keyword"
            ):
                # Heuristic for cases where col3 might be missing but it looks like keyword flow
                is_keyword = True

            if is_keyword:
                kw_node = Node("Keyword", col1, col3)
                if current_block:
                    current_block.add_child(kw_node)
                elif current_l2:
                    current_l2.add_child(kw_node)
            else:
                # It's a Cluster Header
                if col1:
                    node = Node("Cluster", col1, col2)
                    if current_l2:
                        current_l2.add_child(node)
                    current_block = node

    return root


def find_node(root, type, name_pattern, parent_name_pattern=None):
    """Recursive find first node matching info."""
    if (
        root.type == type
        and (name_pattern in root.name)
        and (not parent_name_pattern or (root.parent and parent_name_pattern in root.parent.name))
    ):
        return root

    for child in root.children:
        res = find_node(child, type, name_pattern, parent_name_pattern)
        if res:
            return res
    return None


def find_nodes(root, type, name_pattern):
    """Recursive find all nodes matching."""
    res = []
    if root.type == type and re.search(name_pattern, root.name, re.IGNORECASE):
        res.append(root)
    for child in root.children:
        res.extend(find_nodes(child, type, name_pattern))
    return res


def move_keywords(source, target):
    """Moves all keywords from source node to target node."""
    to_move = [c for c in source.children if c.type == "Keyword"]
    for kw in to_move:
        source.remove_child(kw)
        target.add_child(kw)


def transform_structure(root):
    # ==========================
    # 1. SPECIALS & EQUIPMENT
    # ==========================
    equip_l2 = find_node(root, "L2", "Оборудование")
    if equip_l2:
        # Move 'Главная' cluster
        glavnaya = find_node(equip_l2, "Cluster", "Главная")
        if glavnaya:
            equip_l2.remove_child(glavnaya)
            glavnaya.type = "Special"
            root.add_child(glavnaya)

        # Move 'Опт' cluster
        opt = find_node(equip_l2, "Cluster", "Опт")
        if opt:
            equip_l2.remove_child(opt)
            opt.type = "Special"
            root.add_child(opt)

    # ==========================
    # 2. CREATE L2: НАБОРЫ
    # ==========================
    access_l1 = find_node(root, "L1", "Аксессуары")
    if access_l1:
        nabor_l2 = find_node(access_l1, "L2", "Наборы")
        if not nabor_l2:
            nabor_l2 = Node("L2", "Наборы", "")
            access_l1.add_child(nabor_l2)
    else:
        nabor_l2 = None

    # ==========================
    # 3. RELOCATE CLUSTERS TO SETS
    # ==========================
    if equip_l2 and nabor_l2:
        set_moves = [
            ("Набор для химчистки", "Наборы для салона"),
            ("Наборы для детейлинга", "Наборы для салона"),
            ("Набор для уборки", "Наборы для мойки"),
            ("Набор для мойки", "Наборы для мойки"),
            ("Подарочные наборы", "Подарочный"),  # Filter
        ]
        for pattern, target_name in set_moves:
            found_clusters = find_nodes(equip_l2, "Cluster", pattern)
            for clust in found_clusters:
                target_type = "Filter" if target_name == "Подарочный" else "L3"

                target_node = None
                for child in nabor_l2.children:
                    if child.type == target_type and child.name == target_name:
                        target_node = child
                        break

                if not target_node:
                    target_node = Node(target_type, target_name, "")
                    nabor_l2.add_child(target_node)

                move_keywords(clust, target_node)
                equip_l2.remove_child(clust)

    # ==========================
    # 4. CREATE L2: INTERIOR CLEANING
    # ==========================
    inter_l1 = find_node(root, "L1", "интерьер")
    if inter_l1:
        clean_l2 = find_node(inter_l1, "L2", "Для химчистки салона")
        if not clean_l2:
            clean_l2 = Node("L2", "Для химчистки салона", "")
            # Insert after General L1 if possible, or just append
            inter_l1.add_child(clean_l2)

        # Find 'Пятновыводители' in 'Нейтрализаторы' (L2) or check global L3
        # First check if it is already L3 or Cluster
        # Logic: find node named 'Пятновыводители' anywhere in Interior L1
        spots_node = find_node(inter_l1, "Cluster", "Пятновыводители")
        if not spots_node:
            spots_node = find_node(inter_l1, "L3", "Пятновыводители")

        if spots_node:
            # Move to new L2
            if spots_node.parent:
                spots_node.parent.remove_child(spots_node)
            clean_l2.add_child(spots_node)
            spots_node.type = "L3"  # Ensure type is L3

        # Also rename 'Пятновыводители' to 'L3: Пятновыводители' if it was a cluster (handled by type change above)

    # ==========================
    # 5. POLISHING RELOCATIONS
    # ==========================
    pol_l1 = find_node(root, "L1", "Полировка")
    if pol_l1:
        circles_l2 = find_node(pol_l1, "L2", "Полировальные круги")
        if circles_l2:
            # Poly for glass -> Glass cleaners
            glass_pol = find_node(circles_l2, "Cluster", "Полироль для стекла")
            if glass_pol:
                moika_l1 = find_node(root, "L1", "Мойка")
                glass_l2 = find_node(moika_l1, "L2", "Средства для стекол")
                if glass_l2:
                    dest_node = find_node(glass_l2, "L3", "Очистители стекол")
                    if not dest_node:
                        dest_node = Node("L3", "Очистители стекол", "")
                        glass_l2.add_child(dest_node)
                    move_keywords(glass_pol, dest_node)
                    circles_l2.remove_child(glass_pol)

            # Move 'General' extraction for Sets
            # Find category cluster
            cat_cluster = find_node(circles_l2, "Cluster", "категория")
            # If not found, look for keyword-based identification?
            # Or maybe "General" logic handled in CSV parser implicit?
            # Let's check for implicit general container named 'Cluster: General' or just direct keywords under L2
            # Our parser puts direct kws under L2.

            # Move keywords containing "набор" to Sets
            direct_kws = [c for c in circles_l2.children if c.type == "Keyword"]
            if cat_cluster:
                direct_kws.extend([c for c in cat_cluster.children if c.type == "Keyword"])

            if nabor_l2:
                nabor_poly = None
                for child in nabor_l2.children:
                    if child.name == "Наборы для полировки":
                        nabor_poly = child
                        break
                if not nabor_poly:
                    nabor_poly = Node("L3", "Наборы для полировки", "")
                    nabor_l2.add_child(nabor_poly)

                for kw in list(direct_kws):  # Copy list to modify
                    if "набор" in kw.name.lower():
                        if kw.parent:
                            kw.parent.remove_child(kw)
                        nabor_poly.add_child(kw)

    # ==========================
    # 6. CONVERSIONS (Cluster -> L3/Filter)
    # ==========================
    conversions = [
        ("Средства для стекол", "Омыватель", "L3", "Омыватель"),
        ("Средства для стекол", "Антидождь", "L3", "Антидождь"),
        ("Средства для кожи", "Уход за кожей", "L3", "Уход за кожей"),
        ("Средства для кожи", "Чистка кожи", "L3", "Очистители кожи"),
        ("Квик-детейлеры", "Силанты", "L3", "Силанты"),
        ("Воски", "Твердый", "L3", "Твердый воск"),
        ("Воски", "Жидкий", "L3", "Жидкий воск"),
        ("Микрофибра", "Для стекла", "Filter", "Для стекол"),
        ("Микрофибра", "Для сушки", "Filter", "Для сушки"),
    ]

    for l2_pat, node_pat, new_type, new_name in conversions:
        found_l2s = find_nodes(root, "L2", l2_pat)
        for l2 in found_l2s:
            targets = find_nodes(l2, "Cluster", node_pat) + find_nodes(l2, "Filter", node_pat)
            for t in targets:
                t.type = new_type
                t.name = new_name

    # ==========================
    # 7. MERGE MICROFIBER
    # ==========================
    micro_l2 = find_node(root, "L2", "Микрофибра")
    if micro_l2:
        base = find_node(micro_l2, "Cluster", "Тряпка для авто")
        if not base:
            base = find_node(micro_l2, "Cluster", "категория")

        if not base:
            base = Node("Cluster", "категория", "")
            micro_l2.add_child(base)
        else:
            base.name = "категория"  # Canonical name for General in CSV

        sources_pats = [
            "Тряпка микрофибра",
            "Без разводов",
            "Для мойки",
            "Микрофибра для мойки",
            "General",
            "категория",
        ]
        for pat in sources_pats:
            blocks = find_nodes(micro_l2, "Cluster", pat)
            for b in blocks:
                if b == base:
                    continue
                move_keywords(b, base)
                micro_l2.remove_child(b)

    # ==========================
    # 8. MERGE BRUSHES
    # ==========================
    brush_l2 = find_node(root, "L2", "Щетки")
    if brush_l2:
        # 8.1 Wash Brushes
        base1 = find_node(brush_l2, "Cluster", "Щетка для мойки")
        if not base1:
            base1 = Node("L3", "Щетки для мойки", "")
        else:
            base1.type = "L3"
            base1.name = "Щетки для мойки"
        if base1 not in brush_l2.children:
            brush_l2.add_child(base1)

        src1 = find_nodes(brush_l2, "Cluster", "Щетка для автомобиля")
        for s in src1:
            move_keywords(s, base1)
            brush_l2.remove_child(s)

        # 8.2 Detail Brushes
        base2 = find_node(brush_l2, "Cluster", "щетки для детейлинга")
        if not base2:
            base2 = find_node(brush_l2, "Cluster", "детейлинга")
        if not base2:
            base2 = Node("L3", "Кисти для детейлинга", "")
        else:
            base2.type = "L3"
            base2.name = "Кисти для детейлинга"
        if base2 not in brush_l2.children:
            brush_l2.add_child(base2)

        src2 = find_nodes(brush_l2, "Cluster", "Щетки для химчистки") + find_nodes(
            brush_l2, "Cluster", "Кисти для детейлинга"
        )
        for s in src2:
            if s == base2:
                continue
            move_keywords(s, base2)
            brush_l2.remove_child(s)

    # ==========================
    # 9. REFINED GENERAL / TORNADOR FIX
    # ==========================

    # 9.1 MOIKA GENERAL (Selective)
    moika_l1 = find_node(root, "L1", "Мойка")
    # Try finding by name 'Обезжириватели' OR 'Очистители двигателя'
    degrease_l2 = find_node(moika_l1, "L2", "Обезжириватели")
    if not degrease_l2 and moika_l1:
        degrease_l2 = find_node(moika_l1, "L2", "Очистители двигателя")

    if moika_l1 and degrease_l2:
        # Move ONLY general terms "shampoo", "chemistry", "wash" to L1
        # Keep "degreaser", "anti-silicone" in L2
        general_terms = [
            "шампунь",
            "химия",
            "мойка",
            "автохимия",
            "автокосметика",
            "средство для мойки",
        ]
        degreaser_terms = ["обезжир", "антисиликон", "битум", "спирт"]

        # Flatten clusters first? "General (Обезжириватели)" usually holds them
        # Let's just scan all keywords in L2
        kws_to_move = []

        def scan_degrease(n):
            if n.type == "Keyword":
                # Logic: if contains any degreaser term -> STAY. Else if contains general term -> MOVE.
                name = n.name.lower()
                is_degreaser = any(d in name for d in degreaser_terms)
                if not is_degreaser and any(g in name for g in general_terms):
                    kws_to_move.append(n)
            for c in n.children:
                scan_degrease(c)

        scan_degrease(degrease_l2)

        if kws_to_move:
            print(f"Moving {len(kws_to_move)} general keywords from Degreasers to L1 Moika")
            # Add to implicit L1 keywords (create 'категория' cluster or direct?)
            # Usually L1 holds data in 'Cluster: General' or just keywords.
            # CSV parser puts direct L1 keywords into root? No, structure is L1 -> ...
            # Add direct to L1
            for k in kws_to_move:
                if k.parent:
                    k.parent.remove_child(k)
                moika_l1.add_child(k)

    # 9.2 EQUIPMENT / TORNADOR CLEANUP
    if equip_l2:
        # Find 'Special' keys (Opt / Main) in Equipment and its children (incl Tornador)
        special_terms = {
            "опт": "Special: Опт",
            "набор для авто": "Special: Главная",  # Specific from TZ
        }

        # Also handle "General L2: Equipment" keywords like "equipment for wash"
        # Move them to... keep in Equipment L2? Or General?
        # TZ says: "L3: Tornador contains... equipment -> General L2: Equipment".
        # So create Cluster: General in Equipment if needed.

        equip_general = find_node(equip_l2, "Cluster", "General")
        if not equip_general:
            equip_general = Node("Cluster", "General", "")
            equip_l2.add_child(equip_general)

        # Iterate all keywords in Equipment
        all_eq_kws = []

        def collect_eq(n):
            if n.type == "Keyword":
                all_eq_kws.append(n)
            for c in n.children:
                collect_eq(c)

        collect_eq(equip_l2)

        for kw in all_eq_kws:
            name = kw.name.lower()

            # Special check
            target_special = None
            for term, spec_name in special_terms.items():
                if term in name:
                    target_special = spec_name
                    break

            if target_special:
                # Find/Create Special Node
                # Special nodes are at Root
                s_node = find_node(root, "Special", target_special)
                if not s_node:
                    s_name = target_special.replace("Special: ", "")
                    s_node = Node("Special", s_name, "")
                    root.add_child(s_node)

                kw.parent.remove_child(kw)
                s_node.add_child(kw)
                continue

            # Tornador/Equipment check
            # If keyword is in L3: Tornador BUT is 'equipment' -> Move to General
            if (
                kw.parent
                and kw.parent.name.startswith("Tornador")
                or kw.parent.name.startswith("Аппараты")
            ) and "оборудование" in name:
                kw.parent.remove_child(kw)
                equip_general.add_child(kw)

    # ==========================
    # 10. REMOVE EMPTY NODES
    # ==========================
    def remove_empty_recursive(node):
        for c in list(node.children):
            remove_empty_recursive(c)
        # Remove empty clusters/filters/L3/L2 (unless it's empty by design like Flat L2?)
        # TZ says remove empty L2: Antirain, etc.
        # Check against "Flat" allow list?
        allow_empty = [
            "Обезжириватели",
            "Очистители двигателя",
            "Губки и варежки",
            "Распылители и пенники",
            "Аксессуары для нанесения",
            "Ведра и емкости",
        ]

        is_empty = not node.children
        if (
            is_empty
            and (
                node.type in ["Cluster", "L3", "Filter"]
                or node.type == "L2"
                and node.name not in allow_empty
            )
            and node.parent
        ):
            node.parent.remove_child(node)

    remove_empty_recursive(root)


def write_csv(root, filepath):
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Фраза", "кол-во", "Запросы сред. [GA]"])

        # Helper to write list of nodes
        def write_nodes(nodes):
            for n in nodes:
                write_node_recursive(writer, n)

        # 1. Specials first? Or L1s?
        # Standard CSV: L1 zones first.

        l1s = [c for c in root.children if c.type == "L1"]
        specials = [c for c in root.children if c.type == "Special"]

        for s in specials:
            writer.writerow([])
            writer.writerow([f"Special: {s.name}", s.info, ""])
            writer.writerow([])
            for kw in s.children:
                if kw.type == "Keyword":
                    writer.writerow([kw.name, "", kw.info])

        for l1 in l1s:
            writer.writerow([])
            writer.writerow([f"L1: {l1.name}", l1.info, ""])
            writer.writerow([])

            # L1 Keywords
            l1_kws = [c for c in l1.children if c.type == "Keyword"]
            for kw in l1_kws:
                writer.writerow([kw.name, "", kw.info])

            # L1 Clusters (General)
            l1_clusters = [c for c in l1.children if c.type == "Cluster"]
            for cl in l1_clusters:
                write_node_recursive(writer, cl)

            # L2s
            l2s = [c for c in l1.children if c.type == "L2"]
            for l2 in l2s:
                write_node_recursive(writer, l2)


def write_node_recursive(writer, node):
    if node.type == "L2":
        writer.writerow([])
        writer.writerow([f"L2: {node.name}", node.info, ""])
        writer.writerow([])
    elif node.type in ["L3", "Filter", "Cluster"]:
        prefix = ""
        if node.type == "L3":
            prefix = "L3: "
        elif node.type == "Filter":
            prefix = "SEO-Фильтр: "
        elif node.type == "Cluster":
            prefix = ""  # Cluster usually no prefix in CSV key col? Or "Cluster:"?
        # CSV format usually implies name in Col1. If implicit header, checks heuristics.
        # But if we write specific name, valid.

        # Standardize 'Cluster' row:
        # Col1: Name, Col2: Info
        name_str = f"{prefix}{node.name}"
        writer.writerow([name_str, node.info, ""])

    # Write children
    keywords = [c for c in node.children if c.type == "Keyword"]
    nodes = [c for c in node.children if c.type != "Keyword"]

    for kw in keywords:
        writer.writerow([kw.name, "", kw.info])

    for n in nodes:
        write_node_recursive(writer, n)


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    import shutil

    shutil.copyfile(INPUT_FILE, BACKUP_FILE)
    print(f"Backed up to {BACKUP_FILE}")

    print("Parsing CSV...")
    root = parse_csv(INPUT_FILE)

    print("Transforming structure...")
    transform_structure(root)

    print(f"Writing to {OUTPUT_FILE}...")
    write_csv(root, OUTPUT_FILE)
    print("Done.")


if __name__ == "__main__":
    main()
