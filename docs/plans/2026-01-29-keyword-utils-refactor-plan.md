# Implementation Plan: Keyword Utils Refactoring

**Date:** 2026-01-29
**Design:** [2026-01-29-keyword-utils-refactor-design.md](./2026-01-29-keyword-utils-refactor-design.md)
**Estimated Tasks:** 8

---

## Task 1: Update requirements.txt

**Files:** `requirements.txt`

**Actions:**
1. Replace pymorphy2 with pymorphy3:
   ```diff
   - pymorphy2==0.9.1
   - pymorphy2-dicts-ru==2.4.417127.4579844
   + pymorphy3>=2.0.0
   + pymorphy3-dicts-ru>=2.4.0
   + pymorphy3-dicts-uk>=2.4.0
   ```
2. Run `pip install -r requirements.txt`
3. Verify import works: `python3 -c "import pymorphy3; print(pymorphy3.__version__)"`

**Verification:**
```bash
python3 -c "from pymorphy3 import MorphAnalyzer; m = MorphAnalyzer(); print(m.parse('щётки')[0].normal_form)"
# Expected: щётка
```

---

## Task 2: Create scripts/keyword_utils.py

**Files:** `scripts/keyword_utils.py` (NEW)

**Actions:**
1. Create file with full API from design document:
   - Constants: COMMERCIAL_MARKERS, STOPLIST_PHRASES
   - MorphAnalyzer class (singleton with LRU cache)
   - KeywordMatcher class
   - CoverageChecker class
   - Backward-compatible functions

2. Key features:
   - pymorphy3 → pymorphy2 → Snowball fallback chain
   - `get_lemma()` with 10000-item LRU cache
   - `get_all_forms()` for generating word forms
   - `match_lemma()` for phrase matching with gap tolerance

**Verification:**
```bash
python3 -c "
from scripts.keyword_utils import KeywordMatcher
m = KeywordMatcher('ru')
found, form = m.find_in_text('щётка для мытья', 'используйте щётку для мытья авто')
print(f'Found: {found}, Form: {form}')
"
# Expected: Found: True, Form: щётку для мытья
```

---

## Task 3: Create tests/unit/test_keyword_utils.py

**Files:** `tests/unit/test_keyword_utils.py` (NEW)

**Actions:**
1. Test MorphAnalyzer:
   - `test_get_lemma_noun` — щётки → щётка
   - `test_get_lemma_verb` — моющий → мыть
   - `test_get_lemma_adjective` — грязеуловительный → грязеуловительный
   - `test_get_all_forms` — returns set of word forms
   - `test_normalize_phrase` — phrase → list of lemmas

2. Test KeywordMatcher:
   - `test_match_exact` — точное совпадение
   - `test_match_single_word_nominative` — щётка в тексте "щётка"
   - `test_match_single_word_accusative` — щётка в тексте "щётку"
   - `test_match_single_word_instrumental` — щётка в тексте "щёткой"
   - `test_match_phrase` — многословная фраза
   - `test_match_phrase_with_gap` — слова с пропуском
   - `test_no_match` — ключ отсутствует

3. Test CoverageChecker:
   - `test_coverage_all_found` — 100% coverage
   - `test_coverage_partial` — частичное покрытие
   - `test_coverage_none_found` — 0% coverage
   - `test_adaptive_target` — пороги 70/60/50%
   - `test_coverage_split` — core vs commercial

4. Test Ukrainian:
   - `test_uk_lemma` — щітки → щітка
   - `test_uk_matcher` — поиск в украинском тексте

**Verification:**
```bash
pytest tests/unit/test_keyword_utils.py -v
```

---

## Task 4: Migrate validate_content.py

**Files:** `scripts/validate_content.py`

**Actions:**
1. Add import:
   ```python
   from scripts.keyword_utils import (
       keyword_matches_text,
       CoverageChecker,
       get_adaptive_coverage_target,
   )
   ```

2. Replace `keyword_matches_semantic()` (lines 394-445):
   ```python
   def keyword_matches_semantic(keyword: str, text: str) -> bool:
       """Backward-compatible wrapper."""
       return keyword_matches_text(keyword, text, lang="ru")
   ```

3. Replace `check_keyword_coverage()` (lines 340-391):
   - Use CoverageChecker internally
   - Keep same return format for compatibility

4. Replace `check_keyword_coverage_split()` (lines 448-510):
   - Use CoverageChecker.check_split()

5. Delete:
   - Ручной стемминг `word[:-2]` (lines 432-442)
   - `get_adaptive_coverage_target()` дубль если есть

**Verification:**
```bash
python3 scripts/validate_content.py categories/aksessuary/shchetki-i-kisti/content/shchetki-i-kisti_ru.md
pytest tests/unit/test_validate_content.py -v
```

---

## Task 5: Migrate validate_meta.py

**Files:** `scripts/validate_meta.py`

**Actions:**
1. Add import:
   ```python
   from scripts.keyword_utils import keyword_matches_text, MorphAnalyzer
   ```

