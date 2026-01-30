# Fix Primary Keyword Morphology for UK Language

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix `check_primary_keyword()` to properly use morphological matching for Ukrainian content by passing `lang` parameter.

**Architecture:** The fix requires passing `lang` through the call chain: `validate_content()` → `check_primary_keyword()` → `KeywordMatcher(lang)`. Also fix `check_primary_keyword_semantic()` which hardcodes `lang="ru"`.

**Tech Stack:** Python, pymorphy3/snowball, pytest

---

## Problem Analysis

Current bug flow:
1. `validate_content()` receives `lang="uk"` parameter
2. Calls `check_primary_keyword(text, primary_keyword)` — **without lang**
3. `check_primary_keyword()` defaults to `lang="ru"`
4. `KeywordMatcher(lang="ru")` uses Russian morphology for Ukrainian text
5. Result: "губка" doesn't match "губку" for UK content

Files affected:
- `scripts/validate_content.py:927` — call site (missing `lang=lang`)
- `scripts/validate_content.py:294` — `check_primary_keyword_semantic()` hardcodes `lang="ru"`

---

### Task 1: Add UK Morphology Test

**Files:**
- Modify: `tests/unit/test_validate_content.py`

**Step 1: Write the failing test**

Add to `TestPrimaryKeyword` class:

```python
def test_uk_morphology_match(self):
    """UK: губка should match губку (case declension)."""
    text = "# Губку для салону авто\n\nВикористовуйте губку для салону."
    kw = "губка для салону авто"
    res = check_primary_keyword(text, kw, lang="uk")
    assert res["in_h1"]["passed"], f"H1 match failed: expected губка~губку"
    assert res["in_intro"]["passed"], f"Intro match failed"
    assert res["overall"] == "PASS"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_validate_content.py::TestPrimaryKeyword::test_uk_morphology_match -v`
Expected: FAIL (currently `lang` not passed, defaults to `ru`)

---

### Task 2: Fix validate_content() Call Site

**Files:**
- Modify: `scripts/validate_content.py:927`

**Step 1: Find and fix the call**

Change line 927 from:
```python
primary_kw = check_primary_keyword(text, primary_keyword)
```

To:
```python
primary_kw = check_primary_keyword(text, primary_keyword, lang=lang)
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/unit/test_validate_content.py::TestPrimaryKeyword::test_uk_morphology_match -v`
Expected: PASS

**Step 3: Run full test suite**

Run: `pytest tests/unit/test_validate_content.py -v`
Expected: All PASS

---

### Task 3: Fix check_primary_keyword_semantic() Hardcoded Lang

**Files:**
- Modify: `scripts/validate_content.py:261-294`

**Step 1: Add lang parameter to function signature**

Change line 261 from:
```python
def check_primary_keyword_semantic(text: str, primary_keyword: str, use_llm: bool = False) -> dict:
```

To:
```python
def check_primary_keyword_semantic(text: str, primary_keyword: str, use_llm: bool = False, lang: str = "ru") -> dict:
```

**Step 2: Fix hardcoded KeywordMatcher**

Change line 294 from:
```python
matcher = KeywordMatcher(lang="ru")
```

To:
```python
matcher = KeywordMatcher(lang=lang)
```

**Step 3: Update call site in validate_content()**

Change line 932 from:
```python
semantic_kw = check_primary_keyword_semantic(text, primary_keyword, use_llm=semantic_allowed)
```

To:
```python
semantic_kw = check_primary_keyword_semantic(text, primary_keyword, use_llm=semantic_allowed, lang=lang)
```

**Step 4: Run tests**

Run: `pytest tests/unit/test_validate_content.py -v`
Expected: All PASS

---

### Task 4: Add Semantic UK Test

**Files:**
- Modify: `tests/unit/test_validate_content.py`

**Step 1: Add test for semantic UK matching**

Add to `TestPrimaryKeyword` class:

```python
def test_uk_semantic_match(self):
    """UK semantic: чорнитель should match чорнителі (plural)."""
    text = "# Чорнителі шин\n\nКупуйте чорнителі шин."
    kw = "чорнитель шин"
    res = check_primary_keyword_semantic(text, kw, lang="uk")
    assert res["semantic_h1"], "UK semantic H1 match failed"
    assert res["semantic_intro"], "UK semantic intro match failed"
    assert res["overall"] == "PASS"
```

**Step 2: Run test**

Run: `pytest tests/unit/test_validate_content.py::TestPrimaryKeyword::test_uk_semantic_match -v`
Expected: PASS

---

### Task 5: Integration Test with Real UK File

**Files:**
- No new files

**Step 1: Test on real UK category**

Run:
```bash
python3 scripts/validate_content.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md "активна піна" --mode seo --lang uk
```

Expected: PRIMARY KEYWORD section shows `In H1: ✓` and `In Intro: ✓`

**Step 2: Run full test suite**

Run: `pytest tests/ -v --ignore=tests/integration`
Expected: All PASS

---

### Task 6: Commit

**Step 1: Stage changes**

```bash
git add scripts/validate_content.py tests/unit/test_validate_content.py
```

**Step 2: Commit**

```bash
git commit -m "fix(validate): pass lang param to primary keyword morphology check

- check_primary_keyword() now receives lang from validate_content()
- check_primary_keyword_semantic() accepts lang param instead of hardcoding 'ru'
- Added UK morphology tests for губка/губку matching

Fixes UK validation false negatives where declined forms weren't matched."
```

---

## Verification Checklist

- [ ] `pytest tests/unit/test_validate_content.py -v` — all pass
- [ ] UK file validation shows correct H1/intro matching
- [ ] RU validation still works (regression)
- [ ] `ruff check scripts/validate_content.py` — no lint errors
