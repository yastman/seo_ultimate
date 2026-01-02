from __future__ import annotations

import json
import runpy
import sys
import types
from pathlib import Path

import pytest

import scripts.quality_runner as qr
import builtins


def _write_md(tmp_path: Path, text: str = "# H1\n\nintro text\n\n## H2\nbody\n") -> Path:
    p = tmp_path / "x.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_script_standalone_inserts_project_root(monkeypatch):
    script_path = Path(__file__).parent.parent / "scripts" / "quality_runner.py"
    monkeypatch.setattr(sys, "argv", ["quality_runner.py"])
    monkeypatch.setattr(sys, "path", ["__sentinel__"])

    with pytest.raises(SystemExit):
        code = script_path.read_text(encoding="utf-8")
        exec(compile(code, str(script_path), "exec"), {"__name__": "__main__", "__package__": None, "__file__": str(script_path)})

    assert sys.path[0] == str(script_path.resolve().parent.parent)


def test_markdown_warn_prints_and_more_than_5(monkeypatch, tmp_path: Path, capsys):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)

    class Failure:
        def __init__(self, n: int):
            self.scan_file = "x.md"
            self.line_number = n
            self.column_number = 1
            self.rule_id = "MD000"
            self.rule_description = "desc"

    class FakeScanResult:
        scan_failures = [Failure(i) for i in range(6)]

    class FakeApi:
        def scan_path(self, _path):
            return FakeScanResult()

    monkeypatch.setitem(qr.sys.modules, "pymarkdown.api", types.SimpleNamespace(PyMarkdownApi=FakeApi))

    status, _errors = checker.check_markdown_structure()
    out = capsys.readouterr().out
    assert status == "WARN"
    assert "... and 1 more" in out


def test_check_grammar_skipped_branch(tmp_path: Path):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)
    status, errors = checker.check_grammar()
    assert status == "PASS"
    assert errors == []


def test_check_grammar_no_matches_branch(monkeypatch, tmp_path: Path):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_water=True, skip_ner=True)

    class FakeTool:
        def check(self, _text):
            return []

    fake_mod = types.SimpleNamespace(LanguageTool=lambda _lang: FakeTool())
    monkeypatch.setitem(qr.sys.modules, "language_tool_python", fake_mod)

    status, errors = checker.check_grammar()
    assert status == "PASS"
    assert errors == []


def test_check_grammar_more_than_5_errors_prints_summary(monkeypatch, tmp_path: Path, capsys):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_water=True, skip_ner=True)

    class Match:
        def __init__(self, n: int):
            self.context = f"ctx{n}"
            self.message = f"m{n}"
            self.ruleId = f"R{n}"
            self.replacements = ["a", "b", "c"]

    class FakeTool:
        def check(self, _text):
            return [Match(i) for i in range(6)]

    fake_mod = types.SimpleNamespace(LanguageTool=lambda _lang: FakeTool())
    monkeypatch.setitem(qr.sys.modules, "language_tool_python", fake_mod)

    status, _errors = checker.check_grammar()
    out = capsys.readouterr().out
    assert status == "WARN"
    assert "... and 1 more" in out


def test_check_water_nausea_warn_branch(monkeypatch, tmp_path: Path):
    md = _write_md(tmp_path, "# H1\n\nтест\n")
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_ner=True)

    import scripts.check_water_natasha as cwn
    import scripts.seo_utils as su

    monkeypatch.setattr(
        cwn,
        "calculate_metrics_from_text",
        lambda _t: {"water_percent": 64.0, "classic_nausea": 3.6, "academic_nausea": 8.0, "lemma_repetition_index": 0.0},
    )
    monkeypatch.setattr(
        su,
        "get_tier_requirements",
        lambda _tier: {
            "water_min": 40.0,
            "water_max": 60.0,
            "water_blocker_low": 30.0,
            "water_blocker_high": 70.0,
            "nausea_classic_max": 3.5,
            "nausea_classic_blocker": 4.0,
            "nausea_academic_min": 7.0,
            "nausea_academic_max": 9.5,
        },
    )

    status, _metrics = checker.check_water_nausea()
    assert status == "WARN"


def test_check_keyword_density_prints_warnings_count(monkeypatch, tmp_path: Path, capsys):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)

    json_path = md.parent / f"{md.stem}_validation.json"
    json_path.write_text(
        json.dumps({"checks": {"density_distribution": {"metrics": {"total_density": 1.0, "coverage": 55.0, "keywords_found": 1, "keywords_total": 2, "warnings_count": 2, "errors_count": 0}}}}),
        encoding="utf-8",
    )

    monkeypatch.setattr(qr.subprocess, "run", lambda *_a, **_k: types.SimpleNamespace(returncode=1, stdout="", stderr=""))
    status, _metrics = checker.check_keyword_density()
    out = capsys.readouterr().out
    assert status == "WARN"
    assert "Warnings: 2" in out


