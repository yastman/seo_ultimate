#!/usr/bin/env python3
"""
find_orphan_keywords.py — Находит ключи из CSV, которых нет в _clean.json

1. Парсит ВСЕ ключи из CSV (любая строка с volume)
2. Собирает все ключи из _clean.json файлов
3. Находит "сирот" и предлагает категории для них
"""

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SEMANTICS_CSV = PROJECT_ROOT / "Структура _Ultimate.csv"
CATEGORIES_DIR = PROJECT_ROOT / "categories"

# Правила распределения ключей по содержимому
KEYWORD_RULES = [
    # (паттерн, slug, приоритет)
    # Шампуни
    (r"шампун.*воск|воск.*шампун", "s-voskom", 10),
    (r"кислотн.*шампун", "kislotnyy-shampun", 10),
    (r"бесконтакт.*шампун|шампун.*бесконтакт", "aktivnaya-pena", 10),
    (r"автошампун|шампунь.*(авто|машин|мойк)", "avtoshampuni", 5),
    (r"шампунь", "avtoshampuni", 3),
    # Пена и мойка
    (r"активн.*пен|пен.*мойк|бесконтакт.*пен", "aktivnaya-pena", 10),
    (r"пен.*(авто|машин)|пенообразовател", "aktivnaya-pena", 8),
    (r"ручн.*мойк|мойк.*ручн", "dlya-ruchnoy-moyki", 10),
    # Насекомые и битум
    (r"антимошк|мошк", "antimoshka", 10),
    (r"антибитум|битум", "antibitum", 10),
    # Кузов
    (r"очистител.*кузов|кузов.*очистител|кузов.*очист", "ochistiteli-kuzova", 10),
    # Шины и диски
    (r"чернител.*шин|черн.*резин", "cherniteli-shin", 10),
    (r"средств.*шин|уход.*шин|обработк.*шин|натиран.*шин|для шин", "cherniteli-shin", 10),
    (r"очистител.*диск|химия.*диск|средств.*диск", "ochistiteli-diskov", 10),
    (r"очистител.*шин|чист.*(шин|резин)|средств.*резин", "ochistiteli-shin", 10),
    # Стекла
    (r"очистител.*стекл|средств.*стекл", "ochistiteli-stekol", 10),
    (r"омывател|незамерзайк|стеклоомывател", "omyvatel", 10),
    (r"антидожд", "antidozhd", 10),
    # Глина
    (r"глин.*(авто|кузов|полиров)|автоскраб|clay", "glina-i-avtoskraby", 10),
    # Торнадор (включая "торнадо")
    (r"торнадор|tornador|торнадо", "apparaty-tornador", 10),
    # Микрофибра и тряпки
    (r"микрофибр.*полиров|полиров.*микрофибр|тряпк.*полиров", "mikrofibra-dlya-polirovki", 10),
    (r"микрофибр.*стекл|стекл.*микрофибр", "mikrofibra-dlya-stekol", 10),
    (r"тряпк|микрофибр|салфетк.*авто|полотенц.*авто|фибра", "mikrofibra-i-tryapki", 5),
    # Щетки и кисти
    (r"щетк|кист|кисточ", "shchetki-i-kisti", 5),
    # Губки
    (r"губк|варежк|мочалк", "gubki-i-varezhki", 5),
    # Ведра
    (r"ведр|ёмкост|емкост", "vedra-i-emkosti", 5),
    # Распылители
    (r"распылител|пенник|пеногенератор|триггер|помпов", "raspyliteli-i-penniki", 5),
    # Полировка - машинки
    (r"полироваль.*машин|полировочн.*машин|машин.*полиров", "polirovalnye-mashinki", 10),
    (r"аккумулятор.*машин", "akkumulyatornye-mashinki", 10),
    # Полировка - пасты
    (r"полироваль.*паст|полировочн.*паст|паст.*полиров", "polirovalnye-pasty", 10),
    # Полировка - круги
    (r"полироваль.*круг|полировочн.*круг|круг.*полиров", "polirovalnye-krugi", 10),
    (r"диск.*полиров|полиров.*диск", "polirovalnye-krugi", 10),
    (r"мехов.*круг|шерстян.*круг", "mekhovye", 10),
    (r"поролонов.*круг", "porolonovye", 10),
    # Воски
    (r"воск.*тверд|тверд.*воск", "tverdyy-vosk", 10),
    (r"воск.*жидк|жидк.*воск|быстр.*воск|холодн.*воск|горяч.*воск", "zhidkiy-vosk", 10),
    (r"воск", "voski", 3),
    # Керамика
    (r"керамик|нанокерамик|жидк.*стекл", "keramika-i-zhidkoe-steklo", 10),
    (r"силант", "silanty", 10),
    # Квик-детейлеры
    (r"квик.*детейл|быстр.*детейл|полимер.*авто", "kvik-deteylery", 10),
    # Обезжириватели
    (r"обезжирив", "obezzhirivateli", 10),
    # Двигатель
    (
        r"очистител.*двигател|мойк.*мотор|химия.*мотор|двигател.*очист|мойк.*двигател|средств.*двигател",
        "ochistiteli-dvigatelya",
        10,
    ),
    (
        r"химия.*(двигател|мотор)|(двигател|мотор).*химия|средств.*мот|мыт.*мотор",
        "ochistiteli-dvigatelya",
        10,
    ),
    (r"чист.*двигател", "ochistiteli-dvigatelya", 10),
    # Запахи
    (r"нейтрализатор.*запах|поглотител.*запах|запах.*авто|освежител", "neytralizatory-zapakha", 10),
    (r"устранител.*запах|удален.*запах|запах.*(машин|салон)", "neytralizatory-zapakha", 10),
    # Пластик и полировка салона
    (
        r"полирол.*пластик|пластик.*полирол|полирол.*торпед|торпед.*полирол",
        "poliroli-dlya-plastika",
        10,
    ),
    (r"полир.*салон|салон.*полир", "poliroli-dlya-plastika", 10),
    (r"уход.*пластик|средств.*пластик", "poliroli-dlya-plastika", 10),
    (r"внешн.*пластик|наружн.*пластик", "dlya-vneshnego-plastika", 10),
    # Кожа
    # Кожа (детализация)
    (r"крем.*кож|полирол.*кож|лосьон.*кож|уход.*за.*кож", "ukhod-za-kozhey", 10),
    (r"чист.*кож|очистител.*кож|химия.*кож.*салон", "chistka-kozhi", 10),
    (r"средств.*кож|для кожи", "sredstva-dlya-kozhi", 5),
    # Стекла
    (r"очистител.*стекл|мыт.*стекл|чист.*стекл", "ochistiteli-stekol", 10),
    (r"средств.*стекл", "sredstva-dlya-stekol", 5),
    # Диски
    (r"очистител.*диск|химия.*диск|чист.*диск|мойк.*диск", "ochistiteli-diskov", 10),
    (r"средств.*диск", "sredstva-dlya-diskov-i-shin", 5),
    # Полировка (пасты отдельно)
    (r"паст.*полиров|полиров.*паст", "polirovalnye-pasty", 15),
    # Салон и химчистка
    (r"химчистк.*салон|чист.*салон|средств.*салон|химия.*салон", "dlya-khimchistki-salona", 5),
    (r"химия.*текстил|текстил.*химия|средств.*химчист", "dlya-khimchistki-salona", 10),
    (r"пятновывод", "pyatnovyvoditeli", 10),
    # Наборы
    (r"набор.*химчист|химчист.*набор", "nabory-dlya-khimchistki", 10),
    (r"набор.*мойк|мойк.*набор", "nabory-dlya-moyki", 10),
    (r"набор.*полиров|полиров.*набор|набор.*круг|набор.*паст", "nabory-dlya-polirovki", 10),
    (r"набор.*кож", "nabory-dlya-kozhi", 10),
    (r"подарочн.*набор|набор.*подарок|набор.*мужчин", "podarochnye-nabory", 10),
    (r"набор.*детейлинг|детейлинг.*набор|набор.*кист", "nabory-dlya-deteylinga", 10),
    (r"набор", "nabory", 3),
    # Скотч
    (r"малярн.*скотч|скотч.*малярн|малярск.*скотч", "malyarnyy-skotch", 10),
    (r"малярн.*лент|клейк.*лент", "malyarnyy-skotch", 10),
    # Полироль для стекла
    (r"полирол.*стекл|стекл.*полирол", "polirol-dlya-stekla", 10),
    # Оборудование (любое упоминание) - высокий приоритет
    (r"оборудовани", "oborudovanie", 15),
    (r"оптом|оптов|производител", "opt", 5),
    # Защитные покрытия
    (r"защит.*покрыт.*колес|покрыт.*диск", "zashchitnoe-pokrytie-dlya-koles", 10),
    # Дополнительные паттерны
    (r"керамическ.*покрыт", "keramika-i-zhidkoe-steklo", 10),
    (r"перчатк.*(мойк|мыт)", "gubki-i-varezhki", 10),
    (r"скребок.*авто|авто.*скребок", "shchetki-i-kisti", 10),
    (r"мыт.*двигател|двигател.*мыт|жидкость.*двигател", "ochistiteli-dvigatelya", 10),
    (r"глин.*(машин|авто|купит)", "glina-i-avtoskraby", 10),
    (r"химия.*кузов|кузов.*химия", "aktivnaya-pena", 5),
    (r"полирол.*машин", "polirovalnye-mashinki", 5),
    (r"нейтрализатор.*авто", "neytralizatory-zapakha", 10),
    (r"полирол.*панел|панел.*полирол", "poliroli-dlya-plastika", 10),
    (r"паста.*авто", "polirovalnye-pasty", 5),
    (r"химия.*сиден|сиден.*химия|чист.*сиден", "dlya-khimchistki-salona", 10),
    (r"химия.*очист.*двигател|очист.*двигател", "ochistiteli-dvigatelya", 10),
    (r"для кож.*авто|авто.*кож", "sredstva-dlya-kozhi", 5),
    (r"детейлинг|автодетейлинг", "nabory-dlya-deteylinga", 3),
    (r"магазин.*авто|автокосметик", "glavnaya", 3),
    (r"полир.*авто|авто.*полир", "polirovalnye-pasty", 2),
    (r"мойк.*авто|авто.*мойк|для мойки", "aktivnaya-pena", 2),
    (r"чист.*авто|авто.*чист", "dlya-khimchistki-salona", 2),
    (r"уход.*авто|авто.*уход", "sredstva-dlya-kozhi", 2),
    # Общие паттерны (низкий приоритет)
    (r"химия.*мойк|мойк.*химия|автохимия", "aktivnaya-pena", 2),
    (r"средств.*мойк.*авто", "aktivnaya-pena", 2),
    (r"химия.*(автомобил|авто)|автомобил.*химия", "aktivnaya-pena", 2),
    (r"косметик.*автомобил|автомобил.*косметик", "aktivnaya-pena", 2),
    (r"продаж.*автохим|автохим.*продаж|купить автохим", "aktivnaya-pena", 2),
    (r"профессион.*химия.*автом|химия.*автомо", "aktivnaya-pena", 2),
    (r"химия.*машин|мыт.*машин", "aktivnaya-pena", 2),
]


