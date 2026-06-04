"""TDD test: issue #1 — audit_category must handle UK _clean.json keyword formats.

The bug: TypeError when kw_data is a string instead of a dict.
This happens when keywords list contains plain strings (V1 UK format) or
when the load path passes strings through instead of {keyword: str, volume: int}.
Fix: normalize keywords to list[dict] before passing to audit_category.
"""
import pytest

from llm_keywords_pipeline.core.coverage import audit_category


SAMPLE_TEXT = "Привіт, це тестовий текст для перевірки покриття ключових слів у контенті."


class TestAuditCategoryUKFormats:
    """audit_category must not crash on any valid input format."""

    def test_flat_list_of_dicts(self):
        """Standard V3 format: list of {keyword, volume}."""
        keywords = [
            {"keyword": "тестовий текст", "volume": 100},
            {"keyword": "ключові слова", "volume": 50},
        ]
        result = audit_category(keywords, [], SAMPLE_TEXT, lang="uk")
        assert "total" in result
        assert result["total"] == 2

    def test_flat_list_of_strings(self):
        """V1 UK format: list of plain strings — must not raise TypeError."""
        keywords = ["тестовий текст", "ключові слова", "перевірка"]
        result = audit_category(keywords, [], SAMPLE_TEXT, lang="uk")
        assert "total" in result
        assert result["total"] == 3

    def test_empty_keywords(self):
        """Empty list must return 100% coverage (nothing to check)."""
        result = audit_category([], [], SAMPLE_TEXT, lang="uk")
        assert result["coverage_percent"] == 100.0
        assert result["total"] == 0

    def test_mixed_format_raises_or_normalizes(self):
        """Mixed list (dicts and strings) must not silently skip items."""
        keywords = [
            {"keyword": "тестовий текст", "volume": 100},
            "ключові слова",  # plain string
        ]
        # Should either normalize and process both, or raise a clear error
        try:
            result = audit_category(keywords, [], SAMPLE_TEXT, lang="uk")
            assert result["total"] == 2
        except TypeError as exc:
            pytest.fail(f"audit_category raised TypeError on mixed input: {exc}")

    def test_nested_dict_format(self):
        """V2 format passed as flat list after flattening: list of {keyword, volume}."""
        # This is what audit/coverage.py should produce after flattening V2 dict
        keywords = [
            {"keyword": "перевірка покриття", "volume": 200},
        ]
        result = audit_category(keywords, [], SAMPLE_TEXT, lang="uk")
        assert isinstance(result["results"], list)
        assert len(result["results"]) == 1
