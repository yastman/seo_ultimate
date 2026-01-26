"""Tests for verify_test_infra.py"""

from scripts.verify_test_infra import check_imports, check_structure


class TestCheckStructure:
    """Test structure checking."""

    def test_returns_bool(self):
        """Should return a boolean."""
        result = check_structure()
        assert isinstance(result, bool)

    def test_checks_required_paths(self, monkeypatch, capsys):
        """Should check for required paths."""
        # Mock os.path.exists to return False for everything
        monkeypatch.setattr("os.path.exists", lambda x: False)
        result = check_structure()
        assert result is False
        captured = capsys.readouterr()
        assert "Missing paths" in captured.out


class TestCheckImports:
    """Test import checking."""

    def test_returns_bool(self):
        """Should return a boolean."""
        result = check_imports()
        assert isinstance(result, bool)

    def test_pytest_available(self, capsys):
        """Pytest should be available in test environment."""
        result = check_imports()
        assert result is True
        captured = capsys.readouterr()
        assert "Pytest available" in captured.out
