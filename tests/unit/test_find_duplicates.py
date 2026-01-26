"""Tests for find_duplicates.py"""


class TestFindDuplicates:
    """Test duplicates finding."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.find_duplicates

        assert scripts.find_duplicates is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "find_duplicates.py"
        assert script_path.exists()
