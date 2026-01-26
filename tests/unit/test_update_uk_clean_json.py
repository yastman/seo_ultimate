"""Tests for update_uk_clean_json.py"""

from scripts.update_uk_clean_json import group_keywords, update_clean_json


class TestGroupKeywords:
    """Test keyword grouping by volume."""

    def test_groups_by_volume_thresholds(self):
        """Should group keywords by volume: primary >=500, secondary 100-499, supporting <100."""
        keywords = [
            {"keyword": "high", "volume": 1000},
            {"keyword": "medium", "volume": 200},
            {"keyword": "low", "volume": 50},
        ]
        result = group_keywords(keywords)

        assert len(result["primary"]) == 1
        assert result["primary"][0]["keyword"] == "high"

        assert len(result["secondary"]) == 1
        assert result["secondary"][0]["keyword"] == "medium"

        assert len(result["supporting"]) == 1
        assert result["supporting"][0]["keyword"] == "low"

    def test_boundary_500_is_primary(self):
        """Keyword with volume exactly 500 should be primary."""
        keywords = [{"keyword": "boundary", "volume": 500}]
        result = group_keywords(keywords)
        assert len(result["primary"]) == 1

    def test_boundary_100_is_secondary(self):
        """Keyword with volume exactly 100 should be secondary."""
        keywords = [{"keyword": "boundary", "volume": 100}]
        result = group_keywords(keywords)
        assert len(result["secondary"]) == 1

    def test_empty_list_returns_empty_groups(self):
        """Should return empty groups for empty input."""
        result = group_keywords([])
        assert result["primary"] == []
        assert result["secondary"] == []
        assert result["supporting"] == []


class TestUpdateCleanJson:
    """Test clean JSON file creation."""

    def test_creates_clean_json(self, tmp_path, monkeypatch):
        """Should create _clean.json file with grouped keywords."""
        # Monkeypatch to use tmp_path
        monkeypatch.chdir(tmp_path)

        keywords = [{"keyword": "тест", "volume": 600}]
        result_path = update_clean_json("test-slug", keywords, 600)

        assert result_path.exists()

        import json

        data = json.loads(result_path.read_text(encoding="utf-8"))
        assert data["id"] == "test-slug"
        assert data["language"] == "uk"
        assert data["total_volume"] == 600
        assert len(data["keywords"]) == 1
