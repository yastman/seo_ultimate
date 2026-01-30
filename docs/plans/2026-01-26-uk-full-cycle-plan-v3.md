# UK Full Cycle Implementation Plan v3

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Повний цикл SEO для 52 UK категорій з інтеграцією ВСІХ ключових слів (keywords + secondary + supporting).

**Architecture:**
- Full cycle per category (не batch)
- **Критична зміна v3:** Інтегрувати ВСІ ключі з `_clean.json`, не тільки primary
- Розподіл ключів за правилами content-generator skill
- 4 групи категорій: FAIL (19) → WARNING (3) → NO_KEYWORDS (13) → PASS (17)

**Tech Stack:** Python validators, Edit tool, project skills

---

## Keyword Distribution Rules (from content-generator)

| Джерело | Де розміщувати | Перевірка |
|---------|----------------|-----------|
| `keywords[0]` (primary) | H1 + intro + 2-3x в тексті | BLOCKER якщо немає |
| `keywords[1-2]` | Intro або body | 1 кожен |
| `secondary_keywords` (use_in=content) | **H2 заголовки** | Мінімум 1 H2 |
| `supporting_keywords` (use_in=content) | Таблиці, body, FAQ | 1-2 |

**Ігнорувати:** ключі з `use_in: meta_only`

---

## Task 0: Commit Uncommitted Changes

**Files:**
- Stage: 4 modified `_clean.json` files

**Step 1: Check current changes**

```bash
git status --short | grep -E "^\s*M"
```

Expected: 4 modified files (ochistiteli-stekol, omyvatel, poliroli-dlya-plastika, polirovalnye-pasty)

**Step 2: Review changes**

```bash
git diff uk/categories/*/data/*_clean.json | head -50
```

Expected: Keyword fixes from previous session

**Step 3: Commit**

```bash
git add uk/categories/ochistiteli-stekol/data/ochistiteli-stekol_clean.json
git add uk/categories/omyvatel/data/omyvatel_clean.json
git add uk/categories/poliroli-dlya-plastika/data/poliroli-dlya-plastika_clean.json
git add uk/categories/polirovalnye-pasty/data/polirovalnye-pasty_clean.json
git commit -m "fix(uk): prepare keywords for SEO integration"
```

---

## Category Processing Template v3

### Task N: {slug}

**Files:**
- Read: `uk/categories/{slug}/data/{slug}_clean.json`
- Modify: `uk/categories/{slug}/content/{slug}_uk.md`

---

#### Step 0: Extract ALL Keywords

**Step 0.1: List all keywords for integration**

```bash
python3 -c "
import json
d = json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))

print('=== PRIMARY (H1 + intro + 2-3x) ===')
for kw in d.get('keywords', []):
    print(f'  - {kw[\"keyword\"]} (vol: {kw.get(\"volume\", 0)})')

print('\\n=== SECONDARY (H2 headings, 1 each) ===')
for kw in d.get('secondary_keywords', []):
    if kw.get('use_in') == 'content':
        print(f'  - {kw[\"keyword\"]} (vol: {kw.get(\"volume\", 0)})')
    else:
        print(f'  [meta_only] {kw[\"keyword\"]}')

print('\\n=== SUPPORTING (tables/body/FAQ, 1-2) ===')
for kw in d.get('supporting_keywords', []):
    if kw.get('use_in') == 'content':
        print(f'  - {kw[\"keyword\"]} (vol: {kw.get(\"volume\", 0)})')
    else:
        print(f'  [meta_only] {kw[\"keyword\"]}')
"
```

Expected: Full list of keywords to integrate

---

#### Step 1: Audit Current Content

**Step 1.1: Check primary keyword presence**

```bash
primary=$(python3 -c "import json; d=json.load(open('uk/categories/{slug}/data/{slug}_clean.json')); kws=d.get('keywords',[]); print(kws[0]['keyword'] if kws else '')")
echo "Primary: $primary"
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "$primary"
```

Expected: Either PASS or FAIL with specific issues

**Step 1.2: Check secondary keywords in H2**

```bash
python3 -c "
import json
import re

d = json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))
content = open('uk/categories/{slug}/content/{slug}_uk.md').read()

h2_pattern = r'^##\s+(.+)$'
h2s = re.findall(h2_pattern, content, re.MULTILINE)
print(f'H2 headers found: {len(h2s)}')
for h2 in h2s:
    print(f'  - {h2}')

print('\\n=== Secondary keywords (should be in H2) ===')
secondary = [kw for kw in d.get('secondary_keywords', []) if kw.get('use_in') == 'content']
for kw in secondary:
    keyword = kw['keyword'].lower()
    found_in_h2 = any(keyword in h2.lower() for h2 in h2s)
    status = '✓' if found_in_h2 else '✗ MISSING'
    print(f'  {status} {kw[\"keyword\"]}')
"
```

Expected: At least 1 secondary keyword in H2

**Step 1.3: Check supporting keywords presence**

