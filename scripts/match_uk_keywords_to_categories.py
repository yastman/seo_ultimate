#!/usr/bin/env python3
"""
Matches UK keywords to RU categories using source_ru field.
Uses RU keywords from _clean.json as ground truth for category assignment.
"""

import json
import re
from collections import defaultdict
from pathlib import Path


def load_ru_mapping() -> dict:
    with open("data/generated/ru_keywords_mapping.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_current_uk_keywords() -> dict:
    with open("uk/data/uk_keywords.json", "r", encoding="utf-8") as f:
        return json.load(f)


def normalize_keyword(kw: str) -> str:
    """Normalize keyword for matching."""
    kw = kw.lower().strip()
    # Remove common suffixes/variations
    kw = re.sub(r"\s*(для\s+)?(авто|автомобил[яь]|машин[ыу])\s*", " ", kw)
    kw = re.sub(r"\s+", " ", kw).strip()
    return kw


def build_ru_keyword_index(ru_mapping: dict) -> dict:
    """Build index: ru_keyword_normalized -> slug"""
    index = {}
    for slug, data in ru_mapping.items():
        for kw_data in data["keywords"]:
            kw = kw_data["keyword"]
            # Index exact
            index[kw.lower()] = slug
            # Index normalized
            normalized = normalize_keyword(kw)
            if normalized not in index:
                index[normalized] = slug
    return index


# Manual overrides for keywords that don't match automatically
MANUAL_OVERRIDES = {
    "губки для мойки автомобиля": "gubki-i-varezhki",
    "ведро для мытья машины": "vedra-i-emkosti",
    "полироль для колес": "cherniteli-shin",  # колёса = шины
    "чернение колес": "cherniteli-shin",
    "полироль для резины": "cherniteli-shin",
    "средства по уходу за кожей автомобиля": "sredstva-dlya-kozhi",
}


def match_source_ru(source_ru: str, ru_index: dict) -> str | None:
    """Find matching RU category for source_ru keyword."""
    source_lower = source_ru.lower()

    # Check manual overrides first
    if source_lower in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[source_lower]

    # Direct match
    if source_lower in ru_index:
        return ru_index[source_lower]

    # Normalized match
    normalized = normalize_keyword(source_ru)
    if normalized in ru_index:
        return ru_index[normalized]

    # Partial match - check if source_ru is contained in any RU keyword
    for ru_kw, slug in ru_index.items():
        if source_lower in ru_kw or ru_kw in source_lower:
            return slug

    return None


def main():
    ru_mapping = load_ru_mapping()
    current_uk = load_current_uk_keywords()
    ru_index = build_ru_keyword_index(ru_mapping)

    # Collect all UK keywords
    all_uk_keywords = []
    for slug, cat_data in current_uk.get("categories", {}).items():
        for kw_data in cat_data.get("keywords", []):
            kw_data["_original_category"] = slug
            all_uk_keywords.append(kw_data)

    print(f"Total UK keywords to redistribute: {len(all_uk_keywords)}")

    # Match and redistribute
    new_categories = defaultdict(lambda: {"keywords": [], "total_volume": 0})
    unmatched = []

    for kw_data in all_uk_keywords:
        source_ru = kw_data.get("source_ru", "")
        volume = kw_data.get("volume", 0)

        matched_slug = match_source_ru(source_ru, ru_index) if source_ru else None

        if matched_slug:
            new_categories[matched_slug]["keywords"].append(kw_data)
            new_categories[matched_slug]["total_volume"] += volume
        else:
            unmatched.append(kw_data)

    # Build output
    output = {
        "generated": "2026-01-26",
        "method": "source_ru_to_ru_categories_match",
        "total_keywords": len(all_uk_keywords),
        "matched": len(all_uk_keywords) - len(unmatched),
        "unmatched_count": len(unmatched),
        "categories": dict(new_categories),
    }

    # Add unmatched to special key
    if unmatched:
        output["unmatched"] = unmatched

    # Write output
    output_path = Path("uk/data/uk_keywords_fixed.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Matched: {len(all_uk_keywords) - len(unmatched)}")
    print(f"Unmatched: {len(unmatched)}")
    print(f"Categories with keywords: {len(new_categories)}")
    print(f"Output: {output_path}")

    # Show redistribution changes
    print("\n--- Redistribution Summary ---")
    changes = []
    for kw_data in all_uk_keywords:
        orig = kw_data.get("_original_category", "")
        source_ru = kw_data.get("source_ru", "")
        new_cat = match_source_ru(source_ru, ru_index) if source_ru else None
        if new_cat and new_cat != orig:
            changes.append((kw_data["keyword"], orig, new_cat))

    print(f"Keywords that moved: {len(changes)}")
    if changes:
        print("\nFirst 20 moves:")
        for kw, old, new in changes[:20]:
            print(f"  {kw[:40]}: {old} -> {new}")

    if unmatched:
        print("\n--- Unmatched keywords ---")
        for kw in unmatched[:20]:
            print(f"  - {kw['keyword']} (source_ru: {kw.get('source_ru', 'N/A')})")


if __name__ == "__main__":
    main()
