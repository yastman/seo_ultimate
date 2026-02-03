# Plural Meta Fix — Manual Mapping Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Перевести H1 и Title всех категорий (RU + UK) из единственного числа во множественное с ручным контролем.

**Architecture:**
1. Создать JSON с полным ручным маппингом slug → new_h1 для UK и RU
2. Скрипт применяет маппинг к _meta.json
3. Сгенерировать SQL и залить на сервер

**Tech Stack:** Python 3, JSON, MySQL, SSH

---

## Task 1: Создать ручной маппинг UK

**Files:**
- Create: `data/generated/plural_manual_uk.json`

**Step 1: Создать JSON**

```json
{
  "akkumulyatornaya": "Акумуляторні полірувальні машинки",
  "aksessuary-dlya-naneseniya-sredstv": "Аплікатори та губки для нанесення",
  "antibitum": "Антибітумні засоби",
  "antidozhd": "Антидощ для скла",
  "antimoshka": "Очищувачі від комах",
  "apparaty-tornador": "Апарати Торнадор",
  "avtoshampuni": "Автошампуні",
  "gubki-i-varezhki": "Губки та рукавички для миття",
  "mekhovye": "Хутрові полірувальні круги",
  "nabory": "Набори для авто",
  "neytralizatory-zapakha": "Нейтралізатори запаху",
  "obezzhirivateli": "Знежирювачі для авто",
  "ochistiteli-diskov": "Очищувачі дисків",
  "ochistiteli-dvigatelya": "Очищувачі двигуна",
  "ochistiteli-kozhi": "Очищувачі шкіри",
  "ochistiteli-kuzova": "Очищувачі кузова",
  "ochistiteli-shin": "Очищувачі шин",
  "ochistiteli-stekol": "Очищувачі скла",
  "polirol-dlya-stekla": "Поліролі для скла",
  "poliroli-dlya-plastika": "Поліролі для пластику",
  "polirovalnye-mashinki": "Полірувальні машинки",
  "pyatnovyvoditeli": "Плямовивідники",
  "shampuni-dlya-ruchnoy-moyki": "Шампуні для ручного миття",
  "shchetka-dlya-moyki-avto": "Щітки для миття авто",
  "silanty": "Силанти для авто",
  "sredstva-dlya-kozhi": "Засоби для шкіри",
  "tverdyy-vosk": "Тверді воски",
  "ukhod-za-naruzhnym-plastikom": "Відновлювачі пластику",
  "vedra-i-emkosti": "Відра та ємності",
  "voski": "Воски для авто",
  "zhidkiy-vosk": "Рідкі воски"
}
```

**Step 2: Commit**

```bash
git add data/generated/plural_manual_uk.json
git commit -m "feat: add manual UK plural mapping"
```

---

## Task 2: Создать ручной маппинг RU

**Files:**
- Create: `data/generated/plural_manual_ru.json`

**Step 1: Получить список RU категорий**

```bash
for f in categories/*/meta/*_meta.json; do
  slug=$(basename $f _meta.json)
  h1=$(jq -r '.h1' "$f")
  echo "$slug | $h1"
done
```

**Step 2: Создать JSON** (аналогично UK, адаптировать для русского)

```json
{
  "akkumulyatornaya": "Аккумуляторные полировальные машинки",
  "aksessuary-dlya-naneseniya-sredstv": "Аппликаторы и губки для нанесения",
  "antibitum": "Антибитумные средства",
  "antidozhd": "Антидождь для стекол",
  "antimoshka": "Очистители от насекомых",
  "apparaty-tornador": "Аппараты Торнадор",
  "avtoshampuni": "Автошампуни",
  "gubki-i-varezhki": "Губки и варежки для мойки",
  "mekhovye": "Меховые полировальные круги",
  "nabory": "Наборы для авто",
  "neytralizatory-zapakha": "Нейтрализаторы запаха",
  "obezzhirivateli": "Обезжириватели для авто",
  "ochistiteli-diskov": "Очистители дисков",
  "ochistiteli-dvigatelya": "Очистители двигателя",
  "ochistiteli-kozhi": "Очистители кожи",
  "ochistiteli-kuzova": "Очистители кузова",
  "ochistiteli-shin": "Очистители шин",
  "ochistiteli-stekol": "Очистители стекол",
  "polirol-dlya-stekla": "Полироли для стекла",
  "poliroli-dlya-plastika": "Полироли для пластика",
  "polirovalnye-mashinki": "Полировальные машинки",
  "pyatnovyvoditeli": "Пятновыводители",
  "shampuni-dlya-ruchnoy-moyki": "Шампуни для ручной мойки",
  "shchetka-dlya-moyki-avto": "Щётки для мойки авто",
  "silanty": "Силанты для авто",
  "sredstva-dlya-kozhi": "Средства для кожи",
  "tverdyy-vosk": "Твёрдые воски",
  "ukhod-za-naruzhnym-plastikom": "Восстановители пластика",
  "vedra-i-emkosti": "Вёдра и ёмкости",
  "voski": "Воски для авто",
  "zhidkiy-vosk": "Жидкие воски"
}
```

