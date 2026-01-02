#!/usr/bin/env python3
"""
csv_to_readable_md.py — CSV to Markdown Converter

Converts structure CSV to a readable Markdown file for easier analysis and token saving.
"""

import csv
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add scripts dir to path to allow importing config
sys.path.append(str(Path(__file__).parent))

try:
    import config
    from config import SEMANTICS_CSV, PROJECT_ROOT
except ImportError:
    # Fallback if config not found (e.g. running standalone)
    print("Warning: config.py not found, using default paths.")
    PROJECT_ROOT = Path(__file__).parent.parent
    SEMANTICS_CSV = PROJECT_ROOT / "Структура _Ultimate.csv"

OUTPUT_FILE = PROJECT_ROOT / "data" / "STRUCTURE.md"

class Node:
    def __init__(self, name: str, level: str):
        self.name = name
        self.level = level  # 'L1', 'L2', 'L3', 'Cluster'
        self.children: List['Node'] = []
        self.keywords: List[Dict] = []
        self.total_volume = 0
        self.keyword_count = 0

    def add_keyword(self, keyword: str, volume: int):
        self.keywords.append({"keyword": keyword, "volume": volume})
        self.total_volume += volume
        self.keyword_count += 1
    
    def add_child(self, node: 'Node'):
        self.children.append(node)

