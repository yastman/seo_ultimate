# W1: Update content-reviewer SKILL.md

**Date:** 2026-02-02
**Plan:** docs/plans/2026-02-02-density-nausea-fix.md — Task 1
**Worker:** W1

## Summary

Added Step 8a (Density/Nausea auto-fix) to content-reviewer skill.

## Changes Made

**File:** `.claude/skills/content-reviewer/SKILL.md`

### 1. Updated Workflow list (line 82)

Added Step 8a between Step 8 and Step 9:

```
Step 8: Fix if BLOCKER or REWRITE if needed
Step 8a: Fix Density/Nausea (if BLOCKER)  ← NEW
Step 9: Re-validate Coverage (max 3 iterations)
```

### 2. Added Step 8a section (lines 205-243)

New section with:
- **Trigger:** density >3.0% or nausea >4.0
- **Algorithm:** 7-step process (identify overused word → find occurrences → decide which to keep → replace with synonyms → re-validate → repeat max 3x → log)
- **Example:** "пена" × 15 (3.8%) → "пена" × 4 + synonyms = 1.0%

### 3. Updated BLOCKER Fixes table (line 288)

```
Before: | Stem >3.0% | Replace with synonyms |
After:  | Stem >3.0% | Step 8a: auto-replace with synonyms |
```

### 4. Updated version (line 340)

```
Before: **Version:** 2.1 — February 2026
After:  **Version:** 2.2 — February 2026
```

Added changelog:
```markdown
**Changelog v2.2:**
- **ADDED: Step 8a** — auto-fix density/nausea with synonym replacement
- Iterative cycle: fix → re-validate → repeat (max 3 iterations)
```

### 5. Updated title (line 6)

```
Before: # Content Reviewer v2.0
After:  # Content Reviewer v2.2
```

## Verification

- [x] Step 8a exists between Step 8 and Step 9 in Workflow
- [x] Step 8a section added with full algorithm
- [x] BLOCKER Fixes table references Step 8a
- [x] Version bumped to 2.2
- [x] Changelog added

## Status

**DONE** — No git commit (as instructed)
