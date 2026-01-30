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

    def test_get_lemma_same_stem_for_cases(self):
        """Different cases of same word return same stem/lemma."""
        morph = MorphAnalyzer("ru")
        # All forms should map to same stem (works with both pymorphy and snowball)
        base = morph.get_lemma("щётка")
        assert morph.get_lemma("щётки") == base
        assert morph.get_lemma("щётку") == base
        assert morph.get_lemma("щёткой") == base

    def test_get_lemma_noun_plural(self):
        """Plural form returns same stem as singular."""
        morph = MorphAnalyzer("ru")
        # машинка and машинки should have same stem
        singular = morph.get_lemma("машинка")
        plural = morph.get_lemma("машинки")
        assert singular == plural

    def test_get_lemma_verb(self):
        """Verb forms should have consistent stem."""
        morph = MorphAnalyzer("ru")
        lemma = morph.get_lemma("моющий")
        assert len(lemma) > 0  # Just verify it returns something

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
        # With snowball fallback, only original form is returned
        # With pymorphy, multiple forms are returned
        assert len(forms) >= 1

    def test_normalize_phrase(self):
        """normalize_phrase returns list of lemmas."""
        morph = MorphAnalyzer("ru")
        lemmas = morph.normalize_phrase("щётки для мытья")
        assert len(lemmas) >= 2
        # Check that lemmas are consistent (same words return same stems)
        base_lemma = morph.get_lemma("щётка")
        # "щётки" should normalize to same as "щётка"
        assert morph.get_lemma("щётки") == base_lemma

    def test_backend_property(self):
        """backend property returns string."""
        morph = MorphAnalyzer("ru")
        assert morph.backend in ("pymorphy", "snowball", "fallback")


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


from scripts.keyword_utils import KeywordMatcher


class TestKeywordMatcherUK:
    """Test Ukrainian keyword matching with proper morphology."""

    def test_uk_keyword_match_declension_shchitka(self):
        """UK: 'щітка для миття' should match 'щітку для миття'."""
        matcher = KeywordMatcher(lang="uk")
        found, form = matcher.find_in_text("щітка для миття", "Використовуйте щітку для миття авто.")
        assert found, "Should match declined form щітку"

    def test_uk_keyword_match_plural_shampun(self):
        """UK: 'шампунь для авто' should match 'шампуні для авто'."""
        matcher = KeywordMatcher(lang="uk")
        found, form = matcher.find_in_text("шампунь для авто", "Купуйте шампуні для авто в нашому магазині.")
        assert found, "Should match plural form шампуні"

    def test_uk_keyword_match_instrumental_pina(self):
        """UK: 'піна' should match 'піною'."""
        matcher = KeywordMatcher(lang="uk")
        found, form = matcher.find_in_text("активна піна", "Миття активною піною дає кращий результат.")
        assert found, "Should match instrumental form піною"

    def test_uk_keyword_single_word_accusative(self):
        """UK: Find keyword when text has accusative form."""
        matcher = KeywordMatcher(lang="uk")
        found, form = matcher.find_in_text("щітка", "використовуйте щітку для миття")
        assert found is True
        assert form == "щітку"


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
        found, form = matcher.find_in_text("щётка для мытья", "купить щётка для мытья авто")
        assert found is True

    def test_find_phrase_with_case_change(self):
        """Find phrase when text has different case forms."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text("щётка для мытья", "используйте щётку для мытья")
        assert found is True

    def test_find_phrase_not_found(self):
        """Return False when phrase not in text."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text("губка для мытья", "используйте щётку для мытья")
        assert found is False

    def test_find_preserves_latin(self):
        """Latin words (brand names) preserved."""
        matcher = KeywordMatcher("ru")
        found, form = matcher.find_in_text("Grit Guard", "используйте Grit Guard для защиты")
        assert found is True


from scripts.keyword_utils import (
    CoverageChecker,
    find_keyword_form,
    get_adaptive_coverage_target,
    keyword_matches_text,
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
        result = checker.check(["щётка", "губка"], "используйте щётку и губку")
        assert result["found"] == 2
        assert result["coverage_percent"] == 100.0
        assert result["passed"] is True

    def test_check_partial(self):
        """Partial coverage calculated correctly."""
        checker = CoverageChecker("ru")
        result = checker.check(["щётка", "губка", "микрофибра"], "используйте щётку и губку")
        assert result["found"] == 2
        assert result["total"] == 3
        assert result["coverage_percent"] == pytest.approx(66.7, rel=0.1)

    def test_check_none_found(self):
        """No keywords found returns 0%."""
        checker = CoverageChecker("ru")
        result = checker.check(["щётка", "губка"], "используйте полотенце")
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
        result = checker.check(["щётка", "губка"], "используйте щётку")
        assert "губка" in result["missing_keywords"]

    def test_check_split(self):
        """check_split separates core and commercial."""
        checker = CoverageChecker("ru")
        result = checker.check_split(
            core_keywords=["щётка", "губка"], commercial_keywords=["купить", "цена"], text="используйте щётку для мытья"
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
