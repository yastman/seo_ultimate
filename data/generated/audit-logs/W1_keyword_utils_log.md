# W1: keyword_utils.py Implementation Log

**Started:** 2026-01-29
**Plan:** docs/plans/2026-01-29-keyword-utils-implementation.md
**Tasks:** 1-8 (core module creation)

---

## Task 1: Update Dependencies
**Status:** COMPLETED

- Replaced pymorphy2 with pymorphy3 in requirements.txt
- Installed: pymorphy3-2.0.6, pymorphy3-dicts-ru, pymorphy3-dicts-uk
- Verified: `MorphAnalyzer().parse('щётки')[0].normal_form` → щётка

---

## Task 2: Create keyword_utils.py - Constants
**Status:** COMPLETED

- Created `scripts/keyword_utils.py`
- Added COMMERCIAL_MARKERS_RU, COMMERCIAL_MARKERS_UK
- Added STOPLIST_PHRASES_RU, STOPLIST_PHRASES_UK
- Verified: `get_commercial_markers('ru')` returns 12 items

---

## Task 3: Create MorphAnalyzer Class
**Status:** COMPLETED

- Singleton pattern with _instances dict
- Fallback chain: pymorphy3 → pymorphy2 → Snowball → strip
- Methods: get_lemma(), get_all_forms(), normalize_phrase()
- LRU cache: 10000 for lemmas, 1000 for forms
- Verified: backend = "pymorphy"

---

## Task 4: Create MorphAnalyzer Tests
**Status:** COMPLETED

- Created `tests/unit/test_keyword_utils.py`
- TestConstants: 4 tests
- TestMorphAnalyzer: 12 tests (singleton, lemmas, forms)
- TestMorphAnalyzerUK: 1 test
- **17 tests PASSED**

---

## Task 5: Create KeywordMatcher Class
**Status:** COMPLETED

- Methods: match_exact(), match_lemma(), find_in_text()
- _match_single_word() - uses get_all_forms()
- _match_phrase() - lemma sequence matching with gap tolerance
- Verified: find_in_text('щётка', 'используйте щётку') → (True, 'щётку')

---

## Task 6: Add KeywordMatcher Tests
**Status:** COMPLETED

- TestKeywordMatcher: 11 tests
- Covers: exact match, single word (all cases), phrases, Latin brands
- **11 tests PASSED**

---

## Task 7: Create CoverageChecker Class
**Status:** COMPLETED

- get_adaptive_target(): 70% (≤5), 60% (6-15), 50% (>15)
- check(): returns {total, found, coverage_percent, target, passed, found_keywords, missing_keywords}
- check_split(): separate core vs commercial
- Backward-compat: get_adaptive_coverage_target(), keyword_matches_text(), find_keyword_form()
- Verified: check(['щётка', 'губка'], 'используйте щётку') → 50.0%

---

## Task 8: Add CoverageChecker Tests
**Status:** COMPLETED

- TestCoverageChecker: 10 tests
- TestBackwardCompatibleFunctions: 5 tests
- **43 TOTAL tests PASSED**

---

## Summary

| Task | Description | Status |
|------|-------------|--------|
| 1 | Update dependencies | COMPLETED |
| 2 | Create constants | COMPLETED |
| 3 | Create MorphAnalyzer | COMPLETED |
| 4 | Test MorphAnalyzer | COMPLETED |
| 5 | Create KeywordMatcher | COMPLETED |
| 6 | Test KeywordMatcher | COMPLETED |
| 7 | Create CoverageChecker | COMPLETED |
| 8 | Test CoverageChecker | COMPLETED |

**Files created:**
- scripts/keyword_utils.py (176 lines, 85.8% coverage)
- tests/unit/test_keyword_utils.py (43 tests)

**Files modified:**
- requirements.txt (pymorphy2 → pymorphy3)

**Tests:** 43 passed
