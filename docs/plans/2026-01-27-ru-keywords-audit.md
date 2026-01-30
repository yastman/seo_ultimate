# RU Keywords Audit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Найти неиспользуемые RU ключи из `ull_all_rus_keys.csv` и сгенерировать отчёт с рекомендациями по распределению.

**Architecture:** Python-скрипт читает CSV с ключами, собирает используемые ключи из всех `_clean.json`, находит разницу, классифицирует по паттернам и генерирует markdown-отчёт.

**Tech Stack:** Python 3, csv, json, glob, re, pathlib

---

## Task 1: Создать скрипт аудита ключей

**Files:**
- Create: `scripts/audit_unused_keywords.py`

**Step 1: Создать базовую структуру скрипта**

```python
#!/usr/bin/env python3
"""Аудит неиспользуемых RU ключей из ull_all_rus_keys.csv."""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import date


ROOT = Path(__file__).parent.parent
CSV_FILE = ROOT / "ull_all_rus_keys.csv"
CATEGORIES_DIR = ROOT / "categories"
REPORTS_DIR = ROOT / "reports"


def load_csv_keywords() -> dict[str, int]:
    """Загружает ключи из CSV, возвращает {keyword: volume}."""
    keywords = {}
    with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) >= 2 and row[0] and row[1]:
                keyword = row[0].strip().lower()
                # Пропускаем заголовки
                if keyword.startswith(("l1:", "l2:", "l3:", "seo-")):
                    continue
                try:
                    volume = int(row[1])
                    keywords[keyword] = volume
                except ValueError:
                    continue
    return keywords


def load_used_keywords() -> set[str]:
    """Собирает все ключи из categories/**/*_clean.json."""
    used = set()
    for filepath in CATEGORIES_DIR.rglob("*_clean.json"):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for kw in data.get("keywords", []):
                    if isinstance(kw, dict):
                        used.add(kw.get("keyword", "").lower())
                    else:
                        used.add(str(kw).lower())
                for syn in data.get("synonyms", []):
                    if isinstance(syn, dict):
                        used.add(syn.get("keyword", "").lower())
                    else:
                        used.add(str(syn).lower())
        except Exception as e:
            print(f"Ошибка в {filepath}: {e}")
    return used


# Паттерны для классификации
CATEGORY_PATTERNS = [
    # Главная страница
    (r"^автохимия$|^автокосметика$|интернет.?магазин|киев|украина|^детейлинг.?магазин|^детейлинг.?шоп|автохимия.?купить$|автокосметика.?купить$|для.?детейлинга$|автохимия.?и.?автокосметика|автокосметика.?профессиональная|профессиональная.?автохимия|автохимия.?каталог|автокосметика.?цен|автохимия.?цен", "glavnaya"),
    # Мойка
    (r"пена|бесконтакт", "aktivnaya-pena"),
    (r"шампунь.*(ручн|кислот)|автошампунь.*(ручн|кислот)|(ручн|кислот).*шампунь", "shampuni-dlya-ruchnoy-moyki"),
    (r"омыват|стеклоомыват", "omyvatel"),
    (r"антидожд|гидрофоб.*стекл", "antidozhd"),
    (r"очист.*стекл|стекло.*очист|мойка.*стекл|стекл.*мойк", "ochistiteli-stekol"),
    (r"полироль.*стекл|стекл.*полироль", "polirol-dlya-stekla"),
    (r"двигател|мотор", "ochistiteli-dvigatelya"),
    (r"обезжир", "obezzhirivateli"),
    (r"антибитум|битум|смол", "antibitum"),
    (r"мошк|насеком", "antimoshka"),
    (r"глин.*авто|авто.*глин|скраб", "glina-i-avtoskraby"),
    (r"пластик.*нар|бампер|молдинг|пластик.*кузов", "ukhod-za-naruzhnym-plastikom"),
    (r"диск.*очист|очист.*диск|колес.*очист|очист.*колес|мойка.*диск", "ochistiteli-diskov"),
    (r"черн.*шин|черн.*рез|блеск.*шин|шин.*блеск|чернител", "cherniteli-shin"),
    (r"очист.*шин|шин.*очист", "ochistiteli-shin"),
    (r"керамик.*диск|диск.*керамик", "keramika-dlya-diskov"),
    # Интерьер
    (r"химчист|салон.*чист|чист.*салон|ткан.*чист|чист.*ткан|потолок|велюр|алькантар", "sredstva-dlya-khimchistki-salona"),
    (r"пятн|выводит", "pyatnovyvoditeli"),
    (r"запах|нейтрализ|поглотит|одорант", "neytralizatory-zapakha"),
    (r"пластик.*салон|торпед|полироль.*пластик|пластик.*полироль|панел.*прибор", "poliroli-dlya-plastika"),
    (r"кож.*очист|очист.*кож|чист.*кож|кож.*чист", "ochistiteli-kozhi"),
    (r"кож.*уход|уход.*кож|кож.*крем|кондиц.*кож|кож.*кондиц|кож.*бальзам", "ukhod-za-kozhey"),
    (r"кож.*салон|салон.*кож|кожан", "sredstva-dlya-kozhi"),
    # Защитные покрытия
    (r"воск.*тверд|тверд.*воск|карнауб", "tverdyy-vosk"),
    (r"воск.*жидк|жидк.*воск", "zhidkiy-vosk"),
    (r"воск", "voski"),
    (r"силант|герметик.*кузов", "silanty"),
    (r"керамик|жидк.*стекл|нанокерамик|nano.*керамик", "keramika-i-zhidkoe-steklo"),
    (r"квик|детейлер|спрей.*воск|воск.*спрей|быстр.*блеск", "kvik-deteylery"),
    # Полировка
    (r"полиров.*паст|паст.*полиров|абразив.*паст", "polirovalnye-pasty"),
    (r"полиров.*машин|машин.*полиров|полировщик|полировальн", "polirovalnye-mashinki"),
    (r"аккумулятор.*полиров|полиров.*аккумулятор", "akkumulyatornaya"),
    (r"круг.*полир|полир.*круг|мехов", "mekhovye"),
    # Аксессуары
    (r"микрофибр|тряпк|салфетк|полотенц", "mikrofibra-i-tryapki"),
    (r"губк|варежк|мочалк", "gubki-i-varezhki"),
    (r"кист.*детейл|детейл.*кист|кисточ", "kisti-dlya-deteylinga"),
    (r"щетк.*мойк|мойк.*щетк|щетка.*авто", "shchetka-dlya-moyki-avto"),
    (r"распылит|триггер|пенник|пеногенератор|помпов", "raspyliteli-i-penniki"),
    (r"ведр|ёмкост|емкост", "vedra-i-emkosti"),
    (r"скотч|маляр.*лент", "malyarniy-skotch"),
    (r"набор", "nabory"),
    (r"торнадор", "apparaty-tornador"),
    # B2B
    (r"опт|b2b|производител|поставщик", "opt-i-b2b"),
]


def classify_keyword(keyword: str) -> str:
    """Определяет рекомендуемую категорию для ключа."""
    for pattern, category in CATEGORY_PATTERNS:
        if re.search(pattern, keyword, re.IGNORECASE):
            return category
    return "unknown"


def generate_report(unused: dict[str, int]) -> str:
    """Генерирует markdown-отчёт."""
    # Группируем по категориям
    by_category = defaultdict(list)
    for kw, vol in unused.items():
        cat = classify_keyword(kw)
        by_category[cat].append((kw, vol))

    # Сортируем внутри каждой категории по частотности
    for cat in by_category:
        by_category[cat].sort(key=lambda x: x[1], reverse=True)

    # Считаем статистику
    total_unused = len(unused)
    total_volume = sum(unused.values())

    lines = [
        "# Неиспользуемые RU ключи",
        "",
        f"**Дата:** {date.today()}",
        "",
        "## Сводка",
        "",
        f"- **Неиспользуемых ключей:** {total_unused}",
        f"- **Суммарная частотность:** {total_volume}",
        "",
    ]

    # Сначала glavnaya
    if "glavnaya" in by_category:
        lines.extend([
            "## Ключи для главной страницы (glavnaya)",
            "",
            "| Ключ | Частотность |",
            "|------|-------------|",
        ])
        for kw, vol in by_category["glavnaya"]:
            lines.append(f"| {kw} | {vol} |")
        lines.append("")
        del by_category["glavnaya"]

    # Потом unknown
    if "unknown" in by_category:
        unknown = by_category.pop("unknown")

    # Остальные категории
    if by_category:
        lines.extend([
            "## Ключи для существующих категорий",
            "",
        ])
        for cat in sorted(by_category.keys()):
            keywords = by_category[cat]
            lines.extend([
                f"### {cat}",
                "",
                "| Ключ | Частотность |",
                "|------|-------------|",
            ])
            for kw, vol in keywords:
                lines.append(f"| {kw} | {vol} |")
            lines.append("")

    # Unknown в конце
    if "unknown" in dir() and unknown:
        lines.extend([
            "## Ключи без очевидной категории",
            "",
            "| Ключ | Частотность |",
            "|------|-------------|",
        ])
        for kw, vol in unknown:
            lines.append(f"| {kw} | {vol} |")
        lines.append("")

    return "\n".join(lines)


def main():
    print("Загрузка ключей из CSV...")
    csv_keywords = load_csv_keywords()
    print(f"  Найдено: {len(csv_keywords)}")

    print("Загрузка используемых ключей из категорий...")
    used_keywords = load_used_keywords()
    print(f"  Используется: {len(used_keywords)}")

    print("Поиск неиспользуемых...")
    unused = {k: v for k, v in csv_keywords.items() if k not in used_keywords}
    print(f"  Не используется: {len(unused)}")

    print("Генерация отчёта...")
    report = generate_report(unused)

    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / f"{date.today()}-unused-ru-keywords.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Отчёт сохранён: {report_path}")


if __name__ == "__main__":
    main()
```