```bash
python3 -c "
import json

d = json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))
content = open('uk/categories/{slug}/content/{slug}_uk.md').read().lower()

print('=== Supporting keywords (should be in tables/body/FAQ) ===')
supporting = [kw for kw in d.get('supporting_keywords', []) if kw.get('use_in') == 'content']
found = 0
for kw in supporting:
    keyword = kw['keyword'].lower()
    if keyword in content:
        print(f'  ✓ {kw[\"keyword\"]}')
        found += 1
    else:
        print(f'  ✗ MISSING: {kw[\"keyword\"]}')

print(f'\\nFound: {found}/{len(supporting)} (need 1-2)')
"
```

Expected: 1-2 supporting keywords present

---

#### Step 2: Fix Missing Keywords

**Step 2.1: Add secondary keyword to H2**

If secondary keyword missing from H2:
- Find most relevant H2
- Rewrite to include keyword naturally
- Use Edit tool

Example fix:
```
OLD: ## Як обрати засіб
NEW: ## Як обрати {secondary_keyword}
```

**Step 2.2: Add supporting keywords**

If supporting keywords missing:
- Add to table cells
- Add to FAQ answers
- Add to body paragraphs

Example locations:
- Table: `| {supporting_keyword} | опис | рекомендація |`
- FAQ: `{supporting_keyword} підходить для...`
- Body: `Використовуйте {supporting_keyword} якщо...`

---

#### Step 3: Validate

**Step 3.1: Run full validation**

```bash
primary=$(python3 -c "import json; d=json.load(open('uk/categories/{slug}/data/{slug}_clean.json')); kws=d.get('keywords',[]); print(kws[0]['keyword'] if kws else '')")

echo "=== SEO Structure ==="
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "$primary"

echo "\\n=== Word Count ==="
wc -w uk/categories/{slug}/content/{slug}_uk.md

echo "\\n=== Keyword Density ==="
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk 2>/dev/null || echo "Script not available"
```

Expected: All PASS, 400-700 words

**Step 3.2: Final keyword coverage check**

```bash
python3 -c "
import json
import re

d = json.load(open('uk/categories/{slug}/data/{slug}_clean.json'))
content = open('uk/categories/{slug}/content/{slug}_uk.md').read()
content_lower = content.lower()

print('=== FINAL KEYWORD COVERAGE ===')

# Primary
kws = d.get('keywords', [])
if kws:
    primary = kws[0]['keyword']
    count = content_lower.count(primary.lower())
    status = '✓' if count >= 3 else f'✗ only {count}x (need 3+)'
    print(f'PRIMARY: {primary} → {status}')

# Secondary in H2
h2s = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
secondary_content = [kw for kw in d.get('secondary_keywords', []) if kw.get('use_in') == 'content']
h2_hits = 0
for kw in secondary_content:
    if any(kw['keyword'].lower() in h2.lower() for h2 in h2s):
        h2_hits += 1
status = '✓' if h2_hits >= 1 else '✗ need 1+ in H2'
print(f'SECONDARY in H2: {h2_hits}/{len(secondary_content)} → {status}')

# Supporting
supporting_content = [kw for kw in d.get('supporting_keywords', []) if kw.get('use_in') == 'content']
supporting_found = sum(1 for kw in supporting_content if kw['keyword'].lower() in content_lower)
status = '✓' if supporting_found >= 1 else '✗ need 1-2'
print(f'SUPPORTING: {supporting_found}/{len(supporting_content)} → {status}')
"
```

Expected: All ✓

---

#### Step 4: Commit

```bash
git add uk/categories/{slug}/content/{slug}_uk.md
git commit -m "feat(uk): {slug} — SEO keywords integration"
```

---

## Group 1: FAIL (19 categories) — Remaining

Already processed (with commits):
- ✅ akkumulyatornaya
- ✅ aksessuary-dlya-naneseniya-sredstv
- ✅ antimoshka
- ✅ cherniteli-shin
- ✅ gubki-i-varezhki
- ✅ keramika-i-zhidkoe-steklo
- ✅ kisti-dlya-deteylinga
- ✅ kvik-deteylery
- ✅ malyarniy-skotch
- ✅ neytralizatory-zapakha

**Remaining FAIL (9):**
```
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

---

## Group 2: WARNING (3 categories)

```
aktivnaya-pena
mikrofibra-i-tryapki
voski
```

---

## Group 3: NO_KEYWORDS (13 categories)

After Task 0 pre-flight fix.

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

---

## Group 4: PASS (17 categories)

Verify only.

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

---

## Progress Tracking

```
Total: 52 categories

[x] Task 0: Commit uncommitted changes (4 files)
[x] FAIL processed: 10/19
[ ] FAIL remaining: 9/19
[ ] WARNING: 0/3
[ ] NO_KEYWORDS: 0/13
[ ] PASS verify: 0/17

Progress: 10/52
```

---

**Version:** 3.0
**Created:** 2026-01-26
**Changes from v2:**
- Критично: інтеграція ВСІХ ключів (keywords + secondary + supporting)
- Чіткі правила розподілу з content-generator skill
- Аудит кожної категорії перед фіксом
- Окремий крок для secondary keywords в H2
