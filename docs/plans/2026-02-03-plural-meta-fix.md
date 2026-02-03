# Исправление числа в Meta (H1/Title) — RU + UK

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Перевести H1 и Title всех категорий в множественное число (категория = коллекция товаров).

**Architecture:**
1. Обновить _clean.json — добавить `plural_form` к primary keyword или найти existing plural keyword
2. Обновить _meta.json — Title и H1 во множественном числе
3. Залить на сервер — SQL update для RU (language_id=3) и UK (language_id=1)

**Tech Stack:** Python, JSON, SQL, SSH

---

## Анализ: какие категории требуют исправления

### UK категории с единственным числом (30 шт.):

| slug | Текущий H1 (ед.) | Нужно (мн.) |
|------|------------------|-------------|
| ochistiteli-diskov | Очищувач дисків | Очищувачі дисків |
| ochistiteli-dvigatelya | Очищувач двигуна | Очищувачі двигуна |
| ochistiteli-kozhi | Очищувач шкіри | Очищувачі шкіри |
| ochistiteli-kuzova | Очищувач кузова | Очищувачі кузова |
| ochistiteli-shin | Очищувач гуми | Очищувачі гуми |
| ochistiteli-stekol | Очищувач скла | Очищувачі скла |
| poliroli-dlya-plastika | Поліроль для пластику авто | Поліролі для пластику |
| polirol-dlya-stekla | Поліроль для скла | Поліролі для скла |
| silanty | Силант | Силанти для авто |
| obezzhirivateli | Знежирювач для авто | Знежирювачі для авто |
| pyatnovyvoditeli | Плямовивідник | Плямовивідники |
| neytralizatory-zapakha | Поглинач запахів | Поглиначі запахів |
| gubki-i-varezhki | Губка для авто | Губки та рукавички |
| vedra-i-emkosti | Відро для миття авто | Відра та ємності |
| nabory | Набір для миття авто | Набори для авто |
| voski | Віск для авто | Воски для авто |
| tverdyy-vosk | Твердий віск для авто | Тверді воски |
| zhidkiy-vosk | Рідкий віск для авто | Рідкі воски |
| avtoshampuni | Автошампунь | Автошампуні |
| shampuni-dlya-ruchnoy-moyki | Автошампунь для ручного миття | Шампуні для ручного миття |
| antimoshka | Очищувач слідів комах | Очищувачі слідів комах |
| antibitum | Антибітум | Антибітумні засоби |
| antidozhd | Антидощ | Засоби "Антидощ" |
| apparaty-tornador | Торнадор | Торнадори |
| shchetka-dlya-moyki-avto | Щітка для миття авто | Щітки для миття авто |
| mekhovye | Шерстяний круг для полірування | Хутрові та вовняні круги |
| akkumulyatornaya | Акумуляторна полірувальна машина | Акумуляторні полірувальні машини |
| polirovalnye-mashinki | полірувальна машинка для авто | Полірувальні машинки |
| sredstva-dlya-kozhi | Засіб для шкіри авто | Засоби для шкіри |
| aksessuary-dlya-naneseniya-sredstv | Губка для полірування автомобіля | Аксесуари для нанесення |

### RU категории (аналогичный список, ~30 шт.)

Применить ту же логику: единственное → множественное.

---

## Task 1: Создать маппинг единственное → множественное

**Files:**
- Create: `data/generated/plural_mapping.json`

**Step 1: Создать JSON с маппингом**

```json
{
  "uk": {
    "очищувач": "очищувачі",
    "поліроль": "поліролі",
    "силант": "силанти",
    "знежирювач": "знежирювачі",
    "плямовивідник": "плямовивідники",
    "поглинач": "поглиначі",
    "губка": "губки",
    "відро": "відра",
    "набір": "набори",
    "віск": "воски",
    "автошампунь": "автошампуні",
    "щітка": "щітки",
    "машина": "машини",
    "машинка": "машинки",
    "круг": "круги",
    "засіб": "засоби",
    "торнадор": "торнадори"
  },
  "ru": {
    "очиститель": "очистители",
    "полироль": "полироли",
    "силант": "силанты",
    "обезжириватель": "обезжириватели",
    "пятновыводитель": "пятновыводители",
    "нейтрализатор": "нейтрализаторы",
    "губка": "губки",
    "ведро": "вёдра",
    "набор": "наборы",
    "воск": "воски",
    "шампунь": "шампуни",
    "щётка": "щётки",
    "машина": "машины",
    "машинка": "машинки",
    "круг": "круги",
    "средство": "средства",
    "торнадор": "торнадоры"
  }
}
```

