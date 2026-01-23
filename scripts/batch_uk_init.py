#!/usr/bin/env python3
"""Batch UK init: create _clean.json and _meta.json for all categories."""

import json
import re
from pathlib import Path

# Translation dictionary RU → UK
TRANSLATIONS = {
    # Nouns
    "резина": "гума",
    "средство": "засіб",
    "мойка": "миття",
    "стекло": "скло",
    "чернитель": "чорнитель",
    "очиститель": "очищувач",
    "полироль": "поліроль",
    "полировка": "полірування",
    "полировальн": "полірувальн",
    "аккумулятор": "акумулятор",
    "машинк": "машинк",
    "машина": "машина",
    "воск": "віск",
    "покрыти": "покритт",
    "защит": "захист",
    "керамик": "керамік",
    "жидк": "рідк",
    "твёрд": "тверд",
    "твердый": "твердий",
    "пластик": "пластик",
    "кожа": "шкіра",
    "кож": "шкір",
    "салон": "салон",
    "интерьер": "інтер'єр",
    "двигател": "двигун",
    "диск": "диск",
    "шин": "шин",
    "шампун": "шампун",
    "пена": "піна",
    "пятн": "плям",
    "запах": "запах",
    "обезжириват": "знежирювач",
    "скраб": "скраб",
    "глин": "глин",
    "губк": "губк",
    "варежк": "рукавичк",
    "микрофибр": "мікрофібр",
    "тряпк": "ганчірк",
    "кист": "кист",
    "щётк": "щітк",
    "щетк": "щітк",
    "распылител": "розпилювач",
    "пенник": "піноутворювач",
    "ведр": "відр",
    "ёмкост": "ємност",
    "набор": "набір",
    "скотч": "скотч",
    "оборудован": "обладнання",
    "торнадор": "торнадор",
    "силант": "силант",
    "детейлер": "детейлер",
    "детейлинг": "детейлінг",
    "круг": "круг",
    "меховой": "хутряний",
    "мехов": "хутрян",
    "паст": "паст",
    "омыват": "омивач",
    # Verbs/adjectives
    "ручн": "ручн",
    "купить": "купити",
    "выбрать": "обрати",
    "нанесен": "нанесен",
    "аксессуар": "аксесуар",
    "химчистк": "хімчистк",
    "нейтрализатор": "нейтралізатор",
    "наружн": "зовнішн",
    "беспроводн": "бездротов",
    # Commercial (meta_only)
    "интернет-магазин": "інтернет-магазин",
    "цена": "ціна",
    "недорого": "недорого",
    "доставка": "доставка",
    "украина": "україна",
    "Украина": "Україна",
    "Украине": "Україні",
}

