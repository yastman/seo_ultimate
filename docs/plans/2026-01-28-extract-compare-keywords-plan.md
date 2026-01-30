# Extract & Compare Keywords Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать два скрипта для извлечения всех ключей из категорий и сравнения с master CSV.

**Architecture:** Скрипт extract парсит все _clean.json и создаёт единый CSV. Скрипт compare загружает оба CSV, нормализует ключи и генерирует markdown-отчёт с расхождениями.

**Tech Stack:** Python 3, pathlib, csv, json. Без внешних зависимостей.

**Design:** `docs/plans/2026-01-28-extract-compare-keywords-design.md`

---

## Task 1: Создать extract_all_keywords.py

**Files:**
- Create: `scripts/extract_all_keywords.py`

**Step 1: Создать скрипт**

```python
#!/usr/bin/env python3
"""Извлечение всех ключей из _clean.json категорий."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT / "categories"
OUTPUT_FILE = ROOT / "data" / "generated" / "all_from_categories.csv"


def extract_from_file(clean_file: Path) -> list[dict]:
    """Извлекает все ключи из одного _clean.json файла."""
    rows = []
    try:
        data = json.loads(clean_file.read_text(encoding="utf-8"))
        category = data.get("id", clean_file.stem.replace("_clean", ""))

        # Keywords
        for kw in data.get("keywords", []):
            rows.append({
                "keyword": kw["keyword"],
                "volume": kw.get("volume", 0),
                "category": category,
                "source_type": "keyword",
            })

        # Synonyms
        for syn in data.get("synonyms", []):
            rows.append({
                "keyword": syn["keyword"],
                "volume": syn.get("volume", 0),
                "category": category,
                "source_type": "synonym",
            })

        # Variations
        for var in data.get("variations", []):
            rows.append({
                "keyword": var["keyword"],
                "volume": var.get("volume", 0),
                "category": category,
                "source_type": "variation",
            })

    except Exception as e:
        print(f"⚠️  {clean_file.name}: {e}")

    return rows


def main():
    all_rows = []

    for clean_file in sorted(CATEGORIES_DIR.rglob("*_clean.json")):
        rows = extract_from_file(clean_file)
        all_rows.extend(rows)
        if not rows:
            print(f"⚠️  {clean_file.name}: пустой файл")

    # Save CSV
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["keyword", "volume", "category", "source_type"])
        writer.writeheader()
        writer.writerows(all_rows)

    # Stats
    keywords_count = sum(1 for r in all_rows if r["source_type"] == "keyword")
    synonyms_count = sum(1 for r in all_rows if r["source_type"] == "synonym")
    variations_count = sum(1 for r in all_rows if r["source_type"] == "variation")
    categories_count = len(set(r["category"] for r in all_rows))

    print(f"✅ Извлечено {len(all_rows)} записей → {OUTPUT_FILE}")
    print(f"   keywords: {keywords_count}, synonyms: {synonyms_count}, variations: {variations_count}")
    print(f"   категорий: {categories_count}")


if __name__ == "__main__":
    main()
```

**Step 2: Запустить и проверить**

```bash
python3 scripts/extract_all_keywords.py
```

Expected: CSV создан в `data/generated/all_from_categories.csv`

**Step 3: Проверить результат**

```bash
head -20 data/generated/all_from_categories.csv
wc -l data/generated/all_from_categories.csv
```

---

## Task 2: Создать compare_with_master.py

**Files:**
- Create: `scripts/compare_with_master.py`

**Step 1: Создать скрипт**

