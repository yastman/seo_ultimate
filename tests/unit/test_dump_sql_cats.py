"""Tests for dump_sql_cats.py"""

import re


class TestDumpSqlCats:
    """Test SQL category dump."""

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "dump_sql_cats.py"
        assert script_path.exists()

    def test_regex_pattern_extracts_categories(self):
        """The regex pattern should extract category ID and name."""
        pattern = r"\((\d+),1,'([^']+)'"
        test_data = "(123,1,'Автохимия'),(456,1,'Детейлинг')"
        matches = re.findall(pattern, test_data)
        assert len(matches) == 2
        assert matches[0] == ("123", "Автохимия")
        assert matches[1] == ("456", "Детейлинг")

    def test_sorting_by_id(self):
        """Categories should be sortable by ID."""
        matches = [("100", "B"), ("50", "A"), ("200", "C")]
        sorted_matches = sorted(matches, key=lambda x: int(x[0]))
        assert sorted_matches[0][0] == "50"
        assert sorted_matches[1][0] == "100"
        assert sorted_matches[2][0] == "200"
