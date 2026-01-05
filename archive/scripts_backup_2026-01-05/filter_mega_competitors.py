#!/usr/bin/env python3
"""
Filter MEGA competitors CSV for a specific category.

Stage 5 helper script for filter-mega-csv-agent:
- Reads data/mega/mega_competitors.csv (Screaming Frog export)
- Reads categories/{slug}/data/{slug}.json (keywords)
- Filters rows where Title/H1 match category keywords
- Extracts H2 themes and meta patterns
- Saves:
  - categories/{slug}/competitors/meta_competitors.csv
  - categories/{slug}/competitors/meta_patterns.json

Exit codes:
- 0: OK (>= min_competitors and >= min_h2_themes)
- 1: WARNING (some data, but below thresholds)
- 2: FAIL (no competitors found)
"""

import argparse
import csv
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

# Allow running as `python3 scripts/filter_mega_competitors.py` without PYTHONPATH=.
if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Import shared utilities
from scripts.seo_utils import fix_ua_in_url, is_blacklisted_domain, is_category_page


# Note: is_category_page() from seo_utils returns (bool, str)
# We wrap it for backward compatibility with existing code
def is_category_page_simple(url: str) -> bool:
    """Wrapper for seo_utils.is_category_page that returns only bool"""
    is_cat, _ = is_category_page(url)
    return is_cat


def load_category_keywords(category_json: Path, max_keywords: int = 5) -> list[str]:
    """
    Load keywords from category JSON.

    Supports both formats for backward compatibility:
    - Dict format: {"keyword": "фраза", "volume": 1300}
    - String format: "фраза"
    """
    with category_json.open("r", encoding="utf-8") as f:
        data = json.load(f)

    keywords = []
    kw_dict = data.get("keywords", {})

    for role in ["primary", "secondary", "supporting"]:
        for kw in kw_dict.get(role, []):
            # Support both string and dict formats
            if isinstance(kw, str):
                phrase = kw
            elif isinstance(kw, dict):
                phrase = kw.get("keyword") or kw.get("text")
            else:
                continue

            if phrase:
                keywords.append(phrase.strip().lower())
            if len(keywords) >= max_keywords:
                return keywords

    return keywords


def load_url_mapping(map_file: Path, slug: str) -> set[str]:
    """
    Load URLs for specific category from mega_urls_map.csv.

    Returns set of URLs that were extracted using this category's seed phrases.
    """
    if not map_file.exists():
        return set()

    category_urls = set()

    with map_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_slug = row.get("slug", "").strip()
            url = row.get("url", "").strip()

            if row_slug == slug and url:
                category_urls.add(url.lower())

    return category_urls


def filter_rows_by_mapping_and_keywords(
    rows: list[dict], category_urls: set[str], keywords: list[str], use_mapping: bool = True
) -> list[dict]:
    """
    Filter rows by URL mapping (hard filter) + keywords (soft filter).

    Two-layer filtering:
    1. HARD: URL must be in category_urls (from mega_urls_map.csv)
    2. SOFT: Title/H1 should contain keywords (warning if not)

    Standard filters:
    - Status Code = 200 only
    - NOT blacklisted domains
    - IS category page (heuristic)
    - Fix /ua/ in URLs
    """
    filtered = []
    seen_urls = set()
    keyword_mismatches = []

    for row in rows:
        # Filter: Status Code = 200
        status = str(row.get("Status Code", "")).strip()
        if status and status != "200":
            continue

        url = row.get("Address", "").strip()
        if not url:
            continue

        # Filter: Blacklist domains
        if is_blacklisted_domain(url):
            continue

        # Filter: Category pages only
        if not is_category_page_simple(url):
            continue

        # Fix /ua/ in URL
        url_fixed = fix_ua_in_url(url)
        if url_fixed != url:
            row["Address"] = url_fixed
            url = url_fixed

        # Deduplicate
        if url in seen_urls:
            continue

        # HARD FILTER: URL must be in mapping (if enabled)
        if use_mapping and category_urls:
            url_normalized = url.lower()
            if url_normalized not in category_urls:
                continue

        seen_urls.add(url)

        # SOFT FILTER: Keywords match (warning if not)
        title = (row.get("Title 1") or "").lower()
        h1 = (row.get("H1-1") or "").lower()
        text = f"{title} {h1}"

        has_keyword_match = any(kw in text for kw in keywords)

        if has_keyword_match:
            filtered.append(row)
        elif use_mapping:
            # URL in mapping but no keyword match - add with warning
            keyword_mismatches.append(url)
            filtered.append(row)

    if keyword_mismatches:
        print(
            f"⚠️  WARNING: {len(keyword_mismatches)} URLs in mapping but no keyword match in Title/H1"
        )

    return filtered


