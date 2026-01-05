import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# Add scripts to path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from validate_content import (  # noqa: E402
    check_blacklist_phrases,
    check_content_standards,
    check_grammar,
    check_keyword_coverage,
    check_keyword_coverage_split,
    check_length,
    check_markdown_lint,
    check_primary_keyword,
    check_primary_keyword_semantic,
    check_quality,
    check_structure,
    clean_markdown,
    count_chars_no_spaces,
    count_faq,
    count_words,
    extract_h1,
    extract_h2s,
    extract_intro,
    validate_content,
)


# Text samples for testing
SAMPLE_TEXT_VALID = """# Active Foam

This is a great intro about active foam. It contains the keyword active foam and is long enough to pass the check. We need at least 30 words in the intro so I am adding more text here to ensure it passes the length requirement. Active foam is amazing for cleaning cars without touching them.

## Benefits
Active foam cleans well.

## Usage
Use with a foam cannon.

**Q: Is it safe?**
A: Yes.
"""

SAMPLE_TEXT_FAIL = """# Wrong Title

Short intro.

## Only One Header
"""

# =============================================================================
# Text Processing Tests
# =============================================================================


def test_clean_markdown():
    text = "# Header\n**Bold** and *Italic*.\n[Link](http://example.com)"
    cleaned = clean_markdown(text)
    assert "Header" in cleaned
    assert "Bold" in cleaned
    assert "Italic" in cleaned
    assert "Link" in cleaned
    assert "#" not in cleaned
    assert "**" not in cleaned
    assert "[" not in cleaned


def test_count_words():
    text = "One two three."
    assert count_words(text) == 3


def test_count_chars_no_spaces():
    text = "One two"
    assert count_chars_no_spaces(text) == 6


def test_extract_h1():
    text = "# My Header\n## Subheader"
    assert extract_h1(text) == "My Header"
    assert extract_h1("No header") is None


def test_extract_h2s():
    text = "# H1\n## H2 First\nText\n## H2 Second"
    h2s = extract_h2s(text)
    assert len(h2s) == 2
    assert "H2 First" in h2s
    assert "H2 Second" in h2s


def test_extract_intro():
    text = "# H1\nIntro line 1.\nIntro line 2.\n## H2"
    intro = extract_intro(text)
    assert "Intro line 1." in intro
    assert "Intro line 2." in intro
    assert "## H2" not in intro


def test_count_faq():
    text = "**Q: Question?**\n**В: Вопрос?**"
    assert count_faq(text) == 2


# =============================================================================
# Check Functions Tests
# =============================================================================


def test_check_structure_pass():
    result = check_structure(SAMPLE_TEXT_VALID)
    assert result["overall"] == "PASS"
    assert result["h1"]["passed"] is True
    assert result["intro"]["passed"] is True
    assert result["h2_count"]["passed"] is True


def test_check_structure_fail():
    result = check_structure(SAMPLE_TEXT_FAIL)
    assert result["overall"] == "FAIL"
    assert result["intro"]["passed"] is False  # Too short


def test_check_primary_keyword_pass():
    result = check_primary_keyword(SAMPLE_TEXT_VALID, "active foam")
    assert result["overall"] == "PASS"
    assert result["in_h1"]["passed"] is True
    assert result["in_intro"]["passed"] is True
    assert result["frequency"]["status"] == "OK"


def test_check_primary_keyword_fail():
    result = check_primary_keyword(SAMPLE_TEXT_FAIL, "active foam")
    assert result["overall"] == "FAIL"
    assert result["in_h1"]["passed"] is False


def test_check_keyword_coverage():
    text = "one two three four"
    keywords = ["one", "two", "five"]
    result = check_keyword_coverage(text, keywords)
    assert result["total"] == 3
    assert result["found"] == 2
    assert result["coverage_percent"] == 66.7
    # 3 keywords -> target 70%, so 66.7% is FAIL/WARNING check logic
    # The code says: coverage >= target. 66.7 < 70, so passed=False => WARNING
    assert result["overall"] == "WARNING"


def test_check_primary_keyword_semantic_pass():
    text = "# Чернитель резины\nВведение про чернители шин."
    # "чернитель резины" -> stem "черни"
    # "чернители шин" -> contains "черни"
    result = check_primary_keyword_semantic(text, "чернитель резины")
    # Both H1 and Intro have matches
    assert result["semantic_h1"] is True
    assert result["semantic_intro"] is True
    assert result["overall"] == "PASS"


def test_check_primary_keyword_semantic_fail():
    text = "# Другой заголовок\nВведение совсем про другое."
    result = check_primary_keyword_semantic(text, "чернитель резины")
    assert result["semantic_h1"] is False
    assert result["semantic_intro"] is False
    assert result["overall"] == "FAIL"


# =============================================================================
# Quality & External Mocks Tests
# =============================================================================


@patch("validate_content.calculate_water_and_nausea")
def test_check_quality_pass(mock_calc):
    mock_calc.return_value = {"water_percent": 45, "classic_nausea": 2.5, "academic_nausea": 8.0}
    result = check_quality("some text")
    assert result["overall"] == "PASS"
    assert result["water"]["status"] == "OK"


