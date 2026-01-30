#!/usr/bin/env python3
"""Извлечение всех ключей из RU категорий в MD файл."""

import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT / "categories"
OUTPUT_FILE = ROOT / "data" / "generated" / "RU_KEYWORDS.md"


def extract_keywords_from_file(filepath: Path) -> set[str]:
    """Извлекает все ключи из _clean.json файла."""
    keywords = set()

    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"⚠️  {filepath.name}: {e}")
        return keywords

    keywords_data = data.get("keywords", [])
    synonyms_data = data.get("synonyms", [])
    variations_data = data.get("variations", [])

    # Handle legacy format: keywords is dict with groups
    if isinstance(keywords_data, dict):
        for group_items in keywords_data.values():
            if isinstance(group_items, list):
                for item in group_items:
                    if "keyword" in item:
                        keywords.add(item["keyword"].lower().strip())
    else:
        # New format: keywords is list
        for item in keywords_data:
            if "keyword" in item:
                keywords.add(item["keyword"].lower().strip())

    # Synonyms
    if isinstance(synonyms_data, list):
        for item in synonyms_data:
            if "keyword" in item:
                keywords.add(item["keyword"].lower().strip())

    # Variations
    if isinstance(variations_data, list):
        for item in variations_data:
            if "keyword" in item:
                keywords.add(item["keyword"].lower().strip())

    return keywords


def main():
    all_keywords = set()
    files_count = 0

    for clean_file in sorted(CATEGORIES_DIR.rglob("*_clean.json")):
        keywords = extract_keywords_from_file(clean_file)
        all_keywords.update(keywords)
        files_count += 1

    # Sort and save
    sorted_keywords = sorted(all_keywords)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text("\n".join(sorted_keywords), encoding="utf-8")

    print(f"Найдено {files_count} файлов _clean.json")
    print(f"Извлечено {len(sorted_keywords)} уникальных ключей")
    print(f"✅ Сохранено → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
