# UK Full Cycle Design Plan

> **Goal:** Повний цикл мета + контент + валідація для всіх 50 UK категорій через скіли.

**Дата:** 2026-01-26
**Режим:** Ручний (через скіли)
**Послідовність:** Full cycle per category

---

## Поточний стан

| Статус | Кількість | Опис |
|--------|-----------|------|
| PASS | 17 | Готові до деплою |
| WARNING | 3 | Потребують minor fixes |
| FAIL | 19 | H2 keyword missing |
| NO_KEYWORDS | 13 | Всі ключі в supporting (volume < 100) |
| **Total** | **52** | UK категорій |

### Проблема NO_KEYWORDS

13 категорій мають ключі в `uk_keywords.json`, але скрипт `update_uk_clean_json.py` записав їх у `supporting_keywords` (volume < 100), а `keywords` пустий.

**Рішення:** Перед генерацією мета/контенту — ручна валідація та перенос найвищого keyword в primary.

---

## Workflow per Category

```
┌─────────────────────────────────────────────────────────────────┐
│                    FULL CYCLE PER CATEGORY                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 0: RU Comparison (ручна валідація)                        │
│    └── Порівняти UK з RU категорією                             │
│                                                                 │
│  Step 1: /uk-generate-meta {slug}                               │
│    └── Title, Description, H1                                   │
│                                                                 │
│  Step 2: Validate Meta                                          │
│    └── validate_meta.py + ручна перевірка                       │
│                                                                 │
│  Step 3: /uk-content-generator {slug}                           │
│    └── Buyer guide 500-700 слів                                 │
│                                                                 │
│  Step 4: uk-content-reviewer {slug}                             │
│    └── Ревізія + виправлення                                    │
│                                                                 │
│  Step 5: /uk-quality-gate {slug}                                │
│    └── Фінальна валідація                                       │
│                                                                 │
│  Step 6: Commit                                                 │
│    └── git add + commit                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 0: RU Comparison (НОВИЙ)

**Мета:** Переконатися що UK категорія відповідає RU перед генерацією.

### Checklist

| # | Перевірка | Як | Severity |
|---|-----------|-----|----------|
| 1 | **Keywords mapping** | UK keywords ⊆ RU keywords (source_ru) | BLOCKER |
| 2 | **Primary keyword** | Є хоча б 1 keyword в `keywords` або `secondary_keywords` | BLOCKER |
| 3 | **Content parity** | RU контент існує і покриває теми | WARNING |
| 4 | **Meta consistency** | RU meta існує для reference | WARNING |

### Команди

```bash
# 1. Порівняти UK vs RU keywords
cat uk/categories/{slug}/data/{slug}_clean.json | jq '.keywords + .secondary_keywords + .supporting_keywords | .[].source_ru'
cat categories/{slug}/data/{slug}_clean.json | jq '.keywords[].keyword'

# 2. Перевірити чи є primary
python3 -c "
import json
d = json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))
kws = d.get('keywords', []) + d.get('secondary_keywords', [])
print('Primary/Secondary:', len(kws))
if not kws:
    print('⚠️  NO PRIMARY — треба перенести з supporting!')
    sup = d.get('supporting_keywords', [])
    if sup:
        print(f'Найвищий supporting: {sup[0][\"keyword\"]} (vol: {sup[0].get(\"volume\", 0)})')
"

# 3. Перевірити RU контент
ls categories/{slug}/content/{slug}_ru.md

# 4. Перевірити RU meta
cat categories/{slug}/meta/{slug}_meta.json | jq '.h1, .meta.title'
```

### Fix NO_KEYWORDS

Якщо `keywords` пустий — вручну відредагувати `_clean.json`:

```bash
# Перенести найвищий supporting → keywords
# Edit uk/categories/{slug}/data/{slug}_clean.json
```

---

## Step 1: /uk-generate-meta {slug}

**Скіл:** `uk-generate-meta`
**Input:** `uk/categories/{slug}/data/{slug}_clean.json`
**Output:** `uk/categories/{slug}/meta/{slug}_meta.json`

### Правила

| Поле | Правило |
|------|---------|
| Title | 50-60 chars, "Купити" обов'язково |
| Description | 120-160 chars, "від виробника Ultimate" або "в інтернет-магазині" |
| H1 | = primary_keyword, БЕЗ "Купити" |

### Виклик

```
/uk-generate-meta {slug}
```

---

## Step 2: Validate Meta

**Команди:**

```bash
# Автоматична валідація
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json