@patch("validate_content.calculate_water_and_nausea")
def test_check_quality_warning(mock_calc):
    mock_calc.return_value = {
        "water_percent": 80,  # Too high
        "classic_nausea": 5.0,  # Too high
        "academic_nausea": 15.0,  # Too high
    }
    result = check_quality("some text")
    assert result["overall"] == "WARNING"
    assert result["water"]["status"] == "WARNING"


@patch("validate_content.check_blacklist")
def test_check_blacklist_pass(mock_check):
    mock_check.return_value = {"strict_phrases": [], "brands": [], "cities": [], "ai_fluff": []}
    result = check_blacklist_phrases("text")
    assert result["overall"] == "PASS"


@patch("validate_content.check_blacklist")
def test_check_blacklist_fail(mock_check):
    mock_check.return_value = {
        "strict_phrases": ["forbidden"],
        "brands": [],
        "cities": [],
        "ai_fluff": [],
    }
    result = check_blacklist_phrases("text")
    assert result["overall"] == "FAIL"


def test_check_length():
    short_text = "word " * 10
    result = check_length(short_text)
    assert result["status"] == "WARNING_SHORT"

    good_text = "word " * 200
    result = check_length(good_text)
    assert result["status"] == "OK"

    assert result["status"] == "OK"


def test_check_grammar():
    # Patch the global flag AND the module
    with (
        patch("validate_content.GRAMMAR_AVAILABLE", True),
        patch("validate_content.language_tool_python") as mock_lt,
    ):
        # Mock LanguageTool
        mock_tool = MagicMock()
        mock_lt.LanguageTool.return_value = mock_tool

        # Case 1: Pass
        mock_tool.check.return_value = []
        result = check_grammar("Clean text")
        assert result["overall"] == "PASS"

        # Case 2: Warning
        mock_match = MagicMock()
        mock_match.message = "Error"
        mock_match.context = "ctx"
        mock_match.ruleId = "RULE"
        mock_match.replacements = []

        # 6 errors > 5 threshold for WARNING
        mock_tool.check.return_value = [mock_match] * 6
        result = check_grammar("Bad text")
        assert result["overall"] == "WARNING"
        assert len(result["errors"]) == 6


def test_check_markdown_lint():
    with (
        patch("validate_content.MDLINT_AVAILABLE", True),
        patch("validate_content.PyMarkdownApi") as mock_api,
    ):
        # Mock API instance
        mock_instance = MagicMock()
        mock_api.return_value = mock_instance

        # Case 1: Pass
        mock_scan = MagicMock()
        mock_scan.scan_failures = []
        mock_instance.scan_path.return_value = mock_scan

        result = check_markdown_lint("file.md")
        assert result["overall"] == "PASS"

        # Case 2: Warning
        mock_fail = MagicMock()
        mock_fail.line_number = 1
        mock_fail.column_number = 1
        mock_fail.rule_id = "MD001"
        mock_fail.rule_description = "Desc"

        # 6 failures > 5 threshold for WARNING
        mock_scan.scan_failures = [mock_fail] * 6
        mock_instance.scan_path.return_value = mock_scan

        result = check_markdown_lint("file.md")
        assert result["overall"] == "WARNING"


# =============================================================================
# Integration Test
# =============================================================================


@patch("validate_content.Path.read_text")
@patch("validate_content.Path.exists")
@patch("validate_content.check_quality")
@patch("validate_content.check_blacklist_phrases")
def test_validate_content_integration(mock_blacklist, mock_quality, mock_exists, mock_read):
    mock_exists.return_value = True
    mock_read.return_value = SAMPLE_TEXT_VALID

    # Mock quality and blacklist to return PASS
    mock_quality.return_value = {"overall": "PASS"}
    mock_blacklist.return_value = {"overall": "PASS"}

    # Mock language tools to avoid import errors during test
    with (
        patch("validate_content.check_grammar", return_value={"overall": "PASS"}),
        patch("validate_content.check_markdown_lint", return_value={"overall": "PASS"}),
    ):
        result = validate_content("dummy_path.md", "active foam")

        # WARNING is acceptable (no blockers), PASS is ideal
        assert result["summary"]["overall"] in ["PASS", "WARNING"]
        assert result["summary"]["blockers"] == []


# =============================================================================
# Semantic Matching Tests
# =============================================================================


def test_semantic_match_singular_plural():
    """Test that singular/plural variations are matched."""
    text = (
        "# Чернители шин для автомобиля\n\nЧернители помогают вернуть цвет резине и защищают от UV."
    )
    result = check_primary_keyword_semantic(text, "чернитель резины")
    # Should match via stem "чернител"
    assert result["semantic_h1"] is True
    assert result["confidence"] >= 60


def test_semantic_match_stem_based():
    """Test stem-based matching."""
    text = "# Очистители дисков\n\nОчистители эффективно удаляют тормозную пыль и грязь."
    result = check_primary_keyword_semantic(text, "очиститель дисков")
    assert result["semantic_h1"] is True


def test_semantic_no_match():
    """Test that completely different text doesn't match."""
    text = "# Шампуни для ручной мойки\n\nШампуни для ручной мойки автомобиля."
    result = check_primary_keyword_semantic(text, "активная пена")
    assert result["confidence"] < 60


