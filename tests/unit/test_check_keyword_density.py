"""Tests for check_keyword_density.py UK support."""

from scripts.check_keyword_density import (
    STOPWORDS_RU,
    STOPWORDS_UK,
    get_stemmer,
    get_stopwords,
    remove_stopwords,
)


class TestStopwords:
    """Tests for language-specific stopwords."""

    def test_get_stopwords_ru_default(self):
        """Default returns Russian stopwords."""
        result = get_stopwords()
        assert result is STOPWORDS_RU

    def test_get_stopwords_ru_explicit(self):
        """Explicit ru returns Russian stopwords."""
        result = get_stopwords("ru")
        assert result is STOPWORDS_RU

    def test_get_stopwords_uk(self):
        """uk returns Ukrainian stopwords."""
        result = get_stopwords("uk")
        assert result is STOPWORDS_UK

    def test_stopwords_ru_contains_common(self):
        """Russian stopwords contain common words."""
        assert "и" in STOPWORDS_RU
        assert "в" in STOPWORDS_RU
        assert "на" in STOPWORDS_RU
        assert "но" in STOPWORDS_RU

    def test_stopwords_uk_contains_common(self):
        """Ukrainian stopwords contain common words."""
        assert "і" in STOPWORDS_UK
        assert "в" in STOPWORDS_UK
        assert "на" in STOPWORDS_UK
        assert "але" in STOPWORDS_UK

    def test_stopwords_are_different(self):
        """RU and UK stopwords are different sets."""
        assert STOPWORDS_RU != STOPWORDS_UK
        # "но" is Russian, "але" is Ukrainian equivalent
        assert "но" in STOPWORDS_RU
        assert "но" not in STOPWORDS_UK
        assert "але" in STOPWORDS_UK
        assert "але" not in STOPWORDS_RU


class TestRemoveStopwords:
    """Tests for remove_stopwords with language support."""

    def test_remove_stopwords_ru_default(self):
        """Default removes Russian stopwords."""
        words = ["активная", "и", "пена", "для", "авто"]
        result = remove_stopwords(words)
        assert "и" not in result
        assert "для" not in result
        assert "активная" in result
        assert "пена" in result
        assert "авто" in result

    def test_remove_stopwords_uk(self):
        """UK removes Ukrainian stopwords."""
        words = ["активна", "і", "піна", "для", "авто"]
        result = remove_stopwords(words, "uk")
        assert "і" not in result
        assert "для" not in result
        assert "активна" in result
        assert "піна" in result
        assert "авто" in result

    def test_remove_stopwords_keeps_long_words(self):
        """Removes words with len <= 2."""
        words = ["авто", "в", "на", "шампунь"]
        result = remove_stopwords(words, "ru")
        assert "в" not in result
        assert "на" not in result
        assert "авто" in result
        assert "шампунь" in result


class TestStemmer:
    """Tests for language-specific stemmers."""

    def test_get_stemmer_ru_default(self):
        """Default returns Russian stemmer."""
        stemmer = get_stemmer()
        assert stemmer is not None
        # Test Russian word
        stem = stemmer.stemWord("полировальная")
        assert stem == "полировальн"

    def test_get_stemmer_uk(self):
        """UK returns stemmer (Russian fallback if Ukrainian unavailable)."""
        stemmer = get_stemmer("uk")
        assert stemmer is not None
        # Should work on similar Slavic words
        stem = stemmer.stemWord("полірувальна")
        assert len(stem) > 0

    def test_stemmers_are_same_or_different(self):
        """UK stemmer may be same as RU (fallback) or different."""
        ru_stemmer = get_stemmer("ru")
        uk_stemmer = get_stemmer("uk")
        # Both should exist and work
        assert ru_stemmer is not None
        assert uk_stemmer is not None
