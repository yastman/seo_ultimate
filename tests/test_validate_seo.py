#!/usr/bin/env python3
"""Tests for validate_seo.py UK language support."""

from llm_keywords_pipeline.validate.seo import (
    detect_language,
    get_russian_word_stems,
    get_ukrainian_word_stems,
    get_word_stems,
)


class TestDetectLanguage:
    """Tests for detect_language function."""

    def test_uk_categories_path(self):
        """UK path detected correctly."""
        assert detect_language("uk/categories/aktivnaya-pena/content/file.md") == "uk"

    def test_uk_path_with_backslash(self):
        """Windows-style UK path detected correctly."""
        assert detect_language("uk\\categories\\aktivnaya-pena\\content\\file.md") == "uk"

    def test_ru_categories_path(self):
        """RU path detected correctly."""
        assert detect_language("categories/aktivnaya-pena/content/file.md") == "ru"

    def test_absolute_uk_path(self):
        """Absolute UK path detected correctly."""
        assert detect_language("/workspace/project/uk/categories/test/file.md") == "uk"

    def test_default_to_ru(self):
        """Unknown path defaults to RU."""
        assert detect_language("some/random/path/file.md") == "ru"


class TestWordStems:
    """Tests for word lemmatization functions (MorphAnalyzer-based)."""

    def test_russian_stems_filters_short_words(self):
        """Words <= 2 chars are filtered out."""
        stems = get_russian_word_stems("на для авто")
        # "на" (2 chars) filtered, "для" (3 chars) kept, "авто" stays as lemma
        assert len(stems) == 2
        assert "для" in stems
        assert "авто" in stems  # MorphAnalyzer lemma (not Snowball stem)

    def test_russian_stems_returns_normalized_form(self):
        """Russian words returned as normalised lemmas (MorphAnalyzer)."""
        stems = get_russian_word_stems("активная пена")
        assert "активный" in stems  # lemma of "активная"
        assert "пена" in stems

    def test_ukrainian_stems_filters_short_words(self):
        """Words <= 2 chars are filtered out."""
        stems = get_ukrainian_word_stems("на для авто")
        assert len(stems) == 2
        assert "для" in stems
        assert "авто" in stems  # MorphAnalyzer lemma

    def test_ukrainian_stems_returns_normalized_form(self):
        """Ukrainian words returned as normalised lemmas (MorphAnalyzer)."""
        stems = get_ukrainian_word_stems("активна піна")
        assert "активний" in stems  # lemma of "активна"
        assert "піна" in stems

    def test_get_word_stems_ru(self):
        """Wrapper returns RU stems for ru lang."""
        stems = get_word_stems("активная пена", "ru")
        assert stems == get_russian_word_stems("активная пена")

    def test_get_word_stems_uk(self):
        """Wrapper returns UK stems for uk lang."""
        stems = get_word_stems("активна піна", "uk")
        assert stems == get_ukrainian_word_stems("активна піна")


class TestH2KeywordMatching:
    """Tests for H2 keyword detection with language support."""

    def test_uk_h2_with_exact_match(self):
        """UK H2 matches keyword via exact match."""
        from llm_keywords_pipeline.validate.seo import check_keywords_in_h2

        text = """# Title

## Як обрати активну піну для безконтактної мийки

Some text here.

## Активна піна: поради щодо вибору

More text.

## Яка піна краще для автомобіля

Third section.

## FAQ

Questions.
"""
        # H2 "Активна піна:" contains the full keyword phrase → exact match
        result = check_keywords_in_h2(text, "активна піна", lang="uk")
        assert result["with_keyword"] >= 1
        assert result["total_h2"] == 4

    def test_ru_h2_with_partial_keyword_match(self):
        """RU H2 matches via partial word match (word > 4 chars as substring)."""
        from llm_keywords_pipeline.validate.seo import check_keywords_in_h2

        text = """# Title

## Как выбрать щетка для мойки авто

Some text.

## FAQ

Questions.
"""
        # Keyword "щетка" has 6 chars (> 4 threshold) — partial match works
        # only when the keyword word appears as an exact substring in the H2
        result = check_keywords_in_h2(text, "щетка для авто", lang="ru")
        assert result["with_keyword"] >= 1
