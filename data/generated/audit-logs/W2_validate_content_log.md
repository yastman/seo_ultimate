# W2: Task 9 - Migrate validate_content.py

**Date:** 2026-01-29
**Plan:** docs/plans/2026-01-29-keyword-utils-refactor-plan.md

## Status: COMPLETE

## Changes Made

### 1. Added import for keyword_utils (lines 66-79)

```python
# Unified keyword matching (keyword_utils)
try:
    from scripts.keyword_utils import (
        CoverageChecker,
        KeywordMatcher,
        get_adaptive_coverage_target,
        keyword_matches_text,
    )
except ImportError:
    from keyword_utils import (  # type: ignore
        CoverageChecker,
        KeywordMatcher,
        get_adaptive_coverage_target,
        keyword_matches_text,
    )
```

### 2. Replaced `keyword_matches_semantic()` (lines 394-406)

**Before:** 52 lines of manual stemming (`word[:-2]`, `word[:-1]`)

**After:**
```python
def keyword_matches_semantic(keyword: str, text: str) -> bool:
    """
    Check if keyword matches text semantically.
    Uses morphology-aware matching via keyword_utils.
    """
    return keyword_matches_text(keyword, text, lang="ru")
```

### 3. Replaced `check_keyword_coverage()` (lines 340-379)

**Before:** Manual exact-match loop

**After:** Uses `CoverageChecker(lang="ru").check()` with morphology

```python
def check_keyword_coverage(text: str, keywords: list[str]) -> dict:
    checker = CoverageChecker(lang="ru")
    result = checker.check(keywords, text, use_lemma=True)
    # Convert to legacy format...
```

### 4. Replaced `check_keyword_coverage_split()` (lines 381-424)

**Before:** Manual loop with `keyword_matches_semantic()`

**After:** Uses `CoverageChecker.check()` twice (core + commercial)

```python
def check_keyword_coverage_split(...) -> dict:
    checker = CoverageChecker(lang="ru")
    core_result = checker.check(core_keywords, text, use_lemma=use_semantic)
    comm_result = checker.check(commercial_keywords, text, use_lemma=False)
```

### 5. Replaced `check_primary_keyword_semantic()` (lines 264-335)

**Before:** Manual stemming (`word[:-2]`, significant_words loop)

**After:** Uses `KeywordMatcher(lang="ru").find_in_text()`

```python
matcher = KeywordMatcher(lang="ru")
h1_matched, _ = matcher.find_in_text(primary_keyword, h1)
intro_matched, _ = matcher.find_in_text(primary_keyword, intro)
```

### 6. Updated tests (tests/unit/test_validate_content.py)

Changed mock targets from `scripts.validate_content.get_adaptive_coverage_target` to `scripts.keyword_utils.CoverageChecker.get_adaptive_target` since coverage checking now uses CoverageChecker internally.

## Verification

### Tests: PASS
```
pytest tests/unit/test_validate_content.py -v
# 17 passed, 2 warnings
```

### CLI Validation: PASS
```
python3 -m scripts.validate_content categories/aksessuary/content/aksessuary_ru.md "аксессуары"
# Works correctly, shows OVERALL: WARNING (content_standards)
```

## Code Deleted

1. Manual stemming in `keyword_matches_semantic()` (~40 lines)
2. Manual coverage loop in `check_keyword_coverage()` (~15 lines)
3. Manual coverage loop in `check_keyword_coverage_split()` (~20 lines)
4. Manual stemming in `check_primary_keyword_semantic()` (~20 lines)

## Notes

- The `get_adaptive_coverage_target` import is no longer needed from config (now comes from keyword_utils)
- Legacy return format preserved for backward compatibility (found_keywords as strings, not dicts)
- CLI invocation as `python3 scripts/validate_content.py` has pre-existing import issues (seo_utils.py), but `python3 -m scripts.validate_content` works correctly
- Test mocks updated to patch `scripts.keyword_utils.CoverageChecker.get_adaptive_target` since coverage checking now uses CoverageChecker internally
