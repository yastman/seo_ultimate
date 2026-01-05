#!/usr/bin/env python3
"""
products.py — Tool for extracting product data and finding category IDs.

Combines functionality of:
- extract_products.py
- extract_products_with_desc.py
- find_category_id.py

Usage:
    python scripts/products.py list [--desc]   # List products by category
    python scripts/products.py find "Query"    # Find category ID by name
"""

import argparse
import html
import re
import sys
from pathlib import Path

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_FILE = PROJECT_ROOT / "ultimate_net_ua_backup.sql"

# Category mapping: category_id -> (slug, uk_name)
CATEGORIES_MAP = {
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


# =============================================================================
# Helpers
# =============================================================================


def clean_html(text):
    """Remove HTML tags and decode entities."""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def check_sql_file():
    if not SQL_FILE.exists():
        print(f"❌ SQL backup not found at {SQL_FILE}")
        sys.exit(1)
    return SQL_FILE.read_text(encoding="utf-8", errors="ignore")


# =============================================================================
# Logic: List Products
# =============================================================================


def extract_product_to_category(sql_content):
    """Extract product_id -> category_id mapping."""
    pattern = r"\((\d+),(\d+),[01]\)"
    matches = re.findall(pattern, sql_content)

    cat_products = {}
    for product_id, category_id in matches:
        cat_id = int(category_id)
        prod_id = int(product_id)
        if cat_id in CATEGORIES_MAP:
            if cat_id not in cat_products:
                cat_products[cat_id] = []
            cat_products[cat_id].append(prod_id)

    return cat_products


def extract_product_data(sql_content, product_ids, include_desc=False):
    """Extract product name and description."""
    products = {}

    for pid in product_ids:
        # Patter: (pid, 1, 'name', 'desc'...)
        # We try to match robustly
        pattern = rf"\({pid},1,'([^']*(?:''[^']*)*)'"
        if include_desc:
            pattern += r",'([^']*(?:''[^']*)*)'"

        match = re.search(pattern, sql_content)

        if match:
            name = match.group(1).replace("''", "'")
            desc = ""
            if include_desc:
                desc = match.group(2).replace("''", "'")
                desc = clean_html(desc)[:300] + "..." if len(desc) > 300 else clean_html(desc)

            # Skip URLs and extremely short trash
            if not name.startswith("http") and len(name) > 3:
                products[pid] = {"name": name, "desc": desc}

    return products


def list_products(include_desc=False):
    print("Loading SQL...")
    content = check_sql_file()

    cat_products = extract_product_to_category(content)

    print("# Products by Category (UK)\n")

    for cat_id, (_slug, uk_name) in CATEGORIES_MAP.items():
        print(f"## {uk_name} (ID: {cat_id})")

        if cat_id in cat_products:
            pids = cat_products[cat_id]
            products = extract_product_data(content, pids, include_desc)

            if products:
                # Sort by name
                for _pid, data in sorted(products.items(), key=lambda x: x[1]["name"]):
                    print(f"- **{data['name']}**")
                    if include_desc and data["desc"]:
                        print(f"  {data['desc']}")
                    if include_desc:
                        print()
            else:
                print("*No products found*")
        else:
            print("*No products found*")
        print()


# =============================================================================
# Logic: Find Category ID
# =============================================================================


def find_category_id(search_term):
    content = check_sql_file()

    # Pattern: (ID,1,'Name'...)
    # We construct regex safely
    safe_term = re.escape(search_term)
    pattern = r"\((\d+),1,'([^']*" + safe_term + r"[^']*)"

    matches = re.findall(pattern, content, re.IGNORECASE)

    print(f"🔎 Results for '{search_term}':")
    if matches:
        for cat_id, name in matches:
            print(f"   ID: {cat_id:<5} Name: {name}")
    else:
        print("   No matches found.")


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Products & Categories SQL Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: list
    p_list = subparsers.add_parser("list", help="List products by category")
    p_list.add_argument("--desc", action="store_true", help="Include descriptions")

    # Command: find
    p_find = subparsers.add_parser("find", help="Find category ID by name")
    p_find.add_argument("query", help="Search query (e.g. 'Торнадор')")

    args = parser.parse_args()

    if args.command == "list":
        list_products(include_desc=args.desc)
    elif args.command == "find":
        find_category_id(args.query)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
