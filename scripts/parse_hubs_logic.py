#!/usr/bin/env python3
"""
Script to parse structure CSV and generate Hub tasks (L1/L2).
Logic:
1. Parse CSV structure.
2. Find L1: and L2: rows.
3. Collect L3 categories nested under them.
4. Generate task_{slug}.json with "page_type": "hub".
5. In keywords put subcategory names (for linking).
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# Transliteration map
TRANSLIT_MAP = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
    'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
    'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
    'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
    'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    ' ': '-', '/': '-', ':': '-', ',': ''
}

def slugify(text: str) -> str:
    """Make slug from Russian text."""
    text = text.lower()
    result = []
    for char in text:
        if char in TRANSLIT_MAP:
            result.append(TRANSLIT_MAP[char])
        elif char.isalnum():
            result.append(char)
        elif char == '-':
            result.append(char)
    
    slug = "".join(result)
    slug = re.sub(r'-+', '-', slug)
    return slug.strip('-')

def parse_structure(csv_path: Path) -> Dict:
    """
    Parse CSV and build hierarchy.
    Returns:
    {
        "L1 Name": {
            "slug": "l1-slug",
            "children": {
                "L2 Name": {
                    "slug": "l2-slug",
                    "children": ["L3 Name 1", "L3 Name 2"]
                }
            }
        }
    }
    """
    import csv
    
    tree = {}
    current_l1 = None
    current_l2 = None
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            
            phrase = row[0].strip()
            if not phrase:
                continue
            
            # Check for L levels
            if phrase.startswith("L1:"):
                name = phrase.replace("L1:", "").strip()
                current_l1 = name
                current_l2 = None
                tree[current_l1] = {
                    "slug": slugify(name),
                    "children": {}
                }
                
            elif phrase.startswith("L2:"):
                if current_l1:
                    name = phrase.replace("L2:", "").strip()
                    current_l2 = name
                    tree[current_l1]["children"][current_l2] = {
                        "slug": slugify(name),
                        "children": []
                    }
                    
            elif phrase.startswith("L3:"):
                if current_l1 and current_l2:
                    name = phrase.replace("L3:", "").strip()
                    tree[current_l1]["children"][current_l2]["children"].append(name)
    
    return tree

def generate_hub_tasks(tree: Dict, output_dir: Path):
    """Generate task JSONs for Hubs."""
    
    for l1_name, l1_data in tree.items():
        # Generate L1 Task
        l2_names = list(l1_data["children"].keys())
        
        l1_task = {
            "slug": l1_data["slug"],
            "category_name": l1_name,
            "page_type": "hub",
            "keywords": [l1_name] + l2_names, # Primary + Subcategories
            "structure": {
                "subcategories": l2_names
            },
            "content_targets": {
                "tier": "A", # Hubs are Tier A per instructions
                "char_min": 2500,
                "char_max": 3500
            }
        }
        
        filename = f"task_{l1_data['slug']}.json"
        with open(output_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(l1_task, f, indent=2, ensure_ascii=False)
        print(f"Generated L1 Hub: {filename}")
        
        # Generate L2 Tasks
        for l2_name, l2_data in l1_data["children"].items():
            l3_names = l2_data["children"]
            
            l2_task = {
                "slug": l2_data["slug"],
                "category_name": l2_name,
                "page_type": "hub",
                "keywords": [l2_name] + l3_names,
                "structure": {
                    "subcategories": l3_names
                },
                "content_targets": {
                    "tier": "A", # Hubs are Tier A
                    "char_min": 2500,
                    "char_max": 3500 # Using Tier A limits
                }
            }
            
            filename = f"task_{l2_data['slug']}.json"
            with open(output_dir / filename, 'w', encoding='utf-8') as f:
                json.dump(l2_task, f, indent=2, ensure_ascii=False)
            print(f"Generated L2 Hub: {filename}")

def main():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    csv_file = data_dir / "Структура  Ultimate финал - Лист2.csv"
    
    if not csv_file.exists():
        print(f"Error: CSV file not found at {csv_file}")
        # Try fallback if filename works differently in environment
        csv_path_str = str(csv_file)
        if "Лист2.csv" in csv_path_str:
             # Try glob logic if needed, but for now exact name
             pass
        return

    print(f"Parsing structure from: {csv_file.name}")
    tree = parse_structure(csv_file)
    
    print("\nGenerating Task Files...")
    generate_hub_tasks(tree, base_dir) # Output to root project dir
    
    print("\nDone.")

if __name__ == "__main__":
    main()
