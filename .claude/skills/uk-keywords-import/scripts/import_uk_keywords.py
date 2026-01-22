#!/usr/bin/env python3
"""
UK Keywords Import - Imports Ukrainian keywords with frequency from CSV.

Parses CSV with keyword,volume columns, matches keywords to RU categories
using translation mapping, groups by category slug, and writes to JSON.

Usage:
    python import_uk_keywords.py <csv_path> [--output <output_dir>] [--mapping <mapping_file>]

Input CSV format:
    keyword,volume
    чорнитель шин,1200
    активна піна для миття авто,800
    засіб для скла,500

Output: uk/data/uk_keywords.json grouped by category slug
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Optional


# Default translation patterns RU -> UK
TRANSLATION_PATTERNS = {
    # Core translations
    "резина": "гума",
    "средство": "засіб",
    "мойка": "миття",
    "стекло": "скло",
    "чернитель": "чорнитель",
    "очиститель": "очищувач",
    "купить": "купити",
    "полировка": "полірування",
    "воск": "віск",
    "кожа": "шкіра",
    "пятновыводитель": "плямовивідник",
    "обезжириватель": "знежирювач",
    "защита": "захист",
    "диск": "диск",
    "шина": "шина",
    # Action verbs
    "мыть": "мити",
    "чистить": "чистити",
    "полировать": "полірувати",
}

# Reverse mapping UK -> RU for matching
REVERSE_PATTERNS = {v: k for k, v in TRANSLATION_PATTERNS.items()}

# Category slug to keywords mapping (main keywords) - all 50 categories
CATEGORY_KEYWORDS = {
    # === L1 Categories (7) ===
    "aksessuary": ["аксесуари", "аксесуари для детейлінгу", "приладдя"],
    "moyka-i-eksterer": ["миття", "екстер'єр", "зовнішній догляд"],
    "oborudovanie": ["обладнання", "обладнання для детейлінгу", "техніка"],
    "opt-i-b2b": ["опт", "оптом", "b2b", "гуртом"],
    "polirovka": ["полірування", "полірувальні засоби", "поліровка"],
    "ukhod-za-intererom": ["інтер'єр", "догляд за салоном", "чистка салону"],
    "zashchitnye-pokrytiya": ["захисне покриття", "захист кузова", "захисні засоби"],

    # === L2/L3 Categories (43) ===
    "aktivnaya-pena": ["активна піна", "піна для миття", "безконтактна піна"],
    "antibitum": ["антибітум", "засіб від бітуму", "очищувач бітуму"],
    "antimoshka": ["антимошка", "засіб від мошки", "очищувач від комах"],
    "antidozhd": ["антидощ", "антидощ для скла", "гідрофобне покриття"],
    "apparaty-tornador": ["торнадор", "апарат торнадор", "tornador"],
    "aksessuary-dlya-naneseniya-sredstv": ["аплікатор", "апликатори", "подушечка для нанесення"],
    "akkumulyatornaya": ["акумуляторна", "акумуляторна машинка", "бездротова"],
    "avtoshampuni": ["автошампунь", "шампунь для авто", "автошампуні"],
    "cherniteli-shin": ["чорнитель шин", "чорніння шин", "чорнитель гуми"],
    "glina-i-avtoskraby": ["глина", "автоскраб", "очисна глина"],
    "gubki-i-varezhki": ["губка для миття", "рукавиця для миття", "мийна губка"],
    "keramika-dlya-diskov": ["кераміка для дисків", "керамічне покриття дисків"],
    "keramika-i-zhidkoe-steklo": ["кераміка", "рідке скло", "керамічне покриття"],
    "kisti-dlya-deteylinga": ["пензель для детейлінгу", "кисть детейлінг", "кисті"],
    "kvik-deteylery": ["квік детейлер", "швидкий детейлер", "детейлер спрей"],
    "malyarniy-skotch": ["малярний скотч", "малярна стрічка", "скотч"],
    "mekhovye": ["хутряний круг", "овчина", "хутро для полірування"],
    "mikrofibra-i-tryapki": ["мікрофібра", "серветка мікрофібра", "ганчірка"],
    "nabory": ["набір", "набори для детейлінгу", "комплект"],
    "neytralizatory-zapakha": ["нейтралізатор запаху", "поглинач запаху", "освіжувач"],
    "obezzhirivateli": ["знежирювач", "засіб знежирювання", "обезжирювач"],
    "ochistiteli-diskov": ["очищувач дисків", "засіб для дисків", "мийка дисків"],
    "ochistiteli-dvigatelya": ["очищувач двигуна", "мийка двигуна", "засіб для мотора"],
    "ochistiteli-kozhi": ["очищувач шкіри", "засіб для чищення шкіри"],
    "ochistiteli-shin": ["очищувач шин", "засіб для очистки шин"],
    "ochistiteli-stekol": ["очищувач скла", "засіб для скла", "миття скла"],
    "ochistiteli-kuzova": ["очищувач кузова", "засіб для кузова", "мийка кузова"],
    "omyvatel": ["омивач", "омивач скла", "рідина для омивача"],
    "polirol-dlya-stekla": ["поліроль для скла", "полірування скла"],
    "poliroli-dlya-plastika": ["поліроль для пластику", "засіб для пластику"],
    "polirovalnye-krugi": ["полірувальний круг", "круг для полірування", "поролоновий круг"],
    "polirovalnye-mashinki": ["полірувальна машинка", "машинка для полірування"],
    "polirovalnye-pasty": ["полірувальна паста", "паста для полірування", "абразивна паста"],
    "pyatnovyvoditeli": ["плямовивідник", "засіб від плям", "виводитель плям"],
    "raspyliteli-i-penniki": ["розпилювач", "пінник", "пульверизатор", "тригер"],
    "shampuni-dlya-ruchnoy-moyki": ["шампунь для ручного миття", "ручний шампунь"],
    "shchetka-dlya-moyki-avto": ["щітка для миття", "мийна щітка", "щітка авто"],
    "shchetki-i-kisti": ["щітки", "кисті", "набір щіток"],
    "silanty": ["силант", "силанти", "герметик для кузова"],
    "sredstva-dlya-diskov-i-shin": ["засіб для дисків і шин", "догляд за дисками"],
    "sredstva-dlya-khimchistki-salona": ["хімчистка салону", "засіб для салону", "чистка тканини"],
    "sredstva-dlya-kozhi": ["засіб для шкіри", "догляд за шкірою", "кондиціонер шкіри"],
    "sredstva-dlya-stekol": ["засіб для скла", "догляд за склом"],
    "tverdyy-vosk": ["твердий віск", "пастоподібний віск", "карнаубський віск"],
    "ukhod-za-kozhey": ["догляд за шкірою", "шкіра авто", "кондиціонер"],
    "ukhod-za-naruzhnym-plastikom": ["догляд за пластиком", "чорнитель пластику", "зовнішній пластик"],
    "vedra-i-emkosti": ["відро", "ємність", "відро для миття"],
    "voski": ["віск", "віск для авто", "автовіск", "воскування"],
    "zhidkiy-vosk": ["рідкий віск", "спрей віск", "швидкий віск"],
}


def normalize_keyword(keyword: str) -> str:
    """Normalize keyword for matching: lowercase, strip, collapse spaces."""
    return re.sub(r'\s+', ' ', keyword.lower().strip())


def translate_uk_to_ru_pattern(uk_keyword: str) -> str:
    """Attempt to translate UK keyword back to RU for matching."""
    result = uk_keyword.lower()
    for uk_pattern, ru_pattern in REVERSE_PATTERNS.items():
        result = result.replace(uk_pattern, ru_pattern)
    return result


def match_keyword_to_category(keyword: str, category_keywords: dict) -> Optional[str]:
    """Match a UK keyword to a category slug."""
    normalized = normalize_keyword(keyword)

    # Direct match in category keywords
    for slug, keywords in category_keywords.items():
        for cat_kw in keywords:
            if cat_kw in normalized or normalized in cat_kw:
                return slug
            # Try substring match
            cat_normalized = normalize_keyword(cat_kw)
            if cat_normalized in normalized or normalized in cat_normalized:
                return slug

    # Try translating back to RU patterns and matching
    ru_pattern = translate_uk_to_ru_pattern(normalized)
    for slug, keywords in category_keywords.items():
        for cat_kw in keywords:
            cat_ru = translate_uk_to_ru_pattern(cat_kw)
            if cat_ru in ru_pattern or ru_pattern in cat_ru:
                return slug

    return None


def load_custom_mapping(mapping_path: Path) -> dict:
    """Load custom category-keyword mapping from JSON file."""
    if not mapping_path.exists():
        return {}

    with open(mapping_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_csv_keywords(csv_path: Path) -> list[dict]:
    """Read keywords from CSV file."""
    keywords = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        # Try to detect delimiter
        sample = f.read(2048)
        f.seek(0)

        # Check for different delimiters
        if ';' in sample and ',' not in sample:
            delimiter = ';'
        elif '\t' in sample:
            delimiter = '\t'
        else:
            delimiter = ','

        reader = csv.DictReader(f, delimiter=delimiter)

        # Normalize column names
        fieldnames = reader.fieldnames
        keyword_col = None
        volume_col = None

        for field in fieldnames:
            field_lower = field.lower().strip()
            if field_lower in ('keyword', 'keywords', 'query', 'ключ', 'ключове слово', 'запит'):
                keyword_col = field
            elif field_lower in ('volume', 'freq', 'frequency', 'частота', 'частотність', 'об\'єм'):
                volume_col = field

        if not keyword_col:
            # Assume first column is keyword
            keyword_col = fieldnames[0]
        if not volume_col and len(fieldnames) > 1:
            # Assume second column is volume
            volume_col = fieldnames[1]

        for row in reader:
            keyword = row.get(keyword_col, '').strip()
            volume_str = row.get(volume_col, '0').strip()

            if not keyword:
                continue

            # Parse volume (handle various formats)
            try:
                volume = int(re.sub(r'[^\d]', '', volume_str) or 0)
            except ValueError:
                volume = 0

            keywords.append({
                'keyword': keyword,
                'volume': volume
            })

    return keywords


def group_keywords_by_category(
    keywords: list[dict],
    category_keywords: dict
) -> tuple[dict, list[dict]]:
    """Group keywords by category, return grouped and unmatched."""
    grouped = defaultdict(list)
    unmatched = []

    for kw_data in keywords:
        keyword = kw_data['keyword']
        category = match_keyword_to_category(keyword, category_keywords)

        if category:
            grouped[category].append(kw_data)
        else:
            unmatched.append(kw_data)

    # Sort keywords within each category by volume (descending)
    for slug in grouped:
        grouped[slug] = sorted(grouped[slug], key=lambda x: x['volume'], reverse=True)

    return dict(grouped), unmatched


def write_output(
    grouped: dict,
    unmatched: list,
    output_dir: Path,
    source_file: str
):
    """Write grouped keywords to JSON output."""
    output_dir.mkdir(parents=True, exist_ok=True)

    output_data = {
        "source": source_file,
        "total_keywords": sum(len(kws) for kws in grouped.values()) + len(unmatched),
        "matched_keywords": sum(len(kws) for kws in grouped.values()),
        "unmatched_keywords": len(unmatched),
        "categories": {}
    }

    for slug, keywords in sorted(grouped.items()):
        output_data["categories"][slug] = {
            "count": len(keywords),
            "total_volume": sum(kw['volume'] for kw in keywords),
            "keywords": keywords
        }

    if unmatched:
        output_data["unmatched"] = sorted(unmatched, key=lambda x: x['volume'], reverse=True)

    output_path = output_dir / "uk_keywords.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Output written to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Import UK keywords from CSV and group by category"
    )
    parser.add_argument(
        "csv_path",
        type=Path,
        help="Path to input CSV file with keyword,volume columns"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("uk/data"),
        help="Output directory (default: uk/data)"
    )
    parser.add_argument(
        "--mapping", "-m",
        type=Path,
        help="Custom category-keyword mapping JSON file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"Error: CSV file not found: {args.csv_path}", file=sys.stderr)
        sys.exit(1)

    # Load custom mapping if provided
    category_keywords = CATEGORY_KEYWORDS.copy()
    if args.mapping:
        custom = load_custom_mapping(args.mapping)
        category_keywords.update(custom)
        if args.verbose:
            print(f"Loaded {len(custom)} custom category mappings")

    # Read CSV
    keywords = read_csv_keywords(args.csv_path)
    print(f"Read {len(keywords)} keywords from {args.csv_path}")

    # Group by category
    grouped, unmatched = group_keywords_by_category(keywords, category_keywords)

    print(f"Matched: {sum(len(kws) for kws in grouped.values())} keywords in {len(grouped)} categories")
    print(f"Unmatched: {len(unmatched)} keywords")

    if args.verbose and unmatched:
        print("\nTop 10 unmatched keywords:")
        for kw in unmatched[:10]:
            print(f"  - {kw['keyword']} (volume: {kw['volume']})")

    # Write output
    output_path = write_output(grouped, unmatched, args.output, args.csv_path.name)

    print(f"\nCategories with keywords:")
    for slug in sorted(grouped.keys()):
        count = len(grouped[slug])
        volume = sum(kw['volume'] for kw in grouped[slug])
        print(f"  {slug}: {count} keywords, total volume: {volume}")


if __name__ == "__main__":
    main()
