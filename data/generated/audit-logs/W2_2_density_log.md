# W2-2: Миграция check_keyword_density.py

**Task:** Task 6 — Migrate check_keyword_density.py to use text_utils
**Started:** 2026-01-29
**Status:** ✅ COMPLETED

---

## Step 1: Run existing tests to verify baseline

```bash
pytest tests/unit/test_check_keyword_density.py -v
```

**Result:** 12 tests PASSED

---

## Step 2: Update check_keyword_density.py imports

### Changes made:

1. **Added imports from text_utils SSOT:**
```python
try:
    from scripts.text_utils import (
        clean_markdown,
        get_stopwords,
        tokenize,
    )
except ImportError:
    from text_utils import (
        clean_markdown,
        get_stopwords,
        tokenize,
    )
```

2. **Deleted local definitions:**
   - STOPWORDS_RU (~123 lines)
   - STOPWORDS_UK (~116 lines)
   - get_stopwords() function
   - clean_markdown() function
   - tokenize() local function
   - tokenize_all() function
   - remove_stopwords() function

3. **Updated function signatures:**
   - `check_keyword_density()` — added `lang` parameter, uses `tokenize(..., remove_stopwords=False)`
   - `analyze_text()` — uses `tokenize(..., remove_stopwords=False)` for all_words, `tokenize(..., remove_stopwords=True)` for content words

4. **Updated test file:**
   - Changed imports to use `scripts.text_utils` for STOPWORDS and tokenize
   - Renamed `TestRemoveStopwords` → `TestTokenizeStopwords`
   - Updated tests to use `tokenize()` directly instead of `remove_stopwords()`

---

## Step 3: Run tests to verify no regression

```bash
pytest tests/unit/test_check_keyword_density.py -v --no-cov
```

**Result:** 12 tests PASSED ✅

---

## Step 4: Manual verification

```bash
python3 scripts/check_keyword_density.py categories/polirovka/content/polirovka_ru.md --top 5
```

**Result:** Script works correctly, shows density report with proper statistics.

---

## Files Modified

1. `scripts/check_keyword_density.py` — Migrated to use text_utils SSOT
2. `tests/unit/test_check_keyword_density.py` — Updated imports and tests

---

## Summary

- ✅ Removed ~250 lines of duplicate code (STOPWORDS_RU, STOPWORDS_UK, clean_markdown, tokenize, remove_stopwords)
- ✅ All 12 tests pass
- ✅ Script works correctly from command line
- ✅ No regressions detected

**Lines removed:** ~250 (stopwords, functions)
**Lines added:** ~15 (imports with fallback)
**Net reduction:** ~235 lines
