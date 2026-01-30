#!/usr/bin/env python3
"""Tests for validate_seo.py UK language support."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validate_seo import (
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
        assert detect_language("/home/user/project/uk/categories/test/file.md") == "uk"

    def test_default_to_ru(self):
        """Unknown path defaults to RU."""
        assert detect_language("some/random/path/file.md") == "ru"


class TestWordStems:
    """Tests for word stemming functions (Snowball stemmer by default)."""

    def test_russian_stems_filters_short_words(self):
        """Words <= 2 chars are filtered out."""
        stems = get_russian_word_stems("на для авто")
        # "на" (2 chars) filtered, "для" (3 chars) kept, "авто" stemmed
        assert len(stems) == 2
        assert "для" in stems
        assert "авт" in stems  # Snowball stem

    def test_russian_stems_returns_stemmed_form(self):
        """Russian words returned as stems (Snowball)."""
        stems = get_russian_word_stems("активная пена")
        assert "активн" in stems  # Snowball stem
        assert "пен" in stems  # Snowball stem

    def test_ukrainian_stems_filters_short_words(self):
        """Words <= 2 chars are filtered out."""
        stems = get_ukrainian_word_stems("на для авто")
        assert len(stems) == 2
        assert "для" in stems
        assert "авт" in stems  # Snowball stem

    def test_ukrainian_stems_returns_stemmed_form(self):
        """Ukrainian words returned as stems (Snowball)."""
        stems = get_ukrainian_word_stems("активна піна")
        assert "активн" in stems  # Snowball stem
        assert "піна" in stems  # Ukrainian Snowball keeps short words

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

    def test_uk_h2_with_partial_match(self):
        """UK H2 matches keyword via stems."""
        from validate_seo import check_keywords_in_h2

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
        # Keyword "активна піна" → stems ["активн", "піна"] (Snowball)
        # H2 2: "Активна піна:" — exact match found
        # Function requires min 2 H2s with keyword for passed=True
        result = check_keywords_in_h2(text, "активна піна", lang="uk")
        assert result["with_keyword"] >= 1
        assert result["total_h2"] == 4
        # Note: passed may be False if with_keyword < min_required

    def test_ru_h2_backward_compatible(self):
        """RU H2 matching still works."""
        from validate_seo import check_keywords_in_h2

        text = """# Title

## Как выбрать активную пену для мойки авто

Some text.

## FAQ

Questions.
"""
        result = check_keywords_in_h2(text, "активная пена", lang="ru")
        assert result["with_keyword"] >= 1