def test_semantic_returns_confidence():
    """Test that confidence score is returned."""
    text = "# Активная пена\n\nАктивная пена для мойки."
    result = check_primary_keyword_semantic(text, "активная пена")
    assert "confidence" in result
    assert isinstance(result["confidence"], int)
    assert result["overall"] == "PASS"


def test_semantic_with_intro_check():
    """Test that intro is also checked semantically."""
    text = "# Заголовок\n\nЧернители шин помогают вернуть цвет."
    result = check_primary_keyword_semantic(text, "чернитель резины")
    assert result["semantic_intro"] is True


# =============================================================================
# Edge Cases
# =============================================================================


def test_empty_text():
    """Test with empty text."""
    result = check_structure("")
    assert result["overall"] == "FAIL"
    assert result["h1"]["passed"] is False


def test_keyword_coverage_empty():
    """Test coverage with no keywords."""
    result = check_keyword_coverage("some text", [])
    assert result["passed"] is True
    assert result["total"] == 0


def test_adaptive_target_large():
    """Test adaptive target for large keyword sets."""
    keywords = [f"kw{i}" for i in range(25)]  # 20+ keywords
    result = check_keyword_coverage("", keywords)
    assert result["target"] == 50


def test_check_structure_no_h2():
    """Test structure check fails without H2."""
    text = "# H1\n\nLong intro text that is more than thirty words. " * 3
    result = check_structure(text)
    assert result["h2_count"]["passed"] is False


# =============================================================================
# Split Coverage Tests (v8.4)
# =============================================================================


def test_coverage_split_basic():
    """Test split coverage with core and commercial keywords."""
    text = "активная пена для мойки автомобиля бесконтактная"
    core = ["активная пена", "бесконтактная", "шампунь"]
    commercial = ["купить", "цена", "в наличии"]

    result = check_keyword_coverage_split(text, core, commercial)

    assert result["core"]["total"] == 3
    assert result["core"]["found"] == 2  # активная пена, бесконтактная
    assert result["commercial"]["total"] == 3
    assert result["commercial"]["found"] == 0
    assert result["overall"] == "WARNING"  # core < target


def test_coverage_split_core_pass():
    """Test split coverage passes when core meets target."""
    text = "активная пена бесконтактная шампунь концентрат"
    core = ["активная пена", "бесконтактная", "шампунь"]  # 3 keywords, need 70%
    commercial = ["купить", "цена"]

    result = check_keyword_coverage_split(text, core, commercial)

    assert result["core"]["found"] == 3
    assert result["core"]["coverage_percent"] == 100.0
    assert result["overall"] == "PASS"


def test_coverage_split_commercial_info_only():
    """Test that commercial coverage doesn't affect overall status."""
    text = "активная пена бесконтактная шампунь"  # All core, no commercial
    core = ["активная пена", "бесконтактная", "шампунь"]
    commercial = ["купить активную пену", "цена", "доставка", "в наличии", "заказать"]

    result = check_keyword_coverage_split(text, core, commercial)

    # Core passes
    assert result["core"]["passed"] is True
    assert result["overall"] == "PASS"
    # Commercial is 0% but doesn't affect overall
    assert result["commercial"]["found"] == 0
    assert result["commercial"]["coverage_percent"] == 0.0
    assert "note" in result["commercial"]  # INFO only


def test_coverage_split_empty_commercial():
    """Test split coverage with no commercial keywords."""
    text = "активная пена для мойки"
    core = ["активная пена"]
    commercial = []

    result = check_keyword_coverage_split(text, core, commercial)

    assert result["core"]["found"] == 1
    assert result["commercial"]["total"] == 0
    assert result["overall"] == "PASS"


def test_coverage_split_missing_keywords():
    """Test that missing keywords are tracked separately."""
    text = "активная пена"
    core = ["активная пена", "шампунь", "концентрат"]
    commercial = ["купить", "цена"]

    result = check_keyword_coverage_split(text, core, commercial)

    assert "шампунь" in result["core"]["missing_keywords"]
    assert "концентрат" in result["core"]["missing_keywords"]
    assert "купить" in result["commercial"]["missing_keywords"]
    assert "цена" in result["commercial"]["missing_keywords"]


@patch("validate_content.print")
def test_print_results(mock_print):
    results = {
        "file": "test.md",
        "primary_keyword": "pk",
        "checks": {
            "structure": {
                "overall": "PASS",
                "h1": {"passed": True, "value": "Title"},
                "intro": {"passed": True, "words": 50},
                "h2_count": {"passed": True, "count": 2},
                "faq_count": {"count": 1},
            },
            "primary_keyword": {
                "overall": "PASS",
                "in_h1": {"passed": True},
                "in_intro": {"passed": True},
                "frequency": {"status": "OK", "count": 3},
            },
            "coverage": {
                "overall": "PASS",
                "coverage_percent": 100,
                "target": 70,
                "found": 5,
                "total": 5,
            },
            "quality": {
                "overall": "PASS",
                "water": {"value": 50, "status": "OK"},
                "nausea_classic": {"value": 1, "status": "OK"},
                "nausea_academic": {"value": 5, "status": "OK"},
            },
            "blacklist": {
                "overall": "PASS",
                "strict_phrases": [],
                "brands": [],
                "cities": [],
                "ai_fluff": [],
            },
            "length": {"status": "OK", "words": 500, "chars_no_spaces": 3000},
            "grammar": {"overall": "PASS", "error_count": 0},
            "md_lint": {"overall": "PASS", "violation_count": 0},
        },
        "summary": {"overall": "PASS", "blockers": [], "warnings": []},
    }

    # Need to import print_results locally or from module if exported
    from validate_content import print_results

    print_results(results)
    assert mock_print.called