**Step 3: Commit**

```bash
git add data/generated/plural_manual_ru.json
git commit -m "feat: add manual RU plural mapping"
```

---

## Task 3: Скрипт применения маппинга

**Files:**
- Create: `scripts/apply_manual_plural.py`

**Step 1: Написать скрипт**

```python
#!/usr/bin/env python3
"""
Apply manual plural mapping to _meta.json files.
Usage: python3 scripts/apply_manual_plural.py --lang uk --dry-run
       python3 scripts/apply_manual_plural.py --lang uk --apply
"""
import json
from pathlib import Path
import argparse


def load_mapping(lang: str) -> dict:
    mapping_file = Path(f'data/generated/plural_manual_{lang}.json')
    if not mapping_file.exists():
        return {}
    with open(mapping_file) as f:
        return json.load(f)


def update_title(old_title: str, old_h1: str, new_h1: str) -> str:
    """Update title: replace old H1 with new H1."""
    if old_h1 in old_title:
        return old_title.replace(old_h1, new_h1)
    # Case-insensitive replacement
    idx = old_title.lower().find(old_h1.lower())
    if idx >= 0:
        return old_title[:idx] + new_h1 + old_title[idx + len(old_h1):]
    # Fallback: replace beginning before dash
    if ' — ' in old_title:
        return new_h1 + ' — ' + old_title.split(' — ', 1)[1]
    return old_title


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', choices=['ru', 'uk'], required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Error: specify --dry-run or --apply")
        return

    mapping = load_mapping(args.lang)
    if not mapping:
        print(f"No mapping found for {args.lang}")
        return

    base_dir = Path('uk/categories') if args.lang == 'uk' else Path('categories')
    changes = []

    for meta_file in sorted(base_dir.glob('*/meta/*_meta.json')):
        slug = meta_file.parent.parent.name

        if slug not in mapping:
            continue

        with open(meta_file) as f:
            meta = json.load(f)

        old_h1 = meta.get('h1', '')
        new_h1 = mapping[slug]
        old_title = meta.get('meta', {}).get('title', '')
        new_title = update_title(old_title, old_h1, new_h1)

        changes.append({
            'slug': slug,
            'old_h1': old_h1,
            'new_h1': new_h1,
            'old_title': old_title,
            'new_title': new_title,
            'file': str(meta_file),
        })

        if args.apply:
            meta['h1'] = new_h1
            meta['meta']['title'] = new_title
            with open(meta_file, 'w') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
                f.write('\n')

    # Report
    mode = 'DRY RUN' if args.dry_run else 'APPLIED'
    print(f"\n{'='*60}")
    print(f"{mode}: {len(changes)} changes for {args.lang.upper()}")
    print(f"{'='*60}\n")

    for c in changes:
        print(f"{c['slug']}:")
        print(f"  H1: {c['old_h1']}")
        print(f"   →  {c['new_h1']}")
        print()


if __name__ == '__main__':
    main()
```

**Step 2: Commit**

```bash
git add scripts/apply_manual_plural.py
git commit -m "feat: add script to apply manual plural mapping"
```

---

## Task 4: Применить UK маппинг

**Step 1: Dry-run**

```bash
python3 scripts/apply_manual_plural.py --lang uk --dry-run
```

**Step 2: Apply**

```bash
python3 scripts/apply_manual_plural.py --lang uk --apply
```

**Step 3: Verify**

```bash
jq '.h1' uk/categories/ochistiteli-diskov/meta/ochistiteli-diskov_meta.json
# Expected: "Очищувачі дисків"
```

