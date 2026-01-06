import json
import os

PROJECT_ROOT = r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт"
CATALOG_STRUCTURE_PATH = os.path.join(PROJECT_ROOT, "data", "catalog_structure.json")
MANUAL_SHAMPOO_PATH = os.path.join(
    PROJECT_ROOT,
    "categories",
    "shampuni-dlya-ruchnoy-moyki",
    "data",
    "shampuni-dlya-ruchnoy-moyki_clean.json",
)


def update_catalog_structure():
    print(f"Reading {CATALOG_STRUCTURE_PATH}...")
    with open(CATALOG_STRUCTURE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Remove 'oborudovanie-l2'
    new_data = [item for item in data if item["id"] != "oborudovanie-l2"]

    # 2. Update 'apparaty-tornador'
    tornador_found = False
    for item in new_data:
        if item["id"] == "apparaty-tornador":
            print("Updating apparaty-tornador...")
            item["level"] = "L2"
            item["parent_id"] = "oborudovanie"
            item["path"] = "oborudovanie/apparaty-tornador"
            tornador_found = True
            break

    if not tornador_found:
        print("WARNING: apparaty-tornador not found in json!")

    # 3. Verify 'oborudovanie' L1 exists
    oborudovanie_exists = any(item["id"] == "oborudovanie" and item["level"] == "L1" for item in new_data)
    if not oborudovanie_exists:
        print("WARNING: oborudovanie (L1) not found!")

    with open(CATALOG_STRUCTURE_PATH, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print("Catalog structure updated.")


def convert_shampoo_legacy():
    print(f"Reading {MANUAL_SHAMPOO_PATH}...")
    with open(MANUAL_SHAMPOO_PATH, "r", encoding="utf-8") as f:
        legacy_data = json.load(f)

    # Extract keywords from all groups
    keywords = []

    # helper to process group
    def process_group(group_list):
        for k in group_list:
            keywords.append({"keyword": k["keyword"], "volume": k["volume"]})

    if "keywords" in legacy_data:
        kw_data = legacy_data["keywords"]
        for group in ["primary", "secondary", "supporting", "commercial"]:
            if group in kw_data:
                process_group(kw_data[group])

    # Create new V2 structure
    new_data = {
        "id": "shampuni-dlya-ruchnoy-moyki",
        "name": "Шампуни для ручной мойки",
        "type": "category",
        "parent_id": "avtoshampuni",
        "keywords": keywords,
        "source": "migrated_from_legacy",
    }

    with open(MANUAL_SHAMPOO_PATH, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    print("Shampoo file converted to V2 format.")


if __name__ == "__main__":
    update_catalog_structure()
    convert_shampoo_legacy()
