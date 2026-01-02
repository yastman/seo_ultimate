from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import sys

import pytest

import scripts.check_h1_sync as h1sync


class TestExtractH1FromMd:
    def test_missing_file_returns_none(self, tmp_path: Path):
        assert h1sync.extract_h1_from_md(tmp_path / "nope.md") is None

    def test_extracts_first_h1(self, tmp_path: Path):
        md = tmp_path / "a.md"
        md.write_text("# H1\n\n## H2\n# Not H1 (still a header)\n", encoding="utf-8")
        assert h1sync.extract_h1_from_md(md) == "H1"


class TestGetH1FromJson:
    def test_missing_file_returns_none(self, tmp_path: Path):
        assert h1sync.get_h1_from_json(tmp_path / "nope.json") is None

    def test_reads_h1_field(self, tmp_path: Path):
        p = tmp_path / "m.json"
        p.write_text(json.dumps({"h1": "X"}, ensure_ascii=False), encoding="utf-8")
        assert h1sync.get_h1_from_json(p) == "X"

    def test_falls_back_to_meta_h1(self, tmp_path: Path):
        p = tmp_path / "m.json"
        p.write_text(json.dumps({"meta_h1": "Y"}, ensure_ascii=False), encoding="utf-8")
        assert h1sync.get_h1_from_json(p) == "Y"

    def test_invalid_json_returns_none(self, tmp_path: Path):
        p = tmp_path / "bad.json"
        p.write_text("{", encoding="utf-8")
        assert h1sync.get_h1_from_json(p) is None


class TestCheckSync:
    def test_check_sync_counts_and_prints(self, tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]):
        categories = tmp_path / "categories"
        categories.mkdir()

        # Non-dir entry must be skipped.
        (categories / "README.txt").write_text("x", encoding="utf-8")

        # Missing MD → skipped.
        (categories / "missing-md").mkdir()

        # MD without H1 → counted as missing + warning printed.
        slug_no_h1 = "no-h1"
        (categories / slug_no_h1 / "content").mkdir(parents=True)
        (categories / slug_no_h1 / "meta").mkdir(parents=True)
        (categories / slug_no_h1 / "content" / f"{slug_no_h1}_ru.md").write_text(
            "text only",
            encoding="utf-8",
        )
        (categories / slug_no_h1 / "meta" / f"{slug_no_h1}_meta.json").write_text(
            json.dumps({"h1": "X"}, ensure_ascii=False),
            encoding="utf-8",
        )

        # MD + missing JSON (or missing field) → skipped.
        slug_no_json = "no-json"
        (categories / slug_no_json / "content").mkdir(parents=True)
        (categories / slug_no_json / "content" / f"{slug_no_json}_ru.md").write_text(
            "# H1\n",
            encoding="utf-8",
        )

        # Synced category.
        slug_ok = "ok"
        (categories / slug_ok / "content").mkdir(parents=True)
        (categories / slug_ok / "meta").mkdir(parents=True)
        (categories / slug_ok / "content" / f"{slug_ok}_ru.md").write_text("# Same\n", encoding="utf-8")
        (categories / slug_ok / "meta" / f"{slug_ok}_meta.json").write_text(
            json.dumps({"h1": "Same"}, ensure_ascii=False),
            encoding="utf-8",
        )

        # Mismatch category.
        slug_bad = "bad"
        (categories / slug_bad / "content").mkdir(parents=True)
        (categories / slug_bad / "meta").mkdir(parents=True)
        (categories / slug_bad / "content" / f"{slug_bad}_ru.md").write_text("# New H1\n", encoding="utf-8")
        (categories / slug_bad / "meta" / f"{slug_bad}_meta.json").write_text(
            json.dumps({"h1": "Old H1", "meta_h1": "Old H1"}, ensure_ascii=False),
            encoding="utf-8",
        )

        monkeypatch.setattr(h1sync, "CATEGORIES_DIR", categories)

        h1sync.check_sync(fix=False)
        out = capsys.readouterr().out
        assert "❌ bad" in out
        assert "👉 Используйте --fix" in out
        assert "H1 не найден" in out

    def test_check_sync_fix_updates_json(self, tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]):
        categories = tmp_path / "categories"
        slug = "cat"

        (categories / slug / "content").mkdir(parents=True)
        (categories / slug / "meta").mkdir(parents=True)
        md_path = categories / slug / "content" / f"{slug}_ru.md"
        json_path = categories / slug / "meta" / f"{slug}_meta.json"

        md_path.write_text("#  New   H1  \n", encoding="utf-8")
        json_path.write_text(
            json.dumps({"h1": "Old H1", "meta_h1": "Old H1"}, ensure_ascii=False),
            encoding="utf-8",
        )

        monkeypatch.setattr(h1sync, "CATEGORIES_DIR", categories)

        h1sync.check_sync(fix=True)
        out = capsys.readouterr().out
        assert "✅ FIXED" in out

        updated = json.loads(json_path.read_text(encoding="utf-8"))
        assert updated["h1"] == "New H1"
        assert updated["meta_h1"] == "New H1"

    def test_check_sync_fix_error_is_reported(self, tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]):
        categories = tmp_path / "categories"
        slug = "cat"

        (categories / slug / "content").mkdir(parents=True)
        (categories / slug / "meta").mkdir(parents=True)
        (categories / slug / "content" / f"{slug}_ru.md").write_text("# H1\n", encoding="utf-8")
        json_path = categories / slug / "meta" / f"{slug}_meta.json"
        json_path.write_text(json.dumps({"h1": "Old"}, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(h1sync, "CATEGORIES_DIR", categories)

        # First json.loads is in get_h1_from_json (needs to succeed),
        # second is in the fix branch (force it to fail).
        real_loads = h1sync.json.loads
        calls = {"n": 0}

        def loads_twice(s: str):
            calls["n"] += 1
            if calls["n"] >= 2:
                raise RuntimeError("boom")
            return real_loads(s)

        monkeypatch.setattr(h1sync.json, "loads", loads_twice)

        h1sync.check_sync(fix=True)
        out = capsys.readouterr().out
        assert "ERROR fixing" in out

    def test_import_fallback_branch_executes_without_config(self):
        # Full suite adds `scripts/` into sys.path in a few places, so force a
        # separate import where `import config` fails and the fallback branch runs.
        scripts_dir = Path(__file__).parent.parent / "scripts"
        check_path = scripts_dir / "check_h1_sync.py"

        old_path = list(sys.path)
        try:
            sys.path = [p for p in sys.path if Path(p).resolve() != scripts_dir.resolve()]
            sys.modules.pop("config", None)

            spec = importlib.util.spec_from_file_location("_h1sync_no_config", check_path)
            assert spec and spec.loader
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            assert str(mod.CATEGORIES_DIR).endswith("categories")
        finally:
            sys.path = old_path