# Ручна перевірка
cat uk/categories/{slug}/meta/{slug}_meta.json | jq '.'
```

### Checklist

- [ ] Title 50-60 chars
- [ ] Title містить "Купити"
- [ ] Description 120-160 chars
- [ ] H1 = primary_keyword
- [ ] H1 БЕЗ "Купити"
- [ ] **RU parity:** H1 логічно відповідає RU H1

---

## Step 3: /uk-content-generator {slug}

**Скіл:** `uk-content-generator`
**Input:** `_clean.json` + `_meta.json` + `research/*.md`
**Output:** `uk/categories/{slug}/content/{slug}_uk.md`

### Правила

| Параметр | Значення |
|----------|----------|
| Word count | 500-700 |
| H2 з keyword | мінімум 2 |
| Патерни "Якщо X → Y" | мінімум 3 |
| Academic | ≥7% |
| Stem density | ≤2.5% |

### Виклик

```
/uk-content-generator {slug}
```

---

## Step 4: uk-content-reviewer {slug}

**Агент:** `uk-content-reviewer`
**Режим:** Автономний (знаходить і виправляє проблеми)

### Що перевіряє

| Категорія | Перевірки |
|-----------|-----------|
| SEO | H2 keywords, intro, density |
| UK термінологія | гума (не резина), миття (не мойка), скло (не стекло) |
| Commercial intent | Buyer guide, не how-to |
| Research | Типи з Блок 2, факти |
| Dryness | Academic ≥7%, звертання |

### Виклик

```
uk-content-reviewer {slug}
```

### RU Parity Check (ручний)

Після review — порівняти з RU контентом:

```bash
# Теми покриті?
head -50 categories/{slug}/content/{slug}_ru.md
head -50 uk/categories/{slug}/content/{slug}_uk.md

# Таблиці аналогічні?
grep -A5 "^|" categories/{slug}/content/{slug}_ru.md | head -20
grep -A5 "^|" uk/categories/{slug}/content/{slug}_uk.md | head -20
```

---

## Step 5: /uk-quality-gate {slug}

**Скіл:** `uk-quality-gate`
**Output:** `uk/categories/{slug}/QUALITY_REPORT.md`

### Валідації

```bash
# JSON validity
python3 -c "import json; json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))"

# Meta
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json

# Content + SEO
python3 scripts/validate_content.py uk/categories/{slug}/content/{slug}_uk.md "{primary}" --mode seo
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary}"
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

# UK terminology
grep -E "резина|мойка|стекло" uk/categories/{slug}/content/{slug}_uk.md
```

### Pass Criteria

| Критерій | Вимога |
|----------|--------|
| Title | 50-60 chars, "Купити" |
| Description | 120-160 chars |
| H1 | БЕЗ "Купити" |
| Word count | 500-700 |
| H2 з keyword | ≥2 |
| Academic | ≥7% |
| Stem | ≤2.5% |
| UK terms | No резина/мойка/стекло |
| **RU parity** | Keywords + topics match |

### Виклик

```
/uk-quality-gate {slug}
```

---

## Step 6: Commit

```bash
git add uk/categories/{slug}/
git commit -m "feat(uk): {slug} — meta + content + quality-gate"
```

---

## Порядок обробки категорій

### Група 1: FAIL (19) — виправити H2 keywords

Вже є контент, потрібно тільки review + fix:

```
akkumulyatornaya, aksessuary-dlya-naneseniya-sredstv, antimoshka,
cherniteli-shin, gubki-i-varezhki, keramika-i-zhidkoe-steklo,
kisti-dlya-deteylinga, kvik-deteylery, malyarniy-skotch,
neytralizatory-zapakha, ochistiteli-stekol, omyvatel,
poliroli-dlya-plastika, polirovalnye-pasty, raspyliteli-i-penniki,
shampuni-dlya-ruchnoy-moyki, sredstva-dlya-khimchistki-salona,
tverdyy-vosk, ukhod-za-intererom
```

**Workflow:** Step 0 → Step 4 (reviewer) → Step 5 → Step 6

### Група 2: WARNING (3) — minor fixes

```
aktivnaya-pena, mikrofibra-i-tryapki, voski
```

**Workflow:** Step 0 → Step 4 (reviewer) → Step 5 → Step 6

### Група 3: NO_KEYWORDS (13) — fix _clean.json first

```
aksessuary, antibitum, keramika-dlya-diskov, mekhovye,
oborudovanie, ochistiteli-diskov, ochistiteli-kozhi,
ochistiteli-shin, opt-i-b2b, silanty,
ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, zashchitnye-pokrytiya
```

**Workflow:** Fix _clean.json → Step 0 → Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6

### Група 4: Решта (17) — PASS, verify only

```
antidozhd, apparaty-tornador, avtoshampuni, glina-i-avtoskraby,
moyka-i-eksterer, nabory, obezzhirivateli, ochistiteli-dvigatelya,
ochistiteli-kuzova, polirol-dlya-stekla, polirovalnye-mashinki,
polirovka, pyatnovyvoditeli, shchetka-dlya-moyki-avto,
sredstva-dlya-kozhi, ukhod-za-kozhey, zhidkiy-vosk
```

**Workflow:** Step 0 (RU parity check) → Step 5 (verify) → Step 6 (if changes)

---

## Tracking

Оновлювати `tasks/TODO_UK_CONTENT.md` після кожної категорії:

```markdown
- [x] {slug} — full cycle done (2026-01-XX)
```

---

## Summary

| Етап | Скіл/Команда | Що робить |
|------|--------------|-----------|
| 0 | Ручна валідація | RU ↔ UK parity check |
| 1 | `/uk-generate-meta` | Title, Desc, H1 |
| 2 | `validate_meta.py` | Перевірка мета |
| 3 | `/uk-content-generator` | Buyer guide контент |
| 4 | `uk-content-reviewer` | Ревізія + fix |
| 5 | `/uk-quality-gate` | Фінальна валідація |
| 6 | `git commit` | Збереження |

**Estimated:** 50 категорій × 6 steps = 300 операцій

---

**Version:** 1.0
