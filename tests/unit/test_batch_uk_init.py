"""Tests for batch_uk_init.py"""


class TestBatchUkInit:
    """Test batch UK initialization."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.batch_uk_init

        assert scripts.batch_uk_init is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "batch_uk_init.py"
        assert script_path.exists()
