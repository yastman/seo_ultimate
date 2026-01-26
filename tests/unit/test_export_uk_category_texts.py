"""Tests for export_uk_category_texts.py"""


class TestExportUkCategoryTexts:
    """Test UK category texts export."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.export_uk_category_texts

        assert scripts.export_uk_category_texts is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "export_uk_category_texts.py"
        assert script_path.exists()
