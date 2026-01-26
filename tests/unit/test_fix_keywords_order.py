"""Tests for fix_keywords_order.py"""


class TestFixKeywordsOrder:
    """Test keywords order fixer."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.fix_keywords_order

        assert scripts.fix_keywords_order is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "fix_keywords_order.py"
        assert script_path.exists()
