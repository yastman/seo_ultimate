#!/usr/bin/env python3
"""
Unit tests for check_water_natasha.py calculations.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest


# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_water_natasha import (
    calculate_metrics,
    calculate_metrics_from_text,
    clean_markdown,
    load_stopwords,
)


class TestLoadStopwords:
    def test_load_stopwords_file_exists(self):
        """Should load from file if it exists."""
        mock_content = "слово1\nслово2\n"
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=mock_content)),
        ):
            stopwords = load_stopwords()
            assert "слово1" in stopwords
            assert "слово2" in stopwords

    def test_load_stopwords_fallback_library(self):
        """Should fallback to stop_words library if file missing."""
        # Mock stop_words module
        mock_stop_words = MagicMock()
        mock_stop_words.get_stop_words.return_value = ["lib_word"]

        with (
            patch("pathlib.Path.exists", return_value=False),
            patch.dict(sys.modules, {"stop_words": mock_stop_words}),
        ):
            # We need to reload or re-import if we want to trigger the import inside the function
            # But the function does 'from stop_words import get_stop_words'
            # mocking sys.modules should work if it hasn't been imported yet,
            # OR we patch the function logic.

            # Since load_stopwords handles the import internally:
            stopwords = load_stopwords()
            assert "lib_word" in stopwords

    def test_load_stopwords_fallback_hardcoded(self):
        """Should fallback to hardcoded set if everything fails."""
        with (
            patch("pathlib.Path.exists", return_value=False),
            patch.dict(sys.modules, {"stop_words": None}),
        ):
            stopwords = load_stopwords()
            assert "и" in stopwords
            assert len(stopwords) > 10


class TestCleanMarkdown:
    def test_clean_markdown_removes_bold(self):
        text = "This is **bold** text"
        cleaned = clean_markdown(text)
        assert "bold" in cleaned
        assert "**" not in cleaned

    def test_clean_markdown_removes_links(self):
        text = "[Link text](http://url.com)"
        cleaned = clean_markdown(text)
        assert "Link text" in cleaned
        assert "http" not in cleaned
        assert "]" not in cleaned

    def test_clean_markdown_removes_code_blocks(self):
        text = "Text\n```\ncode\n```\nMore text"
        cleaned = clean_markdown(text)
        assert "Text" in cleaned
        assert "More text" in cleaned
        assert "code" not in cleaned.split()


class TestCalculateMetrics:
    @pytest.fixture(autouse=True)
    def mock_stopwords(self):
        """Mock load_stopwords to a known set for calculation tests."""
        known_stopwords = {"и", "в", "на", "stopword"}
        with patch("check_water_natasha.load_stopwords", return_value=known_stopwords):
            yield

    def test_calculate_metrics_empty_text(self):
        metrics = calculate_metrics_from_text("")
        assert metrics is None

    def test_calculate_metrics_no_russian(self):
        metrics = calculate_metrics_from_text("Hello world 123")
        assert metrics is None

    def test_calculate_metrics_simple_text(self):
        text = "Мама мыла раму."
        metrics = calculate_metrics_from_text(text)

        assert metrics is not None
        assert metrics["total_words"] == 3
        assert "water_percent" in metrics

    def test_calculate_metrics_water_calculation(self):
        # "и" is a stopword (mocked). "стол", "стул" are not.
        text = "стол и стул"

        metrics = calculate_metrics_from_text(text)
        assert metrics["total_words"] == 3
        assert metrics["water_count"] == 1
        # 1/3 = 33.3%
        assert 33.0 < metrics["water_percent_raw"] < 33.4

    def test_calculate_metrics_nausea_calculation(self):
        # "тест тест тест тест"
        text = "тест тест тест тест"
        metrics = calculate_metrics_from_text(text)

        # Max freq = 4
        # Classic nausea = sqrt(4) = 2.0
        assert metrics["max_frequency"] == 4
        assert metrics["classic_nausea"] == 2.0

    def test_calculate_metrics_academic_nausea(self):
        # "тест тест слово"
        # Mock stopwords: 'и', 'в', 'на', 'stopword'
        # 'тест' (2) -> count > 1 -> included.
        # 'слово' (1) -> count <= 1 -> excluded by code logic (academic nausea filter).
        # Total significant = 2.
        # Academic nausea = (2 / 2) * 100 = 100%

        text = "тест тест слово"
        metrics = calculate_metrics_from_text(text)

        assert metrics["total_significant"] == 2
        assert metrics["max_freq_significant"] == 2
        assert 99.0 < metrics["academic_nausea"] < 101.0

    def test_calculate_metrics_academic_nausea_no_repeats(self):
        text = "раз два три"
        metrics = calculate_metrics_from_text(text)
        assert metrics["academic_nausea"] == 0.0


def test_calculate_metrics_reads_file(tmp_path: Path):
    fp = tmp_path / "t.md"
    fp.write_text("Мама мыла раму.", encoding="utf-8")
    metrics = calculate_metrics(str(fp))
    assert metrics is not None
