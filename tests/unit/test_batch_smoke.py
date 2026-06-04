"""Smoke tests for batch package — issue #14 coverage."""


class TestBatchPackageImports:
    """All batch submodules must be importable."""

    def test_batch_importable(self):
        import llm_keywords_pipeline.batch  # noqa: F401

    def test_generate_importable(self):
        from llm_keywords_pipeline.batch import generate  # noqa: F401

    def test_uk_init_importable(self):
        from llm_keywords_pipeline.batch import uk_init  # noqa: F401


class TestGetCategoryStatus:
    """batch.generate.get_category_status must return a status dict."""

    def test_unknown_slug_returns_dict(self):
        from llm_keywords_pipeline.batch.generate import get_category_status
        log = {}
        result = get_category_status("__nonexistent__", log)
        assert isinstance(result, dict)

    def test_returns_stage_or_status_key(self):
        from llm_keywords_pipeline.batch.generate import get_category_status
        log = {}
        result = get_category_status("__test__", log)
        # Function returns either 'status' or 'stage' key
        assert "stage" in result or "status" in result or "last_status" in result


class TestExtractIssuesFromValidation:
    """extract_issues_from_validation must return a list."""

    def test_empty_validation(self):
        from llm_keywords_pipeline.batch.generate import extract_issues_from_validation
        result = extract_issues_from_validation({})
        assert isinstance(result, list)

    def test_with_failed_checks(self):
        from llm_keywords_pipeline.batch.generate import extract_issues_from_validation
        validation = {
            "checks": {
                "water": {"passed": False, "message": "Water too high: 75%"},
                "density": {"passed": True},
            }
        }
        result = extract_issues_from_validation(validation)
        assert isinstance(result, list)
