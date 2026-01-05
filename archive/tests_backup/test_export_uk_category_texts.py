from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

import scripts.export_uk_category_texts as exp


def _write_semantics(path: Path, l3_names: list[str]) -> None:
    rows = []
    for name in l3_names:
        rows.append([f"L3: {name}", "", ""])
        rows.append(["kw", "", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerows(rows)


class TestSlugOrdering:
    def test_get_slugs_in_order_from_semantics(self, tmp_path: Path, monkeypatch):
        root = tmp_path
        uk_categories = root / "uk" / "categories"
        uk_categories.mkdir(parents=True)

        # Only one folder exists, and it should be returned if present in semantics.
        (uk_categories / "slug-a").mkdir()
        semantics = root / "data" / "Структура  Ultimate финал - Лист2.csv"
        _write_semantics(semantics, ["Slug A", "Slug A", "Missing"])

        monkeypatch.setattr(exp, "ROOT", root)
        monkeypatch.setattr(exp, "UK_CATEGORIES_DIR", uk_categories)
        monkeypatch.setattr(exp, "SEMANTICS_CSV", semantics)
        monkeypatch.setattr(exp, "_slugify_l3", lambda s: "slug-a" if s == "Slug A" else "missing")

        assert exp.get_slugs_in_order() == ["slug-a"]

    def test_get_slugs_in_order_fallback_to_disk(self, tmp_path: Path, monkeypatch):
        root = tmp_path
        uk_categories = root / "uk" / "categories"
        uk_categories.mkdir(parents=True)
        (uk_categories / "b").mkdir()
        (uk_categories / "a").mkdir()

        monkeypatch.setattr(exp, "ROOT", root)
        monkeypatch.setattr(exp, "UK_CATEGORIES_DIR", uk_categories)
        monkeypatch.setattr(exp, "SEMANTICS_CSV", root / "nope.csv")

        assert exp.get_slugs_in_order() == ["a", "b"]

    def test_slugify_l3_uses_mapping_or_slugify(self):
        # Covers import path + both return branches inside _slugify_l3().
        assert exp._slugify_l3("Активная пена")  # known key in L3_TO_SLUG
        assert exp._slugify_l3("Новая категория")  # falls back to slugify()


class TestRowsAndCsv:
    def test_build_rows_reads_json_and_md(self, tmp_path: Path, monkeypatch):
        root = tmp_path
        uk_categories = root / "uk" / "categories"
        slug = "s1"
        (uk_categories / slug / "data").mkdir(parents=True)
        (uk_categories / slug / "content").mkdir(parents=True)

        (uk_categories / slug / "data" / f"{slug}_clean.json").write_text(
            json.dumps(
                {
                    "language": "uk",
                    "category_name_uk": "Назва",
                    "seo_titles": {
                        "h1": "H1",
                        "main_keyword": "kw",
                        "meta": {"title": "T", "description": "D"},
                    },
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        (uk_categories / slug / "content" / f"{slug}_uk.md").write_text(
            "# H1\n\ntext", encoding="utf-8"
        )

        monkeypatch.setattr(exp, "ROOT", root)
        monkeypatch.setattr(exp, "UK_CATEGORIES_DIR", uk_categories)

        rows = exp.build_rows([slug])
        assert rows[0]["slug"] == slug
        assert rows[0]["language"] == "uk"
        assert rows[0]["meta_title"] == "T"
        assert rows[0]["text_md"].endswith("\n")

    def test_build_rows_missing_files_raise(self, tmp_path: Path, monkeypatch):
        root = tmp_path
        uk_categories = root / "uk" / "categories"
        slug = "s1"
        (uk_categories / slug).mkdir(parents=True)

        monkeypatch.setattr(exp, "ROOT", root)
        monkeypatch.setattr(exp, "UK_CATEGORIES_DIR", uk_categories)

        with pytest.raises(SystemExit):
            exp.build_rows([slug])

    def test_build_rows_missing_content_raises(self, tmp_path: Path, monkeypatch):
        root = tmp_path
        uk_categories = root / "uk" / "categories"
        slug = "s1"
        (uk_categories / slug / "data").mkdir(parents=True)
        (uk_categories / slug / "data" / f"{slug}_clean.json").write_text(
            json.dumps({"seo_titles": {"meta": {}}, "language": "uk"}, ensure_ascii=False),
            encoding="utf-8",
        )

        monkeypatch.setattr(exp, "ROOT", root)
        monkeypatch.setattr(exp, "UK_CATEGORIES_DIR", uk_categories)

        with pytest.raises(SystemExit) as exc:
            exp.build_rows([slug])
        assert "Missing content" in str(exc.value)

    def test_write_csv_file_writes_header_and_rows(self, tmp_path: Path):
        out = tmp_path / "out.csv"
        exp.write_csv_file(
            out,
            [
                {
                    "slug": "s",
                    "language": "uk",
                    "category_name_uk": "",
                    "h1": "",
                    "main_keyword": "",
                    "meta_title": "",
                    "meta_description": "",
                    "text_md": "x\n",
                }
            ],
        )

        text = out.read_text(encoding="utf-8")
        assert "slug" in text
        assert '"s"' in text


class TestMain:
    def test_main_writes_output(
        self, tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]
    ):
        root = tmp_path
        uk_categories = root / "uk" / "categories"
        slug = "s1"
        (uk_categories / slug / "data").mkdir(parents=True)
        (uk_categories / slug / "content").mkdir(parents=True)
        (uk_categories / slug / "data" / f"{slug}_clean.json").write_text(
            json.dumps({"seo_titles": {"meta": {}}, "language": "uk"}, ensure_ascii=False),
            encoding="utf-8",
        )
        (uk_categories / slug / "content" / f"{slug}_uk.md").write_text("text", encoding="utf-8")

        monkeypatch.setattr(exp, "ROOT", root)
        monkeypatch.setattr(exp, "UK_CATEGORIES_DIR", uk_categories)
        monkeypatch.setattr(exp, "SEMANTICS_CSV", root / "nope.csv")

        out_path = root / "uk" / "data" / "output" / "x.csv"
        rc = exp.main(["--output", str(out_path)])
        assert rc == 0
        assert out_path.exists()
        assert "Wrote 1 rows" in capsys.readouterr().out

    def test_main_raises_when_no_categories(self, tmp_path: Path, monkeypatch):
        root = tmp_path
        uk_categories = root / "uk" / "categories"
        uk_categories.mkdir(parents=True)

        monkeypatch.setattr(exp, "ROOT", root)
        monkeypatch.setattr(exp, "UK_CATEGORIES_DIR", uk_categories)
        monkeypatch.setattr(exp, "SEMANTICS_CSV", root / "nope.csv")

        with pytest.raises(SystemExit):
            exp.main([])


def test_iter_slugs_from_semantics_csv_skips_empty_rows(tmp_path: Path):
    csv_path = tmp_path / "s.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([])
        w.writerow(["L3: Активная пена"])

    slugs = list(exp.iter_slugs_from_semantics_csv(csv_path))
    assert slugs  # at least one slug from L3 line
