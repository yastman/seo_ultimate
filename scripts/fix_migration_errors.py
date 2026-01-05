import csv
import shutil
from pathlib import Path


CSV_FILE = Path(
    "c:/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт/Структура _Ultimate.csv"
)
BACKUP_FILE = CSV_FILE.parent / "Структура _Ultimate_pre_fix.csv"

# Explicit manual fixes for missed items
FIXES = [
    {
        "keys": ["автошампунь для ручной мойки", "автомобильный шампунь для ручной мойки"],
        "target": "L3: Шампуни для ручной мойки",
    },
    {
        "keys": [
            "автохимия от производителя",
            "автохимия производство",
            "автохимия поставщики",
            "производители автохимии украина",
        ],
        "target": "Special: Опт и B2B",
    },
]


def fix_csv():
    print("🔧 Fixing migration errors...")

    if not CSV_FILE.exists():
        print("CSV not found.")
        return

    # Backup
    shutil.copy2(CSV_FILE, BACKUP_FILE)

    # Read all data into memory structure
    # Category -> List of rows
    data = []
    current_cat_name = "ROOT"
    current_rows = []

    with open(CSV_FILE, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                current_rows.append(row)
                continue

            col1 = row[0].strip()
            # Simple heuristic for category header: starts with L1/L2/L3/Filter etc AND has no stats in col3 usually
            # But consistent with previous scripts
            lower = col1.lower()
            if (
                lower.startswith("l1:")
                or lower.startswith("l2:")
                or lower.startswith("l3:")
                or lower.startswith("filter:")
                or lower.startswith("seo-")
                or lower.startswith("cluster:")
                or lower.startswith("категория")
                or lower.startswith("special:")
                or lower.startswith("спец:")
            ):
                # Save previous block
                data.append({"cat": current_cat_name, "rows": current_rows})
                current_cat_name = col1
                current_rows = [row]  # Start new block with header
            else:
                current_rows.append(row)

    # Append last block
    data.append({"cat": current_cat_name, "rows": current_rows})

    # Now execute moves
    for fix in FIXES:
        target_cat = fix["target"]
        keys_to_move = fix["keys"]

        # 1. Find if target category exists
        target_idx = -1
        for i, block in enumerate(data):
            if block["cat"].lower().strip() == target_cat.lower().strip():
                target_idx = i
                break

        # Create if not exists
        if target_idx == -1:
            print(f"Creating category: {target_cat}")
            new_block = {"cat": target_cat, "rows": [[target_cat, "", ""], ["", "", ""]]}
            data.append(new_block)
            target_idx = len(data) - 1

        # 2. Find and move keys
        for key in keys_to_move:
            moved = False
            for block in data:
                # Don't take from target itself
                if block["cat"] == target_cat:
                    continue

                # Look for key in rows (skipping header row 0)
                rows_to_remove = []
                for r_idx, row in enumerate(block["rows"]):
                    if r_idx == 0:
                        continue  # Skip header
                    if not row:
                        continue

                    if row[0].strip().lower() == key.lower():
                        print(f"Moving '{key}' from '{block['cat']}' to '{target_cat}'")
                        # Add to target
                        data[target_idx]["rows"].append(row)
                        rows_to_remove.append(r_idx)
                        moved = True

                # Remove from source (in reverse order to keep indices valid)
                for r_idx in sorted(rows_to_remove, reverse=True):
                    del block["rows"][r_idx]

            if not moved:
                print(f"⚠️ Key not found in source: '{key}' (already moved?)")

    # Save
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for block in data:
            writer.writerows(block["rows"])

    print("✅ Logic fixes applied.")


if __name__ == "__main__":
    fix_csv()
