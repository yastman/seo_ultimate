---
name: uk-quality-gate
description: >-
  Фінальна валідація UK категорії перед деплоєм. Перевіряє дані, мета, контент, термінологію.
  Use when /uk-quality-gate, перевір UK категорію, фінальна перевірка UK, валідація UK перед деплоєм.
---

# UK Quality Gate v3.0

Фінальна валідація перед деплоєм в OpenCart (language_id=1).

**Документація:**

- [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md) — SEO Guide v20.0 (правила валідації)
- [docs/RESEARCH_GUIDE.md](../../../docs/RESEARCH_GUIDE.md) — Вимоги до research

---

## Input Requirements

```
uk/categories/{slug}/
├── data/{slug}_clean.json      # UK ключі з частотністю
├── meta/{slug}_meta.json       # UK мета-теги
├── content/{slug}_uk.md        # UK контент
└── research/RESEARCH_DATA.md   # Research дані
```

---

## Validation Checklist

### 1. Data Validation (_clean.json)

```bash
python3 -c "import json; json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))"
```

**Перевірки:**

- [ ] Valid JSON
- [ ] Has primary keywords with volumes
- [ ] Keywords clustered (primary, secondary, supporting, commercial)
- [ ] Total keywords: 10-15

### 2. Meta Validation (_meta.json)

```bash
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
```

**Перевірки:**

| Поле | Правило | BLOCKER |
|------|---------|---------|
| Title | 50-60 chars | ✅ |
| Title | Містить "Купити" | ✅ |
| Title | Primary keyword на початку | ✅ |
| Description | 120-160 chars | ✅ |
| Description | Без emojis | ✅ |
| H1 | БЕЗ "Купити" | ✅ |
| H1 | ≠ Title | ✅ |
| keywords_in_content | synced with data | ✅ |

### 3. Content Validation (_uk.md)

```bash
python3 scripts/validate_content.py uk/categories/{slug}/content/{slug}_uk.md "{primary_uk}" --mode seo
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md
```

**Перевірки:**

