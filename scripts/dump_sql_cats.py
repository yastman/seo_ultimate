import re
from pathlib import Path

# Paths
ROOT = Path("C:/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт")
SQL_FILE = ROOT / "data/dumps/ultimate_net_ua_backup.sql"
OUTPUT_FILE = ROOT / "sql_cats_dump.txt"


def main():
    if not SQL_FILE.exists():
        print("SQL not found")
        return

    with open(SQL_FILE, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Pattern: (ID, 1, 'Name'...)
    pattern = r"\((\d+),1,'([^']+)'"
    matches = re.findall(pattern, content)

    print(f"Found {len(matches)} potential categories. Writing to {OUTPUT_FILE}...")

    # Sort by ID
    matches.sort(key=lambda x: int(x[0]))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for cid, name in matches:
            # Filter out non-cyrillic or very short names to reduce noise?
            # Actually keep everything to be safe.
            f.write(f"{cid}: {name}\n")

    print("Done.")


if __name__ == "__main__":
    main()
