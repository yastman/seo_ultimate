#!/usr/bin/env python3
"""
TDD tests for scripts/generate_sql.py — MD → HTML + OpenCart SQL generator.

Scope:
- md_to_html basics (H1 extraction, headers, lists, tables, links)
- escape_sql correctness
- generate_update_sql uses meta JSON if present
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.generate_sql as gen


class TestMdToHtml:
    def test_extracts_h1_and_removes_from_body(self):
        h1, html = gen.md_to_html("# Заголовок\n\nТекст\n")
        assert h1 == "Заголовок"
        assert "Заголовок" not in html
        assert "<p>Текст</p>" in html

    def test_converts_h2_h3_bold_italic_code_link(self):
        md = "\n".join(
            [
                "# H1",
                "## H2",
                "### H3",
                "**bold** *italic* `code`",
                "[link](/slug)",
            ]
        )
        _h1, html = gen.md_to_html(md)
        assert "<h2>H2</h2>" in html
        assert "<h3>H3</h3>" in html
        assert "<strong>bold</strong>" in html
        assert "<em>italic</em>" in html
        assert "<code>code</code>" in html
        assert '<a href="/slug">link</a>' in html

    def test_converts_lists(self):
        md = "\n".join(
            [
                "# H1",
                "- a",
                "- b",
                "1. c",
                "2. d",
            ]
        )
        _h1, html = gen.md_to_html(md)
        assert "<ul>" in html and "</ul>" in html
        assert "<ol>" in html and "</ol>" in html
        assert "<li>a</li>" in html
        assert "<li>d</li>" in html

    def test_converts_simple_table(self):
        md = "\n".join(
            [
                "# H1",
                "| A | B |",
                "|---|---|",
                "| 1 | 2 |",
            ]
        )
        _h1, html = gen.md_to_html(md)
        assert "<table>" in html
        assert "<th>A</th>" in html
        assert "<td>2</td>" in html

    def test_convert_tables_closes_table_on_non_table_line(self):
        content = "\n".join(
            [
                "| A | B |",
                "|---|---|",
                "| 1 | 2 |",
                "after",
            ]
        )
        out = gen.convert_tables(content)
        assert "<table>" in out
        assert "after" in out
    
    def test_build_html_table_returns_original_for_short_input(self):
        # build_html_table() returns input if there isn't a real table.
        assert gen.build_html_table(["| A | B |"]) == "| A | B |"

    def test_convert_lists_closes_tags_before_plain_text(self):
        md = "\n".join(
            [
                "<h2>H2</h2>",
                "- a",
                "- b",
                "plain",
            ]
        )
        html = gen.convert_lists(md)
        assert "</ul>" in html
        assert "plain" in html

    def test_convert_lists_switches_between_ol_and_ul(self):
        content = "\n".join(
            [
                "1. a",
                "2. b",
                "- c",
                "- d",
                "end",
            ]
        )
        out = gen.convert_lists(content)
        # switching from OL to UL must close </ol>
        assert "</ol>" in out
        assert "<ul>" in out
        # leaving lists for plain text must close </ul>
        assert "</ul>" in out
        assert "end" in out

    def test_convert_lists_closes_ol_on_plain_text(self):
        out = gen.convert_lists("1. a\n2. b\nplain")
        assert "</ol>" in out
        assert "plain" in out

    def test_convert_lists_closes_ul_at_eof(self):
        out = gen.convert_lists("- a\n- b")
        assert out.strip().endswith("</ul>")

    def test_convert_lists_switches_from_ul_to_ol(self):
        out = gen.convert_lists("- a\n- b\n1. c\n2. d\nend")
        assert "</ul>" in out
        assert "<ol>" in out
        assert "</ol>" in out


class TestEscapeSql:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("", ""),
            ("a'b", "a\\'b"),
            ('a"b', 'a\\"b'),
            ("a\\b", "a\\\\b"),
        ],
    )
    def test_escape_sql(self, raw: str, expected: str):
        assert gen.escape_sql(raw) == expected


class TestGenerateUpdateSql:
    def test_generate_update_sql_missing_content_returns_warning_comment(self, tmp_path: Path, monkeypatch):
        slug = "missing"
        project_dir = tmp_path
        monkeypatch.setattr(gen, "PROJECT_DIR", project_dir)
        sql = gen.generate_update_sql(slug, 1)
        assert "Нет контента" in sql

    def test_generate_update_sql_includes_meta(self, tmp_path: Path, monkeypatch):
        # Arrange: temporary project structure
        slug = "test-slug"
        cat_id = 123
        project_dir = tmp_path

        (project_dir / "categories" / slug / "content").mkdir(parents=True)
        (project_dir / "categories" / slug / "meta").mkdir(parents=True)

        (project_dir / "categories" / slug / "content" / f"{slug}_ru.md").write_text(
            "# H1\n\n## H2\n\nТекст\n",
            encoding="utf-8",
        )

        (project_dir / "categories" / slug / "meta" / f"{slug}_meta.json").write_text(
            json.dumps(
                {
                    "meta": {
                        "title": "Title text",
                        "description": "Description text",
                    }
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        monkeypatch.setattr(gen, "PROJECT_DIR", project_dir)

        # Act
        sql = gen.generate_update_sql(slug, cat_id)

        # Assert
        assert f"category_id: {cat_id}" in sql
        assert "`meta_title`" in sql and "Title text" in sql
        assert "`meta_description`" in sql and "Description text" in sql
        assert "`meta_h1`" in sql and "H1" in sql
        assert "<h2>H2</h2>" in sql

    def test_generate_update_sql_handles_missing_meta_file(self, tmp_path: Path, monkeypatch):
        slug = "test-slug"
        cat_id = 123
        project_dir = tmp_path

        (project_dir / "categories" / slug / "content").mkdir(parents=True)
        (project_dir / "categories" / slug / "content" / f"{slug}_ru.md").write_text(
            "# H1\n\nText\n",
            encoding="utf-8",
        )

        monkeypatch.setattr(gen, "PROJECT_DIR", project_dir)
        sql = gen.generate_update_sql(slug, cat_id)
        assert "`meta_title`" in sql
        assert "`meta_description`" in sql


class TestTableHelpers:
    def test_is_table_separator_empty_returns_false(self):
        assert gen._is_table_separator("|||") is False

    def test_build_html_table_returns_original_for_invalid_separator(self):
        lines = ["| A | B |", "sep", "| 1 | 2 |"]
        assert gen.build_html_table(lines) == "\n".join(lines)

    def test_build_html_table_returns_original_for_invalid_row(self):
        lines = ["| A | B |", "|---|---|", "row"]
        assert gen.build_html_table(lines) == "\n".join(lines)


class TestMain:
    def test_main_writes_output_file(self, tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]):
        slug = "test-slug"
        cat_id = 1

        project_dir = tmp_path
        out_file = tmp_path / "content_updates.sql"

        (project_dir / "categories" / slug / "content").mkdir(parents=True)
        (project_dir / "categories" / slug / "meta").mkdir(parents=True)

        (project_dir / "categories" / slug / "content" / f"{slug}_ru.md").write_text(
            "# H1\n\n## H2\n\nText\n",
            encoding="utf-8",
        )
        (project_dir / "categories" / slug / "meta" / f"{slug}_meta.json").write_text(
            json.dumps({"meta": {"title": "T", "description": "D"}}, ensure_ascii=False),
            encoding="utf-8",
        )

        monkeypatch.setattr(gen, "PROJECT_DIR", project_dir)
        monkeypatch.setattr(gen, "OUTPUT_FILE", out_file)
        monkeypatch.setattr(gen, "CATEGORY_MAP", {slug: cat_id})

        gen.main()
        out = capsys.readouterr().out
        assert out_file.exists()
        assert "SQL сохранён" in out
        assert "UPDATE `oc_category_description`" in out_file.read_text(encoding="utf-8")
