# W2: Update uk-content-reviewer SKILL.md

**Date:** 2026-02-02
**Task:** Task 2 from docs/plans/2026-02-02-density-nausea-fix.md
**Worker:** W2

## Summary

Added Step 9a (Density/Nausea fix) to uk-content-reviewer skill for automated synonym replacement when density/nausea validators fail.

## Changes Made

### File: `.claude/skills/uk-content-reviewer/SKILL.md`

1. **Workflow list updated** (line 83)
   - Added: `Step 9a: Fix Density/Nausea (if BLOCKER)`
   - Position: After Step 9, before Step 10

2. **Step 9a section added** (lines 237-275)
   - Trigger: validate_density.py stem >3.0% OR check_water_natasha.py nausea >4.0
   - Algorithm: identify overused word → keep 3-4 occurrences → replace rest with synonyms
   - Common UK alternatives: "засіб", "склад", "продукт", "формула"
   - Re-validate command included
   - Max 3 iterations
   - Example before/after

3. **BLOCKER Fixes table updated** (line 342)
   - Changed: `| Stem >3.0% | Replace with synonyms |`
   - To: `| Stem >3.0% | Step 9a: auto-replace with synonyms |`

4. **Version updated** (line 396)
   - From: 2.3 — January 2026
   - To: 2.4 — February 2026

5. **Changelog v2.4 added** (lines 398-400)
   - ADDED: Step 9a — auto-fix density/nausea with synonym replacement
   - Iterative cycle: fix → re-validate → repeat (max 3 iterations)

## Verification

- [x] Step 9a in Workflow list
- [x] Step 9a section exists between Step 8 (Verdict) and Step 10 (Re-validate)
- [x] BLOCKER Fixes table references Step 9a
- [x] Version bumped to 2.4
- [x] Changelog v2.4 added

## Status

**DONE** - No commit (per instructions)
