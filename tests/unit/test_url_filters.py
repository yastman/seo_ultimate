"""Tests for url_filters.py"""


class TestUrlFilters:
    """Test URL filters."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.url_filters

        assert scripts.url_filters is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "url_filters.py"
        assert script_path.exists()
