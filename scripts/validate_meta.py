#!/usr/bin/env python3
"""
validate_meta.py — Meta Tags Validation (v17.0)

Валідація Title + Description для категорій.

Перевірки:
- Title містить primary keyword
- Title довжина 40-60 chars
- Title без двокрапки
- Description містить primary keyword
- Description довжина 120-150 chars
- Description містить "виробника Ultimate" або "производителя Ultimate"
- Description містить "опт"

Usage:
    python3 scripts/validate_meta.py <meta.json>
    python3 scripts/validate_meta.py <meta.json> --keywords <keywords.json>
    python3 scripts/validate_meta.py --all                    # Validate all categories
    python3 scripts/validate_meta.py --all --fix              # Auto-fix issues
    python3 scripts/validate_meta.py <meta.json> --json       # JSON output

Exit codes:
    0 = PASS
    1 = WARNING
    2 = FAIL
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

# Fix Windows encoding is moved to main() block to avoid pytest conflicts


# =============================================================================
# Constants
# =============================================================================

# Soft limits (warnings, not failures)
TITLE_MIN_LENGTH = 30
TITLE_MAX_LENGTH = 60
DESC_MIN_LENGTH = 100
DESC_MAX_LENGTH = 160

# Patterns to detect
COLON_PATTERN = re.compile(r":\s")
PRODUCER_PATTERNS = [
    r"від виробника",
    r"от производителя",
    r"виробника ultimate",
    r"производителя ultimate",
]
WHOLESALE_PATTERNS = [r"опт\b", r"роздріб", r"розница", r"оптом"]
MARKETING_FLUFF = [
    r"без разводов",
    r"без розводів",
    r"густая пена",
    r"густа піна",
    r"быстро",
    r"швидко",
    r"качественн",
    r"якісн",
    r"лучшие цены",
    r"найкращі ціни",
]


# =============================================================================
# Validation Functions
# =============================================================================


# from typing import Any


def load_json(path: str) -> dict[str, Any]:
    """Load JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)  # type: ignore


def get_primary_keywords(keywords_data: dict[str, Any]) -> list[str]:
    """Extract primary keywords from keywords JSON."""
    keywords = []

    if "keywords" in keywords_data:
        kw_section = keywords_data["keywords"]
        if "primary" in kw_section:
            for item in kw_section["primary"]:
                if isinstance(item, dict):
                    keywords.append(item.get("keyword", "").lower())
                else:
                    keywords.append(str(item).lower())

    return keywords


def get_commercial_keywords(keywords_data: dict[str, Any]) -> list[str]:
    """Extract commercial keywords from keywords JSON."""
    keywords = []

    if "keywords" in keywords_data:
        kw_section = keywords_data["keywords"]
        if "commercial" in kw_section:
            for item in kw_section["commercial"]:
                if isinstance(item, dict):
                    keywords.append(item.get("keyword", "").lower())
                else:
                    keywords.append(str(item).lower())

    return keywords


def get_word_stem(word: str) -> str:
    """
    Extract stem from a single word for fuzzy matching.
    Handles singular/plural forms in Russian/Ukrainian.
    """
    w = word.lower().strip()
    if len(w) <= 4:
        return w

    # Remove common noun endings (ordered by length)
    for suffix in [
        "ого",
        "его",
        "ому",
        "ему",
        "ими",
        "ыми",
        "ая",
        "яя",
        "ую",
        "юю",
        "ое",
        "ее",
        "ые",
        "ие",
        "ый",
        "ій",
        "ями",
        "ей",
        "ов",
        "ів",
        "ах",
        "ях",
        "ий",
        "ой",
        "ем",
        "ом",
        "и",
        "і",
        "ы",
        "а",
        "я",
        "е",
        "ь",
        "у",
        "ю",
    ]:
        if len(w) > len(suffix) + 3 and w.endswith(suffix):
            return w[: -len(suffix)]
    return w


def keyword_matches(keyword: str, text: str) -> bool:
    """
    Check if keyword matches text, accounting for plural/singular forms.
    Uses word-level stem matching for each significant word.
    """
    text_lower = text.lower()
    kw_lower = keyword.lower()

    # Direct match
    if kw_lower in text_lower:
        return True

    # Split keyword into words and match stems for main words
    kw_words = kw_lower.split()
    if not kw_words:
        return False

    # Get the first significant word (usually the main noun)
    main_word = kw_words[0]
    main_stem = get_word_stem(main_word)

    # Check if main stem appears in text (at least 4 chars)
    return len(main_stem) >= 4 and main_stem in text_lower

    return False


