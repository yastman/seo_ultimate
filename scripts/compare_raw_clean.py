#!/usr/bin/env python3
"""
compare_raw_clean.py — Сравнение CSV семантики с _clean.json

Парсит весь CSV и сравнивает с существующими _clean.json файлами.
Показывает расхождения: добавленные/удалённые ключи, изменённые volumes.

Usage:
    python3 scripts/compare_raw_clean.py              # Показать все расхождения
    python3 scripts/compare_raw_clean.py --fix        # Автоматически исправить
    python3 scripts/compare_raw_clean.py aktivnaya-pena  # Проверить одну категорию
"""

import csv
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SEMANTICS_CSV = PROJECT_ROOT / "Структура _Ultimate.csv"
CATEGORIES_DIR = PROJECT_ROOT / "categories"

# Маппинг названий из CSV → slug категории
CSV_TO_SLUG = {
    # L3 категории
    "Активная пена": "aktivnaya-pena",
    "Для ручной мойки": "dlya-ruchnoy-moyki",
    "Очистители стекол": "ochistiteli-stekol",
    "Глина и автоскрабы": "glina-i-avtoskraby",
    "Антимошка": "antimoshka",
    "Антибитум": "antibitum",
    "Чернители шин": "cherniteli-shin",
    "Очистители дисков": "ochistiteli-diskov",
    "Очистители шин": "ochistiteli-shin",
    "Аппараты Tornador": "apparaty-tornador",
    "Меховые": "mekhovye",
    "Поролоновые": "porolonovye",
    "Наборы для мойки": "nabory-dlya-moyki",
    "Наборы для полировки": "nabory-dlya-polirovki",
    "Наборы для ухода за кожей": "nabory-dlya-kozhi",
    "Наборы для химчистки": "nabory-dlya-khimchistki",
    "Подарочные наборы": "podarochnye-nabory",

    # L2 категории (в CSV это L2: ...)
    "Автошампуни": "avtoshampuni",
    "Очистители двигателя": "ochistiteli-dvigatelya",
    "Обезжириватели": "obezzhirivateli",
    "Малярний Скотч": "malyarnyy-skotch",
    "Микрофибра и тряпки": "mikrofibra-i-tryapki",
    "Щетки и кисти": "shchetki-i-kisti",
    "Губки и варежки": "gubki-i-varezhki",
    "Распылители и пенники": "raspyliteli-i-penniki",
    "Аксессуары для нанесения средств": "aksessuary-dlya-naneseniya",
    "Ведра и емкости": "vedra-i-emkosti",
    "Полировальные машинки": "polirovalnye-mashinki",
    "Полировальные пасты": "polirovalnye-pasty",
    "Полировальные круги": "polirovalnye-krugi",
    "Нейтрализаторы запаха": "neytralizatory-zapakha",
    "Полироли для пластика": "poliroli-dlya-plastika",
    "Средства для кожи": "sredstva-dlya-kozhi",
    "Воски": "voski",
    "Керамика и жидкое стекло": "keramika-i-zhidkoe-steklo",
    "Квик-детейлеры": "kvik-deteylery",
    "Наборы для детейлинга": "nabory-dlya-deteylinga",
    "Средства для стекол": "sredstva-dlya-stekol",
    "Очистители кузова": "ochistiteli-kuzova",
    "Средства для дисков и шин": "sredstva-dlya-diskov-i-shin",
    "Оборудование": "oborudovanie",

    # L1 категории (хабы) - в CSV это L1: ...
    "Мойка и Экстерьер": "moyka-i-eksteryer",
    "Аксессуары": "aksessuary",
    "Полировка": "polirovka",
    "Уход за интерьером": "ukhod-za-interyerom",
    "Защитные покрытия": "zashchitnye-pokrytiya",

    # SEO-фильтры (в CSV это SEO-Фильтр: ...)
    "С воском": "s-voskom",
    "Кислотный": "kislotnyy-shampun",
    "Аккумуляторная": "akkumulyatornye-mashinki",
    "Твердый": "tverdyy-vosk",
    "Жидкий (быстрый)": "zhidkiy-vosk",
    "Для полировки": "mikrofibra-dlya-polirovki",
    "для стекол": "mikrofibra-dlya-stekol",

    # Специальные блоки (без префикса L или SEO-)
    "Омыватель": "omyvatel",
    "Антидождь": "antidozhd",
    "Для химчистки салона": "dlya-khimchistki-salona",
    "Пятновыводители": "pyatnovyvoditeli",
    "Уход за кожей": "ukhod-za-kozhey",
    "Чистка кожи": "chistka-kozhi",
    "Полироль для стекла": "polirol-dlya-stekla",
    "Силанты": "silanty",
    "Защитные покрытие для колес": "zashchitnoe-pokrytie-dlya-koles",
    "Для внешнего пластика и резины": "dlya-vneshnego-plastika",
    "Главная": "glavnaya",
    "Наборы": "nabory",
    "Опт": "opt",

    # Подблоки внутри L2 (объединены в категории)
    "тряпка для авто": "mikrofibra-i-tryapki",
    "тряпка микрофибра для авто": "mikrofibra-i-tryapki",
    "тряпка для авто без разводов": "mikrofibra-i-tryapki",
    "полотенце микрофибра для авто": "mikrofibra-i-tryapki",
    "микрофибра для мойки авто": "mikrofibra-i-tryapki",
    "супер впитывающая тряпка для авто": "mikrofibra-i-tryapki",
    "тряпка для стекла автомобиля": "mikrofibra-i-tryapki",
    "тряпка для вытирания авто после мойки": "mikrofibra-i-tryapki",
    "тряпки для полировки авто": "mikrofibra-dlya-polirovki",

    "щетка для мойки авто": "shchetki-i-kisti",
    "щетка для автомобиля": "shchetki-i-kisti",
    "щетка для мытья машины": "shchetki-i-kisti",
    "купить щетки для детейлинга": "shchetki-i-kisti",
    "щетки для химчистки авто": "shchetki-i-kisti",
    "щетка для салона авто": "shchetki-i-kisti",
    "щетка для дисков авто": "shchetki-i-kisti",
    "кисточки для мойки авто": "shchetki-i-kisti",
    "кисти для мойки авто": "shchetki-i-kisti",

    "набор для химчистки автомобиля": "nabory-dlya-khimchistki",
    "набор химии для автомобиля": "nabory",
    "подарочный набор для авто": "podarochnye-nabory",
    "набор для уборки автомобиля": "nabory",
    "наборы для авто": "nabory",
    "наборы для детейлинга": "nabory-dlya-deteylinga",
    "подарочные наборы для мужчин в машину": "podarochnye-nabory",
    "набор для мойки авто": "nabory-dlya-moyki",
    "набор для чистки салона авто": "nabory-dlya-khimchistki",
    "набор для ухода за машиной": "nabory",
    "набор кругов для полировки авто": "nabory-dlya-polirovki",
    "набор кистей для детейлинга": "nabory-dlya-deteylinga",
    "набор тряпок для машины": "nabory-dlya-moyki",

    "купить оборудование для мойки автомобилей": "oborudovanie",
    "производители автохимии украина": "opt",
}