def parse_csv(csv_path: Path) -> List[Node]:
    tree = []
    # explicit text-based hierarchy
    current_l1 = None
    current_l2 = None
    
    # "Current Container" where keywords go. 
    # Can be an L3 node, or a loose Cluster node.
    current_container = None 

    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return []

    print(f"Reading CSV from: {csv_path}")
    
    # We will create a "Root" pseudo-node for orphans if needed, 
    # but preferably we attach to current L1/L2.
    # To handle the mixed structure, we'll try to maintain valid L1/L2 pointers.
    
    with open(csv_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row_idx, row in enumerate(reader):
            if not row:
                continue
            
            # Safe access
            col1 = row[0].strip() if len(row) > 0 else ""
            col2 = row[1].strip() if len(row) > 1 else ""
            col3 = row[2].strip() if len(row) > 2 else "" # Volume usually here
            
            if not col1:
                continue

            # 1. Detect Explicit Hierarchy L1/L2/L3
            if col1.startswith('L1:'):
                name = col1.replace('L1:', '').strip()
                current_l1 = Node(name, 'L1')
                tree.append(current_l1)
                current_l2 = None
                current_container = None
                continue
                
            if col1.startswith('L2:'):
                name = col1.replace('L2:', '').strip()
                current_l2 = Node(name, 'L2')
                if current_l1:
                    current_l1.add_child(current_l2)
                else:
                    # Orphan L2, create a dummy L1 or attach to root? 
                    # Let's attach to a "Misc" L1 if none exists
                    if not tree:
                        dummy = Node("Разное / Без категории", "L1")
                        tree.append(dummy)
                        current_l1 = dummy
                    current_l1.add_child(current_l2)
                
                current_container = None
                continue

            if col1.startswith('L3:'):
                name = col1.replace('L3:', '').strip()
                node = Node(name, 'L3')
                current_container = node
                if current_l2:
                    current_l2.add_child(node)
                elif current_l1:
                    current_l1.add_child(node)
                else:
                    # Orphan L3
                    if not tree:
                         dummy = Node("Разное / Без категории", "L1")
                         tree.append(dummy)
                         current_l1 = dummy
                    current_l1.add_child(node)
                continue

            # 2. Detect "Implicit Cluster Headers"
            # Pattern: Col1 has text, Col2 (Count) has number, Col3 (Vol) is empty (or 0/empty)
            # Example: "тряпка для авто,35,"
            # Some rows might be "Category, 9,"
            is_header = False
            if col2 and (not col3 or col3 == '0'):
                # Heuristic: It's likely a header if it has a count but no volume for the phrase itself
                # But wait, look at line 9: "пена для мойки автомобиля,,1300" -> Col2 empty, Col3=1300
                # Look at line 419: "тряпка для авто,35," -> Col2=35, Col3=""
                # Only check if it looks like a count.
                # However, sometimes real keywords have count filled? (Unlikely in this file format)
                # Let's assume: if col2 is digit, and col3 is NOT digit (or empty), it's a header.
                if col2.replace('/','').isdigit(): # handle "24/338" format if present
                    is_header = True
            
            if is_header and not col1.startswith('SEO-Фильтр'):
                # It's a header line. Create new cluster.
                current_container = Node(col1, 'Cluster')
                
                # Attach to hierarchy
                if current_l2:
                    current_l2.add_child(current_container)
                elif current_l1:
                    current_l1.add_child(current_container)
                else:
                    # Root level cluster (e.g. "Главная")
                    # Create a dummy L1 for it if needed, or just treat as L1?
                    # "Главная" is big. Let's make it an L1 if it appears at root 
                    # but usually these are L2-equivalent if they have no parent.
                    # Let's auto-create L1 if missing.
                    if not tree:
                         dummy = Node("Разное / Без категории", "L1")
                         tree.append(dummy)
                         current_l1 = dummy
                    current_l1.add_child(current_container)
                continue

            # 3. Detect Keywords
            # Must have volume in Col3
            if col3.isdigit():
                vol = int(col3)
                if current_container:
                    current_container.add_keyword(col1, vol)
                elif current_l2:
                    # Keyword directly under L2? (Rare, but possible if loose)
                    # Create implicit "General" cluster
                    # Check if last child is general
                    if not current_l2.children or current_l2.children[-1].name != "General":
                         gen = Node("General", "Cluster")
                         current_l2.add_child(gen)
                    current_l2.children[-1].add_keyword(col1, vol)
                elif current_l1:
                     # Keyword directly under L1
                     if not current_l1.children or current_l1.children[-1].name != "General":
                         gen = Node("General", "Cluster")
                         current_l1.add_child(gen)
                     current_l1.children[-1].add_keyword(col1, vol)
                else:
                    # Keyword at root? Skip or log
                    pass

    return tree

def generate_markdown(tree: List[Node], output_path: Path):
    # First aggregate stats
    total_clusters = 0
    total_keywords = 0
    total_volume_global = 0
    
    for l1 in tree:
        l1_kws = 0
        l1_vol = 0
        for l2 in l1.children:
            l2_kws = 0
            l2_vol = 0
            for l3 in l2.children:
                total_clusters += 1
                l2_kws += l3.keyword_count
                l2_vol += l3.total_volume
            
            l2.keyword_count = l2_kws
            l2.total_volume = l2_vol
            l1_kws += l2_kws
            l1_vol += l2_vol
            
        l1.keyword_count = l1_kws
        l1.total_volume = l1_vol
        
        total_volume_global += l1.total_volume
        total_keywords += l1.keyword_count

    print(f"Writing Markdown to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Структура Семантики Ultimate.net.ua\n\n")
        f.write("Generated from `Структура _Ultimate.csv`\n\n")
        
        f.write("## 📊 Сводка\n\n")
        f.write(f"- **Всего L1 Категорий**: {len(tree)}\n")
        f.write(f"- **Всего Кластеров (L3)**: {total_clusters}\n")
        f.write(f"- **Всего Ключей**: {total_keywords}\n")
        f.write(f"- **Общий Volume**: {total_volume_global}\n\n")
        f.write("---\n\n")
        
        f.write("## 🌳 Дерево Категорий\n\n")
        
        for l1 in tree:
            f.write(f"### 📂 L1: {l1.name} (Vol: {l1.total_volume})\n\n")
            
            if not l1.children:
                 f.write("_Нет подкатегорий_\n\n")

            for l2 in l1.children:
                f.write(f"#### 📁 L2: {l2.name} (Vol: {l2.total_volume})\n\n")
                
                if not l2.children:
                    f.write("_Нет подкатегорий_\n\n")
                    continue
                    
                for l3 in l2.children:
                    f.write(f"##### 🏷️ L3: {l3.name} (Keys: {l3.keyword_count}, Vol: {l3.total_volume})\n\n")
                    
                    if l3.keywords:
                        f.write("| Keyword | Volume |\n")
                        f.write("|---|---|\n")
                        # Sort keywords by volume desc
                        sorted_kws = sorted(l3.keywords, key=lambda k: k['volume'], reverse=True)
                        for kw in sorted_kws:
                            f.write(f"| {kw['keyword']} | {kw['volume']} |\n")
                        f.write("\n")
                    else:
                        f.write("_Нет ключей_\n\n")
            
            f.write("---\n\n")

if __name__ == "__main__":
    if not OUTPUT_FILE.parent.exists():
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
    tree = parse_csv(SEMANTICS_CSV)
    if tree:
        generate_markdown(tree, OUTPUT_FILE)
        print("Done!")
    else:
        print("Empty tree, something went wrong.")