**Step 2: Commit**

```bash
git add data/generated/plural_mapping.json
git commit -m "feat: add singular-to-plural mapping for meta fix"
```

---

## Task 2: Скрипт для обновления _meta.json

**Files:**
- Create: `scripts/fix_plural_meta.py`

**Step 1: Написать скрипт**

```python
#!/usr/bin/env python3
"""
Fix singular H1/Title to plural in _meta.json files.
Usage: python3 scripts/fix_plural_meta.py --lang uk --dry-run
       python3 scripts/fix_plural_meta.py --lang uk --apply
"""
import json
import argparse
from pathlib import Path

PLURAL_MAP = {
    "uk": {
        # Primary word mappings (start of H1)
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
        # Adjective + noun patterns
        "Твердий віск": "Тверді воски",
        "Рідкий віск": "Рідкі воски",
        "Шерстяний круг": "Хутрові круги",
        "Акумуляторна полірувальна машина": "Акумуляторні машинки",
        "полірувальна машинка": "Полірувальні машинки",
        "Засіб для": "Засоби для",
    },
    "ru": {
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
    }
}

def pluralize_h1(h1: str, lang: str) -> str:
    """Convert singular H1 to plural."""
    mapping = PLURAL_MAP.get(lang, {})

    # Try longer patterns first
    for singular, plural in sorted(mapping.items(), key=lambda x: -len(x[0])):
        if h1.startswith(singular):
            return h1.replace(singular, plural, 1)

    return h1  # No change if no pattern matched

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["ru", "uk"], required=True)
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()

    if args.lang == "uk":
        base_dir = Path("uk/categories")
    else:
        base_dir = Path("categories")

    changes = []

    for meta_file in base_dir.glob("*/meta/*_meta.json"):
        with open(meta_file) as f:
            data = json.load(f)

        old_h1 = data.get("h1", "")
        new_h1 = pluralize_h1(old_h1, args.lang)

        if old_h1 != new_h1:
            changes.append({
                "file": str(meta_file),
                "slug": meta_file.parent.parent.name,
                "old_h1": old_h1,
                "new_h1": new_h1
            })

            if args.apply:
                data["h1"] = new_h1
                # Update title too
                old_title = data.get("meta", {}).get("title", "")
                new_title = old_title.replace(old_h1, new_h1)
                data["meta"]["title"] = new_title

                with open(meta_file, "w") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

    # Print report
    print(f"\n{'DRY RUN' if args.dry_run else 'APPLIED'}: {len(changes)} changes\n")
    for c in changes:
        print(f"{c['slug']}: {c['old_h1']} → {c['new_h1']}")

if __name__ == "__main__":
    main()
```

**Step 2: Run dry-run to verify**

```bash
python3 scripts/fix_plural_meta.py --lang uk --dry-run
```

Expected: List of ~30 changes

**Step 3: Commit script**

```bash
git add scripts/fix_plural_meta.py
git commit -m "feat: add script to fix singular meta to plural"
```

---

## Task 3: Применить исправления UK

**Files:**
- Modify: `uk/categories/*/meta/*_meta.json` (~30 files)

**Step 1: Apply changes**

```bash
python3 scripts/fix_plural_meta.py --lang uk --apply
```

**Step 2: Verify changes**

```bash
git diff uk/categories/*/meta/*.json | head -100
```

**Step 3: Commit**

```bash
git add uk/categories/
git commit -m "fix(uk-meta): convert H1/Title to plural form"
```

---

## Task 4: Применить исправления RU

**Files:**
- Modify: `categories/*/meta/*_meta.json`

**Step 1: Apply changes**

```bash
python3 scripts/fix_plural_meta.py --lang ru --apply
```

**Step 2: Verify**

```bash
git diff categories/*/meta/*.json | head -50
```

