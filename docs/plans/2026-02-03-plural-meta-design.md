# Plural Meta Fix — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Перевести H1 и Title всех категорий (RU + UK) из единственного числа во множественное.

**Architecture:**
1. Найти plural-форму в существующей семантике `_clean.json` (keywords/synonyms)
2. Если нет — использовать морфологический fallback (pymorphy2)
3. Обновить `_meta.json` локально
4. Залить изменения на сервер через SQL

**Tech Stack:** Python 3, pymorphy2, JSON, MySQL, SSH

---

## Анализ данных

### Текущее состояние UK (примеры)

| slug | H1 (ед.ч.) | В _clean.json есть мн.ч.? |
|------|-----------|---------------------------|
| ochistiteli-diskov | Очищувач дисків | Нет |
| silanty | Силант | Да: "силанти для авто" (40) |
| voski | Віск для авто | Нет |
| avtoshampuni | Автошампунь | Нет |
| gubki-i-varezhki | Губка для авто | Нет |

### Стратегия выбора plural-формы

```
1. Искать в _clean.json → keywords[] форму во мн.ч.
2. Если нет — искать в synonyms[]
3. Если нет — pymorphy2 fallback для первого слова H1
4. Капитализировать первую букву
```

### Категории-исключения (не менять)

| slug | H1 | Причина |
|------|-----|---------|
| glavnaya | Автокосметика | Собирательное |
| polirovka | Полірування авто | Процесс |
| ukhod-za-intererom | Хімчистка салону | Процесс |
| aksessuary | Аксесуари | Уже мн.ч. |
| oborudovanie | Обладнання | Уже мн.ч. |
| zashchitnye-pokrytiya | Захисні покриття | Уже мн.ч. |
| sredstva-dlya-khimchistki-salona | Засоби для хімчистки | Уже мн.ч. |

---

## Task 1: Создать список исключений

**Files:**
- Create: `data/generated/plural_exceptions.json`

**Step 1: Создать JSON с исключениями**

```json
{
  "skip_slugs": [
    "glavnaya",
    "polirovka",
    "ukhod-za-intererom",
    "aksessuary",
    "oborudovanie",
    "zashchitnye-pokrytiya",
    "sredstva-dlya-khimchistki-salona",
    "keramika-i-zhidkoe-steklo",
    "moyka-i-eksterer",
    "opt-i-b2b",
    "cherniteli-shin",
    "kisti-dlya-deteylinga",
    "ukhod-za-kozhey",
    "mikrofibra-i-tryapki",
    "raspyliteli-i-penniki",
    "polirovalnye-krugi",
    "polirovalnye-pasty",
    "glina-i-avtoskraby",
    "aktivnaya-pena",
    "malyarniy-skotch",
    "kvik-deteylery"
  ],
  "reason": "Already plural, collective noun, or process name"
}
```

**Step 2: Commit**

```bash
git add data/generated/plural_exceptions.json
git commit -m "feat: add plural conversion exceptions list"
```

---

## Task 2: Скрипт поиска plural в семантике

**Files:**
- Create: `scripts/find_plural_in_semantics.py`

**Step 1: Написать скрипт**