**Step 4: Commit**

```bash
git add uk/categories/
git commit -m "fix(uk-meta): convert H1/Title to plural (31 categories)"
```

---

## Task 5: Применить RU маппинг

**Step 1: Dry-run**

```bash
python3 scripts/apply_manual_plural.py --lang ru --dry-run
```

**Step 2: Apply**

```bash
python3 scripts/apply_manual_plural.py --lang ru --apply
```

**Step 3: Commit**

```bash
git add categories/
git commit -m "fix(ru-meta): convert H1/Title to plural"
```

---

## Task 6: Сгенерировать SQL

**Files:**
- Create: `data/generated/plural_meta_update.sql`

**Step 1: Генерация**

```bash
python3 -c "
import json
from pathlib import Path

mapping_file = Path('data/opencart_mapping.json')
with open(mapping_file) as f:
    mapping = json.load(f)
slug_to_id = mapping.get('slug_to_id', {})

sql = []

# UK (language_id=1)
for meta_file in Path('uk/categories').glob('*/meta/*_meta.json'):
    slug = meta_file.parent.parent.name
    cat_id = slug_to_id.get(slug)
    if not cat_id:
        continue
    with open(meta_file) as f:
        meta = json.load(f)
    h1 = meta.get('h1', '').replace(chr(39), chr(92)+chr(39))
    title = meta.get('meta', {}).get('title', '').replace(chr(39), chr(92)+chr(39))
    sql.append(f\"UPDATE oc_category_description SET meta_h1='{h1}', meta_title='{title}' WHERE category_id={cat_id} AND language_id=1;\")

# RU (language_id=3)
for meta_file in Path('categories').glob('*/meta/*_meta.json'):
    slug = meta_file.parent.parent.name
    cat_id = slug_to_id.get(slug)
    if not cat_id:
        continue
    with open(meta_file) as f:
        meta = json.load(f)
    h1 = meta.get('h1', '').replace(chr(39), chr(92)+chr(39))
    title = meta.get('meta', {}).get('title', '').replace(chr(39), chr(92)+chr(39))
    sql.append(f\"UPDATE oc_category_description SET meta_h1='{h1}', meta_title='{title}' WHERE category_id={cat_id} AND language_id=3;\")

print('\\n'.join(sql))
" > data/generated/plural_meta_update.sql
```

**Step 2: Review**

```bash
wc -l data/generated/plural_meta_update.sql
head -5 data/generated/plural_meta_update.sql
```

**Step 3: Commit**

```bash
git add data/generated/plural_meta_update.sql
git commit -m "feat: generate SQL for plural meta update"
```

---

## Task 7: Выполнить SQL на сервере

**Step 1: Upload**

```bash
scp data/generated/plural_meta_update.sql ult:/tmp/
```

**Step 2: Execute**

```bash
ssh ult "mysql yastman_test < /tmp/plural_meta_update.sql"
```

**Step 3: Clear cache**

```bash
ssh ult "rm -rf /home/yastman/web/ultimate.net.ua/public_html/system/storage/cache/*"
```

---

## Task 8: Валидация

**Step 1: Проверить UK на сервере**

```bash
ssh ult "mysql yastman_test -N -e \"SELECT category_id, meta_h1 FROM oc_category_description WHERE language_id=1 AND category_id IN (419,422,478,476) LIMIT 10;\""
```

**Step 2: Проверить RU на сервере**

```bash
ssh ult "mysql yastman_test -N -e \"SELECT category_id, meta_h1 FROM oc_category_description WHERE language_id=3 AND category_id IN (419,422,478,476) LIMIT 10;\""
```

**Step 3: Visual check**

- Открыть https://ultimate.net.ua/ochistiteli-diskov
- Проверить H1 страницы = "Очистители дисков"
- Открыть https://ultimate.net.ua/uk/ochistiteli-diskov
- Проверить H1 = "Очищувачі дисків"

---

## Checklist

- [ ] Task 1: plural_manual_uk.json создан
- [ ] Task 2: plural_manual_ru.json создан
- [ ] Task 3: apply_manual_plural.py создан
- [ ] Task 4: UK meta обновлены (31 файл)
- [ ] Task 5: RU meta обновлены
- [ ] Task 6: SQL сгенерирован
- [ ] Task 7: SQL выполнен на сервере
- [ ] Task 8: Валидация пройдена
