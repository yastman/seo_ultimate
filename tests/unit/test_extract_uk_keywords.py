"""Tests for extract_uk_keywords.py"""


class TestExtractUkKeywords:
    """Test UK keywords extraction."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.extract_uk_keywords

        assert scripts.extract_uk_keywords is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "extract_uk_keywords.py"
        assert script_path.exists()
