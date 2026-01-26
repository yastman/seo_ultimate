"""Tests for gen_map.py"""

import re


class TestGenMap:
    """Test map generation."""

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "gen_map.py"
        assert script_path.exists()

    def test_find_id_pattern(self):
        """The regex pattern should find category ID by name."""
        name = "Автохимия"
        safe_name = re.escape(name)
        pattern = r"\((\d+),1,'" + safe_name + r"'"
        content = "(123,1,'Автохимия','description'),(456,1,'Детейлинг','desc')"
        match = re.search(pattern, content, re.IGNORECASE)
        assert match is not None
        assert match.group(1) == "123"

    def test_find_id_pattern_not_found(self):
        """Should return None when name not found."""
        name = "НесуществующаяКатегория"
        safe_name = re.escape(name)
        pattern = r"\((\d+),1,'" + safe_name + r"'"
        content = "(123,1,'Автохимия','description')"
        match = re.search(pattern, content, re.IGNORECASE)
        assert match is None

    def test_regex_escapes_special_chars(self):
        """Should properly escape special regex characters in name."""
        name = "Тест (с скобками)"
        safe_name = re.escape(name)
        pattern = r"\((\d+),1,'" + safe_name + r"'"
        content = "(789,1,'Тест (с скобками)','desc')"
        match = re.search(pattern, content, re.IGNORECASE)
        assert match is not None
        assert match.group(1) == "789"