def parse_all_csv_keywords() -> list[dict]:
    """Парсит ВСЕ ключи из CSV (любая строка где есть volume)."""
    keywords = []

    with open(SEMANTICS_CSV, encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue

            phrase = row[0].strip()
            volume_str = row[2].strip() if len(row) > 2 else ""

            # Skip headers
            if phrase.startswith(("L1:", "L2:", "L3:", "SEO-Фильтр:")):
                continue

            # Skip block headers (have count in col2, no volume)
            count_str = row[1].strip() if len(row) > 1 else ""
            if count_str and ("/" in count_str or count_str.isdigit()) and not volume_str:
                continue

            # Parse keyword with volume
            if volume_str.isdigit():
                volume = int(volume_str)
                if volume > 0:  # Skip zero volume
                    keywords.append({"keyword": phrase, "volume": volume})

    return keywords


def get_all_clean_keywords() -> tuple[set[str], dict[str, str]]:
    """Собирает все ключи из всех _clean.json файлов.

    Returns:
        (set of all keywords, dict mapping keyword -> slug)
    """
    all_keywords = set()
    keyword_to_slug = {}

    for cat_dir in CATEGORIES_DIR.iterdir():
        if not cat_dir.is_dir():
            continue

        clean_file = cat_dir / "data" / f"{cat_dir.name}_clean.json"
        if not clean_file.exists():
            continue

        with open(clean_file, encoding="utf-8") as f:
            data = json.load(f)

        kw_data = data.get("keywords", {})
        for category in ["primary", "secondary", "supporting", "commercial"]:
            for kw in kw_data.get(category, []):
                keyword = kw["keyword"].lower()
                all_keywords.add(keyword)
                keyword_to_slug[keyword] = cat_dir.name

    return all_keywords, keyword_to_slug


def suggest_category(keyword: str) -> tuple[str, int]:
    """Предлагает категорию для ключа на основе правил.
    Выбирает совпадение с наивысшим приоритетом.

    Returns:
        (slug, confidence) или (None, 0)
    """
    keyword_lower = keyword.lower()
    best_slug = None
    best_priority = 0

    for pattern, slug, priority in KEYWORD_RULES:
        if re.search(pattern, keyword_lower) and priority > best_priority:
            best_slug = slug
            best_priority = priority

    return best_slug, best_priority


def main():
    print("📖 Парсинг всех ключей из CSV...")
    csv_keywords = parse_all_csv_keywords()
    print(f"   Найдено {len(csv_keywords)} ключей с volume > 0")

    print("\n📖 Сбор ключей из _clean.json файлов...")
    used_keywords, keyword_to_slug = get_all_clean_keywords()
    print(f"   Найдено {len(used_keywords)} уникальных ключей в _clean.json")

    # Find orphans
    orphans = []
    for kw in csv_keywords:
        if kw["keyword"].lower() not in used_keywords:
            orphans.append(kw)

    print(f"\n🔍 Найдено {len(orphans)} 'сирот' (есть в CSV, нет в _clean.json)")

    # Group orphans by suggested category
    by_category = defaultdict(list)
    unassigned = []

    for kw in orphans:
        slug, confidence = suggest_category(kw["keyword"])
        if slug:
            by_category[slug].append({**kw, "confidence": confidence})
        else:
            unassigned.append(kw)

    print("\n📊 Распределение сирот по категориям:")
    print("=" * 60)

    # Sort by total volume
    sorted_cats = sorted(
        by_category.items(), key=lambda x: sum(k["volume"] for k in x[1]), reverse=True
    )

    for slug, keywords in sorted_cats:
        total_vol = sum(k["volume"] for k in keywords)
        print(f"\n{slug}: {len(keywords)} ключей, общий volume={total_vol}")
        # Show top 5 by volume
        top5 = sorted(keywords, key=lambda x: x["volume"], reverse=True)[:5]
        for kw in top5:
            print(f"   + {kw['keyword']} ({kw['volume']})")
        if len(keywords) > 5:
            print(f"   ... и ещё {len(keywords) - 5}")

    if unassigned:
        print(f"\n❓ Не удалось распределить: {len(unassigned)} ключей")
        unassigned_sorted = sorted(unassigned, key=lambda x: x["volume"], reverse=True)
        for kw in unassigned_sorted[:10]:
            print(f"   ? {kw['keyword']} ({kw['volume']})")
        if len(unassigned) > 10:
            print(f"   ... и ещё {len(unassigned) - 10}")

    # Return data for potential auto-fix
    return by_category, unassigned


def distribute_orphans(by_category: dict[str, list], dry_run: bool = True) -> int:
    """Распределяет сирот по _clean.json файлам.

    Args:
        by_category: словарь {slug: [keywords]}
        dry_run: если True - только показать что будет сделано

    Returns:
        количество добавленных ключей
    """
    COMMERCIAL_MODIFIERS = ["купить", "цена", "заказать", "стоимость", "недорого", "оптом"]

    total_added = 0

    for slug, keywords in sorted(by_category.items()):
        clean_path = CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"

        if not clean_path.exists():
            print(f"⚠️  {slug}: файл не найден, пропускаем")
            continue

        # Read current data
        with open(clean_path, encoding="utf-8") as f:
            data = json.load(f)

        kw_data = data.get("keywords", {})
        existing = set()
        for cat in ["primary", "secondary", "supporting", "commercial"]:
            for kw in kw_data.get(cat, []):
                existing.add(kw["keyword"].lower())

        # Filter out already existing
        new_keywords = [kw for kw in keywords if kw["keyword"].lower() not in existing]

        if not new_keywords:
            continue

        # Sort by volume
        new_keywords.sort(key=lambda x: x["volume"], reverse=True)

        # Distribute to categories
        added = {"primary": [], "secondary": [], "supporting": [], "commercial": []}

        for kw in new_keywords:
            keyword = kw["keyword"]
            volume = kw["volume"]
            is_commercial = any(mod in keyword.lower() for mod in COMMERCIAL_MODIFIERS)

            if is_commercial:
                if len(added["commercial"]) < 10:  # Limit commercials
                    added["commercial"].append(
                        {
                            "keyword": keyword,
                            "volume": volume,
                            "cluster": "commercial",
                            "use_in": "meta_only",
                        }
                    )
            elif volume >= 200:
                if len(added["primary"]) < 5:
                    added["primary"].append(
                        {"keyword": keyword, "volume": volume, "cluster": "main"}
                    )
                else:
                    added["secondary"].append(
                        {"keyword": keyword, "volume": volume, "cluster": "related"}
                    )
            elif volume >= 30:
                added["secondary"].append(
                    {"keyword": keyword, "volume": volume, "cluster": "related"}
                )
            else:
                added["supporting"].append(
                    {"keyword": keyword, "volume": volume, "cluster": "long_tail"}
                )

        # Merge with existing
        for cat in ["primary", "secondary", "supporting", "commercial"]:
            if cat not in kw_data:
                kw_data[cat] = []
            kw_data[cat].extend(added[cat])
            # Sort by volume
            kw_data[cat].sort(key=lambda x: x["volume"], reverse=True)

        # Update stats
        total_kws = sum(
            len(kw_data.get(cat, []))
            for cat in ["primary", "secondary", "supporting", "commercial"]
        )
        total_vol = sum(
            kw["volume"]
            for cat in ["primary", "secondary", "supporting", "commercial"]
            for kw in kw_data.get(cat, [])
        )

        if "stats" in data:
            data["stats"]["after"] = total_kws
            data["stats"]["total_volume"] = total_vol

        added_count = sum(len(v) for v in added.values())
        total_added += added_count

        if dry_run:
            print(f"📝 {slug}: +{added_count} ключей (dry-run)")
            for cat, kws in added.items():
                if kws:
                    print(f"   {cat}: {len(kws)}")
        else:
            # Write
            with open(clean_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ {slug}: +{added_count} ключей")

    return total_added


if __name__ == "__main__":
    import sys

    distribute_mode = "--distribute" in sys.argv
    dry_run = "--apply" not in sys.argv

    by_category, unassigned = main()

    if distribute_mode:
        print("\n" + "=" * 60)
        if dry_run:
            print("🔍 Режим dry-run (добавьте --apply для записи)")
        else:
            print("📝 Применяем изменения...")

        added = distribute_orphans(by_category, dry_run=dry_run)
        print(f"\n{'Будет добавлено' if dry_run else 'Добавлено'}: {added} ключей")
