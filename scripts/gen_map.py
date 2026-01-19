import json
import os
import re
from pathlib import Path

# Paths
ROOT = Path("C:/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт")
CAT_DIR = ROOT / "categories"
SQL_FILE = ROOT / "data/dumps/ultimate_net_ua_backup.sql"


def load_sql():
    with open(SQL_FILE, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def find_id_in_sql(content, name):
    # Try exact match first
    # (ID,1,'Name'...)
    safe_name = re.escape(name)
    pattern = r"\((\d+),1,'" + safe_name + r"'"
    match = re.search(pattern, content, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def main():
    if not SQL_FILE.exists():
        print("SQL not found")
        return

    content = load_sql()

    cats = [d for d in os.listdir(CAT_DIR) if (CAT_DIR / d).is_dir()]

    print("CATEGORIES_MAP_NEW = {")
    for slug in sorted(cats):
        json_path = CAT_DIR / slug / "data" / f"{slug}_clean.json"
        name = slug
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                name = data.get("name", slug)
            except Exception:
                pass

        # Search ID
        cat_id = find_id_in_sql(content, name)

        if cat_id:
            print(f'    {cat_id}: ("{slug}", "{name}"),')
        else:
            print(f'    # ???: ("{slug}", "{name}"), # NOT FOUND')

    print("}")


if __name__ == "__main__":
    main()
