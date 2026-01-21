# Content Revision: 50 Categories Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Провести ручную ревизию контента и мета-тегов 50 категорий, написанных субагентами, с валидацией по стандартам content-generator v3.2.

**Architecture:** Sequential review per category: read data → run 4 validation scripts → manual checklist v3.2 → verdict → fix if needed → re-validate. Categories grouped into 6 batches by theme.

**Tech Stack:** Python validation scripts (validate_meta.py, validate_content.py, check_keyword_density.py, check_water_natasha.py), /content-generator v3.2 skill, /generate-meta skill.

---

## Prerequisites

**Step 1: Verify validation scripts work**

```bash
python3 scripts/validate_meta.py --help
python3 scripts/validate_content.py --help
python3 scripts/check_keyword_density.py --help 2>/dev/null || echo "OK - no help flag"
python3 scripts/check_water_natasha.py --help 2>/dev/null || echo "OK - no help flag"
```

Expected: No errors, scripts are available.

**Step 2: Understand data structure**

Each category at `categories/{path}/` contains:
```
{slug}/
├── content/{slug}_ru.md        # Content to review
├── data/{slug}_clean.json      # name, parent_id, entities, keywords
├── meta/{slug}_meta.json       # h1, keywords_in_content, meta.title/description
└── research/RESEARCH_DATA.md   # FAQ source (if exists)
```

Key fields:
- `_clean.json` → `name` (for H1), `parent_id` (null=Hub, else=Product), `entities` (E-E-A-T terms)
- `_meta.json` → `h1`, `keywords_in_content.primary/secondary/supporting`

---

## Category Review Template

For each category `{slug}` at path `{path}`:

### Step 1: Read data files (parallel)

```bash
# Read 4 files
cat categories/{path}/data/{slug}_clean.json
cat categories/{path}/meta/{slug}_meta.json
cat categories/{path}/research/RESEARCH_DATA.md   # ← референс для проверки фактов
cat categories/{path}/content/{slug}_ru.md
```

Extract key values:
- `name` from _clean.json → H1 должен = name (множественное число для категорий!)
- `parent_id` from _clean.json → null=Hub Page, else=Product Page
- `keywords_in_content.primary` from _meta.json → must be in intro
- `keywords_in_content.secondary` from _meta.json → at least 1 H2 must contain one
- **RESEARCH_DATA.md** → референс для проверки фактов и FAQ

### Step 2: Run 4 validation scripts (parallel)

```bash
# 1. Meta validation
python3 scripts/validate_meta.py categories/{path}/meta/{slug}_meta.json

# 2. Content SEO validation
python3 scripts/validate_content.py categories/{path}/content/{slug}_ru.md "{primary_keyword}" --mode seo

# 3. Keyword density
python3 scripts/check_keyword_density.py categories/{path}/content/{slug}_ru.md

# 4. Water and nausea
python3 scripts/check_water_natasha.py categories/{path}/content/{slug}_ru.md
```

### Step 3: Manual checklist v3.3

**Structure:**
- [ ] H1 = name из _clean.json (множественное число!)
- [ ] Intro 30-60 words
- [ ] Comparison table exists
- [ ] FAQ 3-5 questions about CHOICE (not how-to)
- [ ] NO how-to sections (no 5+ step instructions)

**SEO/LSI:**
- [ ] Primary keyword in intro
- [ ] At least 1 H2 contains secondary keyword
- [ ] No commercial keywords in body (купить, цена, заказать)

**Research соответствие:**
- [ ] Факты в тексте соответствуют RESEARCH_DATA.md
- [ ] FAQ не противоречит research

**RU-first:**
- [ ] Russian term first, English in brackets: "разбрызгивание (sling)"

**Metrics (from scripts):**
- [ ] Stem density ≤2.5% (BLOCKER if >3.0%)
- [ ] Classic nausea ≤3.5 (BLOCKER if >4.0)
- [ ] Academic nausea ≥7% (INFO if <7% = dry text)
- [ ] Water 40-65% (WARNING if >75%)

### Step 4: Verdict

