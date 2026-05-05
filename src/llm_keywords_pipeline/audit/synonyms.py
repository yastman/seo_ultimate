#!/usr/bin/env python3
"""
audit_synonyms.py — Аудит разделения keywords/synonyms в _clean.json файлах.

Проверяет соответствие правилам TZ_SEO_SYNONYMS.md

Usage:
    uv run python -m llm_keywords_pipeline.audit.synonyms
"""

from __future__ import annotations

import json
from pathlib import Path

from llm_keywords_pipeline.core.config import CATEGORIES_DIR

# Паттерны, которые должны быть в synonyms, а не в keywords
COMMERCIAL_PATTERNS = [
    "купить",
    "цена",
    "в украине",
    "в україні",
    "киев",
    "київ",
    "недорого",
    "отзывы",
    "фото",
    "стоимость",
]

# Модификаторы (могут быть допустимы в keywords если это часть названия категории)
MODIFIER_PATTERNS = ["для авто", "для автомобиля", "для машины", "для машин"]


def audit_category(json_path: Path) -> dict:
    """Проверяет один JSON файл и возвращает найденные проблемы."""
    issues = {
        "json_error": None,
        "no_synonyms": False,
        "commercial_in_keywords": [],
        "long_tail_in_keywords": [],  # Фразы > 4 слов
        "keywords_count": 0,
        "synonyms_count": 0,
    }

    try:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        issues["json_error"] = str(e)
        return issues

    keywords = data.get("keywords", [])
    synonyms = data.get("synonyms", None)

    issues["keywords_count"] = len(keywords)

    # Проверка наличия synonyms
    if synonyms is None:
        issues["no_synonyms"] = True
    else:
        issues["synonyms_count"] = len(synonyms)

    # Проверка коммерческих терминов в keywords
    for kw in keywords:
        if not isinstance(kw, dict):
            continue
        keyword_text = kw.get("keyword", "").lower()

        # Проверка коммерческих паттернов
        for pattern in COMMERCIAL_PATTERNS:
            if pattern in keyword_text:
                issues["commercial_in_keywords"].append(
                    {"keyword": kw.get("keyword"), "pattern": pattern}
                )
                break

        # Проверка длинных хвостов (более 4 слов)
        word_count = len(keyword_text.split())
        if word_count > 4:
            issues["long_tail_in_keywords"].append(
                {"keyword": kw.get("keyword"), "word_count": word_count}
            )

    return issues


def main():
    print("=" * 60)
    print("АУДИТ РАЗДЕЛЕНИЯ KEYWORDS/SYNONYMS")
    print("=" * 60)

    all_issues = {}
    json_errors = []
    no_synonyms = []
    commercial_issues = []
    long_tail_issues = []

    for json_file in sorted(CATEGORIES_DIR.glob("*/data/*_clean.json")):
        slug = json_file.parent.parent.name
        issues = audit_category(json_file)

        if issues["json_error"]:
            json_errors.append((slug, issues["json_error"]))
            continue

        if issues["no_synonyms"]:
            no_synonyms.append(slug)

        if issues["commercial_in_keywords"]:
            for item in issues["commercial_in_keywords"]:
                commercial_issues.append((slug, item["keyword"], item["pattern"]))

        if issues["long_tail_in_keywords"]:
            for item in issues["long_tail_in_keywords"]:
                long_tail_issues.append((slug, item["keyword"], item["word_count"]))

        all_issues[slug] = issues

    # Вывод результатов
    print(f"\n📁 Проверено категорий: {len(all_issues) + len(json_errors)}")

    if json_errors:
        print(f"\n❌ JSON ОШИБКИ ({len(json_errors)}):")
        for slug, error in json_errors:
            print(f"   - {slug}: {error}")

    if no_synonyms:
        print(f"\n⚠️  КАТЕГОРИИ БЕЗ SYNONYMS ({len(no_synonyms)}):")
        for slug in no_synonyms:
            print(f"   - {slug}")

    if commercial_issues:
        print(f"\n🔴 КОММЕРЧЕСКИЕ ТЕРМИНЫ В KEYWORDS ({len(commercial_issues)}):")
        for slug, kw, pattern in commercial_issues:
            print(f'   - {slug}: "{kw}" (паттерн: "{pattern}")')

    if long_tail_issues:
        print(f"\n🟡 ДЛИННЫЕ ХВОСТЫ В KEYWORDS ({len(long_tail_issues)}):")
        for slug, kw, wc in long_tail_issues:
            print(f'   - {slug}: "{kw}" ({wc} слов)')

    # Итог
    total_problems = (
        len(json_errors) + len(no_synonyms) + len(commercial_issues) + len(long_tail_issues)
    )
    if total_problems == 0:
        print("\n✅ Все категории соответствуют правилам TZ_SEO_SYNONYMS.md")
    else:
        print(f"\n📊 ИТОГО ПРОБЛЕМ: {total_problems}")
        print("   - JSON ошибки:", len(json_errors))
        print("   - Без synonyms:", len(no_synonyms))
        print("   - Коммерческие в keywords:", len(commercial_issues))
        print("   - Длинные хвосты в keywords:", len(long_tail_issues))


if __name__ == "__main__":
    main()
