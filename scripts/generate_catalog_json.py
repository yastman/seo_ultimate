import json
import os
import re
from typing import Dict, List, Optional

# Constants
SOURCE_FILE = "tasks/reports/STRUCTURE_TREE.md"
OUTPUT_FILE = "data/catalog_structure.json"
UK_OUTPUT_FILE = "uk/data/catalog_structure.json"

# Transliteration map (RU -> Latin)
TRANSLIT_MAP = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
    "і": "i",
    "ї": "yi",
    "є": "ye",
    "ґ": "g",
}


def sluggify(text: str) -> str:
    """
    Transliterates and sluggifies text.
    Example: "Мойка и Экстерьер" -> "moyka-i-eksterer"
    """
    text = text.lower()
    transliterated = ""
    for char in text:
        transliterated += TRANSLIT_MAP.get(char, char)

    # Replace non-alphanumeric with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", transliterated)
    # Remove leading/trailing hyphens
    slug = slug.strip("-")
    return slug


def parse_structure_tree(file_path: str) -> List[Dict]:
    """
    Parses STRUCTURE_TREE.md and returns a flat list of category objects.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Source file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    catalog = []

    # Context trackers
    current_l1: Optional[Dict] = None
    current_l2: Optional[Dict] = None

    # Regex patterns
    l1_pattern = re.compile(r"^L1:\s+(.+)$")
    l2_pattern = re.compile(r"^\s+(?:├──|└──)\s+L2:\s+(.+)$")
    l3_pattern = re.compile(r"^\s+(?:│\s+)?(?:├──|└──)\s+L3:\s+(.+)$")
    filter_pattern = re.compile(r"^\s+(?:│\s+)?(?:├──|└──)\s+Filter:\s+(.+)$")

    sort_counter = 0
    existing_ids = set()

    def get_unique_slug(base_slug: str, level: str) -> str:
        if base_slug not in existing_ids:
            return base_slug

        # Try appending level e.g. "oborudovanie-l2"
        new_slug = f"{base_slug}-{level.lower()}"
        if new_slug not in existing_ids:
            return new_slug

        # Fallback counter
        counter = 1
        while True:
            candidate = f"{base_slug}-{counter}"
            if candidate not in existing_ids:
                return candidate
            counter += 1

    for line in lines:
        line = line.rstrip()
        if not line:
            continue

        # L1 parsing
        l1_match = l1_pattern.match(line)
        if l1_match:
            name = l1_match.group(1).strip()
            slug = get_unique_slug(sluggify(name), "L1")
            existing_ids.add(slug)
            sort_counter += 10

            current_l1 = {
                "id": slug,
                "name": name,
                "type": "category",
                "level": "L1",
                "parent_id": None,
                "path": slug,
                "sort_order": sort_counter,
                "status": "active",
            }
            catalog.append(current_l1)
            current_l2 = None  # Reset L2 context
            continue

        # L2 parsing
        l2_match = l2_pattern.match(line)
        if l2_match:
            if not current_l1:
                print(f"Warning: L2 found without L1 context: {line}")
                continue

            name = l2_match.group(1).strip()
            slug = get_unique_slug(sluggify(name), "L2")
            existing_ids.add(slug)
            sort_counter += 10

            current_l2 = {
                "id": slug,
                "name": name,
                "type": "category",
                "level": "L2",
                "parent_id": current_l1["id"],
                "path": f"{current_l1['path']}/{slug}",
                "sort_order": sort_counter,
                "status": "active",
            }
            catalog.append(current_l2)
            continue

        # L3 parsing
        l3_match = l3_pattern.match(line)
        if l3_match:
            name = l3_match.group(1).strip()
            slug = get_unique_slug(sluggify(name), "L3")
            existing_ids.add(slug)
            sort_counter += 10

            # Parent is current_l2 if exists, else current_l1
            parent = current_l2 if current_l2 else current_l1
            if not parent:
                print(f"Warning: L3 found without parent context: {line}")
                continue

            item = {
                "id": slug,
                "name": name,
                "type": "category",
                "level": "L3",
                "parent_id": parent["id"],
                "path": f"{parent['path']}/{slug}",
                "sort_order": sort_counter,
                "status": "active",
            }
            catalog.append(item)
            continue

        # Filter parsing
        filter_match = filter_pattern.match(line)
        if filter_match:
            name = filter_match.group(1).strip()
            slug = get_unique_slug(sluggify(name), "Filter")
            existing_ids.add(slug)
            sort_counter += 10

            parent = current_l2 if current_l2 else current_l1
            if not parent:
                continue

            item = {
                "id": slug,
                "name": name,
                "type": "filter",
                "level": "Filter",
                "parent_id": parent["id"],
                "path": f"{parent['path']}/{slug}",
                "sort_order": sort_counter,
                "status": "active",
            }
            catalog.append(item)
            continue

    return catalog


def main():
    print(f"Parsing {SOURCE_FILE}...")
    try:
        catalog = parse_structure_tree(SOURCE_FILE)
    except Exception as e:
        print(f"Error parsing tree: {e}")
        return

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # Save JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated {len(catalog)} items in {OUTPUT_FILE}")

    # Print validation summary
    l1_count = len([x for x in catalog if x["level"] == "L1"])
    l2_count = len([x for x in catalog if x["level"] == "L2"])
    l3_count = len([x for x in catalog if x["level"] == "L3"])
    filter_count = len([x for x in catalog if x["level"] == "Filter"])

    print(f"Stats: L1: {l1_count}, L2: {l2_count}, L3: {l3_count}, Filter: {filter_count}")


if __name__ == "__main__":
    main()
