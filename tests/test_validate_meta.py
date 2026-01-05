import pytest
import json
from scripts.validate_meta import validate_title, validate_description, validate_meta_file

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
        desc = "Купить активную пену для бесконтактной мойки от производителя Ultimate. Опт и розница, доставка по Украине. Эффективное удаление грязи."
        keywords = ["активная пена"]
        result = validate_description(desc, keywords)
        with open("debug_result.txt", "w", encoding="utf-8") as f:
            import pprint
            f.write(pprint.pformat(result))
        assert result["overall"] == "PASS"
        assert result["checks"]["producer"]["passed"]
        assert result["checks"]["wholesale"]["passed"]
        assert result["overall"] == "PASS"
        
    def test_missing_producer(self):
        desc = "Хороший шампунь для машины, купить можно у нас в магазине с доставкой." + "а" * 50 # length ok
        result = validate_description(desc)
        assert not result["checks"]["producer"]["passed"]

class TestValidateMetaFile:
    def test_valid_file(self, tmp_path):
        meta_file = tmp_path / "test_meta.json"
        content = {
            "meta": {
                "title": "Купить Активная пена для мойки авто (5л) | Ultimate",
                "description": "Купить активную пену для бесконтактной мойки от производителя Ultimate. Опт и розница, доставка по Украине. Эффективное удаление грязи."
            },
            "h1": "Активная пена",
            "keywords_in_content": {
                "primary": ["активная пена"]
            }
        }
        meta_file.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")
        
        result = validate_meta_file(str(meta_file))
        if result["overall"] != "PASS":
            import pprint
            pprint.pprint(result)
        assert result["overall"] == "PASS"
        
    def test_missing_file(self):
        result = validate_meta_file("non_existent.json")
        assert "Cannot load meta file" in result["errors"][0]
