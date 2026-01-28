#!/usr/bin/env python3
"""Синхронизация master CSV → _clean.json файлы."""

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEFAULT_CSV = ROOT / "data" / "ru_semantics_master.csv"
CATEGORIES_DIR = ROOT / "categories"

PRESERVED_FIELDS = ["id", "name", "type", "parent_id", "entities", "micro_intents", "variations", "source"]


def load_master_csv(csv_path: Path) -> list[dict]:
    """Загружает master CSV."""
    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["volume"] = int(row["volume"])
            rows.append(row)
    return rows


def group_by_category(rows: list[dict]) -> dict[str, list[dict]]:
    """Группирует строки по категориям."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)
    return dict(grouped)


def find_clean_json_path(category: str, categories_dir: Path) -> Path | None:
    """Находит путь к _clean.json для категории."""
    # Direct path
    direct = categories_dir / category / "data" / f"{category}_clean.json"
    if direct.exists():
        return direct

    # Search nested
    for path in categories_dir.rglob(f"{category}_clean.json"):
        return path

    return None


def build_keywords_list(rows: list[dict]) -> list[dict]:
    """Строит список keywords из строк CSV."""
    keywords = []
    for row in rows:
        if row["type"] == "keyword":
            kw = {"keyword": row["keyword"], "volume": row["volume"]}
            if row.get("use_in"):
                kw["use_in"] = row["use_in"]
            keywords.append(kw)

    return sorted(keywords, key=lambda x: x["volume"], reverse=True)


def build_synonyms_list(rows: list[dict]) -> list[dict]:
    """Строит список synonyms из строк CSV."""
    synonyms = []
    for row in rows:
        if row["type"] == "synonym":
            syn = {"keyword": row["keyword"], "volume": row["volume"]}
            if row.get("use_in"):
                syn["use_in"] = row["use_in"]
            synonyms.append(syn)

    return sorted(synonyms, key=lambda x: x["volume"], reverse=True)


def sync_category(category: str, rows: list[dict], categories_dir: Path, dry_run: bool = True) -> dict:
    """Синхронизирует одну категорию. Возвращает статистику."""
    clean_path = find_clean_json_path(category, categories_dir)

    if not clean_path:
        # Create new file
        clean_path = categories_dir / category / "data" / f"{category}_clean.json"
        existing = {"id": category, "name": category}
    else:
        existing = json.loads(clean_path.read_text(encoding="utf-8"))

    # Build new keywords/synonyms
    new_keywords = build_keywords_list(rows)
    new_synonyms = build_synonyms_list(rows)

    # Stats
    old_kw_count = len(existing.get("keywords", []))
    old_syn_count = len(existing.get("synonyms", []))

    # Update
    updated = {}
    for field in PRESERVED_FIELDS:
        if field in existing:
            updated[field] = existing[field]

    updated["keywords"] = new_keywords
    updated["synonyms"] = new_synonyms

    stats = {
        "category": category,
        "keywords_before": old_kw_count,
        "keywords_after": len(new_keywords),
        "synonyms_before": old_syn_count,
        "synonyms_after": len(new_synonyms),
    }

    if not dry_run:
        clean_path.parent.mkdir(parents=True, exist_ok=True)
        clean_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sync master CSV to _clean.json files")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Master CSV path")
    parser.add_argument("--categories-dir", type=Path, default=CATEGORIES_DIR, help="Categories dir")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    parser.add_argument("--categories", type=str, help="Comma-separated list of categories to sync")
    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("🔍 DRY-RUN mode (use --apply to make changes)\n")
    else:
        print("📝 APPLYING changes\n")

    print(f"Loading {args.csv}...")
    rows = load_master_csv(args.csv)
    print(f"Loaded {len(rows)} rows")

    grouped = group_by_category(rows)
    print(f"Found {len(grouped)} categories\n")

    # Filter categories if specified
    if args.categories:
        filter_cats = set(args.categories.split(","))
        grouped = {k: v for k, v in grouped.items() if k in filter_cats}
        print(f"Filtering to {len(grouped)} categories\n")

    # Skip uncategorized
    if "uncategorized" in grouped:
        print(f"⚠️  Skipping {len(grouped['uncategorized'])} uncategorized keywords\n")
        del grouped["uncategorized"]

    # Sync each category
    total_stats = {"updated": 0, "kw_added": 0, "kw_removed": 0, "syn_added": 0, "syn_removed": 0}

    for category, cat_rows in sorted(grouped.items()):
        stats = sync_category(category, cat_rows, args.categories_dir, dry_run=dry_run)

        kw_diff = stats["keywords_after"] - stats["keywords_before"]
        syn_diff = stats["synonyms_after"] - stats["synonyms_before"]

        if kw_diff != 0 or syn_diff != 0:
            total_stats["updated"] += 1
            if kw_diff > 0:
                total_stats["kw_added"] += kw_diff
            else:
                total_stats["kw_removed"] += abs(kw_diff)
            if syn_diff > 0:
                total_stats["syn_added"] += syn_diff
            else:
                total_stats["syn_removed"] += abs(syn_diff)

            print(
                f"  {category}: kw {stats['keywords_before']}→{stats['keywords_after']}, "
                f"syn {stats['synonyms_before']}→{stats['synonyms_after']}"
            )

    print(f"\n{'Would update' if dry_run else 'Updated'}: {total_stats['updated']} categories")
    print(f"Keywords: +{total_stats['kw_added']} / -{total_stats['kw_removed']}")
    print(f"Synonyms: +{total_stats['syn_added']} / -{total_stats['syn_removed']}")

    if dry_run:
        print("\n💡 Run with --apply to make changes")


if __name__ == "__main__":
    main()
