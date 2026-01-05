import re


SQL_FILE = "ultimate_net_ua_backup.sql"


def find_category_id(search_term):
    with open(SQL_FILE, encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Pattern: (ID,1,'Name'
    # Use simple string find or regex for the specific structure
    # escaping single quotes in search term just in case

    pattern = r"\((\d+),1,'([^']*" + re.escape(search_term) + r"[^']*)"
    matches = re.findall(pattern, content, re.IGNORECASE)

    if matches:
        print(f"--- Results for '{search_term}' ---")
        for cat_id, name in matches:
            print(f"ID: {cat_id}, Name: {name}")
    else:
        print(f"--- No results for '{search_term}' ---")


if __name__ == "__main__":
    find_category_id("Полірувальні")
    find_category_id("Нейтралізатор")
    find_category_id("Торнадор")
    find_category_id("Розпилювач")
    find_category_id("Пінник")
    find_category_id("Тригер")  # Trigger sprayers
    find_category_id("Пляшка")  # Bottles
