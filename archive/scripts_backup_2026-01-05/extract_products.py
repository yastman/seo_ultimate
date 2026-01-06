#!/usr/bin/env python3
"""Extract products by category from SQL backup."""

import re

SQL_FILE = "ultimate_net_ua_backup.sql"

# Category mapping: category_id -> (slug, uk_name)
CATEGORIES = {
    415: ("aktivnaya-pena", "Активна піна"),
    412: ("dlya-ruchnoy-moyki", "Для ручного миття"),
    418: ("ochistiteli-stekol", "Очищувач скла"),
    419: ("ochistiteli-diskov", "Очищувач дисків"),
    420: ("ochistiteli-shin", "Засоби для шин"),
    421: ("cherniteli-shin", "Чорнитель гуми"),
    423: ("glina-i-avtoskraby", "Глина та автоскраби"),
    417: ("antibitum-antimoshka", "Очищення кузова (антибітум, антимошка)"),
}


def extract_product_to_category(sql_content):
    """Extract product_id -> category_id mapping."""
    pattern = r"\((\d+),(\d+),[01]\)"
    matches = re.findall(pattern, sql_content)

    cat_products = {}
    for product_id, category_id in matches:
        cat_id = int(category_id)
        prod_id = int(product_id)
        if cat_id in CATEGORIES and prod_id != cat_id:
            if cat_id not in cat_products:
                cat_products[cat_id] = []
            cat_products[cat_id].append(prod_id)

    return cat_products


def extract_product_names(sql_content, product_ids):
    """Extract product names for given IDs (UK language_id=1)."""
    names = {}
    for pid in product_ids:
        # Pattern: (product_id,1,'Name'
        pattern = rf"\({pid},1,\'([^\']+)\'"
        match = re.search(pattern, sql_content)
        if match:
            name = match.group(1)
            # Skip URLs
            if not name.startswith("http") and len(name) > 10:
                names[pid] = name
    return names


def main():
    with open(SQL_FILE, encoding="utf-8", errors="ignore") as f:
        sql_content = f.read()

    cat_products = extract_product_to_category(sql_content)

    print("# Товари по категоріях UK\n")

    for cat_id, (slug, uk_name) in CATEGORIES.items():
        print(f"## {uk_name}")
        print(f"<!-- category_id: {cat_id}, slug: {slug} -->\n")

        if cat_id in cat_products:
            product_ids = cat_products[cat_id]
            names = extract_product_names(sql_content, product_ids)

            if names:
                for _pid, name in sorted(names.items(), key=lambda x: x[1]):
                    print(f"- {name}")
            else:
                print("*Товари не знайдено*")
        else:
            print("*Товари не знайдено*")

        print("")


if __name__ == "__main__":
    main()