**Step 2: Запустить скрипт**

Run: `python scripts/audit_unused_keywords.py`
Expected: Создан файл `reports/2026-01-27-unused-ru-keywords.md`

**Step 3: Проверить отчёт**

Run: `head -50 reports/2026-01-27-unused-ru-keywords.md`
Expected: Видим сводку и таблицу ключей для glavnaya

**Step 4: Commit**

```bash
git add scripts/audit_unused_keywords.py reports/2026-01-27-unused-ru-keywords.md
git commit -m "feat: add RU keywords audit script and report"
```

---

## Task 2: Проверить результаты и скорректировать паттерны (если нужно)

**Files:**
- Modify: `scripts/audit_unused_keywords.py` (если паттерны неточные)
- Read: `reports/2026-01-27-unused-ru-keywords.md`

**Step 1: Проанализировать секцию "unknown"**

Если много ключей попало в "unknown" — добавить паттерны.

**Step 2: Проверить ключи для glavnaya**

Убедиться, что туда попали именно общие ключи (автохимия, автокосметика, интернет магазин), а не специфичные.

**Step 3: Перезапустить при необходимости**

Run: `python scripts/audit_unused_keywords.py`

**Step 4: Commit (если были изменения)**

```bash
git add scripts/audit_unused_keywords.py reports/2026-01-27-unused-ru-keywords.md
git commit -m "fix: improve keyword classification patterns"
```
