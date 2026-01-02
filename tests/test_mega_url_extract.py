"""
Tests for mega_url_extract.py — MEGA URL Aggregation

Tests cover:
1. CLI parser help
2. Exit codes
3. Aggregation + deduplication
"""

from __future__ import annotations

from pathlib import Path

from scripts.mega_url_extract import build_parser, main


class TestMegaUrlExtractCli:
    def test_help_includes_args(self):
        help_text = build_parser().format_help()
        assert "--categories-dir" in help_text
        assert "--output-dir" in help_text
        assert "--min-urls" in help_text


class TestMegaUrlExtractIntegration:
    def test_no_cluster_files_returns_error(self, tmp_path: Path):
        empty_cats = tmp_path / "empty_cats"
        empty_cats.mkdir()
        output_dir = tmp_path / "output"

        assert main(["--categories-dir", str(empty_cats), "--output-dir", str(output_dir)]) == 2

    def test_successful_extraction_with_cluster_files(self, tmp_path: Path):
        cat1 = tmp_path / "categories" / "cat1" / "competitors"
        cat1.mkdir(parents=True)
        (cat1 / "cluster_urls.txt").write_text(
            "\n".join([f"https://site{i}.com/page" for i in range(15)]) + "\n",
            encoding="utf-8",
        )

        cat2 = tmp_path / "categories" / "cat2" / "competitors"
        cat2.mkdir(parents=True)
        (cat2 / "cluster_urls.txt").write_text(
            "\n".join([f"https://other{i}.com/page" for i in range(15)]) + "\n",
            encoding="utf-8",
        )

        output_dir = tmp_path / "output"
        assert main(["--categories-dir", str(tmp_path / "categories"), "--output-dir", str(output_dir)]) == 0

        assert (output_dir / "mega_urls.txt").exists()
        urls = (output_dir / "mega_urls.txt").read_text(encoding="utf-8").strip().split("\n")
        assert len(urls) == 30

    def test_deduplication_works(self, tmp_path: Path):
        cat1 = tmp_path / "categories" / "cat1" / "competitors"
        cat1.mkdir(parents=True)
        (cat1 / "cluster_urls.txt").write_text(
            "https://shared.com/page\n" + "\n".join([f"https://unique1-{i}.com" for i in range(20)]) + "\n",
            encoding="utf-8",
        )

        cat2 = tmp_path / "categories" / "cat2" / "competitors"
        cat2.mkdir(parents=True)
        (cat2 / "cluster_urls.txt").write_text(
            "https://shared.com/page\n" + "\n".join([f"https://unique2-{i}.com" for i in range(10)]) + "\n",
            encoding="utf-8",
        )

        output_dir = tmp_path / "output"
        assert main(["--categories-dir", str(tmp_path / "categories"), "--output-dir", str(output_dir)]) == 0

        urls = (output_dir / "mega_urls.txt").read_text(encoding="utf-8").strip().split("\n")
        assert len(urls) == 31

    def test_warning_for_low_url_count(self, tmp_path: Path):
        cat1 = tmp_path / "categories" / "cat1" / "competitors"
        cat1.mkdir(parents=True)
        (cat1 / "cluster_urls.txt").write_text(
            "\n".join([f"https://site{i}.com" for i in range(15)]) + "\n",
            encoding="utf-8",
        )

        output_dir = tmp_path / "output"
        assert main(["--categories-dir", str(tmp_path / "categories"), "--output-dir", str(output_dir)]) == 1

