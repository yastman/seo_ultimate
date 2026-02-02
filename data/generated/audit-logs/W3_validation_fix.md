# W3: Update audit_coverage.py verbose output

**Task:** Task 3 from docs/plans/2026-01-30-validation-skills-fix-plan.md
**Date:** 2026-01-30
**Worker:** W3

## Progress

### Step 1: Analyze current code ✅

Found `print_verbose` function (lines 206-246):
- Line 220: SYNONYM in COVERED section: `for status in ["EXACT", "NORM", "LEMMA", "SYNONYM"]`
- Line 234: NOT COVERED section: `for status in ["TOKENIZATION", "PARTIAL", "ABSENT"]`

Issue: SYNONYM should be in NOT COVERED after Task 2 changes.

### Step 2: Make changes ✅

**Change 1:** Removed SYNONYM from COVERED list (line 220)
```python
# Before:
for status in ["EXACT", "NORM", "LEMMA", "SYNONYM"]:

# After:
for status in ["EXACT", "NORM", "LEMMA"]:
```

**Change 2:** Added SYNONYM to NOT COVERED list (line 232)
```python
# Before:
for status in ["TOKENIZATION", "PARTIAL", "ABSENT"]:

# After:
for status in ["SYNONYM", "TOKENIZATION", "PARTIAL", "ABSENT"]:
```

**Change 3:** Added special formatting for SYNONYM in NOT COVERED output
```python
if r["status"] == "SYNONYM":
    extra = f' ← via "{r["covered_by"]}" [{r["syn_match_method"]}]'
else:
    extra = f" — {r['reason']}" if r.get("reason") else ""
```

### Step 3: Test verbose output ✅

```bash
python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --verbose
```

**Output:**
```
=== aktivnaya-pena (uk) ===
Coverage: 4/11 (36.4%)

✓ EXACT (2):
  - піна для миття авто (1300)
  - активна піна (1000)

✓ NORM (1):
  - активна піна для безконтактної мийки (320)

✗ NOT COVERED (8):
  - [SYNONYM] активна піна для авто (1600) ← via "активна піна для миття авто" [NORM]
  - [PARTIAL] хімія для миття авто (1000) — 100% lemmas found
  ...
```

✅ SYNONYM correctly appears in NOT COVERED section with proper formatting.

## Summary

Task 3 completed successfully:
- SYNONYM moved from COVERED to NOT COVERED section in verbose output
- Special formatting shows synonym match info: `← via "synonym" [method]`
- Tested and verified on aktivnaya-pena UK category

**Note:** Coverage count (4/11) still includes SYNONYM as covered because Task 2 (change covered=False in coverage_matcher.py) not yet completed. After Task 2, the count will update correctly.

---
**Status:** ✅ DONE
**Files modified:** `scripts/audit_coverage.py`
**No git commit** (per instructions)
