#!/usr/bin/env python3
"""Удаление ключей с частотностью 0 из всех категорий."""

import json
from pathlib import Path

# Путь к папке с категориями
categories_dir = Path("categories")

# Результаты для отчета
report = {"total_categories": 0, "categories_with_zero_freq": [], "total_keys_removed": 0, "details": []}

# Проходим по всем категориям
for category_path in sorted(categories_dir.iterdir()):
    if not category_path.is_dir():
        continue

    report["total_categories"] += 1
    slug = category_path.name
    clean_json_path = category_path / "data" / "_clean.json"

    if not clean_json_path.exists():
        continue

    # Читаем _clean.json
    with open(clean_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Проверяем ключи
    original_keys = data.get("keywords", [])
    keys_before = len(original_keys)

    # Фильтруем ключи с частотностью > 0
    filtered_keys = [k for k in original_keys if k.get("frequency", 0) > 0]
    keys_after = len(filtered_keys)
    removed_count = keys_before - keys_after

    if removed_count > 0:
        # Обновляем данные
        data["keywords"] = filtered_keys

        # Сохраняем обратно
        with open(clean_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Добавляем в отчет
        report["categories_with_zero_freq"].append(slug)
        report["total_keys_removed"] += removed_count
        report["details"].append(
            {"slug": slug, "keys_before": keys_before, "keys_after": keys_after, "removed": removed_count}
        )

# Выводим отчет
print("=== ОТЧЕТ ПО УДАЛЕНИЮ КЛЮЧЕЙ С ЧАСТОТНОСТЬЮ 0 ===\n")
print(f"Всего категорий проверено: {report['total_categories']}")
print(f"Категорий с удаленными ключами: {len(report['categories_with_zero_freq'])}")
print(f"Всего ключей удалено: {report['total_keys_removed']}\n")

if report["details"]:
    print("ДЕТАЛИ ПО КАТЕГОРИЯМ:\n")
    for detail in report["details"]:
        print(f"📁 {detail['slug']}")
        print(f"   Было ключей: {detail['keys_before']}")
        print(f"   Стало ключей: {detail['keys_after']}")
        print(f"   Удалено: {detail['removed']}")
        print()
else:
    print("✅ Ключей с частотностью 0 не найдено!")

# Сохраняем отчет в файл
with open("ZERO_FREQUENCY_CLEANUP_REPORT.md", "w", encoding="utf-8") as f:
    f.write("# Отчет по удалению ключей с частотностью 0\n\n")
    f.write("**Дата:** 2026-01-19\n\n")
    f.write("## Сводка\n\n")
    f.write(f"- Всего категорий проверено: **{report['total_categories']}**\n")
    f.write(f"- Категорий с удаленными ключами: **{len(report['categories_with_zero_freq'])}**\n")
    f.write(f"- Всего ключей удалено: **{report['total_keys_removed']}**\n\n")

    if report["details"]:
        f.write("## Детали по категориям\n\n")
        f.write("| Категория | Было ключей | Стало ключей | Удалено |\n")
        f.write("|-----------|-------------|--------------|----------|\n")
        for detail in report["details"]:
            f.write(
                f"| `{detail['slug']}` | {detail['keys_before']} | {detail['keys_after']} | **{detail['removed']}** |\n"
            )

        f.write("\n### Список категорий с изменениями\n\n")
        for slug in report["categories_with_zero_freq"]:
            f.write(f"- `{slug}`\n")
    else:
        f.write("✅ **Ключей с частотностью 0 не найдено!**\n")

print("\n📄 Отчет сохранен в файл: ZERO_FREQUENCY_CLEANUP_REPORT.md")