def extract_h2_themes(rows: list[dict]) -> list[str]:
    themes: list[str] = []
    for row in rows:
        for key, value in row.items():
            if key.startswith("H2") and value:
                theme = str(value).strip()
                if theme:
                    themes.append(theme)
    return themes


def calculate_meta_patterns(rows: list[dict], h2_themes: list[str]) -> dict:
    titles = [row.get("Title 1") or "" for row in rows]
    descriptions = [row.get("Meta Description 1") or "" for row in rows]

    title_lengths = [len(t) for t in titles if t]
    desc_lengths = [len(d) for d in descriptions if d]

    title_median = statistics.median(title_lengths) if title_lengths else 0
    desc_median = statistics.median(desc_lengths) if desc_lengths else 0

    title_ne_h1_count = 0
    total_with_h1 = 0
    for row in rows:
        title = (row.get("Title 1") or "").strip()
        h1 = (row.get("H1-1") or "").strip()
        if title and h1:
            total_with_h1 += 1
            if title != h1:
                title_ne_h1_count += 1

    title_ne_h1_rate = title_ne_h1_count / total_with_h1 if total_with_h1 > 0 else 0.0

    counter = Counter(h2_themes)
    top_h2 = [theme for theme, _count in counter.most_common(10)]

    return {
        "competitors_count": len(rows),
        "title_length_median": title_median,
        "description_length_median": desc_median,
        "h2_themes": top_h2,
        "title_ne_h1_rate": title_ne_h1_rate,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Filter MEGA competitors CSV for a specific category"
    )
    parser.add_argument("slug", help="Category slug (e.g. aktivnaya-pena)")
    parser.add_argument(
        "--mega-csv",
        default="data/mega/mega_competitors.csv",
        help="Path to MEGA competitors CSV",
    )
    parser.add_argument(
        "--data-json",
        help="Path to category data JSON; default: categories/{slug}/data/{slug}.json",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for competitors; default: categories/{slug}/competitors",
    )
    parser.add_argument(
        "--min-competitors",
        type=int,
        default=None,
        help="Minimum competitors threshold; if not set, uses tier-based: Tier A=5, Tier B=4",
    )
    parser.add_argument(
        "--tier",
        type=str,
        choices=["A", "B", "C"],
        help="Category tier (A/B/C) for tier-aware validation",
    )
    parser.add_argument(
        "--min-h2-themes",
        type=int,
        default=3,
        help="Minimum distinct H2 themes (default: 3)",
    )

    args = parser.parse_args()

    base_dir = Path(__file__).parent.parent
    slug = args.slug

    mega_csv = base_dir / args.mega_csv
    if not mega_csv.exists():
        print(f"❌ MEGA CSV not found: {mega_csv}", file=sys.stderr)
        return 2

    # D+E: Fallback — _clean.json (12 kw) → {slug}.json (52 kw)
    if args.data_json:
        data_json = base_dir / args.data_json
    else:
        clean_json = base_dir / f"categories/{slug}/data/{slug}_clean.json"
        raw_json = base_dir / f"categories/{slug}/data/{slug}.json"
        data_json = clean_json if clean_json.exists() else raw_json

    if not data_json.exists():
        print(f"❌ Category JSON not found: {data_json}", file=sys.stderr)
        return 2

    output_dir = (
        base_dir / f"categories/{slug}/competitors"
        if not args.output_dir
        else base_dir / args.output_dir
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    competitors_csv = output_dir / "meta_competitors.csv"
    patterns_json = output_dir / "meta_patterns.json"

    print(f"📂 MEGA CSV: {mega_csv}")
    print(f"📂 Category JSON: {data_json}")
    print(f"📁 Output dir: {output_dir}")

    # Load keywords from category JSON
    keywords = load_category_keywords(data_json)
    if not keywords:
        print("❌ No keywords found in category JSON", file=sys.stderr)
        return 2

    print(f"🔑 Using {len(keywords)} keywords for filtering")

    # Load URL mapping (hard filter)
    map_file = base_dir / "data" / "mega" / "mega_urls_map.csv"
    category_urls = load_url_mapping(map_file, slug)

    if category_urls:
        print(f"🗺️  Loaded {len(category_urls)} URLs from mapping for {slug}")
        use_mapping = True
    else:
        print(f"⚠️  WARNING: mega_urls_map.csv not found or no URLs for {slug}")
        print("   Falling back to keyword-only filtering")
        use_mapping = False

    # Load MEGA CSV rows
    rows: list[dict] = []
    with mega_csv.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print(f"📊 MEGA CSV rows (incl. non-200): {len(rows)}")

    # Filter using mapping + keywords
    filtered_rows = filter_rows_by_mapping_and_keywords(rows, category_urls, keywords, use_mapping)
    print(f"✅ Competitors matched for {slug}: {len(filtered_rows)}")

    if not filtered_rows:
        print("❌ No competitors matched by keywords", file=sys.stderr)
        return 2

    h2_themes = extract_h2_themes(filtered_rows)
    patterns = calculate_meta_patterns(filtered_rows, h2_themes)

    with competitors_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in filtered_rows:
            writer.writerow(row)

    with patterns_json.open("w", encoding="utf-8") as f:
        json.dump(patterns, f, ensure_ascii=False, indent=2)

    print(f"💾 Saved competitors CSV: {competitors_csv}")
    print(f"💾 Saved meta patterns JSON: {patterns_json}")
    print(f"📈 Competitors count: {patterns['competitors_count']}")
    print(f"📈 H2 themes count: {len(patterns['h2_themes'])}")
    print(f"📈 Title median: {patterns['title_length_median']}")
    print(f"📈 Description median: {patterns['description_length_median']}")
    print(f"📈 Title≠H1 rate: {patterns['title_ne_h1_rate']:.2f}")

    # Determine tier-based minimum
    if args.min_competitors is not None:
        min_competitors = args.min_competitors
    elif args.tier:
        # Tier-aware minimums
        tier_minimums = {"A": 5, "B": 4, "C": 3}
        min_competitors = tier_minimums.get(args.tier, 4)
        print(f"ℹ️  Using tier-based minimum: Tier {args.tier} = {min_competitors} competitors")
    else:
        # Try to detect tier from JSON
        try:
            with data_json.open("r", encoding="utf-8") as f:
                data = json.load(f)
                tier = data.get("tier", "B")
                tier_minimums = {"A": 5, "B": 4, "C": 3}
                min_competitors = tier_minimums.get(tier, 4)
                print(
                    f"ℹ️  Auto-detected tier from JSON: Tier {tier} = {min_competitors} competitors"
                )
        except Exception:
            min_competitors = 4  # Default fallback
            print(f"ℹ️  Using default minimum: {min_competitors} competitors")

    # Target range: 5-10 is optimal
    competitors_count = patterns["competitors_count"]
    h2_count = len(patterns["h2_themes"])

    # Validation logic
    competitors_fail = competitors_count < min_competitors
    h2_fail = h2_count < args.min_h2_themes

    # Target range recommendations
    if competitors_count >= 8:
        print("🎯 EXCELLENT: 8+ competitors (rich material for patterns)")
    elif competitors_count >= 5:
        print("🎯 GOOD: 5-7 competitors (solid coverage)")
    elif competitors_count >= min_competitors:
        print(f"⚠️  ACCEPTABLE: {competitors_count} competitors (minimum met)")
        print("   💡 Recommendation: Add 1-2 more competitors for better H2/FAQ coverage")

    if competitors_fail or h2_fail:
        print("\n❌ FAIL: Minimum thresholds not met")
        if competitors_fail:
            print(f"   • Competitors: {competitors_count} < {min_competitors} (minimum)")
        if h2_fail:
            print(f"   • H2 themes: {h2_count} < {args.min_h2_themes} (minimum)")
        return 2

    if competitors_count < 5:
        print("\n⚠️  WARNING: Below target range (5-10 competitors)")
        return 1

    print("\n✅ SUCCESS: All thresholds met")
    return 0


if __name__ == "__main__":
    sys.exit(main())
