#!/usr/bin/env python3
"""
init_categories_from_checklists.py

Инициализирует _clean.json для всех категорий.
Источники данных (в порядке приоритета):
1. tasks/categories/{slug}.md (чеклисты)
2. data/generated/STRUCTURE.md (fallback для пустых)

Также создаёт data/all_keywords.json — единый файл со всеми ключами.

Usage:
    python3 scripts/init_categories_from_checklists.py
"""

import json
import os
import re

# Constants
CATALOG_PATH = os.path.abspath("data/catalog_structure.json")
TASKS_DIR = os.path.abspath("tasks/categories")
CATEGORIES_DIR = os.path.abspath("categories")
STRUCTURE_MD_PATH = os.path.abspath("data/generated/STRUCTURE.md")
ALL_KEYWORDS_PATH = os.path.abspath("data/all_keywords.json")

# Cache for STRUCTURE.md parsing
_structure_cache = None


def load_catalog():
    if not os.path.exists(CATALOG_PATH):
        print(f"Error: Catalog file not found at {CATALOG_PATH}")
        return []

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_keywords_from_md(checklist_path):
    """Parse keywords from tasks/categories/{slug}.md checklist."""
    keywords = []
    in_keyword_section = False

    if not os.path.exists(checklist_path):
        return []

    with open(checklist_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Detect start of Keywords section
        if re.match(r"^##\s*Keywords", line, re.IGNORECASE):
            in_keyword_section = True
            continue

        if in_keyword_section:
            # Stop if we hit the next header
            if line.startswith("## ") and not re.match(r"^##\s*Keywords", line, re.IGNORECASE):
                break

            # Parse table rows | keyword | volume |
            if line.startswith("|") and line.endswith("|"):
                content = line.strip("|")
                parts = [p.strip() for p in content.split("|")]

                if len(parts) >= 2:
                    kw = parts[0]
                    vol_str = parts[1]

                    # Skip header row and separator row
                    if "Keyword" in kw or "---" in kw:
                        continue

                    try:
                        vol_clean = re.sub(r"[^\d]", "", vol_str)
                        vol = int(vol_clean) if vol_clean else 0
                    except ValueError:
                        vol = 0

                    keywords.append({"keyword": kw, "volume": vol})

    return keywords


def load_structure_md():
    """Load and cache STRUCTURE.md content."""
    global _structure_cache
    if _structure_cache is not None:
        return _structure_cache

    if not os.path.exists(STRUCTURE_MD_PATH):
        print(f"Warning: STRUCTURE.md not found at {STRUCTURE_MD_PATH}")
        _structure_cache = {}
        return _structure_cache

    with open(STRUCTURE_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Normalize line endings
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    _structure_cache = {}

    # Parse line by line
    lines = content.split("\n")
    current_name = None
    current_keywords = []
    in_table = False

    for line in lines:
        line = line.strip()

        # Check for headers: ### 📂 L1: Name (Vol: X) or #### 📁 L2: Name (Vol: X)
        # or ##### 🏷️ L3: Name (Vol: X) or #### 📦 Cluster: 🔑 Direct Keywords (Name) (Vol: X)
        if line.startswith("#"):
            # Save previous section if we have keywords
            if current_name and current_keywords:
                _structure_cache[current_name] = current_keywords.copy()
                _structure_cache[current_name.lower()] = current_keywords.copy()

            current_keywords = []
            in_table = False

            # Extract name from header
            # Pattern: ### 📂 L1: Мойка и Экстерьер (Vol: 25530)
            # or: #### 📦 Cluster: 🔑 Direct Keywords (Мойка и Экстерьер) (Vol: 1540)
            if "L1:" in line or "L2:" in line or "L3:" in line:
                # Extract name after L1:/L2:/L3:
                match = re.search(r"L[123]:\s*([^(]+)", line)
                if match:
                    current_name = match.group(1).strip()
            elif "Direct Keywords" in line:
                # Extract name from parentheses: Direct Keywords (Name)
                match = re.search(r"Direct Keywords\s*\(([^)]+)\)", line)
                if match:
                    current_name = match.group(1).strip()
            elif "Filter:" in line:
                match = re.search(r"Filter:\s*([^(]+)", line)
                if match:
                    current_name = match.group(1).strip()
            elif "Cluster:" in line and "Direct Keywords" not in line:
                match = re.search(r"Cluster:\s*([^(]+)", line)
                if match:
                    current_name = match.group(1).strip()
            else:
                current_name = None

            continue

        # Check for table header
        if "| Keyword" in line and "| Volume" in line:
            in_table = True
            continue

        # Skip separator row
        if in_table and line.startswith("|") and "---" in line:
            continue

        # Parse table row
        if in_table and line.startswith("|") and line.endswith("|"):
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) >= 2:
                kw = parts[0].strip()
                vol_str = parts[1].strip()
                # Skip if keyword looks like header
                if kw and kw != "Keyword" and "---" not in kw:
                    try:
                        vol = int(re.sub(r"[^\d]", "", vol_str) or "0")
                    except ValueError:
                        vol = 0
                    current_keywords.append({"keyword": kw, "volume": vol})
        elif in_table and not line.startswith("|"):
            # End of table
            in_table = False

    # Save last section
    if current_name and current_keywords:
        _structure_cache[current_name] = current_keywords.copy()
        _structure_cache[current_name.lower()] = current_keywords.copy()

    return _structure_cache


def get_keywords_from_structure(category_name):
    """Get keywords for category from STRUCTURE.md."""
    structure = load_structure_md()

    # Try exact match first
    if category_name in structure:
        return structure[category_name]

    # Try lowercase match
    if category_name.lower() in structure:
        return structure[category_name.lower()]

    # Try partial match
    for key in structure:
        if category_name.lower() in key.lower() or key.lower() in category_name.lower():
            return structure[key]

    return []


def init_category_clean_json(category_item):
    slug = category_item.get("id")
    name = category_item.get("name")

    if not slug:
        return

    print(f"Processing {slug}...")

    # Try checklist first
    checklist_path = os.path.join(TASKS_DIR, f"{slug}.md")
    keywords = []
    source = "none"

    if os.path.exists(checklist_path):
        keywords = parse_keywords_from_md(checklist_path)
        if keywords:
            source = "checklist"

    # Fallback to STRUCTURE.md if no keywords from checklist
    if not keywords:
        keywords = get_keywords_from_structure(name)
        if keywords:
            source = "STRUCTURE.md"

    if not keywords:
        print(f"  Warning: No keywords found for {slug} (tried checklist and STRUCTURE.md)")
    else:
        print(f"  Found {len(keywords)} keywords from {source}")

    # Create directory structure
    category_path = os.path.join(CATEGORIES_DIR, slug)
    data_path = os.path.join(category_path, "data")
    os.makedirs(data_path, exist_ok=True)

    # Create _clean.json
    clean_json_path = os.path.join(data_path, f"{slug}_clean.json")

    data = {
        "id": slug,
        "name": name,
        "type": category_item.get("type", "category"),
        "parent_id": category_item.get("parent_id"),
        "keywords": keywords,
        "source": source,
    }

    with open(clean_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  Saved {slug}_clean.json ({len(keywords)} keywords)")


def generate_all_keywords_json(catalog):
    """Generate data/all_keywords.json — unified keywords file."""
    all_keywords = {}

    for item in catalog:
        slug = item.get("id")
        if not slug:
            continue

        # Skip filters
        if item.get("type") == "filter":
            continue

        # Read _clean.json
        clean_path = os.path.join(CATEGORIES_DIR, slug, "data", f"{slug}_clean.json")
        if not os.path.exists(clean_path):
            continue

        with open(clean_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        keywords = data.get("keywords", [])
        if not keywords:
            continue

        total_volume = sum(k.get("volume", 0) for k in keywords)

        all_keywords[slug] = {
            "name": item.get("name"),
            "level": item.get("level", ""),
            "parent_id": item.get("parent_id"),
            "keywords": keywords,
            "total_volume": total_volume,
            "keyword_count": len(keywords),
            "source": data.get("source", "unknown"),
        }

    # Sort by total_volume descending
    sorted_keywords = dict(sorted(all_keywords.items(), key=lambda x: x[1]["total_volume"], reverse=True))

    with open(ALL_KEYWORDS_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted_keywords, f, ensure_ascii=False, indent=2)

    return sorted_keywords


def main():
    print("=" * 60)
    print("Initializing categories from checklists + STRUCTURE.md")
    print("=" * 60)

    catalog = load_catalog()
    if not catalog:
        return

    # Pre-load STRUCTURE.md
    load_structure_md()
    print(f"Loaded STRUCTURE.md with {len(_structure_cache) // 2} categories\n")

    count = 0
    with_keywords = 0
    without_keywords = 0

    for item in catalog:
        slug = item.get("id")

        # Skip filters (they don't need separate content)
        if item.get("type") == "filter":
            continue

        init_category_clean_json(item)
        count += 1

        # Check if keywords were found
        clean_path = os.path.join(CATEGORIES_DIR, slug, "data", f"{slug}_clean.json")
        if os.path.exists(clean_path):
            with open(clean_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("keywords"):
                    with_keywords += 1
                else:
                    without_keywords += 1

    # Generate all_keywords.json
    print("\n" + "-" * 60)
    print("Generating data/all_keywords.json...")
    all_kw = generate_all_keywords_json(catalog)

    total_kw = sum(d["keyword_count"] for d in all_kw.values())
    total_vol = sum(d["total_volume"] for d in all_kw.values())

    print(f"  Categories: {len(all_kw)}")
    print(f"  Keywords: {total_kw}")
    print(f"  Total volume: {total_vol}")
    print(f"  Saved: {ALL_KEYWORDS_PATH}")

    print("\n" + "=" * 60)
    print(f"Completed! Processed {count} categories.")
    print(f"  With keywords: {with_keywords}")
    print(f"  Without keywords: {without_keywords}")
    print("=" * 60)


if __name__ == "__main__":
    main()
