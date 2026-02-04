"""Tests for audit/ner_brands.py"""

from seo_ultimate.audit.ner_brands import (
    check_blacklist,
    is_false_positive_location,
)


class TestBrandBlacklist:
    """Tests for brand blacklist checks."""

    def test_detects_brand_koch(self):
        """Should detect Koch Chemie brand."""
        text = "Это средство от Koch Chemie отлично работает"
        result = check_blacklist(text)
        assert len(result["brands"]) > 0

    def test_detects_brand_grass(self):
        """Should detect Grass brand."""
        text = "Активная пена Grass для бесконтактной мойки"
        result = check_blacklist(text)
        assert len(result["brands"]) > 0

    def test_no_brands_in_clean_text(self):
        """Clean text should have no brands."""
        text = "Активная пена для бесконтактной мойки автомобиля"
        result = check_blacklist(text)
        assert len(result["brands"]) == 0


class TestCityBlacklist:
    """Tests for city blacklist checks."""

    def test_detects_city_kiev(self):
        """Should detect Kiev city."""
        text = "Доставка по Киеву и области"
        result = check_blacklist(text)
        assert len(result["cities"]) > 0

    def test_no_cities_in_clean_text(self):
        """Clean text should have no cities."""
        text = "Доставка по всей Украине"
        result = check_blacklist(text)
        # May have false positives for "украине" but not cities
        # Check specifically for city entities
        city_names = [c["entity"] for c in result["cities"]]
        assert "киев" not in city_names


class TestFalsePositiveLocation:
    """Tests for false positive detection."""

    def test_rovno_as_adverb_is_false_positive(self):
        """'ровно' as adverb should be false positive."""
        # Without preposition - should be false positive
        result = is_false_positive_location("ровно", "занимает ровно 5 минут")
        assert result is True

    def test_rovno_with_preposition_is_real_city(self):
        """'в ровно' should be detected as real city."""
        result = is_false_positive_location("ровно", "доставка в Ровно")
        assert result is False


class TestAIFluff:
    """Tests for AI fluff detection."""

    def test_detects_ai_fluff_phrase(self):
        """Should detect AI fluff phrases."""
        text = "В этой статье мы рассмотрим особенности выбора"
        result = check_blacklist(text)
        assert len(result["ai_fluff"]) > 0

    def test_no_ai_fluff_in_clean_text(self):
        """Clean text should have no AI fluff."""
        text = "Активная пена создаёт густую плотную пену для мойки"
        result = check_blacklist(text)
        assert len(result["ai_fluff"]) == 0


class TestStrictPhrases:
    """Tests for strict blacklist phrases."""

    def test_detects_strict_phrase(self):
        """Should detect strict blacklist phrase."""
        text = "В современном мире автохимия стала необходимостью"
        result = check_blacklist(text)
        assert len(result["strict_phrases"]) > 0
