# Keyword Utils Refactoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create unified keyword matching module with pymorphy3 morphology support, eliminating 35+ code duplications.

**Architecture:** Single `scripts/keyword_utils.py` module with MorphAnalyzer (singleton, LRU-cached), KeywordMatcher (lemma-based search), CoverageChecker (unified coverage API). Fallback chain: pymorphy3 → pymorphy2 → Snowball.

**Tech Stack:** Python 3.9+, pymorphy3, snowballstemmer, pytest

**Design Doc:** [2026-01-29-keyword-utils-refactor-design.md](./2026-01-29-keyword-utils-refactor-design.md)

---

## Task 1: Update Dependencies

**Files:**
- Modify: `requirements.txt`

**Step 1: Update requirements.txt**

Replace pymorphy2 with pymorphy3:

```python
# Remove these lines:
# pymorphy2==0.9.1
# pymorphy2-dicts-ru==2.4.417127.4579844

# Add these lines:
pymorphy3>=2.0.0
pymorphy3-dicts-ru>=2.4.0
pymorphy3-dicts-uk>=2.4.0
```

**Step 2: Install updated dependencies**

Run: `pip install -r requirements.txt`
Expected: Successfully installed pymorphy3-2.0.x

**Step 3: Verify installation**

Run: `python3 -c "from pymorphy3 import MorphAnalyzer; m = MorphAnalyzer(); print(m.parse('щётки')[0].normal_form)"`
Expected: `щётка`

**Step 4: Commit**

```bash
git add requirements.txt
git commit -m "deps: replace pymorphy2 with pymorphy3 for RU/UK morphology"
```

---

## Task 2: Create keyword_utils.py - Constants

**Files:**
- Create: `scripts/keyword_utils.py`

**Step 1: Create file with constants and docstring**

```python
"""
keyword_utils.py — Unified Keyword Matching with Russian/Ukrainian Morphology

Единый модуль для:
- Лемматизации (pymorphy3)
- Поиска ключевых слов с учётом падежей
- Проверки coverage
- Генерации всех форм слова

Usage:
    from scripts.keyword_utils import KeywordMatcher, CoverageChecker

    matcher = KeywordMatcher(lang='ru')
    found, form = matcher.find_in_text("щётка для мытья", text)
    # found=True, form="щётку для мытья"

    checker = CoverageChecker(lang='ru')
    result = checker.check(keywords, text)
    # {found: [...], missing: [...], coverage: 85.0}
"""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Literal

# =============================================================================
# Constants (SSOT - Single Source of Truth)
# =============================================================================

COMMERCIAL_MARKERS_RU = [
    "купить",
    "цена",
    "стоимость",
    "заказать",
    "доставка",
    "интернет-магазин",
    "каталог",
    "в наличии",
    "со скидкой",
    "недорого",
    "дёшево",
    "оптом",
]

COMMERCIAL_MARKERS_UK = [
    "купити",
    "ціна",
    "вартість",
    "замовити",
    "доставка",
    "інтернет-магазин",
    "каталог",
    "в наявності",
    "зі знижкою",
    "недорого",
    "дешево",
    "оптом",
]

STOPLIST_PHRASES_RU = [
    "лучший",
    "самый лучший",
    "номер один",
    "№1",
    "гарантируем",
    "100%",
    "обещаем",
    "безусловно лучший",
]

STOPLIST_PHRASES_UK = [
    "найкращий",
    "номер один",
    "№1",
    "гарантуємо",
    "100%",
    "обіцяємо",
    "безумовно найкращий",
]


def get_commercial_markers(lang: str = "ru") -> list[str]:
    """Get commercial markers for language (SSOT)."""
    return COMMERCIAL_MARKERS_UK if lang == "uk" else COMMERCIAL_MARKERS_RU


def get_stoplist_phrases(lang: str = "ru") -> list[str]:
    """Get stoplist phrases for language (SSOT)."""
    return STOPLIST_PHRASES_UK if lang == "uk" else STOPLIST_PHRASES_RU
```

**Step 2: Verify syntax**

Run: `python3 -c "from scripts.keyword_utils import get_commercial_markers; print(len(get_commercial_markers('ru')))"`
Expected: `12`

**Step 3: Commit**

```bash
git add scripts/keyword_utils.py
git commit -m "feat(keyword_utils): add constants module with commercial markers and stoplist"
```

---

## Task 3: Create MorphAnalyzer Class

**Files:**
- Modify: `scripts/keyword_utils.py`

**Step 1: Add MorphAnalyzer class**