# Category name translations
CATEGORY_NAMES = {
    "akkumulyatornaya": ("Аккумуляторные полировальные машинки", "Акумуляторні полірувальні машинки"),
    "aksessuary": ("Аксессуары", "Аксесуари"),
    "aksessuary-dlya-naneseniya-sredstv": ("Аксессуары для нанесения средств", "Аксесуари для нанесення засобів"),
    "antidozhd": ("Антидождь", "Антидощ"),
    "apparaty-tornador": ("Аппараты Торнадор", "Апарати Торнадор"),
    "avtoshampuni": ("Автошампуни", "Автошампуні"),
    "cherniteli-shin": ("Чернители шин", "Чорнителі шин"),
    "glina-i-avtoskraby": ("Глина и автоскрабы", "Глина та автоскраби"),
    "gubki-i-varezhki": ("Губки и варежки", "Губки та рукавички"),
    "keramika-dlya-diskov": ("Керамика для дисков", "Кераміка для дисків"),
    "keramika-i-zhidkoe-steklo": ("Керамика и жидкое стекло", "Кераміка та рідке скло"),
    "kisti-dlya-deteylinga": ("Кисти для детейлинга", "Кисті для детейлінгу"),
    "kvik-deteylery": ("Квик-детейлеры", "Квік-детейлери"),
    "malyarniy-skotch": ("Малярный скотч", "Малярний скотч"),
    "mekhovye": ("Меховые круги", "Хутряні круги"),
    "mikrofibra-i-tryapki": ("Микрофибра и тряпки", "Мікрофібра та ганчірки"),
    "moyka-i-eksterer": ("Мойка и экстерьер", "Миття та екстер'єр"),
    "nabory": ("Наборы", "Набори"),
    "neytralizatory-zapakha": ("Нейтрализаторы запаха", "Нейтралізатори запаху"),
    "obezzhirivateli": ("Обезжириватели", "Знежирювачі"),
    "oborudovanie": ("Оборудование", "Обладнання"),
    "ochistiteli-diskov": ("Очистители дисков", "Очищувачі дисків"),
    "ochistiteli-dvigatelya": ("Очистители двигателя", "Очищувачі двигуна"),
    "ochistiteli-kozhi": ("Очистители кожи", "Очищувачі шкіри"),
    "ochistiteli-shin": ("Очистители шин", "Очищувачі шин"),
    "ochistiteli-stekol": ("Очистители стёкол", "Очищувачі скла"),
    "omyvatel": ("Омыватель", "Омивач"),
    "opt-i-b2b": ("Опт и B2B", "Опт та B2B"),
    "polirol-dlya-stekla": ("Полироль для стекла", "Поліроль для скла"),
    "poliroli-dlya-plastika": ("Полироли для пластика", "Поліролі для пластику"),
    "polirovalnye-pasty": ("Полировальные пасты", "Полірувальні пасти"),
    "polirovka": ("Полировка", "Полірування"),
    "pyatnovyvoditeli": ("Пятновыводители", "Плямовивідники"),
    "raspyliteli-i-penniki": ("Распылители и пенники", "Розпилювачі та піноутворювачі"),
    "shampuni-dlya-ruchnoy-moyki": ("Шампуни для ручной мойки", "Шампуні для ручного миття"),
    "shchetka-dlya-moyki-avto": ("Щётка для мойки авто", "Щітка для миття авто"),
    "silanty": ("Силанты", "Силанти"),
    "sredstva-dlya-khimchistki-salona": ("Средства для химчистки салона", "Засоби для хімчистки салону"),
    "sredstva-dlya-kozhi": ("Средства для кожи", "Засоби для шкіри"),
    "tverdyy-vosk": ("Твёрдый воск", "Твердий віск"),
    "ukhod-za-intererom": ("Уход за интерьером", "Догляд за інтер'єром"),
    "ukhod-za-kozhey": ("Уход за кожей", "Догляд за шкірою"),
    "ukhod-za-naruzhnym-plastikom": ("Уход за наружным пластиком", "Догляд за зовнішнім пластиком"),
    "vedra-i-emkosti": ("Вёдра и ёмкости", "Відра та ємності"),
    "voski": ("Воски", "Воски"),
    "zashchitnye-pokrytiya": ("Защитные покрытия", "Захисні покриття"),
    "zhidkiy-vosk": ("Жидкий воск", "Рідкий віск"),
}


