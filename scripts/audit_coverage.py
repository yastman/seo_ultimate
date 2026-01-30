#!/usr/bin/env python3
"""
audit_coverage.py — Keyword Coverage Audit Tool

Usage:
    python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --verbose
    python3 scripts/audit_coverage.py --lang uk  # batch all UK categories
    python3 scripts/audit_coverage.py --slug X --lang uk --json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from coverage_matcher import audit_category  # noqa: E402


def find_category_path(slug: str, lang: str) -> Path | None:
    """
    Find category path by slug.

    UK: flat structure uk/categories/{slug}/
    RU: hierarchical categories/.../slug/  (need recursive search)
    """
    if lang == "uk":
        path = PROJECT_ROOT / "uk" / "categories" / slug
        if path.exists():
            return path
        return None
    else:
        # RU categories are nested: categories/parent/child/slug/
        # Search recursively for directory with matching slug
        base = PROJECT_ROOT / "categories"
        for clean_file in base.rglob(f"{slug}_clean.json"):
            # clean_file: categories/.../slug/data/slug_clean.json
            return clean_file.parent.parent  # .../slug/
        return None


def load_category_data(slug: str, lang: str) -> tuple[list, list, str] | None:
    """Load keywords, synonyms, and content for a category."""
    base = find_category_path(slug, lang)
    if base is None:
        return None

    if lang == "uk":
        content_file = base / "content" / f"{slug}_uk.md"
    else:
        content_file = base / "content" / f"{slug}_ru.md"

    clean_file = base / "data" / f"{slug}_clean.json"

    if not clean_file.exists():
        return None
    if not content_file.exists():
        return None

    with open(clean_file, encoding="utf-8") as f:
        data = json.load(f)

    keywords = data.get("keywords", [])
    synonyms = data.get("synonyms", [])

    content = content_file.read_text(encoding="utf-8")

    return keywords, synonyms, content


def load_meta_keywords(slug: str, lang: str) -> dict[str, list[str]] | None:
    """
    Load keywords_in_content from _meta.json.

    Returns:
        {"primary": [...], "secondary": [...], "supporting": [...]}
        or None if category not found.
    """
    base = find_category_path(slug, lang)
    if base is None:
        return None

    meta_file = base / "meta" / f"{slug}_meta.json"
    if not meta_file.exists():
        return {"primary": [], "secondary": [], "supporting": []}

    with open(meta_file, encoding="utf-8") as f:
        data = json.load(f)

    kic = data.get("keywords_in_content", {})
    return {
        "primary": kic.get("primary", []),
        "secondary": kic.get("secondary", []),
        "supporting": kic.get("supporting", []),
    }


def audit_with_meta(
    keywords: list[dict],
    synonyms: list[dict],
    meta_keywords: dict[str, list[str]],
    text: str,
    lang: str,
) -> dict:
    """
    Audit both keywords[] and keywords_in_content.

    Args:
        keywords: List from _clean.json
        synonyms: List from _clean.json
        meta_keywords: Dict with primary/secondary/supporting lists
        text: Content text
        lang: Language code

    Returns:
        {
            "keywords_in_content": {
                "primary": {"total": N, "covered": M, "coverage_percent": X, "results": [...]},
                "secondary": {...},
                "supporting": {...}
            },
            "keywords": {"total": N, "covered": M, "coverage_percent": X, "results": [...]}
        }
    """
    from coverage_matcher import PreparedText, check_keyword

    prepared = PreparedText(text, lang)

    # Build volume lookup from keywords[]
    volume_map = {kw["keyword"]: kw.get("volume", 0) for kw in keywords}

    # Audit keywords_in_content groups
    kic_results = {}
    for group in ["primary", "secondary", "supporting"]:
        group_keywords = meta_keywords.get(group, [])
        results = []
        for kw in group_keywords:
            match = check_keyword(kw, prepared, synonyms)
            results.append(
                {
                    "keyword": kw,
                    "volume": volume_map.get(kw, 0),
                    "status": match.status,
                    "covered": match.covered,
                    "covered_by": match.covered_by,
                    "syn_match_method": match.syn_match_method,
                    "lemma_coverage": match.lemma_coverage,
                    "reason": match.reason,
                }
            )

        total = len(group_keywords)
        covered = sum(1 for r in results if r["covered"])
        kic_results[group] = {
            "total": total,
            "covered": covered,
            "coverage_percent": round(covered / total * 100, 1) if total > 0 else 100.0,
            "results": results,
        }

    # Audit full keywords[]
    keywords_result = audit_category(keywords, synonyms, text, lang)

    return {
        "keywords_in_content": kic_results,
        "keywords": keywords_result,
    }


def get_all_slugs(lang: str) -> list[str]:
    """Get all category slugs for a language."""
    if lang == "uk":
        base = PROJECT_ROOT / "uk" / "categories"
        if not base.exists():
            return []
        slugs = []
        for d in base.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                clean_file = d / "data" / f"{d.name}_clean.json"
                if clean_file.exists():
                    slugs.append(d.name)
        return sorted(slugs)
    else:
        # RU: recursive search
        base = PROJECT_ROOT / "categories"
        if not base.exists():
            return []
        slugs = []
        for clean_file in base.rglob("*_clean.json"):
            # Extract slug from filename: slug_clean.json
            slug = clean_file.stem.replace("_clean", "")
            # Verify directory structure
            if clean_file.parent.name == "data" and clean_file.parent.parent.name == slug:
                slugs.append(slug)
        return sorted(slugs)


def print_verbose(slug: str, lang: str, result: dict):
    """Print human-readable audit report."""
    print(f"\n=== {slug} ({lang}) ===")
    print(f"Coverage: {result['covered']}/{result['total']} ({result['coverage_percent']}%)")

    # Group by status
    by_status: dict[str, list] = {}
    for r in result["results"]:
        status = r["status"]
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(r)

    # Print COVERED
    for status in ["EXACT", "NORM", "LEMMA", "SYNONYM"]:
        if status in by_status:
            items = by_status[status]
            print(f"\n✓ {status} ({len(items)}):")
            for r in items[:5]:
                if status == "SYNONYM":
                    print(f"  - {r['keyword']} ({r['volume']}) ← {r['covered_by']} [{r['syn_match_method']}]")
                else:
                    print(f"  - {r['keyword']} ({r['volume']})")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")

    # Print NOT COVERED
    not_covered = []
    for status in ["TOKENIZATION", "PARTIAL", "ABSENT"]:
        if status in by_status:
            not_covered.extend(by_status[status])

    if not_covered:
        print(f"\n✗ NOT COVERED ({len(not_covered)}):")
        # Sort by volume desc
        not_covered.sort(key=lambda x: x["volume"], reverse=True)
        for r in not_covered[:10]:
            extra = f" — {r['reason']}" if r.get("reason") else ""
            print(f"  - [{r['status']}] {r['keyword']} ({r['volume']}){extra}")
        if len(not_covered) > 10:
            print(f"  ... and {len(not_covered) - 10} more")


def write_summary_csv(results: list[dict], lang: str) -> Path:
    """Write coverage_summary.csv"""
    today = date.today().isoformat()
    filename = PROJECT_ROOT / "reports" / f"coverage_summary_{lang}_{today}.csv"
    filename.parent.mkdir(exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["slug", "lang", "total_keywords", "covered", "not_covered", "coverage_percent", "top_missing"])

        for r in results:
            # Get top 3 missing by volume
            missing = [x for x in r["results"] if not x["covered"]]
            missing.sort(key=lambda x: x["volume"], reverse=True)
            top_missing = ";".join(f"{x['keyword']} ({x['volume']})" for x in missing[:3])

            writer.writerow(
                [
                    r["slug"],
                    r["lang"],
                    r["total"],
                    r["covered"],
                    r["total"] - r["covered"],
                    r["coverage_percent"],
                    top_missing,
                ]
            )

    print(f"Written: {filename}")
    return filename


def write_details_csv(results: list[dict], lang: str) -> Path:
    """Write coverage_details.csv"""
    today = date.today().isoformat()
    filename = PROJECT_ROOT / "reports" / f"coverage_details_{lang}_{today}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "slug",
                "lang",
                "keyword",
                "volume",
                "status",
                "covered",
                "covered_by",
                "syn_match_method",
                "lemma_coverage",
                "reason",
            ]
        )

        for cat in results:
            for r in cat["results"]:
                writer.writerow(
                    [
                        cat["slug"],
                        cat["lang"],
                        r["keyword"],
                        r["volume"],
                        r["status"],
                        r["covered"],
                        r["covered_by"] or "",
                        r["syn_match_method"] or "",
                        r["lemma_coverage"] or "",
                        r["reason"] or "",
                    ]
                )

    print(f"Written: {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(description="Audit keyword coverage")
    parser.add_argument("--slug", help="Single category slug")
    parser.add_argument("--lang", choices=["ru", "uk", "all"], default="uk")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--include-meta",
        action="store_true",
        help="Include keywords_in_content from _meta.json",
    )

    args = parser.parse_args()

    if args.slug:
        # Single category mode
        langs = ["ru", "uk"] if args.lang == "all" else [args.lang]

        for lang in langs:
            data = load_category_data(args.slug, lang)
            if data is None:
                print(f"Category {args.slug} ({lang}) not found", file=sys.stderr)
                continue

            keywords, synonyms, content = data

            if args.json and args.include_meta:
                # --include-meta mode: audit both keywords_in_content and keywords[]
                meta_kw = load_meta_keywords(args.slug, lang)
                if meta_kw is None:
                    meta_kw = {"primary": [], "secondary": [], "supporting": []}
                result = audit_with_meta(keywords, synonyms, meta_kw, content, lang)
                result["slug"] = args.slug
                result["lang"] = lang
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                # Standard mode: only keywords[]
                result = audit_category(keywords, synonyms, content, lang)
                result["slug"] = args.slug
                result["lang"] = lang

                if args.json:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                elif args.verbose:
                    print_verbose(args.slug, lang, result)
                else:
                    print(
                        f"{args.slug} ({lang}): {result['covered']}/{result['total']} ({result['coverage_percent']}%)"
                    )
    else:
        # Batch mode
        langs = ["ru", "uk"] if args.lang == "all" else [args.lang]

        for lang in langs:
            slugs = get_all_slugs(lang)
            if not slugs:
                print(f"No categories found for {lang}", file=sys.stderr)
                continue

            print(f"\nAuditing {len(slugs)} {lang.upper()} categories...")

            all_results = []
            for slug in slugs:
                data = load_category_data(slug, lang)
                if data is None:
                    continue

                keywords, synonyms, content = data
                result = audit_category(keywords, synonyms, content, lang)
                result["slug"] = slug
                result["lang"] = lang
                all_results.append(result)

                if args.verbose:
                    print_verbose(slug, lang, result)
                else:
                    status = "✓" if result["coverage_percent"] >= 60 else "✗"
                    print(f"  {status} {slug}: {result['coverage_percent']}%")

            # Write CSVs
            write_summary_csv(all_results, lang)
            write_details_csv(all_results, lang)


if __name__ == "__main__":
    main()
