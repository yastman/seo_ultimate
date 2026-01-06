#!/usr/bin/env python3
"""
MEGA URL Aggregation — Stage -4 (V3.1 Cluster-First)

Конкатенирует cluster-level URLs из всех категорий в глобальный MEGA пул.

V3.1 ИЗМЕНЕНИЕ:
- НЕ извлекает URLs из SERP напрямую
- ВМЕСТО этого конкатенирует cluster_urls*.txt|csv из categories/*/competitors/
- Применяет глобальную дедупликацию
- Формирует mega_urls.txt для единого Screaming Frog запуска

Workflow:
1. Найти все categories/*/competitors/cluster_urls_raw.txt
2. Найти все categories/*/competitors/cluster_urls.txt
3. Найти все categories/*/competitors/cluster_urls_map.csv
4. Конкатенировать с дедупликацией
5. Сохранить в data/mega/

Exit codes:
- 0: OK (≥30 URLs extracted)
- 1: Warning (10-29 URLs)
- 2: Fail (<10 URLs or no cluster files found)
"""

from __future__ import annotations

import argparse
import csv as csv_module
from pathlib import Path

# ============================================================================
# FUNCTIONS
# ============================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MEGA URL Aggregation (V3.1 Cluster-First)")
    parser.add_argument(
        "--categories-dir",
        type=str,
        default="categories",
        help="Categories directory (default: categories)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/mega",
        help="Output directory (default: data/mega)",
    )
    parser.add_argument(
        "--min-urls",
        type=int,
        default=30,
        help="Minimum total URLs required (default: 30)",
    )
    return parser