**Step 3: Commit**

```bash
git add categories/
git commit -m "fix(ru-meta): convert H1/Title to plural form"
```

---

## Task 5: Сгенерировать SQL для сервера

**Files:**
- Create: `data/generated/fix_plural_meta.sql`

**Step 1: Create SQL generator**

```bash
# Generate SQL from updated _meta.json files
python3 -c "
import json
from pathlib import Path

sql_lines = []

# UK categories (language_id=1)
for meta_file in Path('uk/categories').glob('*/meta/*_meta.json'):
    with open(meta_file) as f:
        data = json.load(f)
    slug = data.get('slug')
    h1 = data.get('h1', '').replace(\"'\", \"\\\\'\")
    title = data.get('meta', {}).get('title', '').replace(\"'\", \"\\\\'\")

    # Get category_id from mapping
    with open('data/opencart_mapping.json') as f:
        mapping = json.load(f)

    cat_id = mapping.get('slug_to_id', {}).get(slug)
    if cat_id:
        sql_lines.append(f\"UPDATE oc_category_description SET meta_h1='{h1}', meta_title='{title}' WHERE category_id={cat_id} AND language_id=1;\")

# RU categories (language_id=3)
for meta_file in Path('categories').glob('*/meta/*_meta.json'):
    with open(meta_file) as f:
        data = json.load(f)
    slug = data.get('slug')
    h1 = data.get('h1', '').replace(\"'\", \"\\\\'\")
    title = data.get('meta', {}).get('title', '').replace(\"'\", \"\\\\'\")

    with open('data/opencart_mapping.json') as f:
        mapping = json.load(f)

    cat_id = mapping.get('slug_to_id', {}).get(slug)
    if cat_id:
        sql_lines.append(f\"UPDATE oc_category_description SET meta_h1='{h1}', meta_title='{title}' WHERE category_id={cat_id} AND language_id=3;\")

print('\\n'.join(sql_lines))
" > data/generated/fix_plural_meta.sql
```

**Step 2: Review SQL**

```bash
head -20 data/generated/fix_plural_meta.sql
```

**Step 3: Commit**

```bash
git add data/generated/fix_plural_meta.sql
git commit -m "feat: generate SQL for plural meta fix"
```

---

## Task 6: Выполнить SQL на сервере

**Step 1: Upload SQL**

```bash
scp data/generated/fix_plural_meta.sql ult:/tmp/
```

**Step 2: Execute SQL**

```bash
ssh ult "mysql yastman_test < /tmp/fix_plural_meta.sql"
```

**Step 3: Verify**

```bash
ssh ult "mysql yastman_test -e \"SELECT category_id, meta_h1 FROM oc_category_description WHERE language_id=1 LIMIT 10;\""
```

---

## Task 7: Очистить кэш OpenCart

**Step 1: Clear cache**

```bash
ssh ult "rm -rf /home/yastman/web/ultimate.net.ua/public_html/system/storage/cache/*"
```

**Step 2: Verify on site**

Открыть категорию на сайте и проверить H1/Title.

---

## Исключения (НЕ менять)

Некоторые категории не требуют изменения (H1 уже корректный или это абстрактное понятие):

| slug | H1 | Причина |
|------|-----|---------|
| glavnaya | Автокосметика | Собирательное |
| polirovka | Полірування авто | Процесс, не товар |
| moyka-i-eksterer | Хімія для миття авто | Собирательное |
| ukhod-za-intererom | Хімчистка салону | Процесс |
| zashchitnye-pokrytiya | Захисні покриття | Уже множественное |
| keramika-i-zhidkoe-steklo | Кераміка для авто | Собирательное |
| aksessuary | Аксесуари | Уже множественное |
| oborudovanie | Обладнання | Уже множественное |

---

## Checklist

- [ ] Task 1: Создан plural_mapping.json
- [ ] Task 2: Скрипт fix_plural_meta.py работает
- [ ] Task 3: UK _meta.json обновлены
- [ ] Task 4: RU _meta.json обновлены
- [ ] Task 5: SQL файл сгенерирован
- [ ] Task 6: SQL выполнен на сервере
- [ ] Task 7: Кэш очищен, сайт проверен