@patch("validate_content.validate_content")
@patch("validate_content.print_results")
def test_main(mock_print, mock_validate):
    # Mock sys.argv
    with patch("sys.argv", ["script.py", "file.md", "keyword"]):
        from validate_content import main

        mock_validate.return_value = {"summary": {"overall": "PASS"}}

        # Test normal execution - main() calls sys.exit(0) on success
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0  # Success exit code
        mock_validate.assert_called_once()
        # Check core arguments (file_path, primary_keyword, all_keywords)
        call_args = mock_validate.call_args
        assert call_args[0][0] == "file.md"
        assert call_args[0][1] == "keyword"
        mock_print.assert_called()


def test_check_content_standards_ok_ru():
    text = """# Заголовок

## Важно
Наденьте перчатки, не пересушивайте состав.

## Как использовать
1. Нанесите
2. Подождите
3. Смойте

Расход: 50 мл на 1 л воды, разведение 1:50.

Ссылка: [x](/catalog/x/)
"""
    res = check_content_standards(text)
    assert res["overall"] == "OK"
    assert res["issues"] == []
    assert res["crosslinks_count"] == 1


def test_check_content_standards_warning_crosslinks_not_required():
    text = """# Заголовок

Текст без важных блоков.
"""
    res = check_content_standards(text)
    assert res["overall"] == "WARNING"
    assert any("Нет блока про безопасность" in s for s in res["issues"])
    assert not any("внутренних ссылок" in s.lower() for s in res["issues"])


def test_validate_content_invalid_mode_returns_error():
    res = validate_content("x.md", "kw", mode="bad")
    assert "error" in res
    assert "Invalid mode" in res["error"]


def test_validate_content_file_not_found_returns_error(tmp_path):
    missing = tmp_path / "nope.md"
    res = validate_content(str(missing), "kw")
    assert "error" in res
    assert "File not found" in res["error"]


def test_validate_content_semantic_override(tmp_path, monkeypatch):
    import validate_content as vc

    md = tmp_path / "t.md"
    md.write_text("# H1\nIntro text", encoding="utf-8")

    monkeypatch.setattr(
        vc,
        "check_structure",
        lambda _t: {
            "overall": "PASS",
            "h1": {"passed": True, "value": "H1"},
            "intro": {"passed": True, "words": 40},
            "h2_count": {"passed": True, "count": 2},
        },
    )
    monkeypatch.setattr(
        vc,
        "check_primary_keyword",
        lambda _t, _kw: {
            "overall": "FAIL",
            "in_h1": {"passed": False},
            "in_intro": {"passed": False},
            "frequency": {"count": 0, "status": "LOW"},
        },
    )
    monkeypatch.setattr(
        vc,
        "check_primary_keyword_semantic",
        lambda _t, _kw, use_llm=True: {
            "overall": "PASS",
            "semantic_h1": True,
            "semantic_intro": True,
            "confidence": 80,
        },
    )
    monkeypatch.setattr(
        vc, "check_keyword_coverage", lambda _t, _k: {"overall": "PASS", "passed": True}
    )
    monkeypatch.setattr(vc, "check_quality", lambda _t, **kw: {"overall": "PASS"})
    monkeypatch.setattr(vc, "check_blacklist_phrases", lambda _t: {"overall": "PASS"})
    monkeypatch.setattr(
        vc, "check_length", lambda _t: {"status": "OK", "words": 200, "chars_no_spaces": 1000}
    )
    monkeypatch.setattr(vc, "check_content_standards", lambda _t: {"overall": "OK", "issues": []})
    monkeypatch.setattr(vc, "check_grammar", lambda _t: {"overall": "PASS"})
    monkeypatch.setattr(vc, "check_markdown_lint", lambda _p: {"overall": "PASS"})

    res = vc.validate_content(str(md), "kw", all_keywords=["a"])
    pk = res["checks"]["primary_keyword"]
    assert pk["semantic_override"] is True
    assert pk["overall"] == "PASS"


def test_validate_content_seo_mode_sets_skipped_and_info(tmp_path, monkeypatch):
    import validate_content as vc

    md = tmp_path / "t.md"
    md.write_text("# Активная пена\n\nАктивная пена.", encoding="utf-8")

    monkeypatch.setattr(
        vc,
        "check_strict_blacklist_only",
        lambda _t: {
            "overall": "PASS",
            "strict_phrases": [],
            "brands": [],
            "cities": [],
            "ai_fluff": [],
        },
    )

    res = vc.validate_content(str(md), "активная пена", all_keywords=["активная пена"], mode="seo")
    assert res["checks"]["coverage"]["overall"] == "INFO"
    assert res["checks"]["quality"]["overall"] == "SKIPPED"
    assert res["checks"]["grammar"]["overall"] == "SKIPPED"
    assert res["checks"]["md_lint"]["overall"] == "SKIPPED"
    assert res["checks"]["content_standards"]["overall"] == "SKIPPED"


