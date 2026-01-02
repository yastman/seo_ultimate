from __future__ import annotations

import builtins
import importlib.util
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def _load_validate_module(module_name: str, import_guard):
    module_path = Path(__file__).parent.parent / "scripts" / "validate_content.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec
    assert spec.loader

    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        import_guard(name, fromlist)
        return real_import(name, globals, locals, fromlist, level)

    old_import = builtins.__import__
    builtins.__import__ = guarded_import  # type: ignore[assignment]
    try:
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod
    finally:
        builtins.__import__ = old_import  # type: ignore[assignment]
        sys.modules.pop(spec.name, None)


def test_import_fallbacks_for_optional_dependencies():
    def guard(name: str, fromlist):
        if name in {"check_water_natasha", "check_ner_brands", "language_tool_python"}:
            raise ImportError("forced")
        if name == "pymarkdown.api":
            raise ImportError("forced")

    mod = _load_validate_module("validate_content_optional_deps_missing", guard)
    assert mod.calculate_water_and_nausea is None
    assert mod.check_blacklist is None
    assert mod.GRAMMAR_AVAILABLE is False
    assert mod.MDLINT_AVAILABLE is False


def test_import_fails_when_seo_utils_missing(capsys):
    def guard(name: str, _fromlist):
        if name == "seo_utils":
            raise ImportError("forced")

    with pytest.raises(SystemExit) as exc:
        _load_validate_module("validate_content_no_seo_utils", guard)
    assert exc.value.code == 1
    assert "Could not import core functions" in capsys.readouterr().out


def test_check_primary_keyword_frequency_high():
    from validate_content import check_primary_keyword

    text = "# Активная пена\n\n" + ("активная пена " * 11)
    res = check_primary_keyword(text, "активная пена")
    assert res["frequency"]["status"] == "HIGH"


def test_check_primary_keyword_semantic_warning_when_only_h1_matches():
    from validate_content import check_primary_keyword_semantic

    text = "\n".join(
        [
            "# Очистители стекол",
            "",
            "В этом тексте нет эквивалента ключа в интро.",
            "",
            "## H2",
            "Текст.",
        ]
    )
    res = check_primary_keyword_semantic(text, "очиститель стекол", use_llm=False)
    assert res["overall"] == "WARNING"
    assert res["confidence"] == 60


def test_check_keyword_coverage_target_60():
    from validate_content import check_keyword_coverage

    res = check_keyword_coverage("x", [f"k{i}" for i in range(15)])
    assert res["target"] == 60


def test_keyword_matches_semantic_branches():
    from validate_content import keyword_matches_semantic

    assert keyword_matches_semantic("а б", "текст") is False
    assert keyword_matches_semantic("шампунь для мойки", "шампунь") is True
    assert keyword_matches_semantic("очиститель дисков", "очистители дисков") is True
    assert keyword_matches_semantic("шинам", "шина") is True


def test_check_keyword_coverage_split_exact_mode_target_60():
    from validate_content import check_keyword_coverage_split

    core = [f"k{i}" for i in range(15)]
    res = check_keyword_coverage_split("k0 k1", core, ["купить"], use_semantic=False)
    assert res["core"]["target"] == 60
    assert res["core"]["found"] == 2


def test_extract_intro_stops_after_5_lines():
    from validate_content import extract_intro

    text = "\n".join(
        [
            "# H1",
            "",
            "l1",
            "l2",
            "l3",
            "l4",
            "l5",
            "l6",
            "",
            "## H2",
            "body",
        ]
    )
    intro = extract_intro(text)
    assert intro == "l1 l2 l3 l4 l5"


def test_check_keyword_coverage_split_core_target_50_for_many_keywords():
    from validate_content import check_keyword_coverage_split

    core = [f"kw{i}" for i in range(21)]
    text = " ".join(core[:11])
    res = check_keyword_coverage_split(text, core, ["купить"], use_semantic=False)
    assert res["core"]["target"] == 50
    assert res["overall"] == "PASS"


def test_validate_content_seo_warning_suppression_guard_branch(monkeypatch, tmp_path: Path):
    import validate_content as mod

    class FlipSeoMode(str):
        def __new__(cls):
            return str.__new__(cls, "seo")

        def __init__(self):
            self._seo_eq_calls = 0

        def __eq__(self, other):  # type: ignore[override]
            if other == "seo":
                self._seo_eq_calls += 1
                # This value is "seo", but we need to:
                # - pass the initial "mode in VALIDATION_MODES" check,
                # - behave as "not seo" for the early branches,
                # - behave as "seo" for the final guard branch.
                #
                # Comparisons seen in this function:
                #   1) membership check (may call our __eq__ due to subtype rules)
                #   2) coverage/quality branch (mode == "seo")
                #   3) grammar/md-lint branch (mode == "seo")
                #   4) final guard (mode == "seo")
                return self._seo_eq_calls in (1, 4)
            return str.__eq__(self, other)

        def __ne__(self, other):  # type: ignore[override]
            if other == "seo":
                return True
            return str.__ne__(self, other)

    md = tmp_path / "x.md"
    md.write_text("# H1\n\nkw\n", encoding="utf-8")

    monkeypatch.setattr(mod, "check_structure", lambda _t: {"overall": "PASS"})
    monkeypatch.setattr(mod, "check_primary_keyword", lambda _t, _k: {"overall": "PASS"})
    monkeypatch.setattr(mod, "check_keyword_coverage", lambda _t, _kws: {"overall": "PASS"})
    monkeypatch.setattr(mod, "check_quality", lambda _t, lang="ru": {"overall": "PASS"})
    monkeypatch.setattr(mod, "check_blacklist_phrases", lambda _t: {"overall": "PASS"})
    monkeypatch.setattr(
        mod, "check_length", lambda _t, keywords_count=None: {"status": "WARNING: short"}
    )
    monkeypatch.setattr(mod, "check_grammar", lambda _t: {"overall": "PASS"})
    monkeypatch.setattr(mod, "check_markdown_lint", lambda _p: {"overall": "PASS"})

    res = mod.validate_content(
        str(md),
        "kw",
        all_keywords=["a", "b"],
        use_semantic=False,
        mode=FlipSeoMode(),
    )
    assert res["summary"]["overall"] == "PASS"
    assert "length" in res["summary"]["warnings"]


