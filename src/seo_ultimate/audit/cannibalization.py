#!/usr/bin/env python3
"""
check_cannibalization.py — Check for keyword cannibalization between categories.

Finds:
- Full duplicates: same keyword in multiple categories
- Partial intersections: keyword A is substring of keyword B in different categories

Usage:
    uv run python -m seo_ultimate.audit.cannibalization
    uv run python -m seo_ultimate.audit.cannibalization --lang uk
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path

from seo_ultimate.core.config import CATEGORIES_DIR, PROJECT_ROOT


def load_keywords(base_path: Path) -> dict[str, list[dict]]:
    """
    Build keyword map from _clean.json files.

    Returns:
        {keyword: [{"category": slug, "type": section, "volume": N}, ...]}
    """
    keyword_map: dict[str, list[dict]] = defaultdict(list)

    if not base_path.exists():
        return keyword_map

    for cat_dir in base_path.iterdir():
        if not cat_dir.is_dir() or cat_dir.name.startswith("."):
            continue

        slug = cat_dir.name
        clean_file = cat_dir / "data" / f"{slug}_clean.json"

        if not clean_file.exists():
            # Try finding any _clean.json
            clean_files = list((cat_dir / "data").glob("*_clean.json"))
            if clean_files:
                clean_file = clean_files[0]
            else:
                continue

        try:
            with open(clean_file, encoding="utf-8") as f:
                data = json.load(f)

            keywords_raw = data.get("keywords", [])

            # Handle both formats
            if isinstance(keywords_raw, list):
                # New format: [{"keyword": "...", "volume": N}, ...]
                for item in keywords_raw:
                    if isinstance(item, dict):
                        kw = item.get("keyword", "").strip().lower()
                        vol = item.get("volume", 0)
                        if kw:
                            keyword_map[kw].append(
                                {"category": slug, "type": "keywords", "volume": vol}
                            )
            elif isinstance(keywords_raw, dict):
                # Old format: {"primary": [...], "secondary": [...], ...}
                for k_type, k_list in keywords_raw.items():
                    if isinstance(k_list, list):
                        for item in k_list:
                            if isinstance(item, dict):
                                kw = item.get("keyword", "").strip().lower()
                                vol = item.get("volume", 0)
                                if kw:
                                    keyword_map[kw].append(
                                        {"category": slug, "type": k_type, "volume": vol}
                                    )

        except Exception as e:
            print(f"Error loading {clean_file}: {e}")

    return keyword_map


def find_full_duplicates(keyword_map: dict[str, list[dict]]) -> list[dict]:
    """Find keywords that appear in multiple categories."""
    full_duplicates = []

    for kw, occurrences in keyword_map.items():
        if len(occurrences) > 1:
            categories = {occ["category"] for occ in occurrences}
            if len(categories) > 1:
                # Group by category
                cat_map = defaultdict(list)
                for occ in occurrences:
                    cat_map[occ["category"]].append(f"{occ['type']} ({occ['volume']})")

                full_duplicates.append({"keyword": kw, "details": dict(cat_map)})

    return full_duplicates


def find_partial_intersections(keyword_map: dict[str, list[dict]]) -> list[dict]:
    """
    Find cases where keyword A is a substring of keyword B in different categories.
    """
    keys = sorted(keyword_map.keys(), key=len)
    partials = []

    for i in range(len(keys)):
        short_kw = keys[i]
        short_cats = {x["category"] for x in keyword_map[short_kw]}

        for j in range(i + 1, len(keys)):
            long_kw = keys[j]

            # Skip if not contained
            if short_kw not in long_kw:
                continue

            long_cats = {x["category"] for x in keyword_map[long_kw]}

            # Find disjoint categories
            disjoint_cats_short = short_cats - long_cats
            disjoint_cats_long = long_cats - short_cats

            if disjoint_cats_short and disjoint_cats_long:
                for c1 in disjoint_cats_short:
                    for c2 in disjoint_cats_long:
                        partials.append(
                            {
                                "short_kw": short_kw,
                                "cat_1": c1,
                                "vol_1": max(
                                    [
                                        x["volume"]
                                        for x in keyword_map[short_kw]
                                        if x["category"] == c1
                                    ]
                                ),
                                "long_kw": long_kw,
                                "cat_2": c2,
                                "vol_2": max(
                                    [
                                        x["volume"]
                                        for x in keyword_map[long_kw]
                                        if x["category"] == c2
                                    ]
                                ),
                            }
                        )

    return partials


def generate_report(lang: str, base_path: Path) -> list[str]:
    """Generate report for a single language."""
    report_lines = []
    report_lines.append(f"# Analysis for {lang.upper()}")

    kw_map = load_keywords(base_path)
    full_dups = find_full_duplicates(kw_map)

    if full_dups:
        report_lines.append("\n## ❌ CRITICAL PROBLEM: Full Duplicates\n")

        # Group by category pair
        pair_map = defaultdict(list)
        for dup in full_dups:
            cats = list(dup["details"].keys())
            for c1, c2 in itertools.combinations(cats, 2):
                pair = tuple(sorted((c1, c2)))
                pair_map[pair].append(dup)

        for (c1, c2), dups in pair_map.items():
            report_lines.append(f"\n### {c1} ↔ {c2}\n")
            report_lines.append(f"| Key | {c1} | {c2} |")
            report_lines.append("|---|---|---|")
            for d in dups:
                info1 = d["details"].get(c1, ["-"])[0]
                info2 = d["details"].get(c2, ["-"])[0]
                report_lines.append(f'| *"{d["keyword"]}"* | {info1} | {info2} |')

    else:
        report_lines.append("\n✅ No Full Duplicates Found.\n")

    # Partial intersections
    partials = find_partial_intersections(kw_map)
    if partials:
        report_lines.append("\n## ⚠️ PARTIAL INTERSECTIONS\n")

        # Group by category pair
        pair_map_p = defaultdict(list)
        for p in partials:
            pair = tuple(sorted((p["cat_1"], p["cat_2"])))
            pair_map_p[pair].append(p)

        sorted_pairs = sorted(pair_map_p.items(), key=lambda x: len(x[1]), reverse=True)

        for (c1, c2), issues in sorted_pairs:
            if len(issues) < 1:
                continue

            report_lines.append(f"\n### {c1} ↔ {c2}\n")
            report_lines.append(f"| {c1} | {c2} |")
            report_lines.append("|---|---|")

            # Limit to 10 examples per pair
            for shown, issue in enumerate(issues):
                if shown >= 10:
                    report_lines.append(f"| ... (+{len(issues) - 10} more) | ... |")
                    break

                if issue["cat_1"] == c1:
                    left = f'"{issue["short_kw"]}" ({issue["vol_1"]})'
                    right = f'"{issue["long_kw"]}" ({issue["vol_2"]})'
                else:
                    left = f'"{issue["long_kw"]}" ({issue["vol_2"]})'
                    right = f'"{issue["short_kw"]}" ({issue["vol_1"]})'

                report_lines.append(f"| {left} | {right} |")

    else:
        report_lines.append("\n✅ No Partial Intersections (Substring matches) Found.\n")

    report_lines.append("\n---\n")

    return report_lines


def main():
    parser = argparse.ArgumentParser(description="Check keyword cannibalization")
    parser.add_argument(
        "--lang", choices=["ru", "uk", "all"], default="all", help="Language to check"
    )
    args = parser.parse_args()

    report_lines = []

    if args.lang in ("ru", "all"):
        report_lines.extend(generate_report("ru", CATEGORIES_DIR))

    if args.lang in ("uk", "all"):
        uk_path = PROJECT_ROOT / "uk" / "categories"
        report_lines.extend(generate_report("uk", uk_path))

    report = "\n".join(report_lines)
    print(report)

    # Write to file
    output_path = PROJECT_ROOT / "reports" / "cannibalization_report.md"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
