# tests/smoke/test_text_utils_smoke.py
"""Smoke tests for text_utils on real category data."""

from pathlib import Path

import pytest

# Real data paths (using actual hierarchy)
PROJECT_ROOT = Path(__file__).parent.parent.parent


def find_ru_content(slug: str) -> Path | None:
    """Find RU content file recursively in categories."""
    for p in PROJECT_ROOT.glob(f"categories/**/{slug}/content/{slug}_ru.md"):
        return p
    return None


def find_uk_content(slug: str) -> Path | None:
    """Find UK content file in uk/categories."""
    path = PROJECT_ROOT / "uk" / "categories" / slug / "content" / f"{slug}_uk.md"
    return path if path.exists() else None


class TestTextUtilsSmoke:
    """Smoke tests using real category content."""

    @pytest.fixture
    def real_ru_content(self):
        """Load real RU content file."""
        path = find_ru_content("aktivnaya-pena")
        if path is None or not path.exists():
            pytest.skip("Real RU data not available")
        return path.read_text(encoding="utf-8")

    @pytest.fixture
    def real_uk_content(self):
        """Load real UK content file."""
        path = find_uk_content("aktivnaya-pena")
        if path is None or not path.exists():
            pytest.skip("Real UK data not available")
        return path.read_text(encoding="utf-8")

    def test_clean_markdown_on_real_ru_content(self, real_ru_content):
        """clean_markdown works on real RU content."""
        from scripts.text_utils import clean_markdown

        result = clean_markdown(real_ru_content)

        # Should produce non-empty text
        assert len(result) > 100
        # Should remove markdown markers
        assert "##" not in result
        assert "**" not in result
        # Should preserve content words
        assert "пен" in result.lower() or "активн" in result.lower()

    def test_clean_markdown_on_real_uk_content(self, real_uk_content):
        """clean_markdown works on real UK content."""
        from scripts.text_utils import clean_markdown

        result = clean_markdown(real_uk_content)

        assert len(result) > 100
        assert "##" not in result
        assert "піна" in result.lower() or "активн" in result.lower()

    def test_extract_h1_on_real_content(self, real_ru_content):
        """extract_h1 finds H1 in real content."""
        from scripts.text_utils import extract_h1

        h1 = extract_h1(real_ru_content)

        assert h1 is not None
        assert len(h1) > 5
        # H1 should contain main keyword
        assert "пен" in h1.lower() or "активн" in h1.lower()

    def test_extract_h2s_on_real_content(self, real_ru_content):
        """extract_h2s finds H2s in real content."""
        from scripts.text_utils import extract_h2s

        h2s = extract_h2s(real_ru_content)

        # Content should have multiple H2s
        assert len(h2s) >= 2
        # H2s should be meaningful text (>= 3 chars, e.g. "FAQ")
        for h2 in h2s:
            assert len(h2) >= 3

    def test_extract_intro_on_real_content(self, real_ru_content):
        """extract_intro finds intro in real content."""
        from scripts.text_utils import extract_intro

        intro = extract_intro(real_ru_content)

        assert len(intro) > 50
        # Intro should contain keyword
        assert "пен" in intro.lower() or "активн" in intro.lower()

    def test_tokenize_ru_on_real_content(self, real_ru_content):
        """tokenize produces tokens from real RU content."""
        from scripts.text_utils import clean_markdown, tokenize

        clean = clean_markdown(real_ru_content)
        tokens = tokenize(clean, lang="ru", remove_stopwords=True)

        # Should have meaningful tokens
        assert len(tokens) > 50
        # Should not contain stopwords
        assert "и" not in tokens
        assert "в" not in tokens
        # Should contain content words
        assert any("пен" in t for t in tokens) or any("активн" in t for t in tokens)

    def test_tokenize_uk_on_real_content(self, real_uk_content):
        """tokenize produces tokens from real UK content."""
        from scripts.text_utils import clean_markdown, tokenize

        clean = clean_markdown(real_uk_content)
        tokens = tokenize(clean, lang="uk", remove_stopwords=True)

        assert len(tokens) > 50
        # Should not contain UK stopwords
        assert "і" not in tokens
        assert "та" not in tokens

    def test_count_words_on_real_content(self, real_ru_content):
        """count_words returns reasonable count for real content."""
        from scripts.text_utils import clean_markdown, count_words

        clean = clean_markdown(real_ru_content)
        words = count_words(clean)

        # Real content should have substantial word count
        assert words >= 150
        assert words <= 5000  # Not unreasonably large

    def test_stopwords_ru_coverage(self):
        """RU stopwords set has adequate coverage."""
        from scripts.text_utils import get_stopwords

        stopwords = get_stopwords("ru")
        assert len(stopwords) >= 50
        # Common Russian stopwords
        assert "и" in stopwords
        assert "в" in stopwords
        assert "для" in stopwords

    def test_stopwords_uk_coverage(self):
        """UK stopwords set has adequate coverage."""
        from scripts.text_utils import get_stopwords

        stopwords = get_stopwords("uk")
        assert len(stopwords) >= 50
        # Common Ukrainian stopwords
        assert "і" in stopwords
        assert "та" in stopwords
        assert "для" in stopwords
