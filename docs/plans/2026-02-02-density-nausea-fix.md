# Density/Nausea Auto-Fix Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add iterative density/nausea fix cycle to all 4 validation skills (content-reviewer, uk-content-reviewer, verify-content, uk-verify-content).

**Architecture:** Each skill gets a new Step/Phase that: (1) parses validator output to find overused words, (2) replaces excess occurrences with contextual synonyms, (3) re-validates, (4) repeats up to 3 times.

**Tech Stack:** Markdown skill files, no code changes to validators.

---

## Task 1: Update content-reviewer (RU Autonomous)

**Files:**
- Modify: `.claude/skills/content-reviewer/SKILL.md`

**Step 1: Read current skill file**

Read `.claude/skills/content-reviewer/SKILL.md` to understand current structure.

**Step 2: Add Step 8a after Step 8**

Insert new section after "Step 8: Fix if BLOCKER" and before "Step 9: Re-validate Coverage":

```markdown
### Step 8a: Fix Density/Nausea (if BLOCKER)

**Trigger:** Step 2 validators show:
- `validate_density.py`: stem >3.0%
- `check_water_natasha.py`: classic nausea >4.0

**Algorithm:**

1. From validator output, identify overused word:
   - Density: `"пена*" — 15 раз (3.8%)`
   - Nausea: `Самое частое слово: 'пена' (15 раз)`

2. Find all occurrences in `{slug}_ru.md`

3. Decide which to keep (3-4 max):
   - ✅ Keep: first mention in intro
   - ✅ Keep: H2 headings
   - ✅ Keep: table headers
   - ❌ Replace: body text repetitions

4. Replace excess with contextual synonyms:
   - Choose synonym based on sentence context
   - Match grammatical case/gender
   - Common alternatives: "средство", "состав", "продукт", "формула"

5. Re-run validator:
   ```bash
   python3 scripts/validate_density.py categories/{path}/content/{slug}_ru.md
   ```

6. Repeat until ≤2.5% or max 3 iterations

7. Log all replacements made

**Example:**
```
Before: "пена" × 15 (3.8%)
After:  "пена" × 4 + "средство" × 5 + "состав" × 3 + "продукт" × 3 = 1.0%
```
```

**Step 3: Update BLOCKER Fixes table**

Find the BLOCKER Fixes table and update the Stem row:

```markdown
| Stem >3.0% | Step 8a: auto-replace with synonyms |
```

**Step 4: Update Workflow list**

Update the Workflow section to include Step 8a:

```markdown
## Workflow

```
Step 1: Read files (parallel)
Step 2: Run validators (parallel)
Step 3: Keywords Coverage (100% required)
Step 4: Research Completeness
Step 5: Commercial Intent Check
Step 6: Dryness Diagnosis
Step 7: Verdict table
Step 8: Fix if BLOCKER or REWRITE if needed
Step 8a: Fix Density/Nausea (if BLOCKER)
Step 9: Re-validate Coverage (max 3 iterations)
Step 10: Output verdict
```
```

**Step 5: Update version**

Update version at bottom:

```markdown
**Version:** 2.2 — February 2026

**Changelog v2.2:**
- **ADDED: Step 8a** — auto-fix density/nausea with synonym replacement
- Iterative cycle: fix → re-validate → repeat (max 3 iterations)
```

**Step 6: Verify changes**

Read the modified file and confirm:
- Step 8a exists between Step 8 and Step 9
- BLOCKER Fixes table updated
- Workflow list updated
- Version bumped

---

## Task 2: Update uk-content-reviewer (UK Autonomous)

**Files:**
- Modify: `.claude/skills/uk-content-reviewer/SKILL.md`

**Step 1: Read current skill file**

Read `.claude/skills/uk-content-reviewer/SKILL.md`.

**Step 2: Add Step 9a after Step 9**

Insert new section after "Step 9: Fix if BLOCKER" and before "Step 10: Re-validate":