- [ ] Has H1 (перший рядок починається з #)
- [ ] H1 = `name` з _clean.json (множина)
- [ ] Intro: 30-60 слів (buyer guide, НЕ визначення "X — це...")
- [ ] Has comparison table (3 колонки: Задача → Тип → Чому)
- [ ] Has "Якщо X → Y" patterns (≥3 шт)
- [ ] Has FAQ (3-5 питань, не дублюють таблиці)
- [ ] **НЕТ how-to секцій** (BLOCKER!)
- [ ] Word count: 400-700
- [ ] No brand names/prices
- [ ] Primary keyword у перших 100 словах
- [ ] Secondary keywords used naturally
- [ ] Stem-група ≤2.5% (BLOCKER >3.0%)
- [ ] Класична тошнота ≤3.5 (BLOCKER >4.0)
- [ ] **Academic ≥7%** (WARNING <7%)
- [ ] Вода 40-65% (WARNING >75%)

> **Примітка:** entities в _clean.json автогенеровані — НЕ використовувати для контенту. Профтерміни беруться з RESEARCH_DATA.md.

### 4. SEO Structure Check

```bash
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary_uk}"
```

**Перевірки:**

| Перевірка | Правило | BLOCKER |
|-----------|---------|---------|
| Keyword в INTRO | Перші 150 символів | ✅ |
| H2 з keyword | Мінімум 2 H2 | ⚠️ WARN |
| Keyword frequency | 3-7 разів (не >10 SPAM) | ✅ |
| H1 exists | Matches meta | ✅ |
| Tables formatted | Correctly | ✅ |
| Lists formatted | Properly | ✅ |

### 5. UK Terminology Check (BLOCKER)

```bash
# Перевірка RU термінів, яких НЕ повинно бути
grep -c "резина" uk/categories/{slug}/content/{slug}_uk.md  # Має бути 0
grep -c "мойка" uk/categories/{slug}/content/{slug}_uk.md   # Має бути 0
grep -c "стекло" uk/categories/{slug}/content/{slug}_uk.md  # Має бути 0
```

| RU термін | UK термін | Статус |
|-----------|-----------|--------|
| резина | гума | BLOCKER |
| мойка | миття | BLOCKER |
| стекло | скло | BLOCKER |
| чернитель | чорнитель | WARNING |
| очиститель | очищувач | WARNING |
| покрытие | покриття | WARNING |
| поверхность | поверхня | WARNING |
| защита | захист | WARNING |
| блеск | блиск | WARNING |
| нанесение | нанесення | WARNING |
| чистка | чищення | WARNING |

### 6. Keyword Density

```bash
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
```

**Пороги:**

| Метрика | Ціль | BLOCKER |
|---------|------|---------|
| Stem-група ключа | ≤2.5% | >3.0% |
| Класична тошнота | ≤3.5 | >4.0 |

### 7. Academic Nausea Check

```bash
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md
```

**Пороги:**

| Метрика | Ціль | BLOCKER |
|---------|------|---------|
| Академічна тошнота | **≥7%** | <6% = сухий текст |
| Класична тошнота | ≤3.5 | >4.0 |
| Вода | 40-65% | >75% |

---

## Workflow

### Step 1: Run All Validations

```bash
# JSON validity
python3 -c "import json; json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))"

# Meta validation
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json

# Content validation
python3 scripts/validate_content.py uk/categories/{slug}/content/{slug}_uk.md "{primary_uk}" --mode seo

# SEO structure
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary_uk}"

# Academic nausea
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md

# UK terminology
grep -E "резина|мойка|стекло" uk/categories/{slug}/content/{slug}_uk.md

# Keyword density
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

# H1 sync check
python3 scripts/check_h1_sync.py --lang uk

# Semantic coverage check
python3 scripts/check_semantic_coverage.py --lang uk
```

### Step 2: Generate Report

```markdown
# UK Quality Gate Report: {slug}

**Дата:** {YYYY-MM-DD}
**Статус:** PASS / FAIL

## Validation Results

| Перевірка | Статус | Деталі |
|-----------|--------|--------|
| Data JSON | ✅/❌ | {details} |
| Meta tags | ✅/❌ | Title: X chars, Desc: Y chars |
| Content | ✅/❌ | X words, Y keywords |
| UK Terminology | ✅/❌ | No RU terms found / Found: резина, мойка |
| Keyword Density | ✅/❌ | Stem: X%, Nausea: Y |
| SEO Structure | ✅/❌ | H2 with keyword: X, Intro keyword: ✅/❌ |
| Academic Nausea | ✅/❌ | Academic: X%, Water: Y% |

## Issues Found

1. {Issue 1}
2. {Issue 2}

## Recommendations

- {Recommendation}

## Decision

**PASS** — Ready for /uk-deploy {slug}
**FAIL** — Виправити помилки вище
```

### Step 3: Save Report

```bash
# Save to category folder
uk/categories/{slug}/QUALITY_REPORT.md
```

---

## Pass Criteria

**PASS** вимагає ВСІ:

| Критерій | Обов'язково |
|----------|-------------|
| Data valid JSON | ✅ |
| Title 50-60 chars | ✅ |
| Title містить "Купити" | ✅ |
| Description 120-160 | ✅ |
| H1 БЕЗ "Купити" | ✅ |
| H1 ≠ Title | ✅ |
| Немає "резина" (use "гума") | ✅ |
| Немає "мойка" (use "миття") | ✅ |
| Немає "стекло" (use "скло") | ✅ |
| Content structured | ✅ |
| No brands/prices | ✅ |
| UK keywords integrated | ✅ |
| Stem ≤2.5% | ✅ |
| H2 з keyword мін. 2 | ✅ |
| Патерни "Якщо X→Y" ≥3 | ✅ |
| Academic ≥7% | ⚠️ |
| Word count 400-700 | ✅ |

---

## Common Issues

| Проблема | Рішення |
|----------|---------|
| Title too long | Скоротити, використати абревіатури |
| Title missing "Купити" | Додати комерційний модифікатор |
| H1 has "Купити" | Видалити комерційне з H1 |
| Description > 160 | Скоротити, прибрати зайве |
| Missing FAQ | Додати 3-5 FAQ питань |
| Found "резина" | Замінити на "гума" |
| Found "мойка" | Замінити на "миття" |
| Found "стекло" | Замінити на "скло" |
| Stem >2.5% | Розбавити синонімами |
| Word count >700 | Скоротити до 500-700 слів |
| H2 без keyword | Додати secondary keyword в 2+ H2 |
| Academic <7% | Додати звернення "вам", "якщо ви" |
| Немає "Якщо X→Y" | Додати 3+ сценарії вибору |

---

## Output

```
uk/categories/{slug}/QUALITY_REPORT.md

Status: PASS → ready for /uk-deploy {slug}
Status: FAIL → fix issues first
```

---

## Next Step

```
If PASS: /uk-deploy {slug}
If FAIL: Fix issues, then run /uk-quality-gate {slug} again
```

---

**Version:** 3.0 — January 2026

**Changelog v3.0:**
- **Синхронізовано з RU v3.0** — повний паритет
- ADDED: Посилання на docs/CONTENT_GUIDE.md та RESEARCH_GUIDE.md
- ADDED: keywords_in_content synced with data check
- ADDED: Примітка про entities (не використовувати, профтерміни з RESEARCH_DATA.md)
- ADDED: Розширена таблиця термінології (блиск, нанесення, чищення)
- ADDED: Більше деталей у Common Issues

**Changelog v2.1:**
- Added `--lang uk` to check_keyword_density.py calls
- Added check_h1_sync.py --lang uk validation
- Added check_semantic_coverage.py --lang uk validation

**Changelog v2.0:**
- Додано check_seo_structure.py валідацію
- Додано H2 keyword check (мін. 2)
- Додано Academic ≥7% вимогу
- Description length: 120-160 (було 100-160)
- Додано "Якщо X→Y" patterns check (≥3)
- Word count: 400-700 (було 300-800)
