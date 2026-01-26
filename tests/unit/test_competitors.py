"""Tests for competitors.py"""


class TestCompetitors:
    """Test competitors analysis."""

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "competitors.py"
        assert script_path.exists()

    def test_script_has_main_function(self):
        """Script should have main function defined."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "competitors.py"
        content = script_path.read_text(encoding="utf-8")
        assert "def main(" in content or "if __name__" in content
