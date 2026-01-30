# UK Full Cycle Implementation Plan v2

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Повний цикл мета + контент + валідація для 52 UK категорій через скіли (БЕЗ субагентів).

**Architecture:**
- Full cycle per category (не batch)
- 5 кроків: RU comparison → meta → content → manual review → quality-gate → commit
- 4 групи категорій за пріоритетом: FAIL → WARNING → NO_KEYWORDS → PASS
- **Review через валідатори + Edit** замість субагента uk-content-reviewer

**Tech Stack:** Python validators, project skills (`/uk-generate-meta`, `/uk-content-generator`, `/uk-quality-gate`), Edit tool

---

## Pre-flight: Fix NO_KEYWORDS Categories

**Problem:** 13 категорій мають пусті `keywords` (всі в `supporting_keywords` через volume < 100).

### Task 0: Promote keywords for NO_KEYWORDS categories

**Files:**
- Modify: `uk/categories/{slug}/data/{slug}_clean.json` (13 files)

**Step 1: Check current state**

```bash
python3 -c "
import json
from pathlib import Path

no_kw_cats = [
    'aksessuary', 'antibitum', 'keramika-dlya-diskov', 'mekhovye',
    'oborudovanie', 'ochistiteli-diskov', 'ochistiteli-kozhi',
    'ochistiteli-shin', 'opt-i-b2b', 'silanty',
    'ukhod-za-naruzhnym-plastikom', 'vedra-i-emkosti', 'zashchitnye-pokrytiya'
]

for slug in no_kw_cats:
    path = f'uk/categories/{slug}/data/{slug}_clean.json'
    try:
        d = json.load(open(path))
        kw = d.get('keywords', [])
        sup = d.get('supporting_keywords', [])
        if kw:
            print(f'{slug}: HAS {len(kw)} keywords')
        elif sup:
            top = sup[0]
            print(f'{slug}: NO keywords, top supporting: {top[\"keyword\"]} (vol: {top.get(\"volume\", 0)})')
        else:
            print(f'{slug}: NO keywords at all!')
    except FileNotFoundError:
        print(f'{slug}: FILE NOT FOUND')
"
```

Expected: List showing which categories need fix

**Step 2: For each category with empty `keywords`, promote top supporting**

For each slug where `keywords` is empty:

1. Read `uk/categories/{slug}/data/{slug}_clean.json`
2. Move first item from `supporting_keywords` to `keywords`
3. Save file

**Step 3: Verify fix**

```bash
python3 -c "
import json
cats = ['aksessuary', 'antibitum', 'keramika-dlya-diskov', 'mekhovye',
        'oborudovanie', 'ochistiteli-diskov', 'ochistiteli-kozhi',
        'ochistiteli-shin', 'opt-i-b2b', 'silanty',
        'ukhod-za-naruzhnym-plastikom', 'vedra-i-emkosti', 'zashchitnye-pokrytiya']
for slug in cats:
    d = json.load(open(f'uk/categories/{slug}/data/{slug}_clean.json'))
    kw = d.get('keywords', [])
    print(f'{slug}: {len(kw)} keywords - {kw[0][\"keyword\"] if kw else \"NONE\"}')"
```

Expected: All have ≥1 keyword

**Step 4: Commit fix**

```bash
git add uk/categories/*/data/*_clean.json
git commit -m "fix(uk): promote top keywords from supporting for 13 categories"
```

---

## Category Processing Template

### Task N: {slug}

**Files:**
- Read: `uk/categories/{slug}/data/{slug}_clean.json`
- Read: `categories/{slug}/data/{slug}_clean.json` (RU reference)
- Read: `categories/{slug}/meta/{slug}_meta.json` (RU reference)
- Read: `categories/{slug}/content/{slug}_ru.md` (RU reference)
- Modify: `uk/categories/{slug}/meta/{slug}_meta.json`
- Modify: `uk/categories/{slug}/content/{slug}_uk.md`
- Create: `uk/categories/{slug}/QUALITY_REPORT.md`

