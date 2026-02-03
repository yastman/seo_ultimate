#!/usr/bin/env python3
"""
Generate SQL for plural meta update.
"""

import json
from pathlib import Path

# Load mapping
mapping_file = Path("data/opencart_mapping.json")
with open(mapping_file) as f:
    mapping = json.load(f)
slug_to_id = mapping.get("slug_to_id", {})

# Load plural mappings
with open("data/generated/plural_manual_uk.json") as f:
    plural_uk = json.load(f)
with open("data/generated/plural_manual_ru.json") as f:
    plural_ru = json.load(f)

sql_lines = []

# UK (language_id=1) - from local meta files
for meta_file in sorted(Path("uk/categories").glob("*/meta/*_meta.json")):
    slug = meta_file.parent.parent.name
    cat_id = slug_to_id.get(slug)
    if not cat_id:
        continue

    with open(meta_file) as f:
        meta = json.load(f)

    h1 = meta.get("h1", "").replace("'", "\\'")
    title = meta.get("meta", {}).get("title", "").replace("'", "\\'")

    sql_lines.append(
        f"UPDATE oc_category_description SET meta_h1='{h1}', meta_title='{title}' WHERE category_id={cat_id} AND language_id=1;"
    )

# RU (language_id=3) - from plural mapping directly
for slug, new_h1 in plural_ru.items():
    cat_id = slug_to_id.get(slug)
    if not cat_id:
        continue

    h1_escaped = new_h1.replace("'", "\\'")
    # Title format: "[H1] — купить, цены | Ultimate"
    title = f"{new_h1} — купить, цены | Ultimate".replace("'", "\\'")

    sql_lines.append(
        f"UPDATE oc_category_description SET meta_h1='{h1_escaped}', meta_title='{title}' WHERE category_id={cat_id} AND language_id=3;"
    )

# Write to file
output = Path("data/generated/plural_meta_update.sql")
output.write_text("\n".join(sql_lines) + "\n")
print(f"Generated {len(sql_lines)} SQL statements to {output}")
