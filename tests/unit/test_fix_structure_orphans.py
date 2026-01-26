"""Tests for fix_structure_orphans.py"""


class TestFixStructureOrphans:
    """Test structure orphans fixer."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.fix_structure_orphans

        assert scripts.fix_structure_orphans is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "fix_structure_orphans.py"
        assert script_path.exists()