```markdown
### Step 9a: Fix Density/Nausea (if BLOCKER)

**Trigger:** Step 2 validators show:
- `validate_density.py`: stem >3.0%
- `check_water_natasha.py`: classic nausea >4.0

**Algorithm:**

1. From validator output, identify overused word:
   - Density: `"піна*" — 15 раз (3.8%)`
   - Nausea: `Самое частое слово: 'піна' (15 раз)`

2. Find all occurrences in `{slug}_uk.md`

3. Decide which to keep (3-4 max):
   - ✅ Keep: first mention in intro
   - ✅ Keep: H2 headings
   - ✅ Keep: table headers
   - ❌ Replace: body text repetitions

4. Replace excess with contextual synonyms:
   - Choose synonym based on sentence context
   - Match grammatical case/gender
   - Common alternatives: "засіб", "склад", "продукт", "формула"

5. Re-run validator:
   ```bash
   python3 scripts/validate_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
   ```

6. Repeat until ≤2.5% or max 3 iterations

7. Log all replacements made

**Example:**
```
Before: "піна" × 15 (3.8%)
After:  "піна" × 4 + "засіб" × 5 + "склад" × 3 + "продукт" × 3 = 1.0%
```
```

**Step 3: Update BLOCKER Fixes table**

```markdown
| Stem >3.0% | Step 9a: auto-replace with synonyms |
```

**Step 4: Update Workflow list**

```markdown
## Workflow

```
Step 1: Read files (parallel)
Step 2: Run validators (parallel)
Step 3: Keywords Coverage (audit_coverage.py)
Step 4: Research Completeness
Step 5: Commercial Intent Check
Step 6: Dryness Diagnosis
Step 7: UK Terminology Check
Step 8: Verdict table
Step 9: Fix if BLOCKER or REWRITE if needed
Step 9a: Fix Density/Nausea (if BLOCKER)
Step 10: Re-validate
Step 11: Output verdict
```
```

**Step 5: Update version**

```markdown
**Version:** 2.4 — February 2026

**Changelog v2.4:**
- **ADDED: Step 9a** — auto-fix density/nausea with synonym replacement
- Iterative cycle: fix → re-validate → repeat (max 3 iterations)
```

**Step 6: Verify changes**

Confirm all sections updated correctly.

---

## Task 3: Update verify-content (RU Interactive)

**Files:**
- Modify: `.claude/skills/verify-content/SKILL.md`

**Step 1: Read current skill file**

Read `.claude/skills/verify-content/SKILL.md`.

**Step 2: Add Phase 2a after Phase 2**

Since verify-content runs validators in Phase 2, add density fix phase right after. Insert after Phase 2 (Facts Verification becomes Phase 3, etc.):

```markdown
### Phase 2a: Density/Nausea Fix (if needed)

**Trigger:** Phase 2 validators show stem >3.0% OR nausea >4.0

1. Show issue summary:
   ```
   ## Density Issue

   Word "пена" appears 15 times (3.8%)
   Target: 3-4 times (≤2.5%)

   Occurrences found at lines: 5, 12, 18, 23, 31, 42, 48, 55, 61, 67, 73, 79, 85, 91, 97

   Recommend keeping:
   - Line 5 (intro - first mention)
   - Line 31 (H2 heading)
   - Line 67 (table header)
   - Line 85 (FAQ)

   Recommend replacing: 11 others

   Fix density now? [Y/n]
   ```

2. If user confirms, show each replacement proposal:
   ```
   Line 12: "активная пена быстро удаляет грязь"
         → "активное средство быстро удаляет грязь"

   Apply? [Y/n/edit]
   ```

3. After all replacements, re-run validator:
   ```bash
   python3 scripts/validate_density.py categories/{path}/content/{slug}_ru.md
   ```

4. Show before/after:
   ```
   ## Density Fix Result

   | Metric | Before | After |
   |--------|--------|-------|
   | "пена" count | 15 | 4 |
   | Density | 3.8% | 1.0% |
   | Status | ❌ BLOCKER | ✅ PASS |
   ```

5. If still >2.5%, offer to continue (max 3 iterations)
```

**Step 3: Renumber subsequent phases**

Update phase numbers:
- Phase 2 → Phase 2 (unchanged)
- NEW Phase 2a (density fix)
- Phase 3 (was 2) → Phase 3: AI Patterns
- Phase 4 (was 3) → Phase 4: Keywords Coverage
- etc.

Actually, simpler approach - keep Phase 2a as inserted, no renumbering needed.

**Step 4: Add to Verdict actions**

In Phase 6 Verdict, the actions list already has `[D] Fix density/nausea`. Verify it exists, no change needed.

**Step 5: Update version**

```markdown
**Version:** 1.4 — February 2026

**Changelog v1.4:**
- **ADDED: Phase 2a** — interactive density/nausea fix
- Shows each replacement, asks for confirmation
- Before/after comparison table
```

**Step 6: Verify changes**

Confirm Phase 2a added correctly.

---

## Task 4: Update uk-verify-content (UK Interactive)

