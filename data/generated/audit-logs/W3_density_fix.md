# W3: Density Fix - verify-content SKILL.md Update

**Date:** 2026-02-02
**Task:** Task 3 from docs/plans/2026-02-02-density-nausea-fix.md
**Worker:** W3

## Changes Made

### File: `.claude/skills/verify-content/SKILL.md`

**1. Added Phase 2a: Density/Nausea Fix (if needed)**

Inserted after Phase 2 (Facts Verification), before Phase 3 (AI Patterns Detection).

Phase 2a includes:
- Trigger: Run validators `validate_density.py` and `check_water_natasha.py`
- BLOCKER if: stem >3.0% OR classic nausea >4.0
- Interactive flow:
  1. Show issue summary with line numbers and recommendations
  2. Ask user confirmation to fix
  3. Show each replacement proposal with Apply? [Y/n/edit]
  4. Re-run validator after replacements
  5. Show before/after comparison table
  6. Repeat up to 3 iterations if still >2.5%

**2. Updated Version**

- Version: 1.3 → 1.4
- Added Changelog v1.4:
  - ADDED: Phase 2a — interactive density/nausea fix
  - Shows each replacement, asks for confirmation
  - Before/after comparison table

## Summary

| Step | Status |
|------|--------|
| Read plan | Done |
| Read current skill | Done |
| Add Phase 2a | Done |
| Update version | Done |
| Write log | Done |
| Git commit | SKIPPED (per instructions) |

## No Commit

As instructed, no git commit was made.