def test_check_quality_unavailable_when_natasha_missing(monkeypatch):
    import validate_content as mod

    monkeypatch.setattr(mod, "calculate_water_and_nausea", None)
    res = mod.check_quality("текст")
    assert res["note"].startswith("Water/Nausea check unavailable")


def test_check_quality_exception_sets_error(monkeypatch):
    import validate_content as mod

    def boom(*_a, **_k):
        raise RuntimeError("boom")

    monkeypatch.setattr(mod, "calculate_water_and_nausea", boom)
    res = mod.check_quality("текст")
    assert res["overall"] == "ERROR"
    assert "boom" in res["error"]


def test_check_blacklist_phrases_exception_sets_error(monkeypatch):
    import validate_content as mod

    monkeypatch.setattr(
        mod, "check_blacklist", lambda _t: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    res = mod.check_blacklist_phrases("текст")
    assert "error" in res


def test_check_strict_blacklist_only_unavailable(monkeypatch):
    import validate_content as mod

    monkeypatch.setattr(mod, "check_blacklist", None)
    res = mod.check_strict_blacklist_only("текст")
    assert res["note"] == "Blacklist check unavailable"


def test_check_length_get_adaptive_requirements_exception_is_swallowed(monkeypatch):
    import validate_content as mod

    monkeypatch.setattr(
        mod, "get_adaptive_requirements", lambda _n: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    res = mod.check_length("слово " * 10, keywords_count=10)
    assert res["recommended_words"] == (150, 600)


def test_print_results_length_targets_and_grammar_icon(capsys):
    import validate_content as mod

    base = {
        "file": "x.md",
        "primary_keyword": "kw",
        "mode": "quality",
        "checks": {
            "structure": {
                "overall": "PASS",
                "h1": {"passed": True, "value": "H1"},
                "intro": {"passed": True, "words": 30},
                "h2_count": {"passed": True, "count": 1, "h2s": []},
                "faq_count": {"count": 0},
            },
            "primary_keyword": {
                "overall": "PASS",
                "in_h1": {"passed": True},
                "in_intro": {"passed": True},
                "frequency": {"count": 2, "status": "OK"},
            },
            "coverage": {
                "overall": "PASS",
                "total": 0,
                "found": 0,
                "coverage_percent": 0,
                "target": 0,
                "passed": True,
                "found_keywords": [],
                "missing_keywords": [],
            },
            "quality": {
                "overall": "PASS",
                "water": {"value": 50, "status": "OK"},
                "nausea_classic": {"value": 3.0, "status": "OK"},
                "nausea_academic": {"value": 8.0, "status": "OK"},
            },
            "blacklist": {
                "overall": "PASS",
                "strict_phrases": [],
                "brands": [],
                "cities": [],
                "ai_fluff": [],
            },
            "length": {
                "words": 200,
                "chars_no_spaces": 1000,
                "status": "OK",
                "keywords_count": None,
                "recommended_words": (150, 600),
            },
            "content_standards": {"overall": "PASS", "issues": []},
            "grammar": {"overall": "ERROR", "note": "x", "error_count": 0, "errors": []},
            "md_lint": {"overall": "SKIPPED", "note": "x", "violations": [], "violation_count": 0},
        },
        "summary": {"overall": "PASS", "blockers": [], "warnings": []},
    }

    mod.print_results(base)
    out = capsys.readouterr().out
    assert "Target:" in out  # keywords_count is None branch
    assert "GRAMMAR:" in out

    base["checks"]["length"]["keywords_count"] = 10
    mod.print_results(base)
    out = capsys.readouterr().out
    assert "Target (by 10 keywords)" in out


def test_main_parses_lang_flag(monkeypatch, tmp_path: Path):
    import validate_content as mod

    md = tmp_path / "x.md"
    md.write_text("# H1\n", encoding="utf-8")

    called = {}

    def fake_validate(
        file_path,
        primary_keyword,
        all_keywords,
        core_keywords=None,
        commercial_keywords=None,
        use_semantic=True,
        mode="quality",
        lang="ru",
    ):
        called["lang"] = lang
        return {
            "file": file_path,
            "primary_keyword": primary_keyword,
            "checks": {},
            "summary": {"overall": "PASS", "blockers": [], "warnings": []},
        }

    monkeypatch.setattr(mod, "validate_content", fake_validate)
    monkeypatch.setattr(mod, "print_results", lambda *_a, **_k: None)

    monkeypatch.setattr(sys, "argv", ["validate_content.py", str(md), "kw", "--lang", "uk"])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == 0
    assert called["lang"] == "uk"