def test_check_keyword_density_exception_branch(monkeypatch, tmp_path: Path):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)

    monkeypatch.setattr(qr.subprocess, "run", lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")))
    status, _metrics = checker.check_keyword_density()
    assert status == "FAIL"


def test_check_ner_blacklist_prints_more_than_3_items(monkeypatch, tmp_path: Path, capsys):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=False)

    import scripts.check_ner_brands as ner_mod

    monkeypatch.setattr(
        ner_mod,
        "check_blacklist",
        lambda _t: {
            "brands": [{"entity": f"b{i}"} for i in range(4)],
            "cities": [{"entity": f"c{i}"} for i in range(4)],
            "ai_fluff": [{"entity": f"a{i}"} for i in range(4)],
            "strict_phrases": [],
        },
    )
    monkeypatch.setattr(
        ner_mod,
        "check_ner",
        lambda _t: {"ner_entities": [{"type": "ORG", "entity": "x"}, {"type": "LOC", "entity": "y"}]},
    )

    status, _findings = checker.check_ner_blacklist()
    out = capsys.readouterr().out
    assert status == "WARN"
    assert "... и ещё" in out
    assert "NER обнаружил" in out


def test_parse_density_text_fallback_extracts_metrics(tmp_path: Path):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)
    metrics = checker._parse_density_text_fallback("Density: 1.2%\nCoverage: 55.0%\n")
    assert metrics["density"] == 1.2
    assert metrics["coverage"] == 55.0


def test_check_commercial_markers_prints_more_than_6(monkeypatch, tmp_path: Path, capsys):
    md = _write_md(tmp_path, "# H1\n\nкупить цена доставка заказать в наличии магазин каталог\n")
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)

    import scripts.seo_utils as su

    monkeypatch.setattr(su, "get_tier_requirements", lambda _t: {"commercial_min": 1})
    monkeypatch.setattr(
        su,
        "check_commercial_markers",
        lambda _t, _min: {"passed": True, "found_count": 7, "found_markers": [f"m{i}" for i in range(7)], "message": "ok"},
    )

    status, _result = checker.check_commercial_markers()
    out = capsys.readouterr().out
    assert status == "PASS"
    assert "... и ещё 1" in out


def test_check_commercial_markers_importerror_branch(monkeypatch, tmp_path: Path):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)

    real_import = builtins.__import__

    def fail_seo_utils(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "scripts.seo_utils":
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fail_seo_utils)
    status, _result = checker.check_commercial_markers()
    assert status == "WARN"


def test_check_seo_structure_print_branches(monkeypatch, tmp_path: Path, capsys):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)

    import scripts.check_seo_structure as ss

    monkeypatch.setattr(
        ss,
        "check_seo_structure",
        lambda *_a, **_k: (
            "PASS",
            {
                "intro": {"passed": True, "in_first_sentence": False, "message": "m", "intro_preview": "x"},
                "h2": {"passed": True, "message": "m", "h2_with_keyword": ["a"], "h2_without_keyword": []},
                "frequency": {"status": "SPAM", "is_spam": True, "message": "m"},
            },
        ),
    )
    status, _res = checker.check_seo_structure()
    out = capsys.readouterr().out
    assert status == "PASS"
    assert "Лучше переместить keyword" in out
    assert "✓ С keyword" in out


def test_check_keyword_density_script_missing_returns_fail(monkeypatch, tmp_path: Path, capsys):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)

    expected_script_path = Path(qr.__file__).resolve().parent / "check_simple_v2_md.py"
    real_exists = qr.Path.exists

    def fake_exists(self) -> bool:  # type: ignore[no-untyped-def]
        if self == expected_script_path:
            return False
        return real_exists(self)

    monkeypatch.setattr(qr.Path, "exists", fake_exists, raising=False)

    status, _metrics = checker.check_keyword_density()
    out = capsys.readouterr().out
    assert status == "FAIL"
    assert "Script not found" in out


def test_check_ner_blacklist_skip_ner_branch(tmp_path: Path, capsys):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)

    status, findings = checker.check_ner_blacklist()
    out = capsys.readouterr().out
    assert status == "PASS"
    assert findings == {}
    assert "SKIPPED" in out


def test_check_seo_structure_importerror_branch(monkeypatch, tmp_path: Path):
    md = _write_md(tmp_path)
    checker = qr.QualityCheck(str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True)

    real_import = builtins.__import__

    def fail_check_seo_structure(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "scripts.check_seo_structure":
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fail_check_seo_structure)
    status, _res = checker.check_seo_structure()
    assert status == "FAIL"


def test_main_writes_report_file(tmp_path: Path, monkeypatch):
    md = _write_md(tmp_path)

    monkeypatch.setattr(qr.QualityCheck, "run_all_checks", lambda self: 0)
    monkeypatch.setattr(qr.QualityCheck, "results", {"ok": True}, raising=False)

    rc = qr.main([str(md), "intro", "B"])
    assert rc == 0
    assert (tmp_path / f"{md.stem}_quality_report.json").exists()


def test_main_exception_branch_prints_to_stderr(capsys):
    rc = qr.main(["/no/such.md", "kw", "B"])
    assert rc == 2
    assert "ERROR:" in capsys.readouterr().err
