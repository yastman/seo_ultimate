"""Tests for match_uk_keywords_to_categories.py"""


class TestMatchUkKeywordsToCategories:
    """Test UK keywords to categories matching."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.match_uk_keywords_to_categories

        assert scripts.match_uk_keywords_to_categories is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "match_uk_keywords_to_categories.py"
        assert script_path.exists()
