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
        # Russian endings removal
        assert get_word_stem("краcного") == "краcн"  # ого
        # "яя" skipped (len 5 !> 2+3), but "я" might be removed if present?
        # Actually logic: finds first match that satisfies length.
        # "я" is at the end. "яя" matched but length check failed.
        # So it falls through to "я" (len 1). 5 > 1+3 (5>4) True. Removes last char. -> синя.
        assert get_word_stem("синяя") == "синя"
        assert get_word_stem("шампуни") == "шампун"  # и
        assert get_word_stem("короткое") == "коротк"  # ое

        # Short words
        assert get_word_stem("пена") == "пена"  # <= 4 chars logic

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
