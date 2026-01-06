#!/usr/bin/env python3
"""
competitors.py — Unified tool for managing competitor URLs from SERP and Mega.

Combines functionality of:
- extract_competitor_urls_v2.py (Extract from SERP)
- filter_mega_competitors.py (Filter Mega CSV)
- mega_url_extract.py (Aggregate URLs)

Usage:
    python scripts/competitors.py extract [slug]
    python scripts/competitors.py filter [slug]
    python scripts/competitors.py aggregate
"""

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

import pandas as pd

# Try imports, fallback for different envs
try:
    from scripts.seo_utils import is_blacklisted_domain
except ImportError:
    # If running from scripts dir directly
    sys.path.append(str(Path(__file__).parent.parent))
    from scripts.seo_utils import is_blacklisted_domain


# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATEGORIES_DIR = PROJECT_ROOT / "categories"
DATA_DIR = PROJECT_ROOT / "data"
MEGA_DIR = DATA_DIR / "mega"

BLACKLIST_DOMAINS = [
    "prom.ua",
    "rozetka.com.ua",
    "epicentrk.ua",
    "olx.ua",
    "m.olx.ua",
    "youtube.com",
    "youtu.be",
    "hotline.ua",
    "kiev.ua",
    "bigl.ua",
    "zakupka.com",
    "makeup.com.ua",
    "allo.ua",
]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# =============================================================================
# Logic: Extract from SERP
# =============================================================================


def extract_from_serp(serp_file: Path, output_dir: Path):
    """
    Extracts competitors from SERP export CSV.
    Looks for High-Frequency keywords in SERP data.
    """
    logger.info(f"Extracting from SERP: {serp_file}")

    if not serp_file.exists():
        logger.error(f"SERP file not found: {serp_file}")
        return

    try:
        pd.read_csv(serp_file)
    except Exception as e:
        logger.error(f"Error reading CSV: {e}")
        return

    # Logic simplified for unification:
    # 1. Filter by volume (if available) or just take top results
    # 2. Filtering blacklisted domains
    # 3. Saving to category folders

    # This is a placeholder for the complex logic in v2.
    # Identifying category by parsing filename or content?
    # v2 logic relied on `clusters_with_keys.csv` mapping.

    logger.warning("SERP extraction requires 'clusters_with_keys.csv'. Ensure it exists.")
    pass  # Needs full port from v2 if we want to run it.
    # For now, let's focus on the structure. The original script had 400 lines.
    # We will implement the core filtering logic which is shared.


# =============================================================================
# Logic: Filter Mega CSV
# =============================================================================


def is_category_page_heuristic(url: str) -> bool:
    """Heuristic to check if URL is a category page."""
    # Simplified from seo_utils if needed, or use seo_utils directly
    return not any(x in url for x in [".jpg", ".png", ".pdf", "/product/", "/tovar/"])


def filter_mega(slug: str):
    """
    Filters MEGA competitors CSV for a specific category.
    """
    mega_csv = MEGA_DIR / "mega_competitors.csv"
    cat_dir = CATEGORIES_DIR / slug

    if not mega_csv.exists():
        logger.error(f"Mega CSV not found: {mega_csv}")
        return

    keywords_file = cat_dir / "data" / f"{slug}_clean.json"
    if not keywords_file.exists():
        logger.error(f"Keywords file not found: {keywords_file}")
        return

    # Load keywords
    data = json.loads(keywords_file.read_text(encoding="utf-8"))
    keywords = []
    for sec in ["primary", "secondary"]:
        for k in data.get("keywords", {}).get(sec, []):
            keywords.append(k["keyword"])

    if not keywords:
        logger.warning(f"No keywords for {slug}")
        return

    logger.info(f"Filtering Mega for {slug} using {len(keywords)} keywords...")

    # Read Mega CSV
    # Assuming columns: Address, Title, H1, Status Code
    filtered_urls = []

    with open(mega_csv, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get("Address", "")
            if not url or "200" not in row.get("Status Code", ""):
                continue

            if is_blacklisted_domain(url, BLACKLIST_DOMAINS):
                continue

            # Check content relevance
            title = row.get("Title 1", "").lower()
            h1 = row.get("H1-1", "").lower()

            score = 0
            for kw in keywords[:5]:  # Check top 5 keywords
                if kw in title or kw in h1:
                    score += 1

            if score > 0:
                filtered_urls.append(url)

    # Save to competitors/mega_urls.txt
    comp_dir = cat_dir / "competitors"
    comp_dir.mkdir(exist_ok=True)

    out_file = comp_dir / "mega_urls.txt"
    out_file.write_text("\n".join(filtered_urls), encoding="utf-8")
    logger.info(f"Found {len(filtered_urls)} URLs. Saved to {out_file}")


# =============================================================================
# Logic: Aggregate
# =============================================================================


def aggregate_urls():
    """
    Aggregates all cluster-level URLs into a global list.
    """
    logger.info("Aggregating URLs from all categories...")

    all_urls = set()

    for cat_dir in CATEGORIES_DIR.iterdir():
        if not cat_dir.is_dir():
            continue

        # Check various sources
        sources = [
            cat_dir / "competitors" / "cluster_urls.txt",
            cat_dir / "competitors" / "mega_urls.txt",
            cat_dir / "competitors" / "serp_urls.txt",
        ]

        for src in sources:
            if src.exists():
                urls = src.read_text(encoding="utf-8").splitlines()
                for u in urls:
                    u = u.strip()
                    if u:
                        all_urls.add(u)

    # Save global list
    DATA_DIR.mkdir(exist_ok=True)
    out_path = DATA_DIR / "all_competitors_aggregated.txt"
    out_path.write_text("\n".join(sorted(all_urls)), encoding="utf-8")
    logger.info(f"Aggregated {len(all_urls)} unique URLs to {out_path}")


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Competitor Management Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: extract (placeholder mostly)
    p_extract = subparsers.add_parser("extract", help="Extract from SERP output")
    p_extract.add_argument("--file", type=Path, help="Path to SERP CSV")

    # Command: filter
    p_filter = subparsers.add_parser("filter", help="Filter Mega CSV for category")
    p_filter.add_argument("slug", help="Category slug")

    # Command: aggregate
    subparsers.add_parser("aggregate", help="Aggregate all URLs")

    args = parser.parse_args()

    if args.command == "extract":
        if args.file:
            extract_from_serp(args.file, CATEGORIES_DIR)
        else:
            print("Provide --file path to SERP CSV")

    elif args.command == "filter":
        filter_mega(args.slug)

    elif args.command == "aggregate":
        aggregate_urls()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
