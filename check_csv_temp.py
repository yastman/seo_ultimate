import csv
from pathlib import Path


csv_path = Path(
    r"c:\Users\user\Documents\Сайты\Ultimate.net.ua\сео_для_категорий_ультимейт\data\Структура  Ultimate финал - Лист2.csv"
)


def check_csv():
    print(f"Checking file: {csv_path}")
    if not csv_path.exists():
        print("ERROR: File not found")
        return

    l3_count = 0
    keyword_count = 0
    rows_checked = 0

    try:
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                rows_checked += 1
                if not row:
                    continue

                col0 = row[0].strip()

                if col0.startswith("L3:"):
                    l3_count += 1
                elif col0.startswith("L1:") or col0.startswith("L2:"):
                    pass
                elif col0:  # Assume keyword
                    keyword_count += 1
                    # Check volume column if it exists
                    if len(row) > 2:
                        vol = row[2].strip()
                        if vol and not vol.isdigit():
                            print(
                                f"WARNING: Line {i + 1} - Volume '{vol}' is not a digit for keyword '{col0}'"
                            )

        print("SUCCESS: CSV Read Completed")
        print(f"Total Lines: {rows_checked}")
        print(f"L3 Categories Found: {l3_count}")
        print(f"Keywords Found: {keyword_count}")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")


if __name__ == "__main__":
    check_csv()
