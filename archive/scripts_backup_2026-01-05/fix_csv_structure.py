import csv
import shutil

from config import SEMANTICS_CSV


# import config

BACKUP_CSV = SEMANTICS_CSV.parent / f"{SEMANTICS_CSV.stem}_backup{SEMANTICS_CSV.suffix}"


def is_explicit_marker(col1: str, col2: str) -> bool:
    """Check if the row is a valid structural marker that should keep its count."""
    lower_col1 = col1.lower()
    if lower_col1.startswith("l1:") or lower_col1.startswith("l2:") or lower_col1.startswith("l3:"):
        return True
    if lower_col1.startswith("seo-фильтр:") or lower_col1.startswith("seo-filter:"):
        return True
    # Check for "категория" or "Категория"
    if lower_col1.startswith("категория"):
        return True

    # Check for X/Y format in col2 (e.g. 3/59)
    return "/" in col2

    return False


def fix_csv():
    print("🔍 Анализ CSV...")

    if not SEMANTICS_CSV.exists():
        print(f"Error: {SEMANTICS_CSV} not found.")
        return

    rows = []
    changes = []
    keeps = []

    with open(SEMANTICS_CSV, encoding="utf-8") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader, start=1):
            if not row:
                rows.append(row)
                continue

            # Ensure row has at least 3 columns to avoid index errors
            current_row = row[:]
            while len(current_row) < 3:
                current_row.append("")

            col1 = current_row[0].strip()
            col2 = current_row[1].strip()
            col3 = current_row[2].strip()

            # Logic:
            # Target: col2 is digit 1-4, col3 is empty/0
            # Exclude: Explicit markers

            should_fix = False

            if col2.isdigit():
                val = int(col2)
                if (
                    1 <= val <= 4
                    and (not col3 or col3 == "0")
                    and not is_explicit_marker(col1, col2)
                ):
                    should_fix = True

            if should_fix:
                original_col2 = current_row[1]
                current_row[1] = ""  # Clear col2
                changes.append(f"- {i}: {col1},{original_col2}, → {col1},,")
            elif col2 and col2.isdigit():
                # Check if it was in the range of interest (1-4) but kept
                val = int(col2)
                if 1 <= val <= 4:
                    keeps.append(f"- {i}: {col1},{col2},")

            rows.append(current_row)

    print(f"Найдено {len(changes) + len(keeps)} строк с col2 = 1-4")

    if keeps:
        print("\n✅ Оставляем (маркеры):")
        for k in keeps[:10]:  # Limit output
            print(f"  {k}")
        if len(keeps) > 10:
            print(f"  ... и еще {len(keeps) - 10}")

    if changes:
        print("\n⚠️ Исправляем (ложные заголовки):")
        for c in changes:
            print(f"  {c}")

        print(f"\n💾 Бэкап: {BACKUP_CSV.name}")
        shutil.copy2(SEMANTICS_CSV, BACKUP_CSV)

        print(f"✅ Сохраняем: {SEMANTICS_CSV.name} ({len(changes)} строк исправлено)")
        # Calculate newlines logic if needed, but csv module handles it with newline=''
        with open(SEMANTICS_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
    else:
        print("\n✅ Исправления не требуются.")


if __name__ == "__main__":
    fix_csv()