**Files:**
- Modify: `.claude/skills/uk-verify-content/SKILL.md`

**Step 1: Read current skill file**

Read `.claude/skills/uk-verify-content/SKILL.md`.

**Step 2: Add Phase 2a after Phase 2**

Insert after Phase 2 (Run Validators):

```markdown
### Phase 2a: Density/Nausea Fix (if needed)

**Trigger:** Phase 2 validators show stem >3.0% OR nausea >4.0

1. Show issue summary:
   ```
   ## Density Issue

   Word "піна" appears 15 times (3.8%)
   Target: 3-4 times (≤2.5%)

   Occurrences found at lines: 5, 12, 18, 23, 31, 42, 48, 55, 61, 67, 73, 79, 85, 91, 97

   Recommend keeping:
   - Line 5 (intro - first mention)
   - Line 31 (H2 heading)
   - Line 67 (table header)
   - Line 85 (FAQ)

   Recommend replacing: 11 others

   Fix density now? [Y/n]
   ```

2. If user confirms, show each replacement proposal:
   ```
   Line 12: "активна піна швидко видаляє бруд"
         → "активний засіб швидко видаляє бруд"

   Apply? [Y/n/edit]
   ```

3. After all replacements, re-run validator:
   ```bash
   python3 scripts/validate_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
   ```

4. Show before/after:
   ```
   ## Density Fix Result

   | Metric | Before | After |
   |--------|--------|-------|
   | "піна" count | 15 | 4 |
   | Density | 3.8% | 1.0% |
   | Status | ❌ BLOCKER | ✅ PASS |
   ```

5. If still >2.5%, offer to continue (max 3 iterations)
```

**Step 3: Update version**

```markdown
**Version:** 1.4 — February 2026

**Changelog v1.4:**
- **ADDED: Phase 2a** — interactive density/nausea fix
- Shows each replacement, asks for confirmation
- Before/after comparison table
- SYNCED with RU verify-content v1.4
```

**Step 4: Verify changes**

Confirm Phase 2a added correctly.

---

## Task 5: Test RU Autonomous (content-reviewer)

**Files:**
- Test category: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/`

**Step 1: Check current density**

```bash
python3 scripts/validate_density.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
```

Note the output - if already PASS, find another category with density issues.

**Step 2: Run skill (manual test)**

In a new Claude session, run:
```
/content-reviewer moyka-i-eksterer/avtoshampuni/aktivnaya-pena
```

Observe if Step 8a triggers when density >3.0%.

**Step 3: Verify fix applied**

```bash
python3 scripts/validate_density.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
```

Confirm density reduced.

---

## Task 6: Test UK Autonomous (uk-content-reviewer)

**Files:**
- Test category: `uk/categories/aktivnaya-pena/`

**Step 1: Check current density**

```bash
python3 scripts/validate_density.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md --lang uk
```

**Step 2: Run skill (manual test)**

```
uk-content-reviewer aktivnaya-pena
```

**Step 3: Verify fix applied**

```bash
python3 scripts/validate_density.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md --lang uk
```

---

## Task 7: Commit Changes

**Step 1: Stage skill files**

```bash
git add .claude/skills/content-reviewer/SKILL.md
git add .claude/skills/uk-content-reviewer/SKILL.md
git add .claude/skills/verify-content/SKILL.md
git add .claude/skills/uk-verify-content/SKILL.md
```

**Step 2: Commit**

```bash
git commit -m "feat(skills): add density/nausea auto-fix to validation skills

- content-reviewer: Step 8a for RU autonomous fix
- uk-content-reviewer: Step 9a for UK autonomous fix
- verify-content: Phase 2a for RU interactive fix
- uk-verify-content: Phase 2a for UK interactive fix

Algorithm: find overused word → keep 3-4 occurrences → replace rest with synonyms → re-validate → repeat max 3x

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Summary

| Task | File | Change |
|------|------|--------|
| 1 | content-reviewer/SKILL.md | Add Step 8a |
| 2 | uk-content-reviewer/SKILL.md | Add Step 9a |
| 3 | verify-content/SKILL.md | Add Phase 2a |
| 4 | uk-verify-content/SKILL.md | Add Phase 2a |
| 5 | — | Test RU autonomous |
| 6 | — | Test UK autonomous |
| 7 | — | Commit |

**Estimated tasks:** 7
**Dependencies:** Tasks 1-4 independent, can run in parallel. Tasks 5-6 depend on 1-4. Task 7 depends on all.
