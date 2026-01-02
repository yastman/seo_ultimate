#!/usr/bin/env python3
"""Extract products with descriptions by category from SQL backup."""

import re
import html
import sys

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
    453: ("gubki-i-varezhki", "Губки та рукавиці"),
}

def clean_html(text):
    """Remove HTML tags and decode entities."""
    text = html.unescape(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_product_to_category(sql_content):
    """Extract product_id -> category_id mapping."""
    pattern = r'\((\d+),(\d+),[01]\)'
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

def extract_product_data(sql_content, product_ids):
    """Extract product name and description for given IDs (UK language_id=1)."""
    products = {}

    for pid in product_ids:
        # Pattern for oc_product_description: (product_id, language_id, 'name', 'description', ...)
        # Looking for: (pid,1,'name','description'
        pattern = rf"\({pid},1,'([^']*(?:''[^']*)*)','([^']*(?:''[^']*)*)',"
        match = re.search(pattern, sql_content)

        if match:
            name = match.group(1).replace("''", "'")
            desc = match.group(2).replace("''", "'")

            # Skip URLs and short names
            if not name.startswith('http') and len(name) > 10:
                products[pid] = {
                    'name': name,
                    'description': clean_html(desc)[:500] if desc else ''
                }

    return products

def main():
    print("Loading SQL backup...", file=sys.stderr)
    with open(SQL_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        sql_content = f.read()

    print("Extracting product categories...", file=sys.stderr)
    cat_products = extract_product_to_category(sql_content)

    print("# Товари по категоріях (з описами)\n")

    for cat_id, (slug, uk_name) in CATEGORIES.items():
        print(f"## {uk_name}")
        print(f"<!-- category_id: {cat_id}, slug: {slug} -->\n")

        if cat_id in cat_products:
            product_ids = cat_products[cat_id]
            products = extract_product_data(sql_content, product_ids)

            if products:
                for pid, data in sorted(products.items(), key=lambda x: x[1]['name']):
                    print(f"### {data['name']}")
                    if data['description']:
                        print(f"{data['description'][:300]}...")
                    print()
            else:
                print("*Товари не знайдено*\n")
        else:
            print("*Товари не знайдено*\n")

if __name__ == "__main__":
    main()