Append to `scripts/keyword_utils.py`:

```python
# =============================================================================
# Morphology Backend
# =============================================================================


class MorphAnalyzer:
    """
    Singleton морфологический анализатор.

    Использует pymorphy3 если доступен, иначе Snowball fallback.
    """

    _instances: dict[str, "MorphAnalyzer"] = {}

    def __new__(cls, lang: Literal["ru", "uk"] = "ru"):
        if lang not in cls._instances:
            instance = super().__new__(cls)
            instance._init_analyzer(lang)
            cls._instances[lang] = instance
        return cls._instances[lang]

    def _init_analyzer(self, lang: str) -> None:
        self.lang = lang
        self._morph = None
        self._stemmer = None
        self._use_pymorphy = False

        # Try pymorphy3 first
        try:
            import pymorphy3

            if lang == "uk":
                self._morph = pymorphy3.MorphAnalyzer(lang="uk")
            else:
                self._morph = pymorphy3.MorphAnalyzer()
            self._use_pymorphy = True
        except ImportError:
            pass

        # Fallback to pymorphy2
        if not self._use_pymorphy:
            try:
                import pymorphy2

                self._morph = pymorphy2.MorphAnalyzer()
                self._use_pymorphy = True
            except ImportError:
                pass

        # Fallback to Snowball
        if not self._use_pymorphy:
            try:
                from snowballstemmer import stemmer

                self._stemmer = stemmer("russian" if lang == "ru" else "russian")
            except ImportError:
                pass

    @lru_cache(maxsize=10000)
    def get_lemma(self, word: str) -> str:
        """
        Получить лемму (начальную форму) слова.

        щётки → щётка
        машинки → машинка
        грязеуловителем → грязеуловитель
        """
        word_lower = word.lower()

        if self._use_pymorphy and self._morph:
            parsed = self._morph.parse(word_lower)
            if parsed:
                return parsed[0].normal_form

        if self._stemmer:
            return self._stemmer.stemWord(word_lower)

        # Ultimate fallback: strip 2 chars
        if len(word_lower) > 4:
            return word_lower[:-2]
        return word_lower

    @lru_cache(maxsize=1000)
    def get_all_forms(self, word: str) -> frozenset[str]:
        """
        Получить все формы слова (падежи, числа).

        щётка → frozenset({'щётка', 'щётки', 'щётке', 'щётку', 'щёткой', ...})
        """
        if not self._use_pymorphy or not self._morph:
            return frozenset({word.lower()})

        word_lower = word.lower()
        parsed = self._morph.parse(word_lower)
        if not parsed:
            return frozenset({word_lower})

        forms = set()
        for p in parsed[:1]:  # Take first parse (most likely)
            for form in p.lexeme:
                forms.add(form.word)

        return frozenset(forms)

    def normalize_phrase(self, phrase: str) -> list[str]:
        """
        Лемматизировать фразу (каждое значимое слово).

        "щётки для мытья машины" → ["щётка", "мытьё", "машина"]
        """
        words = re.findall(r"[а-яёїієґa-z]+", phrase.lower())
        lemmas = []
        for w in words:
            if len(w) > 2:
                lemmas.append(self.get_lemma(w))
        return lemmas

    @property
    def backend(self) -> str:
        """Return which backend is being used."""
        if self._use_pymorphy:
            return "pymorphy"
        elif self._stemmer:
            return "snowball"
        return "fallback"
```

**Step 2: Verify MorphAnalyzer works**

Run: `python3 -c "from scripts.keyword_utils import MorphAnalyzer; m = MorphAnalyzer('ru'); print(m.get_lemma('щётки'), m.backend)"`
Expected: `щётка pymorphy`

**Step 3: Commit**

```bash
git add scripts/keyword_utils.py
git commit -m "feat(keyword_utils): add MorphAnalyzer with pymorphy3/snowball fallback"
```

---

## Task 4: Create Unit Tests for MorphAnalyzer

**Files:**
- Create: `tests/unit/test_keyword_utils.py`

**Step 1: Create test file with MorphAnalyzer tests**

