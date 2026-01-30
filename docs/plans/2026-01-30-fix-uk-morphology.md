# Fix UK Morphology Support

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ensure Ukrainian morphology works correctly by syncing environment with requirements.txt.

**Architecture:** Code in `keyword_utils.py` already handles lang correctly. Issue is environment mismatch. Fix by syncing via `pip install -r requirements.txt`. Note: pymorphy2 is incompatible with Python 3.12, so pymorphy3 is the only working option.

**Tech Stack:** Python 3.12, pymorphy3, pytest

---

## Problem Analysis

**Current state:**
- `requirements.txt`: pymorphy3 + pymorphy3-dicts-uk ✓
- Runtime: pymorphy3 works, pymorphy2 fails on Python 3.12 (inspect.getargspec removed)

**Known limitations:**
- pymorphy3-dicts-uk has some dictionary bugs (e.g., "губка" → "губко")
- Use stable words for tests: шампунь, щітка, піна, засіб

**Root cause:** Environment may not be synced with requirements.txt

---

### Task 1: Sync Environment via requirements.txt

**Step 1: Install from requirements.txt (canonical sync)**

```bash
.venv/Scripts/pip.exe install -r requirements.txt
```

**Step 2: Verify pymorphy3-dicts-uk is installed**

```bash
.venv/Scripts/pip.exe list | grep -i morph
```

Expected: `pymorphy3-dicts-uk` present

**Step 3: Quick smoke test**

```bash
.venv/Scripts/python.exe -c "import pymorphy3; m = pymorphy3.MorphAnalyzer(lang='uk'); print(m.parse('шампуні')[0].normal_form)"
```

Expected: `шампунь`

---

### Task 2: Update requirements.txt (cleanup)

**Files:**
- Modify: `requirements.txt`

**Step 1: Remove pymorphy2-dicts-uk (incompatible with Python 3.12)**

Remove line:
```
pymorphy2-dicts-uk>=2.4.0
```

Reason: pymorphy2 doesn't work on Python 3.12 due to removed `inspect.getargspec`. Keeping it creates false expectation of working fallback.

---

### Task 3: Write Behavior-Based UK Morphology Tests

**Files:**
- Modify: `tests/unit/test_keyword_utils.py`

**Principle:** Test lemmatization results, not internal backend. Use stable words.

**Step 1: Update TestMorphAnalyzerUK**

Replace existing tests with:

```python
class TestMorphAnalyzerUK:
    """Test Ukrainian MorphAnalyzer with pymorphy3-dicts-uk.

    Note: Some words have dictionary bugs (e.g., губка→губко).
    Use stable words: шампунь, щітка, піна, засіб.
    """

    def test_uk_lemmatization_shampun(self):
        """UK: шампуні/шампунем → шампунь."""
        morph = MorphAnalyzer("uk")
        assert morph.get_lemma("шампуні") == "шампунь"
        assert morph.get_lemma("шампунем") == "шампунь"
        assert morph.get_lemma("шампуню") == "шампунь"

    def test_uk_lemmatization_shchitka(self):
        """UK: щітки/щітку/щіткою → щітка."""
        morph = MorphAnalyzer("uk")
        assert morph.get_lemma("щітки") == "щітка"
        assert morph.get_lemma("щітку") == "щітка"
        assert morph.get_lemma("щіткою") == "щітка"

    def test_uk_lemmatization_pina(self):
        """UK: піни/піну/піною → піна."""
        morph = MorphAnalyzer("uk")
        assert morph.get_lemma("піни") == "піна"
        assert morph.get_lemma("піну") == "піна"
        assert morph.get_lemma("піною") == "піна"

    def test_uk_lemmatization_zasib(self):
        """UK: засоби/засобу/засобом → засіб."""
        morph = MorphAnalyzer("uk")
        assert morph.get_lemma("засоби") == "засіб"
        assert morph.get_lemma("засобу") == "засіб"
        assert morph.get_lemma("засобом") == "засіб"

    def test_uk_not_snowball_russian(self):
        """UK should NOT use Russian Snowball stemming.

        Verify by checking that UK-specific word normalizes correctly,
        not to Russian-style stem.
        """
        morph = MorphAnalyzer("uk")
        # "засоби" in Russian Snowball would stem differently
        # If pymorphy works, it returns proper Ukrainian lemma
        lemma = morph.get_lemma("засоби")
        assert lemma == "засіб", f"Expected 'засіб', got '{lemma}' (possible Snowball fallback)"
```

**Step 2: Run tests**

```bash
.venv/Scripts/python.exe -m pytest tests/unit/test_keyword_utils.py::TestMorphAnalyzerUK -v
```

Expected: All PASS

---

### Task 4: Write KeywordMatcher UK Integration Tests

**Files:**
- Modify: `tests/unit/test_keyword_utils.py`

**Step 1: Update TestKeywordMatcherUK with stable words**

```python
class TestKeywordMatcherUK:
    """Test Ukrainian keyword matching with proper morphology."""

    def test_uk_keyword_match_declension_shchitka(self):
        """UK: 'щітка для миття' should match 'щітку для миття'."""
        matcher = KeywordMatcher(lang="uk")
        found, form = matcher.find_in_text(
            "щітка для миття", "Використовуйте щітку для миття авто."
        )
        assert found, "Should match declined form щітку"

    def test_uk_keyword_match_plural_shampun(self):
        """UK: 'шампунь для авто' should match 'шампуні для авто'."""
        matcher = KeywordMatcher(lang="uk")
        found, form = matcher.find_in_text(
            "шампунь для авто", "Купуйте шампуні для авто в нашому магазині."
        )
        assert found, "Should match plural form шампуні"

    def test_uk_keyword_match_instrumental_pina(self):
        """UK: 'піна' should match 'піною'."""
        matcher = KeywordMatcher(lang="uk")
        found, form = matcher.find_in_text(
            "активна піна", "Миття активною піною дає кращий результат."
        )
        assert found, "Should match instrumental form піною"
```

**Step 2: Run tests**

```bash
.venv/Scripts/python.exe -m pytest tests/unit/test_keyword_utils.py::TestKeywordMatcherUK -v
```

Expected: All PASS

---

### Task 5: Run Full Test Suite + Lint

**Step 1: Run all keyword_utils tests**

```bash
.venv/Scripts/python.exe -m pytest tests/unit/test_keyword_utils.py -v
```

Expected: All PASS

**Step 2: Lint check**

```bash
ruff check scripts/keyword_utils.py tests/unit/test_keyword_utils.py
```

Expected: No errors

---

### Task 6: Cleanup and Commit (Optional)

**Step 1: Remove temp files**

```bash
rm -f morph_test.txt morph_test2.txt morph_test3.txt
```

**Step 2: Stage and commit**

```bash
git add requirements.txt tests/unit/test_keyword_utils.py
git commit -m "fix(morph): add UK morphology regression tests

- Add behavior-based UK lemmatization tests (шампунь, щітка, піна, засіб)
- Add KeywordMatcher UK integration tests for declension/plural
- Remove pymorphy2-dicts-uk (incompatible with Python 3.12)
- Use stable words that work correctly with pymorphy3-dicts-uk

Note: pymorphy3-dicts-uk has known bugs with some words (e.g., губка→губко)."
```

---

## Verification Checklist

- [ ] `pip list | grep morph` shows pymorphy3-dicts-uk
- [ ] `python -c "..."` smoke test returns "шампунь"
- [ ] `pytest tests/unit/test_keyword_utils.py -v` — all pass
- [ ] UK content validation works: `python3 scripts/validate_content.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md "активна піна" --lang uk`
