from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.mega_url_extract import (
    aggregate_raw_urls,
    aggregate_url_maps,
    find_cluster_files,
    main,
    normalize_url,
    read_urls_from_file,
    resolve_dir,
    save_mega_files,
)


def test_resolve_dir_relative(tmp_path: Path):
    resolved = resolve_dir(tmp_path, "data/mega")
    assert str(resolved).startswith(str(tmp_path))


def test_find_cluster_files_skips_non_dirs_and_missing_competitors(tmp_path: Path):
    categories_dir = tmp_path / "categories"
    categories_dir.mkdir()
    (categories_dir / "not_a_dir.txt").write_text("x", encoding="utf-8")

    (categories_dir / "cat_no_competitors").mkdir()

    cat_ok = categories_dir / "cat_ok" / "competitors"
    cat_ok.mkdir(parents=True)
    (cat_ok / "cluster_urls.txt").write_text("https://a.com\n", encoding="utf-8")

    cluster_files = find_cluster_files(categories_dir)
    assert "cat_ok" in cluster_files


def test_read_urls_from_file_missing_path_returns_empty():
    assert read_urls_from_file(None) == []  # type: ignore[arg-type]


def test_normalize_url_removes_trailing_slash():
    assert normalize_url("https://a.com/x/") == "https://a.com/x"


def test_aggregate_raw_urls_reads_raw_files(tmp_path: Path, capsys):
    raw = tmp_path / "raw.txt"
    raw.write_text("https://a.com/x\nhttps://b.com/y\n", encoding="utf-8")
    cluster_files = {"slug": {"raw": raw, "clean": raw, "map": None}}

    urls = aggregate_raw_urls(cluster_files)
    assert len(urls) == 2
    assert "raw URLs" in capsys.readouterr().out


def test_aggregate_url_maps_counts_rows(tmp_path: Path, capsys):
    map_file = tmp_path / "map.csv"
    with map_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["slug", "url"])
        writer.writeheader()
        writer.writerow({"slug": "a", "url": "https://a.com/x"})
        writer.writerow({"slug": "a", "url": "https://a.com/y"})

    cluster_files = {"a": {"raw": None, "clean": tmp_path / "clean.txt", "map": map_file}}
    (tmp_path / "clean.txt").write_text("https://a.com/x\n", encoding="utf-8")

    mappings = aggregate_url_maps(cluster_files)
    out = capsys.readouterr().out
    assert len(mappings) == 2
    assert "mappings" in out


def test_save_mega_files_writes_raw_and_map(tmp_path: Path):
    out_dir = tmp_path / "out"
    save_mega_files(
        out_dir,
        raw_urls=["https://a.com/x"],
        clean_urls=["https://a.com/x"],
        url_mappings=[{"slug": "a", "url": "https://a.com/x"}],
    )
    assert (out_dir / "mega_urls_raw.txt").exists()
    assert (out_dir / "mega_urls_map.csv").exists()


def test_main_categories_dir_missing_returns_2(tmp_path: Path):
    rc = main(["--categories-dir", str(tmp_path / "missing"), "--output-dir", str(tmp_path / "out")])
    assert rc == 2


def test_main_prints_removal_rate_when_raw_urls_present(tmp_path: Path, capsys):
    cat = tmp_path / "categories" / "cat1" / "competitors"
    cat.mkdir(parents=True)
    clean_urls = [f"https://a.com/{i}" for i in range(10)]
    raw_urls = clean_urls + ["https://a.com/0", "https://a.com/1"]
    (cat / "cluster_urls_raw.txt").write_text("\n".join(raw_urls) + "\n", encoding="utf-8")
    (cat / "cluster_urls.txt").write_text("\n".join(clean_urls) + "\n", encoding="utf-8")

    rc = main(["--categories-dir", str(tmp_path / "categories"), "--output-dir", str(tmp_path / "out"), "--min-urls", "1"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "Removal rate" in out


def test_main_fails_when_clean_urls_less_than_10(tmp_path: Path, capsys):
    cat = tmp_path / "categories" / "cat1" / "competitors"
    cat.mkdir(parents=True)
    (cat / "cluster_urls.txt").write_text("\n".join([f"https://a.com/{i}" for i in range(5)]) + "\n", encoding="utf-8")

    rc = main(["--categories-dir", str(tmp_path / "categories"), "--output-dir", str(tmp_path / "out")])
    out = capsys.readouterr().out
    assert rc == 2
    assert "FAIL" in out