2. Replace `get_word_stem()` (lines 119-168):
   ```python
   def get_word_stem(word: str) -> str:
       """Backward-compatible wrapper using MorphAnalyzer."""
       morph = MorphAnalyzer("ru")
       return morph.get_lemma(word)
   ```

3. Replace `keyword_matches()` (lines 171-193):
   ```python
   def keyword_matches(keyword: str, text: str) -> bool:
       return keyword_matches_text(keyword, text, lang="ru")
   ```

**Verification:**
```bash
python3 scripts/validate_meta.py --all
pytest tests/unit/test_validate_meta.py -v
```

---

## Task 6: Migrate check_seo_structure.py

**Files:** `scripts/check_seo_structure.py`

**Actions:**
1. Add import:
   ```python
   from scripts.keyword_utils import MorphAnalyzer, KeywordMatcher
   ```

2. Replace `get_russian_word_stems()` (lines 130-145):
   ```python
   def get_russian_word_stems(text: str) -> set[str]:
       morph = MorphAnalyzer("ru")
       words = re.findall(r'[а-яё]+', text.lower())
       return {morph.get_lemma(w) for w in words if len(w) > 2}
   ```

3. Replace `get_ukrainian_word_stems()` (lines 155-170):
   ```python
   def get_ukrainian_word_stems(text: str) -> set[str]:
       morph = MorphAnalyzer("uk")
       words = re.findall(r'[а-яёїієґ]+', text.lower())
       return {morph.get_lemma(w) for w in words if len(w) > 2}
   ```

**Verification:**
```bash
python3 scripts/check_seo_structure.py categories/aksessuary/content/aksessuary_ru.md "аксессуары"
```

---

## Task 7: Cleanup seo_utils.py and utils/text.py

**Files:**
- `scripts/seo_utils.py`
- `scripts/utils/text.py`

**Actions:**

### seo_utils.py:
1. Replace `get_adaptive_coverage_target()` (lines 53-62):
   ```python
   from scripts.keyword_utils import get_adaptive_coverage_target
   ```

2. Replace `find_commercial_markers()` (lines 798-810):
   ```python
   from scripts.keyword_utils import get_commercial_markers

   def find_commercial_markers(text: str, lang: str = "ru") -> dict:
       markers = get_commercial_markers(lang)
       # ... rest of logic using markers
   ```

3. Replace `check_stoplist_phrases()` (lines 869-879):
   ```python
   from scripts.keyword_utils import get_stoplist_phrases

   def check_stoplist_phrases(text: str, lang: str = "ru") -> list:
       phrases = get_stoplist_phrases(lang)
       # ... rest of logic
   ```

### utils/text.py:
1. Same changes as seo_utils.py — удалить дубли, импортировать из keyword_utils

**Verification:**
```bash
pytest tests/ -v
ruff check scripts/seo_utils.py scripts/utils/text.py
```

---

## Task 8: Integrate with check_keyword_density.py

**Files:** `scripts/check_keyword_density.py`

**Actions:**
1. Add import:
   ```python
   from scripts.keyword_utils import MorphAnalyzer
   ```

2. Replace Snowball stemmer initialization (lines 36-50):
   ```python
   # Use MorphAnalyzer for stemming (has fallback to Snowball)
   def get_stemmer(lang: str = "ru"):
       return MorphAnalyzer(lang)
   ```

3. Update `count_stem_frequencies()` to use MorphAnalyzer.get_lemma()

4. Move STOPWORDS to keyword_utils.py or keep as is (density-specific)

**Verification:**
```bash
python3 scripts/check_keyword_density.py categories/aksessuary/content/aksessuary_ru.md
```

---

## Execution Order

```
Task 1 (requirements) → Task 2 (keyword_utils.py) → Task 3 (tests)
                                    ↓
                        [Run tests, verify core works]
                                    ↓
         Task 4 (validate_content) ──┬── Task 5 (validate_meta)
                                     │
         Task 6 (check_seo_structure)┘
                                    ↓
                        Task 7 (cleanup duplicates)
                                    ↓
                        Task 8 (check_keyword_density)
                                    ↓
                        [Final verification: all tests pass]
```

---

## Parallel Execution

Tasks 4, 5, 6 можно выполнять параллельно после Task 3.

**Worker assignment:**
- W1: Task 4 (validate_content.py)
- W2: Task 5 (validate_meta.py) + Task 6 (check_seo_structure.py)
- W3: Task 7 (seo_utils.py + utils/text.py)

---

## Verification Checklist

After all tasks complete:

- [ ] `pytest tests/` — all tests pass
- [ ] `ruff check scripts/` — no lint errors
- [ ] `python3 scripts/validate_content.py categories/aksessuary/content/aksessuary_ru.md` — works
- [ ] `python3 scripts/validate_meta.py --all` — works
- [ ] `python3 scripts/check_keyword_density.py categories/aksessuary/content/aksessuary_ru.md` — works
- [ ] Coverage false negatives reduced (manual check on 3 categories)

---

## Rollback Plan

If issues arise:
1. Revert `requirements.txt` to pymorphy2
2. keyword_utils.py will fallback to Snowball automatically
3. All backward-compatible functions ensure existing code works
