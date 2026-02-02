# Fix Validation Skills for 100% Coverage Loop — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Синхронізувати RU та UK скіли валідації для забезпечення однакового циклу "validate → fix → re-validate → 100% coverage"

**Architecture:** Оновити 4 скіли (content-reviewer, verify-content, quality-gate, uk-quality-gate) додавши: max 3 ітерації циклу виправлень, явне "SYNONYM = NOT COVERED", BLOCKER severity для keywords[]. Прибрати застарілі посилання на неіснуючі скрипти.

**Tech Stack:** Markdown skill files, Bash validation scripts

---

## Task 1: Update content-reviewer (RU) — Add Coverage Loop

**Files:**
- Modify: `.claude/skills/content-reviewer/SKILL.md`

**Step 1: Read current SKILL.md**

Run: `head -150 .claude/skills/content-reviewer/SKILL.md`
Expected: Current content without iteration loop

**Step 2: Add SYNONYM = NOT COVERED clarification to Step 3**

Find in `.claude/skills/content-reviewer/SKILL.md`:
```markdown
**COVERED** = EXACT / NORM / LEMMA
**NOT COVERED** = SYNONYM / PARTIAL / ABSENT
```

Replace with:
```markdown
**Статуси покриття:**
- ✅ COVERED: `EXACT`, `NORM`, `LEMMA`
- ❌ NOT COVERED: `SYNONYM`, `PARTIAL`, `ABSENT`

> **SYNONYM = NOT COVERED:** Синонім знайдено в тексті, але сам ключ — відсутній. Для SEO потрібен саме ключ.
```

**Step 3: Change keywords[] severity from WARNING to BLOCKER**

Find:
```markdown
| keywords[] | all | adaptive threshold | BLOCKER |
```

This is already BLOCKER. Verify it's present.

**Step 4: Add Re-validate Coverage step after Step 8**

Add new Step 9 after current "Step 8: Fix if BLOCKER or REWRITE if needed":

```markdown
### Step 9: Re-validate Coverage (MANDATORY)

**Обов'язково після будь-яких виправлень!**

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang ru --json --include-meta
```

**Цикл виправлень (max 3 ітерації):**

```
Iteration 1: Fix → Re-validate → check NOT COVERED
Iteration 2: Fix remaining → Re-validate → check NOT COVERED
Iteration 3: Fix remaining → Re-validate → STOP
```

**Якщо після 3 ітерацій залишаються NOT COVERED:**
- Задокументувати в логу які ключі не вдалося вставити
- Перейти до фінального verdict

**Куди вставляти непокриті ключі:**

| Пріоритет | Куди | Приклад |
|-----------|------|---------|
| **primary** | Intro (перший абзац) | "...{keyword} поможет..." |
| **secondary** | H2 заголовки | "## Как выбрать {keyword}" |
| **supporting** | Сценарии, таблицы, FAQ | "**Для {keyword}** — ..." |

**Техніка органічного впровадження:**
- Знайди речення за змістом близьке до ключа
- Переформулюй з включенням ключа
- НЕ додавай нові факти — використовуй RESEARCH_DATA.md
```

**Step 5: Update Workflow list**

Find:
```markdown
Step 8: Fix if BLOCKER or REWRITE if needed
Step 9: Re-validate
Step 10: Output verdict
```

Replace with:
```markdown
Step 8: Fix if BLOCKER or REWRITE if needed
Step 9: Re-validate Coverage (max 3 iterations)
Step 10: Output verdict
```

**Step 6: Add Changelog v2.1**

Add at the end of file before last empty line:

```markdown
---

**Version:** 2.1 — February 2026

