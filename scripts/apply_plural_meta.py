#!/usr/bin/env python3
"""
Apply plural forms to _meta.json files.
Usage: python3 scripts/apply_plural_meta.py --lang uk --dry-run
       python3 scripts/apply_plural_meta.py --lang uk --apply
"""

import argparse
import json
import re
from pathlib import Path

# Load exceptions
EXCEPTIONS_FILE = Path("data/generated/plural_exceptions.json")
SKIP_SLUGS = []
if EXCEPTIONS_FILE.exists():
    with open(EXCEPTIONS_FILE) as f:
        SKIP_SLUGS = json.load(f).get("skip_slugs", [])

# Manual mapping for complex cases
MANUAL_PLURAL_UK = {
    "Очищувач": "Очищувачі",
    "Поліроль": "Поліролі",
    "Силант": "Силанти",
    "Знежирювач": "Знежирювачі",
    "Плямовивідник": "Плямовивідники",
    "Поглинач": "Поглиначі",
    "Губка": "Губки",
    "Відро": "Відра",
    "Набір": "Набори",
    "Віск": "Воски",
    "Автошампунь": "Автошампуні",
    "Щітка": "Щітки",
    "Торнадор": "Торнадори",
    "Відновлювач": "Відновлювачі",
    "Полірувальна паста": "Полірувальні пасти",
    "полірувальна машинка": "Полірувальні машинки",
    "Акумуляторна полірувальна машина": "Акумуляторні полірувальні машинки",
    "Твердий віск": "Тверді воски",
    "Рідкий віск": "Рідкі воски",
    "Шерстяний круг": "Хутрові круги",
    "Засіб для": "Засоби для",
    "Антибітум": "Антибітумні засоби",
    "Антидощ": "Засоби антидощ",
    "Захисне покриття": "Захисні покриття",
}

MANUAL_PLURAL_RU = {
    "Очиститель": "Очистители",
    "Полироль": "Полироли",
    "Силант": "Силанты",
    "Обезжириватель": "Обезжириватели",
    "Пятновыводитель": "Пятновыводители",
    "Нейтрализатор": "Нейтрализаторы",
    "Губка": "Губки",
    "Ведро": "Вёдра",
    "Набор": "Наборы",
    "Воск": "Воски",
    "Шампунь": "Шампуни",
    "Щётка": "Щётки",
    "Торнадор": "Торнадоры",
    "Твёрдый воск": "Твёрдые воски",
    "Жидкий воск": "Жидкие воски",
    "Средство для": "Средства для",
    "Антибитум": "Антибитумные средства",
    "Антидождь": "Средства антидождь",
}

# Plural patterns for detection
PLURAL_PATTERNS_UK = [
    r"\bочищувачі\b",
    r"\bполіролі\b",
    r"\bсиланти\b",
    r"\bзнежирювачі\b",
    r"\bплямовивідники\b",
    r"\bпоглиначі\b",
    r"\bгубки\b",
    r"\bвідра\b",
    r"\bнабори\b",
    r"\bвоски\b",
    r"\bшампуні\b",
    r"\bщітки\b",
    r"\bмашинки\b",
    r"\bкруги\b",
    r"\bзасоби\b",
    r"\bторнадори\b",
    r"\bпасти\b",
    r"\bаксесуари\b",
    r"\bобладнання\b",
    r"\bпокриття\b",
    r"\bмашини\b",
]

PLURAL_PATTERNS_RU = [
    r"\bочистители\b",
    r"\bполироли\b",
    r"\bсиланты\b",
    r"\bобезжириватели\b",
    r"\bпятновыводители\b",
    r"\bнейтрализаторы\b",
    r"\bгубки\b",
    r"\bвёдра\b",
    r"\bнаборы\b",
    r"\bвоски\b",
    r"\bшампуни\b",
    r"\bщётки\b",
    r"\bмашинки\b",
    r"\bкруги\b",
    r"\bсредства\b",
    r"\bторнадоры\b",
    r"\bпасты\b",
    r"\bоборудование\b",
]


def is_plural(text: str, lang: str) -> bool:
    patterns = PLURAL_PATTERNS_UK if lang == "uk" else PLURAL_PATTERNS_RU
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


