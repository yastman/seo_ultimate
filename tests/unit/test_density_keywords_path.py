"""TDD test: issue #11 — load_keywords_from_json must use PROJECT_ROOT from config.

The bug: density.py builds the path as Path(__file__).parent.parent / "categories" / ...
which resolves to src/llm_keywords_pipeline/categories/... (wrong).
The fix: use get_data_path(slug) from core.config (PROJECT_ROOT / categories / ...).
"""
import json
from unittest.mock import patch

from llm_keywords_pipeline.validate.density import load_keywords_from_json


class TestLoadKeywordsFromJson:
    """load_keywords_from_json must find files via PROJECT_ROOT, not package dir."""

    def test_returns_empty_list_for_missing_slug(self):
        """Non-existent slug must return empty list, not raise."""
        result = load_keywords_from_json("__nonexistent_slug_xyz__")
        assert result == []

    def test_loads_keywords_from_correct_path(self, tmp_path):
        """Must load keywords when file exists at get_data_path() location."""
        slug = "test-category"
        # Build the JSON in the correct place according to config
        data_dir = tmp_path / "categories" / slug / "data"
        data_dir.mkdir(parents=True)
        json_path = data_dir / f"{slug}_clean.json"
        json_path.write_text(json.dumps({
            "slug": slug,
            "keywords": [
                {"keyword": "тест ключ", "volume": 100},
                {"keyword": "другой ключ", "volume": 50},
            ],
        }), encoding="utf-8")

        # Patch CATEGORIES_DIR in config so load_keywords_from_json finds the file
        with patch("llm_keywords_pipeline.core.config.CATEGORIES_DIR", tmp_path / "categories"):
            result = load_keywords_from_json(slug)

        assert "тест ключ" in result
        assert "другой ключ" in result

    def test_path_does_not_go_through_src(self):
        """The data path must NOT resolve into src/llm_keywords_pipeline/categories."""
        from llm_keywords_pipeline.core.config import CATEGORIES_DIR

        bad_path_fragment = "src/llm_keywords_pipeline/categories"
        assert bad_path_fragment not in str(CATEGORIES_DIR), (
            f"CATEGORIES_DIR resolves inside src package: {CATEGORIES_DIR}"
        )

    def test_uses_get_data_path_logic(self, tmp_path):
        """get_data_path(slug, clean=True) and load_keywords_from_json must agree on location."""
        slug = "test-category-2"
        with patch("llm_keywords_pipeline.core.config.CATEGORIES_DIR", tmp_path / "categories"):
            from llm_keywords_pipeline.core import config as cfg
            expected_path = cfg.get_data_path(slug, clean=True)
        # Path must end with categories/<slug>/data/<slug>_clean.json
        assert expected_path.name == f"{slug}_clean.json"
        assert "categories" in expected_path.parts
