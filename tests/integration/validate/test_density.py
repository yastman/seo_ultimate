"""Integration tests for llm_keywords_pipeline.validate.density module."""


class TestCheckKeywordDensity:
    """Tests for check_keyword_density function."""

    def test_single_keyword_density(self):
        """Calculate density of a single keyword."""
        from llm_keywords_pipeline.validate.density import check_keyword_density

        text = "Активная пена для мойки. Активная пена эффективно удаляет грязь."
        result = check_keyword_density(text, "активная пена")

        assert result["keyword"] == "активная пена"
        assert result["exact_count"] >= 1
        assert result["exact_density"] > 0

    def test_keyword_not_found(self):
        """Keyword not in text should have zero density."""
        from llm_keywords_pipeline.validate.density import check_keyword_density

        text = "Текст без искомого ключевого слова."
        result = check_keyword_density(text, "активная пена")

        assert result["exact_count"] == 0
        assert result["exact_density"] == 0.0


class TestAnalyzeText:
    """Tests for analyze_text function."""

    def test_basic_analysis(self):
        """Analyze text and get word frequencies."""
        from llm_keywords_pipeline.validate.density import analyze_text

        text = """
        Активная пена для бесконтактной мойки автомобиля.
        Пена образует густую текстуру и эффективно удаляет грязь.
        Активная пена безопасна для лакокрасочного покрытия.
        Используйте пену для регулярной мойки кузова.
        """
        result = analyze_text(text, top_n=10)

        assert "total_words" in result
        assert "word_frequencies" in result
        assert result["total_words"] > 0
        assert len(result["word_frequencies"]) > 0

    def test_stem_frequencies(self):
        """Stem-based analysis should group word forms."""
        from llm_keywords_pipeline.validate.density import analyze_text

        text = """
        Полировка кузова. Полировальная машинка для полировки.
        Полировочные пасты и полировальные круги.
        """
        result = analyze_text(text, top_n=10)

        assert "stem_frequencies" in result
        # Stems should group related words (returned as list)
        stems = result["stem_frequencies"]
        assert isinstance(stems, list)


class TestGetDensityStatus:
    """Tests for get_density_status function."""

    def test_ok_status(self):
        """Low density should return OK."""
        from llm_keywords_pipeline.validate.density import get_density_status

        assert get_density_status(1.0) == "OK"
        assert get_density_status(2.0) == "OK"

    def test_warning_status(self):
        """Medium density should return WARNING."""
        from llm_keywords_pipeline.validate.density import get_density_status

        assert get_density_status(2.6) == "WARNING"
        assert get_density_status(2.9) == "WARNING"

    def test_spam_status(self):
        """High density should return SPAM."""
        from llm_keywords_pipeline.validate.density import get_density_status

        assert get_density_status(3.1) == "SPAM"
        assert get_density_status(5.0) == "SPAM"


class TestCalculateDensity:
    """Tests for calculate_density function."""

    def test_calculation(self):
        """Density = (count / total_words) * 100."""
        from llm_keywords_pipeline.validate.density import calculate_density

        # 10 occurrences in 100 words = 10%
        assert calculate_density(10, 100) == 10.0
        # 2 occurrences in 100 words = 2%
        assert calculate_density(2, 100) == 2.0

    def test_zero_words(self):
        """Zero total words should return 0."""
        from llm_keywords_pipeline.validate.density import calculate_density

        assert calculate_density(5, 0) == 0.0


class TestCountStemFrequencies:
    """Tests for count_stem_frequencies function."""

    def test_russian_stems(self):
        """Russian stems should be grouped (MIN_STEM_FREQUENCY=3)."""
        from llm_keywords_pipeline.validate.density import count_stem_frequencies

        # Need at least 3 words with same stem (declensions, not derivatives)
        words = [
            "машина",
            "машины",
            "машину",  # 3 declensions -> машин
            "полировка",
            "полировки",
            "полировку",  # 3 declensions -> полировк
        ]
        result = count_stem_frequencies(words, lang="ru")

        # Should have entries for stems
        assert len(result) > 0
        # Each stem should have count and forms/example
        for stem, data in result.items():
            assert "count" in data
            assert "forms" in data or "example" in data

    def test_ukrainian_lang(self):
        """Ukrainian language should work (MIN_STEM_FREQUENCY=3)."""
        from llm_keywords_pipeline.validate.density import count_stem_frequencies

        # Need at least 3 words with same stem (declensions)
        words = [
            "машина",
            "машини",
            "машину",  # 3 declensions -> машин
            "полірування",
            "полірування",
            "полірування",  # repeat to reach threshold
        ]
        result = count_stem_frequencies(words, lang="uk")

        assert len(result) > 0
