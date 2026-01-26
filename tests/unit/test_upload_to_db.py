"""Tests for upload_to_db.py"""

from unittest.mock import MagicMock, patch

from scripts.upload_to_db import (
    convert_lists,
    convert_tables,
    md_to_html,
    update_database,
    wrap_paragraphs,
)


class TestMdToHtmlUpload:
    """Test md_to_html from upload_to_db module."""

    def test_removes_h1(self):
        """H1 should be removed from output."""
        md = "# Заголовок\n\nТекст"
        html = md_to_html(md)
        assert "# Заголовок" not in html

    def test_converts_h2(self):
        """H2 should be converted."""
        md = "## Секция"
        html = md_to_html(md)
        assert "<h2>Секция</h2>" in html

    def test_converts_bold(self):
        """Bold should be converted."""
        md = "**жирный**"
        html = md_to_html(md)
        assert "<strong>жирный</strong>" in html


class TestConvertTablesUpload:
    """Test table conversion."""

    def test_simple_table(self):
        """Simple table should convert."""
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = convert_tables(md)
        assert "<table" in html
        assert "border=" in html


class TestConvertListsUpload:
    """Test list conversion."""

    def test_unordered_list(self):
        """Unordered list should convert."""
        md = "- item 1\n- item 2"
        html = convert_lists(md)
        assert "<ul>" in html
        assert "<li>item 1</li>" in html


class TestWrapParagraphs:
    """Test paragraph wrapping."""

    def test_wraps_text_in_p(self):
        """Plain text should be wrapped in <p>."""
        text = "Простой текст"
        html = wrap_paragraphs(text)
        assert "<p>" in html
        assert "Простой текст" in html

    def test_skips_headings(self):
        """Headings should not be wrapped."""
        text = "<h2>Заголовок</h2>"
        html = wrap_paragraphs(text)
        assert "<p><h2>" not in html


class TestUpdateDatabase:
    """Test database update with mocks."""

    def test_dry_run_does_not_connect(self, capsys):
        """Dry run should print but not connect."""
        data = {
            "slug": "test",
            "category_id": 1,
            "language_id": 3,
            "description": "<p>Test</p>",
            "meta_title": "Title",
            "meta_description": "Desc",
            "meta_h1": "H1",
        }
        update_database(data, dry_run=True)
        captured = capsys.readouterr()
        assert "[DRY RUN]" in captured.out

    @patch("scripts.upload_to_db.mysql.connector.connect")
    def test_connects_to_database(self, mock_connect):
        """Should connect and execute query."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        data = {
            "slug": "test",
            "category_id": 1,
            "language_id": 3,
            "description": "<p>Test</p>",
            "meta_title": "Title",
            "meta_description": "Desc",
            "meta_h1": "H1",
        }
        update_database(data, dry_run=False)

        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
