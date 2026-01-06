"""
Tests for show_keyword_distribution.py — Keyword distribution viewer

Tests cover:
1. Missing/invalid arguments
2. OLD structure (keywords_detailed)
3. NEW structure (keywords.primary/secondary/supporting)
4. Output format
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.show_keyword_distribution import (
    _parse_density_percent,
    format_stats,
    load_keywords,
    main,
)


class TestShowKeywordDistributionCli:
    def test_missing_argument_raises(self):
        with pytest.raises(SystemExit) as exc:
            main([])
        assert exc.value.code == 2

    def test_nonexistent_file_error(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
        rc = main([str(tmp_path / "nonexistent.json")])
        out = capsys.readouterr().out
        assert rc == 1
        assert "not found" in out.lower()


class TestOldStructureHandling:
    def test_parses_old_structure(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
        data = {
            "category_name_ru": "Активная пена",
            "tier": "B",
            "keywords_detailed": [
                {
                    "phrase": "активная пена",
                    "volume": 1000,
                    "relative_freq": 25.0,
                    "role": "primary",
                },
                {
                    "phrase": "пена для мойки",
                    "volume": 500,
                    "relative_freq": 12.5,
                    "role": "secondary",
                },
                {
                    "phrase": "бесконтактная мойка",
                    "volume": 300,
                    "relative_freq": 7.5,
                    "role": "supporting",
                },
            ],
        }
        json_file = tmp_path / "test_old.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        rc = main([str(json_file)])
        out = capsys.readouterr().out
        assert rc == 0
        assert "Detected OLD structure" in out
        assert "активная пена" in out
        assert "primary" in out.lower()

    def test_old_structure_shows_statistics(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
        data = {
            "category_name_ru": "Test",
            "tier": "B",
            "keywords_detailed": [
                {"phrase": "kw1", "volume": 100, "relative_freq": 10.0, "role": "primary"},
                {"phrase": "kw2", "volume": 50, "relative_freq": 5.0, "role": "primary"},
                {"phrase": "kw3", "volume": 30, "relative_freq": 3.0, "role": "secondary"},
            ],
        }
        json_file = tmp_path / "test_stats.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        rc = main([str(json_file)])
        out = capsys.readouterr().out
        assert rc == 0
        assert "Primary" in out
        assert "Secondary" in out
        assert "Всего ключей: 3" in out


class TestNewStructureHandling:
    def test_parses_new_structure(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
        data = {
            "category_name_ru": "Активная пена",
            "tier": "A",
            "keywords": {
                "primary": [{"keyword": "активная пена", "occurrences_target": 15, "density_target": "2.5%"}],
                "secondary": [{"keyword": "пена для мойки", "occurrences_target": 8, "density_target": "1.2%"}],
                "supporting": [
                    {
                        "keyword": "бесконтактная мойка",
                        "occurrences_target": 4,
                        "density_target": "0.6%",
                    }
                ],
            },
        }
        json_file = tmp_path / "test_new.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        rc = main([str(json_file)])
        out = capsys.readouterr().out
        assert rc == 0
        assert "Detected NEW structure" in out
        assert "активная пена" in out

    def test_new_structure_converts_density(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
        data = {
            "category": "Test",
            "tier": "B",
            "keywords": {"primary": [{"keyword": "test keyword", "occurrences_target": 10, "density_target": "2.5%"}]},
        }
        json_file = tmp_path / "test_density.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        rc = main([str(json_file)])
        out = capsys.readouterr().out
        assert rc == 0
        assert "2.50" in out


class TestUnknownStructure:
    def test_unknown_structure_error(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
        json_file = tmp_path / "test_unknown.json"
        json_file.write_text(json.dumps({"some_field": "value"}), encoding="utf-8")

        rc = main([str(json_file)])
        out = capsys.readouterr().out
        assert rc == 1
        assert "unknown json structure" in out.lower()


class TestHelpers:
    def test_parse_density_percent_variants(self):
        assert _parse_density_percent(None) == 0.0
        assert _parse_density_percent(2) == 2.0
        assert _parse_density_percent(" 1.5% ") == 1.5
        assert _parse_density_percent("bad") == 0.0

    def test_new_structure_skips_non_dict_kw_obj_and_reports_no_keywords(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ):
        data = {
            "category": "Test",
            "tier": "B",
            "keywords": {"primary": ["not-a-dict"], "secondary": [], "supporting": []},
        }
        json_file = tmp_path / "bad_kw_obj.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        rc = main([str(json_file)])
        out = capsys.readouterr().out
        assert rc == 0
        assert "No keywords found" in out

    def test_format_stats_includes_optional_fields(self):
        data = {"max_volume": 123, "competitor_metadata": {"primary_serp_count": 9}}
        label, keywords = load_keywords(
            {
                "keywords_detailed": [
                    {"phrase": "kw", "volume": 1, "relative_freq": 0.5, "role": "primary"},
                ]
            }
        )
        assert "OLD structure" in label
        out = format_stats(data, keywords)
        assert "Max volume" in out
        assert "Primary SERP URLs" in out
