#!/usr/bin/env python3
"""Создание/обновление master CSV из существующих источников."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT / "categories"
DEFAULT_OUTPUT = ROOT / "data" / "ru_semantics_master.csv"

CSV_COLUMNS = ["keyword", "volume", "category", "type", "use_in"]


def find_clean_json_files(categories_dir: Path) -> list[Path]:
    """Находит все _clean.json файлы."""
    return list(categories_dir.rglob("*_clean.json"))


def extract_category_slug(clean_file: Path) -> str:
    """Извлекает slug категории из пути или содержимого файла."""
    # Try from file content first
    try:
        data = json.loads(clean_file.read_text(encoding="utf-8"))
        if "id" in data:
            return data["id"]
    except (json.JSONDecodeError, OSError):
        pass

    # Fallback to filename
    return clean_file.stem.replace("_clean", "")


def collect_from_clean_json(clean_file: Path) -> list[dict]:
    """Собирает ключи из одного _clean.json файла."""
    data = json.loads(clean_file.read_text(encoding="utf-8"))
    category = extract_category_slug(clean_file)
    rows = []

    # Keywords
    keywords = data.get("keywords", [])
    if isinstance(keywords, list):
        for kw in keywords:
            rows.append(
                {
                    "keyword": kw["keyword"],
                    "volume": kw.get("volume", 0),
                    "category": category,
                    "type": "keyword",
                    "use_in": kw.get("use_in", ""),
                }
            )
    elif isinstance(keywords, dict):
        # Legacy dict format
        for group in keywords.values():
            for kw in group:
                rows.append(
                    {
                        "keyword": kw["keyword"],
                        "volume": kw.get("volume", 0),
                        "category": category,
                        "type": "keyword",
                        "use_in": kw.get("use_in", ""),
                    }
                )

    # Synonyms
    for syn in data.get("synonyms", []):
        rows.append(
            {
                "keyword": syn["keyword"],
                "volume": syn.get("volume", 0),
                "category": category,
                "type": "synonym",
                "use_in": syn.get("use_in", ""),
            }
        )

    return rows


def load_excel_keywords(excel_path: Path) -> dict[str, int]:
    """Загружает ключи из Excel файла. Возвращает {keyword: volume}."""
    import pandas as pd

    df = pd.read_excel(excel_path)

    # Find keyword column
    kw_col = None
    for col in df.columns:
        if "ключ" in col.lower() or "keyword" in col.lower():
            kw_col = col
            break

    # Find volume column
    vol_col = None
    for col in df.columns:
        if "вхожд" in col.lower() or "volume" in col.lower() or "частот" in col.lower():
            vol_col = col
            break

    if not kw_col or not vol_col:
        raise ValueError(f"Cannot find keyword/volume columns in {excel_path}")

    result = {}
    for _, row in df.iterrows():
        kw = str(row[kw_col]).strip().lower()
        try:
            vol = int(row[vol_col])
        except (ValueError, TypeError):
            vol = 0
        if kw and kw != "nan":
            result[kw] = vol

    return result


def merge_keywords(existing: list[dict], excel_volumes: dict[str, int]) -> list[dict]:
    """Объединяет ключи: обновляет volume, добавляет новые, дедуплицирует."""
    # Index existing by keyword
    by_keyword = {}
    for row in existing:
        kw = row["keyword"].lower().strip()
        if kw not in by_keyword or row["volume"] > by_keyword[kw]["volume"]:
            by_keyword[kw] = row.copy()

    # Update volumes from Excel
    for kw, vol in excel_volumes.items():
        kw_lower = kw.lower().strip()
        if kw_lower in by_keyword:
            by_keyword[kw_lower]["volume"] = vol
        else:
            # New keyword from Excel
            by_keyword[kw_lower] = {
                "keyword": kw,
                "volume": vol,
                "category": "uncategorized",
                "type": "keyword",
                "use_in": "",
            }

    return list(by_keyword.values())


def save_master_csv(rows: list[dict], output_path: Path):
    """Сохраняет CSV, сортируя по category, затем по volume DESC."""
    # Sort
    sorted_rows = sorted(rows, key=lambda r: (r["category"], -r["volume"]))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(sorted_rows)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Create/update master CSV")
    parser.add_argument("--excel", nargs="*", type=Path, help="Excel files with frequency")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV path")
    parser.add_argument("--categories", type=Path, default=CATEGORIES_DIR, help="Categories dir")
    args = parser.parse_args()

    print("Collecting keywords from _clean.json files...")
    clean_files = find_clean_json_files(args.categories)
    print(f"   Found {len(clean_files)} _clean.json files")

    all_rows = []
    for f in clean_files:
        try:
            rows = collect_from_clean_json(f)
            all_rows.extend(rows)
        except Exception as e:
            print(f"   Warning: Error in {f.name}: {e}")

    print(f"   Collected {len(all_rows)} keywords")

    # Load Excel if provided
    excel_volumes = {}
    if args.excel:
        for excel_file in args.excel:
            print(f"\nLoading {excel_file.name}...")
            try:
                vols = load_excel_keywords(excel_file)
                excel_volumes.update(vols)
                print(f"   Loaded {len(vols)} keywords")
            except Exception as e:
                print(f"   Warning: Error: {e}")

    # Merge
    print("\nMerging...")
    merged = merge_keywords(all_rows, excel_volumes)
    print(f"   Result: {len(merged)} unique keywords")

    # Count uncategorized
    uncategorized = sum(1 for r in merged if r["category"] == "uncategorized")
    if uncategorized:
        print(f"   Warning: {uncategorized} uncategorized keywords")

    # Save
    save_master_csv(merged, args.output)
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()
