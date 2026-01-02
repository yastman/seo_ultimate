"""
TDD tests for scripts/check_seo_structure.py
"""

from __future__ import annotations

from pathlib import Path

import pytest

import scripts.check_seo_structure as mod


def test_normalize_keyword():
    assert mod.normalize_keyword("  Активная   Пена  ") == "активная пена"


def test_get_keyword_variations_contains_stems():
    vars_ = mod.get_keyword_variations("активная пена")
    assert "активная пена" in vars_
    assert any(v in vars_ for v in ["активн", "пен"])


def test_intro_check_passes_with_h1_structure():
    text = "# H1\n\nАктивная пена для мойки.\n\n## H2\n"
    res = mod.check_keyword_in_intro(text, "активная пена", limit=150)
    assert res["passed"] is True
    assert res["in_first_sentence"] is True


def test_h2_check_passes_with_stems():
    text = "# H1\n\nIntro.\n\n## Преимущества активной пены\n## Как выбрать активную пену\n## Доставка\n"
    res = mod.check_keywords_in_h2(text, "активная пена")
    assert res["total_h2"] == 3
    assert res["with_keyword"] >= 2
    assert res["passed"] is True


@pytest.mark.parametrize(
    "count,expected_status,is_spam",
    [
        (0, "LOW", False),
        (3, "OK", False),
        (8, "HIGH", False),
        (11, "SPAM", True),
    ],
)
def test_frequency_statuses(count: int, expected_status: str, is_spam: bool):
    text = ("активная пена. " * count).strip()
    res = mod.check_keyword_frequency(text, "активная пена")
    assert res["status"] == expected_status
    assert res["is_spam"] is is_spam


def test_check_seo_structure_overall_pass(tmp_path: Path):
    md = tmp_path / "x.md"
    md.write_text(
        "\n".join(
            [
                "# Активная пена",
                "",
                "Активная пена для мойки — это ...",  # intro contains keyword
                "",
                "## Преимущества активной пены",
                "Текст.",
                "## Как выбрать пену",
                "Текст.",
                "## FAQ",
                "Текст.",
                "",
                ("активная пена " * 3).strip(),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    status, results = mod.check_seo_structure(str(md), "активная пена")
    assert status in ("PASS", "WARN")  # depends on H2 counting and frequency
    assert "intro" in results and "h2" in results and "frequency" in results


def test_check_seo_structure_fail_when_missing_intro(tmp_path: Path):
    md = tmp_path / "x.md"
    md.write_text("# H1\n\nintro without keyword\n\n## H2\n", encoding="utf-8")
    status, _results = mod.check_seo_structure(str(md), "активная пена")
    assert status == "FAIL"


def test_cli_main_usage(capsys):
    rc = mod.main([])
    out = capsys.readouterr().out
    assert rc == 2
    assert "Usage" in out


def test_cli_main_file_not_found(capsys):
    rc = mod.main(["/no/such.md", "kw"])
    out = capsys.readouterr().out
    assert rc == 2
    assert "File not found" in out


def test_cli_main_runs_and_returns_code(tmp_path: Path, capsys):
    md = tmp_path / "x.md"
    md.write_text("# Активная пена\n\nАктивная пена.\n\n## Активная пена\n", encoding="utf-8")
    rc = mod.main([str(md), "активная пена"])
    out = capsys.readouterr().out
    assert rc in (0, 1, 2)
    assert "SEO Structure Check" in out


def test_check_keyword_in_intro_without_h1_uses_cleanup():
    text = "**Активная пена** для мойки.\n\n## H2\n"
    res = mod.check_keyword_in_intro(text, "активная пена", limit=150)
    assert res["passed"] is True
    assert "Активная пена" in res["intro_preview"]


def test_get_russian_word_stems_short_word():
    stems = mod.get_russian_word_stems("для")
    assert stems == ["для"]


def test_check_seo_structure_spam_is_fail(tmp_path: Path):
    md = tmp_path / "spam.md"
    md.write_text(
        "\n".join(
            [
                "# Активная пена",
                "",
                "Активная пена для мойки. Второе предложение.",
                "",
                "## Как выбрать активную пену",
                "Текст.",
                "## Преимущества активной пены",
                "Текст.",
                "",
                ("активная пена " * 11).strip(),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    status, results = mod.check_seo_structure(str(md), "активная пена")
    assert status == "FAIL"
    assert results["frequency"]["is_spam"] is True


def test_check_seo_structure_low_frequency_warn(tmp_path: Path):
    md = tmp_path / "low.md"
    md.write_text(
        "\n".join(
            [
                "# Активная пена",
                "",
                "Это обзор. Активная пена помогает.",  # keyword not in first sentence
                "",
                "## Как выбрать активную пену",  # matches stems, but not exact keyword string
                "Текст.",
                "## Преимущества активную пену",  # matches stems, but not exact keyword string
                "Текст.",
                "## FAQ",
                "Текст.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    status, results = mod.check_seo_structure(str(md), "активная пена")
    assert status == "WARN"
    assert results["frequency"]["status"] == "LOW"


def test_cli_main_pass_banner_printed(tmp_path: Path, capsys):
    md = tmp_path / "pass.md"
    md.write_text(
        "\n".join(
            [
                "# Активная пена",
                "",
                "Активная пена для мойки авто.",  # first sentence contains keyword
                "",
                "## Активная пену",  # stems, not exact phrase
                "активная пена активная пена активная пена",  # bring count to 3
                "## Активной пены",
                "Текст.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    rc = mod.main([str(md), "активная пена"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "SEO STRUCTURE: PASS" in out


def test_cli_main_fail_banner_and_detail_branches(tmp_path: Path, capsys):
    md = tmp_path / "fail.md"
    md.write_text(
        "\n".join(
            [
                "# Активная пена",
                "",
                "Это обзор. Активная пена для мойки авто.",  # keyword not in first sentence
                "",
                "## Как выбрать активную пену",
                "Текст.",
                "## Контакты",  # no keyword, should appear in h2_without_keyword
                "Текст.",
                "",
                ("активная пена " * 11).strip(),  # spam
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    rc = mod.main([str(md), "активная пена"])
    out = capsys.readouterr().out
    assert rc == 2
    assert "В первом предложении: нет" in out
    assert "Без keyword" in out
    assert "SEO STRUCTURE: FAIL" in out


def test_cli_main_frequency_non_ok_non_spam_uses_warning_icon(tmp_path: Path, capsys):
    md = tmp_path / "high.md"
    # 8 occurrences => status "HIGH" => CLI should use the fallback "⚠️" icon branch.
    md.write_text(
        "\n".join(
            [
                "# Активная пена",
                "",
                "Активная пена для мойки авто.",  # keyword in first sentence
                "",
                "## Преимущества активной пены",
                "Текст.",
                "## Как выбрать активную пену",
                "Текст.",
                "",
                ("активная пена " * 8).strip(),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    rc = mod.main([str(md), "активная пена"])
    out = capsys.readouterr().out
    assert rc in (0, 1, 2)
    assert "3. ЧАСТОТА KEYWORD:" in out
    assert "\n3. ЧАСТОТА KEYWORD:\n   ⚠️" in out
