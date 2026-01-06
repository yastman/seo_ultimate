"""
TDD tests for check_water_natasha.py

Covers:
- main() argument handling
- check_water() branches via mocked metrics
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import scripts.check_water_natasha as mod


def test_main_usage_no_args(capsys):
    rc = mod.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "Usage" in out


def test_main_file_not_found(capsys):
    rc = mod.main(["/no/such/file.md"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "Файл не найден" in out


def test_check_water_pass_all(tmp_path: Path, monkeypatch):
    md = tmp_path / "t.md"
    md.write_text("тест", encoding="utf-8")

    monkeypatch.setattr(
        mod,
        "calculate_metrics",
        lambda _file: {
            "total_words": 100,
            "unique_lemmas": 90,
            "water_percent": 50.0,
            "water_percent_raw": 20.8,
            "water_count": 21,
            "classic_nausea": 3.0,
            "most_common_lemma": "тест",
            "max_frequency": 9,
            "academic_nausea": 8.0,
            "most_common_significant": "тест",
            "max_freq_significant": 3,
            "total_significant": 30,
            "lemma_repetition_index": 10.0,
            "repeated_words_count": 10,
        },
    )

    assert mod.check_water(str(md), 40, 60) == 0


def test_check_water_warn_water_excess(tmp_path: Path, monkeypatch):
    md = tmp_path / "t.md"
    md.write_text("тест", encoding="utf-8")

    monkeypatch.setattr(
        mod,
        "calculate_metrics",
        lambda _file: {
            "total_words": 100,
            "unique_lemmas": 90,
            "water_percent": 63.0,  # above max by 3
            "water_percent_raw": 26.25,
            "water_count": 26,
            "classic_nausea": 3.0,
            "most_common_lemma": "тест",
            "max_frequency": 9,
            "academic_nausea": 8.0,
            "most_common_significant": "тест",
            "max_freq_significant": 3,
            "total_significant": 30,
            "lemma_repetition_index": 10.0,
            "repeated_words_count": 10,
        },
    )

    assert mod.check_water(str(md), 40, 60) == 0


def test_check_water_warn_water_excess_over_5(tmp_path: Path, monkeypatch, capsys):
    md = tmp_path / "t.md"
    md.write_text("тест", encoding="utf-8")

    monkeypatch.setattr(
        mod,
        "calculate_metrics",
        lambda _file: {
            "total_words": 100,
            "unique_lemmas": 90,
            "water_percent": 80.0,  # above max by 20
            "water_percent_raw": 33.3,
            "water_count": 33,
            "classic_nausea": 3.0,
            "most_common_lemma": "тест",
            "max_frequency": 9,
            "academic_nausea": 8.0,
            "most_common_significant": "тест",
            "max_freq_significant": 3,
            "total_significant": 30,
            "lemma_repetition_index": 10.0,
            "repeated_words_count": 10,
        },
    )

    assert mod.check_water(str(md), 40, 60) == 0
    assert "Превышение" in capsys.readouterr().out


def test_check_water_blocker_classic_nausea(tmp_path: Path, monkeypatch):
    md = tmp_path / "t.md"
    md.write_text("тест", encoding="utf-8")

    monkeypatch.setattr(
        mod,
        "calculate_metrics",
        lambda _file: {
            "total_words": 100,
            "unique_lemmas": 90,
            "water_percent": 50.0,
            "water_percent_raw": 20.8,
            "water_count": 21,
            "classic_nausea": 4.2,  # blocker
            "most_common_lemma": "тест",
            "max_frequency": 18,
            "academic_nausea": 8.0,
            "most_common_significant": "тест",
            "max_freq_significant": 3,
            "total_significant": 30,
            "lemma_repetition_index": 10.0,
            "repeated_words_count": 10,
        },
    )

    assert mod.check_water(str(md), 40, 60) == 0


def test_check_water_blocker_academic_nausea(tmp_path: Path, monkeypatch):
    md = tmp_path / "t.md"
    md.write_text("тест", encoding="utf-8")

    monkeypatch.setattr(
        mod,
        "calculate_metrics",
        lambda _file: {
            "total_words": 100,
            "unique_lemmas": 90,
            "water_percent": 50.0,
            "water_percent_raw": 20.8,
            "water_count": 21,
            "classic_nausea": 3.0,
            "most_common_lemma": "тест",
            "max_frequency": 9,
            "academic_nausea": 13.0,  # blocker
            "most_common_significant": "тест",
            "max_freq_significant": 13,
            "total_significant": 100,
            "lemma_repetition_index": 10.0,
            "repeated_words_count": 10,
        },
    )

    assert mod.check_water(str(md), 40, 60) == 0


def test_clean_markdown_fallback_local(monkeypatch):
    dummy1 = types.ModuleType("scripts.seo_utils")
    dummy2 = types.ModuleType("seo_utils")
    monkeypatch.setitem(sys.modules, "scripts.seo_utils", dummy1)
    monkeypatch.setitem(sys.modules, "seo_utils", dummy2)

    cleaned = mod.clean_markdown("# H1\n**bold** `code`")
    assert "H1" in cleaned
    assert "bold" in cleaned
    assert "code" not in cleaned


def test_clean_markdown_fallback_to_seo_utils(monkeypatch):
    dummy = types.ModuleType("scripts.seo_utils")
    monkeypatch.setitem(sys.modules, "scripts.seo_utils", dummy)

    scripts_dir = Path(__file__).parent.parent / "scripts"
    monkeypatch.syspath_prepend(str(scripts_dir))

    cleaned = mod.clean_markdown("# H1\n**bold**")
    assert "H1" in cleaned
    assert "bold" in cleaned


def test_calculate_metrics_from_text_fallback_morph_vocab(monkeypatch):
    # Force the morph_tagger=None branch and a morph_vocab() that returns [] so
    # the code hits the "parsed is empty" fallback.
    monkeypatch.setattr(
        mod,
        "get_nlp_pipeline",
        lambda: {
            "segmenter": mod.Segmenter(),
            "morph_vocab": (lambda _w: []),
            "morph_tagger": None,
        },
    )
    # Ensure significant_lemma_counts is empty to cover its fallback as well.
    monkeypatch.setattr(mod, "load_stopwords", lambda *args: {"тест"})

    metrics = mod.calculate_metrics_from_text("тест тест")
    assert metrics is not None
    assert metrics["most_common_lemma"] == "тест"


def test_calculate_metrics_from_text_fallback_morph_vocab_parsed(monkeypatch):
    monkeypatch.setattr(
        mod,
        "get_nlp_pipeline",
        lambda: {
            "segmenter": mod.Segmenter(),
            "morph_vocab": (lambda _w: [types.SimpleNamespace(normal="норм")]),
            "morph_tagger": None,
        },
    )
    monkeypatch.setattr(mod, "load_stopwords", lambda *args: set())

    metrics = mod.calculate_metrics_from_text("тест")
    assert metrics is not None
    assert metrics["most_common_lemma"] == "норм"


def test_check_water_returns_1_when_no_metrics(tmp_path: Path, monkeypatch):
    md = tmp_path / "t.md"
    md.write_text("тест", encoding="utf-8")
    monkeypatch.setattr(mod, "calculate_metrics", lambda _file: None)
    assert mod.check_water(str(md), 40, 60) == 1


def test_check_water_warn_below_min(tmp_path: Path, monkeypatch, capsys):
    md = tmp_path / "t.md"
    md.write_text("тест", encoding="utf-8")

    monkeypatch.setattr(
        mod,
        "calculate_metrics",
        lambda _file: {
            "total_words": 100,
            "unique_lemmas": 90,
            "water_percent": 30.0,  # below min
            "water_percent_raw": 12.5,
            "water_count": 13,
            "classic_nausea": 3.0,
            "most_common_lemma": "тест",
            "max_frequency": 9,
            "academic_nausea": 8.0,
            "most_common_significant": "тест",
            "max_freq_significant": 3,
            "total_significant": 30,
            "lemma_repetition_index": 10.0,
            "repeated_words_count": 10,
        },
    )

    assert mod.check_water(str(md), 40, 60) == 0
    assert "Ниже минимума" in capsys.readouterr().out


def test_check_water_warn_classic_nausea_between_35_and_40(tmp_path: Path, monkeypatch, capsys):
    md = tmp_path / "t.md"
    md.write_text("тест", encoding="utf-8")

    monkeypatch.setattr(
        mod,
        "calculate_metrics",
        lambda _file: {
            "total_words": 100,
            "unique_lemmas": 90,
            "water_percent": 50.0,
            "water_percent_raw": 20.8,
            "water_count": 21,
            "classic_nausea": 3.8,  # warning (<= 4.0)
            "most_common_lemma": "тест",
            "max_frequency": 15,
            "academic_nausea": 8.0,
            "most_common_significant": "тест",
            "max_freq_significant": 3,
            "total_significant": 30,
            "lemma_repetition_index": 10.0,
            "repeated_words_count": 10,
        },
    )

    assert mod.check_water(str(md), 40, 60) == 0
    assert "WARNING" in capsys.readouterr().out


def test_check_water_academic_branches(tmp_path: Path, monkeypatch, capsys):
    md = tmp_path / "t.md"
    md.write_text("тест", encoding="utf-8")

    base = {
        "total_words": 100,
        "unique_lemmas": 90,
        "water_percent": 50.0,
        "water_percent_raw": 20.8,
        "water_count": 21,
        "classic_nausea": 3.0,
        "most_common_lemma": "тест",
        "max_frequency": 9,
        "max_freq_significant": 0,
        "total_significant": 0,
        "lemma_repetition_index": 10.0,
        "repeated_words_count": 10,
    }

    # No significant repeats
    monkeypatch.setattr(
        mod,
        "calculate_metrics",
        lambda _file: {**base, "academic_nausea": 0.0, "most_common_significant": None},
    )
    assert mod.check_water(str(md), 40, 60) == 0
    assert "Нет повторяющихся значимых слов" in capsys.readouterr().out

    # "Dry" info (< 7.0)
    monkeypatch.setattr(
        mod,
        "calculate_metrics",
        lambda _file: {**base, "academic_nausea": 5.0, "most_common_significant": "тест"},
    )
    assert mod.check_water(str(md), 40, 60) == 0
    assert "INFO" in capsys.readouterr().out

    # Warning (9.5 < x <= 12.0)
    monkeypatch.setattr(
        mod,
        "calculate_metrics",
        lambda _file: {**base, "academic_nausea": 11.0, "most_common_significant": "тест"},
    )
    assert mod.check_water(str(md), 40, 60) == 0
    assert "WARNING" in capsys.readouterr().out


def test_main_success_calls_check_water_defaults(tmp_path: Path, monkeypatch):
    md = tmp_path / "t.md"
    md.write_text("тест", encoding="utf-8")

    called = {}

    def _check_water(file_path, target_min, target_max):
        called["args"] = (file_path, target_min, target_max)
        return 0

    monkeypatch.setattr(mod, "check_water", _check_water)
    assert mod.main([str(md)]) == 0
    assert called["args"][1:] == (40, 60)

    assert mod.main([str(md), "45", "65"]) == 0
    assert called["args"][1:] == (45, 65)
