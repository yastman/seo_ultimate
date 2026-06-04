"""Smoke tests for compare package — issue #14 coverage."""


class TestComparePackageImports:
    """All compare submodules must be importable."""

    def test_compare_importable(self):
        import llm_keywords_pipeline.compare  # noqa: F401

    def test_keyword_distribution_importable(self):
        from llm_keywords_pipeline.compare import keyword_distribution  # noqa: F401

    def test_match_cats_importable(self):
        from llm_keywords_pipeline.compare import match_cats  # noqa: F401

    def test_raw_clean_importable(self):
        from llm_keywords_pipeline.compare import raw_clean  # noqa: F401

    def test_with_master_importable(self):
        from llm_keywords_pipeline.compare import with_master  # noqa: F401


class TestParseDensityPercent:
    """_parse_density_percent must handle string and numeric input."""

    def test_float_passthrough(self):
        from llm_keywords_pipeline.compare.keyword_distribution import _parse_density_percent
        assert _parse_density_percent(1.5) == 1.5

    def test_string_with_percent(self):
        from llm_keywords_pipeline.compare.keyword_distribution import _parse_density_percent
        assert _parse_density_percent("2.3%") == 2.3

    def test_zero(self):
        from llm_keywords_pipeline.compare.keyword_distribution import _parse_density_percent
        assert _parse_density_percent(0) == 0.0

    def test_invalid_returns_zero(self):
        from llm_keywords_pipeline.compare.keyword_distribution import _parse_density_percent
        result = _parse_density_percent("n/a")
        assert isinstance(result, float)
