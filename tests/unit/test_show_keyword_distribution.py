"""Tests for show_keyword_distribution.py"""


class TestShowKeywordDistribution:
    """Test keyword distribution display."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.show_keyword_distribution

        assert scripts.show_keyword_distribution is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "show_keyword_distribution.py"
        assert script_path.exists()
