#!/usr/bin/env python3
"""Tests for check_seo_structure.py UK language support."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_seo_structure import (
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
    """Tests for stemming functions."""

    def test_russian_stems_short_words(self):
        """Short Russian words unchanged."""
        stems = get_russian_word_stems("для авто")
        assert "для" in stems
        assert "авт" in stems

    def test_russian_stems_long_words(self):
        """Long Russian words stemmed by 2 chars."""
        stems = get_russian_word_stems("активная пена")
        assert "активн" in stems
        assert "пен" in stems

    def test_ukrainian_stems_short_words(self):
        """Short Ukrainian words unchanged."""
        stems = get_ukrainian_word_stems("для авто")
        assert "для" in stems
        assert "авт" in stems

    def test_ukrainian_stems_long_words(self):
        """Long Ukrainian words stemmed by 2 chars."""
        stems = get_ukrainian_word_stems("активна піна")
        # "активна" (7 chars) → "актив" (7-2=5)
        # "піна" (4 chars) → "пін" (4-1=3)
        assert "актив" in stems
        assert "пін" in stems

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
        from check_seo_structure import check_keywords_in_h2

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
        # Keyword "активна піна" → stems ["актив", "пін"]
        # H2 1: "активну піну" contains "актив" and "пін" ✓
        # H2 2: "Активна піна" contains "актив" and "пін" ✓
        # H2 3: "піна" contains "пін" but not "актив" — partial match via word "піна"
        result = check_keywords_in_h2(text, "активна піна", lang="uk")
        assert result["with_keyword"] >= 2
        assert result["passed"] is True

    def test_ru_h2_backward_compatible(self):
        """RU H2 matching still works."""
        from check_seo_structure import check_keywords_in_h2

        text = """# Title

## Как выбрать активную пену для мойки авто

Some text.

## FAQ

Questions.
"""
        result = check_keywords_in_h2(text, "активная пена", lang="ru")
        assert result["with_keyword"] >= 1
