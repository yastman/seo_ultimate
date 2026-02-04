import csv
import re
import shutil
from collections import OrderedDict
from pathlib import Path

# Paths
BASE_DIR = Path("c:/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт")
REGISTRY_FILE = BASE_DIR / "tasks/reports/KEYWORD_MIGRATION_REGISTRY.md"
CSV_FILE = BASE_DIR / "Структура _Ultimate.csv"
BACKUP_CSV = BASE_DIR / "Структура _Ultimate_backup.csv"


def parse_registry(file_path):
    """Parses the migration registry markdown table."""
    migrations = []
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    # Regex to find table rows: | key | vol | source | target |
    # Ignore separator rows |---|---|...
    row_pattern = re.compile(r"\|\s*(.+?)\s*\|\s*(\d+|~?\d+.*)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|")

    for line in lines:
        if "---" in line:
            continue
        match = row_pattern.search(line)
        if match:
            key = match.group(1).strip()
            # vol = match.group(2).strip()
            # source = match.group(3).strip()
            target = match.group(4).strip()

            # Skip header
            if key.lower() == "ключ" or key.startswith("---"):
                continue

            # Clean up target (remove "(General)", "(создать)", etc)
            target_clean = re.sub(r"\s*\(.*?\)", "", target).strip()

            migrations.append({"key": key, "target": target_clean, "target_raw": target})
    return migrations


def load_csv(file_path):
    """Loads CSV into an OrderedDict of Category -> Rows."""
    category_map = OrderedDict()
    current_category = "ROOT"
    category_map[current_category] = []

    with open(file_path, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                category_map[current_category].append(row)
                continue

            col1 = row[0].strip()
            # Check if it's a category header
            # L1, L2, L3, Filter, Category
            is_header = False
            lower_col1 = col1.lower()
            if (
                lower_col1.startswith("l1:")
                or lower_col1.startswith("l2:")
                or lower_col1.startswith("l3:")
                or lower_col1.startswith("filter:")
                or lower_col1.startswith("seo-фильтр:")
                or lower_col1.startswith("seo-filter:")
                or lower_col1.startswith("категория")
                or lower_col1.startswith("cluster:")
                or lower_col1.startswith("спец:")
                or lower_col1.startswith("special:")
            ):
                is_header = True

            if is_header:
                current_category = col1
                if current_category not in category_map:
                    category_map[current_category] = []
                # Add header row to the new category list
                category_map[current_category].append(row)
            else:
                # Add to current category
                category_map[current_category].append(row)

    return category_map


def find_category_key(category_map, target_name):
    """Finds existing category key matching target_name (loose match)."""
    target_lower = target_name.lower()

    # Direct match first
    for cat in category_map:
        if cat.lower() == target_lower:
            return cat

    # Fuzzy match: "L2: Полировальные машинки" vs "L2: Полировальные машинки,1/46,"
    # Extract clean name from csv header
    for cat in category_map:
        # clean_cat = re.sub(r",.*", "", cat) # Remove csv parts
        if target_lower in cat.lower():
            return cat

    return None


def create_category(category_map, target_name, parent_hint=None):
    """Creates a new category in the map."""
    print(f"Creating new category: {target_name}")
    # Initialize list with header row
    # In CSV, headers usually have "Name,Count," format
    # We will just set Name,, for now
    header_row = [target_name, "", ""]
    category_map[target_name] = [header_row, ["", "", ""]]  # Add header and an empty line
    return target_name


def migrate_keywords():
    print("🚀 Starting Keyword Migration...")

    # 1. Parse Migrations
    migrations = parse_registry(REGISTRY_FILE)
    print(f"Found {len(migrations)} migration rules.")

    # 2. Load CSV
    if not CSV_FILE.exists():
        print("CSV file not found!")
        return

    shutil.copy2(CSV_FILE, BACKUP_CSV)
    print(f"Backup created at {BACKUP_CSV.name}")

    category_map = load_csv(CSV_FILE)

    # 3. Apply Migrations
    migrated_count = 0
    not_found_count = 0

    for rule in migrations:
        key = rule["key"]
        target_name = rule["target"]

        # Find the keyword in current structure
        found_source_cat = None
        found_row = None
        found_index = -1

        for cat, rows in category_map.items():
            for i, row in enumerate(rows):
                if row and row[0].strip().lower() == key.lower():
                    found_source_cat = cat
                    found_row = row
                    found_index = i
                    break
            if found_source_cat:
                break

        if not found_source_cat:
            # print(f"Key not found: {key}")
            not_found_count += 1
            continue

        # Remove from source
        del category_map[found_source_cat][found_index]

        # Add to target
        target_cat_key = find_category_key(category_map, target_name)

        if not target_cat_key:
            # Create if doesn't exist
            # Note: This simply appends to the end of OrderedDict.
            # Ideally we'd insert it in a smart place, but that's hard.
            target_cat_key = create_category(category_map, target_name)

        category_map[target_cat_key].append(found_row)
        migrated_count += 1
        # print(f"Moved '{key}' from '{found_source_cat}' -> '{target_cat_key}'")

    print(f"✅ Migrated {migrated_count} keywords.")
    print(f"⚠️ Skipped {not_found_count} keywords (not found in source).")

    # 4. Save CSV
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for _, rows in category_map.items():
            writer.writerows(rows)

    print("💾 CSV Saved successfully.")


if __name__ == "__main__":
    migrate_keywords()
