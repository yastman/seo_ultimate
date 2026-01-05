import json
import os
import re

# Constants
CATALOG_PATH = os.path.abspath("data/catalog_structure.json")
TASKS_DIR = os.path.abspath("tasks/categories")
CATEGORIES_DIR = os.path.abspath("categories")


def load_catalog():
    if not os.path.exists(CATALOG_PATH):
        print(f"Error: Catalog file not found at {CATALOG_PATH}")
        return []

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_keywords_from_md(checklist_path):
    keywords = []
    in_keyword_section = False

    if not os.path.exists(checklist_path):
        return []

    with open(checklist_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Detect start of Keywords section (tolerant to case and headers)
        if re.match(r"^##\s*Keywords", line, re.IGNORECASE):
            in_keyword_section = True
            continue

        if in_keyword_section:
            # Stop if we hit the next header
            if line.startswith("## ") and not re.match(r"^##\s*Keywords", line, re.IGNORECASE):
                break

            # Parse table rows | keyword | volume |
            if line.startswith("|") and line.endswith("|"):
                # Remove leading/trailing pipes and split
                content = line.strip("|")
                parts = [p.strip() for p in content.split("|")]

                if len(parts) >= 2:
                    kw = parts[0]
                    vol_str = parts[1]

                    # Skip header row and separator row
                    if "Keyword" in kw or "---" in kw:
                        continue

                    try:
                        # Clean volume string (remove typos if any)
                        vol_clean = re.sub(r"[^\d]", "", vol_str)
                        vol = int(vol_clean) if vol_clean else 0
                    except ValueError:
                        vol = 0

                    keywords.append({"keyword": kw, "volume": vol})

    return keywords


def init_category_clean_json(category_item):
    slug = category_item.get("id")
    name = category_item.get("name")

    if not slug:
        return

    checklist_path = os.path.join(TASKS_DIR, f"{slug}.md")

    if not os.path.exists(checklist_path):
        # Silent skip if no checklist exists (maybe incomplete implementation of structure)
        # print(f"Skipping {slug}: No checklist found at {checklist_path}")
        return

    print(f"Processing {slug}...")

    # Parse keywords
    keywords = parse_keywords_from_md(checklist_path)
    if not keywords:
        print(f"  Warning: No keywords found for {slug}")

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
    }

    with open(clean_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  Saved {slug}_clean.json ({len(keywords)} keywords)")


def main():
    print("Starting automatic initialization of categories from checklists...")

    catalog = load_catalog()
    if not catalog:
        return

    count = 0
    for item in catalog:
        # We process categories and filters if they have checklists
        # Relying on checklist existence as the trigger
        slug = item.get("id")
        checklist_path = os.path.join(TASKS_DIR, f"{slug}.md")

        if os.path.exists(checklist_path):
            init_category_clean_json(item)
            count += 1

    print(f"\nCompleted! Processed {count} categories.")


if __name__ == "__main__":
    main()