def test_check_grammar_skipped_when_unavailable():
    with patch("validate_content.GRAMMAR_AVAILABLE", False):
        res = check_grammar("text")
    assert res["overall"] == "SKIPPED"


def test_check_grammar_exception_returns_error():
    with (
        patch("validate_content.GRAMMAR_AVAILABLE", True),
        patch("validate_content.language_tool_python") as mock_lt,
    ):
        mock_lt.LanguageTool.side_effect = RuntimeError("boom")
        res = check_grammar("text")
    assert res["overall"] == "ERROR"
    assert "boom" in (res.get("note") or "")


def test_check_markdown_lint_skipped_when_unavailable():
    with patch("validate_content.MDLINT_AVAILABLE", False):
        res = check_markdown_lint("file.md")
    assert res["overall"] == "SKIPPED"


def test_check_markdown_lint_exception_returns_error():
    with (
        patch("validate_content.MDLINT_AVAILABLE", True),
        patch("validate_content.PyMarkdownApi") as mock_api,
    ):
        mock_instance = MagicMock()
        mock_instance.scan_path.side_effect = RuntimeError("boom")
        mock_api.return_value = mock_instance
        res = check_markdown_lint("file.md")
    assert res["overall"] == "ERROR"
    assert "boom" in (res.get("note") or "")


@patch("validate_content.validate_content")
def test_main_error_result_exits_2(mock_validate):
    with patch("sys.argv", ["script.py", "file.md", "keyword"]):
        from validate_content import main

        mock_validate.return_value = {"error": "nope"}
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 2


def test_main_usage_exits_1(capsys):
    import validate_content as vc

    with patch("sys.argv", ["script.py"]), pytest.raises(SystemExit) as exc:
        vc.main()
    assert exc.value.code == 1
    assert "Usage" in capsys.readouterr().out


def test_main_json_output(monkeypatch, capsys):
    import validate_content as vc

    def _fake_validate(*_a, **_kw):
        return {
            "file": "f",
            "primary_keyword": "k",
            "checks": {},
            "summary": {"overall": "PASS", "blockers": [], "warnings": []},
        }

    monkeypatch.setattr(vc, "validate_content", _fake_validate)
    monkeypatch.setattr(sys, "argv", ["script.py", "file.md", "keyword", "--json"])
    with pytest.raises(SystemExit) as exc:
        vc.main()
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert '"overall": "PASS"' in out


def test_main_with_analysis_loads_keywords(monkeypatch):
    import types

    import validate_content as vc

    dummy = types.ModuleType("analyze_category")
    dummy.analyze_category = lambda _slug: {
        "keywords": {
            "all_keywords": [{"keyword": "k1"}, {"keyword": "k2"}],
            "core_keywords": ["c1"],
            "commercial_keywords": ["m1"],
        }
    }
    monkeypatch.setitem(sys.modules, "analyze_category", dummy)

    captured = {}

    def _fake_validate(file_path, primary_keyword, all_keywords, **kw):
        captured["all_keywords"] = all_keywords
        captured["core_keywords"] = kw.get("core_keywords")
        captured["commercial_keywords"] = kw.get("commercial_keywords")
        return {
            "file": file_path,
            "primary_keyword": primary_keyword,
            "checks": {},
            "summary": {"overall": "PASS", "blockers": [], "warnings": []},
        }

    monkeypatch.setattr(vc, "validate_content", _fake_validate)
    monkeypatch.setattr(vc, "print_results", lambda _r: None)
    monkeypatch.setattr(sys, "argv", ["script.py", "file.md", "keyword", "--with-analysis", "slug"])

    with pytest.raises(SystemExit) as exc:
        vc.main()
    assert exc.value.code == 0
    assert captured["all_keywords"] == ["k1", "k2"]
    assert captured["core_keywords"] == ["c1"]
    assert captured["commercial_keywords"] == ["m1"]


def test_main_mode_option_is_parsed(monkeypatch):
    import validate_content as vc

    captured = {}

    def _fake_validate(*_a, **kw):
        captured["mode"] = kw.get("mode")
        return {
            "file": "f",
            "primary_keyword": "k",
            "checks": {},
            "summary": {"overall": "PASS", "blockers": [], "warnings": []},
        }

    monkeypatch.setattr(vc, "validate_content", _fake_validate)
    monkeypatch.setattr(vc, "print_results", lambda _r: None)
    monkeypatch.setattr(sys, "argv", ["script.py", "file.md", "keyword", "--mode", "seo"])

    with pytest.raises(SystemExit) as exc:
        vc.main()
    assert exc.value.code == 0
    assert captured["mode"] == "seo"