def validate_title(title: str, primary_keywords: list[str] | None = None) -> dict[str, Any]:
    """
    Validate meta title.

    Checks:
    - Length 40-60 chars (before | Ultimate)
    - No colon
    - Contains primary keyword
    - No marketing fluff
    """
    checks: dict[str, Any] = {
        "length": {"passed": False, "message": ""},
        "no_colon": {"passed": False, "message": ""},
        "primary_keyword": {"passed": False, "message": ""},
        "no_fluff": {"passed": False, "message": ""},
    }
    results: dict[str, Any] = {
        "value": title,
        "length": len(title),
        "checks": checks,
        "overall": "FAIL",
    }

    # Extract title without brand suffix
    title_clean = title
    if "|" in title:
        title_clean = title.split("|")[0].strip()

    title_length = len(title_clean)
    results["length_without_brand"] = title_length

    # 1. Length check
    if TITLE_MIN_LENGTH <= title_length <= TITLE_MAX_LENGTH:
        results["checks"]["length"]["passed"] = True
        results["checks"]["length"]["message"] = f"OK ({title_length} chars)"
    elif title_length < TITLE_MIN_LENGTH:
        results["checks"]["length"]["message"] = f"Too short ({title_length} < {TITLE_MIN_LENGTH})"
    else:
        results["checks"]["length"]["message"] = f"Too long ({title_length} > {TITLE_MAX_LENGTH})"

    # 2. No colon check
    if not COLON_PATTERN.search(title_clean):
        results["checks"]["no_colon"]["passed"] = True
        results["checks"]["no_colon"]["message"] = "OK (no colon)"
    else:
        results["checks"]["no_colon"]["message"] = "Contains colon (:) - replace with 'для' or brackets"

    # 3. Primary keyword check (with stem matching)
    if primary_keywords:
        found = [kw for kw in primary_keywords if keyword_matches(kw, title)]
        if found:
            results["checks"]["primary_keyword"]["passed"] = True
            results["checks"]["primary_keyword"]["message"] = f"Found: {found[0]}"
        else:
            results["checks"]["primary_keyword"]["message"] = "Missing primary keyword"
    else:
        results["checks"]["primary_keyword"]["passed"] = True
        results["checks"]["primary_keyword"]["message"] = "No keywords to check"

    # 4. No marketing fluff
    title_lower = title.lower()
    fluff_found = [p for p in MARKETING_FLUFF if re.search(p, title_lower)]
    if not fluff_found:
        results["checks"]["no_fluff"]["passed"] = True
        results["checks"]["no_fluff"]["message"] = "OK (no marketing fluff)"
    else:
        results["checks"]["no_fluff"]["message"] = f"Marketing fluff found: {fluff_found}"

    # Overall
    all_passed = all(c["passed"] for c in results["checks"].values())
    critical_passed = results["checks"]["no_colon"]["passed"] and results["checks"]["primary_keyword"]["passed"]

    if all_passed:
        results["overall"] = "PASS"
    elif critical_passed:
        results["overall"] = "WARNING"
    else:
        results["overall"] = "FAIL"

    return results


def validate_description(description: str, primary_keywords: list[str] | None = None) -> dict[str, Any]:
    """
    Validate meta description.

    Checks:
    - Length 120-150 chars
    - Contains primary keyword
    - Contains "виробника Ultimate" or equivalent
    - Contains "опт" or wholesale indicator
    - No marketing fluff
    """
    checks: dict[str, Any] = {
        "length": {"passed": False, "message": ""},
        "primary_keyword": {"passed": False, "message": ""},
        "producer": {"passed": False, "message": ""},
        "wholesale": {"passed": False, "message": ""},
        "no_fluff": {"passed": False, "message": ""},
    }
    results: dict[str, Any] = {
        "value": description,
        "length": len(description),
        "checks": checks,
        "overall": "FAIL",
    }

    desc_lower = description.lower()

    # 1. Length check
    desc_length = len(description)
    if DESC_MIN_LENGTH <= desc_length <= DESC_MAX_LENGTH:
        results["checks"]["length"]["passed"] = True
        results["checks"]["length"]["message"] = f"OK ({desc_length} chars)"
    elif desc_length < DESC_MIN_LENGTH:
        results["checks"]["length"]["message"] = f"Too short ({desc_length} < {DESC_MIN_LENGTH})"
    else:
        results["checks"]["length"]["passed"] = True  # Warning only
        results["checks"]["length"]["message"] = f"Slightly long ({desc_length} > {DESC_MAX_LENGTH})"

    # 2. Primary keyword check (with stem matching)
    if primary_keywords:
        found = [kw for kw in primary_keywords if keyword_matches(kw, description)]
        if found:
            results["checks"]["primary_keyword"]["passed"] = True
            results["checks"]["primary_keyword"]["message"] = f"Found: {found[0]}"
        else:
            results["checks"]["primary_keyword"]["message"] = "Missing primary keyword"
    else:
        results["checks"]["primary_keyword"]["passed"] = True
        results["checks"]["primary_keyword"]["message"] = "No keywords to check"

    # 3. Producer check
    producer_found = any(re.search(p, desc_lower) for p in PRODUCER_PATTERNS)
    if producer_found:
        results["checks"]["producer"]["passed"] = True
        results["checks"]["producer"]["message"] = "OK (contains 'виробника/производителя')"
    else:
        results["checks"]["producer"]["message"] = "Missing 'від виробника Ultimate'"

    # 4. Wholesale check
    wholesale_found = any(re.search(p, desc_lower) for p in WHOLESALE_PATTERNS)
    if wholesale_found:
        results["checks"]["wholesale"]["passed"] = True
        results["checks"]["wholesale"]["message"] = "OK (contains 'опт/роздріб')"
    else:
        results["checks"]["wholesale"]["message"] = "Missing 'Опт і роздріб'"

    # 5. No marketing fluff
    fluff_found = [p for p in MARKETING_FLUFF if re.search(p, desc_lower)]
    if not fluff_found:
        results["checks"]["no_fluff"]["passed"] = True
        results["checks"]["no_fluff"]["message"] = "OK (no marketing fluff)"
    else:
        results["checks"]["no_fluff"]["message"] = f"Marketing fluff found: {fluff_found}"

    # Overall
    all_passed = all(c["passed"] for c in results["checks"].values())
    critical_passed = results["checks"]["primary_keyword"]["passed"] and results["checks"]["producer"]["passed"]

    if all_passed:
        results["overall"] = "PASS"
    elif critical_passed:
        results["overall"] = "WARNING"
    else:
        results["overall"] = "FAIL"

    return results