---

#### Step 0: RU Comparison

**Step 0.1: Check UK keywords exist**

```bash
python3 -c "
import json
d = json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))
kws = d.get('keywords', []) + d.get('secondary_keywords', [])
print(f'Primary/Secondary keywords: {len(kws)}')
if kws:
    print(f'Top keyword: {kws[0][\"keyword\"]}')
else:
    print('⚠️  NO PRIMARY — need to fix _clean.json first!')
"
```

Expected: `Primary/Secondary keywords: N` (N > 0)

**Step 0.2: Check RU reference exists**

```bash
ls -la categories/{slug}/content/{slug}_ru.md 2>/dev/null && echo "RU content: EXISTS" || echo "RU content: MISSING"
ls -la categories/{slug}/meta/{slug}_meta.json 2>/dev/null && echo "RU meta: EXISTS" || echo "RU meta: MISSING"
```

Expected: Both exist

---

#### Step 1: Generate Meta

**Skill:** `/uk-generate-meta {slug}`

Expected output: `uk/categories/{slug}/meta/{slug}_meta.json` created/updated

**Step 1.1: Verify meta**

```bash
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
```

Expected: All checks PASS

---

#### Step 2: Generate Content (if needed)

**Check if content exists:**

```bash
ls -la uk/categories/{slug}/content/{slug}_uk.md 2>/dev/null && echo "UK content: EXISTS" || echo "UK content: MISSING"
```

**If MISSING — Skill:** `/uk-content-generator {slug}`

Expected output: `uk/categories/{slug}/content/{slug}_uk.md` created

---

#### Step 3: Manual Review (replaces uk-content-reviewer subagent)

**Step 3.1: Run validators**

```bash
# Get primary keyword
primary=$(python3 -c "import json; d=json.load(open('uk/categories/{slug}/data/{slug}_clean.json')); kws=d.get('keywords',[])+d.get('secondary_keywords',[]); print(kws[0]['keyword'] if kws else '')")
echo "Primary keyword: $primary"

# SEO Structure
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "$primary"

# Keyword density
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

# Academic nausea
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md

# Word count
wc -w uk/categories/{slug}/content/{slug}_uk.md
```

**Step 3.2: Check UK terminology**

```bash
echo "=== UK Terminology Check ==="
grep -in "резин" uk/categories/{slug}/content/{slug}_uk.md || echo "  резина: OK"
grep -in "мойк" uk/categories/{slug}/content/{slug}_uk.md || echo "  мойка: OK"
grep -in "стекл" uk/categories/{slug}/content/{slug}_uk.md || echo "  стекло: OK"
```

Expected: No matches (all should show "OK")

**Step 3.3: Check H1/Title**

```bash
python3 -c "
import json
d = json.load(open('uk/categories/{slug}/meta/{slug}_meta.json'))
h1 = d.get('h1', '')
title = d.get('meta', {}).get('title', '')
print(f'H1: {h1}')
print(f'  - Has Купити: {\"Купити\" in h1}')
print(f'Title: {title}')
print(f'  - Has Купити: {\"Купити\" in title}')
if 'Купити' in h1:
    print('⚠️  H1 should NOT have Купити!')
if 'Купити' not in title:
    print('⚠️  Title SHOULD have Купити!')
"
```

Expected: H1 without "Купити", Title with "Купити"

**Step 3.4: Fix issues (if any)**

Based on validator output, use Edit tool to fix:
- H2 keywords missing → add keyword to H2
- RU terms found → replace with UK terms
- Academic <7% → add reader addressing ("вам", "якщо ви")
- Word count >700 → trim verbose sections
- Keyword density >2.5% → use synonyms from uk-lsi-synonyms.md

---

#### Step 4: Quality Gate

**Skill:** `/uk-quality-gate {slug}`

Expected: PASS status in `uk/categories/{slug}/QUALITY_REPORT.md`

**Step 4.1: Quick validation summary**

