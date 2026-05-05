"""Integration tests for llm_keywords_pipeline.validate.structural module."""


class TestCheckCategory:
    """Tests for check_category function."""

    def test_nonexistent_category(self):
        """Non-existent category should report missing status."""
        from llm_keywords_pipeline.validate.structural import check_category

        result = check_category("nonexistent-slug-12345")

        # Returns dict with status field
        assert "status" in result
        assert result["status"] == "MISSING_JSON"

    def test_returns_dict(self):
        """Function should return a dict."""
        from llm_keywords_pipeline.validate.structural import check_category

        result = check_category("test-slug")

        assert isinstance(result, dict)
        assert "slug" in result
