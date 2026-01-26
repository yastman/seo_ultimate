"""Tests for extract_ru_keywords_mapping.py"""

import json


class TestExtractRuKeywordsMapping:
    """Test RU keywords mapping extraction."""

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "extract_ru_keywords_mapping.py"
        assert script_path.exists()

    def test_extract_keywords_v2_format(self, tmp_path, monkeypatch):
        """Should extract keywords from V2 format (list)."""
        from scripts.extract_ru_keywords_mapping import extract_ru_keywords

        # Create test structure
        cat_dir = tmp_path / "categories" / "test-cat" / "data"
        cat_dir.mkdir(parents=True)

        data = {"id": "test-cat", "keywords": [{"keyword": "тест", "volume": 100}]}
        (cat_dir / "test-cat_clean.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        monkeypatch.chdir(tmp_path)
        result = extract_ru_keywords()

        assert "test-cat" in result
        assert len(result["test-cat"]["keywords"]) == 1

    def test_extract_keywords_legacy_format(self, tmp_path, monkeypatch):
        """Should extract keywords from legacy format (dict with groups)."""
        from scripts.extract_ru_keywords_mapping import extract_ru_keywords

        cat_dir = tmp_path / "categories" / "legacy-cat" / "data"
        cat_dir.mkdir(parents=True)

        data = {
            "id": "legacy-cat",
            "keywords": {
                "primary": [{"keyword": "ключ1", "volume": 500}],
                "secondary": [{"keyword": "ключ2", "volume": 100}],
            },
        }
        (cat_dir / "legacy-cat_clean.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        monkeypatch.chdir(tmp_path)
        result = extract_ru_keywords()

        assert "legacy-cat" in result
        assert len(result["legacy-cat"]["keywords"]) == 2

    def test_includes_synonyms(self, tmp_path, monkeypatch):
        """Should include synonyms in extraction."""
        from scripts.extract_ru_keywords_mapping import extract_ru_keywords

        cat_dir = tmp_path / "categories" / "syn-cat" / "data"
        cat_dir.mkdir(parents=True)

        data = {
            "id": "syn-cat",
            "keywords": [{"keyword": "основной", "volume": 100}],
            "synonyms": [{"keyword": "синоним", "volume": 50}],
        }
        (cat_dir / "syn-cat_clean.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        monkeypatch.chdir(tmp_path)
        result = extract_ru_keywords()

        assert len(result["syn-cat"]["keywords"]) == 2
