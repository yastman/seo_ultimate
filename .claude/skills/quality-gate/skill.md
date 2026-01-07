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
```

**Checks:**

- [ ] Has H1 (first line starts with #)
- [ ] Intro: 30-60 words
- [ ] Has comparison table
- [ ] Has how-to section with numbered steps
- [ ] Has FAQ (3-5 questions)
- [ ] Word count appropriate (300-800)
- [ ] No brand names/prices
- [ ] Primary keyword in first 100 words
- [ ] Secondary keywords used naturally

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

## Next Step

If PASS: `/deploy-to-opencart {slug}`
If FAIL: Fix issues, then run `/quality-gate {slug}` again

---

**Version:** 1.0 — December 2025
