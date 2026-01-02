from __future__ import annotations

import builtins
import importlib.util
import json
import sys
from pathlib import Path

import pytest

import scripts.audit_content as audit


class TestCheckMetaQuality:
    def test_missing_file(self, tmp_path: Path):
        res = audit.check_meta_quality(tmp_path / "nope.json")
        assert res["status"] == "MISSING"

    def test_invalid_json(self, tmp_path: Path):
        p = tmp_path / "bad.json"
        p.write_text("{", encoding="utf-8")
        res = audit.check_meta_quality(p)
        assert res["status"] == "ERROR"

    def test_empty_title_and_description(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(audit, "COMMERCIAL_MODIFIERS", ["купить"])

        p = tmp_path / "m.json"
        p.write_text(
            json.dumps({"meta": {"title": "", "description": ""}}, ensure_ascii=False),
            encoding="utf-8",
        )
        res = audit.check_meta_quality(p)
        assert res["status"] == "FAIL"
        assert "Empty Title" in res["issues"]
        assert "Empty Description" in res["issues"]

    def test_length_and_commercial_marker_checks(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(audit, "COMMERCIAL_MODIFIERS", ["купить"])

        p = tmp_path / "m.json"
        p.write_text(
            json.dumps(
                {
                    "meta": {
                        "title": "Очень коротко",
                        "description": "d" * 200,
                    }
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        res = audit.check_meta_quality(p)
        assert res["status"] == "FAIL"
        assert any("Short Title" in s for s in res["issues"])
        assert any("Title: Нет коммерческих маркеров" in s for s in res["issues"])
        assert any("Long Description" in s for s in res["issues"])

    def test_long_title_and_short_description(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(audit, "COMMERCIAL_MODIFIERS", ["купить"])

        p = tmp_path / "m.json"
        p.write_text(
            json.dumps(
                {
                    "meta": {
                        "title": "Купить " + ("x" * 80),
                        "description": "x" * 100,
                    }
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        res = audit.check_meta_quality(p)
        assert any("Long Title" in s for s in res["issues"])
        assert any("Short Description" in s for s in res["issues"])

    def test_ok_when_in_ranges_and_has_marker(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(audit, "COMMERCIAL_MODIFIERS", ["купить"])

        p = tmp_path / "m.json"
        p.write_text(
            json.dumps(
                {"meta": {"title": "Купить хороший товар в наличии", "description": "x" * 140}},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        res = audit.check_meta_quality(p)
        assert res["status"] == "OK"
        assert res["issues"] == []


class TestCheckContentQuality:
    def test_missing_file(self, tmp_path: Path):
        res = audit.check_content_quality(tmp_path / "nope.md")
        assert res["status"] == "MISSING"

    def test_detects_table_and_ai_fluff(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(
            audit, "AI_FLUFF_PATTERNS", [r"в современном мире", r"давайте разберемся"]
        )

        p = tmp_path / "t.md"
        p.write_text(
            "# H1\n\nВ современном мире...\n\n| A | B |\n|---|---|\n| 1 | 2 |\n",
            encoding="utf-8",
        )
        res = audit.check_content_quality(p)
        assert res["status"] == "WARNING"
        assert res["has_table"] is True
        assert any("стоп-фразы" in s.lower() for s in res["issues"])

    def test_no_table_when_no_pipes(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr(audit, "AI_FLUFF_PATTERNS", [])

        p = tmp_path / "t.md"
        p.write_text("# H1\n\nJust text\n", encoding="utf-8")
        res = audit.check_content_quality(p)
        assert res["status"] == "OK"
        assert res["has_table"] is False


class TestMain:
    def test_main_prints_report(
        self, tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]
    ):
        categories = tmp_path / "categories"
        categories.mkdir()

        # Hidden dir is ignored.
        (categories / ".hidden").mkdir()

        # Create a category with a long issues string (to hit truncation branch).
        slug_bad = "cat-bad"
        (categories / slug_bad / "content").mkdir(parents=True)
        (categories / slug_bad / "meta").mkdir(parents=True)
        (categories / slug_bad / "content" / f"{slug_bad}_ru.md").write_text(
            "# H1\n", encoding="utf-8"
        )
        (categories / slug_bad / "meta" / f"{slug_bad}_meta.json").write_text(
            json.dumps({"meta": {"title": "", "description": ""}}, ensure_ascii=False),
            encoding="utf-8",
        )

        # OK category (covers issues_str = "✅ OK").
        slug_ok = "cat-ok"
        (categories / slug_ok / "content").mkdir(parents=True)
        (categories / slug_ok / "meta").mkdir(parents=True)
        (categories / slug_ok / "content" / f"{slug_ok}_ru.md").write_text(
            "# H1\n", encoding="utf-8"
        )
        (categories / slug_ok / "meta" / f"{slug_ok}_meta.json").write_text(
            json.dumps(
                {"meta": {"title": "Купить отличный товар в наличии", "description": "x" * 140}},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        monkeypatch.setattr(audit, "CATEGORIES_DIR", categories)
        monkeypatch.setattr(audit, "COMMERCIAL_MODIFIERS", ["купить"])
        monkeypatch.setattr(audit, "AI_FLUFF_PATTERNS", [r"в современном мире"])

        audit.main()
        out = capsys.readouterr().out
        assert "Аудит контента" in out
        assert "Slug" in out
        assert "Итог:" in out


def test_module_import_fallback_branch_executes_without_config(monkeypatch):
    # Cover ImportError fallback at import time (lines 25-30).
    scripts_dir = Path(__file__).parent.parent / "scripts"
    path = scripts_dir / "audit_content.py"

    real_import = builtins.__import__

    def failing_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "config":
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", failing_import)
    sys.modules.pop("config", None)

    spec = importlib.util.spec_from_file_location("_audit_no_config", path)
    assert spec
    assert spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    assert isinstance(mod.COMMERCIAL_MODIFIERS, list)
