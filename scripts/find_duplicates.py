#!/usr/bin/env python3
"""
Поиск дублей ключевых слов между категориями.
Находит:
1. Точные дубликаты между разными категориями
2. L2/L3 конфликты (родитель содержит ключи детей)
3. Ключи в неправильных категориях (по паттернам)

Использование:
    python scripts/find_duplicates.py
    python scripts/find_duplicates.py --verbose
    python scripts/find_duplicates.py --category aktivnaya-pena
"""

import json
import os
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set
import argparse

# Корневая директория проекта
ROOT_DIR = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT_DIR / "categories"

# Паттерны для определения неправильных категорий
# Формат: target_category -> [(pattern, exclude_from_categories), ...]
# Если exclude_from_categories пустой — применяется ко всем
INTENT_PATTERNS = {
    # Только явно неправильные перемещения
    "glina-i-avtoskraby": [
        ("глина для чистки машины", []),  # конкретный ключ
    ],
    "ochistiteli-stekol": [
        ("средство для очистки стекол", ["sredstva-dlya-stekol"]),
        ("средство для чистки стекол", ["sredstva-dlya-stekol"]),
    ],
    "dlya-khimchistki-salona": [
        ("средства для чистки салона машины", ["ochistiteli-shin"]),
        ("средство для химчистки салона машины", ["ochistiteli-shin"]),
        ("химия для чистки салона машины", ["ochistiteli-shin"]),
    ],
    "zashchitnoe-pokrytie-dlya-koles": [
        ("защитное покрытие для дисков", ["ochistiteli-shin"]),
        ("защитное покрытие для литых дисков", ["ochistiteli-shin"]),
    ],
    "kislotnyy-shampun": [
        ("кислотный шампунь для авто", ["dlya-ruchnoy-moyki"]),
        ("кислотный автошампунь", ["dlya-ruchnoy-moyki"]),
    ],
    "raspyliteli-i-penniki": [
        ("пенник для минимойки", ["aktivnaya-pena"]),
        ("распылитель пены", ["aktivnaya-pena"]),
    ],
    "ochistiteli-dvigatelya": [
        ("автохимия для двигателя", ["aktivnaya-pena"]),
    ],
    "omyvatel": [
        ("омыватель стекла антимошка", ["antimoshka"]),
        ("омывайка антимошка", ["antimoshka"]),
    ],
    "polirovalnye-krugi": [
        ("диск для полировки авто", ["polirovalnye-pasty"]),
        ("диск для полировки автомобиля", ["polirovalnye-pasty"]),
    ],
    "cherniteli-shin": [
        ("полироль для резины автомобиля", ["polirovalnye-pasty"]),
    ],
    "glavnaya": [
        ("автохимия украина", ["aktivnaya-pena"]),
        ("автохимия интернет магазин", ["aktivnaya-pena"]),
        ("автохимия каталог", ["aktivnaya-pena"]),
        ("автохимия интернет магазин украина", ["aktivnaya-pena"]),
        ("автохимия киев интернет магазин", ["aktivnaya-pena"]),
        ("химия для автомоек киев", ["aktivnaya-pena"]),
        ("профессиональная химия для автомоек", ["aktivnaya-pena"]),
        ("автомобильная косметика", ["aktivnaya-pena"]),
        ("химия автомобильная", ["aktivnaya-pena"]),
        ("продажа автохимии", ["aktivnaya-pena"]),
        ("автохимия и косметика", ["aktivnaya-pena"]),
        ("автохимия для автомобиля", ["aktivnaya-pena"]),
        ("автохимия для автомобиля интернет магазин", ["aktivnaya-pena"]),
        ("химия для автомойки украина", ["aktivnaya-pena"]),
    ],
}

# Иерархия категорий (L2 -> L3)
HIERARCHY = {
    "avtoshampuni": ["dlya-ruchnoy-moyki", "kislotnyy-shampun", "s-voskom"],
    "voski": ["tverdyy-vosk", "zhidkiy-vosk"],
    "sredstva-dlya-kozhi": ["ukhod-za-kozhey", "chistka-kozhi"],
    "sredstva-dlya-stekol": ["ochistiteli-stekol", "antidozhd", "omyvatel", "polirol-dlya-stekla"],
    "sredstva-dlya-diskov-i-shin": ["ochistiteli-diskov", "ochistiteli-shin", "cherniteli-shin", "zashchitnoe-pokrytie-dlya-koles"],
    "polirovalnye-krugi": ["mekhovye", "porolonovye"],
    "mikrofibra-i-tryapki": ["mikrofibra-dlya-polirovki", "mikrofibra-dlya-stekol"],
    "nabory": ["nabory-dlya-polirovki", "nabory-dlya-moyki", "nabory-dlya-khimchistki", "nabory-dlya-kozhi", "nabory-dlya-deteylinga", "podarochnye-nabory"],
}


