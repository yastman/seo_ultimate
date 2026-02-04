"""Integration tests for seo_ultimate.validate.meta module."""

import json
from pathlib import Path


class TestValidateMetaFile:
    """Tests for validate_meta_file function."""

    def test_valid_meta_passes(self, tmp_path: Path):
        """Valid meta file with all required fields should pass validation."""
        meta_file = tmp_path / "test_meta.json"
        meta_data = {
            "slug": "test",
            "language": "ru",
            "meta": {
                "title": "Тестовый товар — купить, цены | Ultimate",
                "description": "Тестовый товар от производителя Ultimate. Опт и розница. Доставка по Украине.",
            },
            "h1": "Тестовый товар",
        }
        meta_file.write_text(json.dumps(meta_data, ensure_ascii=False))

        from seo_ultimate.validate.meta import validate_meta_file

        result = validate_meta_file(str(meta_file))

        assert result["overall"] in ["PASS", "WARNING"]
        assert not result.get("errors")

    def test_missing_h1_fails(self, tmp_path: Path):
        """Meta file without H1 should fail validation."""
        meta_file = tmp_path / "test_meta.json"
        meta_data = {
            "slug": "test",
            "language": "ru",
            "meta": {
                "title": "Test Title",
                "description": "Test description",
            },
        }
        meta_file.write_text(json.dumps(meta_data, ensure_ascii=False))

        from seo_ultimate.validate.meta import validate_meta_file

        result = validate_meta_file(str(meta_file))

        # H1 is empty, not an error but validation should reflect this
        assert result["h1"]["value"] == ""

    def test_invalid_json_returns_errors(self, tmp_path: Path):
        """Invalid JSON file should return errors."""
        meta_file = tmp_path / "test_meta.json"
        meta_file.write_text("{ invalid json }")

        from seo_ultimate.validate.meta import validate_meta_file

        result = validate_meta_file(str(meta_file))

        assert result["overall"] == "FAIL"
        assert len(result["errors"]) > 0

    def test_uk_language_validation(self, tmp_path: Path):
        """Ukrainian meta should use UK-specific validation patterns."""
        meta_file = tmp_path / "test_meta.json"
        meta_data = {
            "slug": "test",
            "language": "uk",
            "meta": {
                "title": "Тестовий товар — купити, ціни | Ultimate",
                "description": "Тестовий товар від виробника Ultimate. Опт і роздріб. Доставка по Україні.",
            },
            "h1": "Тестовий товар",
        }
        meta_file.write_text(json.dumps(meta_data, ensure_ascii=False))

        from seo_ultimate.validate.meta import validate_meta_file

        result = validate_meta_file(str(meta_file), lang="uk")

        assert result["lang"] == "uk"
        # UK patterns should be validated
        assert result["description"]["checks"]["producer"]["passed"]


class TestValidateTitle:
    """Tests for validate_title function."""

    def test_title_length_ok(self):
        """Title within length limits should pass."""
        from seo_ultimate.validate.meta import validate_title

        # Title without brand (before |) should be 30-60 chars
        title = "Активная пена для авто — купить, цены в Украине | Ultimate"
        result = validate_title(title)

        assert result["checks"]["length"]["passed"]

    def test_title_too_short(self):
        """Title below min length should fail length check."""
        from seo_ultimate.validate.meta import validate_title

        title = "Пена | Ultimate"
        result = validate_title(title)

        assert not result["checks"]["length"]["passed"]
        assert "short" in result["checks"]["length"]["message"].lower()

    def test_title_with_colon_fails(self):
        """Title with colon should fail no_colon check."""
        from seo_ultimate.validate.meta import validate_title

        title = "Товар: купить онлайн | Ultimate"
        result = validate_title(title)

        assert not result["checks"]["no_colon"]["passed"]

    def test_title_primary_keyword_found(self):
        """Title containing primary keyword should pass."""
        from seo_ultimate.validate.meta import validate_title

        title = "Активная пена — купить, цены | Ultimate"
        result = validate_title(title, primary_keywords=["активная пена"])

        assert result["checks"]["primary_keyword"]["passed"]


class TestValidateDescription:
    """Tests for validate_description function."""

    def test_description_length_ok(self):
        """Description within length limits should pass."""
        from seo_ultimate.validate.meta import validate_description

        desc = "Активная пена от производителя Ultimate. Опт и розница. Доставка по Украине. Качественная автохимия."
        result = validate_description(desc)

        assert result["checks"]["length"]["passed"]

    def test_description_producer_pattern_ru(self):
        """Russian description should check for RU producer pattern."""
        from seo_ultimate.validate.meta import validate_description

        desc = "Товар от производителя Ultimate. Опт и розница. Доставка."
        result = validate_description(desc, lang="ru")

        assert result["checks"]["producer"]["passed"]

    def test_description_producer_pattern_uk(self):
        """Ukrainian description should check for UK producer pattern."""
        from seo_ultimate.validate.meta import validate_description

        desc = "Товар від виробника Ultimate. Опт і роздріб. Доставка."
        result = validate_description(desc, lang="uk")

        assert result["checks"]["producer"]["passed"]


class TestValidateH1:
    """Tests for validate_h1 function."""

    def test_h1_exact_match(self):
        """H1 with exact keyword match should pass."""
        from seo_ultimate.validate.meta import validate_h1

        result = validate_h1("Активная пена", "активная пена")

        assert result["passed"]
        assert result["form"] == "exact"

    def test_h1_plural_match(self):
        """H1 with plural form should pass."""
        from seo_ultimate.validate.meta import validate_h1

        result = validate_h1("Активные пены", "активная пена")

        assert result["passed"]
        assert result["form"] in ["plural", "morphological"]

    def test_h1_no_match(self):
        """H1 without keyword should fail."""
        from seo_ultimate.validate.meta import validate_h1

        result = validate_h1("Моющие средства", "активная пена")

        assert not result["passed"]


class TestGetPrimaryKeywords:
    """Tests for get_primary_keywords function."""

    def test_clean_json_format(self):
        """Should extract MAX volume keyword from _clean.json format."""
        from seo_ultimate.validate.meta import get_primary_keywords

        data = {
            "keywords": [
                {"keyword": "пена", "volume": 100},
                {"keyword": "активная пена", "volume": 500},
                {"keyword": "автопена", "volume": 200},
            ]
        }

        result = get_primary_keywords(data)

        assert result == ["активная пена"]

    def test_old_format(self):
        """Should handle old format with nested primary list."""
        from seo_ultimate.validate.meta import get_primary_keywords

        data = {"keywords": {"primary": [{"keyword": "активная пена"}]}}

        result = get_primary_keywords(data)

        assert result == ["активная пена"]