def translate_keyword(text: str) -> str:
    """Translate RU keyword to UK."""
    result = text
    for ru, uk in sorted(TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        result = re.sub(re.escape(ru), uk, result, flags=re.IGNORECASE)
    return result


def translate_title(title_ru: str, slug: str) -> str:
    """Translate meta title RU → UK."""
    name_ru, name_uk = CATEGORY_NAMES.get(slug, (slug, slug))
    # Replace category name
    result = title_ru.replace(name_ru, name_uk)
    # Replace "купить" → "Купити"
    result = re.sub(r"\bкупить\b", "Купити", result, flags=re.IGNORECASE)
    # Other translations
    result = result.replace("интернет-магазин", "інтернет-магазин")
    result = result.replace("Интернет-магазин", "Інтернет-магазин")
    return result


def translate_description(desc_ru: str, slug: str) -> str:
    """Translate meta description RU → UK."""
    name_ru, name_uk = CATEGORY_NAMES.get(slug, (slug, slug))
    result = desc_ru.replace(name_ru, name_uk)
    # Common translations
    replacements = [
        ("интернет-магазин", "інтернет-магазин"),
        ("Интернет-магазин", "Інтернет-магазин"),
        ("купить", "купити"),
        ("Купить", "Купити"),
        ("в Украине", "в Україні"),
        ("Украине", "Україні"),
        ("выбор", "вибір"),
        ("доставка", "доставка"),
        ("цена", "ціна"),
        ("по всей", "по всій"),
        ("Доставка по всей Украине", "Доставка по всій Україні"),
    ]
    for ru, uk in replacements:
        result = result.replace(ru, uk)
    return result


def translate_h1(h1_ru: str, slug: str) -> str:
    """Translate H1 RU → UK (NO 'Купити')."""
    name_ru, name_uk = CATEGORY_NAMES.get(slug, (slug, slug))
    result = h1_ru.replace(name_ru, name_uk)
    # Remove any "купить/купити" from H1
    result = re.sub(r"\b[Кк]упить\b\s*", "", result)
    result = re.sub(r"\b[Кк]упити\b\s*", "", result)
    return result.strip()


def process_category(slug: str, ru_meta_path: str) -> dict:
    """Process single category: read RU, create UK files."""
    base = Path("/mnt/c/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт")
    ru_meta = base / ru_meta_path
    uk_dir = base / "uk" / "categories" / slug

    # Read RU meta
    with open(ru_meta, "r", encoding="utf-8") as f:
        meta_ru = json.load(f)

    # Get category names
    name_ru, name_uk = CATEGORY_NAMES.get(slug, (meta_ru.get("h1", slug), meta_ru.get("h1", slug)))

    # Create UK meta
    meta_uk = {
        "slug": slug,
        "language": "uk",
        "meta": {
            "title": translate_title(meta_ru["meta"]["title"], slug),
            "description": translate_description(meta_ru["meta"]["description"], slug),
        },
        "h1": translate_h1(meta_ru["h1"], slug) if meta_ru.get("h1") else name_uk,
        "status": "generated",
        "updated_at": "2026-01-23",
    }

    # Add keywords_in_content if present
    if "keywords_in_content" in meta_ru:
        kw = meta_ru["keywords_in_content"]
        meta_uk["keywords_in_content"] = {
            "primary": [translate_keyword(k) for k in kw.get("primary", [])],
            "secondary": [translate_keyword(k) for k in kw.get("secondary", [])],
            "supporting": [translate_keyword(k) for k in kw.get("supporting", [])],
        }

    # Write UK meta
    meta_path = uk_dir / "meta" / f"{slug}_meta.json"
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta_uk, f, ensure_ascii=False, indent=2)

    # Create UK clean.json
    clean_uk = {
        "slug": slug,
        "language": "uk",
        "category_name_uk": name_uk,
        "category_name_ru": name_ru,
        "keywords": {
            "primary": [],
            "secondary": [],
            "supporting": [],
            "commercial": [
                {
                    "keyword": f"купити {name_uk.lower()}",
                    "keyword_ru": f"купить {name_ru.lower()}",
                    "volume": 100,
                    "use_in": "meta_only",
                }
            ],
        },
        "translation_notes": {
            "adapted_terms": list(TRANSLATIONS.items())[:5],
            "kept_original": ["pH", "PPF", "APC", "SiO2"],
            "intent_preserved": True,
        },
    }

    # Add keywords from meta
    if "keywords_in_content" in meta_ru:
        kw = meta_ru["keywords_in_content"]
        for k in kw.get("primary", []):
            clean_uk["keywords"]["primary"].append(
                {
                    "keyword": translate_keyword(k),
                    "keyword_ru": k,
                    "volume": 100,
                }
            )
        for k in kw.get("secondary", []):
            clean_uk["keywords"]["secondary"].append(
                {
                    "keyword": translate_keyword(k),
                    "keyword_ru": k,
                    "volume": 50,
                }
            )
        for k in kw.get("supporting", []):
            clean_uk["keywords"]["supporting"].append(
                {
                    "keyword": translate_keyword(k),
                    "keyword_ru": k,
                    "volume": 20,
                }
            )

    # Write UK clean
    clean_path = uk_dir / "data" / f"{slug}_clean.json"
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(clean_uk, f, ensure_ascii=False, indent=2)

    # Create CONTEXT.md
    context_md = f"""# Research Context: {name_uk}

## Primary Keyword
**UK:** {name_uk.lower()}
**RU:** {name_ru.lower()}

## Category
- **Slug:** {slug}
- **Name UK:** {name_uk}
- **Name RU:** {name_ru}

## Content Requirements
- 300-700 words
- H1 = primary keyword (NO "Купити")
- Intro: 30-60 words
- 1+ table, 1+ warning

## RU Research
See: {ru_meta_path.replace("/meta/", "/research/").replace("_meta.json", "/RESEARCH_DATA.md")}

## Next Steps
1. Copy RESEARCH_DATA.md from RU (if exists)
2. Write uk/categories/{slug}/content/{slug}_uk.md
"""
    context_path = uk_dir / "research" / "CONTEXT.md"
    context_path.parent.mkdir(parents=True, exist_ok=True)
    with open(context_path, "w", encoding="utf-8") as f:
        f.write(context_md)

    return {
        "slug": slug,
        "meta_created": str(meta_path),
        "clean_created": str(clean_path),
        "context_created": str(context_path),
    }


