# W4 Log: seo_utils.py + utils/text.py Cleanup

**Date:** 2026-01-29
**Tasks:** 12-13
**Status:** COMPLETED

---

## Task 12: seo_utils.py

### Changes Made

1. **Added imports from keyword_utils:**
   ```python
   from scripts.keyword_utils import (
       get_adaptive_coverage_target as _get_adaptive_coverage_target,
   )
   from scripts.keyword_utils import (
       get_commercial_markers,
       get_stoplist_phrases,
   )
   ```

2. **Replaced `get_adaptive_coverage_target()`** (lines 53-62 -> line 58):
   - Old: Local implementation with config fallback
   - New: Simple wrapper calling `_get_adaptive_coverage_target()` from keyword_utils

3. **Removed local `COMMERCIAL_MARKERS` list** (23 items):
   - Replaced with `get_commercial_markers(lang)` call

4. **Added `find_commercial_markers()` function:**
   ```python
   def find_commercial_markers(text: str, lang: str = "ru") -> dict[str, int]:
       markers = get_commercial_markers(lang)
       found: dict[str, int] = {}
       text_lower = text.lower()
       for marker in markers:
           if marker in text_lower:
               count = text_lower.count(marker)
               found[marker] = count
       return found
   ```

5. **Updated `check_commercial_markers()`:**
   - Added `lang` parameter
   - Now uses `find_commercial_markers()` internally
   - Removed `missing_markers` from return (not needed)

6. **Removed local `STOPLIST_PHRASES` list** (21 items):
   - Replaced with `get_stoplist_phrases(lang)` call

7. **Added `check_stoplist_phrases()` function:**
   ```python
   def check_stoplist_phrases(text: str, lang: str = "ru") -> list[str]:
       phrases = get_stoplist_phrases(lang)
       found = []
       text_lower = text.lower()
       for phrase in phrases:
           if phrase in text_lower:
               found.append(phrase)
       return found
   ```

8. **Updated `check_stoplist()`:**
   - Added `lang` parameter
   - Now uses `check_stoplist_phrases()` internally

---

## Task 13: utils/text.py

### Changes Made

Identical changes to seo_utils.py:

1. Added imports from keyword_utils
2. Replaced `get_adaptive_coverage_target()` with wrapper
3. Removed local `COMMERCIAL_MARKERS` list
4. Added `find_commercial_markers()` function
5. Updated `check_commercial_markers()` with lang parameter
6. Removed local `STOPLIST_PHRASES` list
7. Added `check_stoplist_phrases()` function
8. Updated `check_stoplist()` with lang parameter

---

## Verification Results

### Ruff Check
```
$ ruff check scripts/seo_utils.py scripts/utils/text.py
Found 2 errors (2 fixed, 0 remaining).
```
Fixed import sorting with `--fix`.

### Function Tests
```python
>>> from scripts.seo_utils import find_commercial_markers
>>> find_commercial_markers('купить шампунь')
{'купить': 1}

>>> from scripts.seo_utils import check_stoplist_phrases
>>> check_stoplist_phrases('лучший товар')
['лучший']

>>> from scripts.seo_utils import get_adaptive_coverage_target
>>> get_adaptive_coverage_target(5)
70
>>> get_adaptive_coverage_target(10)
60
>>> get_adaptive_coverage_target(20)
50
```

### Pytest Results
```
$ pytest tests/ -v -k "seo_utils or text"
49 passed
```

---

## Files Modified

| File | Lines Changed |
|------|--------------|
| `scripts/seo_utils.py` | -67 lines (constants), +24 lines (imports/functions) |
| `scripts/utils/text.py` | -67 lines (constants), +24 lines (imports/functions) |

---

## SSOT Established

All commercial markers and stoplist phrases are now sourced from:
- `scripts/keyword_utils.py` - Single Source of Truth

Functions using SSOT:
- `get_commercial_markers(lang)` - returns list for RU or UK
- `get_stoplist_phrases(lang)` - returns list for RU or UK
- `get_adaptive_coverage_target(count)` - returns 70/60/50% threshold

---

**Worker:** W4
**Commit:** NOT COMMITTED (per instructions)