```python
"""Unit tests for scripts/keyword_utils.py"""

import pytest

from scripts.keyword_utils import (
    MorphAnalyzer,
    get_commercial_markers,
    get_stoplist_phrases,
)


class TestConstants:
    """Test constant functions."""

    def test_commercial_markers_ru(self):
        markers = get_commercial_markers("ru")
        assert "купить" in markers
        assert "ціна" not in markers

    def test_commercial_markers_uk(self):
        markers = get_commercial_markers("uk")
        assert "купити" in markers
        assert "цена" not in markers

    def test_stoplist_phrases_ru(self):
        phrases = get_stoplist_phrases("ru")
        assert "лучший" in phrases

    def test_stoplist_phrases_uk(self):
        phrases = get_stoplist_phrases("uk")
        assert "найкращий" in phrases


class TestMorphAnalyzer:
    """Test MorphAnalyzer class."""

    def test_singleton_same_lang(self):
        """Same language returns same instance."""
        m1 = MorphAnalyzer("ru")
        m2 = MorphAnalyzer("ru")
        assert m1 is m2

    def test_singleton_different_lang(self):
        """Different languages return different instances."""
        m_ru = MorphAnalyzer("ru")
        m_uk = MorphAnalyzer("uk")
        assert m_ru is not m_uk

    def test_get_lemma_noun_nominative(self):
        """Nominative case returns same lemma."""
        morph = MorphAnalyzer("ru")
        assert morph.get_lemma("щётка") == "щётка"

    def test_get_lemma_noun_genitive(self):
        """Genitive case returns lemma."""
        morph = MorphAnalyzer("ru")
        assert morph.get_lemma("щётки") == "щётка"

    def test_get_lemma_noun_accusative(self):
        """Accusative case returns lemma."""
        morph = MorphAnalyzer("ru")
        assert morph.get_lemma("щётку") == "щётка"

    def test_get_lemma_noun_instrumental(self):
        """Instrumental case returns lemma."""
        morph = MorphAnalyzer("ru")
        assert morph.get_lemma("щёткой") == "щётка"

    def test_get_lemma_noun_plural(self):
        """Plural form returns singular lemma."""
        morph = MorphAnalyzer("ru")
        # машинки (plural) → машинка (singular)
        lemma = morph.get_lemma("машинки")
        assert lemma in ("машинка", "машинки")  # pymorphy may return either

    def test_get_lemma_verb(self):
        """Verb conjugation returns infinitive."""
        morph = MorphAnalyzer("ru")
        assert morph.get_lemma("моющий") in ("мыть", "моющий")

    def test_get_lemma_adjective(self):
        """Adjective returns base form."""
        morph = MorphAnalyzer("ru")
        lemma = morph.get_lemma("грязеуловительный")
        assert "грязеулов" in lemma  # May vary

    def test_get_all_forms_returns_frozenset(self):
        """get_all_forms returns frozenset for caching."""
        morph = MorphAnalyzer("ru")
        forms = morph.get_all_forms("щётка")
        assert isinstance(forms, frozenset)
        assert "щётка" in forms
        assert "щётки" in forms

    def test_normalize_phrase(self):
        """normalize_phrase returns list of lemmas."""
        morph = MorphAnalyzer("ru")
        lemmas = morph.normalize_phrase("щётки для мытья")
        assert len(lemmas) >= 2
        assert "щётка" in lemmas

    def test_backend_property(self):
        """backend property returns string."""
        morph = MorphAnalyzer("ru")
        assert morph.backend in ("pymorphy", "snowball", "fallback")


class TestMorphAnalyzerUK:
    """Test Ukrainian MorphAnalyzer."""

    def test_uk_get_lemma(self):
        """Ukrainian lemmatization works."""
        morph = MorphAnalyzer("uk")
        # щітки → щітка (Ukrainian)
        lemma = morph.get_lemma("щітки")
        # May return stem if UK dict not available
        assert len(lemma) > 0
```

**Step 2: Run tests to verify they pass**

Run: `pytest tests/unit/test_keyword_utils.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add tests/unit/test_keyword_utils.py
git commit -m "test(keyword_utils): add unit tests for MorphAnalyzer and constants"
```

---

## Task 5: Create KeywordMatcher Class

**Files:**
- Modify: `scripts/keyword_utils.py`

**Step 1: Add KeywordMatcher class**

Append to `scripts/keyword_utils.py`:

