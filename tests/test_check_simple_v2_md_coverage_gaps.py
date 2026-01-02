from __future__ import annotations

import builtins
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))


def _load_module_from_scripts(
    module_name: str, filename: str, import_guard
) -> ModuleType:
    scripts_dir = Path(__file__).parent.parent / "scripts"
    module_path = scripts_dir / filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec and spec.loader

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


def test_import_fallbacks_when_seo_utils_and_water_missing(capsys):
    def guard(name: str, fromlist):
        if name in {"seo_utils", "check_water_natasha"}:
            raise ImportError("forced")

    mod = _load_module_from_scripts(
        "check_simple_v2_md_no_utils_no_water",
        "check_simple_v2_md.py",
        guard,
    )

    out = capsys.readouterr().out
    assert "seo_utils.py не найден" in out
    assert mod.UTILS_AVAILABLE is False
    assert mod.NAUSEA_AVAILABLE is False

    assert mod.count_chars_no_spaces("a b\tc\n") == 3


def test_find_matches_longest_first_overlaps_and_short_phrases():
    import check_simple_v2_md as mod

    keywords_data = {
        "primary": [
            {"keyword": "активная пена", "variations": {"exact": ["активная пена", "aa"]}},
        ],
        "supporting": [
            {"keyword": "пена", "variations": {"exact": ["пена"]}},
        ],
    }
    res = mod.find_matches_longest_first("активная пена и пена aa", keywords_data)
    assert res["total_unique"] >= 2


def test_check_keyword_density_distribution_raw_thresholds_adds_warning(tmp_path: Path):
    import check_simple_v2_md as mod

    data = {
        "keywords": {
            "primary": [{"keyword": "key0", "variations": {"exact": ["key0"]}}],
            "secondary": [{"keyword": "key1", "variations": {"exact": ["key1"]}}],
            "supporting": [
                {"keyword": f"key{i}", "variations": {"exact": [f"key{i}"]}}
                for i in range(2, 23)
            ],
        }
    }
    json_path = tmp_path / "data.json"
    json_path.write_text(__import__("json").dumps(data, ensure_ascii=False), encoding="utf-8")

    md_content = "key0 key1 key2 " + ("word " * 97)
    result = mod.check_keyword_density_and_distribution(md_content, str(json_path), word_count=100, requirements=None)
    assert result["warnings"]
    assert result["total_density"] > 2.5


def test_check_h2_intent_structure_no_h2():
    import check_simple_v2_md as mod

    ok, msg = mod.check_h2_intent_structure("# H1\n\ntext")
    assert ok is False
    assert "Нет H2" in msg


def test_check_faq_too_many_questions():
    import check_simple_v2_md as mod

    md = "\n".join([f"### Вопрос {i}?" for i in range(7)])
    ok, msg = mod.check_faq(md)
    assert ok is False
    assert "рекомендуется 3-6" in msg


def test_check_keyword_stuffing_suspicious_density():
    import check_simple_v2_md as mod

    keyword = "активная"
    paras = []
    for _ in range(6):
        paras.append(f"{keyword} {keyword} " + ("слово " * 10).strip())
    text = "\n\n".join(paras)

    ok, msg = mod.check_keyword_stuffing(text, keyword)
    assert ok is False
    assert "Подозрение на переспам" in msg


def test_check_nausea_metrics_exception_and_no_metrics(monkeypatch):
    import check_simple_v2_md as mod

    monkeypatch.setattr(mod, "NAUSEA_AVAILABLE", True)
    monkeypatch.setattr(mod, "calculate_metrics_from_text", lambda _t: None)
    res = mod.check_nausea_metrics("text", tier="B")
    assert "текст слишком короткий" in res["message"]

    def boom(_t):
        raise RuntimeError("boom")

    monkeypatch.setattr(mod, "calculate_metrics_from_text", boom)
    res = mod.check_nausea_metrics("text", tier="B")
    assert "ошибка" in res["message"].lower()


def test_check_nausea_metrics_fallback_thresholds_and_issue_lines():
    def guard(name: str, _fromlist):
        if name == "seo_utils":
            raise ImportError("forced")

    mod = _load_module_from_scripts(
        "check_simple_v2_md_no_utils",
        "check_simple_v2_md.py",
        guard,
    )
    assert mod.UTILS_AVAILABLE is False
    assert mod.NAUSEA_AVAILABLE is True

    mod.calculate_metrics_from_text = lambda _t: {
        "water_percent": 30.0,
        "classic_nausea": 3.8,
        "academic_nausea": 5.0,
    }
    res = mod.check_nausea_metrics("тест", tier="B")
    assert res["pass"] is True
    assert "Water" in res["message"]
    assert "Classic Nausea" in res["message"]
    assert "Academic" in res["message"]

    mod.calculate_metrics_from_text = lambda _t: {
        "water_percent": 30.0,
        "classic_nausea": 3.8,
        "academic_nausea": 10.0,
    }
    res = mod.check_nausea_metrics("тест", tier="B")
    assert "Academic" in res["message"]


def test_check_internal_links_too_many_links():
    import check_simple_v2_md as mod

    md = "\n".join([f"[a{i}](/x{i})" for i in range(6)])
    ok, msg = mod.check_internal_links(md)
    assert ok is True
    assert "рекомендуется 2-5" in msg


