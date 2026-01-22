#!/usr/bin/env python3
"""
Export RU keywords from all categories, translate to UK, deduplicate.
Output: data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
"""

import json
import re
import sys
from pathlib import Path

# Translation dictionary RU → UK (based on TRANSLATION_RULES.md)
TRANSLATION_MAP = {
    # Базовые термины
    "резина": "гума",
    "резины": "гуми",
    "резину": "гуму",
    "резиной": "гумою",
    "средство": "засіб",
    "средства": "засоби",
    "автомобиль": "автомобіль",
    "автомобиля": "автомобіля",
    "автомобилей": "автомобілів",
    "автомобилем": "автомобілем",
    "автомобильный": "автомобільний",
    "автомобильная": "автомобільна",
    # Чернители
    "чернитель": "чорнитель",
    "чернители": "чорнителі",
    "чернение": "чорніння",
    "блеск": "блиск",
    # Мойка
    "мойка": "миття",
    "мойки": "миття",
    "мойку": "миття",
    "мыть": "мити",
    "мытья": "миття",
    "бесконтактная": "безконтактна",
    "бесконтактной": "безконтактної",
    "бесконтактное": "безконтактне",
    "ручная": "ручна",
    "ручной": "ручної",
    "ручное": "ручне",
    "пена": "піна",
    "пену": "піну",
    "пены": "піни",
    "минимойка": "мінімийка",
    "минимойки": "мінімийки",
    # Стекла
    "стекло": "скло",
    "стекла": "скла",
    "стекол": "скла",
    # Очистители
    "очиститель": "очищувач",
    "очистители": "очищувачі",
    "очистителей": "очищувачів",
    "обезжириватель": "знежирювач",
    "обезжиривателя": "знежирювача",
    "обезжиривателей": "знежирювачів",
    "антибитум": "антибітум",
    "антидождь": "антидощ",
    # Защита
    "воск": "віск",
    "воска": "воску",
    "полироль": "поліроль",
    "полироли": "поліролі",
    "керамика": "кераміка",
    "керамики": "кераміки",
    "керамическое": "керамічне",
    "керамическая": "керамічна",
    "защитное": "захисне",
    "защитного": "захисного",
    "защита": "захист",
    "защиты": "захисту",
    "покрытие": "покриття",
    # Коммерческие
    "купить": "купити",
    "цена": "ціна",
    "заказать": "замовити",
    # Интерьер
    "кожа": "шкіра",
    "кожи": "шкіри",
    "кожу": "шкіру",
    "кожей": "шкірою",
    "кожаный": "шкіряний",
    "кожаная": "шкіряна",
    "кожаного": "шкіряного",
    "пластик": "пластик",
    "пластика": "пластику",
    "салон": "салон",
    "салона": "салону",
    # Диски/шины
    "диск": "диск",
    "диски": "диски",
    "дисков": "дисків",
    "шина": "шина",
    "шины": "шини",
    "шин": "шин",
    # Глина
    "глина": "глина",
    "деконтаминация": "деконтамінація",
    # Misc
    "двигатель": "двигун",
    "двигателя": "двигуна",
    "машина": "машина",
    "машины": "машини",
    "машину": "машину",
    "машине": "машині",
    "авто": "авто",
    "автохимия": "автохімія",
    "химчистка": "хімчистка",
    "химчистки": "хімчистки",
    # Полировка
    "полировка": "полірування",
    "полировки": "полірування",
    "полировальная": "полірувальна",
    "полировальный": "полірувальний",
    "полировальные": "полірувальні",
    "паста": "паста",
    "пасты": "пасти",
    "круг": "круг",
    "круги": "круги",
    "кругов": "кругів",
    "машинка": "машинка",
    "машинки": "машинки",
    # Аксессуары
    "губка": "губка",
    "губки": "губки",
    "варежка": "рукавиця",
    "варежки": "рукавиці",
    "щетка": "щітка",
    "щетки": "щітки",
    "кисть": "пензель",
    "кисти": "пензлі",
    "микрофибра": "мікрофібра",
    "микрофибры": "мікрофібри",
    "тряпка": "ганчірка",
    "тряпки": "ганчірки",
    "ведро": "відро",
    "ведра": "відра",
    "распылитель": "розпилювач",
    "распылителя": "розпилювача",
    "пенник": "піноутворювач",
    "пенника": "піноутворювача",
    "скотч": "скотч",
    "малярный": "малярний",
    "набор": "набір",
    "наборы": "набори",
    # Свойства
    "аккумуляторная": "акумуляторна",
    "аккумуляторный": "акумуляторний",
    "профессиональный": "професійний",
    "профессиональная": "професійна",
    "жидкий": "рідкий",
    "жидкая": "рідка",
    "твердый": "твердий",
    "твердая": "тверда",
    "меховой": "хутряний",
    "меховые": "хутряні",
    # Действия
    "уход": "догляд",
    "ухода": "догляду",
    "уходу": "догляду",
    "уходом": "доглядом",
    "чистка": "чистка",
    "чистки": "чистки",
    "удаление": "видалення",
    "удалитель": "видаляч",
    "нейтрализатор": "нейтралізатор",
    "запах": "запах",
    "запаха": "запаху",
    "пятновыводитель": "плямовивідник",
    "пятно": "пляма",
    "пятна": "плями",
    "пятен": "плям",
    # Оптовые
    "опт": "опт",
    "оптом": "оптом",
    "розница": "роздріб",
    "розницу": "роздріб",
    "производитель": "виробник",
    "производителя": "виробника",
    "производство": "виробництво",
    "поставщик": "постачальник",
    "поставщики": "постачальники",
    # Другое
    "наружный": "зовнішній",
    "наружного": "зовнішнього",
    "омыватель": "омивач",
    "омывателя": "омивача",
    "триггер": "тригер",
    "силант": "силант",
    "силанты": "силанти",
    "квик детейлер": "квік детейлер",
    "детейлер": "детейлер",
    "детейлинг": "детейлінг",
    "детейлинга": "детейлінгу",
    # Дополнительные слова
    "активная": "активна",
    "активный": "активний",
    "активное": "активне",
    "аксессуары": "аксесуари",
    "аксессуар": "аксесуар",
    "внутренний": "внутрішній",
    "внутренняя": "внутрішня",
    "наружная": "зовнішня",
    # Служебные слова (с word boundaries они безопасны)
    "от": "від",
    "и": "та",
    "с": "з",
    "на": "на",
    "для": "для",
    "по": "по",
    "или": "або",
    "без": "без",
    "что": "що",
    "как": "як",
    "какой": "який",
    "какая": "яка",
    "какое": "яке",
    "лучший": "кращий",
    "лучшая": "краща",
    "лучшее": "краще",
    "выбрать": "обрати",
    "разводить": "розводити",
    "наносить": "наносити",
    "использовать": "використовувати",
    "зачем": "навіщо",
    "почему": "чому",
    "сколько": "скільки",
    "когда": "коли",
    "где": "де",
    # Дополнительные существительные
    "концентрат": "концентрат",
    "раствор": "розчин",
    "разводов": "розводів",
    "потеков": "патьоків",
    "насадка": "насадка",
    "насадки": "насадки",
    "оборудование": "обладнання",
    "аппарат": "апарат",
    "аппараты": "апарати",
    "автомойка": "автомийка",
    "автомойки": "автомийки",
    "автомоек": "автомийок",
    "автомойке": "автомийці",
    "мойке": "мийці",
    "самообслуживания": "самообслуговування",
    "быстрый": "швидкий",
    "быстрая": "швидка",
    "сетка": "сітка",
    "сеткой": "сіткою",
    "гидрофобное": "гідрофобне",
    "гидрофобный": "гідрофобний",
    "очистки": "очищення",
    "восстановитель": "відновлювач",
    "восковый": "восковий",
    "аппликатор": "аплікатор",
    "всё": "все",
    "химия": "хімія",
    # Дополнительно
    "зеркало": "дзеркало",
    "зеркала": "дзеркала",
    "зеркал": "дзеркал",
    "лобовое": "лобове",
    "лобового": "лобового",
    "краска": "фарба",
    "краски": "фарби",
    "крыло": "крило",
    "крыла": "крила",
    "дверь": "двері",
    "двери": "дверей",
    "спрей": "спрей",
    "чем": "чим",
    "отличается": "відрізняється",
    "правильно": "правильно",
    "своими": "своїми",
    "руками": "руками",
}