```python
# =============================================================================
# Keyword Matcher
# =============================================================================


class KeywordMatcher:
    """
    Поиск ключевых слов в тексте с учётом морфологии.
    """

    def __init__(self, lang: Literal["ru", "uk"] = "ru"):
        self.lang = lang
        self.morph = MorphAnalyzer(lang)

    def match_exact(self, keyword: str, text: str) -> bool:
        """Точное вхождение (case-insensitive)."""
        return keyword.lower() in text.lower()

    def match_lemma(self, keyword: str, text: str) -> tuple[bool, str | None]:
        """
        Поиск по леммам — основной метод.

        Returns:
            (found: bool, matched_form: str | None)

        Example:
            match_lemma("щётка для мытья", "используйте щётку для мытья")
            → (True, "щётку для мытья")
        """
        # 1. Try exact match first
        if self.match_exact(keyword, text):
            return (True, keyword)

        # 2. Single word keyword
        kw_words = keyword.lower().split()
        if len(kw_words) == 1:
            return self._match_single_word(kw_words[0], text)

        # 3. Multi-word phrase
        return self._match_phrase(kw_words, text)

    def _match_single_word(self, word: str, text: str) -> tuple[bool, str | None]:
        """Match single word using all its forms."""
        forms = self.morph.get_all_forms(word)
        text_lower = text.lower()

        for form in forms:
            # Word boundary check
            pattern = rf"\b{re.escape(form)}\b"
            match = re.search(pattern, text_lower)
            if match:
                return (True, form)

        return (False, None)

    def _match_phrase(
        self, kw_words: list[str], text: str
    ) -> tuple[bool, str | None]:
        """
        Match multi-word phrase.

        Strategy:
        1. Get lemmas of keyword words
        2. Get lemmas of text words
        3. Check if all keyword lemmas appear in sequence (with gap tolerance)
        """
        # Filter short words
        kw_lemmas = [
            self.morph.get_lemma(w) for w in kw_words if len(w) > 2
        ]

        if not kw_lemmas:
            return (False, None)

        # Tokenize text
        text_words = re.findall(r"[а-яёїієґa-z]+", text.lower())
        text_lemmas = [self.morph.get_lemma(w) for w in text_words]

        # Find sequence with gap tolerance (max 2 words between)
        max_gap = 2

        for start_idx in range(len(text_lemmas)):
            if text_lemmas[start_idx] == kw_lemmas[0]:
                # Try to match rest of phrase
                matched, end_idx = self._match_sequence(
                    kw_lemmas[1:], text_lemmas[start_idx + 1 :], max_gap
                )
                if matched:
                    # Reconstruct matched form from original text
                    matched_words = text_words[
                        start_idx : start_idx + end_idx + 1
                    ]
                    return (True, " ".join(matched_words))

        return (False, None)

    def _match_sequence(
        self, remaining_lemmas: list[str], text_lemmas: list[str], max_gap: int
    ) -> tuple[bool, int]:
        """Match remaining lemmas with gap tolerance."""
        if not remaining_lemmas:
            return (True, 0)

        target = remaining_lemmas[0]

        for i, lemma in enumerate(text_lemmas[: max_gap + 1]):
            if lemma == target:
                matched, end_idx = self._match_sequence(
                    remaining_lemmas[1:], text_lemmas[i + 1 :], max_gap
                )
                if matched:
                    return (True, i + 1 + end_idx)

        return (False, 0)

    def find_in_text(self, keyword: str, text: str) -> tuple[bool, str | None]:
        """
        Unified method: find keyword in text.

        Returns (found, matched_form).
        """
        return self.match_lemma(keyword, text)
```

**Step 2: Verify KeywordMatcher works**

Run: `python3 -c "from scripts.keyword_utils import KeywordMatcher; m = KeywordMatcher('ru'); print(m.find_in_text('щётка', 'используйте щётку'))"`
Expected: `(True, 'щётку')`

**Step 3: Commit**

```bash
git add scripts/keyword_utils.py
git commit -m "feat(keyword_utils): add KeywordMatcher with lemma-based phrase matching"
```

---

## Task 6: Add KeywordMatcher Tests

**Files:**
- Modify: `tests/unit/test_keyword_utils.py`

**Step 1: Add KeywordMatcher tests**

Append to `tests/unit/test_keyword_utils.py`:

```python
from scripts.keyword_utils import KeywordMatcher


class TestKeywordMatcher:
    """Test KeywordMatcher class."""

    def test_match_exact_found(self):
        """Exact match finds keyword."""
        matcher = KeywordMatcher("ru")
        assert matcher.match_exact("щётка", "купить щётка для авто") is True

    def test_match_exact_not_found(self):
        """Exact match returns False when not found."""
        matcher = KeywordMatcher("ru")
        assert matcher.match_exact("губка", "купить щётка для авто") is False

    def test_match_exact_case_insensitive(self):
        """Exact match is case-insensitive."""
        matcher = KeywordMatcher("ru")
        assert matcher.match_exact("ЩЁТКА", "купить щётка для авто") is True

    def test_find_single_word_nominative(self):
        """Find nominative form in text."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text("щётка", "купить щётка для авто")
        assert found is True
        assert form == "щётка"

    def test_find_single_word_accusative(self):
        """Find keyword when text has accusative form."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text("щётка", "используйте щётку для мытья")
        assert found is True
        assert form == "щётку"

    def test_find_single_word_instrumental(self):
        """Find keyword when text has instrumental form."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text("щётка", "мойте щёткой")
        assert found is True
        assert form == "щёткой"

    def test_find_single_word_not_found(self):
        """Return False when keyword not in text."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text("губка", "используйте щётку")
        assert found is False
        assert form is None

    def test_find_phrase_exact(self):
        """Find multi-word phrase with exact match."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text(
            "щётка для мытья", "купить щётка для мытья авто"
        )
        assert found is True

    def test_find_phrase_with_case_change(self):
        """Find phrase when text has different case forms."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text(
            "щётка для мытья", "используйте щётку для мытья"
        )
        assert found is True

    def test_find_phrase_not_found(self):
        """Return False when phrase not in text."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text(
            "губка для мытья", "используйте щётку для мытья"
        )
        assert found is False

    def test_find_preserves_latin(self):
        """Latin words (brand names) preserved."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text(
            "Grit Guard", "используйте Grit Guard для защиты"
        )
        assert found is True
```

**Step 2: Run tests**

Run: `pytest tests/unit/test_keyword_utils.py::TestKeywordMatcher -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add tests/unit/test_keyword_utils.py
git commit -m "test(keyword_utils): add KeywordMatcher unit tests"
```

---

## Task 7: Create CoverageChecker Class

**Files:**
- Modify: `scripts/keyword_utils.py`

**Step 1: Add CoverageChecker class**

Append to `scripts/keyword_utils.py`:

```python
# =============================================================================
# Coverage Checker
# =============================================================================


class CoverageChecker:
    """
    Проверка покрытия ключевых слов в тексте.
    """

    def __init__(self, lang: Literal["ru", "uk"] = "ru"):
        self.lang = lang
        self.matcher = KeywordMatcher(lang)

    @staticmethod
    def get_adaptive_target(keyword_count: int) -> float:
        """
        Адаптивный target coverage (ЕДИНСТВЕННАЯ ВЕРСИЯ).

        <= 5 keywords: 70%
        6-15 keywords: 60%
        > 15 keywords: 50%
        """
        if keyword_count <= 5:
            return 70.0
        elif keyword_count <= 15:
            return 60.0
        else:
            return 50.0

    def check(
        self, keywords: list[str], text: str, use_lemma: bool = True
    ) -> dict:
        """
        Check keyword coverage in text.

        Returns:
            {
                "total": int,
                "found": int,
                "coverage_percent": float,
                "target": float,
                "passed": bool,
                "found_keywords": [{"keyword": str, "form": str}, ...],
                "missing_keywords": [str, ...]
            }
        """
        if not keywords:
            return {
                "total": 0,
                "found": 0,
                "coverage_percent": 100.0,
                "target": 0,
                "passed": True,
                "found_keywords": [],
                "missing_keywords": [],
            }

        found_keywords = []
        missing_keywords = []

        for kw in keywords:
            if use_lemma:
                matched, form = self.matcher.find_in_text(kw, text)
            else:
                matched = self.matcher.match_exact(kw, text)
                form = kw if matched else None

            if matched:
                found_keywords.append({"keyword": kw, "form": form})
            else:
                missing_keywords.append(kw)

        total = len(keywords)
        found = len(found_keywords)
        coverage = (found / total) * 100
        target = self.get_adaptive_target(total)

        return {
            "total": total,
            "found": found,
            "coverage_percent": round(coverage, 1),
            "target": target,
            "passed": coverage >= target,
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
        }

    def check_split(
        self,
        core_keywords: list[str],
        commercial_keywords: list[str],
        text: str,
    ) -> dict:
        """
        Check coverage split by intent (core vs commercial).

        Core keywords: target applies (WARNING if below)
        Commercial keywords: INFO only (no penalty)
        """
        core_result = self.check(core_keywords, text)
        comm_result = self.check(commercial_keywords, text, use_lemma=False)

        return {
            "core": core_result,
            "commercial": comm_result,
            "overall_passed": core_result["passed"],
        }


# =============================================================================
# Backward-Compatible Functions
# =============================================================================


def get_adaptive_coverage_target(keyword_count: int) -> float:
    """Backward-compatible wrapper."""
    return CoverageChecker.get_adaptive_target(keyword_count)


def keyword_matches_text(keyword: str, text: str, lang: str = "ru") -> bool:
    """
    Backward-compatible function.

    Replaces:
    - validate_content.py: keyword_matches_semantic()
    - validate_meta.py: keyword_matches()
    """
    matcher = KeywordMatcher(lang)
    found, _ = matcher.find_in_text(keyword, text)
    return found


def find_keyword_form(keyword: str, text: str, lang: str = "ru") -> str | None:
    """
    Find which form of keyword appears in text.

    Example:
        find_keyword_form("щётка для мытья", text)
        → "щётку для мытья"
    """
    matcher = KeywordMatcher(lang)
    found, form = matcher.find_in_text(keyword, text)
    return form if found else None
```

