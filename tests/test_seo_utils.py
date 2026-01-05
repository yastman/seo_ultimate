import pytest

from scripts.seo_utils import clean_markdown, normalize_text, slugify


class TestSlugify:
    """Tests for slugify function."""

    def test_basic_cyrillic(self):
        assert slugify("Активная пена") == "aktivnaya-pena"

    def test_ukrainian_letters(self):
        assert slugify("Очищувач скла") == "ochishchuvach-skla"

    def test_special_chars_removal(self):
        assert slugify("Товар №1 (новый)") == "tovar-1-novyy"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_only_spaces(self):
        assert slugify("   ") == ""

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("Купить воск", "kupit-vosk"),
            ("L'oreal Paris", "l-oreal-paris"),
            ("100% результат", "100-rezultat"),
            ("Киев/Украина", "kiev-ukraina"),
        ],
    )
    def test_edge_cases(self, input_text, expected):
        assert slugify(input_text) == expected


class TestCleanMarkdown:
    """Tests for clean_markdown function."""

    def test_remove_headers(self):
        # clean_markdown replaces newlines with spaces
        assert clean_markdown("# Title\nText") == "Title Text"
        # Note: current implementation might keep text but remove marker, or keep logic.
        # Let's verify actual behavior through tests.
        # Looking at previous view_file of seo_utils, clean_markdown removes markers.

    def test_remove_bold_italic(self):
        text = "Some **bold** and *italic* text"
        # The regex in clean_markdown usually handles simple cases
        # We'll assert based on typical implementation
        cleaned = clean_markdown(text)
        assert "**" not in cleaned
        assert "*" not in cleaned

    def test_remove_links(self):
        text = "[Link](http://example.com)"
        assert "http" not in clean_markdown(text)

    def test_empty(self):
        assert clean_markdown("") == ""


class TestNormalizeText:
    def test_lowercase_preserved(self):
        # normalize_text does NOT lowercase by default
        assert normalize_text("TeSt") == "TeSt"

    def test_strip(self):
        assert normalize_text("  test  ") == "test"