# Create SLUG_TO_CSV prioritizing L1/L2/L3 blocks over sub-blocks
PRIORITY_MAPPINGS = {
    "mikrofibra-i-tryapki": "Микрофибра и тряпки",
    "shchetki-i-kisti": "Щетки и кисти",
    "nabory-dlya-moyki": "набор для мойки авто",
    "nabory-dlya-polirovki": "набор кругов для полировки авто",
    "nabory-dlya-khimchistki": "набор для химчистки автомобиля",
    "nabory-dlya-deteylinga": "наборы для детейлинга",
    "podarochnye-nabory": "подарочные наборы для мужчин в машину",
}

SLUG_TO_CSV = {v: k for k, v in CSV_TO_SLUG.items()}
# Override with priority mappings
SLUG_TO_CSV.update(PRIORITY_MAPPINGS)


def parse_csv_keywords() -> Dict[str, List[Dict]]:
    """
    Парсит CSV и возвращает все ключевые слова по блокам.

    Returns:
        {
            "Активная пена": [{"keyword": "...", "volume": 1300}, ...],
            ...
        }
    """
    blocks: Dict[str, List[Dict]] = {}
    current_block: Optional[str] = None

    with open(SEMANTICS_CSV, encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue

            phrase = row[0].strip()
            count_str = row[1].strip() if len(row) > 1 else ''
            volume_str = row[2].strip() if len(row) > 2 else ''

            # Detect block headers
            if phrase.startswith('L1:'):
                block_name = phrase.replace('L1:', '').strip()
                current_block = block_name
                if current_block not in blocks:
                    blocks[current_block] = []
                continue

            if phrase.startswith('L2:'):
                block_name = phrase.replace('L2:', '').strip()
                current_block = block_name
                if current_block not in blocks:
                    blocks[current_block] = []
                continue

            if phrase.startswith('L3:'):
                block_name = phrase.replace('L3:', '').strip()
                current_block = block_name
                if current_block not in blocks:
                    blocks[current_block] = []
                continue

            if phrase.startswith('SEO-Фильтр:'):
                block_name = phrase.replace('SEO-Фильтр:', '').strip()
                current_block = block_name
                if current_block not in blocks:
                    blocks[current_block] = []
                continue

            # Special blocks (name with count, no volume)
            if count_str and count_str.replace('/', '').isdigit() and not volume_str:
                # This is a block header like "Омыватель,35," or "категория,16,"
                if phrase.lower() != 'категория':
                    current_block = phrase
                    if current_block not in blocks:
                        blocks[current_block] = []
                continue

            # Skip if no current block
            if not current_block:
                continue

            # Parse keyword with volume
            if volume_str.isdigit():
                volume = int(volume_str)
                blocks[current_block].append({
                    'keyword': phrase,
                    'volume': volume
                })

    return blocks


def read_clean_json(slug: str) -> Optional[Dict]:
    """Читает _clean.json для категории."""
    path = CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"
    if not path.exists():
        return None

    with open(path, encoding='utf-8') as f:
        return json.load(f)


def get_clean_keywords(clean_data: Dict) -> List[Dict]:
    """Извлекает все ключи из _clean.json в плоский список."""
    keywords = []
    kw_data = clean_data.get('keywords', {})

    for category in ['primary', 'secondary', 'supporting', 'commercial']:
        for kw in kw_data.get(category, []):
            keywords.append({
                'keyword': kw['keyword'],
                'volume': kw['volume']
            })

    return keywords


def compare_keywords(csv_kws: List[Dict], clean_kws: List[Dict]) -> Dict:
    """
    Сравнивает ключи из CSV с _clean.json.

    Returns:
        {
            'added': [...],      # в clean, но нет в csv
            'removed': [...],    # в csv, но нет в clean
            'volume_changed': [...],  # разные volumes
            'match': True/False
        }
    """
    csv_dict = {kw['keyword']: kw['volume'] for kw in csv_kws}
    clean_dict = {kw['keyword']: kw['volume'] for kw in clean_kws}

    added = []
    removed = []
    volume_changed = []

    # Keywords in clean but not in csv
    for kw, vol in clean_dict.items():
        if kw not in csv_dict:
            added.append({'keyword': kw, 'volume': vol})
        elif csv_dict[kw] != vol:
            volume_changed.append({
                'keyword': kw,
                'csv_volume': csv_dict[kw],
                'clean_volume': vol
            })

    # Keywords in csv but not in clean
    for kw, vol in csv_dict.items():
        if kw not in clean_dict:
            removed.append({'keyword': kw, 'volume': vol})

    return {
        'added': added,
        'removed': removed,
        'volume_changed': volume_changed,
        'match': not (added or removed or volume_changed)
    }


def fix_clean_json(slug: str, clean_data: Dict, csv_kws: List[Dict], result: Dict) -> Tuple[bool, str]:
    """
    Исправляет _clean.json:
    - Удаляет ключи, которых нет в CSV (added)
    - Исправляет volumes на значения из CSV (volume_changed)

    Returns:
        (success, message)
    """
    # Build CSV lookup
    csv_dict = {kw['keyword']: kw['volume'] for kw in csv_kws}

    # Keywords to remove (added = not in CSV)
    added_kws = {kw['keyword'] for kw in result['added']}

    # Keywords with wrong volumes
    volume_fixes = {kw['keyword']: kw['csv_volume'] for kw in result['volume_changed']}

    changes = []
    kw_data = clean_data.get('keywords', {})

    for category in ['primary', 'secondary', 'supporting', 'commercial']:
        if category not in kw_data:
            continue

        original_count = len(kw_data[category])

        # Filter out added keywords and fix volumes
        new_list = []
        for kw in kw_data[category]:
            keyword = kw['keyword']

            # Skip keywords not in CSV
            if keyword in added_kws:
                changes.append(f"Removed '{keyword}' from {category}")
                continue

            # Fix volume if needed
            if keyword in volume_fixes:
                old_vol = kw['volume']
                new_vol = volume_fixes[keyword]
                kw['volume'] = new_vol
                changes.append(f"Fixed volume '{keyword}': {old_vol} → {new_vol}")

            new_list.append(kw)

        kw_data[category] = new_list

    # Update stats
    total_kws = sum(len(kw_data.get(cat, [])) for cat in ['primary', 'secondary', 'supporting', 'commercial'])
    total_vol = sum(kw['volume'] for cat in ['primary', 'secondary', 'supporting', 'commercial'] for kw in kw_data.get(cat, []))

    if 'stats' in clean_data:
        clean_data['stats']['after'] = total_kws
        clean_data['stats']['total_volume'] = total_vol

    if not changes:
        return False, "No changes needed"

    # Write back
    path = CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)

    return True, f"{len(changes)} changes: " + "; ".join(changes[:3]) + ("..." if len(changes) > 3 else "")


