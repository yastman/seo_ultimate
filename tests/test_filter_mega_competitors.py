"""
Tests for filter_mega_competitors.py — MEGA CSV filtering per category

Tests cover:
1. Keyword loading from category JSON
2. URL mapping loading
3. Filtering rows + output generation (end-to-end)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import scripts.filter_mega_competitors as mod


class TestKeywordLoading:
    def test_load_category_keywords_supports_dict_and_string(self, tmp_path: Path):
        data = {
            "keywords": {
                "primary": [{"keyword": "Активная пена", "volume": 1000}, "пена для мойки"],
                "secondary": [{"text": "бесконтактная мойка"}],
                "supporting": [],
            }
        }
        json_file = tmp_path / "cat.json"
        json_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        keywords = mod.load_category_keywords(json_file, max_keywords=10)
        assert "активная пена" in keywords
        assert "пена для мойки" in keywords
        assert "бесконтактная мойка" in keywords


class TestUrlMapping:
    def test_load_url_mapping_filters_by_slug(self, tmp_path: Path):
        map_file = tmp_path / "mega_urls_map.csv"
        with map_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["slug", "url"])
            writer.writeheader()
            writer.writerow({"slug": "a", "url": "https://a.com/x"})
            writer.writerow({"slug": "b", "url": "https://b.com/y"})
            writer.writerow({"slug": "a", "url": "https://a.com/z"})

        urls = mod.load_url_mapping(map_file, "a")
        assert urls == {"https://a.com/x", "https://a.com/z"}


class TestEndToEnd:
    def test_filters_and_writes_outputs(self, tmp_path: Path, monkeypatch):
        category_slug = "test-slug"
        cat_dir = tmp_path / "categories" / category_slug
        (cat_dir / "data").mkdir(parents=True)
        (cat_dir / "competitors").mkdir()

        category_json = {
            "tier": "B",
            "keywords": {
                "primary": [{"keyword": "активная пена", "volume": 1000}],
                "secondary": [{"keyword": "пена для мойки", "volume": 500}],
                "supporting": [],
            },
        }
        data_json = tmp_path / "cat.json"
        data_json.write_text(json.dumps(category_json, ensure_ascii=False), encoding="utf-8")

        mega_csv = tmp_path / "mega.csv"
        with mega_csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Address",
                    "Status Code",
                    "Title 1",
                    "H1-1",
                    "Meta Description 1",
                    "H2-1",
                    "H2-2",
                    "H2-3",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "Address": "https://shop1.com/catalog/pena",
                    "Status Code": "200",
                    "Title 1": "Активная пена для бесконтактной мойки",
                    "H1-1": "Активная пена",
                    "Meta Description 1": "Купить активную пену",
                    "H2-1": "Преимущества",
                    "H2-2": "Как использовать",
                    "H2-3": "",
                }
            )
            writer.writerow(
                {
                    "Address": "https://shop2.com/contact",
                    "Status Code": "200",
                    "Title 1": "Контакты",
                    "H1-1": "Контакты",
                    "Meta Description 1": "",
                    "H2-1": "",
                    "H2-2": "",
                    "H2-3": "",
                }
            )
            writer.writerow(
                {
                    "Address": "https://rozetka.com.ua/catalog/pena",
                    "Status Code": "200",
                    "Title 1": "Активная пена",
                    "H1-1": "Активная пена",
                    "Meta Description 1": "",
                    "H2-1": "",
                    "H2-2": "",
                    "H2-3": "",
                }
            )

        # Make main ignore repo-level mega_urls_map.csv for this test.
        monkeypatch.setattr(mod, "load_url_mapping", lambda *_a, **_k: set())

        # Run main() with argv via sys.argv monkeypatch (script-style).
        monkeypatch.setattr(
            mod.sys,
            "argv",
            [
                "filter_mega_competitors.py",
                category_slug,
                "--mega-csv",
                str(mega_csv),
                "--data-json",
                str(data_json),
                "--output-dir",
                str(cat_dir / "competitors"),
                "--min-competitors",
                "1",
                "--min-h2-themes",
                "1",
            ],
        )

        rc = mod.main()
        assert rc in (0, 1)  # depending on heuristics, but should not be FAIL

        output_csv = cat_dir / "competitors" / "meta_competitors.csv"
        output_json = cat_dir / "competitors" / "meta_patterns.json"
        assert output_csv.exists()
        assert output_json.exists()

        rows = list(csv.DictReader(output_csv.open("r", encoding="utf-8")))
        assert any("shop1.com" in r["Address"] for r in rows)
        assert all("rozetka.com.ua" not in r["Address"] for r in rows)