```python
#!/usr/bin/env python3
"""
Find plural forms in _clean.json semantics.
Usage: python3 scripts/find_plural_in_semantics.py --lang uk
"""
import json
import re
from pathlib import Path
import argparse

# Patterns for plural detection (UK)
PLURAL_PATTERNS_UK = [
    r'\bочищувачі\b', r'\bполіролі\b', r'\bсиланти\b', r'\bзнежирювачі\b',
    r'\bплямовивідники\b', r'\bпоглиначі\b', r'\bгубки\b', r'\bвідра\b',
    r'\bнабори\b', r'\bвоски\b', r'\bшампуні\b', r'\bщітки\b', r'\bмашинки\b',
    r'\bмашини\b', r'\bкруги\b', r'\bзасоби\b', r'\bторнадори\b', r'\bпасти\b',
    r'\bаксесуари\b', r'\bрозпилювачі\b', r'\bвідновлювачі\b', r'\bомивачі\b',
]

PLURAL_PATTERNS_RU = [
    r'\bочистители\b', r'\bполироли\b', r'\bсиланты\b', r'\bобезжириватели\b',
    r'\bпятновыводители\b', r'\bнейтрализаторы\b', r'\bгубки\b', r'\bвёдра\b',
    r'\bнаборы\b', r'\bвоски\b', r'\bшампуни\b', r'\bщётки\b', r'\bмашинки\b',
    r'\bмашины\b', r'\bкруги\b', r'\bсредства\b', r'\bторнадоры\b', r'\bпасты\b',
]


def is_plural(text: str, lang: str) -> bool:
    """Check if text contains plural form."""
    patterns = PLURAL_PATTERNS_UK if lang == 'uk' else PLURAL_PATTERNS_RU
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


def find_plural_keyword(clean_data: dict, lang: str) -> str | None:
    """Find plural keyword in semantics."""
    # Check keywords array
    keywords = clean_data.get('keywords', [])
    if isinstance(keywords, dict):
        # New format: {"primary": [...], "secondary": [...]}
        all_kw = []
        for group in ['primary', 'secondary', 'supporting', 'commercial']:
            all_kw.extend(keywords.get(group, []))
        keywords = all_kw

    for kw in keywords:
        keyword = kw.get('keyword', '')
        if is_plural(keyword, lang):
            return keyword

    # Check synonyms
    for syn in clean_data.get('synonyms', []):
        keyword = syn.get('keyword', '')
        if is_plural(keyword, lang):
            return keyword

    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', choices=['ru', 'uk'], required=True)
    args = parser.parse_args()

    base_dir = Path('uk/categories') if args.lang == 'uk' else Path('categories')

    results = []

    for clean_file in sorted(base_dir.glob('*/data/*_clean.json')):
        slug = clean_file.parent.parent.name

        with open(clean_file) as f:
            data = json.load(f)

        # Get current H1 from meta
        meta_file = clean_file.parent.parent / 'meta' / f'{slug}_meta.json'
        current_h1 = ''
        if meta_file.exists():
            with open(meta_file) as f:
                meta = json.load(f)
                current_h1 = meta.get('h1', '')

        # Find plural in semantics
        plural_kw = find_plural_keyword(data, args.lang)

        results.append({
            'slug': slug,
            'current_h1': current_h1,
            'plural_found': plural_kw,
            'needs_fallback': plural_kw is None and not is_plural(current_h1, args.lang)
        })

    # Print report
    print(f"\n{'='*60}")
    print(f"PLURAL ANALYSIS - {args.lang.upper()}")
    print(f"{'='*60}\n")

    found = [r for r in results if r['plural_found']]
    needs_fb = [r for r in results if r['needs_fallback']]
    already_ok = [r for r in results if not r['needs_fallback'] and not r['plural_found']]

    print(f"Found plural in semantics: {len(found)}")
    for r in found:
        print(f"  {r['slug']}: {r['current_h1']} → {r['plural_found']}")

    print(f"\nNeeds fallback (no plural found): {len(needs_fb)}")
    for r in needs_fb:
        print(f"  {r['slug']}: {r['current_h1']}")

    print(f"\nAlready OK (plural or excluded): {len(already_ok)}")


if __name__ == '__main__':
    main()
```

**Step 2: Run analysis**

```bash
python3 scripts/find_plural_in_semantics.py --lang uk
```

Expected: Report showing which categories have plural in semantics vs need fallback.

**Step 3: Commit**

```bash
git add scripts/find_plural_in_semantics.py
git commit -m "feat: add script to find plural forms in semantics"
```

---

## Task 3: Скрипт применения plural к meta

**Files:**
- Create: `scripts/apply_plural_meta.py`

**Step 1: Написать скрипт**

