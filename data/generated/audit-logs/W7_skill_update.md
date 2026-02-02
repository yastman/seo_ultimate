# W7: Update quality-gate skill

**Date:** 2026-01-30
**Task:** Task 7 from docs/plans/2026-01-30-validation-skills-fix-plan.md
**Status:** COMPLETE

---

## Changes Made

### File: `.claude/skills/quality-gate/SKILL.md`

| Line | Old | New |
|------|-----|-----|
| 73 | `check_keyword_density.py` | `validate_density.py` |
| 111 | `check_seo_structure.py` | `validate_seo.py` |
| 260 | `check_keyword_density.py` | `validate_density.py` |

### Specific Edits

1. **RU Content Validation (Section 3)**
   - `python3 scripts/check_keyword_density.py categories/{slug}/content/{slug}_ru.md`
   - → `python3 scripts/validate_density.py categories/{slug}/content/{slug}_ru.md`

2. **SEO Structure Check (Section 4)**
   - `python scripts/check_seo_structure.py categories/{slug}/content/{slug}_ru.md`
   - → `python3 scripts/validate_seo.py categories/{slug}/content/{slug}_ru.md`
   - Also fixed: `python` → `python3`

3. **UK Validation Commands**
   - `python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk`
   - → `python3 scripts/validate_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk`

---

## Coverage Rules Documentation

Reviewed coverage rules in the skill - they are already correct:

```
**Keywords Coverage (audit_coverage.py --json --include-meta):**

| Источник | Группа | Требование | При фейле |
|----------|--------|------------|-----------|
| keywords_in_content | primary | 100% COVERED | BLOCKER |
| keywords_in_content | secondary | 100% COVERED | BLOCKER |
| keywords_in_content | supporting | ≥80% COVERED | WARNING |
| keywords[] | all | adaptive threshold | WARNING |

Adaptive thresholds: ≤5 ключей → 70%, 6-15 → 60%, >15 → 50%
```

No updates needed for coverage rules.

---

## Verification

Confirmed no remaining references to old script names in quality-gate skill:
- ✅ No `check_keyword_density.py` references
- ✅ No `check_seo_structure.py` references

---

## Git Status

Changes NOT committed (per instructions).
File modified: `.claude/skills/quality-gate/SKILL.md`
