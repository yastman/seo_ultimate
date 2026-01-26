# UK Full Cycle Implementation Plan

> **For Claude:** This is a MANUAL plan executed through skills. Run each step interactively with user confirmation.

**Goal:** Повний цикл мета + контент + валідація для всіх 50 UK категорій через скіли.

**Architecture:**
- Full cycle per category (не batch)
- 6 кроків: RU comparison → meta → validate → content → review → quality-gate → commit
- 4 групи категорій за пріоритетом: FAIL → WARNING → NO_KEYWORDS → PASS

**Tech Stack:** Python validators, project skills (`/uk-generate-meta`, `/uk-content-generator`, `/uk-quality-gate`), subagent (`uk-content-reviewer`)

---

## Pre-flight: Fix NO_KEYWORDS Categories

**Problem:** 13 категорій мають пусті `keywords` (всі в `supporting_keywords` через volume < 100).

**Files to fix:**
```
uk/categories/aksessuary/data/aksessuary_clean.json
uk/categories/antibitum/data/antibitum_clean.json
uk/categories/keramika-dlya-diskov/data/keramika-dlya-diskov_clean.json
uk/categories/mekhovye/data/mekhovye_clean.json
uk/categories/oborudovanie/data/oborudovanie_clean.json
uk/categories/ochistiteli-diskov/data/ochistiteli-diskov_clean.json
uk/categories/ochistiteli-kozhi/data/ochistiteli-kozhi_clean.json
uk/categories/ochistiteli-shin/data/ochistiteli-shin_clean.json
uk/categories/opt-i-b2b/data/opt-i-b2b_clean.json
uk/categories/silanty/data/silanty_clean.json
uk/categories/ukhod-za-naruzhnym-plastikom/data/ukhod-za-naruzhnym-plastikom_clean.json
uk/categories/vedra-i-emkosti/data/vedra-i-emkosti_clean.json
uk/categories/zashchitnye-pokrytiya/data/zashchitnye-pokrytiya_clean.json
```

### Task 0.1: Check each NO_KEYWORDS category

**Step 1: Identify top keyword from supporting**

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
        sup = d.get('supporting_keywords', [])
        if sup:
            top = sup[0]
            print(f'{slug}: {top[\"keyword\"]} (vol: {top.get(\"volume\", 0)})')
        else:
            print(f'{slug}: NO KEYWORDS AT ALL')
    except FileNotFoundError:
        print(f'{slug}: FILE NOT FOUND')
