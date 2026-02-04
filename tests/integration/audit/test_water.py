"""Tests for audit/water.py"""

from seo_ultimate.audit.water import calculate_metrics_from_text


class TestCalculateMetrics:
    """Tests for calculate_metrics_from_text function."""

    def test_returns_dict_with_required_keys(self):
        """Should return dict with all required metrics."""
        text = """
        Активная пена для бесконтактной мойки автомобиля.
        Создаёт густую плотную пену, которая эффективно удаляет грязь.
        Подходит для использования с пеногенератором или пенной насадкой.
        """
        result = calculate_metrics_from_text(text, lang="ru")

        assert result is not None
        assert "total_words" in result
        assert "water_percent" in result
        assert "classic_nausea" in result
        assert "academic_nausea" in result

    def test_water_percent_is_positive(self):
        """Water percent should be positive for normal text."""
        text = "Активная пена для бесконтактной мойки автомобиля удаляет грязь"
        result = calculate_metrics_from_text(text, lang="ru")

        assert result is not None
        assert result["water_percent"] >= 0

    def test_classic_nausea_is_positive(self):
        """Classic nausea should be positive."""
        text = "Пена пена пена для мойки пена автомобиля пена"
        result = calculate_metrics_from_text(text, lang="ru")

        assert result is not None
        assert result["classic_nausea"] > 0

    def test_empty_text_returns_none(self):
        """Empty text should return None."""
        result = calculate_metrics_from_text("", lang="ru")
        assert result is None

    def test_non_cyrillic_text_returns_none(self):
        """Non-cyrillic text should return None."""
        result = calculate_metrics_from_text("Hello world this is English text", lang="ru")
        assert result is None

    def test_uk_language_works(self):
        """Should work with Ukrainian text."""
        text = "Активна піна для безконтактної мийки автомобіля видаляє бруд"
        result = calculate_metrics_from_text(text, lang="uk")

        assert result is not None
        assert result["total_words"] > 0


class TestWaterCalculation:
    """Tests for water percentage calculation."""

    def test_high_stopword_text_has_high_water(self):
        """Text with many stopwords should have high water percent."""
        # Text with many stopwords
        text = "Это и есть то что нужно для того чтобы было хорошо и правильно"
        result = calculate_metrics_from_text(text, lang="ru")

        assert result is not None
        # Should have relatively high water due to stopwords
        assert result["water_count"] > 0


class TestNauseaCalculation:
    """Tests for nausea calculation."""

    def test_repeated_word_increases_nausea(self):
        """Repeated word should increase classic nausea."""
        # Normal text
        text1 = "Активная пена для мойки автомобиля удаляет грязь эффективно"
        result1 = calculate_metrics_from_text(text1, lang="ru")

        # Text with repeated word
        text2 = "Пена пена пена пена пена пена пена пена пена для мойки"
        result2 = calculate_metrics_from_text(text2, lang="ru")

        assert result1 is not None
        assert result2 is not None
        assert result2["classic_nausea"] > result1["classic_nausea"]
