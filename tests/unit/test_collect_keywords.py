"""Tests for collect_keywords.py"""

import json

from scripts.collect_keywords import collect_keywords


class TestCollectKeywords:
    """Test collect_keywords function."""

    def test_returns_list(self, tmp_path, monkeypatch):
        """Should return a list."""
        # Empty categories dir
        monkeypatch.setattr("scripts.collect_keywords.CATEGORIES_DIR", tmp_path)
        result = collect_keywords()
        assert isinstance(result, list)

    def test_extracts_keywords_from_clean_json(self, tmp_path, monkeypatch):
        """Should extract keywords from _clean.json files."""
        # Create test structure
        cat_path = tmp_path / "test-cat" / "data"
        cat_path.mkdir(parents=True)

        data = {"keywords": [{"keyword": "тест", "volume": 100}, {"keyword": "проверка", "volume": 50}]}
        (cat_path / "test-cat_clean.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr("scripts.collect_keywords.CATEGORIES_DIR", tmp_path)

        result = collect_keywords()
        keywords = [k["keyword"] for k in result]
        assert "тест" in keywords
        assert "проверка" in keywords

    def test_deduplicates_by_highest_volume(self, tmp_path, monkeypatch):
        """Should keep keyword with highest volume when duplicates exist."""
        # Create two categories with same keyword
        for i, vol in enumerate([50, 100]):
            cat_path = tmp_path / f"cat-{i}" / "data"
            cat_path.mkdir(parents=True)
            data = {"keywords": [{"keyword": "общий", "volume": vol}]}
            (cat_path / f"cat-{i}_clean.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr("scripts.collect_keywords.CATEGORIES_DIR", tmp_path)

        result = collect_keywords()
        общий = [k for k in result if k["keyword"] == "общий"]
        assert len(общий) == 1
        assert общий[0]["volume"] == 100

    def test_sorts_by_volume_descending(self, tmp_path, monkeypatch):
        """Should return keywords sorted by volume descending."""
        cat_path = tmp_path / "test-cat" / "data"
        cat_path.mkdir(parents=True)

        data = {
            "keywords": [
                {"keyword": "low", "volume": 10},
                {"keyword": "high", "volume": 1000},
                {"keyword": "mid", "volume": 100},
            ]
        }
        (cat_path / "test-cat_clean.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr("scripts.collect_keywords.CATEGORIES_DIR", tmp_path)

        result = collect_keywords()
        volumes = [k["volume"] for k in result]
        assert volumes == sorted(volumes, reverse=True)
