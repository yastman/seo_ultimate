"""Tests for extract_categories.py"""


class TestExtractCategories:
    """Test category extraction."""

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "extract_categories.py"
        assert script_path.exists()

    def test_regex_pattern_valid(self):
        """The regex pattern used in script should be valid."""
        import re

        # Pattern from the script
        pattern = r"\((\d+),1,'([^']*)'"
        test_line = "(123,1,'Test Category')"
        matches = re.findall(pattern, test_line)
        assert len(matches) == 1
        assert matches[0] == ("123", "Test Category")
