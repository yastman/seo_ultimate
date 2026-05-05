"""Tests for audit/coverage.py"""

import pytest

from llm_keywords_pipeline.audit.coverage import (
    audit_category_coverage,
    find_category_path,
    get_all_slugs,
)


class TestFindCategoryPath:
    """Tests for find_category_path function."""

    def test_find_uk_category_returns_path_if_exists(self):
        """UK category path should be found if exists."""
        # This test will pass if any UK category exists
        slugs = get_all_slugs("uk")
        if slugs:
            path = find_category_path(slugs[0], "uk")
            assert path is not None
            assert path.exists()

    def test_find_nonexistent_category_returns_none(self):
        """Non-existent category should return None."""
        path = find_category_path("nonexistent-category-xyz", "uk")
        assert path is None


class TestGetAllSlugs:
    """Tests for get_all_slugs function."""

    def test_get_all_uk_slugs_returns_list(self):
        """Should return a list of slugs."""
        slugs = get_all_slugs("uk")
        assert isinstance(slugs, list)

    def test_get_all_ru_slugs_returns_list(self):
        """Should return a list of slugs."""
        slugs = get_all_slugs("ru")
        assert isinstance(slugs, list)


class TestAuditCategoryCoverage:
    """Tests for audit_category_coverage function."""

    def test_audit_returns_coverage_percent(self):
        """Audit should return coverage_percent key."""
        # Use any existing category
        slugs = get_all_slugs("uk")
        if not slugs:
            pytest.skip("No UK categories found")

        result = audit_category_coverage(slugs[0], lang="uk")
        assert "coverage_percent" in result
        assert isinstance(result["coverage_percent"], (int, float))

    def test_audit_nonexistent_returns_error(self):
        """Audit of non-existent category should return error."""
        result = audit_category_coverage("nonexistent-xyz", lang="uk")
        assert "error" in result or result.get("coverage_percent") == 0
