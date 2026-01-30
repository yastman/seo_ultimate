# W3-1: UK Support + Archive + Docs

**Worker:** W3-1
**Date:** 2026-01-29
**Tasks:** 9, 12, 13

---

## Task 9: Add UK patterns to validate_meta.py

### Changes

**File:** `scripts/validate_meta.py`

1. Added language-specific patterns:
   - `PRODUCER_PATTERNS_RU` — Russian producer patterns
   - `PRODUCER_PATTERNS_UK` — Ukrainian producer patterns
   - `WHOLESALE_PATTERNS_RU` — Russian wholesale patterns
   - `WHOLESALE_PATTERNS_UK` — Ukrainian wholesale patterns

2. Added `get_validation_patterns(lang)` function to return patterns by language

3. Updated functions with `lang` parameter:
   - `keyword_matches(keyword, text, lang="ru")` — now passes lang to keyword_utils
   - `validate_title(title, keywords, lang="ru")` — added lang parameter
   - `validate_description(desc, keywords, lang="ru")` — uses language-specific patterns
   - `validate_meta_file(path, keywords_path, lang="ru")` — supports lang parameter

4. Updated CLI with `--lang` argument:
   - Auto-detects language from path (uk/ prefix)
   - Supports explicit `--lang ru` or `--lang uk`

**File:** `tests/unit/test_validate_meta.py`

Added `TestValidateMetaUK` class with 3 tests:
- `test_validate_meta_uk_language` — UK validation passes
- `test_validate_meta_uk_detects_missing_producer` — detects missing 'від виробника'
- `test_validate_meta_uk_wholesale_pattern` — detects 'опт/роздріб'

### Verification

```
pytest tests/unit/test_validate_meta.py -v
15 passed
```

---

## Task 12: Create scripts/archive/ and move validate_uk.py

### Changes

1. Created `scripts/archive/` directory
2. Moved `scripts/validate_uk.py` → `scripts/archive/validate_uk.py`
3. Created `scripts/archive/README.md` with migration docs

### Files

```
scripts/archive/
├── README.md
└── validate_uk.py
```

---

## Task 13: Update CLAUDE.md

### Changes

Updated `## Команды` section:
- Replaced old validator commands with unified commands
- Added `--lang` parameter documentation
- Removed `validate_uk.py` reference
- Updated script names (validate_seo, validate_density)

### Before

```bash
# Валидация
python3 scripts/validate_meta.py --all
python3 scripts/validate_content.py categories/{slug}/content/{slug}_ru.md
python3 scripts/check_seo_structure.py categories/{slug}/content/{slug}_ru.md "main keyword"

# Валидация (UK)
python3 scripts/validate_uk.py uk/categories/{slug}/content/{slug}_uk.md
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
```

### After

```bash
# Валидация (Unified с --lang поддержкой)
python3 scripts/validate_meta.py <path> [--lang ru|uk]
python3 scripts/validate_meta.py --all [--lang ru|uk]
python3 scripts/validate_content.py <path> "<keyword>" [--lang ru|uk]
python3 scripts/validate_seo.py <path> "<keyword>" [--lang ru|uk]
python3 scripts/validate_density.py <path> [--lang ru|uk]
```

---

## Summary

| Task | Status | Files Changed |
|------|--------|---------------|
| Task 9 | DONE | validate_meta.py, test_validate_meta.py |
| Task 12 | DONE | scripts/archive/* |
| Task 13 | DONE | CLAUDE.md |

**Tests:** 15 passed
**Commits:** NOT MADE (as instructed)
