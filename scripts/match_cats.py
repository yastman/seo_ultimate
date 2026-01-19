import json
import os
from pathlib import Path

# Paths
ROOT = Path("C:/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт")
CAT_DIR = ROOT / "categories"
DUMP_FILE = ROOT / "sql_cats_dump.txt"


def load_dump():
    mapping = {}
    with open(DUMP_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if ": " in line:
                cid, name = line.strip().split(": ", 1)
                # Store multiple variants?
                # Just store by name for now
                mapping[name.strip()] = int(cid)
                mapping[name.strip().lower()] = int(cid)
    return mapping


def main():
    if not DUMP_FILE.exists():
        print("Dump not found")
        return

    sql_map = load_dump()
    cats = [d for d in os.listdir(CAT_DIR) if (CAT_DIR / d).is_dir()]

    found_count = 0
    missing = []

    print("CATEGORIES_MAP = {")

    for slug in sorted(cats):
        # clean_slug = slug.replace("-", " ")

        # Load name from json
        json_path = CAT_DIR / slug / "data" / f"{slug}_clean.json"

        candidates = [slug]

        ru_name = ""
        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                ru_name = data.get("name", "")
                if ru_name:
                    candidates.insert(0, ru_name)
            except Exception:
                pass

        # Try to find ID
        cat_id = None
        match_name = ""

        for cand in candidates:
            if cand in sql_map:
                cat_id = sql_map[cand]
                match_name = cand
                break
            if cand.lower() in sql_map:
                cat_id = sql_map[cand.lower()]
                match_name = cand
                break

            # Try fuzzy checks
            # e.g. "Активная пена" vs "Активна піна" (UA vs RU)
            # The dump likely contains BOTH if it's a bilingual store.
            # But the products.py mapping usually works with UK names?
            # Wait, products.py output says "Products by Category (UK)".
            # So the ID points to a category, which might have multiple descriptions.
            # My regex `(ID, 1, 'Name')` finds language_id=1.
            # I don't know if 1 is RU or UK.
            pass

        if cat_id:
            print(f'    {cat_id}: ("{slug}", "{match_name if match_name else ru_name}"),')
            found_count += 1
        else:
            print(f'    # ???: ("{slug}", "{ru_name}"), # NOT FOUND')
            missing.append((slug, ru_name))

    print("}")
    print(f"\n# Found: {found_count}/{len(cats)}")
    if missing:
        print("# Missing:")
        for m in missing:
            print(f"# - {m}")


if __name__ == "__main__":
    main()
