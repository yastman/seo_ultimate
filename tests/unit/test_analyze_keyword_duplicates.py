"""Tests for analyze_keyword_duplicates.py"""


class TestAnalyzeKeywordDuplicates:
    """Test keyword duplicates analysis."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.analyze_keyword_duplicates

        assert scripts.analyze_keyword_duplicates is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "analyze_keyword_duplicates.py"
        assert script_path.exists()