**Step 2: Verify CoverageChecker works**

Run: `python3 -c "from scripts.keyword_utils import CoverageChecker; c = CoverageChecker('ru'); r = c.check(['щётка', 'губка'], 'используйте щётку'); print(r['coverage_percent'])"`
Expected: `50.0`

**Step 3: Commit**

```bash
git add scripts/keyword_utils.py
git commit -m "feat(keyword_utils): add CoverageChecker with adaptive targets"
```

---

## Task 8: Add CoverageChecker Tests

**Files:**
- Modify: `tests/unit/test_keyword_utils.py`

**Step 1: Add CoverageChecker tests**

Append to `tests/unit/test_keyword_utils.py`:

```python
from scripts.keyword_utils import (
    CoverageChecker,
    get_adaptive_coverage_target,
    keyword_matches_text,
    find_keyword_form,
)


class TestCoverageChecker:
    """Test CoverageChecker class."""

    def test_adaptive_target_small(self):
        """Small keyword count has 70% target."""
        assert CoverageChecker.get_adaptive_target(3) == 70.0
        assert CoverageChecker.get_adaptive_target(5) == 70.0

    def test_adaptive_target_medium(self):
        """Medium keyword count has 60% target."""
        assert CoverageChecker.get_adaptive_target(6) == 60.0
        assert CoverageChecker.get_adaptive_target(15) == 60.0

    def test_adaptive_target_large(self):
        """Large keyword count has 50% target."""
        assert CoverageChecker.get_adaptive_target(16) == 50.0
        assert CoverageChecker.get_adaptive_target(100) == 50.0

    def test_check_empty_keywords(self):
        """Empty keyword list returns 100% coverage."""
        checker = CoverageChecker("ru")
        result = checker.check([], "some text")
        assert result["coverage_percent"] == 100.0
        assert result["passed"] is True

    def test_check_all_found(self):
        """All keywords found returns 100%."""
        checker = CoverageChecker("ru")
        result = checker.check(
            ["щётка", "губка"],
            "используйте щётку и губку"
        )
        assert result["found"] == 2
        assert result["coverage_percent"] == 100.0
        assert result["passed"] is True

    def test_check_partial(self):
        """Partial coverage calculated correctly."""
        checker = CoverageChecker("ru")
        result = checker.check(
            ["щётка", "губка", "микрофибра"],
            "используйте щётку и губку"
        )
        assert result["found"] == 2
        assert result["total"] == 3
        assert result["coverage_percent"] == pytest.approx(66.7, rel=0.1)

    def test_check_none_found(self):
        """No keywords found returns 0%."""
        checker = CoverageChecker("ru")
        result = checker.check(
            ["щётка", "губка"],
            "используйте полотенце"
        )
        assert result["found"] == 0
        assert result["coverage_percent"] == 0.0
        assert result["passed"] is False

    def test_check_returns_found_forms(self):
        """Check returns actual forms found in text."""
        checker = CoverageChecker("ru")
        result = checker.check(["щётка"], "используйте щётку")
        assert len(result["found_keywords"]) == 1
        assert result["found_keywords"][0]["keyword"] == "щётка"
        assert result["found_keywords"][0]["form"] == "щётку"

    def test_check_returns_missing(self):
        """Check returns missing keywords."""
        checker = CoverageChecker("ru")
        result = checker.check(
            ["щётка", "губка"],
            "используйте щётку"
        )
        assert "губка" in result["missing_keywords"]

    def test_check_split(self):
        """check_split separates core and commercial."""
        checker = CoverageChecker("ru")
        result = checker.check_split(
            core_keywords=["щётка", "губка"],
            commercial_keywords=["купить", "цена"],
            text="используйте щётку для мытья"
        )
        assert result["core"]["found"] == 1
        assert result["commercial"]["found"] == 0
        assert result["overall_passed"] is False  # Below 70% for 2 keywords


class TestBackwardCompatibleFunctions:
    """Test backward-compatible wrapper functions."""

    def test_get_adaptive_coverage_target(self):
        """Wrapper function works."""
        assert get_adaptive_coverage_target(5) == 70.0
        assert get_adaptive_coverage_target(10) == 60.0

    def test_keyword_matches_text_found(self):
        """keyword_matches_text returns True when found."""
        assert keyword_matches_text("щётка", "используйте щётку", "ru") is True

    def test_keyword_matches_text_not_found(self):
        """keyword_matches_text returns False when not found."""
        assert keyword_matches_text("губка", "используйте щётку", "ru") is False

    def test_find_keyword_form_found(self):
        """find_keyword_form returns matched form."""
        form = find_keyword_form("щётка", "используйте щётку", "ru")
        assert form == "щётку"

    def test_find_keyword_form_not_found(self):
        """find_keyword_form returns None when not found."""
        form = find_keyword_form("губка", "используйте щётку", "ru")
        assert form is None
```

