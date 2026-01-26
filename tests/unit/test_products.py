"""Tests for products.py"""


class TestProducts:
    """Test products handling."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.products

        assert scripts.products is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "products.py"
        assert script_path.exists()