```python
#!/usr/bin/env python3
"""
Apply plural forms to _meta.json files.
Usage: python3 scripts/apply_plural_meta.py --lang uk --dry-run
       python3 scripts/apply_plural_meta.py --lang uk --apply
"""
import json
import re
from pathlib import Path
import argparse

try:
    import pymorphy2
    MORPH_UK = pymorphy2.MorphAnalyzer(lang='uk')
    MORPH_RU = pymorphy2.MorphAnalyzer()
except ImportError:
    MORPH_UK = None
    MORPH_RU = None

# Load exceptions
EXCEPTIONS_FILE = Path('data/generated/plural_exceptions.json')
SKIP_SLUGS = []
if EXCEPTIONS_FILE.exists():
    with open(EXCEPTIONS_FILE) as f:
        SKIP_SLUGS = json.load(f).get('skip_slugs', [])

# Plural patterns for detection
PLURAL_PATTERNS_UK = [
    r'\bочищувачі\b', r'\bполіролі\b', r'\bсиланти\b', r'\bзнежирювачі\b',
    r'\bплямовивідники\b', r'\bпоглиначі\b', r'\bгубки\b', r'\bвідра\b',
    r'\bнабори\b', r'\bвоски\b', r'\bшампуні\b', r'\bщітки\b', r'\bмашинки\b',
    r'\bкруги\b', r'\bзасоби\b', r'\bторнадори\b', r'\bпасти\b', r'\bаксесуари\b',
]

PLURAL_PATTERNS_RU = [
    r'\bочистители\b', r'\bполироли\b', r'\bсиланты\b', r'\bобезжириватели\b',
    r'\bпятновыводители\b', r'\bнейтрализаторы\b', r'\bгубки\b', r'\bвёдра\b',
    r'\bнаборы\b', r'\bвоски\b', r'\bшампуни\b', r'\bщётки\b', r'\bмашинки\b',
    r'\bкруги\b', r'\bсредства\b', r'\bторнадоры\b', r'\bпасты\b',
]


def is_plural(text: str, lang: str) -> bool:
    patterns = PLURAL_PATTERNS_UK if lang == 'uk' else PLURAL_PATTERNS_RU
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


def find_plural_in_clean(clean_file: Path, lang: str) -> str | None:
    """Find plural keyword in _clean.json."""
    if not clean_file.exists():
        return None

    with open(clean_file) as f:
        data = json.load(f)

    keywords = data.get('keywords', [])
    if isinstance(keywords, dict):
        all_kw = []
        for group in ['primary', 'secondary', 'supporting', 'commercial']:
            all_kw.extend(keywords.get(group, []))
        keywords = all_kw

    for kw in keywords:
        keyword = kw.get('keyword', '')
        if is_plural(keyword, lang):
            return keyword.capitalize()

    for syn in data.get('synonyms', []):
        keyword = syn.get('keyword', '')
        if is_plural(keyword, lang):
            return keyword.capitalize()

    return None


def pluralize_first_word(h1: str, lang: str) -> str:
    """Pluralize first word using pymorphy2."""
    morph = MORPH_UK if lang == 'uk' else MORPH_RU
    if not morph:
        return h1  # No morphology available

    words = h1.split()
    if not words:
        return h1

    first_word = words[0]
    parsed = morph.parse(first_word)[0]

    # Try to inflect to plural nominative
    plural_form = parsed.inflect({'plur', 'nomn'})
    if plural_form:
        words[0] = plural_form.word.capitalize()
        return ' '.join(words)

    return h1


def update_title(old_title: str, old_h1: str, new_h1: str) -> str:
    """Update title with new H1."""
    # Title format: "[H1] — купити, ціни | Ultimate"
    if old_h1 in old_title:
        return old_title.replace(old_h1, new_h1)
    # Fallback: replace start of title
    return re.sub(r'^[^—]+', new_h1 + ' ', old_title)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', choices=['ru', 'uk'], required=True)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()

    if not args.dry_run and not args.apply:
        print("Error: specify --dry-run or --apply")
        return

    base_dir = Path('uk/categories') if args.lang == 'uk' else Path('categories')

    changes = []

    for meta_file in sorted(base_dir.glob('*/meta/*_meta.json')):
        slug = meta_file.parent.parent.name

        # Skip exceptions
        if slug in SKIP_SLUGS:
            continue

        with open(meta_file) as f:
            meta = json.load(f)

        old_h1 = meta.get('h1', '')
        old_title = meta.get('meta', {}).get('title', '')

        # Skip if already plural
        if is_plural(old_h1, args.lang):
            continue

        # Find plural in semantics
        clean_file = meta_file.parent.parent / 'data' / f'{slug}_clean.json'
        new_h1 = find_plural_in_clean(clean_file, args.lang)

        # Fallback to morphology
        if not new_h1:
            new_h1 = pluralize_first_word(old_h1, args.lang)

        # Skip if no change
        if new_h1 == old_h1:
            continue

        new_title = update_title(old_title, old_h1, new_h1)

        changes.append({
            'slug': slug,
            'file': str(meta_file),
            'old_h1': old_h1,
            'new_h1': new_h1,
            'old_title': old_title,
            'new_title': new_title,
        })

        if args.apply:
            meta['h1'] = new_h1
            meta['meta']['title'] = new_title
            with open(meta_file, 'w') as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
                f.write('\n')

    # Report
    mode = 'DRY RUN' if args.dry_run else 'APPLIED'
    print(f"\n{mode}: {len(changes)} changes\n")

    for c in changes:
        print(f"{c['slug']}:")
        print(f"  H1: {c['old_h1']} → {c['new_h1']}")
        print(f"  Title: {c['old_title'][:50]}...")
        print()


if __name__ == '__main__':
    main()
```

