"""Integration tests for llm_keywords_pipeline.validate.seo module."""


class TestCheckSeoStructure:
    """Tests for check_seo_structure function."""

    def test_keyword_in_intro_passes(self, tmp_path):
        """Content with keyword in intro should pass intro check."""
        from llm_keywords_pipeline.validate.seo import check_seo_structure

        content_file = tmp_path / "test.md"
        content = """# Активная пена

Активная пена — это средство для бесконтактной мойки автомобиля.

## Как выбрать активную пену

Выбор зависит от типа загрязнений.

## Применение активной пены

Разведите концентрат согласно инструкции.
"""
        content_file.write_text(content, encoding="utf-8")

        # Returns tuple[str, dict] - (status, details)
        status, details = check_seo_structure(str(content_file), "активная пена")

        assert status in ["PASS", "WARN", "FAIL"]
        # details["intro"]["passed"] indicates keyword found
        assert details["intro"]["passed"]

    def test_keyword_missing_intro_fails(self, tmp_path):
        """Content without keyword in intro should fail intro check."""
        from llm_keywords_pipeline.validate.seo import check_seo_structure

        content_file = tmp_path / "test.md"
        content = """# Моющее средство

Это средство для бесконтактной мойки автомобиля.

## Как выбрать

Выбор зависит от типа.
"""
        content_file.write_text(content, encoding="utf-8")

        status, details = check_seo_structure(str(content_file), "активная пена")

        assert not details["intro"]["passed"]


class TestDetectLanguage:
    """Tests for detect_language function."""

    def test_ru_path(self):
        """Russian path should return 'ru'."""
        from llm_keywords_pipeline.validate.seo import detect_language

        assert detect_language("categories/test/content/test_ru.md") == "ru"

    def test_uk_path(self):
        """Ukrainian path should return 'uk'."""
        from llm_keywords_pipeline.validate.seo import detect_language

        assert detect_language("uk/categories/test/content/test_uk.md") == "uk"
