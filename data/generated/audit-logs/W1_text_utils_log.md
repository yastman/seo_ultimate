# W1: text_utils.py SSOT Module Log

**Worker:** W1
**Date:** 2026-01-29
**Plan:** docs/plans/2026-01-29-scripts-refactoring-plan.md
**Tasks:** 0-4

## Summary

Created `scripts/text_utils.py` — SSOT module for text processing with full test coverage.

## Tasks Completed

### Task 0: Create test fixtures with real data
- Created `tests/fixtures/real_data.py` with sample markdown content
- Updated `tests/conftest.py` with fixtures: `sample_ru_markdown`, `sample_uk_markdown`, `real_ru_content_path`, `real_uk_content_path`
- Status: PASS

### Task 1: Create text_utils.py with stopwords
- Created `scripts/text_utils.py`
- Added `STOPWORDS_RU` (74 words) and `STOPWORDS_UK` (74 words)
- Added `get_stopwords(lang)` function
- Tests: 2 PASS
- Status: PASS

### Task 2: Add clean_markdown to text_utils
- Added `clean_markdown(text)` function
- Removes: YAML front matter, headers markup, bold/italic, links, code blocks, tables, list markers
- Added `normalize_text(text)` alias for backward compatibility
- Tests: 4 PASS
- Status: PASS

### Task 3: Add extract_h1, extract_h2s, extract_intro
- Added `extract_h1(text)` — returns H1 text or None
- Added `extract_h2s(text)` — returns list of H2 texts
- Added `extract_intro(text, max_lines=5)` — returns intro paragraph
- Tests: 6 PASS
- Status: PASS

### Task 4: Add count_words, count_chars_no_spaces, tokenize
- Added `count_words(text)` — word count
- Added `count_chars_no_spaces(text)` — char count without whitespace
- Added `tokenize(text, lang='ru', remove_stopwords=True)` — word splitting with optional stopword removal
- Tests: 6 PASS
- Status: PASS

## Final Test Results

```
pytest tests/unit/test_text_utils.py -v
============================== 18 passed in 22.30s ==============================
```

## Files Created/Modified

### Created:
- `tests/fixtures/real_data.py`
- `scripts/text_utils.py`
- `tests/unit/test_text_utils.py`

### Modified:
- `tests/conftest.py` (added fixtures)

## text_utils.py API

```python
# Stopwords
get_stopwords(lang: str = "ru") -> frozenset[str]

# Markdown cleaning
clean_markdown(text: str) -> str
normalize_text(text: str) -> str  # alias

# Heading extraction
extract_h1(text: str) -> str | None
extract_h2s(text: str) -> list[str]
extract_intro(text: str, max_lines: int = 5) -> str

# Text metrics
count_words(text: str) -> int
count_chars_no_spaces(text: str) -> int
tokenize(text: str, lang: str = "ru", remove_stopwords: bool = True) -> list[str]
```

## Notes

- NO git commits made (as instructed)
- All tests follow TDD: write failing test first, then implement
- Module is ready for import migration in Tasks 5-8
