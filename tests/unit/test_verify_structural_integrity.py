"""Tests for verify_structural_integrity.py"""

import json

from scripts.verify_structural_integrity import check_category


class TestCheckCategory:
    """Test category structure check."""

    def test_returns_dict(self, tmp_path, monkeypatch):
        """Should return a dict with results."""
        import scripts.verify_structural_integrity as vsi

        monkeypatch.setattr(vsi, "CATEGORIES_DIR", tmp_path)

        result = check_category("nonexistent")
        assert isinstance(result, dict)
        assert result["status"] == "MISSING_JSON"

    def test_detects_missing_json(self, tmp_path, monkeypatch):
        """Should detect when _clean.json is missing."""
        import scripts.verify_structural_integrity as vsi

        monkeypatch.setattr(vsi, "CATEGORIES_DIR", tmp_path)

        result = check_category("test-slug")
        assert result["status"] == "MISSING_JSON"

    def test_parses_valid_json(self, tmp_path, monkeypatch):
        """Should parse valid _clean.json file."""
        import scripts.verify_structural_integrity as vsi

        monkeypatch.setattr(vsi, "CATEGORIES_DIR", tmp_path)

        # Create category structure
        cat_dir = tmp_path / "test-cat" / "data"
        cat_dir.mkdir(parents=True)
        data = {"type": "L3", "keywords": {"primary": [{"keyword": "тест"}]}}
        (cat_dir / "test-cat_clean.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        result = check_category("test-cat")
        assert result["status"] == "OK"
        assert result["type"] == "L3"
        assert result["kw_count"] == 1

    def test_detects_empty_category(self, tmp_path, monkeypatch):
        """Should flag empty categories (no keywords)."""
        import scripts.verify_structural_integrity as vsi

        monkeypatch.setattr(vsi, "CATEGORIES_DIR", tmp_path)

        cat_dir = tmp_path / "empty-cat" / "data"
        cat_dir.mkdir(parents=True)
        data = {"type": "L3", "keywords": {}}
        (cat_dir / "empty-cat_clean.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        result = check_category("empty-cat")
        assert result["status"] == "ISSUES"
        assert any("Empty category" in issue for issue in result["issues"])