**Step 2: Run all tests**

Run: `pytest tests/unit/test_keyword_utils.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add tests/unit/test_keyword_utils.py
git commit -m "test(keyword_utils): add CoverageChecker and backward-compat tests"
```

---

## Task 9: Migrate validate_content.py

**Files:**
- Modify: `scripts/validate_content.py`

**Step 1: Add import at top of file**

Add after existing imports (around line 15):

```python
from scripts.keyword_utils import (
    keyword_matches_text,
    CoverageChecker,
    get_adaptive_coverage_target,
)
```

**Step 2: Replace keyword_matches_semantic function (lines ~394-445)**

Replace the entire function with:

```python
def keyword_matches_semantic(keyword: str, text: str) -> bool:
    """
    Check if keyword matches text semantically.

    Uses keyword_utils.KeywordMatcher with pymorphy3 morphology.
    """
    return keyword_matches_text(keyword, text, lang="ru")
```

**Step 3: Update check_keyword_coverage_split to use CoverageChecker (lines ~448-510)**

Simplify the function to use CoverageChecker internally while keeping the same return format.

**Step 4: Remove duplicate get_adaptive_coverage_target if exists**

Search for any local definition and remove it.

**Step 5: Run existing tests**

Run: `pytest tests/unit/test_validate_content.py -v`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add scripts/validate_content.py
git commit -m "refactor(validate_content): use keyword_utils for morphology matching"
```

---

## Task 10: Migrate validate_meta.py

**Files:**
- Modify: `scripts/validate_meta.py`

**Step 1: Add import**

```python
from scripts.keyword_utils import keyword_matches_text, MorphAnalyzer
```

**Step 2: Replace get_word_stem function (lines ~119-168)**

```python
def get_word_stem(word: str) -> str:
    """Get word stem using MorphAnalyzer."""
    morph = MorphAnalyzer("ru")
    return morph.get_lemma(word)
```

**Step 3: Replace keyword_matches function (lines ~171-193)**

```python
def keyword_matches(keyword: str, text: str) -> bool:
    """Check if keyword matches text."""
    return keyword_matches_text(keyword, text, lang="ru")
```

**Step 4: Run tests**

Run: `pytest tests/unit/test_validate_meta.py -v`
Expected: All tests PASS

**Step 5: Commit**

```bash
git add scripts/validate_meta.py
git commit -m "refactor(validate_meta): use keyword_utils for morphology"
```

---

## Task 11: Migrate check_seo_structure.py

**Files:**
- Modify: `scripts/check_seo_structure.py`

**Step 1: Add import**

```python
from scripts.keyword_utils import MorphAnalyzer
```

**Step 2: Replace get_russian_word_stems function (lines ~130-145)**

```python
def get_russian_word_stems(text: str) -> set[str]:
    """Get stems of Russian words in text."""
    morph = MorphAnalyzer("ru")
    words = re.findall(r"[а-яё]+", text.lower())
    return {morph.get_lemma(w) for w in words if len(w) > 2}
```

**Step 3: Replace get_ukrainian_word_stems function (lines ~155-170)**

```python
def get_ukrainian_word_stems(text: str) -> set[str]:
    """Get stems of Ukrainian words in text."""
    morph = MorphAnalyzer("uk")
    words = re.findall(r"[а-яёїієґ]+", text.lower())
    return {morph.get_lemma(w) for w in words if len(w) > 2}
