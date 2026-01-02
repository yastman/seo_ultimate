"""
End-to-end-ish tests for check_simple_v2_md.check_content() to raise coverage.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# Import as script-style module (scripts dir on sys.path).
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import check_simple_v2_md as mod  # noqa: E402


def test_check_content_pass_happy_path(tmp_path: Path, monkeypatch):
    # Make tier requirements permissive for a small test file.
    monkeypatch.setattr(
        mod,
        "get_tier_requirements",
        lambda _tier: {
            "char_min": 0,
            "char_max": 10_000,
            "min_words": 1,
            "max_words": 10_000,
            "water_min": 40.0,
            "water_max": 60.0,
            "nausea_classic_max": 3.5,
            "nausea_classic_blocker": 4.0,
            "nausea_academic_min": 7.0,
            "nausea_academic_max": 9.5,
            "coverage": 0.30,
        },
    )

    # Avoid natasha runtime in this test; still cover check_nausea_metrics branches.
    monkeypatch.setattr(mod, "NAUSEA_AVAILABLE", True)
    monkeypatch.setattr(
        mod,
        "calculate_metrics_from_text",
        lambda _md: {"water_percent": 50.0, "classic_nausea": 3.0, "academic_nausea": 8.0},
    )

    slug = "aktivnaya-pena"
    cat_dir = tmp_path / "categories" / slug
    (cat_dir / "content").mkdir(parents=True)
    (cat_dir / "data").mkdir(parents=True)

    # Minimal keyword JSON for density_distribution.
    (cat_dir / "data" / f"{slug}.json").write_text(
        json.dumps(
            {
                "keywords": {
                    "primary": [
                        {
                            "keyword": "активная пена",
                            "density_target": "0.5%",
                            "occurrences_target": 2,
                            "variations": {"exact": ["активная пена"], "partial": []},
                        }
                    ],
                    "secondary": [],
                    "supporting": [],
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    md_file = cat_dir / "content" / f"{slug}_ru.md"
    md_file.write_text(
        "\n".join(
            [
                "---",
                "title: \"" + ("А" * 55) + "\"",
                "description: \"" + ("Б" * 150) + "\"",
                "---",
                "# Активная пена",
                "",
                " ".join(["вводный"] * 120),
                "",
                "Активная пена для мойки — это средство.",
                "",
                "## Как выбрать активную пену",
                "Текст с активной пеной.",
                "## Преимущества активной пены",
                "Текст.",
                "## FAQ",
                "### Как использовать?",
                "Ответ.",
                "### Подходит ли?",
                "Ответ.",
                "### Где купить?",
                "Ответ.",
                "",
                "[Ссылка на доставку](/delivery)",
                "[Каталог автохимии](/catalog)",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    results = mod.check_content(str(md_file), "активная пена", "B")
    assert results["status"] in ("PASS", "REVIEW")  # depends on density severity heuristics
    assert results["checks"]["char_count"]["pass"] is True
    assert results["checks"]["h1"]["pass"] is True
    assert "density_distribution" in results["checks"]
    assert "nausea_water" in results["checks"]


def test_check_content_density_skipped_without_categories_path(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(mod, "get_tier_requirements", lambda _tier: {"char_min": 0, "char_max": 999999, "min_words": 0, "max_words": 999999, "coverage": 0.3})
    monkeypatch.setattr(mod, "NAUSEA_AVAILABLE", False)

    md_file = tmp_path / "x.md"
    md_file.write_text("# H1\n\nintro\n\n## H2\n", encoding="utf-8")

    results = mod.check_content(str(md_file), "intro", "B")
    assert "density_distribution" in results["checks"]
    assert results["checks"]["density_distribution"]["pass"] is True
