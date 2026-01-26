"""Tests for md_to_html.py"""

from scripts.md_to_html import convert_lists, convert_tables, md_to_html


class TestMdToHtml:
    """Test md_to_html main function."""

    def test_removes_h1_from_output(self):
        """H1 should be removed (goes to meta_h1)."""
        md = "# Заголовок H1\n\n## Заголовок H2\n\nТекст."
        html = md_to_html(md)
        assert "<h1>" not in html
        assert "Заголовок H1" not in html

    def test_converts_h2_to_html(self):
        """## should become <h2>."""
        md = "## Заголовок"
        html = md_to_html(md)
        assert "<h2>Заголовок</h2>" in html

    def test_converts_h3_to_html(self):
        """### should become <h3>."""
        md = "### Подзаголовок"
        html = md_to_html(md)
        assert "<h3>Подзаголовок</h3>" in html

    def test_converts_bold_to_strong(self):
        """**text** should become <strong>."""
        md = "**жирный текст**"
        html = md_to_html(md)
        assert "<strong>жирный текст</strong>" in html

    def test_handles_empty_input(self):
        """Empty input should return empty string."""
        assert md_to_html("") == ""

    def test_handles_cyrillic_text(self):
        """Cyrillic text should be preserved."""
        md = "## Кириллица\n\nТекст на русском."
        html = md_to_html(md)
        assert "Кириллица" in html
        assert "русском" in html


class TestConvertTables:
    """Test table conversion."""

    def test_converts_simple_table(self):
        """Simple markdown table should become HTML table."""
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = convert_tables(md)
        assert "<table" in html
        assert "<th>" in html or "<td>" in html

    def test_preserves_cyrillic_in_table(self):
        """Cyrillic in table cells should be preserved."""
        md = "| Колонка |\n|---|\n| Значение |"
        html = convert_tables(md)
        assert "Колонка" in html
        assert "Значение" in html

    def test_handles_empty_table(self):
        """Empty or malformed table should not crash."""
        md = "| |\n|---|"
        html = convert_tables(md)
        assert html is not None


class TestConvertLists:
    """Test list conversion."""

    def test_converts_unordered_list(self):
        """- items should become <ul><li>."""
        md = "- item 1\n- item 2"
        html = convert_lists(md)
        assert "<ul>" in html
        assert "<li>item 1</li>" in html
        assert "</ul>" in html

    def test_handles_nested_content(self):
        """List followed by text should close properly."""
        md = "- item\n\nПараграф"
        html = convert_lists(md)
        assert "</ul>" in html
