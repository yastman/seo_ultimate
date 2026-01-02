#!/usr/bin/env python3
"""
restore_from_csv.py — Восстанавливает _clean.json из CSV семантики

Для категорий, у которых удалились ключи после auto-fix.
"""

import csv
import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SEMANTICS_CSV = PROJECT_ROOT / "Структура _Ultimate.csv"
CATEGORIES_DIR = PROJECT_ROOT / "categories"

# Mapping slug → CSV block name
SLUG_TO_CSV = {
    "mikrofibra-i-tryapki": "Микрофибра и тряпки",
    "shchetki-i-kisti": "Щетки и кисти",
    "mekhovye": "Меховые",
    "s-voskom": "С воском",
}

# Sub-block mappings (keywords under special sub-headers in "Наборы" section)
SLUG_TO_SUBBLOCKS = {
    "nabory-dlya-moyki": ["набор для мойки авто", "набор тряпок для машины"],
    "nabory-dlya-polirovki": ["набор кругов для полировки авто", "набор паст для полировки авто"],
    "nabory-dlya-khimchistki": ["набор для химчистки автомобиля", "набор для чистки салона авто"],
    "nabory-dlya-kozhi": ["набор для ухода за кожей авто"],
    "nabory-dlya-deteylinga": ["наборы для детейлинга", "набор кистей для детейлинга"],
    "podarochnye-nabory": ["подарочный набор для авто", "подарочные наборы для мужчин в машину"],
}

# Commercial modifiers
COMMERCIAL_MODIFIERS = ["купить", "цена", "заказать", "стоимость", "недорого", "оптом"]


def parse_csv_block(block_name: str) -> list[dict]:
    """Parse all keywords from a CSV block."""
    keywords = []
    current_block = None

    with open(SEMANTICS_CSV, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue

            phrase = row[0].strip()
            volume_str = row[2].strip() if len(row) > 2 else ""

            # Detect block headers
            for prefix in ["L1:", "L2:", "L3:", "SEO-Фильтр:"]:
                if phrase.startswith(prefix):
                    name = phrase.replace(prefix, "").strip()
                    if name == block_name:
                        current_block = name
                    elif current_block:
                        # Exit block
                        return keywords
                    break
            else:
                # Not a header - check if keyword
                if current_block and volume_str.isdigit():
                    keywords.append({"keyword": phrase, "volume": int(volume_str)})

    return keywords


def parse_csv_subblocks(subblock_names: list[str]) -> list[dict]:
    """Parse keywords from multiple sub-blocks in the 'Наборы' section."""
    keywords = []
    current_subblock = None
    in_nabory = False

    with open(SEMANTICS_CSV, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue

            phrase = row[0].strip()
            count_str = row[1].strip() if len(row) > 1 else ""
            volume_str = row[2].strip() if len(row) > 2 else ""

            # Check for "Наборы" parent block
            if phrase == "Наборы" and count_str:
                in_nabory = True
                continue

            # Exit Наборы section on next L1/L2/L3 header
            if in_nabory and phrase.startswith(("L1:", "L2:", "L3:")):
                break

            if not in_nabory:
                continue

            # Check for sub-block header (has count like "2/10" or "2")
            if count_str and ("/" in count_str or count_str.isdigit()) and not volume_str:
                # This is a sub-block header
                if phrase.lower() in [n.lower() for n in subblock_names]:
                    current_subblock = phrase
                else:
                    current_subblock = None
                continue

            # Parse keyword
            if current_subblock and volume_str.isdigit():
                keywords.append({"keyword": phrase, "volume": int(volume_str)})

    return keywords


def cluster_keywords(keywords: list[dict]) -> dict:
    """Cluster keywords into primary/secondary/supporting/commercial."""
    # Sort by volume descending
    sorted_kws = sorted(keywords, key=lambda x: x["volume"], reverse=True)

    primary = []
    secondary = []
    supporting = []
    commercial = []

    for kw in sorted_kws:
        keyword = kw["keyword"]
        volume = kw["volume"]

        # Skip zero volume
        if volume == 0:
            continue

        # Check if commercial
        is_commercial = any(mod in keyword.lower() for mod in COMMERCIAL_MODIFIERS)

        if is_commercial:
            commercial.append(
                {
                    "keyword": keyword,
                    "volume": volume,
                    "cluster": "commercial",
                    "use_in": "meta_only",
                }
            )
        elif volume >= 300:
            primary.append({"keyword": keyword, "volume": volume, "cluster": "main"})
        elif volume >= 50:
            secondary.append({"keyword": keyword, "volume": volume, "cluster": "related"})
        else:
            supporting.append({"keyword": keyword, "volume": volume, "cluster": "long_tail"})

    return {
        "primary": primary[:5],  # Top 5
        "secondary": secondary[:10],  # Top 10
        "supporting": supporting[:15],  # Top 15
        "commercial": commercial[:5],  # Top 5
    }


def restore_category(slug: str) -> bool:
    """Restore a category's _clean.json from CSV."""
    csv_name = SLUG_TO_CSV.get(slug)
    subblocks = SLUG_TO_SUBBLOCKS.get(slug)

    if not csv_name and not subblocks:
        print(f"  ❌ No CSV mapping for {slug}")
        return False

    # Parse CSV (either from main block or subblocks)
    if csv_name:
        keywords = parse_csv_block(csv_name)
        source = f"CSV block '{csv_name}'"
    else:
        keywords = parse_csv_subblocks(subblocks)
        source = f"sub-blocks {subblocks}"

    if not keywords:
        print(f"  ❌ No keywords in {source}")
        return False

    # Cluster
    clustered = cluster_keywords(keywords)

    # Read existing file
    clean_path = CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"
    if clean_path.exists():
        with open(clean_path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"slug": slug, "language": "ru"}

    # Update keywords
    data["keywords"] = clustered

    # Update stats
    total_kws = sum(
        len(clustered[cat]) for cat in ["primary", "secondary", "supporting", "commercial"]
    )
    total_vol = sum(kw["volume"] for cat in clustered.values() for kw in cat)
    data["stats"] = {"before": len(keywords), "after": total_kws, "total_volume": total_vol}

    # Add note
    data["restored_from"] = f"{source} ({len(keywords)} raw keywords)"

    # Write
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"  ✅ {slug}: {total_kws} keywords from {len(keywords)} raw")
    return True


def main():
    print("🔄 Restoring categories from CSV...\n")

    # Categories from main blocks
    main_block_cats = ["mikrofibra-i-tryapki", "shchetki-i-kisti", "mekhovye", "s-voskom"]

    # Categories from sub-blocks
    subblock_cats = [
        "nabory-dlya-moyki",
        "nabory-dlya-polirovki",
        "nabory-dlya-khimchistki",
        "nabory-dlya-kozhi",
        "nabory-dlya-deteylinga",
        "podarochnye-nabory",
    ]

    categories = main_block_cats + subblock_cats

    restored = 0
    for slug in categories:
        if restore_category(slug):
            restored += 1

    print(f"\n✅ Restored {restored}/{len(categories)} categories")


if __name__ == "__main__":
    main()