| Result | Criteria | Action |
|--------|----------|--------|
| ✅ PASS | All checks pass, no BLOCKER/WARNING | Move to next category |
| ⚠️ WARNING | Minor issues (H2 missing keyword, water high) | Show issues, ask user if fix needed |
| ❌ BLOCKER | H1 wrong, how-to sections, spam >3% | Must fix before proceeding |

### Step 5: Fix if needed

Common fixes:

**H1 ≠ name:**
```markdown
# Wrong H1
→
# {name from _clean.json}
```

**H2 missing secondary keyword:**
```markdown
## Generic Title
→
## How to choose {secondary_keyword}
```

**How-to section found:**
Delete entire section or convert to 1-2 sentence mention:
```markdown
❌ 1. Step one... 2. Step two... 3. Step three...
→
✅ **Method name** — professional approach: brief description.
```

**Anglicism without RU-first:**
```markdown
❌ sling, wet look, dwell time
→
✅ разбрызгивание (sling), мокрый блеск (wet look), время выдержки (dwell time)
```

### Step 6: Re-validate after fix

Run same 4 scripts again to confirm fix worked.

### Step 7: Mark complete

Update progress in this document.

---

## Quality Criteria Reference

### BLOCKER (must fix)

| Issue | Detection | Fix |
|-------|-----------|-----|
| H1 ≠ name | H1 должен = name (мн.ч.) | Replace H1 |
| How-to sections | H2/H3 with "Как наносить", "Пошаговая инструкция" | Delete or convert |
| Stem >3.0% | check_keyword_density.py | Replace with synonyms |
| Nausea >4.0 | check_water_natasha.py | Add variety, use synonyms |
| Meta FAIL | validate_meta.py | Fix meta tags |
| Facts contradict research | Compare with RESEARCH_DATA.md | Fix facts |

### WARNING (should fix)

| Issue | Detection | Fix |
|-------|-----------|-----|
| No H2 with secondary keyword | Manual check vs _meta.json | Rewrite 1 H2 |
| Water >75% | check_water_natasha.py | Remove filler words |
| Anglicisms without RU-first | Manual search | Add Russian translation |
| FAQ duplicates table | Manual check | Replace question |

### INFO (optional)

| Issue | Detection | Note |
|-------|-----------|------|
| Academic nausea <7% | check_water_natasha.py | Text is "dry", OK for Hub Pages |
| Water 60-75% | check_water_natasha.py | Slightly high, usually OK |

---

## Typical Fixes Reference

### Synonyms for spam reduction

**Tools/Equipment:**
| Word | Synonyms |
|------|----------|
| машинка/машина | инструмент, устройство, вариант, модель |
| аккумулятор | АКБ, элемент питания, источник питания |
| средство | состав, продукт, препарат |

**Auto care:**
| Word | Synonyms |
|------|----------|
| поверхность | покрытие, основа, материал |
| защита | барьер, слой, покрытие |
| блеск | глянец, сияние, финиш |
| автомобиль | авто, машина, транспорт |

### Exact numbers → soften

| Was | Becomes |
|-----|---------|
| 5-10 минут | дайте впитаться |
| 20-30°C | при комнатной температуре |
| 7-14 дней | обычно требует обновления после нескольких моек |

---

## Task 1: Batch 1 — Мойка и экстерьер (18 categories)

**Scope:** 18 categories in `categories/moyka-i-eksterer/`

### Categories to review:

