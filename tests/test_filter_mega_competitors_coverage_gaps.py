from __future__ import annotations

import csv
import json
import runpy
import sys
from pathlib import Path

import pytest

import scripts.filter_mega_competitors as mod


def test_script_standalone_inserts_project_root(monkeypatch):
    script_path = Path(__file__).parent.parent / "scripts" / "filter_mega_competitors.py"
    monkeypatch.setattr(sys, "argv", ["filter_mega_competitors.py"])
    monkeypatch.setattr(sys, "path", ["__sentinel__"])

    with pytest.raises(SystemExit):
        code = script_path.read_text(encoding="utf-8")
        exec(compile(code, str(script_path), "exec"), {"__name__": "__main__", "__package__": None, "__file__": str(script_path)})

    assert sys.path[0] == str(script_path.resolve().parent.parent)


def test_load_category_keywords_skips_unknown_types_and_honors_max(tmp_path: Path):
    # Place unknown type first so the "continue" branch executes before early return.
    data = {"keywords": {"primary": [123, {"keyword": "Активная пена"}, {"text": "пена"}], "secondary": [], "supporting": []}}
    fp = tmp_path / "cat.json"
    fp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    kws = mod.load_category_keywords(fp, max_keywords=1)
    assert kws == ["активная пена"]


def test_load_url_mapping_missing_file_returns_empty(tmp_path: Path):
    assert mod.load_url_mapping(tmp_path / "missing.csv", "s") == set()


def test_filter_rows_by_mapping_and_keywords_branches(monkeypatch, capsys):
    monkeypatch.setattr(mod, "is_blacklisted_domain", lambda _url: False)
    monkeypatch.setattr(mod, "is_category_page", lambda _url: (True, "ok"))
    monkeypatch.setattr(mod, "fix_ua_in_url", lambda url: url.replace("/ua/", "/"))

    rows = [
        {"Address": "https://x.com/a", "Status Code": "404", "Title 1": "t", "H1-1": "h"},  # status filter
        {"Address": "", "Status Code": "200", "Title 1": "t", "H1-1": "h"},  # missing URL
        {"Address": "https://x.com/ua/cat", "Status Code": "200", "Title 1": "nope", "H1-1": "nope"},  # ua fix + mismatch
        {"Address": "https://x.com/cat", "Status Code": "200", "Title 1": "nope", "H1-1": "nope"},  # duplicate (after fix)
        {"Address": "https://x.com/other", "Status Code": "200", "Title 1": "k", "H1-1": "k"},  # mapping skip
    ]

    filtered = mod.filter_rows_by_mapping_and_keywords(
        rows,
        category_urls={"https://x.com/cat"},
        keywords=["ключ"],
        use_mapping=True,
    )
    out = capsys.readouterr().out
    assert len(filtered) == 1
    assert filtered[0]["Address"] == "https://x.com/cat"
    assert "URLs in mapping but no keyword match" in out


