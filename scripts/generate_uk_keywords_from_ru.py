#!/usr/bin/env python3
"""
Generate uk/data/uk_keywords.json from RU categories with translation.
Uses RU frequency as fallback until real UK frequency is collected.
"""

import json
import sys
from pathlib import Path

# Import translation map from export script
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude/skills/uk-keywords-export/scripts"))
from export_uk_keywords import translate_keyword


def extract_from_list_or_dict(data_field) -> list[dict]:
    """Extract keywords from either a list or dict structure."""
    results = []

    if isinstance(data_field, list):
        # Standard format: [{"keyword": "...", "volume": X}, ...]
        for item in data_field:
            if isinstance(item, dict) and "keyword" in item:
                results.append(
                    {
                        "keyword": item["keyword"],
                        "volume": item.get("volume", 0),
                        "use_in": item.get("use_in", "content"),
                    }
                )
    elif isinstance(data_field, dict):
        # Non-standard format: {"primary": [...], "synonyms_base": [...], ...}
        for group_name, group_items in data_field.items():
            if isinstance(group_items, list):
                for item in group_items:
                    if isinstance(item, dict) and "keyword" in item:
                        # commercial group has use_in: meta_only
                        use_in = item.get("use_in", "meta_only" if group_name == "commercial" else "content")
                        results.append({"keyword": item["keyword"], "volume": item.get("volume", 0), "use_in": use_in})

    return results


def extract_keywords_with_volume(filepath: Path) -> list[dict]:
    """Extract keywords with volume from _clean.json file."""
    keywords = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract from keywords (list or dict)
        keywords.extend(extract_from_list_or_dict(data.get("keywords", [])))

        # Extract from synonyms (list or dict)
        keywords.extend(extract_from_list_or_dict(data.get("synonyms", [])))

        # Extract from variations (list or dict)
        keywords.extend(extract_from_list_or_dict(data.get("variations", [])))

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)

    return keywords


def get_category_slug(filepath: Path) -> str:
    """Extract category slug from filepath."""
    # Path like: categories/.../data/slug_clean.json
    filename = filepath.stem  # e.g., "aktivnaya-pena_clean"
    return filename.replace("_clean", "")


def get_category_name_uk(ru_name: str) -> str:
    """Translate category name to UK."""
    return translate_keyword(ru_name)


def main():
    project_root = Path(__file__).resolve().parents[1]
    categories_dir = project_root / "categories"
    output_file = project_root / "uk" / "data" / "uk_keywords.json"

    # Find all _clean.json files
    clean_files = list(categories_dir.glob("**/data/*_clean.json"))

    if not clean_files:
        print("No _clean.json files found!", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(clean_files)} category files")

    # Build UK keywords by category
    uk_keywords = {"categories": {}, "meta": {"source": "ru_fallback", "version": "1.0"}}

    for filepath in clean_files:
        slug = get_category_slug(filepath)
        ru_keywords = extract_keywords_with_volume(filepath)

        if not ru_keywords:
            print(f"  Warning: No keywords in {slug}")
            continue

        # Read original to get name
        with open(filepath, "r", encoding="utf-8") as f:
            ru_data = json.load(f)

        ru_name = ru_data.get("name", slug)
        uk_name = get_category_name_uk(ru_name)

        # Translate keywords
        uk_kws = []
        seen = set()
        for kw in ru_keywords:
            uk_text = translate_keyword(kw["keyword"])
            if uk_text not in seen:
                seen.add(uk_text)
                uk_kws.append(
                    {
                        "keyword": uk_text,
                        "volume": kw["volume"],  # RU volume as fallback
                        "use_in": kw["use_in"],
                        "source_ru": kw["keyword"],
                    }
                )

        # Sort by volume desc
        uk_kws.sort(key=lambda x: -x["volume"])

        total_volume = sum(kw["volume"] for kw in uk_kws)

        uk_keywords["categories"][slug] = {
            "name_uk": uk_name,
            "name_ru": ru_name,
            "count": len(uk_kws),
            "total_volume": total_volume,
            "keywords": uk_kws[:10],  # Top 10
            "synonyms": uk_kws[10:],  # Rest as synonyms
        }

        print(f"  {slug}: {len(uk_kws)} keywords, volume={total_volume}")

    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(uk_keywords, f, ensure_ascii=False, indent=2)

    print(f"\nOutput: {output_file}")
    print(f"Categories: {len(uk_keywords['categories'])}")


if __name__ == "__main__":
    main()
