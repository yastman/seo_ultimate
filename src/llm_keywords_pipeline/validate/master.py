#!/usr/bin/env python3
"""Валидация master CSV файла семантики."""

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEFAULT_CSV = ROOT / "data" / "ru_semantics_master.csv"
CATEGORIES_DIR = ROOT / "categories"

REQUIRED_COLUMNS = {"keyword", "volume", "category", "type", "use_in"}
VALID_TYPES = {"keyword", "synonym"}
VALID_USE_IN = {"", "meta_only"}


def load_master_csv(csv_path: Path) -> list[dict]:
    """Загружает CSV и возвращает список словарей."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def validate_columns(rows: list[dict]) -> list[str]:
    """Проверяет наличие всех обязательных колонок."""
    if not rows:
        return ["CSV is empty"]

    actual = set(rows[0].keys())
    missing = REQUIRED_COLUMNS - actual
    if missing:
        return [f"Missing columns: {', '.join(sorted(missing))}"]
    return []


def validate_categories_exist(rows: list[dict], categories_dir: Path) -> list[str]:
    """Проверяет существование категорий."""
    errors = []
    categories = {row["category"] for row in rows}

    for cat in categories:
        if cat == "uncategorized":
            continue
        cat_path = categories_dir / cat
        if not cat_path.exists():
            # Check nested paths
            found = list(categories_dir.rglob(cat))
            if not found:
                errors.append(f"Category not found: {cat}")
    return errors


def validate_no_duplicates(rows: list[dict]) -> list[str]:
    """Проверяет отсутствие дубликатов ключей."""
    keywords = [row["keyword"].lower().strip() for row in rows]
    counts = Counter(keywords)
    duplicates = [kw for kw, count in counts.items() if count > 1]

    if duplicates:
        return [f"Duplicate keyword: {kw}" for kw in duplicates[:10]]  # Limit to 10
    return []


def validate_types(rows: list[dict]) -> list[str]:
    """Проверяет валидность поля type."""
    errors = []
    for i, row in enumerate(rows, 1):
        if row.get("type", "") not in VALID_TYPES:
            errors.append(f"Row {i}: Invalid type '{row.get('type')}' for '{row['keyword']}'")
    return errors[:10]


def validate_volumes(rows: list[dict]) -> list[str]:
    """Проверяет валидность поля volume."""
    errors = []
    for i, row in enumerate(rows, 1):
        vol = row.get("volume", "")
        try:
            v = int(vol)
            if v < 0:
                errors.append(f"Row {i}: Negative volume {v} for '{row['keyword']}'")
        except ValueError:
            errors.append(f"Row {i}: Invalid volume '{vol}' for '{row['keyword']}'")
    return errors[:10]


def validate_has_keywords(rows: list[dict]) -> list[str]:
    """Проверяет что каждая категория имеет минимум 1 keyword."""
    from collections import defaultdict

    by_category = defaultdict(set)
    for row in rows:
        by_category[row["category"]].add(row["type"])

    errors = []
    for cat, types in by_category.items():
        if cat == "uncategorized":
            continue
        if "keyword" not in types:
            errors.append(f"Category '{cat}' has no keywords, only synonyms")
    return errors


def validate_use_in(rows: list[dict]) -> list[str]:
    """Проверяет валидность поля use_in."""
    errors = []
    for i, row in enumerate(rows, 1):
        use_in = row.get("use_in", "")
        if use_in not in VALID_USE_IN:
            errors.append(f"Row {i}: Invalid use_in '{use_in}' for '{row['keyword']}'")
    return errors[:10]


def validate(csv_path: Path, categories_dir: Path) -> tuple[list[str], list[str]]:
    """Запускает все проверки. Возвращает (errors, warnings)."""
    errors = []
    warnings = []

    try:
        rows = load_master_csv(csv_path)
    except FileNotFoundError as e:
        return [str(e)], []

    errors.extend(validate_columns(rows))
    if errors:
        return errors, warnings  # Can't continue without columns

    errors.extend(validate_no_duplicates(rows))
    errors.extend(validate_types(rows))
    errors.extend(validate_volumes(rows))
    errors.extend(validate_use_in(rows))
    errors.extend(validate_categories_exist(rows, categories_dir))

    kw_errors = validate_has_keywords(rows)
    warnings.extend(kw_errors)  # Warnings, not errors

    return errors, warnings


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate master CSV")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to CSV")
    parser.add_argument("--categories", type=Path, default=CATEGORIES_DIR, help="Categories dir")
    args = parser.parse_args()

    print(f"Validating {args.csv}...")
    errors, warnings = validate(args.csv, args.categories)

    if warnings:
        print(f"\n⚠️  {len(warnings)} warnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n❌ {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n✅ Validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
