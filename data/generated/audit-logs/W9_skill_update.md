# W9: Update verify-content skill

**Date:** 2026-01-30
**Task:** Task 9 from docs/plans/2026-01-30-validation-skills-fix-plan.md

## Objective

Replace deprecated script names in `.claude/skills/verify-content/SKILL.md`:
- `check_keyword_density.py` → `validate_density.py`
- `check_seo_structure.py` → `validate_seo.py`

## Analysis

Read `.claude/skills/verify-content/SKILL.md` (256 lines).

**Scripts mentioned in the file:**
- `python3 scripts/audit_coverage.py --slug {slug} --lang ru --json --include-meta` (line 101)

**Scripts NOT found:**
- `check_keyword_density.py` — ABSENT
- `check_seo_structure.py` — ABSENT

## Result

**NO CHANGES REQUIRED**

The verify-content skill uses `audit_coverage.py` for keyword validation (Phase 4), not the deprecated `check_keyword_density.py` or `check_seo_structure.py` scripts.

This skill was already updated in v1.1/v1.2 to use the new coverage audit system.

## Verification

Searched for patterns `check_keyword_density|check_seo_structure` in SKILL.md — no matches found.

---

**Status:** ✅ COMPLETE (no changes needed)