**Step 2: Test dry-run**

```bash
python3 scripts/apply_plural_meta.py --lang uk --dry-run
```

Expected: List of ~30 changes with old → new H1.

**Step 3: Commit**

```bash
git add scripts/apply_plural_meta.py
git commit -m "feat: add script to apply plural forms to meta"
```

---

## Task 4: Применить UK исправления

**Files:**
- Modify: `uk/categories/*/meta/*_meta.json` (~30 files)

**Step 1: Apply**

```bash
python3 scripts/apply_plural_meta.py --lang uk --apply
```

**Step 2: Verify sample**

```bash
cat uk/categories/ochistiteli-diskov/meta/ochistiteli-diskov_meta.json | jq '.h1'
# Expected: "Очищувачі дисків"
```

**Step 3: Commit**

```bash
git add uk/categories/
git commit -m "fix(uk-meta): convert H1/Title to plural form

- ochistiteli-* → Очищувачі
- silanty → Силанти
- gubki → Губки
- ~30 categories updated"
```

---

## Task 5: Применить RU исправления

**Files:**
- Modify: `categories/*/meta/*_meta.json`

**Step 1: Apply**

```bash
python3 scripts/apply_plural_meta.py --lang ru --apply
```

**Step 2: Verify**

```bash
git diff categories/*/meta/*.json | head -30
```

**Step 3: Commit**

```bash
git add categories/
git commit -m "fix(ru-meta): convert H1/Title to plural form"
```

---

## Task 6: Генерация SQL для сервера

**Files:**
- Create: `data/generated/plural_meta_update.sql`

**Step 1: Создать SQL генератор**

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

    h1 = meta.get('h1', '').replace(\"'\", \"\\\\'\")
    title = meta.get('meta', {}).get('title', '').replace(\"'\", \"\\\\'\")

    sql.append(f\"UPDATE oc_category_description SET meta_h1='{h1}', meta_title='{title}' WHERE category_id={cat_id} AND language_id=1;\")

# RU (language_id=3)
for meta_file in Path('categories').glob('*/meta/*_meta.json'):
    slug = meta_file.parent.parent.name
    cat_id = slug_to_id.get(slug)
    if not cat_id:
        continue

    with open(meta_file) as f:
        meta = json.load(f)

    h1 = meta.get('h1', '').replace(\"'\", \"\\\\'\")
    title = meta.get('meta', {}).get('title', '').replace(\"'\", \"\\\\'\")

    sql.append(f\"UPDATE oc_category_description SET meta_h1='{h1}', meta_title='{title}' WHERE category_id={cat_id} AND language_id=3;\")

print('\\n'.join(sql))
" > data/generated/plural_meta_update.sql
```

**Step 2: Review SQL**

```bash
wc -l data/generated/plural_meta_update.sql
head -10 data/generated/plural_meta_update.sql
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

**Step 3: Verify**

```bash
ssh ult "mysql yastman_test -N -e \"SELECT category_id, meta_h1 FROM oc_category_description WHERE language_id=1 AND category_id IN (419,422,478) LIMIT 5;\""
```

Expected: Plural forms in meta_h1.

---

## Task 8: Очистить кэш и проверить

**Step 1: Clear cache**

```bash
ssh ult "rm -rf /home/yastman/web/ultimate.net.ua/public_html/system/storage/cache/*"
```

**Step 2: Visual check**

Открыть в браузере:
- https://ultimate.net.ua/ochistiteli-diskov
- https://ultimate.net.ua/uk/ochistiteli-diskov

Проверить H1 и Title страницы.

---

## Checklist

- [ ] Task 1: plural_exceptions.json создан
- [ ] Task 2: find_plural_in_semantics.py работает
- [ ] Task 3: apply_plural_meta.py работает
- [ ] Task 4: UK meta обновлены (~30 файлов)
- [ ] Task 5: RU meta обновлены
- [ ] Task 6: SQL сгенерирован
- [ ] Task 7: SQL выполнен на сервере
- [ ] Task 8: Кэш очищен, сайт проверен
