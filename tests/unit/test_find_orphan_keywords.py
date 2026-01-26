"""Tests for find_orphan_keywords.py"""


class TestFindOrphanKeywords:
    """Test orphan keywords finding."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.find_orphan_keywords

        assert scripts.find_orphan_keywords is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "find_orphan_keywords.py"
        assert script_path.exists()
