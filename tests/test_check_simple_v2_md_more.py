"""
Extra TDD tests for check_simple_v2_md.py to cover error branches and parsing logic.
"""

from __future__ import annotations

import json

# Import in the same way scripts are typically executed (scripts dir on sys.path).
import sys
from pathlib import Path

import pytest


sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import check_simple_v2_md as mod  # noqa: E402


def test_parse_markdown_file_with_yaml(tmp_path: Path):
    md = tmp_path / "x.md"
    md.write_text("---\ntitle: T\n---\n# H1\n\nbody\n", encoding="utf-8")
    meta, content = mod.parse_markdown_file(str(md))
    assert meta.get("title") == "T"
    assert "# H1" in content


def test_parse_markdown_file_yaml_error(tmp_path: Path, monkeypatch):
    md = tmp_path / "x.md"
    md.write_text("---\n: bad\n---\n# H1\n", encoding="utf-8")
    # Force YAML parser to raise
    monkeypatch.setattr(
        mod.yaml, "safe_load", lambda *_a, **_k: (_ for _ in ()).throw(mod.yaml.YAMLError("bad"))
    )
    meta, _content = mod.parse_markdown_file(str(md))
    assert meta == {}


def test_extract_text_content_fallback(monkeypatch):
    monkeypatch.setattr(mod, "UTILS_AVAILABLE", False)
    out = mod.extract_text_content("# H1\n\n**bold** [x](y)\n")
    assert "H1" in out
    assert "bold" in out


def test_keyword_density_missing_json_file(tmp_path: Path):
    result = mod.check_keyword_density_and_distribution("text", str(tmp_path / "no.json"), 100, {})
    assert result["errors"]


def test_keyword_density_bad_json(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    result = mod.check_keyword_density_and_distribution("text", str(p), 100, {})
    assert result["errors"]


def test_keyword_density_no_keywords_in_json(tmp_path: Path):
    p = tmp_path / "empty.json"
    p.write_text(json.dumps({"keywords": {}}), encoding="utf-8")
    result = mod.check_keyword_density_and_distribution("text", str(p), 100, {})
    assert result["errors"]


def test_keyword_density_word_count_zero(tmp_path: Path):
    p = tmp_path / "k.json"
    p.write_text(
        json.dumps(
            {
                "keywords": {
                    "primary": [
                        {
                            "keyword": "активная пена",
                            "density_target": "0.5%",
                            "occurrences_target": 1,
                        }
                    ]
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    result = mod.check_keyword_density_and_distribution("активная пена", str(p), 0, {})
    assert result["keywords_total"] >= 1
    assert result["total_density"] == 0.0


def test_keyword_density_variations_fallback_counts(tmp_path: Path):
    p = tmp_path / "k.json"
    p.write_text(
        json.dumps(
            {
                "keywords": {
                    "primary": [
                        {
                            "keyword": "активная пена",
                            "density_target": "0.5%",
                            "occurrences_target": 1,
                            "variations": {},
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
    md = "Активная пена. Активную пену."
    result = mod.check_keyword_density_and_distribution(md, str(p), 4, {})
    assert result["keywords_found"] == 1
    assert result["details"]


def test_cli_main_writes_json_report(tmp_path: Path, monkeypatch):
    # Make checks permissive and fast.
    monkeypatch.setattr(
        mod,
        "get_tier_requirements",
        lambda _tier: {
            "char_min": 0,
            "char_max": 999999,
            "min_words": 0,
            "max_words": 999999,
            "coverage": 0.3,
            "water_min": 40.0,
            "water_max": 60.0,
            "nausea_classic_max": 3.5,
            "nausea_classic_blocker": 4.0,
            "nausea_academic_min": 7.0,
            "nausea_academic_max": 9.5,
        },
    )
    monkeypatch.setattr(mod, "NAUSEA_AVAILABLE", False)

    slug = "slug"
    cat_dir = tmp_path / "categories" / slug
    (cat_dir / "content").mkdir(parents=True)
    (cat_dir / "data").mkdir(parents=True)
    (cat_dir / "data" / f"{slug}.json").write_text(
        json.dumps(
            {
                "keywords": {
                    "primary": [
                        {
                            "keyword": "активная пена",
                            "density_target": "0.5%",
                            "occurrences_target": 1,
                        }
                    ]
                }
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    md_file = cat_dir / "content" / f"{slug}_ru.md"
    md_file.write_text(
        "# Активная пена\n\nАктивная пена.\n\n## H2\n\n[ok](/x)\n[ok2](/y)\n\n## FAQ\n### Q?\nA\n### Q2?\nA\n### Q3?\nA\n",
        encoding="utf-8",
    )

    # Run main via sys.argv style and catch SystemExit.
    monkeypatch.setattr(
        mod.sys, "argv", ["check_simple_v2_md.py", str(md_file), "активная пена", "B", "--json"]
    )
    with pytest.raises(SystemExit) as exc:
        mod.main()
    assert exc.value.code in (0, 1, 2)

    assert (md_file.parent / f"{md_file.stem}_validation.json").exists()
