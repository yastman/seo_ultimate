#!/usr/bin/env python3
"""
setup_all.py — Batch initialization of all categories from CSV

Reads the semantics CSV, extracts all L3 categories, and for each:
1. Auto-determines tier based on keywords count
2. Creates category folder structure
3. Creates task_{slug}.json checkpoint
4. Generates {slug}.json with keywords

Usage:
    python3 scripts/setup_all.py              # Init all with auto-tier
    python3 scripts/setup_all.py --dry-run    # Preview without creating
    python3 scripts/setup_all.py --force      # Overwrite existing

Tier auto-detection:
    >30 keywords  → Tier A (important category)
    10-30 keywords → Tier B (standard)
    <10 keywords  → Tier C (small)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


# Add scripts to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from parse_semantics_to_json import (  # noqa: E402
    L3_TO_SLUG,
    SEMANTICS_CSV,
    generate_full_json,
    read_semantics_csv,
)


# =============================================================================
# Constants
# =============================================================================

PROJECT_ROOT = SCRIPT_DIR.parent
CATEGORIES_DIR = PROJECT_ROOT / "categories"

TIER_THRESHOLDS = {
    "A": 30,  # >30 keywords
    "B": 10,  # 10-30 keywords
    "C": 0,  # <10 keywords
}

CATEGORY_SUBDIRS = ["data", "content", "meta", "competitors", "deliverables", "research"]


# =============================================================================
# Core Functions
# =============================================================================


def auto_detect_tier(keywords_count: int) -> str:
    """
    Auto-detect tier based on keywords count.

    Args:
        keywords_count: Number of keywords in category

    Returns:
        Tier string: "A", "B", or "C"
    """
    if keywords_count > TIER_THRESHOLDS["A"]:
        return "A"
    elif keywords_count >= TIER_THRESHOLDS["B"]:
        return "B"
    else:
        return "C"


def create_category_folders(slug: str, dry_run: bool = False) -> Path:
    """
    Create category folder structure.

    Args:
        slug: Category slug (e.g., "aktivnaya-pena")
        dry_run: If True, don't actually create

    Returns:
        Path to category root
    """
    category_path = CATEGORIES_DIR / slug

    if not dry_run:
        for subdir in CATEGORY_SUBDIRS:
            (category_path / subdir).mkdir(parents=True, exist_ok=True)

    return category_path


def create_task_file(slug: str, tier: str, keywords_count: int, dry_run: bool = False) -> Path:
    """
    Create task_{slug}.json checkpoint file.

    Args:
        slug: Category slug
        tier: Tier (A/B/C)
        keywords_count: Number of keywords
        dry_run: If True, don't actually create

    Returns:
        Path to task file
    """
    task_file = PROJECT_ROOT / f"task_{slug}.json"

    task_data = {
        "slug": slug,
        "tier": tier,
        "keywords_count": keywords_count,
        "created_at": datetime.now().isoformat(),
        "current_stage": "prepare",
        "stages": {
            "prepare": "completed",  # Folders + Keywords JSON (done by this script)
            "produce": "pending",  # Content RU + Meta
            "deliver": "pending",  # Validation + Package
        },
        "paths": {
            "data": f"categories/{slug}/data/{slug}.json",
            "content_ru": f"categories/{slug}/content/{slug}_ru.md",
            "meta": f"categories/{slug}/meta/{slug}_meta.json",
            "deliverables": f"categories/{slug}/deliverables/",
        },
    }

    if not dry_run:
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)

    return task_file


def create_keywords_json(
    slug: str, tier: str, keywords_raw: list[dict], dry_run: bool = False
) -> Path | None:
    """
    Generate keywords JSON for category.

    Args:
        slug: Category slug
        tier: Tier (A/B/C)
        keywords_raw: Raw keywords list from CSV
        dry_run: If True, don't actually create

    Returns:
        Path to JSON file or None
    """
    if not keywords_raw:
        return None

    json_path = CATEGORIES_DIR / slug / "data" / f"{slug}.json"

    if not dry_run:
        full_json = generate_full_json(slug, tier, keywords_raw)

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(full_json, f, ensure_ascii=False, indent=2)

    return json_path


def get_all_categories_with_keywords() -> dict[str, list[dict]]:
    """
    Read CSV and get all categories with their keywords.

    Returns:
        Dict: {slug: [keywords_list]}
    """
    result = {}

    # Read all categories from CSV at once
    all_categories = read_semantics_csv(str(SEMANTICS_CSV))

    # Map L3 names to slugs
    for l3_name, keywords in all_categories.items():
        if l3_name in L3_TO_SLUG:
            slug = L3_TO_SLUG[l3_name]
            result[slug] = keywords

    return result


def setup_category(
    slug: str, keywords: list[dict], force: bool = False, dry_run: bool = False
) -> dict:
    """
    Setup single category: folders + task file + keywords JSON.

    Args:
        slug: Category slug
        keywords: Keywords list
        force: Overwrite existing
        dry_run: Preview mode

    Returns:
        Dict with setup results
    """
    keywords_count = len(keywords)
    tier = auto_detect_tier(keywords_count)

    # Check if exists
    category_path = CATEGORIES_DIR / slug
    task_file = PROJECT_ROOT / f"task_{slug}.json"

    exists = category_path.exists() or task_file.exists()

    if exists and not force and not dry_run:
        return {
            "slug": slug,
            "status": "skipped",
            "reason": "exists",
            "tier": tier,
            "keywords": keywords_count,
        }

    # Create everything
    create_category_folders(slug, dry_run)
    create_task_file(slug, tier, keywords_count, dry_run)
    create_keywords_json(slug, tier, keywords, dry_run)

    return {
        "slug": slug,
        "status": "created" if not dry_run else "dry_run",
        "tier": tier,
        "keywords": keywords_count,
        "paths": {
            "folder": str(category_path),
            "task": str(task_file),
            "json": str(CATEGORIES_DIR / slug / "data" / f"{slug}.json"),
        },
    }


def setup_all(force: bool = False, dry_run: bool = False) -> list[dict]:
    """
    Setup all categories from CSV.

    Args:
        force: Overwrite existing
        dry_run: Preview mode

    Returns:
        List of setup results
    """
    categories = get_all_categories_with_keywords()
    results = []

    for slug, keywords in categories.items():
        result = setup_category(slug, keywords, force, dry_run)
        results.append(result)

    return results


def print_summary(results: list[dict], dry_run: bool = False):
    """Print setup summary."""

    mode = "[DRY RUN] " if dry_run else ""

    print(f"\n{mode}=== Setup Summary ===\n")

    # Group by tier
    by_tier = {"A": [], "B": [], "C": []}
    for r in results:
        by_tier[r["tier"]].append(r)

    # Print table
    print(f"{'Slug':<25} {'Keywords':>8} {'Tier':>5} {'Status':>10}")
    print("-" * 55)

    for tier in ["A", "B", "C"]:
        for r in by_tier[tier]:
            status = r["status"]
            if status == "skipped":
                status = f"⏭ {status}"
            elif status == "created":
                status = f"✓ {status}"
            else:
                status = f"○ {status}"
            print(f"{r['slug']:<25} {r['keywords']:>8} {r['tier']:>5} {status:>10}")

    print("-" * 55)

    # Stats
    created = len([r for r in results if r["status"] == "created"])
    skipped = len([r for r in results if r["status"] == "skipped"])
    dry = len([r for r in results if r["status"] == "dry_run"])

    tier_counts = {t: len(by_tier[t]) for t in ["A", "B", "C"]}

    print(f"\nTiers: {tier_counts['A']}×A, {tier_counts['B']}×B, {tier_counts['C']}×C")

    if dry_run:
        print(f"Would create: {dry} categories")
    else:
        print(f"Created: {created}, Skipped: {skipped}")

    print()


# =============================================================================
# CLI
# =============================================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Batch initialize all categories from CSV")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating files")
    parser.add_argument("--force", action="store_true", help="Overwrite existing categories")
    parser.add_argument("--list", action="store_true", help="Just list categories and exit")

    args = parser.parse_args(argv)

    if args.list:
        categories = get_all_categories_with_keywords()
        print("\n=== Categories from CSV ===\n")
        for slug, kw in sorted(categories.items(), key=lambda x: -len(x[1])):
            tier = auto_detect_tier(len(kw))
            print(f"{slug:<25} {len(kw):>3} keywords → Tier {tier}")
        print(f"\nTotal: {len(categories)} categories")
        return 0

    results = setup_all(force=args.force, dry_run=args.dry_run)
    print_summary(results, dry_run=args.dry_run)

    if not args.dry_run:
        print("✅ All categories initialized!")
        print("\nNext step:")
        print('  "контент для aktivnaya-pena"')

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