def load_category_keywords(slug: str) -> Dict:
    """Загрузить ключи категории из _clean.json"""
    json_path = CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"
    if not json_path.exists():
        return {}

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"  ⚠️ Ошибка JSON в {slug}: {e}")
        return {}


def extract_all_keywords(data: Dict) -> List[Tuple[str, int, str]]:
    """Извлечь все ключи из категории: [(keyword, volume, type), ...]"""
    keywords = []
    kw_data = data.get("keywords", {})

    for kw_type in ["primary", "secondary", "supporting", "commercial"]:
        for item in kw_data.get(kw_type, []):
            kw = item.get("keyword", "")
            vol = item.get("volume", 0)
            if kw:
                keywords.append((kw.lower().strip(), vol, kw_type))

    return keywords


def get_all_categories() -> List[str]:
    """Получить список всех категорий"""
    categories = []
    for item in CATEGORIES_DIR.iterdir():
        if item.is_dir() and (item / "data").exists():
            categories.append(item.name)
    return sorted(categories)


def find_exact_duplicates(categories: List[str], verbose: bool = False) -> Dict[str, List[Tuple[str, str, int]]]:
    """
    Найти точные дубликаты ключей между категориями.
    Возвращает: {keyword: [(category, type, volume), ...]}
    """
    # Собираем все ключи со всех категорий
    keyword_locations = defaultdict(list)

    for slug in categories:
        data = load_category_keywords(slug)
        if not data:
            continue

        keywords = extract_all_keywords(data)
        for kw, vol, kw_type in keywords:
            keyword_locations[kw].append((slug, kw_type, vol))

    # Фильтруем — оставляем только дубликаты (присутствуют в 2+ категориях)
    duplicates = {
        kw: locs for kw, locs in keyword_locations.items()
        if len(locs) > 1
    }

    return duplicates


def find_hierarchy_conflicts(verbose: bool = False) -> List[Dict]:
    """
    Найти конфликты L2/L3 — когда родитель содержит ключи детей.
    """
    conflicts = []

    for parent_slug, children in HIERARCHY.items():
        parent_data = load_category_keywords(parent_slug)
        if not parent_data:
            continue

        parent_keywords = set(kw for kw, _, _ in extract_all_keywords(parent_data))

        for child_slug in children:
            child_data = load_category_keywords(child_slug)
            if not child_data:
                continue

            child_keywords = extract_all_keywords(child_data)

            for kw, vol, kw_type in child_keywords:
                if kw in parent_keywords:
                    conflicts.append({
                        "keyword": kw,
                        "volume": vol,
                        "parent": parent_slug,
                        "child": child_slug,
                        "type": kw_type
                    })

    return conflicts


def find_misplaced_by_intent(categories: List[str], verbose: bool = False) -> List[Dict]:
    """
    Найти ключи, которые по интенту не подходят категории.
    Новая логика: паттерны задают точные соответствия и категории-источники.
    """
    misplaced = []

    for slug in categories:
        data = load_category_keywords(slug)
        if not data:
            continue

        keywords = extract_all_keywords(data)

        for kw, vol, kw_type in keywords:
            kw_lower = kw.lower().strip()

            # Проверяем каждый паттерн
            for target_category, patterns in INTENT_PATTERNS.items():
                if target_category == slug:
                    continue  # Пропускаем целевую категорию

                for pattern_tuple in patterns:
                    pattern, source_categories = pattern_tuple

                    # Проверяем: если source_categories указаны,
                    # то ключ должен быть именно из этих категорий
                    if source_categories and slug not in source_categories:
                        continue

                    # Проверяем точное или частичное совпадение
                    if pattern.lower() in kw_lower:
                        misplaced.append({
                            "keyword": kw,
                            "volume": vol,
                            "current_category": slug,
                            "suggested_category": target_category,
                            "pattern": pattern,
                            "type": kw_type
                        })
                        break  # Нашли — выходим из цикла паттернов
                else:
                    continue
                break  # Нашли — выходим из цикла целевых категорий

    return misplaced


