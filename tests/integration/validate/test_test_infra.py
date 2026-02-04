"""Integration tests for seo_ultimate.validate.test_infra module."""


class TestCheckStructure:
    """Tests for check_structure function."""

    def test_returns_bool(self):
        """Function should return a bool indicating structure is valid."""
        from seo_ultimate.validate.test_infra import check_structure

        result = check_structure()

        assert isinstance(result, bool)


class TestCheckImports:
    """Tests for check_imports function."""

    def test_returns_bool(self):
        """Function should return a bool indicating imports are valid."""
        from seo_ultimate.validate.test_infra import check_imports

        result = check_imports()

        assert isinstance(result, bool)