def resolve_dir(base_dir: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()


def find_cluster_files(categories_dir: Path) -> dict[str, dict[str, Path | None]]:
    """
    Находит все cluster files в categories/*/competitors/.

    Returns:
        {
            "aktivnaya-pena": {
                "raw": Path(...),
                "clean": Path(...),
                "map": Path(...)
            },
            ...
        }
    """
    cluster_files: dict[str, dict[str, Path | None]] = {}

    for category_dir in categories_dir.iterdir():
        if not category_dir.is_dir():
            continue

        slug = category_dir.name
        competitors_dir = category_dir / "competitors"

        if not competitors_dir.exists():
            continue

        raw_file = competitors_dir / "cluster_urls_raw.txt"
        clean_file = competitors_dir / "cluster_urls.txt"
        map_file = competitors_dir / "cluster_urls_map.csv"

        # Требуем минимум clean_file (TOP-N после фильтров)
        if clean_file.exists():
            cluster_files[slug] = {
                "raw": raw_file if raw_file.exists() else None,
                "clean": clean_file,
                "map": map_file if map_file.exists() else None,
            }

    return cluster_files


def read_urls_from_file(file_path: Path) -> list[str]:
    """Читает URLs из текстового файла."""
    if not file_path or not file_path.exists():
        return []

    urls = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if url and url.startswith("http"):
                urls.append(url)

    return urls


def normalize_url(url: str) -> str:
    """Нормализует URL для дедупликации."""
    url_lower = url.lower()
    # Убрать trailing slash
    if url_lower.endswith("/"):
        url_lower = url_lower[:-1]
    return url_lower


def aggregate_raw_urls(cluster_files: dict[str, dict[str, Path | None]]) -> list[str]:
    """
    Конкатенирует все cluster_urls_raw.txt.

    Returns:
        List of raw URLs (with duplicates, для диагностики)
    """
    all_raw = []

    for slug, files in cluster_files.items():
        if files["raw"]:
            urls = read_urls_from_file(files["raw"])
            all_raw.extend(urls)
            print(f"   {slug}: {len(urls)} raw URLs")

    return all_raw


def aggregate_clean_urls(cluster_files: dict[str, dict[str, Path | None]]) -> tuple[list[str], int]:
    """
    Конкатенирует все cluster_urls.txt с глобальной дедупликацией.

    Returns:
        (unique_urls, duplicates_removed)
    """
    url_map = {}  # normalized -> original

    for slug, files in cluster_files.items():
        urls = read_urls_from_file(files["clean"])

        for url in urls:
            url_normalized = normalize_url(url)

            # Сохраняем первую встреченную версию URL
            if url_normalized not in url_map:
                url_map[url_normalized] = url

        print(f"   {slug}: {len(urls)} clean URLs")

    unique_urls = list(url_map.values())
    duplicates_removed = sum(len(read_urls_from_file(f["clean"])) for f in cluster_files.values()) - len(unique_urls)

    return unique_urls, duplicates_removed


def aggregate_url_maps(cluster_files: dict[str, dict[str, Path | None]]) -> list[dict]:
    """
    Конкатенирует все cluster_urls_map.csv.

    Returns:
        [
            {"slug": "...", "cluster_name": "...", "seed_phrase": "...", ...},
            ...
        ]
    """
    all_mappings = []

    for slug, files in cluster_files.items():
        if not files["map"]:
            continue

        with files["map"].open("r", encoding="utf-8") as f:
            reader = csv_module.DictReader(f)

            for row in reader:
                all_mappings.append(row)

        with files["map"].open("r", encoding="utf-8") as f_count:
            print(f"   {slug}: {len(list(csv_module.DictReader(f_count)))} mappings")

    return all_mappings


def save_mega_files(output_dir: Path, raw_urls: list[str], clean_urls: list[str], url_mappings: list[dict]) -> None:
    """Сохраняет MEGA файлы."""
    # Создать output dir
    output_dir.mkdir(parents=True, exist_ok=True)

    mega_urls_raw = output_dir / "mega_urls_raw.txt"
    mega_urls = output_dir / "mega_urls.txt"
    mega_urls_map = output_dir / "mega_urls_map.csv"

    # 1. mega_urls_raw.txt (диагностика)
    with mega_urls_raw.open("w", encoding="utf-8") as f:
        for url in raw_urls:
            f.write(f"{url}\n")

    # 2. mega_urls.txt (для Screaming Frog)
    with mega_urls.open("w", encoding="utf-8") as f:
        for url in clean_urls:
            f.write(f"{url}\n")

    # 3. mega_urls_map.csv (маппинг)
    with mega_urls_map.open("w", encoding="utf-8", newline="") as f:
        if url_mappings:
            fieldnames = url_mappings[0].keys()
            writer = csv_module.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(url_mappings)

    print("\n✅ Saved MEGA files:")
    print(f"   - {mega_urls_raw} ({len(raw_urls)} URLs)")
    print(f"   - {mega_urls} ({len(clean_urls)} URLs)")
    print(f"   - {mega_urls_map} ({len(url_mappings)} mappings)")


# ============================================================================
# MAIN
# ============================================================================


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_dir = Path(__file__).resolve().parent.parent
    categories_dir = resolve_dir(base_dir, args.categories_dir)
    output_dir = resolve_dir(base_dir, args.output_dir)

    print("\n🎯 MEGA URL Aggregation (V3.1 Cluster-First)")
    print(f"   Categories dir: {categories_dir}")
    print(f"   Output dir: {output_dir}")
    print(f"   Min URLs threshold: {args.min_urls}")

    # 1. Найти cluster files
    print(f"\n📁 Finding cluster files in {categories_dir}...")
    if not categories_dir.exists():
        print(f"\n❌ ERROR: Categories directory does not exist: {categories_dir}")
        return 2

    cluster_files = find_cluster_files(categories_dir)

    if not cluster_files:
        print("\n❌ ERROR: No cluster files found!")
        print("   Expected: categories/*/competitors/cluster_urls.txt")
        print("   Run cluster_url_selection.py for each category first")
        return 2

    print(f"   ✅ Found cluster files for {len(cluster_files)} categories:")
    for slug in cluster_files:
        print(f"      - {slug}")

    # 2. Aggregate RAW URLs (диагностика)
    print("\n📊 Aggregating RAW URLs (cluster_urls_raw.txt)...")
    raw_urls = aggregate_raw_urls(cluster_files)
    print(f"   ✅ Total RAW URLs: {len(raw_urls)}")

    # 3. Aggregate CLEAN URLs (для Screaming Frog)
    print("\n🔄 Aggregating CLEAN URLs (cluster_urls.txt) with dedup...")
    clean_urls, duplicates = aggregate_clean_urls(cluster_files)
    print(f"   ✅ Total CLEAN URLs: {len(clean_urls)}")
    print(f"   ✅ Duplicates removed: {duplicates}")

    # 4. Aggregate URL mappings
    print("\n🗺️  Aggregating URL mappings (cluster_urls_map.csv)...")
    url_mappings = aggregate_url_maps(cluster_files)
    print(f"   ✅ Total mappings: {len(url_mappings)}")

    # 5. Save MEGA files
    print("\n💾 Saving MEGA files...")
    save_mega_files(output_dir, raw_urls, clean_urls, url_mappings)

    # 6. Validation
    print("\n📊 Summary:")
    print(f"   Categories: {len(cluster_files)}")
    print(f"   RAW URLs: {len(raw_urls)}")
    print(f"   CLEAN URLs (deduped): {len(clean_urls)}")
    print(f"   URL mappings: {len(url_mappings)}")
    if len(raw_urls) > 0:
        print(f"   Removal rate: {(len(raw_urls) - len(clean_urls)) / len(raw_urls) * 100:.1f}%")

    # Exit code
    if len(clean_urls) < 10:
        print(f"\n❌ FAIL: Only {len(clean_urls)} URLs (<10 minimum)")
        return 2
    elif len(clean_urls) < args.min_urls:
        print(f"\n⚠️  WARNING: Only {len(clean_urls)} URLs (<{args.min_urls} target)")
        return 1
    else:
        print(f"\n✅ SUCCESS: {len(clean_urls)} URLs extracted (≥{args.min_urls})")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