| # | Slug | Path | Type | Status |
|---|------|------|------|--------|
| 1 | moyka-i-eksterer | moyka-i-eksterer | Hub | ✅ PASS |
| 2 | avtoshampuni | moyka-i-eksterer/avtoshampuni | Hub | ⬜ |
| 3 | aktivnaya-pena | moyka-i-eksterer/avtoshampuni/aktivnaya-pena | Product | ⬜ |
| 4 | shampuni-dlya-ruchnoy-moyki | moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki | Product | ⬜ |
| 5 | ochistiteli-dvigatelya | moyka-i-eksterer/ochistiteli-dvigatelya | Product | ⬜ |
| 6 | glina-i-avtoskraby | moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby | Product | ⬜ |
| 7 | antibitum | moyka-i-eksterer/ochistiteli-kuzova/antibitum | Product | ⬜ |
| 8 | antimoshka | moyka-i-eksterer/ochistiteli-kuzova/antimoshka | Product | ⬜ |
| 9 | obezzhirivateli | moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli | Product | ⬜ |
| 10 | ukhod-za-naruzhnym-plastikom | moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom | Product | ⬜ |
| 11 | cherniteli-shin | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin | Product | ⬜ |
| 12 | ochistiteli-diskov | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov | Product | ⬜ |
| 13 | ochistiteli-shin | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin | Product | ⬜ |
| 14 | keramika-dlya-diskov | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov | Product | ⬜ |
| 15 | ochistiteli-stekol | moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol | Product | ⬜ |
| 16 | antidozhd | moyka-i-eksterer/sredstva-dlya-stekol/antidozhd | Product | ⬜ |
| 17 | omyvatel | moyka-i-eksterer/sredstva-dlya-stekol/omyvatel | Product | ⬜ |
| 18 | polirol-dlya-stekla | moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla | Product | ⬜ |

**Execution:**
1. For each category: follow Category Review Template above
2. Mark status: ✅ PASS, ⚠️ WARNING (with note), ❌ FIXED
3. After batch complete: commit if fixes were made

**Commit after batch:**
```bash
git add categories/moyka-i-eksterer/
git commit -m "review(content): batch 1 moyka-i-eksterer - validated 18 categories"
```

---

## Task 2: Batch 2 — Аксессуары (10 categories)

**Scope:** 10 categories in `categories/aksessuary/`

| # | Slug | Path | Type | Status |
|---|------|------|------|--------|
| 19 | aksessuary | aksessuary | Hub | ⬜ |
| 20 | mikrofibra-i-tryapki | aksessuary/mikrofibra-i-tryapki | Product | ⬜ |
| 21 | gubki-i-varezhki | aksessuary/gubki-i-varezhki | Product | ⬜ |
| 22 | raspyliteli-i-penniki | aksessuary/raspyliteli-i-penniki | Product | ⬜ |
| 23 | aksessuary-dlya-naneseniya-sredstv | aksessuary/aksessuary-dlya-naneseniya-sredstv | Product | ⬜ |
| 24 | nabory | aksessuary/nabory | Product | ⬜ |
| 25 | vedra-i-emkosti | aksessuary/vedra-i-emkosti | Product | ⬜ |
| 26 | shchetka-dlya-moyki-avto | aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto | Product | ⬜ |
| 27 | kisti-dlya-deteylinga | aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga | Product | ⬜ |
| 28 | malyarniy-skotch | aksessuary/malyarniy-skotch | Product | ⬜ |

**Commit after batch:**
```bash
git add categories/aksessuary/
git commit -m "review(content): batch 2 aksessuary - validated 10 categories"
```

---

## Task 3: Batch 3 — Уход за интерьером (8 categories)

**Scope:** 8 categories in `categories/ukhod-za-intererom/`

| # | Slug | Path | Type | Status |
|---|------|------|------|--------|
| 29 | ukhod-za-intererom | ukhod-za-intererom | Hub | ⬜ |
| 30 | sredstva-dlya-khimchistki-salona | ukhod-za-intererom/sredstva-dlya-khimchistki-salona | Product | ⬜ |
| 31 | sredstva-dlya-kozhi | ukhod-za-intererom/sredstva-dlya-kozhi | Hub | ⬜ |
| 32 | ochistiteli-kozhi | ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi | Product | ⬜ |
| 33 | ukhod-za-kozhey | ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey | Product | ⬜ |
| 34 | poliroli-dlya-plastika | ukhod-za-intererom/poliroli-dlya-plastika | Product | ⬜ |
| 35 | pyatnovyvoditeli | ukhod-za-intererom/pyatnovyvoditeli | Product | ⬜ |
| 36 | neytralizatory-zapakha | ukhod-za-intererom/neytralizatory-zapakha | Product | ⬜ |

