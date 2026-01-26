"""Tests for analyze_meta_keywords.py"""


class TestAnalyzeMetaKeywords:
    """Test meta keywords analysis."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.analyze_meta_keywords

        assert scripts.analyze_meta_keywords is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "analyze_meta_keywords.py"
        assert script_path.exists()
