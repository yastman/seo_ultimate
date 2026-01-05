#!/usr/bin/env python3
"""
synonym_tools.py — Unified tool for synonym analysis and cleanup.

Combines functionality of:
- analyze_synonyms.py (Report)
- batch_synonym_cleanup.py (Cleanup)
- propose_synonyms.py (Proposal)

Usage:
    python scripts/synonym_tools.py analyze [--fix]
    python scripts/synonym_tools.py report
"""

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CATEGORIES_DIR = PROJECT_ROOT / "categories"
REPORT_FILE = PROJECT_ROOT / "tasks" / "synonym_cleanup_report.md"

# Synonyms for normalization (SSOT)
AUTO_SYNONYMS = ["авто", "автомобиля", "машины", "машина", "автомобиль", "в авто", "для авто"]
STOP_WORDS = {"для", "в", "на", "под", "с", "от"}

# Commercial intent markers (to separate commercial keys from informational)
COMMERCIAL_MARKERS = ["купить", "цена", "отзывы", "заказать", "стоимость", "киев", "украина"]

# =============================================================================
# Logic: Normalization
# =============================================================================


def normalize_keyword(keyword: str) -> str:
    """
    Creates a canonical fingerprint of the keyword for comparison.
    1. Lowercase
    2. Remove 'avto' related words
    3. Remove stop words
    4. Stem common prefixes (polir, ochist)
    5. Sort words
    """
    text = keyword.lower()

    # 1. Remove specific auto terms
    for syn in AUTO_SYNONYMS:
        text = text.replace(syn, "")

    # 2. Remove stop words
    # Use word boundaries to avoid replacing inside words
    for sw in STOP_WORDS:
        text = re.sub(rf"\b{sw}\b", " ", text)

    # 3. Clean up spaces and split
    words = [w for w in re.split(r"\s+", text) if w.strip()]

    # 4. Handle specific stemming/variations
    normalized_words = []
    for w in words:
        if w.startswith("полиров") or w.startswith("полирал"):
            normalized_words.append("полир")
        elif w.startswith("очистит"):
            normalized_words.append("очист")
        elif w.startswith("кузов"):
            normalized_words.append("кузов")
        else:
            normalized_words.append(w)

    # 5. Sort to handle word order
    normalized_words.sort()

    return " ".join(normalized_words)


def is_commercial(keyword: str) -> bool:
    """Checks if keyword has commercial intent."""
    return any(marker in keyword.lower() for marker in COMMERCIAL_MARKERS)


# =============================================================================
# Logic: Analysis & Proposal
# =============================================================================


def analyze_category(category_path: Path) -> dict | None:
    """
    Analyzes a category for synonym clusters.
    Returns dict with proposed changes or None.
    """
    slug = category_path.name
    clean_json_path = category_path / "data" / f"{slug}_clean.json"

    if not clean_json_path.exists():
        return None

    try:
        data = json.loads(clean_json_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Error reading {clean_json_path}: {e}")
        return None

    keywords_flat = []

    # Flatten all keywords with metadata
    sections = ["primary", "secondary", "supporting", "commercial"]
    for section in sections:
        if section in data.get("keywords", {}):
            for k in data["keywords"][section]:
                # Work with copy to not mutate original immediately if we passed a ref
                k_copy = k.copy()
                k_copy["original_section"] = section
                keywords_flat.append(k_copy)

    # Group by normalized key
    clusters = defaultdict(list)
    for k in keywords_flat:
        norm = normalize_keyword(k["keyword"])
        if not norm:  # If empty (e.g. just "avto"), use original
            norm = k["keyword"].lower()
        clusters[norm].append(k)

    proposed_changes = []

    for norm, group in clusters.items():
        if len(group) < 2:
            continue

        # Sort group to find winner:
        # Prioritize high volume, then shorter length
        group.sort(key=lambda x: (-x.get("volume", 0), len(x["keyword"])))

        winner = group[0]
        losers = group[1:]

        # Create change record
        change_record = {"winner": winner, "losers": losers, "norm_key": norm}
        proposed_changes.append(change_record)

    return {
        "slug": slug,
        "path": category_path,
        "changes": proposed_changes,
        "total_keywords": len(keywords_flat),
        "clean_json_path": clean_json_path,
        "original_data": data,
    }


def generate_report():
    """Generates a Markdown report of potential duplicate synonyms."""
    print("generating report...")
    report_lines = ["# Synonym Cleanup Report\n"]
    report_lines.append("| Category | Total Keys | Clusters Found | Details |")
    report_lines.append("|---|---|---|---|")

    cats = sorted([d for d in CATEGORIES_DIR.iterdir() if d.is_dir()])

    count_cats = 0
    count_clusters = 0

    for cat_path in cats:
        result = analyze_category(cat_path)
        if not result or not result["changes"]:
            continue

        count_cats += 1
        count_clusters += len(result["changes"])

        # Detailed breakdown
        details_list = []
        for c in result["changes"]:
            w = c["winner"]
            l_str = ", ".join([f"`{l['keyword']}` ({l['volume']})" for l in c["losers"]])
            details_list.append(f"**Keep**: `{w['keyword']}` ({w['volume']}) vs **Drop**: {l_str}")

        details_str = "<br>".join(details_list)
        report_lines.append(
            f"| {result['slug']} | {result['total_keywords']} | {len(result['changes'])} | {details_str} |"
        )

    REPORT_FILE.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"✅ Report generated at {REPORT_FILE}")
    print(f"Found {count_clusters} clusters in {count_cats} categories.")


