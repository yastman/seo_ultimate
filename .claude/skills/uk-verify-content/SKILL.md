---
name: uk-verify-content
description: >-
  Інтерактивна верифікація UK контенту категорії перед продакшеном.
  Use when /uk-verify-content {slug}, перевір UK контент, верифікуй UK текст, UK pre-production QA.
  Відрізняється від uk-content-reviewer інтерактивністю — людина контролює кожен крок і вирішує що виправляти.
---

# UK Verify Content

Інтерактивна перевірка UK контенту категорії з контролем людини на кожному кроці.

## Input

```
/uk-verify-content {slug}
/uk-verify-content aktivnaya-pena
```

## Data Files

```
uk/categories/{slug}/
├── content/{slug}_uk.md        # Контент для перевірки
├── research/RESEARCH_DATA.md   # Джерело істини (або CONTEXT.md → RU)
├── meta/{slug}_meta.json       # Keywords для перевірки
└── data/{slug}_clean.json      # name (для H1)
```

---

## Workflow

### Phase 1: Load & Overview

1. Read all 4 files in parallel
2. Show summary:

```
## Overview: {slug}

**Type:** Hub Page / Product Page (parent_id = null → Hub)
**Content:** X words, Y sections (H2)
**Primary keywords:** keyword1, keyword2
**Research:** RESEARCH_DATA.md / CONTEXT.md → RU
```

---

### Phase 2: Run Validators

```bash
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary}"
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md
```

**Output:**

```
## Validators

| Validator | Status | Details |
|-----------|--------|---------|
| Meta | ✅/❌ | Title: X chars, Desc: Y chars |
| SEO Structure | ✅/❌ | H2 keywords: X, Intro: ✅/❌ |
| Density | ✅/⚠️/❌ | Stem: X% (≤2.5%) |
| Nausea | ✅/⚠️/❌ | Classic: X, Academic: Y%, Water: Z% |

⚠️ Found issues. Continue to details? [Y/n]
```

---

### Phase 3: UK Terminology Check (BLOCKER)

```bash
grep -E "резина|мойка|стекло" uk/categories/{slug}/content/{slug}_uk.md
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

**Output:**

```
## UK Terminology

✅ No RU terms found
— OR —
❌ Found RU terms:
- Line 15: "резина" → замінити на "гума"
- Line 42: "мойка" → замінити на "миття"

Fix terminology now? [Y/n]
```

---

### Phase 4: Facts Verification

**Extract concrete claims:**
- Numbers: %, time, sizes, pH, temperatures
- Comparisons: "X краще ніж Y"
- Technical facts

**Check in RESEARCH_DATA.md:**
- ✅ VERIFIED — found in research
- ⚠️ UNVERIFIED — not in research
- ❌ CONTRADICTION — conflicts with research

**Output:**

```
## Facts Verification

| # | Факт | Рядок | Research | Статус |
|---|------|-------|----------|--------|
| 1 | "pH 12-13" | 34 | line 45 | ✅ |
| 2 | "95% ефективність" | 56 | NOT FOUND | ⚠️ |

⚠️ Found 1 issue. Fix now? [Y/n]
```

---

### Phase 5: Keywords Coverage

```
## Keywords Coverage

Primary (need 100%, 3+ occurrences):
- ✅ "активна піна" — 5×
- ❌ "піна для безконтактного миття" — NOT FOUND

Secondary (need ≥80%): ✅ 4/5 (80%)
Supporting (need ≥80%): ✅ 6/7 (86%)

⚠️ 1 primary keyword missing. Add? [Y/n]
```

---

### Phase 6: Content Quality Checklist

**Present to user:**

```
## Quality Checklist

Intro:
- [ ] Зрозуміло що продається за 5 сек?
- [ ] Buyer focus (не визначення "X — це Y")?
- [ ] H1 = name з _clean.json?

Structure:
- [ ] Логічний порядок секцій?
- [ ] H2 допомагають навігації?
- [ ] Є патерни "Якщо X → Y" (≥3)?

Tables:
- [ ] Відповідають на "що обрати"?
- [ ] Немає дублювання між таблицями?

FAQ:
- [ ] Питання реальні (покупець би запитав)?
- [ ] Не дублюють основний текст?

Overall:
- [ ] Читається вголос плавно?
- [ ] Знаєш що купити після прочитання?
```

---

### Phase 7: Verdict & Actions

```
## Verdict

| Aspect | Status |
|--------|--------|
| Validators | ✅/⚠️/❌ |
| UK Terminology | ✅/❌ |
| Facts | ⚠️ 1 unverified |
| Keywords | ⚠️ 1 missing |
| Quality | ✅ Good |

**VERDICT: ⚠️ NEEDS FIXES**

Actions:
1. [T] Fix terminology
2. [F] Fix facts
3. [K] Add keywords
4. [D] Fix density/nausea
5. [S] Skip (keep as-is)
6. [N] Next category
```

**Wait for user choice.**

---

### Phase 8: Fix Mode

If user chooses to fix:

1. Show exact location
2. Propose fix
3. User confirms or edits
4. Apply Edit tool
5. Return to verdict

**Example:**

```
## Fix: RU term at line 15

Current:
> "Безпечний для резини"

Proposed fix:
> "Безпечний для гуми"

Apply this fix? [Y/n/edit]
```

---

## Key Principles

1. **Interactive** — wait for user at each decision point
2. **Transparent** — show where data comes from
3. **User controls** — skill proposes, user decides
4. **Research = truth** — facts verified only against research
5. **No silent fixes** — always ask before Edit
6. **UK terminology** — BLOCKER for RU terms

---

## vs uk-content-reviewer (subagent)

| Aspect | uk-content-reviewer | uk-verify-content |
|--------|---------------------|-------------------|
| Mode | Autonomous | Interactive |
| Control | Minimal | Full |
| Fixes | Automatic | On request |
| Speed | Fast (batch) | Thorough |
| Use case | Mass revision | Pre-prod QA |

---

## Thresholds Reference

| Metric | Target | BLOCKER |
|--------|--------|---------|
| Stem density | ≤2.5% | >3.0% |
| Classic nausea | ≤3.5 | >4.0 |
| Academic | ≥7% | <6% |
| Water | 40-65% | >75% |
| Primary keyword | 3-7× | 0 or >10 |
| H2 with keyword | ≥2 | 0 |
| Word count | 400-700 | <300 or >800 |
