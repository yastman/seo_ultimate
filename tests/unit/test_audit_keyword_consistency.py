"""Tests for audit_keyword_consistency.py"""

import json
from unittest.mock import MagicMock, patch

from scripts.audit_keyword_consistency import scan_actual_keywords


class TestScanActualKeywords:
    """Test scan_actual_keywords function."""

    def test_returns_empty_dict_when_no_files(self, tmp_path, monkeypatch):
        """Should return empty dict when no _clean.json files exist."""
        monkeypatch.setattr(
            "scripts.audit_keyword_consistency.CATEGORIES_DIR", str(tmp_path)
        )
        result = scan_actual_keywords()
        assert result == {}

    def test_extracts_keywords_from_list_format(self, tmp_path, monkeypatch):
        """Should extract keywords from list format _clean.json."""
        monkeypatch.setattr(
            "scripts.audit_keyword_consistency.CATEGORIES_DIR", str(tmp_path)
        )
        cat_path = tmp_path / "test-slug"
        cat_path.mkdir()

        data = {
            "id": "test-slug",
            "keywords": [
                {"keyword": "ключ один", "volume": 100},
                {"keyword": "ключ два", "volume": 50},
            ],
        }
        (cat_path / "test-slug_clean.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )

        result = scan_actual_keywords()
        assert "test-slug" in result
        assert "ключ один" in result["test-slug"]
        assert "ключ два" in result["test-slug"]

    def test_extracts_keywords_from_dict_format(self, tmp_path, monkeypatch):
        """Should extract keywords from dict format _clean.json."""
        monkeypatch.setattr(
            "scripts.audit_keyword_consistency.CATEGORIES_DIR", str(tmp_path)
        )
        cat_path = tmp_path / "test-slug2"
        cat_path.mkdir()

        data = {
            "id": "test-slug2",
            "keywords": {
                "primary": [{"keyword": "первинний", "volume": 100}],
                "secondary": [{"keyword": "вторинний", "volume": 50}],
            },
        }
        (cat_path / "test-slug2_clean.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )

        result = scan_actual_keywords()
        assert "test-slug2" in result
        assert "первинний" in result["test-slug2"]
        assert "вторинний" in result["test-slug2"]

    def test_handles_empty_keywords(self, tmp_path, monkeypatch):
        """Should handle category with no keywords."""
        monkeypatch.setattr(
            "scripts.audit_keyword_consistency.CATEGORIES_DIR", str(tmp_path)
        )
        cat_path = tmp_path / "empty-slug"
        cat_path.mkdir()

        data = {"id": "empty-slug", "keywords": []}
        (cat_path / "empty-slug_clean.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )

        result = scan_actual_keywords()
        assert "empty-slug" in result
        assert len(result["empty-slug"]) == 0

    def test_handles_slug_field_fallback(self, tmp_path, monkeypatch):
        """Should use 'slug' field if 'id' is missing."""
        monkeypatch.setattr(
            "scripts.audit_keyword_consistency.CATEGORIES_DIR", str(tmp_path)
        )
        cat_path = tmp_path / "fallback-slug"
        cat_path.mkdir()

        data = {
            "slug": "fallback-slug",  # Using slug instead of id
            "keywords": [{"keyword": "тест", "volume": 100}],
        }
        (cat_path / "fallback-slug_clean.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )

        result = scan_actual_keywords()
        assert "fallback-slug" in result
        assert "тест" in result["fallback-slug"]