# Keywords to skip (structural artifacts, not real keywords)
SKIP_PATTERNS = [
    r"^synonyms_",
    r"^primary$",
    r"^secondary$",
    r"^commercial$",
    r"^supporting$",
    r"^\d+$",  # Just numbers
]


def should_skip(keyword: str) -> bool:
    """Check if keyword should be skipped (structural artifact)."""
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, keyword.lower()):
            return True
    return False


def translate_keyword(keyword: str) -> str:
    """Translate RU keyword to UK using word-by-word replacement."""
    result = keyword.lower()
    # Sort by length descending to replace longer phrases first
    for ru, uk in sorted(TRANSLATION_MAP.items(), key=lambda x: -len(x[0])):
        # Use word boundary replacement for single words (no spaces)
        if " " not in ru:
            # Use regex to match whole words only
            pattern = rf"\b{re.escape(ru)}\b"
            result = re.sub(pattern, uk, result)
        else:
            # For multi-word phrases, use simple replacement
            result = result.replace(ru, uk)
    return result


def extract_keywords_from_file(filepath: Path) -> list[str]:
    """Extract all keywords from a _clean.json file."""
    keywords = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Extract from keywords array
        if "keywords" in data:
            for item in data["keywords"]:
                if isinstance(item, dict) and "keyword" in item:
                    keywords.append(item["keyword"])
                elif isinstance(item, str):
                    keywords.append(item)

        # Extract from synonyms array
        if "synonyms" in data:
            for item in data["synonyms"]:
                if isinstance(item, dict) and "keyword" in item:
                    keywords.append(item["keyword"])
                elif isinstance(item, str):
                    keywords.append(item)

        # Extract from variations array
        if "variations" in data:
            for item in data["variations"]:
                if isinstance(item, dict) and "keyword" in item:
                    keywords.append(item["keyword"])
                elif isinstance(item, str):
                    keywords.append(item)

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)

    return keywords


