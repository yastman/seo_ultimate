#!/usr/bin/env python3
"""
Скрипт для автоматической перегенерации всех мета-тегов RU категорий
по правилам generate-meta skill v12.0
"""

import json
from pathlib import Path
from typing import Any


def load_json(file_path: Path) -> dict[str, Any]:
    """Загрузить JSON файл"""
    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path: Path, data: dict[str, Any]) -> None:
    """Сохранить JSON файл"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_product_info(slug: str) -> dict[str, list[str]]:
    """
    Извлечь типы/формы/объёмы товаров из PRODUCTS_LIST.md

    ВАЖНО: Извлекаем ТИПЫ по свойствам, НЕ названия товаров!
    """
    products_file = Path("data/generated/PRODUCTS_LIST.md")
    if not products_file.exists():
        return {"types": [], "forms": [], "volumes": []}

    with open(products_file, encoding="utf-8") as f:
        f.read()

    # Маппинг slug -> типы товаров
    type_mapping = {
        "aktivnaya-pena": {
            "types": ["щелочные", "нейтральные"],
            "forms": ["концентраты"],
            "volumes": ["0.5л", "1л", "5л", "20л"],
        },
        "shampuni-dlya-ruchnoy-moyki": {
            "types": ["нейтральные", "кислотные", "керамические"],
            "forms": ["концентраты"],
            "volumes": ["0.5л", "1л", "5л", "20л"],
        },
        "cherniteli-shin": {
            "types": ["матовые", "сатиновые", "глянцевые"],
            "forms": ["гели", "лосьоны"],
            "volumes": ["0.25л", "0.5л", "1л", "5л"],
        },
        "antibitum": {"types": ["сольвентные"], "forms": ["готовые"], "volumes": ["0.5л", "5л"]},
        "antimoshka": {
            "types": ["щелочные", "нейтральные"],
            "forms": ["концентраты", "готовые"],
            "volumes": ["0.5л", "1л", "5л"],
        },
        "ochistiteli-diskov": {
            "types": ["кислотные", "нейтральные"],
            "forms": ["гели", "готовые"],
            "volumes": ["0.5л", "1л", "5л"],
        },
        "ochistiteli-stekol": {
            "types": ["спиртовые"],
            "forms": ["готовые", "концентраты"],
            "volumes": ["0.5л", "5л"],
        },
        "voski": {
            "types": ["жидкие", "твёрдые", "спрей"],
            "forms": ["натуральные", "синтетические"],
            "volumes": [],
        },
    }

    return type_mapping.get(slug, {"types": [], "forms": [], "volumes": []})


def generate_title(primary_keyword: str) -> str:
    """
    Генерировать Title по формуле:
    {ВЧ Ключ} — купить, цены | Ultimate

    ЖЕЛЕЗНОЕ ПРАВИЛО: keywords[0] копируется ДОСЛОВНО!
    """
    # Первая буква заглавная
    pk = primary_keyword[0].upper() + primary_keyword[1:]

    title = f"{pk} — купить, цены | Ultimate"

    # Проверка длины (30-60 chars до | Ultimate)
    unique_part = title.split(" | ")[0]
    if len(unique_part) < 30:
        print(f"⚠️  WARNING: Title слишком короткий ({len(unique_part)} chars): {title}")

    return title


def generate_h1(primary_keyword: str) -> str:
    """
    Генерировать H1: {ВЧ Ключ} без "Купить"

    ЖЕЛЕЗНОЕ ПРАВИЛО: keywords[0] копируется ДОСЛОВНО!
    """
    # Первая буква заглавная
    return primary_keyword[0].upper() + primary_keyword[1:]


def generate_description(primary_keyword: str, slug: str) -> str:
    """
    Генерировать Description:
    {Primary Keyword} от производителя Ultimate. {Типы}. {Формы}. {Volumes}. Опт и розница.

    ОБЯЗАТЕЛЬНО:
    - "от производителя Ultimate"
    - "Опт и розница"
    - Primary keyword
    - 120-160 chars

    ЗАПРЕЩЕНО:
    - Названия товаров
    - Marketing fluff
    """
    pk = primary_keyword[0].upper() + primary_keyword[1:]

    product_info = extract_product_info(slug)

    parts = [f"{pk} от производителя Ultimate."]

    if product_info["types"]:
        parts.append(" ".join(product_info["types"]) + ".")

    if product_info["forms"]:
        parts.append(" ".join(product_info["forms"]).capitalize() + ".")

    if product_info["volumes"]:
        parts.append(" ".join(product_info["volumes"]) + ".")

    parts.append("Опт и розница.")

    description = " ".join(parts)

    # Проверка длины
    if len(description) < 120:
        print(f"⚠️  WARNING: Description короткий ({len(description)} chars): {description[:50]}...")
    elif len(description) > 160:
        # Обрезаем до 160 chars, сохраняя "Опт и розница."
        description = description[:145] + "... Опт и розница."

    return description


def regenerate_meta(meta_file: Path) -> bool:
    """
    Перегенерировать мета для одной категории

    Returns:
        True если успешно, False если ошибка
    """
    try:
        # Извлечь slug из пути
        slug = meta_file.parent.parent.name

        # Пути к файлам
        clean_file = meta_file.parent.parent / "data" / f"{slug}_clean.json"

        if not clean_file.exists():
            print(f"❌ {slug}: _clean.json не найден")
            return False

        # Загрузить данные
        meta_data = load_json(meta_file)
        clean_data = load_json(clean_file)

        # ЖЕЛЕЗНОЕ ПРАВИЛО: keywords[0] ДОСЛОВНО!
        if not clean_data.get("keywords") or len(clean_data["keywords"]) == 0:
            print(f"❌ {slug}: нет keywords в _clean.json")
            return False

        primary_keyword = clean_data["keywords"][0]["keyword"]

        # Генерировать мета по формулам
        new_title = generate_title(primary_keyword)
        new_h1 = generate_h1(primary_keyword)
        new_description = generate_description(primary_keyword, slug)

        # Обновить мета
        meta_data["meta"]["title"] = new_title
        meta_data["meta"]["description"] = new_description
        meta_data["h1"] = new_h1

        # Обновить primary keywords (используем top 3)
        if "keywords_in_content" not in meta_data:
            meta_data["keywords_in_content"] = {}

        meta_data["keywords_in_content"]["primary"] = [
            kw["keyword"] for kw in clean_data["keywords"][:3]
        ]

        # Сохранить
        save_json(meta_file, meta_data)

        print(f"✅ {slug}")
        print(f"   Title: {new_title}")
        print(f"   H1: {new_h1}")
        print(f"   Desc: {new_description[:60]}...")

        return True

    except Exception as e:
        print(f"❌ {meta_file}: {e}")
        return False


def main():
    """Главная функция"""
    print("🚀 Перегенерация всех RU мета по правилам generate-meta v12.0\n")

    categories_dir = Path("categories")

    # Найти все RU мета-файлы
    ru_metas = []
    for meta_file in categories_dir.glob("*/meta/*_meta.json"):
        try:
            data = load_json(meta_file)
            if data.get("language") == "ru":
                ru_metas.append(meta_file)
        except Exception:
            pass

    print(f"Найдено {len(ru_metas)} RU категорий\n")

    # Перегенерировать все
    success = 0
    failed = 0

    for meta_file in sorted(ru_metas):
        if regenerate_meta(meta_file):
            success += 1
        else:
            failed += 1
        print()

    print("\n📊 Результаты:")
    print(f"   ✅ Успешно: {success}")
    print(f"   ❌ Ошибки: {failed}")
    print("\n✨ Готово! Следующий шаг: запустите validate_meta.py")


if __name__ == "__main__":
    main()