**Changelog v2.1:**
- **SYNCED with UK v2.3** — повний паритет
- ADDED: max 3 ітерації для циклу виправлень
- ADDED: SYNONYM = NOT COVERED (explicit)
- ADDED: Таблиця куди вставляти непокриті ключі
- ADDED: Техніка органічного впровадження
```

**Step 7: Validate changes**

Run: `grep -c "max 3" .claude/skills/content-reviewer/SKILL.md`
Expected: 1 or more matches

Run: `grep -c "SYNONYM = NOT COVERED" .claude/skills/content-reviewer/SKILL.md`
Expected: 1 or more matches

**Step 8: Commit**

```bash
git add .claude/skills/content-reviewer/SKILL.md
git commit -m "feat(skills): sync content-reviewer with UK v2.3

- Add max 3 iterations loop for coverage fixes
- Add SYNONYM = NOT COVERED clarification
- Add table for keyword placement priorities
- Add organic integration technique

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Update verify-content (RU) — Add SYNONYM Clarification

**Files:**
- Modify: `.claude/skills/verify-content/SKILL.md`

**Step 1: Fix SYNONYM status in Phase 4**

Find in `.claude/skills/verify-content/SKILL.md`:
```markdown
**COVERED** = EXACT / NORM / LEMMA / SYNONYM
**NOT COVERED** = TOKENIZATION / PARTIAL / ABSENT
```

Replace with:
```markdown
**Статуси покриття:**
- ✅ COVERED: `EXACT`, `NORM`, `LEMMA`
- ❌ NOT COVERED: `SYNONYM`, `PARTIAL`, `ABSENT`

> **SYNONYM = NOT COVERED:** Синонім знайдено в тексті, але сам ключ — відсутній. Для SEO потрібен саме ключ.
```

**Step 2: Add iteration loop instruction to Phase 7**

Find:
```markdown
### Phase 7: Fix Mode
```

Add after this heading and before "If user chooses to fix:":

```markdown
**Цикл виправлень (max 3 ітерації):**
- Iteration 1-3: Fix → Re-validate → check NOT COVERED
- Після 3 ітерацій: STOP і задокументувати невирішені

```

**Step 3: Update Changelog**

Find:
```markdown
**Version:** 1.2 — January 2026
```

Replace with:
```markdown
**Version:** 1.3 — February 2026

**Changelog v1.3:**
- **FIXED: SYNONYM = NOT COVERED** — синонім не замінює ключ для SEO
- ADDED: max 3 ітерації для циклу виправлень

**Changelog v1.2:**
```

**Step 4: Validate changes**

Run: `grep -c "SYNONYM = NOT COVERED" .claude/skills/verify-content/SKILL.md`
Expected: 1 or more matches

**Step 5: Commit**

```bash
git add .claude/skills/verify-content/SKILL.md
git commit -m "feat(skills): add SYNONYM=NOT COVERED to verify-content

- Fix SYNONYM status (was incorrectly COVERED)
- Add max 3 iterations for fix loop

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Cleanup quality-gate (RU) — Remove Obsolete Scripts

**Files:**
- Modify: `.claude/skills/quality-gate/SKILL.md`

**Step 1: Remove check_h1_sync.py reference**

Find in `.claude/skills/quality-gate/SKILL.md`:
```markdown
# H1 sync check
python3 scripts/check_h1_sync.py --lang uk
```

Delete these 2 lines (they are in UK Support section, lines ~263-264).

**Step 2: Remove check_semantic_coverage.py reference**

Find:
```markdown
# Semantic coverage
python3 scripts/check_semantic_coverage.py --lang uk
```

Delete these 2 lines (lines ~266-267).

**Step 3: Add SYNONYM clarification to Keywords Coverage section**

Find in Section 3 Content Validation:
```markdown
**COVERED** = EXACT / NORM / LEMMA
**NOT COVERED** = TOKENIZATION / PARTIAL / ABSENT → фейл групи
```

If present, replace with:
```markdown
**Статуси покриття:**
- ✅ COVERED: `EXACT`, `NORM`, `LEMMA`
- ❌ NOT COVERED: `SYNONYM`, `PARTIAL`, `ABSENT`

