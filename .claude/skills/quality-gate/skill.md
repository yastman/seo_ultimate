---
name: quality-gate
description: Use when you see /quality-gate, проверь категорию, финальная проверка, валидация перед деплоем. (project)
---

# Quality Gate

Final validation before deployment to OpenCart.

**Documentation:**

- [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md) — SEO Guide v20.0 (validation rules)
- [docs/RESEARCH_GUIDE.md](../../../docs/RESEARCH_GUIDE.md) — Research requirements

---

## Input Requirements

Before quality check, category must have:

```
Required for RU:
- [ ] categories/{slug}/data/{slug}_clean.json
- [ ] categories/{slug}/meta/{slug}_meta.json
- [ ] categories/{slug}/content/{slug}_ru.md
- [ ] categories/{slug}/research/RESEARCH_DATA.md

Required for UK (if bilingual):
- [ ] uk/categories/{slug}/data/{slug}_clean.json
- [ ] uk/categories/{slug}/meta/{slug}_meta.json
- [ ] uk/categories/{slug}/content/{slug}_uk.md
```

---

## Validation Checklist

### 1. Data Validation (_clean.json)

```bash
# Check JSON validity
python -c "import json; json.load(open('categories/{slug}/data/{slug}_clean.json'))"
```

**Checks:**

- [ ] Valid JSON
- [ ] Has primary keywords with volumes
- [ ] Keywords clustered (primary, secondary, supporting, commercial)
- [ ] Total keywords: 10-15

### 2. Meta Validation (_meta.json)

```bash
python scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json
```

**Checks:**

- [ ] Title: 50-60 characters
- [ ] Title: Contains "Купить/Купити"
- [ ] Title: Primary keyword at start
- [ ] Description: 120-160 characters
- [ ] Description: No emojis
- [ ] H1: No "Купить/Купити"
- [ ] H1 ≠ Title
- [ ] keywords_in_content synced with data

### 3. Content Validation (_ru.md /_uk.md)

```bash
python scripts/validate_content.py categories/{slug}/content/{slug}_ru.md
python scripts/check_keyword_density.py categories/{slug}/content/{slug}_ru.md
python scripts/check_water_natasha.py categories/{slug}/content/{slug}_ru.md
```

**Checks:**

