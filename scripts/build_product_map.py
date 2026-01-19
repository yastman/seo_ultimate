import json
import os
from pathlib import Path

# Paths
ROOT = Path("C:/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт")
CAT_DIR = ROOT / "categories"
DUMP_FILE = ROOT / "sql_cats_dump.txt"


def load_sql_cats():
    cats = {}
    with open(DUMP_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if ": " not in line:
                continue
            cid_str, name = line.strip().split(": ", 1)
            cid = int(cid_str)
            if 411 <= cid <= 467:
                cats[cid] = name
    return cats


def main():
    sql_cats = load_sql_cats()

    # Load manual map for difficult ones
    manual_map = {
        "akkumulyatornaya": None,  # Missing in SQL range?
        "polirovka": 457,
        "polirovalnye-mashinki": 461,
        "polirovalnye-pasty": 458,
        "polirovalnye-krugi": 459,
        # Add more manual overrides if needed
    }

    # Get local slugs and names
    dirs = sorted([d for d in os.listdir(CAT_DIR) if (CAT_DIR / d).is_dir()])

    print("CATEGORIES_MAP = {")

    for slug in dirs:
        mapped_id = manual_map.get(slug)

        # Try to find by name
        json_path = CAT_DIR / slug / "data" / f"{slug}_clean.json"
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                data.get("name", slug)
            except Exception:
                pass

        if not mapped_id:
            # Fuzzy match ru_name vs sql_cats.values()
            # or slug matching
            pass

        # Print logic placeholder
        # We will do a simple prompt output for now
        pass

    # Better: Just print the SQL cats and let me copy-paste the obvious ones.
    # The list is short (56 items).

    print("# SQL Categories found (411-467):")
    for cid, name in sql_cats.items():
        print(f'    {cid}: "{name}",')


if __name__ == "__main__":
    main()
