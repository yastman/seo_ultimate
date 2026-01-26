"""Tests for generate_sql.py"""

from scripts.generate_sql import (
    build_html_table,
    convert_lists,
    convert_tables,
    escape_sql,
    md_to_html,
)


class TestEscapeSql:
    """Test SQL escaping."""

    def test_escapes_single_quotes(self):
        """Single quotes should be escaped."""
        assert escape_sql("it's") == "it\\'s"

    def test_escapes_double_quotes(self):
        """Double quotes should be escaped."""
        assert escape_sql('say "hello"') == 'say \\"hello\\"'

    def test_escapes_backslashes(self):
        """Backslashes should be escaped."""
        assert escape_sql("path\\to") == "path\\\\to"

    def test_handles_empty_string(self):
        """Empty string should return empty."""
        assert escape_sql("") == ""

    def test_handles_cyrillic(self):
        """Cyrillic should be preserved."""
        assert escape_sql("Привет") == "Привет"

    def test_complex_escaping(self):
        """Multiple special chars in one string."""
        result = escape_sql('It\'s a "test" with \\ backslash')
        assert "\\'" in result
        assert '\\"' in result
        assert "\\\\" in result


class TestMdToHtmlGenerateSql:
    """Test md_to_html from generate_sql module."""

    def test_extracts_h1(self):
        """H1 should be extracted separately."""
        md = "# Заголовок\n\nТекст"
        h1, html = md_to_html(md)
        assert h1 == "Заголовок"
        assert "<h1>" not in html

    def test_returns_empty_h1_if_missing(self):
        """No H1 should return empty string."""
        md = "## H2 Only\n\nТекст"
        h1, html = md_to_html(md)
        assert h1 == ""

    def test_converts_body_to_html(self):
        """Body should be converted to HTML."""
        md = "# H1\n\n## H2\n\nПараграф"
        h1, html = md_to_html(md)
        assert "<h2>" in html or "H2" in html


class TestBuildHtmlTable:
    """Test HTML table building."""

    def test_builds_simple_table(self):
        """Should build valid HTML table."""
        lines = ["| A | B |", "|---|---|", "| 1 | 2 |"]
        html = build_html_table(lines)
        assert "<table>" in html
        assert "<th>" in html
        assert "<td>" in html
        assert "</table>" in html

    def test_returns_original_if_invalid(self):
        """Invalid table should return original lines."""
        lines = ["not a table"]
        result = build_html_table(lines)
        assert "not a table" in result


class TestConvertTables:
    """Test convert_tables function."""

    def test_converts_markdown_table(self):
        """Should convert Markdown table to HTML."""
        md = "| Header |\n|---|\n| Value |"
        html = convert_tables(md)
        assert "<table>" in html

    def test_preserves_non_table_content(self):
        """Non-table content should be preserved."""
        md = "Regular text\n\nMore text"
        result = convert_tables(md)
        assert "Regular text" in result
        assert "More text" in result


class TestConvertLists:
    """Test convert_lists function."""

    def test_converts_unordered_list(self):
        """- items should become <ul><li>."""
        md = "- item 1\n- item 2"
        html = convert_lists(md)
        assert "<ul>" in html
        assert "<li>item 1</li>" in html
        assert "</ul>" in html

    def test_converts_ordered_list(self):
        """1. items should become <ol><li>."""
        md = "1. first\n2. second"
        html = convert_lists(md)
        assert "<ol>" in html
        assert "<li>first</li>" in html
        assert "</ol>" in html

    def test_handles_mixed_lists(self):
        """Mixed lists should be handled."""
        md = "- bullet\n1. numbered"
        html = convert_lists(md)
        assert "<ul>" in html
        assert "<ol>" in html
