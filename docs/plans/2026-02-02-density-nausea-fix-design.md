# Design: Density/Nausea Auto-Fix in Validation Skills

**Date:** 2026-02-02
**Status:** Draft

---

## Problem

All 4 validation skills run `validate_density.py` and `check_water_natasha.py`, but none of them actually fix the problems they detect:

- **Stem density >3.0%** — detected, not fixed
- **Classic nausea >4.0** — detected, not fixed
- **Water >75%** — detected, not fixed

The skills know WHAT the problem is, but lack instructions on HOW to fix it.

---

## Solution

Add a new Step/Phase to all 4 skills with identical fix logic:

| Skill | Mode | New Step |
|-------|------|----------|
| content-reviewer | Autonomous | Step between 8 and 9 |
| uk-content-reviewer | Autonomous | Step between 9 and 10 |
| verify-content | Interactive | New Phase after Phase 6 |
| uk-verify-content | Interactive | New Phase after Phase 7 |

**Difference between modes:**
- Autonomous: fixes silently, reports in log
- Interactive: shows each replacement, asks for confirmation

---

## Fix Algorithm

```
### Step X: Fix Density/Nausea (if BLOCKER)

**Triggers:**
- validate_density.py: stem >3.0%
- check_water_natasha.py: classic nausea >4.0 OR water >75%

**Algorithm:**

1. Parse validator output to get overused word:
   - Stem: "піна* — 12 раз (3.46%)"
   - Nausea: "Самое частое слово: 'піна' (12 раз)"

2. Find all occurrences in content file

3. Calculate target: keep 3-4 occurrences (aim for 1.5-2.0%)
   - Formula: target_count = total_words * 0.02 (round to 3-4)

4. Select which occurrences to replace:
   - Keep: first mention, H2 headings, table headers
   - Replace: body text repetitions

5. Replace with contextually appropriate synonyms:
   - LLM chooses based on sentence context
   - No synonym dictionary needed

6. Re-run validator:
   ```bash
   python3 scripts/validate_density.py {content_path} --lang {lang}
   ```

7. Loop until PASS or max 3 iterations

8. If still >3.0% after 3 iterations:
   - Document in log which words couldn't be fixed
   - Proceed to next step (don't block)
```

---

## Synonym Selection (LLM-driven)

No hardcoded dictionary. LLM picks synonyms based on context:

**Example for "піна" (foam):**

| Context | Replacement |
|---------|-------------|
| "активна піна видаляє бруд" | "засіб видаляє бруд" |
| "нанесіть піну на кузов" | "нанесіть склад на кузов" |
| "піна працює 3-5 хвилин" | "формула працює 3-5 хвилин" |
| "обирайте піну з нейтральним pH" | "обирайте продукт з нейтральним pH" |

**Rules:**
- Preserve technical accuracy
- Match grammatical case/gender
- Don't replace in headings (H1, H2)
- Don't replace first mention in intro

---

## Thresholds

| Metric | Target | Warning | BLOCKER |
|--------|--------|---------|---------|
| Stem density | 1.5-2.5% | 2.5-3.0% | >3.0% |
| Classic nausea | ≤3.5 | 3.5-4.0 | >4.0 |
| Academic nausea | 7-9.5% | — | <6% or >12% |
| Water | 40-65% | 65-75% | >75% |

---

## Changes Required

### 1. content-reviewer/SKILL.md

Add after Step 8 (Fix if BLOCKER):

```markdown
### Step 8a: Fix Density/Nausea (if BLOCKER)

**Trigger:** Step 2 validators show stem >3.0% OR nausea >4.0

1. From validate_density.py output, identify overused stem group
2. Find all occurrences in {slug}_ru.md
3. Keep 3-4 occurrences (first mention, headings, key sentences)
4. Replace remaining with contextual synonyms
5. Re-run: `python3 scripts/validate_density.py {content_path}`
6. Repeat until ≤2.5% or max 3 iterations
7. Log replacements made

**Example:**
- Before: "пена" appears 15 times (3.8%)
- After: "пена" 4 times + "средство" 5 times + "состав" 3 times + "продукт" 3 times = 1.0%
```

Update BLOCKER Fixes table:
```markdown
| Stem >3.0% | Step 8a: Replace with synonyms (auto) |
```

### 2. uk-content-reviewer/SKILL.md

Same addition after Step 9, with UK examples.

### 3. verify-content/SKILL.md

Add new Phase 6a (between Phase 6 Verdict and Phase 7 Fix Mode):

```markdown
### Phase 6a: Density/Nausea Fix (if needed)

If validators show density/nausea issues:

1. Show overused word and count:
   ```
   ## Density Issue

   Word "пена" appears 15 times (3.8%)
   Target: 3-4 times (≤2.5%)

   Found at lines: 5, 12, 18, 23, 31, 42, 48, 55, 61, 67, 73, 79, 85, 91, 97

   Suggest keeping: lines 5 (intro), 31 (H2), 67 (table)
   Suggest replacing: 12 others

   Fix density? [Y/n]
   ```

2. If user confirms, show each replacement:
   ```
   Line 12: "активная пена быстро удаляет"
         → "активное средство быстро удаляет"
   Apply? [Y/n/edit]
   ```

3. After all replacements, re-validate
4. Show before/after comparison
```

### 4. uk-verify-content/SKILL.md

Same addition with UK text.

---

## Validation After Changes

After implementing, test with:

```bash
# Find category with density issues
python3 scripts/validate_density.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md --lang uk

# Run skill
/uk-content-reviewer aktivnaya-pena

# Verify fix worked
python3 scripts/validate_density.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md --lang uk
```

---

## Out of Scope

- Hardcoded synonym dictionary (LLM handles this)
- Changes to validator scripts (they already work)
- Fixing the UK stopwords bug (separate issue)
- Fixing failing tests (separate issue)

---

## Implementation Order

1. Update content-reviewer/SKILL.md (RU autonomous)
2. Update uk-content-reviewer/SKILL.md (UK autonomous)
3. Update verify-content/SKILL.md (RU interactive)
4. Update uk-verify-content/SKILL.md (UK interactive)
5. Test on one category each language
6. Batch run on all categories

---

**Version:** 1.0
