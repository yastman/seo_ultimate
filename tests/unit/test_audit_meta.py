"""Tests for audit_meta.py"""


class TestAuditMeta:
    """Test meta audit."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.audit_meta

        assert scripts.audit_meta is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "audit_meta.py"
        assert script_path.exists()