> **SYNONYM = NOT COVERED** — синонім не замінює ключ для SEO.
```

If not present, add after Keywords Coverage table.

**Step 4: Update Changelog**

Find:
```markdown
**Version:** 3.1 — January 2026
```

Replace with:
```markdown
**Version:** 3.2 — February 2026

**Changelog v3.2:**
- **REMOVED: check_h1_sync.py** — скрипт не існує
- **REMOVED: check_semantic_coverage.py** — скрипт не існує
- **ADDED: SYNONYM = NOT COVERED** — явне роз'яснення

**Changelog v3.1:**
```

**Step 5: Validate changes**

Run: `grep -c "check_semantic_coverage" .claude/skills/quality-gate/SKILL.md`
Expected: 0

Run: `grep -c "check_h1_sync" .claude/skills/quality-gate/SKILL.md`
Expected: 0

**Step 6: Commit**

```bash
git add .claude/skills/quality-gate/SKILL.md
git commit -m "fix(skills): remove obsolete script refs from quality-gate

- Remove check_h1_sync.py (script doesn't exist)
- Remove check_semantic_coverage.py (script doesn't exist)
- Add SYNONYM = NOT COVERED clarification

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Cleanup uk-quality-gate — Remove Obsolete Scripts

**Files:**
- Modify: `.claude/skills/uk-quality-gate/skill.md`

**Step 1: Remove check_h1_sync.py reference**

Find in `.claude/skills/uk-quality-gate/skill.md`:
```markdown
# H1 sync check
python3 scripts/check_h1_sync.py --lang uk
```

Delete these 2 lines (in Step 1: Run All Validations, around line 223-224).

**Step 2: Remove check_semantic_coverage.py reference**

Find:
```markdown
# Semantic coverage check
python3 scripts/check_semantic_coverage.py --lang uk
```

Delete these 2 lines (around line 226-227).

**Step 3: Fix SYNONYM status in Section 8**

Find:
```markdown
**COVERED** = EXACT / NORM / LEMMA / SYNONYM
**NOT COVERED** = TOKENIZATION / PARTIAL / ABSENT → фейл групи
```

Replace with:
```markdown
**Статуси покриття:**
- ✅ COVERED: `EXACT`, `NORM`, `LEMMA`
- ❌ NOT COVERED: `SYNONYM`, `PARTIAL`, `ABSENT`

> **SYNONYM = NOT COVERED** — синонім не замінює ключ для SEO.
```

**Step 4: Update Changelog**

Find:
```markdown
**Version:** 3.2
```

Replace with:
```markdown
**Version:** 3.3 — February 2026

**Changelog v3.3:**
- **REMOVED: check_h1_sync.py** — скрипт не існує
- **REMOVED: check_semantic_coverage.py** — скрипт не існує
- **FIXED: SYNONYM = NOT COVERED** — виправлено статус

**Changelog v3.2:**
```

**Step 5: Validate changes**

Run: `grep -c "check_semantic_coverage" .claude/skills/uk-quality-gate/skill.md`
Expected: 0

Run: `grep -c "check_h1_sync" .claude/skills/uk-quality-gate/skill.md`
Expected: 0

Run: `grep -c "SYNONYM = NOT COVERED" .claude/skills/uk-quality-gate/skill.md`
Expected: 1 or more

**Step 6: Commit**

```bash
git add .claude/skills/uk-quality-gate/skill.md
git commit -m "fix(skills): remove obsolete script refs from uk-quality-gate

- Remove check_h1_sync.py (script doesn't exist)
- Remove check_semantic_coverage.py (script doesn't exist)
- Fix SYNONYM status to NOT COVERED

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Update shared/validation-checklist.md

**Files:**
- Modify: `.claude/skills/shared/validation-checklist.md`

**Step 1: Add Keywords Coverage section**

Add after "## Commands" section:

```markdown
---

## Keywords Coverage (audit_coverage.py)

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang {ru|uk} --json --include-meta
```

**Статуси покриття:**
- ✅ COVERED: `EXACT`, `NORM`, `LEMMA`
- ❌ NOT COVERED: `SYNONYM`, `PARTIAL`, `ABSENT`

> **SYNONYM = NOT COVERED** — синонім знайдено в тексті, але сам ключ відсутній. Для SEO потрібен саме ключ.

**Правила:**

| Джерело | Вимога | Severity |
|---------|--------|----------|
| primary+secondary | **100% COVERED** | BLOCKER |
| supporting | **≥80% COVERED** | WARNING |
| keywords[] | adaptive threshold | BLOCKER |

**Adaptive thresholds:** ≤5 ключів → 70%, 6-15 → 60%, >15 → 50%

**Цикл виправлень:** max 3 ітерації (Fix → Re-validate → Check)
```

**Step 2: Validate changes**

Run: `grep -c "SYNONYM = NOT COVERED" .claude/skills/shared/validation-checklist.md`
Expected: 1 or more

**Step 3: Commit**

```bash
git add .claude/skills/shared/validation-checklist.md
git commit -m "docs(skills): add Keywords Coverage section to shared checklist

- Add audit_coverage.py usage
- Add coverage statuses explanation
- Add SYNONYM = NOT COVERED clarification
- Add iteration loop reference

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Validation — Test on Real Category

**Files:**
- Read only: `uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md`

**Step 1: Run audit_coverage.py on UK aktivnaya-pena**

Run: `python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --verbose --include-meta`

Expected: Output showing NOT COVERED keywords with SYNONYM/PARTIAL/ABSENT status

**Step 2: Verify SYNONYM is NOT COVERED in output**

Check that any keyword with status=SYNONYM has covered=False

**Step 3: Run audit_coverage.py on RU aktivnaya-pena**

Run: `python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang ru --verbose --include-meta`

Expected: Output showing coverage status

**Step 4: Document validation results**

Create log entry in `data/generated/audit-logs/2026-02-02_skills_validation.md`:

```markdown
# Skills Validation Log — 2026-02-02

## Changes Made

1. content-reviewer (RU) v2.1 — added max 3 iterations, SYNONYM=NOT COVERED
2. verify-content (RU) v1.3 — fixed SYNONYM status, added iterations
3. quality-gate (RU) v3.2 — removed obsolete scripts, added SYNONYM clarification
4. uk-quality-gate v3.3 — removed obsolete scripts, fixed SYNONYM status
5. shared/validation-checklist.md — added Keywords Coverage section

## Validation Results

### UK aktivnaya-pena
- primary+secondary: X/X (X%)
- supporting: X/X (X%)
- keywords[]: X/X (X%)
- SYNONYM keywords detected: [list]

### RU aktivnaya-pena
- primary+secondary: X/X (X%)
- supporting: X/X (X%)
- keywords[]: X/X (X%)

## Status

✅ All skills updated and validated
```

**Step 5: Final commit**

```bash
git add data/generated/audit-logs/2026-02-02_skills_validation.md
git commit -m "docs: add skills validation log

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Summary

| Task | Skill | Key Changes |
|------|-------|-------------|
| 1 | content-reviewer (RU) | +max 3 iter, +SYNONYM=NOT COVERED, +placement table |
| 2 | verify-content (RU) | +SYNONYM=NOT COVERED, +max 3 iter |
| 3 | quality-gate (RU) | -obsolete scripts, +SYNONYM clarification |
| 4 | uk-quality-gate | -obsolete scripts, fix SYNONYM status |
| 5 | shared/validation-checklist | +Keywords Coverage section |
| 6 | Validation | Test on aktivnaya-pena RU/UK |

**Total commits:** 6

**Estimated changes:**
- 4 skill files modified
- 1 shared checklist updated
- 1 validation log created
