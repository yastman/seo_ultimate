#!/usr/bin/env python3
"""
extract_uk_keywords_list.py — Извлечение всех UK ключей из uk/categories/

Сканирует uk/categories/**/*_clean.json и извлекает:
- keywords[].keyword
- synonyms[].keyword
- variations[].keyword

Сохраняет уникальные ключи в data/generated/UK_KEYWORDS.md

Usage:
    python3 scripts/extract_uk_keywords_list.py
"""

import json
from pathlib import Path


def extract_keywords_from_file(file_path: Path) -> set[str]:
    """Извлекает все ключи из _clean.json файла."""
    keywords = set()

    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"  ⚠️  Ошибка чтения {file_path}: {e}")
        return keywords

    # V3 format: keywords is list
    if isinstance(data.get("keywords"), list):
        for item in data["keywords"]:
            if isinstance(item, dict) and item.get("keyword"):
                keywords.add(item["keyword"].strip())

    # Legacy format: keywords is dict with groups
    elif isinstance(data.get("keywords"), dict):
        for group in data["keywords"].values():
            if isinstance(group, list):
                for item in group:
                    if isinstance(item, dict) and item.get("keyword"):
                        keywords.add(item["keyword"].strip())

    # Synonyms
    for item in data.get("synonyms", []):
        if isinstance(item, dict) and item.get("keyword"):
            keywords.add(item["keyword"].strip())

    # Variations
    for item in data.get("variations", []):
        if isinstance(item, dict) and item.get("keyword"):
            keywords.add(item["keyword"].strip())

    return keywords


def main():
    project_root = Path(__file__).parent.parent
    uk_categories_dir = project_root / "uk" / "categories"
    output_dir = project_root / "data" / "generated"

    # Создать директорию если не существует
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Извлечение UK ключей из uk/categories/")
    print("=" * 60)

    if not uk_categories_dir.exists():
        print(f"  ⚠️  Директория не существует: {uk_categories_dir}")
        return

    all_keywords: set[str] = set()
    files_processed = 0

    # Сканируем все *_clean.json
    for clean_file in uk_categories_dir.rglob("*_clean.json"):
        file_keywords = extract_keywords_from_file(clean_file)
        if file_keywords:
            all_keywords.update(file_keywords)
            files_processed += 1
            print(f"  ✓ {clean_file.relative_to(project_root)}: {len(file_keywords)} ключей")

    # Сортируем по алфавиту
    sorted_keywords = sorted(all_keywords, key=str.lower)

    # Записываем в MD файл
    output_file = output_dir / "UK_KEYWORDS.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# UK Keywords List\n\n")
        f.write(f"Всего: {len(sorted_keywords)} уникальных ключей\n")
        f.write(f"Файлов обработано: {files_processed}\n\n")
        f.write("---\n\n")
        for kw in sorted_keywords:
            f.write(f"{kw}\n")

    print()
    print("=" * 60)
    print(f"✅ Готово!")
    print(f"   Файлов обработано: {files_processed}")
    print(f"   Уникальных ключей: {len(sorted_keywords)}")
    print(f"   Результат: {output_file.relative_to(project_root)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