def test_main_with_analysis_exception_prints_warning(monkeypatch, capsys):
    import types

    import validate_content as vc

    dummy = types.ModuleType("analyze_category")
    dummy.analyze_category = lambda _slug: (_ for _ in ()).throw(RuntimeError("boom"))
    monkeypatch.setitem(sys.modules, "analyze_category", dummy)

    monkeypatch.setattr(
        vc,
        "validate_content",
        lambda *_a, **_kw: {
            "file": "f",
            "primary_keyword": "k",
            "checks": {},
            "summary": {"overall": "PASS", "blockers": [], "warnings": []},
        },
    )
    monkeypatch.setattr(vc, "print_results", lambda _r: None)
    monkeypatch.setattr(sys, "argv", ["script.py", "file.md", "keyword", "--with-analysis", "slug"])

    with pytest.raises(SystemExit) as exc:
        vc.main()
    assert exc.value.code == 0
    assert "Warning: Could not load analysis" in capsys.readouterr().out


@patch("validate_content.validate_content")
@patch("validate_content.print_results")
def test_main_exit_codes_warning_and_fail(mock_print, mock_validate):
    import validate_content as vc

    mock_validate.return_value = {
        "file": "f",
        "primary_keyword": "k",
        "checks": {},
        "summary": {"overall": "WARNING", "blockers": [], "warnings": ["coverage"]},
    }
    with patch("sys.argv", ["script.py", "file.md", "keyword"]):
        with pytest.raises(SystemExit) as exc:
            vc.main()
        assert exc.value.code == 1

    mock_validate.return_value = {
        "file": "f",
        "primary_keyword": "k",
        "checks": {},
        "summary": {"overall": "FAIL", "blockers": ["primary_keyword"], "warnings": []},
    }
    with patch("sys.argv", ["script.py", "file.md", "keyword"]):
        with pytest.raises(SystemExit) as exc:
            vc.main()
        assert exc.value.code == 2


def test_check_blacklist_phrases_warning_when_non_strict_found():
    with patch("validate_content.check_blacklist") as mock_check:
        mock_check.return_value = {
            "strict_phrases": [],
            "brands": [{"entity": "x"}],
            "cities": [],
            "ai_fluff": [],
        }
        res = check_blacklist_phrases("text")
    assert res["overall"] == "WARNING"


def test_check_blacklist_phrases_unavailable(monkeypatch):
    import validate_content as vc

    monkeypatch.setattr(vc, "check_blacklist", None)
    res = vc.check_blacklist_phrases("text")
    assert res["overall"] == "PASS"
    assert "note" in res


def test_check_strict_blacklist_only_paths(monkeypatch):
    import validate_content as vc

    monkeypatch.setattr(
        vc,
        "check_blacklist",
        lambda _t: {
            "strict_phrases": ["x"],
            "brands": [{"entity": "b"}],
            "cities": [],
            "ai_fluff": [],
        },
    )
    res = vc.check_strict_blacklist_only("text")
    assert res["overall"] == "FAIL"

    monkeypatch.setattr(
        vc, "check_blacklist", lambda _t: (_ for _ in ()).throw(RuntimeError("boom"))
    )
    res = vc.check_strict_blacklist_only("text")
    assert res["overall"] == "ERROR"


def test_check_length_warning_long():
    res = check_length("слово " * 700)
    assert res["status"] == "WARNING_LONG"


def test_check_content_standards_warning_when_many_issues_but_safety_present():
    text = """# Заголовок

## Безопасность
test spot
"""
    res = check_content_standards(text)
    assert res["safety_block"] is True
    assert res["overall"] == "WARNING"
    assert len(res["issues"]) >= 3


def test_check_grammar_pass_with_few_matches():
    with (
        patch("validate_content.GRAMMAR_AVAILABLE", True),
        patch("validate_content.language_tool_python") as mock_lt,
    ):
        mock_tool = MagicMock()
        mock_lt.LanguageTool.return_value = mock_tool
        match = MagicMock()
        match.message = "m"
        match.context = "ctx"
        match.ruleId = "R"
        match.replacements = []
        mock_tool.check.return_value = [match] * 3
        res = check_grammar("text")
    assert res["overall"] == "PASS"
    assert res["error_count"] == 3


def test_check_markdown_lint_pass_with_few_violations():
    with (
        patch("validate_content.MDLINT_AVAILABLE", True),
        patch("validate_content.PyMarkdownApi") as mock_api,
    ):
        mock_instance = MagicMock()
        mock_api.return_value = mock_instance
        mock_fail = MagicMock()
        mock_fail.line_number = 1
        mock_fail.column_number = 1
        mock_fail.rule_id = "MD001"
        mock_fail.rule_description = "Desc"
        scan = MagicMock()
        scan.scan_failures = [mock_fail] * 2
        mock_instance.scan_path.return_value = scan
        res = check_markdown_lint("file.md")
    assert res["overall"] == "PASS"
    assert res["violation_count"] == 2