def main():
    fix_mode = '--fix' in sys.argv
    target_slug = None

    for arg in sys.argv[1:]:
        if not arg.startswith('--'):
            target_slug = arg
            break

    print(f"📖 Reading CSV: {SEMANTICS_CSV}")
    csv_blocks = parse_csv_keywords()
    print(f"✅ Found {len(csv_blocks)} blocks in CSV\n")

    # Get all category slugs
    if target_slug:
        slugs = [target_slug]
    else:
        slugs = sorted([d.name for d in CATEGORIES_DIR.iterdir() if d.is_dir()])

    issues = []
    no_csv_data = []

    for slug in slugs:
        # Find corresponding CSV block
        csv_name = SLUG_TO_CSV.get(slug)
        csv_kws = csv_blocks.get(csv_name, []) if csv_name else []

        # Read clean.json
        clean_data = read_clean_json(slug)
        if not clean_data:
            print(f"⚠️  {slug}: No _clean.json found")
            continue

        clean_kws = get_clean_keywords(clean_data)

        if not csv_kws:
            print(f"❓ {slug}: No CSV data (csv_name={csv_name})")
            no_csv_data.append(slug)
            continue

        # Compare
        result = compare_keywords(csv_kws, clean_kws)

        if result['match']:
            print(f"✅ {slug}: OK ({len(clean_kws)} keywords)")
        else:
            # Only show issues for Added and Volume changed (not Removed - that's expected)
            has_real_issues = result['added'] or result['volume_changed']

            if has_real_issues:
                print(f"❌ {slug}: MISMATCH")
            else:
                print(f"✅ {slug}: OK ({len(clean_kws)} keywords, {len(result['removed'])} filtered)")
                continue

            if result['added']:
                print(f"   Added (not in CSV): {len(result['added'])}")
                for kw in result['added'][:3]:
                    print(f"      + {kw['keyword']} ({kw['volume']})")
                if len(result['added']) > 3:
                    print(f"      ... and {len(result['added']) - 3} more")

            if result['volume_changed']:
                print(f"   Volume changed: {len(result['volume_changed'])}")
                for kw in result['volume_changed'][:3]:
                    print(f"      ~ {kw['keyword']}: {kw['csv_volume']} → {kw['clean_volume']}")
                if len(result['volume_changed']) > 3:
                    print(f"      ... and {len(result['volume_changed']) - 3} more")

            issues.append({
                'slug': slug,
                'result': result,
                'csv_kws': csv_kws,
                'clean_data': clean_data
            })

    print(f"\n{'='*60}")
    ok_count = len(slugs) - len(issues) - len(no_csv_data)
    print(f"Summary: {ok_count} OK, {len(issues)} with issues, {len(no_csv_data)} no CSV data")

    if fix_mode and issues:
        print(f"\n🔧 Fixing {len(issues)} categories...")
        fixed = 0
        for issue in issues:
            slug = issue['slug']
            success, msg = fix_clean_json(
                slug,
                issue['clean_data'],
                issue['csv_kws'],
                issue['result']
            )
            if success:
                print(f"   ✅ {slug}: {msg}")
                fixed += 1
            else:
                print(f"   ⚠️  {slug}: {msg}")
        print(f"\n✅ Fixed {fixed} categories")
    elif issues and not fix_mode:
        print(f"\n💡 Run with --fix to auto-fix issues")


if __name__ == "__main__":
    main()
