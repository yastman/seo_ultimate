#!/usr/bin/env python3
"""
Extracts all keywords from RU _clean.json files.
Creates mapping: slug -> [keywords with volumes]
"""

import json
from pathlib import Path


def extract_ru_keywords():
    categories_dir = Path("categories")
    mapping = {}

    for clean_file in categories_dir.rglob("*_clean.json"):
        with open(clean_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        slug = data.get("id") or data.get("slug")
        if not slug:
            continue

        keywords = []

        # V2 format: keywords is list
        if isinstance(data.get("keywords"), list):
            keywords.extend(data["keywords"])
        # Legacy format: keywords is dict with groups
        elif isinstance(data.get("keywords"), dict):
            for group in data["keywords"].values():
                keywords.extend(group)

        # Add synonyms if present
        if isinstance(data.get("synonyms"), list):
            for syn in data["synonyms"]:
                if isinstance(syn, dict) and "keyword" in syn:
                    keywords.append(syn)

        if keywords:
            mapping[slug] = {"keywords": keywords, "path": str(clean_file.relative_to(categories_dir))}

    return mapping


def main():
    mapping = extract_ru_keywords()

    output_path = Path("data/generated/ru_keywords_mapping.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(mapping)} categories")
    total_kws = sum(len(v["keywords"]) for v in mapping.values())
    print(f"Total keywords: {total_kws}")


if __name__ == "__main__":
    main()
