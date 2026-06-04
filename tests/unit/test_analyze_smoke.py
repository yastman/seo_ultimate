"""Smoke tests for analyze package — issue #14 coverage."""


class TestAnalyzePackageImports:
    """All analyze submodules must be importable."""

    def test_analyze_importable(self):
        import llm_keywords_pipeline.analyze  # noqa: F401

    def test_duplicates_importable(self):
        from llm_keywords_pipeline.analyze import duplicates  # noqa: F401

    def test_order_importable(self):
        from llm_keywords_pipeline.analyze import order  # noqa: F401

    def test_synonyms_importable(self):
        from llm_keywords_pipeline.analyze import synonyms  # noqa: F401

    def test_meta_importable(self):
        from llm_keywords_pipeline.analyze import meta  # noqa: F401


class TestNormalizeKeyword:
    """analyze.duplicates.normalize_keyword must handle basic cases."""

    def test_lowercase(self):
        from llm_keywords_pipeline.analyze.duplicates import normalize_keyword
        assert normalize_keyword("Привет Мир") == "привет мир"

    def test_empty_string(self):
        from llm_keywords_pipeline.analyze.duplicates import normalize_keyword
        assert normalize_keyword("") == ""

    def test_returns_string(self):
        from llm_keywords_pipeline.analyze.duplicates import normalize_keyword
        result = normalize_keyword("  купить авто  ")
        assert isinstance(result, str)


class TestFindDuplicatesInKeywords:
    """find_duplicates_in_keywords must return a list."""

    def test_returns_list(self):
        from llm_keywords_pipeline.analyze.duplicates import find_duplicates_in_keywords
        kws = [{"keyword": "авто", "volume": 100}, {"keyword": "машина", "volume": 50}]
        result = find_duplicates_in_keywords(kws)
        assert isinstance(result, list)

    def test_empty_input(self):
        from llm_keywords_pipeline.analyze.duplicates import find_duplicates_in_keywords
        result = find_duplicates_in_keywords([])
        assert result == []