# =============================================================================
# Logic: Fix / Cleanup
# =============================================================================


def apply_cleanup(category_path: Path):
    """
    Applies synonym cleanup to a single category.
    Merges losers into winner (sum volume?) or just drops losers.
    Current logic: Keep winner, drop losers.
    """
    result = analyze_category(category_path)
    if not result or not result["changes"]:
        return 0

    data = result["original_data"]
    result["slug"]

    # Map keywords to remove
    keywords_to_remove = set()
    for c in result["changes"]:
        for loser in c["losers"]:
            keywords_to_remove.add(loser["keyword"])

    if not keywords_to_remove:
        return 0

    # Filter keywords in data
    removed_count = 0
    new_keywords_section = {}

    sections = ["primary", "secondary", "supporting", "commercial"]
    current_keywords = data.get("keywords", {})

    for section in sections:
        if section not in current_keywords:
            continue

        kept = []
        for k in current_keywords[section]:
            if k["keyword"] in keywords_to_remove:
                removed_count += 1
            else:
                kept.append(k)
        new_keywords_section[section] = kept

    # Update data
    data["keywords"] = new_keywords_section

    # Recalculate stats
    total_vol = 0
    total_count = 0
    for section in new_keywords_section:
        for k in new_keywords_section[section]:
            total_vol += k.get("volume", 0)
            total_count += 1

    if "stats" not in data:
        data["stats"] = {}
    data["stats"]["after"] = total_count
    data["stats"]["total_volume"] = total_vol

    # Save
    with open(result["clean_json_path"], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return removed_count


def run_cleanup():
    """Runs cleanup for all categories."""
    print("🧹 Running synonym cleanup...")
    cats = sorted([d for d in CATEGORIES_DIR.iterdir() if d.is_dir()])

    total_removed = 0
    categories_affected = 0

    for cat_path in cats:
        removed = apply_cleanup(cat_path)
        if removed > 0:
            print(f"   Fixed {cat_path.name}: removed {removed} duplicates")
            total_removed += removed
            categories_affected += 1

    print("\n✅ Cleanup complete.")
    print(f"Categories affected: {categories_affected}")
    print(f"Total duplicates removed: {total_removed}")


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Synonym Analysis & Cleanup Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Command: report
    subparsers.add_parser("report", help="Generate synonym overlap report")

    # Command: cleanup
    subparsers.add_parser("cleanup", help="Apply cleanup to remove duplicates")

    # Command: analyze (same as report for now, but prints to stdout/short)
    subparsers.add_parser("analyze", help="Analyze without generating full file report")

    args = parser.parse_args()

    if args.command == "report":
        generate_report()
    elif args.command == "cleanup":
        print("⚠️  This will modify _clean.json files. Make sure you have a backup!")
        confirm = input("Type 'yes' to proceed: ")
        if confirm.lower() == "yes":
            run_cleanup()
        else:
            print("Aborted.")
    elif args.command == "analyze":
        generate_report()  # Reuse report logic
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