# Categories mapping
CATEGORIES = {
    "akkumulyatornaya": "categories/polirovka/polirovalnye-mashinki/akkumulyatornaya/meta/akkumulyatornaya_meta.json",
    "aksessuary": "categories/aksessuary/meta/aksessuary_meta.json",
    "aksessuary-dlya-naneseniya-sredstv": "categories/aksessuary/aksessuary-dlya-naneseniya-sredstv/meta/aksessuary-dlya-naneseniya-sredstv_meta.json",
    "antidozhd": "categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/meta/antidozhd_meta.json",
    "apparaty-tornador": "categories/oborudovanie/apparaty-tornador/meta/apparaty-tornador_meta.json",
    "avtoshampuni": "categories/moyka-i-eksterer/avtoshampuni/meta/avtoshampuni_meta.json",
    "cherniteli-shin": "categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/meta/cherniteli-shin_meta.json",
    "glina-i-avtoskraby": "categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json",
    "gubki-i-varezhki": "categories/aksessuary/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json",
    "keramika-dlya-diskov": "categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/meta/keramika-dlya-diskov_meta.json",
    "keramika-i-zhidkoe-steklo": "categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json",
    "kisti-dlya-deteylinga": "categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/meta/kisti-dlya-deteylinga_meta.json",
    "kvik-deteylery": "categories/zashchitnye-pokrytiya/kvik-deteylery/meta/kvik-deteylery_meta.json",
    "malyarniy-skotch": "categories/aksessuary/malyarniy-skotch/meta/malyarniy-skotch_meta.json",
    "mekhovye": "categories/polirovka/polirovalnye-krugi/mekhovye/meta/mekhovye_meta.json",
    "mikrofibra-i-tryapki": "categories/aksessuary/mikrofibra-i-tryapki/meta/mikrofibra-i-tryapki_meta.json",
    "moyka-i-eksterer": "categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json",
    "nabory": "categories/aksessuary/nabory/meta/nabory_meta.json",
    "neytralizatory-zapakha": "categories/ukhod-za-intererom/neytralizatory-zapakha/meta/neytralizatory-zapakha_meta.json",
    "obezzhirivateli": "categories/moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli/meta/obezzhirivateli_meta.json",
    "oborudovanie": "categories/oborudovanie/meta/oborudovanie_meta.json",
    "ochistiteli-diskov": "categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov/meta/ochistiteli-diskov_meta.json",
    "ochistiteli-dvigatelya": "categories/moyka-i-eksterer/ochistiteli-dvigatelya/meta/ochistiteli-dvigatelya_meta.json",
    "ochistiteli-kozhi": "categories/ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi/meta/ochistiteli-kozhi_meta.json",
    "ochistiteli-shin": "categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin/meta/ochistiteli-shin_meta.json",
    "ochistiteli-stekol": "categories/moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol/meta/ochistiteli-stekol_meta.json",
    "omyvatel": "categories/moyka-i-eksterer/sredstva-dlya-stekol/omyvatel/meta/omyvatel_meta.json",
    "opt-i-b2b": "categories/opt-i-b2b/meta/opt-i-b2b_meta.json",
    "polirol-dlya-stekla": "categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/meta/polirol-dlya-stekla_meta.json",
    "poliroli-dlya-plastika": "categories/ukhod-za-intererom/poliroli-dlya-plastika/meta/poliroli-dlya-plastika_meta.json",
    "polirovalnye-pasty": "categories/polirovka/polirovalnye-pasty/meta/polirovalnye-pasty_meta.json",
    "polirovka": "categories/polirovka/meta/polirovka_meta.json",
    "pyatnovyvoditeli": "categories/ukhod-za-intererom/pyatnovyvoditeli/meta/pyatnovyvoditeli_meta.json",
    "raspyliteli-i-penniki": "categories/aksessuary/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json",
    "shampuni-dlya-ruchnoy-moyki": "categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/meta/shampuni-dlya-ruchnoy-moyki_meta.json",
    "shchetka-dlya-moyki-avto": "categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/meta/shchetka-dlya-moyki-avto_meta.json",
    "silanty": "categories/zashchitnye-pokrytiya/silanty/meta/silanty_meta.json",
    "sredstva-dlya-khimchistki-salona": "categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/meta/sredstva-dlya-khimchistki-salona_meta.json",
    "sredstva-dlya-kozhi": "categories/ukhod-za-intererom/sredstva-dlya-kozhi/meta/sredstva-dlya-kozhi_meta.json",
    "tverdyy-vosk": "categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/meta/tverdyy-vosk_meta.json",
    "ukhod-za-intererom": "categories/ukhod-za-intererom/meta/ukhod-za-intererom_meta.json",
    "ukhod-za-kozhey": "categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/meta/ukhod-za-kozhey_meta.json",
    "ukhod-za-naruzhnym-plastikom": "categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/meta/ukhod-za-naruzhnym-plastikom_meta.json",
    "vedra-i-emkosti": "categories/aksessuary/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json",
    "voski": "categories/zashchitnye-pokrytiya/voski/meta/voski_meta.json",
    "zashchitnye-pokrytiya": "categories/zashchitnye-pokrytiya/meta/zashchitnye-pokrytiya_meta.json",
    "zhidkiy-vosk": "categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/meta/zhidkiy-vosk_meta.json",
}


if __name__ == "__main__":
    success = 0
    errors = []

    for slug, ru_path in CATEGORIES.items():
        try:
            result = process_category(slug, ru_path)
            print(f"✓ {slug}")
            success += 1
        except Exception as e:
            print(f"✗ {slug}: {e}")
            errors.append((slug, str(e)))

    print(f"\n=== DONE: {success}/{len(CATEGORIES)} categories ===")
    if errors:
        print("Errors:")
        for slug, err in errors:
            print(f"  - {slug}: {err}")