"
```

**Step 2: For each category, move top supporting → keywords**

Edit `uk/categories/{slug}/data/{slug}_clean.json`:
- Move first item from `supporting_keywords` to `keywords`
- Or move top 2-3 items to `secondary_keywords` if volume 50-100

**Step 3: Commit fix**

```bash
git add uk/categories/*/data/*_clean.json
git commit -m "fix(uk): promote top keywords from supporting to primary for 13 categories"
```

---

## Category Processing Groups

### Group 1: FAIL (19 categories)

Вже є контент, потрібно review + fix H2 keywords.

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

**Workflow:** Step 0 → Step 4 → Step 5 → Step 6

### Group 2: WARNING (3 categories)

Minor SEO fixes needed.

```
aktivnaya-pena
mikrofibra-i-tryapki
voski
```

**Workflow:** Step 0 → Step 4 → Step 5 → Step 6

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

**Workflow:** Step 0 → Step 1 → Step 2 → Step 3 → Step 4 → Step 5 → Step 6

### Group 4: PASS (17 categories)

Already passing, verify RU parity only.

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

**Workflow:** Step 0 → Step 5 → Step 6 (if changes)

---

## Task Template: Full Cycle for One Category

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
    sup = d.get('supporting_keywords', [])
    if sup:
        print(f'Top supporting: {sup[0][\"keyword\"]} (vol: {sup[0].get(\"volume\", 0)})')
"
```

Expected: `Primary/Secondary keywords: N` (N > 0)

**Step 0.2: Compare with RU keywords**

```bash
echo "=== RU Keywords ==="
python3 -c "
import json
d = json.load(open('categories/{slug}/data/{slug}_clean.json'))
for kw in d.get('keywords', [])[:5]:
    print(f'  {kw[\"keyword\"]} (vol: {kw.get(\"volume\", 0)})')
"

echo ""
echo "=== UK Keywords (source_ru) ==="
python3 -c "
import json
d = json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))
all_kw = d.get('keywords', []) + d.get('secondary_keywords', []) + d.get('supporting_keywords', [])
for kw in all_kw[:5]:
    print(f'  {kw.get(\"source_ru\", \"N/A\")} → {kw[\"keyword\"]}')
"
```

Expected: UK keywords should map to RU keywords

**Step 0.3: Check RU content exists**

```bash
ls -la categories/{slug}/content/{slug}_ru.md
head -20 categories/{slug}/content/{slug}_ru.md
```

Expected: File exists, shows H1 and intro

**Step 0.4: Check RU meta for reference**

```bash
python3 -c "
import json
d = json.load(open('categories/{slug}/meta/{slug}_meta.json'))
print(f'RU H1: {d.get(\"h1\", \"N/A\")}')
print(f'RU Title: {d.get(\"meta\", {}).get(\"title\", \"N/A\")}')
"
```

Expected: Shows RU H1 and Title for reference

---

#### Step 1: Generate Meta (if needed)

**Skill:** `/uk-generate-meta {slug}`

```
/uk-generate-meta {slug}
```

Expected output: `uk/categories/{slug}/meta/{slug}_meta.json` created/updated

---

#### Step 2: Validate Meta

**Step 2.1: Run validator**

```bash
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
```

Expected: All checks PASS

**Step 2.2: Manual check**

```bash
python3 -c "
import json
d = json.load(open('uk/categories/{slug}/meta/{slug}_meta.json'))
title = d.get('meta', {}).get('title', '')
desc = d.get('meta', {}).get('description', '')
h1 = d.get('h1', '')

print(f'Title ({len(title)} chars): {title}')
print(f'  - Has Купити: {\"Купити\" in title}')
print(f'  - Length OK: {50 <= len(title) <= 60}')
print()
print(f'Description ({len(desc)} chars): {desc}')
print(f'  - Length OK: {120 <= len(desc) <= 160}')
print()
print(f'H1: {h1}')
print(f'  - No Купити: {\"Купити\" not in h1}')
"
```

Expected checklist:
- [ ] Title 50-60 chars
- [ ] Title contains "Купити"
- [ ] Description 120-160 chars
- [ ] H1 has no "Купити"
- [ ] H1 matches RU H1 logically

---

#### Step 3: Generate Content (if needed)

**Skill:** `/uk-content-generator {slug}`

```
/uk-content-generator {slug}
```

Expected output: `uk/categories/{slug}/content/{slug}_uk.md` created

---

#### Step 4: Review Content

**Subagent:** `uk-content-reviewer {slug}`

```
uk-content-reviewer {slug}
```

Expected: Subagent reviews and fixes issues automatically

**Step 4.1: Manual RU parity check after review**

```bash
echo "=== RU Content Structure ==="
grep "^##" categories/{slug}/content/{slug}_ru.md

echo ""
echo "=== UK Content Structure ==="
grep "^##" uk/categories/{slug}/content/{slug}_uk.md
```

Expected: Similar H2 structure

```bash
echo "=== RU Tables ==="
grep -c "^|" categories/{slug}/content/{slug}_ru.md

echo "=== UK Tables ==="
grep -c "^|" uk/categories/{slug}/content/{slug}_uk.md
```

Expected: Similar number of tables

---

#### Step 5: Quality Gate

**Skill:** `/uk-quality-gate {slug}`

```
/uk-quality-gate {slug}
```

Expected: PASS status in `uk/categories/{slug}/QUALITY_REPORT.md`

**Step 5.1: Quick validation summary**

```bash
echo "=== Validation Summary ==="

# Meta
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json 2>&1 | tail -3

# SEO Structure
primary=$(python3 -c "import json; d=json.load(open('uk/categories/{slug}/data/{slug}_clean.json')); kws=d.get('keywords',[])+d.get('secondary_keywords',[]); print(kws[0]['keyword'] if kws else '')")
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "$primary" 2>&1 | grep -E "PASS|WARN|FAIL"

# UK Terminology
echo "UK Terms check:"
grep -c "резина\|мойка\|стекло" uk/categories/{slug}/content/{slug}_uk.md || echo "  No RU terms found ✓"

# Word count
wc -w uk/categories/{slug}/content/{slug}_uk.md
```

Expected: All PASS, no RU terms, 500-700 words

---

#### Step 6: Commit

```bash
git add uk/categories/{slug}/
git commit -m "feat(uk): {slug} — meta + content + quality-gate"
```

---

#### Step 7: Update Tracker

Edit `tasks/TODO_UK_CONTENT.md`:

```markdown
- [x] {slug} — full cycle done (2026-01-26)
```

---

## Execution Order

### Phase 1: Pre-flight (Task 0)

Fix 13 NO_KEYWORDS categories by promoting supporting → primary.

### Phase 2: Group 1 — FAIL (Tasks 1-19)

Process 19 FAIL categories with shortened workflow (Step 0 → 4 → 5 → 6).

### Phase 3: Group 2 — WARNING (Tasks 20-22)

Process 3 WARNING categories with shortened workflow.

### Phase 4: Group 3 — NO_KEYWORDS (Tasks 23-35)

Process 13 categories with full workflow (all steps).

### Phase 5: Group 4 — PASS (Tasks 36-52)

Verify 17 PASS categories (Step 0 → 5 → 6 if changes).

---

## Quick Reference: Skills & Commands

| Step | Skill/Command | What it does |
|------|---------------|--------------|
| 0 | Manual validation | RU ↔ UK parity check |
| 1 | `/uk-generate-meta {slug}` | Generate Title, Desc, H1 |
| 2 | `validate_meta.py` | Validate meta tags |
| 3 | `/uk-content-generator {slug}` | Generate buyer guide content |
| 4 | `uk-content-reviewer {slug}` | Review + auto-fix content |
| 5 | `/uk-quality-gate {slug}` | Final validation |
| 6 | `git commit` | Save changes |

---

## Validation Commands Cheatsheet

```bash
# Meta validation
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json

# SEO structure (replace {primary} with actual keyword)
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary}"

# Academic nausea (should be ≥7%)
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md

# Keyword density (stem ≤2.5%)
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

# UK terminology (should return 0)
grep -c "резина\|мойка\|стекло" uk/categories/{slug}/content/{slug}_uk.md

# Word count (should be 500-700)
wc -w uk/categories/{slug}/content/{slug}_uk.md
```

---

## Progress Tracking

```
Total: 52 categories

[ ] Pre-flight: Fix NO_KEYWORDS (13)
[ ] Group 1: FAIL (19)
[ ] Group 2: WARNING (3)
[ ] Group 3: NO_KEYWORDS full cycle (13)
[ ] Group 4: PASS verify (17)

Progress: 0/52
```

---

**Version:** 1.0
**Created:** 2026-01-26