- [ ] Has H1 (first line starts with #)
- [ ] H1 = `name` из _clean.json (множественное число)
- [ ] Intro: 30-60 words (buyer guide, НЕ определение "X — это...")
- [ ] Has comparison table (3 колонки: Задача → Тип → Почему)
- [ ] Has "Если X → Y" patterns (≥3 шт)
- [ ] Has FAQ (3-5 questions, не дублируют таблицы)
- [ ] **НЕТ how-to секций** (BLOCKER!)
- [ ] Word count appropriate (400-700)
- [ ] No brand names/prices
- [ ] Primary keyword in first 100 words
- [ ] Secondary keywords used naturally
- [ ] Stem-группа ≤2.5% (BLOCKER >3.0%)
- [ ] Классическая тошнота ≤3.5 (BLOCKER >4.0)
- [ ] **Academic ≥7%** (WARNING <7%)
- [ ] Вода 40-65% (WARNING >75%)

> **Примечание:** entities в _clean.json автогенерированные — НЕ использовать для контента. Профтермины берутся из RESEARCH_DATA.md.

### 4. SEO Structure Check

```bash
python scripts/check_seo_structure.py categories/{slug}/content/{slug}_ru.md
```

**Checks:**

- [ ] H1 exists and matches meta
- [ ] H2 structure logical
- [ ] Tables formatted correctly
- [ ] Lists have proper formatting

### 5. Translation Check (UK only)

**Checks:**

- [ ] резина → гума (not резина)
- [ ] мойка → миття/мийка
- [ ] стекло → скло
- [ ] Commercial keywords marked meta_only
- [ ] No mixed RU/UK in same file

---

## Workflow

### Step 1: Run All Validations

```bash
# Full category analysis
python scripts/analyze_category.py {slug}

# Meta validation
python scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json

# Content validation
python scripts/validate_content.py categories/{slug}/content/{slug}_ru.md
```

### Step 2: Generate Report

```markdown
# Quality Gate Report: {slug}

**Date:** {YYYY-MM-DD}
**Status:** PASS / FAIL

## RU Version

| Check | Status | Details |
|-------|--------|---------|
| Data JSON | ✅/❌ | {details} |
| Meta tags | ✅/❌ | Title: X chars, Desc: Y chars |
| Content | ✅/❌ | X words, Y keywords |
| SEO Structure | ✅/❌ | {details} |

## UK Version

| Check | Status | Details |
|-------|--------|---------|
| Data JSON | ✅/❌ | {details} |
| Meta tags | ✅/❌ | Title: X chars, Desc: Y chars |
| Content | ✅/❌ | X words, Y keywords |
| Translation | ✅/❌ | {details} |

## Issues Found

1. {Issue 1}
2. {Issue 2}

## Recommendations

- {Recommendation}

## Decision

**PASS** — Ready for /deploy-to-opencart
**FAIL** — Fix issues above first
```

### Step 3: Save Report

Save to `categories/{slug}/QUALITY_REPORT.md`

---

## Pass Criteria

**PASS** requires ALL of:

| Criterion | RU | UK |
|-----------|----|----|
| Data valid | ✅ | ✅ |
| Title 50-60 chars | ✅ | ✅ |
| Title has commercial | ✅ | ✅ |
| Description 120-160 | ✅ | ✅ |
| H1 no commercial | ✅ | ✅ |
| Content structured | ✅ | ✅ |
| No brands/prices | ✅ | ✅ |

**FAIL** if ANY check fails.

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Title too long | Shorten, use abbreviations |
| Title missing "Купить" | Add commercial modifier |
| H1 has "Купить" | Remove commercial from H1 |
| Description > 160 | Shorten, remove redundant info |
| Missing FAQ | Add 3-5 FAQ questions |
| резина not гума (UK) | Fix translation |

---

## Output

```
categories/{slug}/QUALITY_REPORT.md

Status: PASS → ready for /deploy-to-opencart
Status: FAIL → fix issues first
```

---

## UK Support (--lang uk)

При вызове с `--lang uk` (например: `/quality-gate aktivnaya-pena --lang uk`):

### UK Paths

```
uk/categories/{slug}/
├── data/{slug}_clean.json      # UK ключі з частотністю
├── meta/{slug}_meta.json       # UK мета-теги
└── content/{slug}_uk.md        # UK контент
```

### UK Validation Commands

```bash
# Meta validation
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json

# Content validation
python3 scripts/validate_content.py uk/categories/{slug}/content/{slug}_uk.md "{primary_uk}" --mode seo

# Keyword density
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md
```

### UK-Specific Checks

| Check | Rule | Detection |
|-------|------|-----------|
| Title contains "Купити" | BLOCKER | Grep for "Купити" in title |
| H1 does NOT contain "Купити" | BLOCKER | H1 should be clean keyword |
| резина → гума | BLOCKER | Search for "резина" (should be 0 matches) |
| мойка → миття | BLOCKER | Search for "мойка" (should be 0 matches) |
| стекло → скло | BLOCKER | Search for "стекло" (should be 0 matches) |
| чернитель → чорнитель | WARNING | Search for "чернитель" |
| очиститель → очищувач | WARNING | Search for "очиститель" |

### UK Terminology Validation

```bash
# Check for RU terms that should be UK
grep -c "резина" uk/categories/{slug}/content/{slug}_uk.md  # Should be 0
grep -c "мойка" uk/categories/{slug}/content/{slug}_uk.md   # Should be 0
grep -c "стекло" uk/categories/{slug}/content/{slug}_uk.md  # Should be 0
```

### UK Meta Rules

| Field | UK Rule | Example |
|-------|---------|---------|
| Title | "Купити" ОБОВ'ЯЗКОВО | "Купити активну піну в Україні \| Ultimate" |
| Title length | 50-60 chars | |
| Description | 100-160 chars | "{keyword} від виробника Ultimate. {types}. Опт і роздріб." |
| H1 | БЕЗ "Купити" | "Активна піна" |

### UK Pass Criteria

**PASS** requires ALL of:

| Criterion | Required |
|-----------|----------|
| Data valid JSON | ✅ |
| Title 50-60 chars | ✅ |
| Title contains "Купити" | ✅ |
| Description 100-160 | ✅ |
| H1 no "Купити" | ✅ |
| No "резина" (use "гума") | ✅ |
| No "мойка" (use "миття") | ✅ |
| No "стекло" (use "скло") | ✅ |
| UK keywords integrated | ✅ |

---

## Next Step

If PASS: `/deploy-to-opencart {slug}` or `/deploy-to-opencart {slug} --lang uk`
If FAIL: Fix issues, then run `/quality-gate {slug}` again

---

**Version:** 3.0 — January 2026

**Changelog v3.0:**
- REMOVED: "Has how-to section" (how-to секции запрещены в buyer guide)
- ADDED: check_keyword_density.py и check_water_natasha.py в валидацию
- ADDED: Academic ≥7% (WARNING <7%)
- ADDED: Stem-группа ≤2.5%, тошнота ≤3.5
- ADDED: Примечание про entities (не использовать, профтермины из RESEARCH_DATA.md)
- ADDED: Паттерны "Если X → Y" (≥3 шт)
- UPDATED: Word count 400-700 (было 300-800)

**Changelog v2.0:**
- Added full UK support with `--lang uk` flag
- UK-specific terminology checks (резина→гума, мойка→миття, стекло→скло)
- UK meta rules (Купити in Title, not in H1)
- UK validation commands and paths
