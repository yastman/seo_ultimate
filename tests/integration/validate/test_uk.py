"""Integration tests for seo_ultimate.validate.uk module."""


class TestValidateUkCategory:
    """Tests for validate_uk_category function."""

    def test_nonexistent_category_fails(self, capsys):
        """Non-existent category should return failure exit code."""
        from seo_ultimate.validate.uk import validate_uk_category

        # Returns int exit code (2 = fail)
        result = validate_uk_category("nonexistent-category-12345")

        assert isinstance(result, int)
        assert result == 2  # FAIL exit code

    def test_returns_exit_code(self, capsys):
        """Function should return an exit code integer."""
        from seo_ultimate.validate.uk import validate_uk_category

        result = validate_uk_category("test-slug-that-does-not-exist")

        assert isinstance(result, int)
        assert result in [0, 1, 2]  # PASS, WARN, FAIL
