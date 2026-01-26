"""Tests for update_volume.py"""

import json

from scripts.update_volume import update_category


class TestUpdateCategory:
    """Test category update."""

    def test_updates_keyword_volumes(self, tmp_path):
        """Should update keyword volumes from volumes dict."""
        clean_file = tmp_path / "test_clean.json"
        data = {"keywords": [{"keyword": "тест", "volume": 0}, {"keyword": "проверка", "volume": 50}]}
        clean_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        volumes = {"тест": 100, "проверка": 50}  # проверка unchanged
        updated, total = update_category(clean_file, volumes)

        assert total == 2
        assert updated == 1  # only тест changed

        # Verify file was updated
        result = json.loads(clean_file.read_text(encoding="utf-8"))
        assert result["keywords"][0]["volume"] == 100

    def test_updates_synonym_volumes(self, tmp_path):
        """Should also update synonym volumes."""
        clean_file = tmp_path / "test_clean.json"
        data = {"keywords": [], "synonyms": [{"keyword": "синоним", "volume": 0}]}
        clean_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        volumes = {"синоним": 200}
        updated, total = update_category(clean_file, volumes)

        assert total == 1
        assert updated == 1

    def test_no_update_when_volume_unchanged(self, tmp_path):
        """Should not count as updated when volume is same."""
        clean_file = tmp_path / "test_clean.json"
        data = {"keywords": [{"keyword": "тест", "volume": 100}]}
        clean_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        volumes = {"тест": 100}  # Same value
        updated, total = update_category(clean_file, volumes)

        assert updated == 0

    def test_returns_zero_for_missing_keywords(self, tmp_path):
        """Should return 0 updated when keywords not in volumes dict."""
        clean_file = tmp_path / "test_clean.json"
        data = {"keywords": [{"keyword": "нет в словаре", "volume": 0}]}
        clean_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        volumes = {"другой ключ": 100}
        updated, total = update_category(clean_file, volumes)

        assert updated == 0
        assert total == 1