def test_main_fallbacks_and_tier_autodetect_and_h2_fail(tmp_path: Path, monkeypatch, capsys):
    # Redirect base_dir by overriding __file__ (so main uses tmp_path as project root).
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    monkeypatch.setattr(mod, "__file__", str(scripts_dir / "filter_mega_competitors.py"))

    slug = "test-slug"
    cats_dir = tmp_path / "categories" / slug
    (cats_dir / "data").mkdir(parents=True)
    (cats_dir / "competitors").mkdir()

    # Only raw json exists (covers fallback selection branch).
    raw_json = cats_dir / "data" / f"{slug}.json"
    raw_json.write_text(
        json.dumps(
            {"tier": "A", "keywords": {"primary": [{"keyword": "активная пена"}], "secondary": [], "supporting": []}},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    mega_csv = tmp_path / "data" / "mega" / "mega_competitors.csv"
    mega_csv.parent.mkdir(parents=True)
    with mega_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Address", "Status Code", "Title 1", "H1-1", "Meta Description 1", "H2-1"])
        writer.writeheader()
        for i in range(8):
            writer.writerow(
                {
                    "Address": f"https://shop{i}.com/catalog/pena",
                    "Status Code": "200",
                    "Title 1": "Активная пена",
                    "H1-1": "Активная пена",
                    "Meta Description 1": "desc",
                    "H2-1": "Преимущества",
                }
            )

    monkeypatch.setattr(mod, "load_url_mapping", lambda *_a, **_k: set())
    monkeypatch.setattr(mod, "is_blacklisted_domain", lambda _url: False)
    monkeypatch.setattr(mod, "is_category_page", lambda _url: (True, "ok"))
    monkeypatch.setattr(mod, "fix_ua_in_url", lambda url: url)

    monkeypatch.setattr(sys, "argv", ["filter_mega_competitors.py", slug, "--min-h2-themes", "10"])
    rc = mod.main()
    out = capsys.readouterr().out
    assert rc == 2
    assert "EXCELLENT: 8+ competitors" in out
    assert "H2 themes" in out


def test_main_no_filtered_rows_returns_fail(tmp_path: Path, monkeypatch):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    monkeypatch.setattr(mod, "__file__", str(scripts_dir / "filter_mega_competitors.py"))

    slug = "test-slug"
    cats_dir = tmp_path / "categories" / slug / "data"
    cats_dir.mkdir(parents=True)
    (tmp_path / "categories" / slug / "competitors").mkdir(parents=True)
    (cats_dir / f"{slug}.json").write_text(
        json.dumps({"keywords": {"primary": [{"keyword": "активная пена"}], "secondary": [], "supporting": []}}, ensure_ascii=False),
        encoding="utf-8",
    )

    mega_csv = tmp_path / "data" / "mega" / "mega_competitors.csv"
    mega_csv.parent.mkdir(parents=True)
    with mega_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Address", "Status Code", "Title 1", "H1-1", "Meta Description 1"])
        writer.writeheader()
        writer.writerow({"Address": "https://shop.com/catalog/x", "Status Code": "200", "Title 1": "Контакты", "H1-1": "Контакты", "Meta Description 1": ""})

    monkeypatch.setattr(mod, "load_url_mapping", lambda *_a, **_k: set())
    monkeypatch.setattr(mod, "is_blacklisted_domain", lambda _url: False)
    monkeypatch.setattr(mod, "is_category_page", lambda _url: (True, "ok"))
    monkeypatch.setattr(mod, "fix_ua_in_url", lambda url: url)

    monkeypatch.setattr(sys, "argv", ["filter_mega_competitors.py", slug, "--min-competitors", "1", "--min-h2-themes", "1"])
    assert mod.main() == 2


def test_main_tier_autodetect_json_error_uses_default_min(tmp_path: Path, monkeypatch, capsys):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    monkeypatch.setattr(mod, "__file__", str(scripts_dir / "filter_mega_competitors.py"))

    slug = "test-slug"
    cats_dir = tmp_path / "categories" / slug
    (cats_dir / "data").mkdir(parents=True)
    (cats_dir / "competitors").mkdir()

    # File exists, but tier auto-detect will fail due to forced json.load error.
    (cats_dir / "data" / f"{slug}.json").write_text("{}", encoding="utf-8")

    mega_csv = tmp_path / "data" / "mega" / "mega_competitors.csv"
    mega_csv.parent.mkdir(parents=True)
    with mega_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Address", "Status Code", "Title 1", "H1-1", "Meta Description 1", "H2-1"])
        writer.writeheader()
        writer.writerow(
            {
                "Address": "https://shop.com/catalog/pena",
                "Status Code": "200",
                "Title 1": "Активная пена",
                "H1-1": "Активная пена",
                "Meta Description 1": "desc",
                "H2-1": "Преимущества",
            }
        )

    monkeypatch.setattr(mod, "load_category_keywords", lambda *_a, **_k: ["активная пена"])
    monkeypatch.setattr(mod, "load_url_mapping", lambda *_a, **_k: set())
    monkeypatch.setattr(mod, "filter_rows_by_mapping_and_keywords", lambda rows, *_a, **_k: rows)
    monkeypatch.setattr(mod.json, "load", lambda *_a, **_k: (_ for _ in ()).throw(ValueError("boom")))

    monkeypatch.setattr(sys, "argv", ["filter_mega_competitors.py", slug, "--min-h2-themes", "1"])
    rc = mod.main()
    out = capsys.readouterr().out
    assert rc == 2
    assert "Using default minimum" in out