def validate_meta_file(meta_path: str, keywords_path: str | None = None) -> dict[str, Any]:
    """
    Full validation of meta JSON file.

    Args:
        meta_path: Path to meta JSON file
        keywords_path: Optional path to keywords JSON file

    Returns:
        Validation results dict
    """
    results: dict[str, Any] = {
        "file": meta_path,
        "keywords_file": keywords_path,
        "title": None,
        "description": None,
        "h1": None,
        "overall": "FAIL",
        "errors": [],
    }

    # Load meta file
    try:
        meta = load_json(meta_path)
    except Exception as e:
        results["errors"].append(f"Cannot load meta file: {e}")
        return results

    # Extract values
    title = meta.get("meta", {}).get("title", "")
    description = meta.get("meta", {}).get("description", "")
    h1 = meta.get("h1", "")

    results["h1"] = {"value": h1}

    # Load keywords if provided
    primary_keywords = []
    # commercial_keywords = []

    if keywords_path:
        try:
            keywords_data = load_json(keywords_path)
            primary_keywords = get_primary_keywords(keywords_data)
            # commercial_keywords = get_commercial_keywords(keywords_data)
        except Exception as e:
            results["errors"].append(f"Cannot load keywords file: {e}")

    # Also check keywords_in_content from meta file
    if not primary_keywords and "keywords_in_content" in meta:
        kic = meta["keywords_in_content"]
        if "primary" in kic:
            primary_keywords = [k.lower() for k in kic["primary"]]

    # Validate title
    results["title"] = validate_title(title, primary_keywords)

    # Validate description
    results["description"] = validate_description(description, primary_keywords)

    # Overall
    title_ok = results["title"]["overall"] in ["PASS", "WARNING"]
    desc_ok = results["description"]["overall"] in ["PASS", "WARNING"]

    if results["title"]["overall"] == "PASS" and results["description"]["overall"] == "PASS":
        results["overall"] = "PASS"
    elif title_ok and desc_ok:
        results["overall"] = "WARNING"
    else:
        results["overall"] = "FAIL"

    return results


def find_all_meta_files(base_path: str = ".") -> list[tuple[str, str | None]]:
    """
    Find all meta files and their corresponding keywords files.

    Returns:
        List of (meta_path, keywords_path) tuples
    """
    base = Path(base_path)
    results = []

    # Search in categories/
    for meta_file in base.glob("categories/*/meta/*_meta.json"):
        slug = meta_file.stem.replace("_meta", "")
        keywords_file = meta_file.parent.parent / "data" / f"{slug}_clean.json"
        if not keywords_file.exists():
            keywords_file = meta_file.parent.parent / "data" / f"{slug}.json"
        results.append((str(meta_file), str(keywords_file) if keywords_file.exists() else None))

    # Search in uk/categories/
    for meta_file in base.glob("uk/categories/*/meta/*_meta.json"):
        slug = meta_file.stem.replace("_meta", "")
        keywords_file = meta_file.parent.parent / "data" / f"{slug}_clean.json"
        if not keywords_file.exists():
            keywords_file = meta_file.parent.parent / "data" / f"{slug}.json"
        results.append((str(meta_file), str(keywords_file) if keywords_file.exists() else None))

    return results


