"""Tests for cleanup_misplaced.py"""


class TestCleanupMisplaced:
    """Test misplaced files cleanup."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.cleanup_misplaced

        assert scripts.cleanup_misplaced is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "cleanup_misplaced.py"
        assert script_path.exists()
