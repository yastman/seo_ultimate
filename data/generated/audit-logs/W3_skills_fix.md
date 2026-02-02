# W3: Skills Fix Log — 2026-02-02

## Task Assigned

**Task 5:** Update shared/validation-checklist.md — Add Keywords Coverage section

## Changes Made

**File:** `.claude/skills/shared/validation-checklist.md`

Added new section "## Keywords Coverage (audit_coverage.py)" after "## Commands" section:

1. **Command:** `python3 scripts/audit_coverage.py --slug {slug} --lang {ru|uk} --json --include-meta`

2. **Coverage statuses:**
   - ✅ COVERED: `EXACT`, `NORM`, `LEMMA`
   - ❌ NOT COVERED: `SYNONYM`, `PARTIAL`, `ABSENT`

3. **SYNONYM = NOT COVERED clarification:** Синонім знайдено в тексті, але сам ключ відсутній. Для SEO потрібен саме ключ.

4. **Rules table:**
   | Джерело | Вимога | Severity |
   |---------|--------|----------|
   | primary+secondary | 100% COVERED | BLOCKER |
   | supporting | ≥80% COVERED | WARNING |
   | keywords[] | adaptive threshold | BLOCKER |

5. **Adaptive thresholds:** ≤5 ключів → 70%, 6-15 → 60%, >15 → 50%

6. **Iteration loop:** max 3 ітерації (Fix → Re-validate → Check)

## Verification

```bash
grep -c "Keywords Coverage" .claude/skills/shared/validation-checklist.md  # Result: 1 ✅
grep -c "SYNONYM = NOT COVERED" .claude/skills/shared/validation-checklist.md  # Result: 1 ✅
grep -c "Adaptive thresholds" .claude/skills/shared/validation-checklist.md  # Result: 1 ✅
grep -c "max 3" .claude/skills/shared/validation-checklist.md  # Result: 1 ✅
```

## Status

✅ Task 5 completed — shared/validation-checklist.md updated with Keywords Coverage section

**Note:** git commit НЕ виконувався — коміти робить оркестратор