def find_plural_in_clean(clean_file: Path, lang: str) -> str | None:
    """Find plural keyword in _clean.json."""
    if not clean_file.exists():
        return None

    with open(clean_file) as f:
        data = json.load(f)

    keywords = data.get("keywords", [])
    if isinstance(keywords, dict):
        all_kw = []
        for group in ["primary", "secondary", "supporting", "commercial"]:
            all_kw.extend(keywords.get(group, []))
        keywords = all_kw

    for kw in keywords:
        keyword = kw.get("keyword", "")
        if is_plural(keyword, lang):
            # Capitalize first letter
            return keyword[0].upper() + keyword[1:] if keyword else keyword

    for syn in data.get("synonyms", []):
        keyword = syn.get("keyword", "")
        if is_plural(keyword, lang):
            return keyword[0].upper() + keyword[1:] if keyword else keyword

    return None


def pluralize_h1(h1: str, lang: str) -> str:
    """Convert singular H1 to plural using manual mapping."""
    mapping = MANUAL_PLURAL_UK if lang == "uk" else MANUAL_PLURAL_RU

    # Try longer patterns first (more specific)
    for singular, plural in sorted(mapping.items(), key=lambda x: -len(x[0])):
        if h1.startswith(singular):
            return h1.replace(singular, plural, 1)
        # Also check lowercase start
        if h1.lower().startswith(singular.lower()):
            return plural + h1[len(singular) :]

    return h1


def update_title(old_title: str, old_h1: str, new_h1: str) -> str:
    """Update title with new H1."""
    if old_h1 in old_title:
        return old_title.replace(old_h1, new_h1)
    # Handle case mismatch
    if old_h1.lower() in old_title.lower():
        idx = old_title.lower().find(old_h1.lower())
        return old_title[:idx] + new_h1 + old_title[idx + len(old_h1) :]
    return old_title


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["ru", "uk"], required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Error: specify --dry-run or --apply")
        return

    base_dir = Path("uk/categories") if args.lang == "uk" else Path("categories")

    changes = []
    skipped = []

    for meta_file in sorted(base_dir.glob("*/meta/*_meta.json")):
        slug = meta_file.parent.parent.name

        # Skip exceptions
        if slug in SKIP_SLUGS:
            skipped.append(slug)
            continue

        with open(meta_file) as f:
            meta = json.load(f)

        old_h1 = meta.get("h1", "")
        old_title = meta.get("meta", {}).get("title", "")

        # Skip if already plural
        if is_plural(old_h1, args.lang):
            skipped.append(f"{slug} (already plural)")
            continue

        # Try to find plural in semantics first
        clean_file = meta_file.parent.parent / "data" / f"{slug}_clean.json"
        new_h1 = find_plural_in_clean(clean_file, args.lang)

        # Fallback to manual mapping
        if not new_h1:
            new_h1 = pluralize_h1(old_h1, args.lang)

        # Skip if no change
        if new_h1 == old_h1:
            skipped.append(f"{slug} (no mapping)")
            continue

        new_title = update_title(old_title, old_h1, new_h1)

        changes.append(
            {
                "slug": slug,
                "file": str(meta_file),
                "old_h1": old_h1,
                "new_h1": new_h1,
                "old_title": old_title,
                "new_title": new_title,
            }
        )

        if args.apply:
            meta["h1"] = new_h1
            meta["meta"]["title"] = new_title
            with open(meta_file, "w") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
                f.write("\n")

    # Report
    mode = "DRY RUN" if args.dry_run else "APPLIED"
    print(f"\n{'=' * 60}")
    print(f"{mode}: {len(changes)} changes for {args.lang.upper()}")
    print(f"{'=' * 60}\n")

    for c in changes:
        print(f"{c['slug']}:")
        print(f"  H1: {c['old_h1']} → {c['new_h1']}")
        print()

    print(f"\nSkipped: {len(skipped)}")
    if args.dry_run:
        for s in skipped[:10]:
            print(f"  - {s}")
        if len(skipped) > 10:
            print(f"  ... and {len(skipped) - 10} more")


if __name__ == "__main__":
    main()
