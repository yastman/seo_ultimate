# W1: Fix morphology Surn filter

**Task:** Task 1 from docs/plans/2026-01-30-validation-skills-fix-plan.md
**Date:** 2026-01-30
**Worker:** W1

## Summary

Fixed pymorphy3 `get_lemma()` method to filter out Surn (surname) parses that cause incorrect lemmatization.

**Problem:** `get_lemma("губка")` returned "губко" (surname) instead of "губка" (noun).

**Root cause:** pymorphy3 returns multiple parses for ambiguous words. For "губка", it returns both:
- Parse 1: Surn (surname "Губко") → normal_form = "губко"
- Parse 2: NOUN (noun "губка") → normal_form = "губка"

The old code just took `parsed[0].normal_form` without filtering.

**Solution:** Filter out parses with 'Surn' tag before selecting the first parse.

## Changes

### 1. Tests added (RED)

**File:** `tests/unit/test_keyword_utils.py`

```python
class TestMorphAnalyzerSurnFilter:
    """Test that Surn (surname) parses are filtered out."""

    def test_uk_gubka_not_surname(self):
        """губка should lemmatize to губка, not губко (surname)."""
        morph = MorphAnalyzer(lang='uk')
        assert morph.get_lemma("губка") == "губка"

    def test_uk_gubky_to_gubka(self):
        """губки should lemmatize to губка."""
        morph = MorphAnalyzer(lang='uk')
        assert morph.get_lemma("губки") == "губка"

    def test_ru_no_surname_interference(self):
        """RU morphology should also filter surnames."""
        morph = MorphAnalyzer(lang='ru')
        result = morph.get_lemma("шампунь")
        assert result == "шампунь"
```

### 2. Implementation fixed (GREEN)

**File:** `scripts/keyword_utils.py` (lines 153-184)

**Before:**
```python
if self._use_pymorphy and self._morph:
    parsed = self._morph.parse(word_lower)
    if parsed:
        return parsed[0].normal_form
```

**After:**
```python
if self._use_pymorphy and self._morph:
    parses = self._morph.parse(word_lower)
    if parses:
        # Filter out surname (Surn) parses - they give false lemmas
        # e.g., "губка" parsed as surname "Губко" instead of noun "губка"
        non_surname = [p for p in parses if 'Surn' not in p.tag]

        if non_surname:
            return non_surname[0].normal_form

        # Fallback if all parses are surnames
        return parses[0].normal_form
```

## Test Results

### Surn filter tests (should FAIL before fix, PASS after)
```
tests/unit/test_keyword_utils.py::TestMorphAnalyzerSurnFilter::test_uk_gubka_not_surname PASSED
tests/unit/test_keyword_utils.py::TestMorphAnalyzerSurnFilter::test_uk_gubky_to_gubka PASSED
tests/unit/test_keyword_utils.py::TestMorphAnalyzerSurnFilter::test_ru_no_surname_interference PASSED
```

### All keyword_utils tests (no regressions)
```
51 passed in 10.44s
```

## Files Modified

1. `scripts/keyword_utils.py` - Added Surn filter to get_lemma()
2. `tests/unit/test_keyword_utils.py` - Added TestMorphAnalyzerSurnFilter class

## Status

**DONE** - Ready for commit by orchestrator.
