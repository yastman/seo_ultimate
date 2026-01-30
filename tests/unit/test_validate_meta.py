import json

from scripts.validate_meta import (
    get_primary_keywords,
    get_word_stem,
    keyword_matches,
    validate_description,
    validate_meta_file,
    validate_title,
)


class TestSemanticLogic:
    def test_get_word_stem(self):
        # Now uses MorphAnalyzer (via keyword_utils).
        # With pymorphy3: returns proper lemmas (синяя -> синий)
        # With Snowball fallback: returns stems (синяя -> син)
        # Test verifies consistent behavior within same word family

        # Same word family should produce same stem/lemma
        assert get_word_stem("синяя") == get_word_stem("синюю")  # both from "синий"
        assert get_word_stem("шампуни") == get_word_stem("шампунем")  # both from "шампунь"
        assert get_word_stem("короткое") == get_word_stem("короткую")  # both from "короткий"

        # Different words should produce different stems
        assert get_word_stem("пена") != get_word_stem("шампунь")

    def test_keyword_matches(self):
        # Exact
        assert keyword_matches("пена", "купить пена")

        # Stem matching
        assert keyword_matches("автошампунь", "лучшие автошампуни")
        assert keyword_matches("очиститель", "очистителях")

        # Multi-word
        assert keyword_matches("активная пена", "активную пену купить")
        assert not keyword_matches("активная пена", "пассивная вода")


class TestJsonHelpers:
    def test_get_primary_keywords(self):
        data = {"keywords": {"primary": ["kw1", {"keyword": "kw2", "volume": 100}]}}
        kws = get_primary_keywords(data)
        assert "kw1" in kws
        assert "kw2" in kws


class TestValidateTitle:
    def test_valid_title(self):
        title = "Купить Активная пена для мойки авто (5л) | Ultimate"
        keywords = ["активная пена"]
        result = validate_title(title, keywords)
        # Length without brand: "Купить Активная пена для мойки авто (5л)" = ~40 chars > 30.
        assert result["checks"]["length"]["passed"]
        assert result["checks"]["no_colon"]["passed"]
        assert result["checks"]["primary_keyword"]["passed"]
        assert result["overall"] == "PASS"

    def test_too_short(self):
        title = "Купить воск"
        result = validate_title(title)
        assert not result["checks"]["length"]["passed"]

    def test_with_colon(self):
        title = "Шампунь: лучший выбор для авто (50 chars)"
        result = validate_title(title)
        assert not result["checks"]["no_colon"]["passed"]

    def test_marketing_fluff(self):
        title = "Самые лучшие цены на автошампунь (50 chars)"
        result = validate_title(title)
        assert not result["checks"]["no_fluff"]["passed"]


class TestValidateDescription:
    def test_regex_encoding(self):
        import re

        text = "от производителя"
        pattern = r"от производителя"
        assert re.search(pattern, text)

    def test_valid_desc(self):
        desc = (
            "Купить активную пену для бесконтактной мойки от производителя Ultimate. "
            "Опт и розница, доставка по Украине. Эффективное удаление грязи."
        )
        keywords = ["активная пена"]
        result = validate_description(desc, keywords)

        assert result["overall"] == "PASS"
        assert result["checks"]["producer"]["passed"]
        assert result["checks"]["wholesale"]["passed"]

    def test_missing_producer(self):
        desc = "Хороший шампунь для машины, купить можно у нас в магазине с доставкой." + "а" * 50  # length ok
        result = validate_description(desc)
        assert not result["checks"]["producer"]["passed"]


class TestValidateMetaFile:
    def test_valid_file(self, tmp_path):
        meta_file = tmp_path / "test_meta.json"

        desc = (
            "Купить активную пену для бесконтактной мойки от производителя Ultimate. "
            "Опт и розница, доставка по Украине. Эффективное удаление грязи."
        )

        content = {
            "meta": {
                "title": "Купить Активная пена для мойки авто (5л) | Ultimate",
                "description": desc,
            },
            "h1": "Активная пена",
            "keywords_in_content": {"primary": ["активная пена"]},
        }
        meta_file.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")

        result = validate_meta_file(str(meta_file))
        assert result["overall"] == "PASS"

    def test_missing_file(self):
        result = validate_meta_file("non_existent.json")
        assert "Cannot load meta file" in result["errors"][0]


class TestValidateMetaUK:
    """Tests for UK language support in validate_meta."""

    def test_validate_meta_uk_language(self, tmp_path):
        """validate_meta_file works with lang='uk'."""
        meta_file = tmp_path / "test_meta.json"

        # Use keyword that appears verbatim in title/description (активна піна)
        desc = (
            "Активна піна для безконтактної мийки від виробника Ultimate. "
            "Опт і роздріб, доставка по Україні. Ефективне видалення бруду."
        )

        content = {
            "slug": "test",
            "language": "uk",
            "meta": {
                "title": "Активна піна для безконтактної мийки - купити в Україні | Ultimate",
                "description": desc,
            },
            "h1": "Активна піна для безконтактної мийки",
            "keywords_in_content": {"primary": ["активна піна"]},
        }
        meta_file.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")

        result = validate_meta_file(str(meta_file), lang="uk")
        assert result is not None
        assert result["overall"] in ["PASS", "WARNING"]

    def test_validate_meta_uk_detects_missing_producer(self, tmp_path):
        """UK validation detects missing 'від виробника' pattern."""
        meta_file = tmp_path / "test_meta.json"

        desc = (
            "Активна піна для безконтактної мийки автомобіля. "
            "Доставка по Україні. Ефективне видалення бруду і забруднень."
        )

        content = {
            "slug": "test",
            "language": "uk",
            "meta": {
                "title": "Активна піна для безконтактної мийки - купити в Україні | Ultimate",
                "description": desc,
            },
            "h1": "Активна піна для безконтактної мийки",
            "keywords_in_content": {"primary": ["активна піна"]},
        }
        meta_file.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")

        result = validate_meta_file(str(meta_file), lang="uk")
        # Should fail because missing 'від виробника'
        assert not result["description"]["checks"]["producer"]["passed"]

    def test_validate_meta_uk_wholesale_pattern(self, tmp_path):
        """UK validation detects 'опт і роздріб' pattern."""
        meta_file = tmp_path / "test_meta.json"

        desc = (
            "Активна піна для безконтактної мийки від виробника Ultimate. "
            "Опт і роздріб, доставка по Україні. Ефективне видалення бруду."
        )

        content = {
            "slug": "test",
            "language": "uk",
            "meta": {
                "title": "Активна піна для безконтактної мийки - купити в Україні | Ultimate",
                "description": desc,
            },
            "h1": "Активна піна для безконтактної мийки",
            "keywords_in_content": {"primary": ["активна піна"]},
        }
        meta_file.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")

        result = validate_meta_file(str(meta_file), lang="uk")
        assert result["description"]["checks"]["wholesale"]["passed"]
