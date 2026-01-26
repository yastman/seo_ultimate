"""Tests for match_cats.py"""


class TestMatchCats:
    """Test category matching."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.match_cats

        assert scripts.match_cats is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "match_cats.py"
        assert script_path.exists()
