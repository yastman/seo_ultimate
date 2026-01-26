"""Tests for compare_raw_clean.py"""


class TestCompareRawClean:
    """Test raw vs clean comparison."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.compare_raw_clean

        assert scripts.compare_raw_clean is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "compare_raw_clean.py"
        assert script_path.exists()