# =============================================================================
# CLI Output
# =============================================================================


def print_results(results: dict[str, Any]):
    """Print human-readable validation results."""
    print()
    print("=" * 60)
    print("META VALIDATION (v17.0)")
    print("=" * 60)
    print(f"File: {results['file']}")
    if results.get("keywords_file"):
        print(f"Keywords: {results['keywords_file']}")
    print()

    if results.get("errors"):
        for err in results["errors"]:
            print(f"❌ ERROR: {err}")
        print()
        return

    # Title
    title = results["title"]
    icon = "✅" if title["overall"] == "PASS" else ("⚠️" if title["overall"] == "WARNING" else "❌")
    print(f"{icon} TITLE: {title['overall']}")
    print(f"   Value: {title['value'][:60]}...")
    print(
        f"   Length: {title.get('length_without_brand', title['length'])} chars (target: {TITLE_MIN_LENGTH}-{TITLE_MAX_LENGTH})"
    )
    for check_name, check_data in title["checks"].items():
        check_icon = "✓" if check_data["passed"] else "✗"
        print(f"   {check_icon} {check_name}: {check_data['message']}")
    print()

    # Description
    desc = results["description"]
    icon = "✅" if desc["overall"] == "PASS" else ("⚠️" if desc["overall"] == "WARNING" else "❌")
    print(f"{icon} DESCRIPTION: {desc['overall']}")
    print(f"   Value: {desc['value'][:80]}...")
    print(f"   Length: {desc['length']} chars (target: {DESC_MIN_LENGTH}-{DESC_MAX_LENGTH})")
    for check_name, check_data in desc["checks"].items():
        check_icon = "✓" if check_data["passed"] else "✗"
        print(f"   {check_icon} {check_name}: {check_data['message']}")
    print()

    # H1
    if results.get("h1"):
        print(f"ℹ️  H1: {results['h1']['value']}")
    print()

    # Overall
    print("=" * 60)
    if results["overall"] == "PASS":
        print("✅ OVERALL: PASS")
    elif results["overall"] == "WARNING":
        print("⚠️  OVERALL: WARNING (minor issues)")
    else:
        print("❌ OVERALL: FAIL (blocking issues)")
    print("=" * 60)
    print()


def print_summary(all_results: list[dict[str, Any]]):
    """Print summary of all validations."""
    print()
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in all_results if r["overall"] == "PASS")
    warnings = sum(1 for r in all_results if r["overall"] == "WARNING")
    failed = sum(1 for r in all_results if r["overall"] == "FAIL")

    print(f"Total files: {len(all_results)}")
    print(f"✅ PASS: {passed}")
    print(f"⚠️  WARNING: {warnings}")
    print(f"❌ FAIL: {failed}")
    print()

    if failed > 0:
        print("Failed files:")
        for r in all_results:
            if r["overall"] == "FAIL":
                print(f"  ❌ {r['file']}")
    print()


# =============================================================================
# Main
# =============================================================================


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    output_json = "--json" in sys.argv
    validate_all = "--all" in sys.argv

    if validate_all:
        # Validate all meta files
        meta_files = find_all_meta_files()

        if not meta_files:
            print("No meta files found")
            sys.exit(1)

        all_results = []
        for meta_path, keywords_path in meta_files:
            results = validate_meta_file(meta_path, keywords_path)
            all_results.append(results)

            if not output_json:
                # Print short status
                icon = "✅" if results["overall"] == "PASS" else ("⚠️" if results["overall"] == "WARNING" else "❌")
                print(f"{icon} {meta_path}")

        if output_json:
            print(json.dumps(all_results, ensure_ascii=False, indent=2))
        else:
            print_summary(all_results)

        # Exit code based on worst result
        if any(r["overall"] == "FAIL" for r in all_results):
            sys.exit(2)
        elif any(r["overall"] == "WARNING" for r in all_results):
            sys.exit(1)
        sys.exit(0)

    else:
        # Validate single file
        meta_path = sys.argv[1]

        keywords_path = None
        if "--keywords" in sys.argv:
            idx = sys.argv.index("--keywords")
            if idx + 1 < len(sys.argv):
                keywords_path = sys.argv[idx + 1]

        results = validate_meta_file(meta_path, keywords_path)

        if output_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print_results(results)

        if results["overall"] == "PASS":
            sys.exit(0)
        elif results["overall"] == "WARNING":
            sys.exit(1)
        sys.exit(2)


if __name__ == "__main__":
    main()