def test_print_results_covers_split_coverage_and_icons(capsys):
    from validate_content import print_results

    results = {
        "file": "f",
        "primary_keyword": "k",
        "mode": "quality",
        "checks": {
            "structure": {
                "overall": "FAIL",
                "h1": {"passed": False, "value": None},
                "intro": {"passed": False, "words": 0},
                "h2_count": {"passed": False, "count": 0},
            },
            "primary_keyword": {
                "overall": "FAIL",
                "in_h1": {"passed": False},
                "in_intro": {"passed": False},
                "frequency": {"count": 0, "status": "LOW"},
            },
            "coverage": {
                "overall": "WARNING",
                "core": {
                    "found": 1,
                    "total": 3,
                    "coverage_percent": 33.3,
                    "target": 70,
                    "missing_keywords": ["a", "b"],
                },
                "commercial": {
                    "found": 0,
                    "total": 2,
                    "coverage_percent": 0.0,
                    "missing_keywords": ["c"],
                    "note": "INFO",
                },
                "note": "n",
            },
            "quality": {"overall": "SKIPPED", "water": {"value": None}, "note": "Unavailable"},
            "blacklist": {
                "overall": "FAIL",
                "strict_phrases": ["x"],
                "brands": ["b"],
                "cities": [],
                "ai_fluff": ["f"],
            },
            "length": {"words": 10, "chars_no_spaces": 20, "status": "WARNING_SHORT"},
            "grammar": {"overall": "SKIPPED", "note": "n"},
            "md_lint": {
                "overall": "WARNING",
                "violations": [{"line": 1, "rule": "MD001", "description": "d"}],
                "violation_count": 6,
            },
            "content_standards": {"overall": "OK", "issues": []},
        },
        "summary": {"overall": "FAIL", "blockers": ["primary_keyword"], "warnings": ["coverage"]},
    }
    print_results(results)
    out = capsys.readouterr().out
    assert "KEYWORD COVERAGE" in out
    assert "Core (topic)" in out
    assert "OVERALL: FAIL" in out


def test_validate_content_seo_mode_split_coverage_adjusts_targets(tmp_path):
    import validate_content as vc

    md = tmp_path / "t.md"
    md.write_text("# Активная пена\n\nАктивная пена бесконтактная.", encoding="utf-8")

    res = vc.validate_content(
        str(md),
        "активная пена",
        core_keywords=["активная пена", "бесконтактная"],
        commercial_keywords=["купить"],
        mode="seo",
    )
    cov = res["checks"]["coverage"]
    assert cov["overall"] == "INFO"
    assert cov["core"]["target"] is None
    assert cov["core"]["passed"] is True
    assert cov["commercial"]["note"].startswith("SEO mode:")


def test_validate_content_collects_blockers(tmp_path, monkeypatch):
    import validate_content as vc

    md = tmp_path / "t.md"
    md.write_text("# H1\nintro", encoding="utf-8")

    monkeypatch.setattr(
        vc,
        "check_structure",
        lambda _t: {
            "overall": "FAIL",
            "h1": {"passed": False, "value": None},
            "intro": {"passed": False, "words": 0},
            "h2_count": {"passed": False, "count": 0},
        },
    )
    monkeypatch.setattr(
        vc,
        "check_primary_keyword",
        lambda _t, _kw: {
            "overall": "FAIL",
            "in_h1": {"passed": False},
            "in_intro": {"passed": False},
            "frequency": {"count": 0, "status": "LOW"},
        },
    )
    monkeypatch.setattr(
        vc,
        "check_primary_keyword_semantic",
        lambda *_a, **_kw: {
            "overall": "FAIL",
            "semantic_h1": False,
            "semantic_intro": False,
            "confidence": 0,
        },
    )
    monkeypatch.setattr(
        vc, "check_keyword_coverage", lambda *_a, **_kw: {"overall": "PASS", "passed": True}
    )
    monkeypatch.setattr(vc, "check_quality", lambda _t, **kw: {"overall": "FAIL"})
    monkeypatch.setattr(vc, "check_blacklist_phrases", lambda _t: {"overall": "FAIL"})
    monkeypatch.setattr(
        vc, "check_length", lambda _t: {"status": "OK", "words": 200, "chars_no_spaces": 1000}
    )
    monkeypatch.setattr(vc, "check_content_standards", lambda _t: {"overall": "OK", "issues": []})
    monkeypatch.setattr(vc, "check_grammar", lambda _t: {"overall": "PASS"})
    monkeypatch.setattr(vc, "check_markdown_lint", lambda _p: {"overall": "PASS"})

    res = vc.validate_content(str(md), "kw", all_keywords=["a"], use_semantic=False, mode="quality")
    assert res["summary"]["overall"] == "FAIL"
    assert set(res["summary"]["blockers"]) >= {
        "structure",
        "primary_keyword",
        "quality",
        "blacklist",
    }


