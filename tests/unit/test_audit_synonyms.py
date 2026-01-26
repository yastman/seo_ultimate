"""Tests for audit_synonyms.py"""


class TestAuditSynonyms:
    """Test synonyms audit."""

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "audit_synonyms.py"
        assert script_path.exists()

    def test_script_has_main_function(self):
        """Script should have main function defined."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "audit_synonyms.py"
        content = script_path.read_text(encoding="utf-8")
        assert "def main(" in content