**Commit after batch:**
```bash
git add categories/ukhod-za-intererom/
git commit -m "review(content): batch 3 ukhod-za-intererom - validated 8 categories"
```

---

## Task 4: Batch 4 — Защитные покрытия (7 categories)

**Scope:** 7 categories in `categories/zashchitnye-pokrytiya/`

| # | Slug | Path | Type | Status |
|---|------|------|------|--------|
| 37 | zashchitnye-pokrytiya | zashchitnye-pokrytiya | Hub | ⬜ |
| 38 | keramika-i-zhidkoe-steklo | zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo | Product | ⬜ |
| 39 | voski | zashchitnye-pokrytiya/voski | Hub | ⬜ |
| 40 | tverdyy-vosk | zashchitnye-pokrytiya/voski/tverdyy-vosk | Product | ⬜ |
| 41 | zhidkiy-vosk | zashchitnye-pokrytiya/voski/zhidkiy-vosk | Product | ⬜ |
| 42 | silanty | zashchitnye-pokrytiya/silanty | Product | ⬜ |
| 43 | kvik-deteylery | zashchitnye-pokrytiya/kvik-deteylery | Product | ⬜ |

**Commit after batch:**
```bash
git add categories/zashchitnye-pokrytiya/
git commit -m "review(content): batch 4 zashchitnye-pokrytiya - validated 7 categories"
```

---

## Task 5: Batch 5 — Полировка (4 categories)

**Scope:** 4 categories in `categories/polirovka/`

| # | Slug | Path | Type | Status |
|---|------|------|------|--------|
| 44 | polirovka | polirovka | Hub | ⬜ |
| 45 | polirovalnye-pasty | polirovka/polirovalnye-pasty | Product | ⬜ |
| 46 | mekhovye | polirovka/polirovalnye-krugi/mekhovye | Product | ⬜ |
| 47 | akkumulyatornaya | polirovka/polirovalnye-mashinki/akkumulyatornaya | Product | ⬜ |

**Commit after batch:**
```bash
git add categories/polirovka/
git commit -m "review(content): batch 5 polirovka - validated 4 categories"
```

---

## Task 6: Batch 6 — Оборудование и Опт (3 categories)

**Scope:** 3 categories

| # | Slug | Path | Type | Status |
|---|------|------|------|--------|
| 48 | oborudovanie | oborudovanie | Hub | ⬜ |
| 49 | apparaty-tornador | oborudovanie/apparaty-tornador | Product | ⬜ |
| 50 | opt-i-b2b | opt-i-b2b | Special | ⬜ |

**Commit after batch:**
```bash
git add categories/oborudovanie/ categories/opt-i-b2b/
git commit -m "review(content): batch 6 oborudovanie + opt - validated 3 categories"
```

---

## Execution Checklist

| Batch | Categories | Reviewed | Status |
|-------|------------|----------|--------|
| 1. Мойка и экстерьер | 18 | 1 | 🔄 in progress |
| 2. Аксессуары | 10 | 0 | ⬜ pending |
| 3. Уход за интерьером | 8 | 0 | ⬜ pending |
| 4. Защитные покрытия | 7 | 0 | ⬜ pending |
| 5. Полировка | 4 | 0 | ⬜ pending |
| 6. Оборудование и Опт | 3 | 0 | ⬜ pending |
| **TOTAL** | **50** | **1** | **2%** |

---

## Final Validation

After all 50 categories reviewed:

```bash
# Run full validation
python3 scripts/validate_meta.py --all
python3 scripts/validate_content.py --all --mode seo 2>/dev/null || echo "Run per-category"

# Check git status
git status

# Final commit if needed
git add .
git commit -m "review(content): complete revision of 50 categories"
```

**Next steps:**
- `/quality-gate {slug}` for each category
- `/deploy-to-opencart {slug}` when ready

---

**Plan Version:** 1.0 | **Created:** 2026-01-21
