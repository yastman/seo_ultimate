import csv
import json

# Ensure we can import from scripts
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.analyze_category import analyze_category
from tests.helpers.file_builders import CategoryBuilder


class TestAnalyzeCategoryIntegration:
    @pytest.fixture
    def mock_structure_csv(self, tmp_path):
        csv_file = tmp_path / "structure.csv"
        # Minimal CSV with L3 mapping
        content = [
            ["L1: Care", "", ""],
            ["L2: Wash", "", ""],
            ["L3: Test Cluster", "", ""],  # Maps to test-cluster
            ["keyword1", "10", "100"],
            ["keyword2", "10", "200"],
        ]
        with open(csv_file, "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(content)
        return csv_file

    def test_priority_clean_json(self, tmp_path):
        """Test that _clean.json is prioritized over raw json and csv."""
        slug = "priority-test"

        # Build category with clean.json (default in builder)
        CategoryBuilder().with_slug(slug).with_keywords(
            [
                {"keyword": "clean_kw", "volume": 500, "cluster": "primary"},
                {"keyword": "clean_kw2", "volume": 100},
            ]
        ).build(tmp_path)

        # Also create a raw .json to ensure it's IGNORED
        raw_json = tmp_path / "categories" / slug / "data" / f"{slug}.json"
        with open(raw_json, "w", encoding="utf-8") as f:
            json.dump({"keywords": {"primary": [{"keyword": "raw_kw", "volume": 999}]}}, f)

        # Patch paths
        with patch("scripts.analyze_category.PROJECT_ROOT", tmp_path):
            result = analyze_category(slug)

        assert result["meta"]["source"] == "clean_json"
        assert result["keywords"]["count"] == 2
        # Check that we got keys from clean json
        assert result["keywords"]["primary"]["keyword"] == "clean_kw"

    def test_priority_raw_json(self, tmp_path):
        """Test that raw .json is used if clean.json is missing."""
        slug = "raw-test"

        # Build structure but DELETE clean.json
        cat_dir = CategoryBuilder().with_slug(slug).build(tmp_path)
        clean_json = cat_dir / "data" / f"{slug}_clean.json"
        clean_json.unlink()

        # Create raw .json
        raw_json = cat_dir / "data" / f"{slug}.json"
        raw_data = {
            "keywords": {
                "primary": [{"keyword": "raw_kw_primary", "volume": 300}],
                "secondary": [{"keyword": "raw_kw_sec", "volume": 100}],
            }
        }
        with open(raw_json, "w", encoding="utf-8") as f:
            json.dump(raw_data, f)

        with patch("scripts.analyze_category.PROJECT_ROOT", tmp_path):
            result = analyze_category(slug)

        assert result["meta"]["source"] == "raw_json"
        assert result["keywords"]["count"] == 2
        assert result["keywords"]["primary"]["keyword"] == "raw_kw_primary"

    def test_priority_csv_fallback(self, tmp_path, mock_structure_csv):
        """Test fallback to CSV if no JSONs exist."""
        slug = "test-cluster"  # Must match SLUG_TO_L3 or L3_TO_SLUG default mapping

        # Ensure categories dir exists so it doesn't crash on path construction
        (tmp_path / "categories" / slug / "data").mkdir(parents=True)

        with (
            patch("scripts.analyze_category.PROJECT_ROOT", tmp_path),
            patch("scripts.analyze_category.SEMANTICS_CSV", mock_structure_csv),
            patch("scripts.analyze_category.SLUG_TO_L3", {"test-cluster": "Test Cluster"}),
        ):
            result = analyze_category(slug)

        if "error" in result:
            pytest.fail(f"Analysis failed with error: {result['error']}")

        assert result["meta"]["source"] == "csv"
        assert result["keywords"]["count"] == 2
        assert result["keywords"]["primary"]["keyword"] == "keyword2"  # volume 200 > 100

    def test_semantic_depth_logic(self, tmp_path):
        """Test semantic depth calculation (shallow/medium/deep)."""
        # Shallow (<5)
        slug_s = "shallow"
        CategoryBuilder().with_slug(slug_s).with_keywords(["kw1", "kw2"]).build(tmp_path)

        with patch("scripts.analyze_category.PROJECT_ROOT", tmp_path):
            res_s = analyze_category(slug_s)
        assert res_s["keywords"]["semantic_depth"] == "shallow"
        assert res_s["content"]["format"] == "compact"

        # Medium (6-15)
        slug_m = "medium"
        CategoryBuilder().with_slug(slug_m).with_keywords([f"kw{i}" for i in range(10)]).build(tmp_path)

        with patch("scripts.analyze_category.PROJECT_ROOT", tmp_path):
            res_m = analyze_category(slug_m)
        assert res_m["keywords"]["semantic_depth"] == "medium"
        assert res_m["content"]["format"] == "standard"

        # Deep (>15)
        slug_d = "deep"
        CategoryBuilder().with_slug(slug_d).with_keywords([f"kw{i}" for i in range(25)]).build(tmp_path)

        with patch("scripts.analyze_category.PROJECT_ROOT", tmp_path):
            res_d = analyze_category(slug_d)
        assert res_d["keywords"]["semantic_depth"] == "deep"
        assert res_d["content"]["format"] == "comprehensive"
        assert res_d["keywords"]["need_clustering"] is True

    def test_intent_split(self, tmp_path):
        """Test separation of Core vs Commercial keywords."""
        slug = "intent-test"
        # Keywords mix
        kws = [
            {"keyword": "active foam", "volume": 100},  # core
            {"keyword": "активная пена заказать", "volume": 50},  # commercial
            {"keyword": "активная пена", "volume": 1000},  # core
            {"keyword": "купить активную пену", "volume": 500},  # commercial
            {"keyword": "активная пена цена", "volume": 200},  # commercial
        ]

        CategoryBuilder().with_slug(slug).with_keywords(kws).build(tmp_path)

        with patch("scripts.analyze_category.PROJECT_ROOT", tmp_path):
            result = analyze_category(slug)

        assert result["keywords"]["core_count"] == 2  # active foam, активная пена
        assert result["keywords"]["commercial_count"] == 3  # заказать, купить, цена
        assert "активная пена" in result["keywords"]["core_keywords"]
        assert "купить активную пену" in result["keywords"]["commercial_keywords"]