def test_validate_content_collects_warnings(tmp_path, monkeypatch):
    import validate_content as vc

    md = tmp_path / "t.md"
    md.write_text("# H1\n\nkw " + ("x " * 200) + "\n## H2\ntext", encoding="utf-8")

    monkeypatch.setattr(
        vc,
        "check_structure",
        lambda _t: {
            "overall": "PASS",
            "h1": {"passed": True, "value": "H1"},
            "intro": {"passed": True, "words": 40},
            "h2_count": {"passed": True, "count": 2},
        },
    )
    monkeypatch.setattr(
        vc,
        "check_primary_keyword",
        lambda _t, _kw: {
            "overall": "PASS",
            "in_h1": {"passed": True},
            "in_intro": {"passed": True},
            "frequency": {"count": 1, "status": "OK"},
        },
    )
    monkeypatch.setattr(
        vc, "check_keyword_coverage", lambda *_a, **_kw: {"overall": "WARNING", "passed": False}
    )
    monkeypatch.setattr(vc, "check_quality", lambda _t, **kw: {"overall": "WARNING"})
    monkeypatch.setattr(vc, "check_blacklist_phrases", lambda _t: {"overall": "WARNING"})
    monkeypatch.setattr(
        vc,
        "check_length",
        lambda _t: {"status": "WARNING_SHORT", "words": 10, "chars_no_spaces": 20},
    )
    monkeypatch.setattr(
        vc, "check_content_standards", lambda _t: {"overall": "WARNING", "issues": ["x"]}
    )
    monkeypatch.setattr(vc, "check_grammar", lambda _t: {"overall": "WARNING"})
    monkeypatch.setattr(vc, "check_markdown_lint", lambda _p: {"overall": "WARNING"})

    res = vc.validate_content(str(md), "kw", all_keywords=["a"], use_semantic=False, mode="quality")
    assert res["summary"]["overall"] == "WARNING"
    assert set(res["summary"]["warnings"]) >= {
        "coverage",
        "quality",
        "blacklist",
        "length",
        "grammar",
        "md_lint",
        "content_standards",
    }


def test_print_results_more_branches(capsys):
    from validate_content import print_results

    # Split coverage: target=None branch + coverage icon INFO.
    results_split = {
        "file": "f",
        "primary_keyword": "k",
        "mode": "quality",
        "checks": {
            "structure": {
                "overall": "PASS",
                "h1": {"passed": True, "value": "H1"},
                "intro": {"passed": True, "words": 40},
                "h2_count": {"passed": True, "count": 2},
            },
            "primary_keyword": {
                "overall": "PASS",
                "in_h1": {"passed": True},
                "in_intro": {"passed": True},
                "frequency": {"count": 1, "status": "OK"},
            },
            "coverage": {
                "overall": "INFO",
                "core": {
                    "found": 1,
                    "total": 3,
                    "coverage_percent": 33.3,
                    "target": None,
                    "missing_keywords": ["a"],
                },
                "commercial": {
                    "found": 0,
                    "total": 2,
                    "coverage_percent": 0.0,
                    "missing_keywords": [],
                    "note": "INFO",
                },
                "note": "n",
            },
            "quality": {
                "overall": "PASS",
                "water": {"value": 50.0, "status": "OK"},
                "nausea_classic": {"value": 2.0, "status": "OK"},
                "nausea_academic": {"value": 8.0, "status": "OK"},
            },
            "blacklist": {
                "overall": "PASS",
                "strict_phrases": [],
                "brands": [],
                "cities": [],
                "ai_fluff": [],
            },
            "length": {"words": 200, "chars_no_spaces": 1000, "status": "OK"},
            "grammar": {
                "overall": "WARNING",
                "error_count": 2,
                "errors": [{"message": "m1"}, {"message": "m2"}],
            },
            "md_lint": {"overall": "ERROR", "note": "boom", "violations": [], "violation_count": 0},
            "content_standards": {"overall": "OK", "issues": []},
        },
        "summary": {"overall": "WARNING", "blockers": [], "warnings": ["grammar"]},
    }
    print_results(results_split)

    # Legacy coverage: missing_keywords print.
    results_legacy = {
        "file": "f",
        "primary_keyword": "k",
        "mode": "quality",
        "checks": {
            "structure": {
                "overall": "PASS",
                "h1": {"passed": True, "value": "H1"},
                "intro": {"passed": True, "words": 40},
                "h2_count": {"passed": True, "count": 2},
            },
            "primary_keyword": {
                "overall": "PASS",
                "in_h1": {"passed": True},
                "in_intro": {"passed": True},
                "frequency": {"count": 1, "status": "OK"},
            },
            "coverage": {
                "overall": "INFO",
                "found": 1,
                "total": 3,
                "coverage_percent": 33.3,
                "target": 70,
                "missing_keywords": ["a", "b"],
            },
            "quality": {
                "overall": "PASS",
                "water": {"value": 50.0, "status": "OK"},
                "nausea_classic": {"value": 2.0, "status": "OK"},
                "nausea_academic": {"value": 8.0, "status": "OK"},
            },
            "blacklist": {
                "overall": "PASS",
                "strict_phrases": [],
                "brands": [],
                "cities": [],
                "ai_fluff": [],
            },
            "length": {"words": 200, "chars_no_spaces": 1000, "status": "OK"},
            "grammar": {"overall": "PASS", "error_count": 0, "errors": []},
            "md_lint": {"overall": "SKIPPED", "note": "n", "violations": [], "violation_count": 0},
            "content_standards": {"overall": "OK", "issues": []},
        },
        "summary": {"overall": "PASS", "blockers": [], "warnings": []},
    }
    print_results(results_legacy)

    out = capsys.readouterr().out
    assert "target=70" in out or "Target:" in out
    assert "Missing:" in out
    assert "OVERALL: WARNING" in out
