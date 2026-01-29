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
            except (ImportError, AttributeError):
                # AttributeError: Python 3.12 removed inspect.getargspec
                pass

        # Fallback to Snowball
        if not self._use_pymorphy:
            try:
                from snowballstemmer import stemmer

                self._stemmer = stemmer("russian" if lang == "ru" else "russian")
            except ImportError:
                pass

    @lru_cache(maxsize=10000)  # noqa: B019 - singleton, no memory leak
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

    @lru_cache(maxsize=1000)  # noqa: B019 - singleton, no memory leak
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
        """Match single word using stem comparison."""
        text_lower = text.lower()

        # Strategy 1: Try exact forms from pymorphy (if available)
        forms = self.morph.get_all_forms(word)
        for form in forms:
            pattern = rf"\b{re.escape(form)}\b"
            match = re.search(pattern, text_lower)
            if match:
                return (True, form)

        # Strategy 2: Compare stems (works with Snowball fallback)
        word_stem = self.morph.get_lemma(word)
        text_words = re.findall(r"[а-яёїієґa-z]+", text_lower)

        for text_word in text_words:
            text_stem = self.morph.get_lemma(text_word)
            if word_stem == text_stem:
                return (True, text_word)

        return (False, None)

    def _match_phrase(self, kw_words: list[str], text: str) -> tuple[bool, str | None]:
        """
        Match multi-word phrase.

        Strategy:
        1. Get lemmas of keyword words
        2. Get lemmas of text words
        3. Check if all keyword lemmas appear in sequence (with gap tolerance)
        """
        # Filter short words
        kw_lemmas = [self.morph.get_lemma(w) for w in kw_words if len(w) > 2]

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
                matched, end_idx = self._match_sequence(kw_lemmas[1:], text_lemmas[start_idx + 1 :], max_gap)
                if matched:
                    # Reconstruct matched form from original text
                    matched_words = text_words[start_idx : start_idx + end_idx + 1]
                    return (True, " ".join(matched_words))

        return (False, None)

    def _match_sequence(self, remaining_lemmas: list[str], text_lemmas: list[str], max_gap: int) -> tuple[bool, int]:
        """Match remaining lemmas with gap tolerance."""
        if not remaining_lemmas:
            return (True, 0)

        target = remaining_lemmas[0]

        for i, lemma in enumerate(text_lemmas[: max_gap + 1]):
            if lemma == target:
                matched, end_idx = self._match_sequence(remaining_lemmas[1:], text_lemmas[i + 1 :], max_gap)
                if matched:
                    return (True, i + 1 + end_idx)

        return (False, 0)

    def find_in_text(self, keyword: str, text: str) -> tuple[bool, str | None]:
        """
        Unified method: find keyword in text.

        Returns (found, matched_form).
        """
        return self.match_lemma(keyword, text)


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

    def check(self, keywords: list[str], text: str, use_lemma: bool = True) -> dict:
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
