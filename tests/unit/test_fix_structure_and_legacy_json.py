"""Tests for fix_structure_and_legacy_json.py"""


class TestFixStructureAndLegacyJson:
    """Test structure and legacy JSON fixer."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.fix_structure_and_legacy_json

        assert scripts.fix_structure_and_legacy_json is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "fix_structure_and_legacy_json.py"
        assert script_path.exists()
