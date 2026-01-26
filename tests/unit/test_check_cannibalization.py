"""Tests for check_cannibalization.py"""


class TestCheckCannibalization:
    """Test cannibalization checking."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.check_cannibalization

        assert scripts.check_cannibalization is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "check_cannibalization.py"
        assert script_path.exists()
