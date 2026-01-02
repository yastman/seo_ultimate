#!/usr/bin/env python3
"""
cleanup_misplaced.py — Чистит неправильно распределённые ключи

Находит ключи которые попали не в ту категорию и перемещает их.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

CATEGORIES_DIR = Path(__file__).parent.parent / "categories"

# Правила что куда должно идти (строгие)
STRICT_RULES = [
    # Торнадор - только в apparaty-tornador
    (r'торнадор|tornador|торнадо', 'apparaty-tornador'),

    # Оборудование - в oborudovanie
    (r'оборудовани', 'oborudovanie'),

    # --- КОЖА (L2: sredstva-dlya-kozhi / L3: ukhod-za-kozhey, chistka-kozhi) ---
    # Кремы, полироли, уход -> в ukhod-za-kozhey
    (r'крем.*кож|полирол.*кож|лосьон.*кож|уход.*за.*кож', 'ukhod-za-kozhey'),
    # Чистка, очистители -> в chistka-kozhi
    (r'чист.*кож|очистител.*кож|химия.*кож.*салон', 'chistka-kozhi'),

    # --- ПОЛИРОВКА (L2: polirovalnye-pasty -> пасты) ---
    # Пасты должны быть ТОЛЬКО в пастах, если они случайно попали в круги или машинки
    (r'паст.*полиров|полиров.*паст', 'polirovalnye-pasty'),

    # --- СТЕКЛА (L2: sredstva-dlya-stekol / L3: ochistiteli-stekol) ---
    # Очистители стекол -> в ochistiteli-stekol (а не в L2)
    (r'очистител.*стекл|мыт.*стекл|чист.*стекл', 'ochistiteli-stekol'),

    # --- ДИСКИ (L2: sredstva-dlya-diskov-i-shin / L3: ochistiteli-diskov) ---
    # Очистители/химия для дисков -> в ochistiteli-diskov
    (r'очистител.*диск|химия.*диск|чист.*диск|мойк.*диск', 'ochistiteli-diskov'),

    # Полировка салона/торпеды/панели = пластик
    (r'полир.*(салон|торпед|панел)', 'poliroli-dlya-plastika'),

    # Кузов очистители
    (r'очистител.*кузов|кузов.*очистител|кузов.*очист', 'ochistiteli-kuzova'),

    # --- МИКРОФИБРА (L2: mikrofibra-i-tryapki) ---
    # Стекла
    (r'микрофибр.*стекл|тряпк.*стекл|салфетк.*стекл', 'mikrofibra-dlya-stekol'),
    # Полировка
    (r'микрофибр.*полиров|тряпк.*полиров|фибр.*полиров', 'mikrofibra-dlya-polirovki'),

    # --- ШАМПУНИ (L2: avtoshampuni) ---
    # Активная пена и бесконтакт должен быть в aktivnaya-pena
    (r'активн.*пен|бесконтакт', 'aktivnaya-pena'),
    # Для ручной мойки (если указано явно)
    (r'ручн.*мойк', 'dlya-ruchnoy-moyki'),

    # --- ВОСКИ (L2: voski) ---
    # Твердый
    (r'тверд.*воск', 'tverdyy-vosk'),
    # Жидкий / Горячий
    (r'жидк.*воск|горяч.*воск|быстр.*воск', 'zhidkiy-vosk'),

]


def check_keyword_placement(keyword: str, current_slug: str) -> Tuple[bool, str]:
    """
    Проверяет правильно ли размещён ключ.

    Returns:
        (is_correct, correct_slug or None)
    """
    keyword_lower = keyword.lower()

    for pattern, correct_slug in STRICT_RULES:
        if re.search(pattern, keyword_lower):
            if current_slug != correct_slug:
                return False, correct_slug

    return True, None


def analyze_category(slug: str) -> Dict:
    """Анализирует категорию на неправильные ключи."""
    clean_path = CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"

    if not clean_path.exists():
        return {'slug': slug, 'misplaced': []}

    with open(clean_path, encoding='utf-8') as f:
        data = json.load(f)

    misplaced = []
    kw_data = data.get('keywords', {})

    for category in ['primary', 'secondary', 'supporting', 'commercial']:
        for kw in kw_data.get(category, []):
            is_correct, correct_slug = check_keyword_placement(kw['keyword'], slug)
            if not is_correct:
                misplaced.append({
                    'keyword': kw['keyword'],
                    'volume': kw['volume'],
                    'from_category': category,
                    'should_be': correct_slug
                })

    return {'slug': slug, 'misplaced': misplaced}


def remove_keywords_from_category(slug: str, keywords_to_remove: List[str]) -> int:
    """Удаляет ключи из категории."""
    clean_path = CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"

    with open(clean_path, encoding='utf-8') as f:
        data = json.load(f)

    removed = 0
    keywords_set = set(kw.lower() for kw in keywords_to_remove)
    kw_data = data.get('keywords', {})

    for category in ['primary', 'secondary', 'supporting', 'commercial']:
        if category not in kw_data:
            continue
        original_len = len(kw_data[category])
        kw_data[category] = [
            kw for kw in kw_data[category]
            if kw['keyword'].lower() not in keywords_set
        ]
        removed += original_len - len(kw_data[category])

    # Update stats
    total_kws = sum(len(kw_data.get(cat, [])) for cat in ['primary', 'secondary', 'supporting', 'commercial'])
    total_vol = sum(kw['volume'] for cat in ['primary', 'secondary', 'supporting', 'commercial'] for kw in kw_data.get(cat, []))

    if 'stats' in data:
        data['stats']['after'] = total_kws
        data['stats']['total_volume'] = total_vol

    with open(clean_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return removed


def main():
    print("🔍 Анализ неправильно размещённых ключей...\n")

    all_misplaced = defaultdict(list)

    for cat_dir in sorted(CATEGORIES_DIR.iterdir()):
        if not cat_dir.is_dir():
            continue

        result = analyze_category(cat_dir.name)
        if result['misplaced']:
            print(f"❌ {result['slug']}: {len(result['misplaced'])} неправильных ключей")
            for m in result['misplaced']:
                print(f"   {m['keyword']} → {m['should_be']}")
                all_misplaced[result['slug']].append(m)

    if not all_misplaced:
        print("✅ Все ключи размещены правильно!")
        return

    print(f"\n{'='*60}")
    print(f"Всего категорий с ошибками: {len(all_misplaced)}")
    print(f"Всего неправильных ключей: {sum(len(v) for v in all_misplaced.values())}")

    # Fix mode
    import sys
    if '--fix' in sys.argv:
        print("\n🔧 Исправление...")
        for slug, misplaced in all_misplaced.items():
            keywords = [m['keyword'] for m in misplaced]
            removed = remove_keywords_from_category(slug, keywords)
            print(f"   ✅ {slug}: удалено {removed} ключей")

        print("\n✅ Готово! Запустите find_orphan_keywords.py --distribute --apply чтобы добавить ключи в правильные категории")
    else:
        print("\n💡 Запустите с --fix для исправления")


if __name__ == "__main__":
    main()