def test_check_content_file_not_found_returns_error():
    import check_simple_v2_md as mod

    res = mod.check_content("no_such_file.md", "kw", "B")
    assert res["status"] == "ERROR"
    assert "Файл не найден" in res["message"]


def test_check_content_returns_error_when_utils_missing(tmp_path: Path, capsys):
    def guard(name: str, _fromlist):
        if name == "seo_utils":
            raise ImportError("forced")

    mod = _load_module_from_scripts(
        "check_simple_v2_md_no_utils_check_content",
        "check_simple_v2_md.py",
        guard,
    )
    fp = tmp_path / "x.md"
    fp.write_text("# H1\n\n" + ("слово " * 120) + "\n", encoding="utf-8")

    res = mod.check_content(str(fp), "слово", "B")
    assert res["status"] == "ERROR"
    assert "dependency missing" in res["message"]
    assert "CRITICAL ERROR" in capsys.readouterr().out


def test_check_content_density_distribution_uses_clean_json_and_sets_review_status(tmp_path: Path, monkeypatch):
    import check_simple_v2_md as mod

    slug = "s"
    cat_dir = tmp_path / "categories" / slug
    md_dir = cat_dir / "content"
    data_dir = cat_dir / "data"
    md_dir.mkdir(parents=True)
    data_dir.mkdir(parents=True)

    md_file = md_dir / f"{slug}_ru.md"
    md_file.write_text(
        "\n".join(
            [
                "---",
                "title: t",
                "description: d",
                "---",
                f"# {slug}",
                "",
                ("слово " * 120).strip(),
                "",
                "## Как выбрать",
                "текст",
                "## FAQ",
                "### Вопрос 1?",
                "Ответ.",
                "### Вопрос 2?",
                "Ответ.",
                "### Вопрос 3?",
                "Ответ.",
                "",
                "[a](/x)",
                "[b](/y)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    # Ensure clean json exists (covers selection branch).
    (data_dir / f"{slug}_clean.json").write_text("{}", encoding="utf-8")

    monkeypatch.setattr(
        mod,
        "check_keyword_density_and_distribution",
        lambda *_a, **_k: {
            "total_density": 3.0,
            "coverage": 10.0,
            "keywords_total": 30,
            "warnings": ["w"] * 6,
            "errors": [],
            "details": [{"keyword": f"k{i}", "type": "supporting", "exact": 1, "partial": 0, "total": 1, "target": 0, "density_actual": "0.10%", "density_target": "0.00%", "status": "✓"} for i in range(11)],
        },
    )
    monkeypatch.setattr(mod, "check_nausea_metrics", lambda *_a, **_k: {"pass": True, "blocker": False, "message": "ok"})

    res = mod.check_content(str(md_file), slug, tier="B")
    assert res["status"] == "REVIEW"
    assert res["checks"]["density_distribution"]["severity"] == "REVIEW"


def test_check_content_density_distribution_json_missing_sets_warning_message(tmp_path: Path):
    import check_simple_v2_md as mod

    slug = "s"
    cat_dir = tmp_path / "categories" / slug / "content"
    cat_dir.mkdir(parents=True)
    md_file = cat_dir / f"{slug}_ru.md"
    md_file.write_text("# H1\n\n" + ("слово " * 120) + "\n## Как выбрать\n", encoding="utf-8")

    res = mod.check_content(str(md_file), slug, tier="B")
    msg = res["checks"]["density_distribution"]["message"]
    assert "JSON не найден" in msg


@pytest.mark.parametrize("status,expected", [("PASS", "соответствует"), ("REVIEW", "требует доработки")])
def test_print_report_truncation_and_status_lines(status: str, expected: str, capsys):
    import check_simple_v2_md as mod

    results = {
        "file": "x.md",
        "tier": "B",
        "word_count": 100,
        "char_count_no_spaces": 100,
        "status": status,
        "checks": {
            "density_distribution": {
                "pass": True,
                "message": "Density ok",
                "details": {
                    "details": [{"keyword": f"k{i}", "type": "t", "exact": 1, "partial": 0, "total": 1, "density_actual": "0.10%", "density_target": "0.00%", "status": "✓"} for i in range(11)],
                    "warnings": [f"w{i}" for i in range(6)],
                    "errors": [],
                },
            }
        },
    }

    mod.print_report(results)
    out = capsys.readouterr().out
    assert "... и ещё" in out
    assert expected in out


@pytest.mark.parametrize("status,exit_code", [("PASS", 0), ("REVIEW", 1)])
def test_main_exit_codes_for_pass_and_review(tmp_path: Path, monkeypatch, status: str, exit_code: int):
    import check_simple_v2_md as mod

    md = tmp_path / "x.md"
    md.write_text("# H1\n", encoding="utf-8")

    monkeypatch.setattr(mod, "check_content", lambda *_a, **_k: {"file": "x.md", "tier": "B", "word_count": 1, "checks": {}, "status": status, "metadata": {}})
    monkeypatch.setattr(mod, "print_report", lambda *_a, **_k: None)

    monkeypatch.setattr(sys, "argv", ["check_simple_v2_md.py", str(md), "kw", "B"])
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code == exit_code
