#!/usr/bin/env python3
"""
Анализ дублей ключевых слов в keywords.
Находит семантически идентичные ключи (авто/автомобиля, машины/авто и т.д.)
"""

import json
from collections import defaultdict
from pathlib import Path

# Словарь синонимов для нормализации
SYNONYM_MAP = {
    "автомобиля": "авто",
    "автомобиль": "авто",
    "машины": "авто",
    "машину": "авто",
    "машина": "авто",
    "автомобилей": "авто",
    "автомобили": "авто",
    "машин": "авто",
}


def normalize_keyword(keyword: str) -> str:
    """Нормализует ключ для сравнения."""
    normalized = keyword.lower()
    for old, new in SYNONYM_MAP.items():
        normalized = normalized.replace(old, new)
    return normalized


def find_duplicates_in_keywords(keywords: list) -> list:
    """Находит группы дублей в списке keywords."""
    normalized_groups = defaultdict(list)

    for kw in keywords:
        keyword = kw.get("keyword", "")
        normalized = normalize_keyword(keyword)
        normalized_groups[normalized].append(kw)

    # Возвращаем только группы с дублями (>1 элемент)
    duplicates = []
    for normalized, group in normalized_groups.items():
        if len(group) > 1:
            duplicates.append({"normalized": normalized, "variants": group})

    return duplicates


def analyze_category(json_path: Path) -> dict | None:
    """Анализирует одну категорию на дубли."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    keywords = data.get("keywords", [])
    if not keywords:
        return None

    duplicates = find_duplicates_in_keywords(keywords)

    if not duplicates:
        return None

    return {
        "id": data.get("id", json_path.stem),
        "name": data.get("name", ""),
        "duplicates": duplicates,
        "all_keywords": keywords,
    }


def main():
    categories_dir = Path("categories")

    results = []
    total_categories = 0

    for json_path in sorted(categories_dir.glob("*/data/*_clean.json")):
        total_categories += 1
        result = analyze_category(json_path)
        if result:
            results.append(result)

    # Генерация отчета
    print("# ТЗ: Очистка дублей в keywords")
    print()
    print("**Дата создания:** 2026-01-07")
    print("**Статус:** ⬜ В работе")
    print()
    print("---")
    print()
    print("## Проблема")
    print()
    print("Семантически идентичные ключи (авто/автомобиля, машины/авто) в массиве `keywords`")
    print("создают переспам и занимают место, которое лучше использовать для LSI-расширения.")
    print()
    print("## Правило исправления")
    print()
    print("1. Оставить в `keywords` **короткий** вариант (обычно с «авто»)")
    print("2. Перенести длинный вариант в `synonyms`")
    print("3. При равной длине — оставить вариант с большим volume")
    print()
    print("---")
    print()
    print("## Статистика")
    print()
    print(f"- Всего категорий: **{total_categories}**")
    print(f"- С дублями: **{len(results)}**")
    print(f"- Без дублей: **{total_categories - len(results)}**")
    print()
    print("---")
    print()

    if results:
        print("## Категории для исправления")
        print()

        for r in results:
            print(f"### {r['name']} (`{r['id']}`)")
            print()
            print("**Текущие keywords:**")
            for kw in r["all_keywords"]:
                print(f"- `{kw['keyword']}` (volume: {kw.get('volume', 0)})")
            print()

            print("**Найденные дубли:**")
            for dup in r["duplicates"]:
                variants_str = ", ".join([f"`{v['keyword']}`" for v in dup["variants"]])
                print(f"- {variants_str} → нормализуется в `{dup['normalized']}`")
            print()

            # Рекомендация
            print("**Рекомендация:**")
            for dup_item in r["duplicates"]:
                # Сортируем: короче = лучше, при равной длине — больший volume
                sorted_variants = sorted(dup_item["variants"], key=lambda x: (len(x["keyword"]), -x.get("volume", 0)))
                keep = sorted_variants[0]
                move = sorted_variants[1:]

                print(f"- [ ] Оставить в keywords: `{keep['keyword']}`")
                for m in move:
                    print(f"- [ ] Перенести в synonyms: `{m['keyword']}`")
            print()
    else:
        print("## Результат")
        print()
        print("✅ Дублей не найдено!")


if __name__ == "__main__":
    main()