```bash
echo "=== Final Validation ==="
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json 2>&1 | tail -3
primary=$(python3 -c "import json; d=json.load(open('uk/categories/{slug}/data/{slug}_clean.json')); kws=d.get('keywords',[])+d.get('secondary_keywords',[]); print(kws[0]['keyword'] if kws else '')")
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "$primary" 2>&1 | grep -E "PASS|WARN|FAIL"
wc -w uk/categories/{slug}/content/{slug}_uk.md
```

Expected: All PASS, 500-700 words

---

#### Step 5: Commit

```bash
git add uk/categories/{slug}/
git commit -m "feat(uk): {slug} — meta + content + quality-gate"
```

---

## Category Groups

### Group 1: FAIL (19 categories)

Content exists, needs review + SEO fix.

```
akkumulyatornaya
aksessuary-dlya-naneseniya-sredstv
antimoshka
cherniteli-shin
gubki-i-varezhki
keramika-i-zhidkoe-steklo
kisti-dlya-deteylinga
kvik-deteylery
malyarniy-skotch
neytralizatory-zapakha
ochistiteli-stekol
omyvatel
poliroli-dlya-plastika
polirovalnye-pasty
raspyliteli-i-penniki
shampuni-dlya-ruchnoy-moyki
sredstva-dlya-khimchistki-salona
tverdyy-vosk
ukhod-za-intererom
```

**Workflow:** Step 0 → Step 3 → Step 4 → Step 5

### Group 2: WARNING (3 categories)

Minor SEO fixes needed.

```
aktivnaya-pena
mikrofibra-i-tryapki
voski
```

**Workflow:** Step 0 → Step 3 → Step 4 → Step 5

### Group 3: NO_KEYWORDS (13 categories)

After Pre-flight fix, full cycle needed.

```
aksessuary
antibitum
keramika-dlya-diskov
mekhovye
oborudovanie
ochistiteli-diskov
ochistiteli-kozhi
ochistiteli-shin
opt-i-b2b
silanty
ukhod-za-naruzhnym-plastikom
vedra-i-emkosti
zashchitnye-pokrytiya
```

**Workflow:** Step 0 → Step 1 → Step 2 → Step 3 → Step 4 → Step 5

### Group 4: PASS (17 categories)

Already passing, verify only.

```
antidozhd
apparaty-tornador
avtoshampuni
glina-i-avtoskraby
moyka-i-eksterer
nabory
obezzhirivateli
ochistiteli-dvigatelya
ochistiteli-kuzova
polirol-dlya-stekla
polirovalnye-mashinki
polirovka
pyatnovyvoditeli
shchetka-dlya-moyki-avto
sredstva-dlya-kozhi
ukhod-za-kozhey
zhidkiy-vosk
```

**Workflow:** Step 0 → Step 4 → Step 5 (if changes)

---

## UK Term Replacements

| RU Term | UK Term |
|---------|---------|
| резина | гума |
| мойка | миття |
| стекло | скло |
| полироль | поліроль |
| тряпка | ганчірка |

---

## Validation Commands Cheatsheet

```bash
# Meta validation
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json

# SEO structure
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary}"

# Keyword density
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

# Academic nausea (≥7%)
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md

# UK terminology check
grep -c "резина\|мойка\|стекло" uk/categories/{slug}/content/{slug}_uk.md

# Word count (500-700)
wc -w uk/categories/{slug}/content/{slug}_uk.md
```

---

## Progress Tracking

```
Total: 52 categories

[ ] Task 0: Pre-flight fix NO_KEYWORDS (13)
[ ] Group 1: FAIL (19) — Tasks 1-19
[ ] Group 2: WARNING (3) — Tasks 20-22
[ ] Group 3: NO_KEYWORDS full cycle (13) — Tasks 23-35
[ ] Group 4: PASS verify (17) — Tasks 36-52

Progress: 0/52
```

---

**Version:** 2.0
**Created:** 2026-01-26
**Changes from v1:** Removed uk-content-reviewer subagent, replaced with manual validation + Edit
