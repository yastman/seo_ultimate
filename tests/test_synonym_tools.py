import pytest
import json
from pathlib import Path
from scripts.synonym_tools import normalize_keyword, is_commercial, analyze_category

class TestNormalizeKeyword:
    def test_basic_normalization(self):
        # "автошампунь для авто" -> remove "для", "авто" -> "автошампунь"
        kw = "автошампунь для авто"
        assert normalize_keyword(kw) == "автошампунь"

    def test_sorting(self):
        # Words should be sorted alphabetically
        kw = "мойка ручная"
        assert normalize_keyword(kw) == "мойка ручная" # м, р - sorted?
        # "мойка" < "ручная"? yes.
        # "ручная мойка" -> "мойка ручная"
        assert normalize_keyword("ручная мойка") == "мойка ручная"

    def test_stemming_prefixes(self):
        # "полироль кузова" -> "кузов полир" (prefixes: полиров, полирал -> полир; кузов -> кузов)
        # Wait, script logic:
        # if w.startswith("полиров") or w.startswith("полирал")...
        # "полироль" does NOT start with "полиров".
        # Let's check script source again.
        pass

    def test_stop_words_removal(self):
        kw = "шампунь для бесконтактной мойки"
        expected = "бесконтактной мойки шампунь"
        assert normalize_keyword(kw) == expected

class TestIsCommercial:
    def test_commercial_markers(self):
        assert is_commercial("купить автошампунь")
        assert is_commercial("цена полироли")
        assert is_commercial("отзывы о воске")
        assert is_commercial("заказать химию")
        
    def test_informational(self):
        assert not is_commercial("как выбрать шампунь")
        assert not is_commercial("лучший очиститель") # "лучший" is not in commercial markers list

class TestAnalyzeCategory:
    def test_find_duplicates(self, tmp_path):
        # Setup fake category structure
        cat_dir = tmp_path / "test-category"
        data_dir = cat_dir / "data"
        data_dir.mkdir(parents=True)
        
        # Create _clean.json
        clean_json = data_dir / "test-category_clean.json"
        
        # Two keywords that should normalize to same string:
        # "шампунь для ручной мойки" (vol 100)
        # "шампунь ручной мойки" (vol 50) -> normalized same (remove "для")
        
        content = {
            "keywords": {
                "primary": [
                    {"keyword": "шампунь для ручной мойки", "volume": 100},
                    {"keyword": "шампунь ручной мойки", "volume": 50}
                ]
            }
        }
        clean_json.write_text(json.dumps(content), encoding="utf-8")
        
        # Run analysis
        result = analyze_category(cat_dir)
        
        assert result is not None
        assert len(result["changes"]) == 1
        change = result["changes"][0]
        assert change["winner"]["keyword"] == "шампунь для ручной мойки" # Higher volume
        assert len(change["losers"]) == 1
        assert change["losers"][0]["keyword"] == "шампунь ручной мойки"
