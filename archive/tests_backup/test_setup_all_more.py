"""
Extra TDD tests for setup_all.py to improve coverage.
"""

from __future__ import annotations

from pathlib import Path

import scripts.setup_all as mod


def test_setup_category_skips_when_exists(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(mod, "CATEGORIES_DIR", tmp_path / "categories")
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)

    slug = "exists"
    (mod.CATEGORIES_DIR / slug).mkdir(parents=True)

    result = mod.setup_category(slug, [{"keyword": "x", "volume": 1}])
    assert result["status"] == "skipped"
    assert result["reason"] == "exists"


def test_setup_category_force_overwrites(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(mod, "CATEGORIES_DIR", tmp_path / "categories")
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)

    slug = "force"
    (mod.CATEGORIES_DIR / slug).mkdir(parents=True, exist_ok=True)

    # Avoid depending on parse_semantics_to_json internals.
    monkeypatch.setattr(
        mod, "generate_full_json", lambda *_a, **_k: {"tier": "C", "keywords": {"primary": []}}
    )

    result = mod.setup_category(slug, [{"keyword": "x", "volume": 1}], force=True)
    assert result["status"] == "created"
    assert (tmp_path / f"task_{slug}.json").exists()
    assert (mod.CATEGORIES_DIR / slug / "data" / f"{slug}.json").exists()


def test_setup_all_aggregates_results(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(mod, "CATEGORIES_DIR", tmp_path / "categories")
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)

    monkeypatch.setattr(
        mod, "generate_full_json", lambda *_a, **_k: {"tier": "C", "keywords": {"primary": []}}
    )
    monkeypatch.setattr(
        mod,
        "get_all_categories_with_keywords",
        lambda: {
            "a": [{"keyword": "x", "volume": 1}] * 31,  # tier A
            "b": [{"keyword": "x", "volume": 1}] * 10,  # tier B
        },
    )

    results = mod.setup_all(force=False, dry_run=True)
    assert len(results) == 2
    assert {r["slug"] for r in results} == {"a", "b"}
    assert all(r["status"] == "dry_run" for r in results)


def test_print_summary_runs(tmp_path: Path, capsys):
    results = [
        {"slug": "a", "status": "created", "tier": "A", "keywords": 31},
        {"slug": "b", "status": "skipped", "tier": "B", "keywords": 10},
        {"slug": "c", "status": "dry_run", "tier": "C", "keywords": 3},
    ]
    mod.print_summary(results, dry_run=True)
    out = capsys.readouterr().out
    assert "Setup Summary" in out
    assert "Would create" in out


def test_main_list_mode(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr(
        mod,
        "get_all_categories_with_keywords",
        lambda: {
            "a": [{"keyword": "x", "volume": 1}] * 31,
            "b": [{"keyword": "x", "volume": 1}] * 5,
        },
    )
    rc = mod.main(["--list"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Categories from CSV" in out
    assert "Tier A" in out


def test_main_dry_run(tmp_path: Path, monkeypatch, capsys):
    monkeypatch.setattr(mod, "CATEGORIES_DIR", tmp_path / "categories")
    monkeypatch.setattr(mod, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(
        mod, "generate_full_json", lambda *_a, **_k: {"tier": "C", "keywords": {"primary": []}}
    )
    monkeypatch.setattr(
        mod, "get_all_categories_with_keywords", lambda: {"a": [{"keyword": "x", "volume": 1}]}
    )

    rc = mod.main(["--dry-run"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Setup Summary" in out


def test_create_keywords_json_returns_none_when_empty(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(mod, "CATEGORIES_DIR", tmp_path / "categories")
    assert mod.create_keywords_json("x", "B", [], dry_run=False) is None


def test_print_summary_non_dry_run_prints_created_and_skipped(capsys):
    results = [
        {"slug": "a", "status": "created", "tier": "A", "keywords": 31},
        {"slug": "b", "status": "skipped", "tier": "B", "keywords": 10},
    ]
    mod.print_summary(results, dry_run=False)
    out = capsys.readouterr().out
    assert "Created:" in out


def test_main_non_dry_run_prints_next_step(monkeypatch, capsys):
    monkeypatch.setattr(
        mod,
        "setup_all",
        lambda **_kw: [{"slug": "a", "status": "created", "tier": "B", "keywords": 10}],
    )
    monkeypatch.setattr(mod, "print_summary", lambda *_a, **_kw: None)
    rc = mod.main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "All categories initialized" in out
    assert "Next step" in out
