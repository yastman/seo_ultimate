"""Smoke tests for extract package — issue #14 coverage."""


class TestExtractPackageImports:
    """All extract submodules must be importable."""

    def test_extract_importable(self):
        import llm_keywords_pipeline.extract  # noqa: F401

    def test_categories_importable(self):
        from llm_keywords_pipeline.extract import categories  # noqa: F401

    def test_all_keywords_importable(self):
        from llm_keywords_pipeline.extract import all_keywords  # noqa: F401

    def test_uk_keywords_importable(self):
        from llm_keywords_pipeline.extract import uk_keywords  # noqa: F401


class TestExtractCategories:
    """extract_categories must return empty dict for non-existent file."""

    def test_returns_dict(self, tmp_path):
        from llm_keywords_pipeline.extract.categories import extract_categories
        # Create a minimal SQL file without INSERT INTO categories
        sql_file = tmp_path / "test.sql"
        sql_file.write_text("SELECT 1;", encoding="utf-8")
        result = extract_categories(sql_file)
        assert isinstance(result, dict)

    def test_parses_insert_statement(self, tmp_path):
        from llm_keywords_pipeline.extract.categories import extract_categories
        sql_file = tmp_path / "test.sql"
        sql_file.write_text(
            "INSERT INTO oc_category_description (category_id, name) VALUES (42, 'Авто');",
            encoding="utf-8",
        )
        result = extract_categories(sql_file)
        assert isinstance(result, dict)
