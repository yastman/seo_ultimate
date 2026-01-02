"""
TDD tests for scripts/quality_runner.py (in-process, coverage-friendly).

Covers:
- markdown/grammar/water/keywords/ner/commercial/seo_structure branches
- run_all_checks exit codes
- main(argv) error handling
"""

from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

import scripts.quality_runner as qr


def _write_md(tmp_path: Path, text: str = "# H1\n\nintro text\n\n## H2\nbody\n") -> Path:
    p = tmp_path / "x.md"
    p.write_text(text, encoding="utf-8")
    return p


class TestMain:
    def test_main_missing_args_raises(self):
        with pytest.raises(SystemExit) as exc:
            qr.main([])
        assert exc.value.code == 2

    def test_main_success_no_write_report(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nintro\n")

        class Dummy:
            def __init__(self, *_a, **_k):
                self.results = {"ok": True}

            def run_all_checks(self):
                return 0

        monkeypatch.setattr(qr, "QualityCheck", Dummy)

        rc = qr.main(
            [
                str(md),
                "intro",
                "B",
                "--no-write-report",
                "--skip-grammar",
                "--skip-water",
                "--skip-ner",
            ]
        )
        assert rc == 0


class TestMarkdownCheck:
    def test_markdown_pass_via_pymarkdown_api(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path)
        checker = qr.QualityCheck(
            str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        class FakeScanResult:
            scan_failures: list = []

        class FakeApi:
            def scan_path(self, _path):
                return FakeScanResult()

        fake_mod = types.SimpleNamespace(PyMarkdownApi=FakeApi)
        monkeypatch.setitem(qr.sys.modules, "pymarkdown.api", fake_mod)

        status, errors = checker.check_markdown_structure()
        assert status == "PASS"
        assert errors == []

    def test_markdown_warn_via_pymarkdown_api(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path)
        checker = qr.QualityCheck(
            str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        class Failure:
            scan_file = "x.md"
            line_number = 1
            column_number = 1
            rule_id = "MD013"
            rule_description = "Line length"

        class FakeScanResult:
            scan_failures = [Failure()]

        class FakeApi:
            def scan_path(self, _path):
                return FakeScanResult()

        fake_mod = types.SimpleNamespace(PyMarkdownApi=FakeApi)
        monkeypatch.setitem(qr.sys.modules, "pymarkdown.api", fake_mod)

        status, errors = checker.check_markdown_structure()
        assert status == "WARN"
        assert any("MD013" in e for e in errors)


class TestGrammarCheck:
    def test_grammar_import_error_is_warn(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path)
        checker = qr.QualityCheck(str(md), "intro", "B", skip_water=True, skip_ner=True)

        # Force ImportError only for language_tool_python, keep other imports working.
        real_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "language_tool_python":
                raise ImportError("nope")
            return real_import(name, globals, locals, fromlist, level)

        monkeypatch.setattr("builtins.__import__", fake_import)

        status, errors = checker.check_grammar()
        assert status == "WARN"
        assert errors

    def test_grammar_warn_when_matches_found(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nтестовый текст.\n")
        checker = qr.QualityCheck(str(md), "тестовый", "B", skip_water=True, skip_ner=True)

        class Match:
            context = "тестовый текст"
            message = "Possible typo"
            ruleId = "RULE"
            replacements = ["x", "y"]

        class Tool:
            def check(self, _text):
                return [Match()]

        fake_lang = types.SimpleNamespace(LanguageTool=lambda *_a, **_k: Tool())
        monkeypatch.setitem(qr.sys.modules, "language_tool_python", fake_lang)

        status, errors = checker.check_grammar()
        assert status == "WARN"
        assert errors
        assert isinstance(errors[0], dict)


class TestWaterCheck:
    def test_water_pass_tier_thresholds(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nтекст текст текст\n")
        checker = qr.QualityCheck(str(md), "текст", "C", skip_grammar=True, skip_ner=True)

        import scripts.check_water_natasha as water_mod
        import scripts.seo_utils as seo_utils

        monkeypatch.setattr(
            water_mod,
            "calculate_metrics_from_text",
            lambda _t: {
                "water_percent": 64.0,
                "classic_nausea": 3.0,
                "academic_nausea": 8.0,
                "lemma_repetition_index": 10.0,
            },
        )
        monkeypatch.setattr(
            seo_utils,
            "get_tier_requirements",
            lambda _tier: {
                "water_min": 40.0,
                "water_max": 65.0,
                "water_blocker_low": 30.0,
                "water_blocker_high": 70.0,
                "nausea_classic_max": 3.5,
                "nausea_classic_blocker": 4.0,
                "nausea_academic_min": 7.0,
                "nausea_academic_max": 9.5,
            },
        )

        status, metrics = checker.check_water_nausea()
        assert status == "PASS"
        assert metrics["water"] == 64.0

    def test_water_fail_on_blocker(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nтекст текст текст\n")
        checker = qr.QualityCheck(str(md), "текст", "B", skip_grammar=True, skip_ner=True)

        import scripts.check_water_natasha as water_mod
        import scripts.seo_utils as seo_utils

        monkeypatch.setattr(
            water_mod,
            "calculate_metrics_from_text",
            lambda _t: {
                "water_percent": 80.0,  # blocker high
                "classic_nausea": 3.0,
                "academic_nausea": 8.0,
                "lemma_repetition_index": 10.0,
            },
        )
        monkeypatch.setattr(
            seo_utils,
            "get_tier_requirements",
            lambda _tier: {
                "water_min": 40.0,
                "water_max": 60.0,
                "water_blocker_low": 30.0,
                "water_blocker_high": 61.0,
            },
        )

        status, _metrics = checker.check_water_nausea()
        assert status == "FAIL"


class TestKeywordDensity:
    def test_keyword_density_pass_with_json_report(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nактивная пена активная пена активная пена\n")
        checker = qr.QualityCheck(
            str(md), "активная пена", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        report = {
            "checks": {
                "density_distribution": {
                    "metrics": {
                        "total_density": 1.2,
                        "coverage": 55.0,
                        "keywords_found": 5,
                        "keywords_total": 8,
                    }
                }
            }
        }
        (tmp_path / "x_validation.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        monkeypatch.setattr(qr.subprocess, "run", lambda *_a, **_k: R())

        status, metrics = checker.check_keyword_density()
        assert status == "PASS"
        assert metrics["coverage"] == 55.0

    def test_keyword_density_warn_when_returncode_1(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nактивная пена\n")
        checker = qr.QualityCheck(
            str(md), "активная пена", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        report = {
            "checks": {
                "density_distribution": {"metrics": {"total_density": 2.6, "coverage": 20.0}}
            }
        }
        (tmp_path / "x_validation.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )

        class R:
            returncode = 1
            stdout = ""
            stderr = ""

        monkeypatch.setattr(qr.subprocess, "run", lambda *_a, **_k: R())

        status, _metrics = checker.check_keyword_density()
        assert status == "WARN"

    def test_keyword_density_fail_when_returncode_2(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nактивная пена\n")
        checker = qr.QualityCheck(
            str(md), "активная пена", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        report = {
            "checks": {
                "density_distribution": {"metrics": {"total_density": 4.0, "coverage": 10.0}}
            }
        }
        (tmp_path / "x_validation.json").write_text(
            json.dumps(report, ensure_ascii=False), encoding="utf-8"
        )

        class R:
            returncode = 2
            stdout = "FAIL"
            stderr = ""

        monkeypatch.setattr(qr.subprocess, "run", lambda *_a, **_k: R())

        status, _metrics = checker.check_keyword_density()
        assert status == "FAIL"

    def test_keyword_density_fails_when_json_missing(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nактивная пена\n")
        checker = qr.QualityCheck(
            str(md), "активная пена", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        monkeypatch.setattr(qr.subprocess, "run", lambda *_a, **_k: R())

        status, _metrics = checker.check_keyword_density()
        assert status == "FAIL"


class TestNerCommercialSeoStructure:
    def test_ner_pass_when_no_findings(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nтекст\n")
        checker = qr.QualityCheck(str(md), "текст", "B", skip_grammar=True, skip_water=True)

        import scripts.check_ner_brands as ner_mod

        monkeypatch.setattr(
            ner_mod,
            "check_blacklist",
            lambda _t: {"brands": [], "cities": [], "ai_fluff": [], "strict_phrases": []},
        )
        monkeypatch.setattr(ner_mod, "check_ner", lambda _t: {"ner_entities": []})

        status, findings = checker.check_ner_blacklist()
        assert status == "PASS"
        assert findings["brands"] == []

    def test_ner_fail_on_strict_phrases(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nтекст\n")
        checker = qr.QualityCheck(str(md), "текст", "B", skip_grammar=True, skip_water=True)

        import scripts.check_ner_brands as ner_mod

        monkeypatch.setattr(
            ner_mod,
            "check_blacklist",
            lambda _t: {
                "brands": [],
                "cities": [],
                "ai_fluff": [],
                "strict_phrases": [{"entity": "строго"}],
            },
        )
        monkeypatch.setattr(ner_mod, "check_ner", lambda _t: {"ner_entities": []})

        status, _findings = checker.check_ner_blacklist()
        assert status == "FAIL"

    def test_commercial_pass_when_enough(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nкупить цена доставка\n")
        checker = qr.QualityCheck(
            str(md), "купить", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        import scripts.seo_utils as seo_utils

        monkeypatch.setattr(seo_utils, "get_tier_requirements", lambda _tier: {"commercial_min": 2})
        monkeypatch.setattr(
            seo_utils,
            "check_commercial_markers",
            lambda _text, _min_required: {
                "passed": True,
                "found_count": 3,
                "found_markers": ["купить", "цена"],
                "message": "ok",
            },
        )

        status, _markers = checker.check_commercial_markers()
        assert status == "PASS"

    def test_seo_structure_fail(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nintro\n\n## H2\n")
        checker = qr.QualityCheck(
            str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        import scripts.check_seo_structure as seo_structure_mod

        monkeypatch.setattr(
            seo_structure_mod,
            "check_seo_structure",
            lambda _path, _kw: (
                "FAIL",
                {
                    "intro": {"passed": False, "message": "no"},
                    "h2": {
                        "passed": True,
                        "message": "ok",
                        "h2_with_keyword": [],
                        "h2_without_keyword": [],
                    },
                    "frequency": {"status": "OK", "is_spam": False, "message": "ok"},
                },
            ),
        )

        status, _results = checker.check_seo_structure()
        assert status == "FAIL"


class TestMarkdownFallback:
    def test_markdownlint_fallback_warn(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path)
        checker = qr.QualityCheck(
            str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        real_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name.startswith("pymarkdown"):
                raise ImportError("no pymarkdown")
            return real_import(name, globals, locals, fromlist, level)

        class R:
            returncode = 1
            stdout = "x.md:1:1 MD013 - Line too long"
            stderr = ""

        monkeypatch.setattr("builtins.__import__", fake_import)
        monkeypatch.setattr(qr.subprocess, "run", lambda *_a, **_k: R())

        status, errors = checker.check_markdown_structure()
        assert status == "WARN"
        assert errors

    def test_markdownlint_missing_binary_fails(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path)
        checker = qr.QualityCheck(
            str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        real_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name.startswith("pymarkdown"):
                raise ImportError("no pymarkdown")
            return real_import(name, globals, locals, fromlist, level)

        def raise_fn(*_a, **_k):
            raise FileNotFoundError("markdownlint")

        monkeypatch.setattr("builtins.__import__", fake_import)
        monkeypatch.setattr(qr.subprocess, "run", raise_fn)

        status, _errors = checker.check_markdown_structure()
        assert status == "FAIL"

    def test_commercial_fail_when_not_enough(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nтекст\n")
        checker = qr.QualityCheck(
            str(md), "текст", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        import scripts.seo_utils as seo_utils

        monkeypatch.setattr(seo_utils, "get_tier_requirements", lambda _tier: {"commercial_min": 3})
        monkeypatch.setattr(
            seo_utils,
            "check_commercial_markers",
            lambda _text, _min_required: {
                "passed": False,
                "found_count": 1,
                "found_markers": ["купить"],
                "message": "too few",
            },
        )

        status, _markers = checker.check_commercial_markers()
        assert status == "FAIL"

    def test_seo_structure_warn(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nintro\n\n## Заголовок\n")
        checker = qr.QualityCheck(
            str(md), "intro", "B", skip_grammar=True, skip_water=True, skip_ner=True
        )

        import scripts.check_seo_structure as seo_structure_mod

        monkeypatch.setattr(
            seo_structure_mod,
            "check_seo_structure",
            lambda _path, _kw: (
                "WARN",
                {
                    "intro": {"passed": True, "message": "ok", "in_first_sentence": True},
                    "h2": {
                        "passed": False,
                        "message": "meh",
                        "h2_with_keyword": [],
                        "h2_without_keyword": ["a"],
                    },
                    "frequency": {"status": "OK", "is_spam": False, "message": "ok"},
                },
            ),
        )

        status, results = checker.check_seo_structure()
        assert status == "WARN"
        assert results["h2"]["passed"] is False


class TestRunAllChecks:
    def test_exit_code_0_when_all_pass(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nintro intro intro.\n\n## intro\n")
        checker = qr.QualityCheck(str(md), "intro", "B")

        monkeypatch.setattr(checker, "check_markdown_structure", lambda: ("PASS", []))
        monkeypatch.setattr(checker, "check_grammar", lambda: ("PASS", []))
        monkeypatch.setattr(checker, "check_water_nausea", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_keyword_density", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_ner_blacklist", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_commercial_markers", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_seo_structure", lambda: ("PASS", {}))

        assert checker.run_all_checks() == 0

    def test_exit_code_1_when_only_warnings(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nintro intro intro.\n\n## intro\n")
        checker = qr.QualityCheck(str(md), "intro", "B")

        monkeypatch.setattr(checker, "check_markdown_structure", lambda: ("WARN", ["x"]))
        monkeypatch.setattr(checker, "check_grammar", lambda: ("PASS", []))
        monkeypatch.setattr(checker, "check_water_nausea", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_keyword_density", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_ner_blacklist", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_commercial_markers", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_seo_structure", lambda: ("PASS", {}))

        assert checker.run_all_checks() == 1

    def test_exit_code_2_when_any_fail(self, tmp_path: Path, monkeypatch):
        md = _write_md(tmp_path, "# H1\n\nintro\n")
        checker = qr.QualityCheck(str(md), "intro", "B")

        monkeypatch.setattr(checker, "check_markdown_structure", lambda: ("PASS", []))
        monkeypatch.setattr(checker, "check_grammar", lambda: ("FAIL", ["x"]))
        monkeypatch.setattr(checker, "check_water_nausea", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_keyword_density", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_ner_blacklist", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_commercial_markers", lambda: ("PASS", {}))
        monkeypatch.setattr(checker, "check_seo_structure", lambda: ("PASS", {}))

        assert checker.run_all_checks() == 2
