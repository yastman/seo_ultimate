#!/usr/bin/env python3
"""Извлечение всех ключей из _clean.json категорий."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT / "categories"
OUTPUT_FILE = ROOT / "data" / "generated" / "all_from_categories.csv"


def extract_from_file(clean_file: Path) -> list[dict]:
    """Извлекает все ключи из одного _clean.json файла."""
    rows = []
    try:
        data = json.loads(clean_file.read_text(encoding="utf-8"))
        category = data.get("id", clean_file.stem.replace("_clean", ""))

        keywords_data = data.get("keywords", [])
        synonyms_data = data.get("synonyms", [])

        # Handle legacy format: keywords is dict with groups
        if isinstance(keywords_data, dict):
            # Legacy format: {"primary": [...], "synonyms_base": [...], ...}
            for group_name, items in keywords_data.items():
                if not isinstance(items, list):
                    continue
                for kw in items:
                    # Determine type based on group name
                    if group_name == "primary":
                        source_type = "keyword"
                    elif "commercial" in group_name:
                        source_type = "synonym"  # commercial = meta_only synonyms
                    else:
                        source_type = "synonym"  # all other groups are synonyms

                    rows.append({
                        "keyword": kw["keyword"],
                        "volume": kw.get("volume", 0),
                        "category": category,
                        "source_type": source_type,
                    })
        else:
            # New format: keywords is list
            for kw in keywords_data:
                rows.append({
                    "keyword": kw["keyword"],
                    "volume": kw.get("volume", 0),
                    "category": category,
                    "source_type": "keyword",
                })

        # Synonyms (new format only, legacy has synonyms inside keywords dict)
        if isinstance(synonyms_data, list):
            for syn in synonyms_data:
                rows.append({
                    "keyword": syn["keyword"],
                    "volume": syn.get("volume", 0),
                    "category": category,
                    "source_type": "synonym",
                })

        # Variations
        for var in data.get("variations", []):
            rows.append({
                "keyword": var["keyword"],
                "volume": var.get("volume", 0),
                "category": category,
                "source_type": "variation",
            })

    except Exception as e:
        print(f"⚠️  {clean_file.name}: {e}")

    return rows


def main():
    all_rows = []

    for clean_file in sorted(CATEGORIES_DIR.rglob("*_clean.json")):
        rows = extract_from_file(clean_file)
        all_rows.extend(rows)
        if not rows:
            print(f"⚠️  {clean_file.name}: пустой файл")

    # Save CSV
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["keyword", "volume", "category", "source_type"])
        writer.writeheader()
        writer.writerows(all_rows)

    # Stats
    keywords_count = sum(1 for r in all_rows if r["source_type"] == "keyword")
    synonyms_count = sum(1 for r in all_rows if r["source_type"] == "synonym")
    variations_count = sum(1 for r in all_rows if r["source_type"] == "variation")
    categories_count = len(set(r["category"] for r in all_rows))

    print(f"✅ Извлечено {len(all_rows)} записей → {OUTPUT_FILE}")
    print(f"   keywords: {keywords_count}, synonyms: {synonyms_count}, variations: {variations_count}")
    print(f"   категорий: {categories_count}")


if __name__ == "__main__":
    main()
