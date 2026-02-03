#!/usr/bin/env python3
"""
audit_h1_primary.py — Audit H1 vs Primary Keyword

Перевіряє всі категорії на відповідність H1 ↔ primary_keyword.

Usage:
    python3 scripts/audit_h1_primary.py --lang uk
    python3 scripts/audit_h1_primary.py --lang ru
    python3 scripts/audit_h1_primary.py --lang uk --json
    python3 scripts/audit_h1_primary.py --lang uk --csv > reports/h1_audit_uk.csv
    python3 scripts/audit_h1_primary.py --lang uk --slug aktivnaya-pena
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.keyword_utils import MorphAnalyzer
from scripts.validate_meta import validate_h1


def get_categories_path(lang: str, base_path: Path | None = None) -> Path:
    """Get categories directory path for language."""
    root = base_path or Path(__file__).resolve().parent.parent
    if lang == "uk":
        return root / "uk" / "categories"
    return root / "categories"


def load_json_safe(path: Path) -> dict[str, Any] | None:
    """Load JSON file safely, return None on error."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def audit_category(
    slug: str,
    base_path: Path | None = None,
    lang: str = "ru",
) -> dict[str, Any]:
    """
    Audit single category for H1 vs primary_keyword match.

    Returns:
        {
            "slug": str,
            "primary_keyword": str,
            "primary_volume": int,
            "current_h1": str,
            "expected_h1": str,
            "status": "OK" | "MISMATCH" | "MISSING_DATA",
            "fix_needed": bool
        }
    """
    cats_path = get_categories_path(lang, base_path)
    cat_dir = cats_path / slug

    result: dict[str, Any] = {
        "slug": slug,
        "primary_keyword": None,
        "primary_volume": 0,
        "current_h1": None,
        "expected_h1": None,
        "status": "MISSING_DATA",
        "fix_needed": False,
        "lang": lang,
    }

    # Load _clean.json
    clean_path = cat_dir / "data" / f"{slug}_clean.json"
    clean_data = load_json_safe(clean_path)
    if not clean_data:
        result["status"] = "MISSING_DATA"
        result["message"] = f"Missing {clean_path}"
        return result

    # Get primary keyword (MAX volume)
    keywords_raw = clean_data.get("keywords", [])

    # Support both formats:
    # 1. New: {"keywords": [{"keyword": "...", "volume": N}, ...]}
    # 2. Old: {"keywords": {"primary": [{"keyword": "...", "volume": N}], ...}}
    if isinstance(keywords_raw, dict):
        # Old format - flatten primary + secondary + supporting
        keywords = []
        for section in ["primary", "secondary", "supporting"]:
            keywords.extend(keywords_raw.get(section, []))
    else:
        keywords = keywords_raw

    if not keywords:
        result["status"] = "MISSING_DATA"
        result["message"] = "No keywords in _clean.json"
        return result

    # Check for category_title override
    if clean_data.get("category_title"):
        primary_kw = clean_data["category_title"]
        primary_vol = 0  # category_title doesn't have volume
    else:
        # Filter only dict items (some legacy data may have strings)
        kw_dicts = [k for k in keywords if isinstance(k, dict) and k.get("keyword")]
        if not kw_dicts:
            result["status"] = "MISSING_DATA"
            result["message"] = "No valid keyword dicts in _clean.json"
            return result
        primary_item = max(kw_dicts, key=lambda x: x.get("volume", 0))
        primary_kw = primary_item.get("keyword", "")
        primary_vol = primary_item.get("volume", 0)

    result["primary_keyword"] = primary_kw
    result["primary_volume"] = primary_vol

    # Load _meta.json
    meta_path = cat_dir / "meta" / f"{slug}_meta.json"
    meta_data = load_json_safe(meta_path)
    if not meta_data:
        result["status"] = "MISSING_DATA"
        result["message"] = f"Missing {meta_path}"
        return result

    current_h1 = meta_data.get("h1", "")
    result["current_h1"] = current_h1

    # Calculate expected H1 (plural form)
    morph = MorphAnalyzer(lang)
    expected_h1 = morph.phrase_to_plural(primary_kw)
    result["expected_h1"] = expected_h1

    # Use validate_h1 for consistency
    h1_check = validate_h1(current_h1, primary_kw, lang=lang)

    if h1_check["passed"]:
        result["status"] = "OK"
        result["fix_needed"] = False
        result["match_form"] = h1_check["form"]
    else:
        result["status"] = "MISMATCH"
        result["fix_needed"] = True
        result["message"] = h1_check["message"]

    return result


def audit_all(lang: str = "ru", base_path: Path | None = None) -> list[dict[str, Any]]:
    """Audit all categories for specified language."""
    cats_path = get_categories_path(lang, base_path)
    results = []

    if not cats_path.exists():
        return results

    for cat_dir in sorted(cats_path.iterdir()):
        if not cat_dir.is_dir() or cat_dir.name.startswith("."):
            continue

        result = audit_category(cat_dir.name, base_path, lang)
        results.append(result)

    return results


def print_csv(results: list[dict[str, Any]]) -> None:
    """Print results as CSV."""
    if not results:
        return

    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=[
            "slug",
            "status",
            "primary_keyword",
            "primary_volume",
            "current_h1",
            "expected_h1",
            "fix_needed",
            "lang",
        ],
        extrasaction="ignore",
    )
    writer.writeheader()
    writer.writerows(results)


def print_table(results: list[dict[str, Any]]) -> None:
    """Print results as formatted table."""
    mismatch = [r for r in results if r["status"] == "MISMATCH"]
    ok = [r for r in results if r["status"] == "OK"]
    missing = [r for r in results if r["status"] == "MISSING_DATA"]

    print(f"\nAudit Results: {len(results)} categories\n")
    print(f"  OK: {len(ok)}")
    print(f"  MISMATCH: {len(mismatch)}")
    print(f"  MISSING_DATA: {len(missing)}")

    if mismatch:
        print("\n" + "=" * 80)
        print("CATEGORIES REQUIRING FIX:")
        print("=" * 80)
        for r in mismatch:
            print(f"\n  {r['slug']}")
            print(f'     Primary: "{r["primary_keyword"]}" (vol: {r["primary_volume"]})')
            print(f'     Current H1: "{r["current_h1"]}"')
            print(f'     Expected H1: "{r["expected_h1"]}"')


def main():
    parser = argparse.ArgumentParser(description="Audit H1 vs Primary Keyword")
    parser.add_argument("--lang", choices=["ru", "uk"], default="ru", help="Language")
    parser.add_argument("--slug", help="Audit single category")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--csv", action="store_true", help="CSV output")
    args = parser.parse_args()

    if args.slug:
        results = [audit_category(args.slug, lang=args.lang)]
    else:
        results = audit_all(lang=args.lang)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    elif args.csv:
        print_csv(results)
    else:
        print_table(results)

    # Exit code: 1 if any MISMATCH
    mismatch_count = sum(1 for r in results if r["status"] == "MISMATCH")
    sys.exit(1 if mismatch_count > 0 else 0)


if __name__ == "__main__":
    main()