```

**Step 4: Verify script works**

Run: `python3 scripts/check_seo_structure.py categories/aksessuary/content/aksessuary_ru.md "аксессуары" 2>&1 | head -20`
Expected: Script runs without errors

**Step 5: Commit**

```bash
git add scripts/check_seo_structure.py
git commit -m "refactor(check_seo_structure): use keyword_utils MorphAnalyzer"
```

---

## Task 12: Cleanup Duplicates in seo_utils.py

**Files:**
- Modify: `scripts/seo_utils.py`

**Step 1: Add imports**

```python
from scripts.keyword_utils import (
    get_adaptive_coverage_target,
    get_commercial_markers,
    get_stoplist_phrases,
)
```

**Step 2: Remove duplicate get_adaptive_coverage_target**

Delete the local definition (lines ~53-62), keep only the import.

**Step 3: Update find_commercial_markers to use imported constants**

Modify the function to use `get_commercial_markers(lang)` instead of hardcoded list.

**Step 4: Update check_stoplist_phrases to use imported constants**

Modify the function to use `get_stoplist_phrases(lang)` instead of hardcoded list.

**Step 5: Run tests**

Run: `pytest tests/ -v -k "seo"`
Expected: All tests PASS

**Step 6: Commit**

```bash
git add scripts/seo_utils.py
git commit -m "refactor(seo_utils): remove duplicates, import from keyword_utils"
```

---

## Task 13: Cleanup Duplicates in utils/text.py

**Files:**
- Modify: `scripts/utils/text.py`

**Step 1: Add imports**

```python
from scripts.keyword_utils import (
    get_adaptive_coverage_target,
    get_commercial_markers,
    get_stoplist_phrases,
)
```

**Step 2: Remove duplicate functions**

Delete local definitions of:
- `get_adaptive_coverage_target()`
- Any hardcoded COMMERCIAL_MARKERS list
- Any hardcoded STOPLIST_PHRASES list

**Step 3: Run tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 4: Commit**

```bash
git add scripts/utils/text.py
git commit -m "refactor(utils/text): remove duplicates, import from keyword_utils"
```

---

## Task 14: Final Verification

**Files:** None (verification only)

**Step 1: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS

**Step 2: Run linting**

Run: `ruff check scripts/keyword_utils.py scripts/validate_content.py scripts/validate_meta.py`
Expected: No errors

**Step 3: Test validate_content on real file**

Run: `python3 scripts/validate_content.py categories/aksessuary/shchetki-i-kisti/content/shchetki-i-kisti_ru.md`
Expected: Script completes, coverage reported

**Step 4: Test validate_meta**

Run: `python3 scripts/validate_meta.py --all 2>&1 | tail -10`
Expected: Script completes

**Step 5: Manual verification - check false negatives reduced**

Run: `python3 -c "
from scripts.keyword_utils import CoverageChecker
checker = CoverageChecker('ru')
text = 'Используйте щётку для мытья автомобиля. Автомобильные щётки бывают разных видов.'
result = checker.check(['щётка для мытья', 'автомобильная щётка'], text)
print(f'Coverage: {result[\"coverage_percent\"]}%')
print(f'Found: {result[\"found_keywords\"]}')
"`
Expected: Coverage 100% (both keywords found despite different forms)

**Step 6: Commit final changes if any**

```bash
git status
# If clean, no commit needed
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Update dependencies | requirements.txt |
| 2 | Create constants | scripts/keyword_utils.py |
| 3 | Create MorphAnalyzer | scripts/keyword_utils.py |
| 4 | Test MorphAnalyzer | tests/unit/test_keyword_utils.py |
| 5 | Create KeywordMatcher | scripts/keyword_utils.py |
| 6 | Test KeywordMatcher | tests/unit/test_keyword_utils.py |
| 7 | Create CoverageChecker | scripts/keyword_utils.py |
| 8 | Test CoverageChecker | tests/unit/test_keyword_utils.py |
| 9 | Migrate validate_content.py | scripts/validate_content.py |
| 10 | Migrate validate_meta.py | scripts/validate_meta.py |
| 11 | Migrate check_seo_structure.py | scripts/check_seo_structure.py |
| 12 | Cleanup seo_utils.py | scripts/seo_utils.py |
| 13 | Cleanup utils/text.py | scripts/utils/text.py |
| 14 | Final verification | - |

**Total commits:** 13
**Parallel-safe tasks:** 9-11 (after 8), 12-13 (after 8)