```python
#!/usr/bin/env python3
"""Сравнение ключей из категорий с master CSV."""

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
CATEGORIES_CSV = ROOT / "data" / "generated" / "all_from_categories.csv"
MASTER_CSV = ROOT / "data" / "ru_semantics_master.csv"
OUTPUT_FILE = ROOT / "data" / "generated" / "comparison_report.md"


def normalize(keyword: str) -> str:
    """Нормализует ключ для сравнения."""
    return " ".join(keyword.lower().strip().split())


def load_categories_csv(path: Path) -> dict:
    """Загружает CSV из категорий. Возвращает dict[normalized] = list of records."""
    data = defaultdict(list)
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["volume"] = int(row["volume"])
            key = normalize(row["keyword"])
            data[key].append(row)
    return dict(data)


def load_master_csv(path: Path) -> dict:
    """Загружает master CSV. Возвращает dict[normalized] = list of records."""
    data = defaultdict(list)
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["volume"] = int(row["volume"])
            key = normalize(row["keyword"])
            data[key].append(row)
    return dict(data)


def generate_report(cat_data: dict, master_data: dict) -> str:
    """Генерирует markdown-отчёт сравнения."""
    cat_keys = set(cat_data.keys())
    master_keys = set(master_data.keys())

    only_in_cat = cat_keys - master_keys
    only_in_master = master_keys - cat_keys
    in_both = cat_keys & master_keys

    lines = []
    lines.append("# Сравнение ключей: Категории vs Master")
    lines.append("")
    lines.append("## Статистика")
    lines.append(f"- Уникальных ключей в категориях: {len(cat_keys)}")
    lines.append(f"- Уникальных ключей в master: {len(master_keys)}")
    lines.append(f"- Совпадений: {len(in_both)}")
    lines.append(f"- Только в категориях: {len(only_in_cat)}")
    lines.append(f"- Только в master: {len(only_in_master)}")
    lines.append("")

    # Only in categories
    lines.append("## Только в категориях (добавить в master?)")
    lines.append("")
    if only_in_cat:
        lines.append("| keyword | volume | category | type |")
        lines.append("|---------|--------|----------|------|")
        for key in sorted(only_in_cat):
            for rec in cat_data[key]:
                lines.append(f"| {rec['keyword']} | {rec['volume']} | {rec['category']} | {rec['source_type']} |")
    else:
        lines.append("Нет расхождений.")
    lines.append("")

    # Only in master
    lines.append("## Только в master (не в категориях)")
    lines.append("")
    if only_in_master:
        lines.append("| keyword | volume | category | type |")
        lines.append("|---------|--------|----------|------|")
        for key in sorted(only_in_master):
            for rec in master_data[key]:
                lines.append(f"| {rec['keyword']} | {rec['volume']} | {rec['category']} | {rec['type']} |")
    else:
        lines.append("Нет расхождений.")
    lines.append("")

    # Volume differences
    lines.append("## Разная частотность")
    lines.append("")
    volume_diffs = []
    for key in in_both:
        cat_recs = cat_data[key]
        master_recs = master_data[key]
        # Compare by category
        for cat_rec in cat_recs:
            for master_rec in master_recs:
                if cat_rec["category"] == master_rec["category"]:
                    if cat_rec["volume"] != master_rec["volume"]:
                        diff = cat_rec["volume"] - master_rec["volume"]
                        volume_diffs.append({
                            "keyword": cat_rec["keyword"],
                            "category": cat_rec["category"],
                            "vol_cat": cat_rec["volume"],
                            "vol_master": master_rec["volume"],
                            "diff": diff,
                        })

    if volume_diffs:
        lines.append("| keyword | category | vol_cat | vol_master | diff |")
        lines.append("|---------|----------|---------|------------|------|")
        for d in sorted(volume_diffs, key=lambda x: abs(x["diff"]), reverse=True):
            sign = "+" if d["diff"] > 0 else ""
            lines.append(f"| {d['keyword']} | {d['category']} | {d['vol_cat']} | {d['vol_master']} | {sign}{d['diff']} |")
    else:
        lines.append("Нет расхождений.")
    lines.append("")

    # Duplicates within categories
    lines.append("## Дубли внутри категорий")
    lines.append("")
    lines.append("Ключи которые есть в keywords И synonyms одной категории:")
    lines.append("")
    duplicates = []
    for key, recs in cat_data.items():
        by_cat = defaultdict(list)
        for rec in recs:
            by_cat[rec["category"]].append(rec)
        for cat, cat_recs in by_cat.items():
            types = set(r["source_type"] for r in cat_recs)
            if len(types) > 1:
                duplicates.append({
                    "keyword": cat_recs[0]["keyword"],
                    "category": cat,
                    "types": ", ".join(sorted(types)),
                })

    if duplicates:
        lines.append("| keyword | category | types |")
        lines.append("|---------|----------|-------|")
        for d in sorted(duplicates, key=lambda x: x["keyword"]):
            lines.append(f"| {d['keyword']} | {d['category']} | {d['types']} |")
    else:
        lines.append("Нет дублей.")
    lines.append("")

    return "\n".join(lines)


def main():
    if not CATEGORIES_CSV.exists():
        print(f"❌ Сначала запустите extract_all_keywords.py")
        print(f"   Ожидается: {CATEGORIES_CSV}")
        return

    print(f"Loading {CATEGORIES_CSV}...")
    cat_data = load_categories_csv(CATEGORIES_CSV)
    print(f"  {len(cat_data)} уникальных ключей")

    print(f"Loading {MASTER_CSV}...")
    master_data = load_master_csv(MASTER_CSV)
    print(f"  {len(master_data)} уникальных ключей")

    print("Generating report...")
    report = generate_report(cat_data, master_data)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(report, encoding="utf-8")

    print(f"✅ Отчёт сохранён → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
```

**Step 2: Запустить и проверить**

```bash
python3 scripts/compare_with_master.py
```

Expected: Отчёт создан в `data/generated/comparison_report.md`

**Step 3: Просмотреть отчёт**

```bash
cat data/generated/comparison_report.md
```

---

## Task 3: Валидация и коммит

**Step 1: Проверить линтером**

```bash
ruff check scripts/extract_all_keywords.py scripts/compare_with_master.py
ruff format scripts/extract_all_keywords.py scripts/compare_with_master.py
```

**Step 2: Коммит**

```bash
git add scripts/extract_all_keywords.py scripts/compare_with_master.py
git add data/generated/all_from_categories.csv data/generated/comparison_report.md
git commit -m "feat: add extract and compare keywords scripts"
```

---

## Checklist

- [ ] Task 1: extract_all_keywords.py создан и работает
- [ ] Task 2: compare_with_master.py создан и работает
- [ ] Task 3: Линтинг пройден, закоммичено