def main():
    """Main function to export and translate keywords."""
    project_root = Path(__file__).resolve().parents[4]  # Navigate up from scripts folder
    categories_dir = project_root / "categories"
    output_dir = project_root / "data" / "generated"
    output_file = output_dir / "UK_KEYWORDS_FOR_FREQUENCY.md"

    # Find all _clean.json files
    clean_files = list(categories_dir.glob("**/data/*_clean.json"))

    if not clean_files:
        print("No _clean.json files found!", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(clean_files)} category files")

    # Extract all RU keywords
    all_ru_keywords = set()
    for filepath in clean_files:
        keywords = extract_keywords_from_file(filepath)
        all_ru_keywords.update(keywords)

    print(f"Extracted {len(all_ru_keywords)} unique RU keywords")

    # Filter structural artifacts
    filtered_keywords = {kw for kw in all_ru_keywords if not should_skip(kw)}
    print(f"After filtering: {len(filtered_keywords)} keywords")

    # Translate to UK and deduplicate
    uk_keywords = set()
    for ru_kw in filtered_keywords:
        uk_kw = translate_keyword(ru_kw)
        uk_keywords.add(uk_kw)

    print(f"Generated {len(uk_keywords)} unique UK keywords")

    # Sort alphabetically
    sorted_keywords = sorted(uk_keywords)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# UK Keywords for Frequency Check\n\n")
        f.write(f"Generated from {len(clean_files)} categories.\n")
        f.write(f"Total: {len(sorted_keywords)} unique keywords.\n\n")
        f.write("---\n\n")
        for kw in sorted_keywords:
            f.write(f"{kw}\n")

    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    main()