def print_report(duplicates: Dict, hierarchy_conflicts: List, misplaced: List, verbose: bool = False):
    """Вывести отчёт в консоль"""

    print("\n" + "="*80)
    print("📋 ОТЧЁТ ПО ДУБЛЯМ И КОНФЛИКТАМ КЛЮЧЕВЫХ СЛОВ")
    print("="*80)

    # 1. Точные дубликаты
    print(f"\n\n🔴 ТОЧНЫЕ ДУБЛИКАТЫ ({len(duplicates)} ключей)")
    print("-"*60)

    if duplicates:
        # Сортируем по суммарному volume
        sorted_dups = sorted(
            duplicates.items(),
            key=lambda x: max(loc[2] for loc in x[1]),
            reverse=True
        )

        for kw, locations in sorted_dups[:50]:  # Топ-50
            max_vol = max(loc[2] for loc in locations)
            cats = ", ".join(f"{loc[0]}({loc[1]})" for loc in locations)
            print(f"  [{max_vol:4d}] {kw}")
            print(f"         → {cats}")
    else:
        print("  ✅ Дубликатов не найдено")

    # 2. L2/L3 конфликты
    print(f"\n\n🟡 КОНФЛИКТЫ L2/L3 ({len(hierarchy_conflicts)} ключей)")
    print("-"*60)

    if hierarchy_conflicts:
        # Группируем по родителю
        by_parent = defaultdict(list)
        for c in hierarchy_conflicts:
            by_parent[c["parent"]].append(c)

        for parent, conflicts in sorted(by_parent.items()):
            print(f"\n  📁 {parent}:")
            for c in sorted(conflicts, key=lambda x: -x["volume"])[:10]:
                print(f"     [{c['volume']:4d}] {c['keyword']}")
                print(f"            ↳ дубль с {c['child']}")
    else:
        print("  ✅ Конфликтов не найдено")

    # 3. Неправильные категории по интенту
    print(f"\n\n🟠 КЛЮЧИ В НЕПРАВИЛЬНЫХ КАТЕГОРИЯХ ({len(misplaced)} ключей)")
    print("-"*60)

    if misplaced:
        # Группируем по текущей категории
        by_current = defaultdict(list)
        for m in misplaced:
            by_current[m["current_category"]].append(m)

        for current, items in sorted(by_current.items()):
            print(f"\n  📁 {current}:")
            for m in sorted(items, key=lambda x: -x["volume"])[:10]:
                print(f"     [{m['volume']:4d}] {m['keyword']}")
                print(f"            → перенести в {m['suggested_category']}")
    else:
        print("  ✅ Всё на своих местах")

    # Итоги
    print("\n\n" + "="*80)
    print("📊 ИТОГО:")
    print(f"   • Точных дубликатов: {len(duplicates)}")
    print(f"   • L2/L3 конфликтов: {len(hierarchy_conflicts)}")
    print(f"   • Неправильных по интенту: {len(misplaced)}")
    print("="*80 + "\n")


def export_to_json(duplicates: Dict, hierarchy_conflicts: List, misplaced: List):
    """Экспорт результатов в JSON"""
    output = {
        "duplicates": [
            {"keyword": kw, "locations": [{"category": l[0], "type": l[1], "volume": l[2]} for l in locs]}
            for kw, locs in duplicates.items()
        ],
        "hierarchy_conflicts": hierarchy_conflicts,
        "misplaced": misplaced
    }

    output_path = ROOT_DIR / "reports" / "duplicates_report.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Отчёт сохранён: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Поиск дублей ключевых слов между категориями")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    parser.add_argument("--category", "-c", help="Проверить конкретную категорию")
    parser.add_argument("--export", "-e", action="store_true", help="Экспорт в JSON")
    args = parser.parse_args()

    print("🔍 Загрузка категорий...")
    categories = get_all_categories()

    if args.category:
        if args.category not in categories:
            print(f"❌ Категория '{args.category}' не найдена")
            sys.exit(1)
        categories = [args.category]

    print(f"   Найдено категорий: {len(categories)}")

    print("\n🔍 Поиск точных дубликатов...")
    duplicates = find_exact_duplicates(categories, args.verbose)

    print("🔍 Поиск L2/L3 конфликтов...")
    hierarchy_conflicts = find_hierarchy_conflicts(args.verbose)

    print("🔍 Поиск ключей в неправильных категориях...")
    misplaced = find_misplaced_by_intent(categories, args.verbose)

    print_report(duplicates, hierarchy_conflicts, misplaced, args.verbose)

    if args.export:
        export_to_json(duplicates, hierarchy_conflicts, misplaced)


if __name__ == "__main__":
    main()
