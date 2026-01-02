"""
Tests for extract_competitor_urls_v2.py — SERP competitor extraction

Tests cover:
1. Transliteration function
2. Blacklist checking
3. Pipeline run on small fixtures
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.extract_competitor_urls_v2 import (
    build_parser,
    build_competitors_df,
    is_blacklisted,
    load_clusters_df,
    load_serp_df,
    main,
    resolve_path,
    select_vch_keywords,
    transliterate_slug,
    write_outputs,
)


class TestTransliterateSlug:
    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("Активная пена", "aktivnaya-pena"),
            ("Автохимия", "avtokhimiya"),
            ("Мойка авто", "moyka-avto"),
            ("pH-нейтральный", "ph-neytralnyy"),
        ],
    )
    def test_russian_transliteration(self, input_text: str, expected: str):
        assert transliterate_slug(input_text) == expected

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("Київ", "kiyiv"),
            ("Україна", "ukrayina"),
            ("їжак", "yizhak"),
        ],
    )
    def test_ukrainian_transliteration(self, input_text: str, expected: str):
        assert transliterate_slug(input_text) == expected

    def test_spaces_to_dashes(self):
        assert transliterate_slug("активная пена") == "aktivnaya-pena"
        assert transliterate_slug("мойка  авто") == "moyka-avto"

    def test_preserves_latin_and_numbers(self):
        assert transliterate_slug("test123") == "test123"
        assert transliterate_slug("pH 10") == "ph-10"

    def test_removes_special_chars(self):
        assert transliterate_slug("test!@#$%") == "test"

    def test_strips_dashes(self):
        assert transliterate_slug(" test ") == "test"
        assert transliterate_slug("-test-") == "test"


class TestIsBlacklisted:
    @pytest.mark.parametrize(
        "url",
        [
            "https://prom.ua/catalog/auto",
            "https://www.prom.ua/search",
            "https://rozetka.com.ua/product/123",
            "https://epicentrk.ua/shop/himiya",
            "https://olx.ua/electronics",
            "https://m.olx.ua/auto",
            "https://youtube.com/watch?v=abc",
            "https://youtu.be/abc123",
        ],
    )
    def test_blacklisted_urls(self, url: str):
        assert is_blacklisted(url) is True

    @pytest.mark.parametrize(
        "url",
        [
            "https://auto-chem.com.ua/catalog",
            "https://detailing.ua/products",
            "https://moyka-avto.kiev.ua/services",
            "https://example.com/test",
        ],
    )
    def test_valid_urls_not_blocked(self, url: str):
        assert is_blacklisted(url) is False

    def test_handles_invalid_urls(self):
        assert is_blacklisted("") is False
        assert is_blacklisted("not-a-url") is False
        assert is_blacklisted(None) is False  # type: ignore[arg-type]


def test_resolve_path_relative(tmp_path: Path, monkeypatch):
    import scripts.extract_competitor_urls_v2 as mod

    monkeypatch.setattr(mod, "BASE_DIR", tmp_path)
    resolved = resolve_path("data/x.csv")
    assert str(resolved).startswith(str(tmp_path))


class TestCli:
    def test_help_includes_args(self):
        help_text = build_parser().format_help()
        assert "--slug" in help_text
        assert "--top-n" in help_text
        assert "--max-urls" in help_text
        assert "--max-per-domain" in help_text
        assert "--serp-file" in help_text
        assert "--clusters-file" in help_text

    def test_missing_required_slug_raises(self):
        with pytest.raises(SystemExit) as exc:
            main([])
        assert exc.value.code == 2


class TestPipelineSmallFixtures:
    def test_pipeline_runs_on_small_csv(self, tmp_path: Path):
        serp_file = tmp_path / "serp.csv"
        serp_file.write_text(
            "\n".join(
                [
                    "Phrase;URL;Position",
                    "активная пена;https://shop1.com/catalog/pena;1",
                    ";https://rozetka.com.ua/item/123;2",
                    ";https://shop2.com/catalog/pena;3",
                    "пена для мойки;https://shop1.com/catalog/pena;1",
                    ";https://shop3.com/catalog/foam;2",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        clusters_file = tmp_path / "clusters.csv"
        clusters_file.write_text(
            "\n".join(
                [
                    "Фраза,Запросы сред. [GA]",
                    "L1: Автохимия,",
                    "L2: Мойка,",
                    "L3: Активная пена,",
                    "активная пена,1000",
                    "пена для мойки,500",
                    "L3: Другая категория,",
                    "что-то другое,999",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        out_dir = tmp_path / "out"
        cats_dir = tmp_path / "categories"

        rc = main(
            [
                "--slug",
                "aktivnaya-pena",
                "--serp-file",
                str(serp_file),
                "--clusters-file",
                str(clusters_file),
                "--output-dir",
                str(out_dir),
                "--categories-dir",
                str(cats_dir),
                "--top-n",
                "2",
                "--max-urls",
                "3",
                "--max-per-domain",
                "2",
            ]
        )
        assert rc == 0

        urls_file = cats_dir / "aktivnaya-pena" / "competitors" / ".source" / "urls.txt"
        assert urls_file.exists()
        urls = urls_file.read_text(encoding="utf-8").splitlines()
        assert "https://rozetka.com.ua/item/123" not in urls
        assert "https://shop1.com/catalog/pena" in urls
        assert (out_dir / "screaming_frog_urls_ALL.txt").exists()


def test_load_serp_df_skips_rows_missing_position_and_bad_int(tmp_path: Path):
    serp_file = tmp_path / "serp.csv"
    serp_file.write_text(
        "\n".join(
            [
                "Phrase;URL;Position",
                "kw;https://example.com/x;",  # missing position
                ";https://example.com/y;not-int",  # bad position
                ";https://example.com/z;1",  # ok (current_phrase=kw)
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    df = load_serp_df(serp_file)
    assert len(df) == 1


def test_load_clusters_df_skips_empty_and_unscoped_rows(tmp_path: Path):
    clusters_file = tmp_path / "clusters.csv"
    clusters_file.write_text(
        "\n".join(
            [
                "Фраза,Запросы сред. [GA]",
                ",",  # empty phrase
                "kw-before-scope,100",  # no L1/L2/L3 yet
                "L1: A,",
                "L2: B,",
                "L3: C,",
                "kw,100",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    df = load_clusters_df(clusters_file)
    assert len(df) == 1


def test_select_vch_keywords_returns_empty_for_empty_df():
    import pandas as pd

    df = pd.DataFrame(columns=["l1", "l2", "l3", "keyword", "volume"])
    selected = select_vch_keywords(df, top_n=3)
    assert selected.empty


def test_build_competitors_df_respects_max_urls_per_domain(tmp_path: Path):
    import pandas as pd

    serp_df = pd.DataFrame(
        [
            {"keyword": "kw", "url": "https://a.com/x", "position": 1},
            {"keyword": "kw", "url": "https://a.com/y", "position": 2},
        ]
    )
    vch_df = pd.DataFrame(
        [
            {"l1": "L1", "l2": "L2", "l3": "L3", "keyword": "kw", "keyword_lower": "kw", "volume": 1000},
        ]
    )
    out = build_competitors_df(serp_df, vch_df, max_urls_per_category=10, max_urls_per_domain=0)
    assert out.iloc[0]["competitor_urls"] == []


def test_write_outputs_honors_output_override(tmp_path: Path):
    import pandas as pd

    df = pd.DataFrame(
        [
            {
                "l1": "L1",
                "l2": "L2",
                "l3": "Активная пена",
                "competitor_urls": ["https://a.com/x"],
                "vch_keywords_count": 1,
                "total_volume": 1,
                "competitors_count": 1,
            }
        ]
    )
    out_dir = tmp_path / "out"
    cats_dir = tmp_path / "cats"
    override = tmp_path / "override.txt"

    write_outputs(
        df,
        categories_dir=cats_dir,
        output_dir=out_dir,
        top_n_keywords=1,
        max_urls_per_category=1,
        max_urls_per_domain=1,
        output_override=str(override),
    )
    assert override.exists()


def test_main_errors_cover_missing_files_and_empty_inputs(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    # Missing SERP file.
    rc = main(["--slug", "x", "--serp-file", str(tmp_path / "no.csv"), "--clusters-file", str(tmp_path / "c.csv")])
    assert rc == 2
    assert "SERP file not found" in capsys.readouterr().out

    # Missing clusters file.
    serp_file = tmp_path / "serp.csv"
    serp_file.write_text("Phrase;URL;Position\nkw;https://a.com/x;1\n", encoding="utf-8")
    rc = main(["--slug", "x", "--serp-file", str(serp_file), "--clusters-file", str(tmp_path / "no.csv")])
    assert rc == 2
    assert "Clusters file not found" in capsys.readouterr().out

    # Empty SERP parsed.
    empty_serp = tmp_path / "empty_serp.csv"
    empty_serp.write_text("Phrase;URL;Position\n", encoding="utf-8")
    clusters_file = tmp_path / "clusters.csv"
    clusters_file.write_text("Фраза,Запросы сред. [GA]\nL1: A,\nL2: B,\nL3: C,\nkw,100\n", encoding="utf-8")
    rc = main(["--slug", "c", "--serp-file", str(empty_serp), "--clusters-file", str(clusters_file)])
    assert rc == 2
    assert "SERP file parsed as empty" in capsys.readouterr().out

    # Clusters parsed as empty.
    bad_clusters = tmp_path / "bad_clusters.csv"
    bad_clusters.write_text("Фраза,Запросы сред. [GA]\nkw,100\n", encoding="utf-8")
    rc = main(["--slug", "c", "--serp-file", str(serp_file), "--clusters-file", str(bad_clusters)])
    assert rc == 2


def test_main_category_not_found_and_vch_empty(tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]):
    serp_file = tmp_path / "serp.csv"
    serp_file.write_text("Phrase;URL;Position\nkw;https://a.com/x;1\n", encoding="utf-8")

    clusters_file = tmp_path / "clusters.csv"
    clusters_file.write_text(
        "\n".join(["Фраза,Запросы сред. [GA]", "L1: A,", "L2: B,", "L3: Cat,", "kw,100"]) + "\n",
        encoding="utf-8",
    )

    # Category not found.
    rc = main(["--slug", "missing", "--serp-file", str(serp_file), "--clusters-file", str(clusters_file)])
    assert rc == 2
    assert "не найдена" in capsys.readouterr().out.lower()

    # VCH keywords empty when top-n=0.
    rc = main(
        [
            "--slug",
            "cat",
            "--serp-file",
            str(serp_file),
            "--clusters-file",
            str(clusters_file),
            "--top-n",
            "0",
        ]
    )
    assert rc == 2
    assert "No VCH keywords selected" in capsys.readouterr().out

    # Competitors empty.
    import pandas as pd
    import scripts.extract_competitor_urls_v2 as mod

    monkeypatch.setattr(mod, "build_competitors_df", lambda *_a, **_k: pd.DataFrame([]))
    rc = mod.main(
        [
            "--slug",
            "cat",
            "--serp-file",
            str(serp_file),
            "--clusters-file",
            str(clusters_file),
            "--top-n",
            "1",
        ]
    )
    assert rc == 2
    assert "No competitors extracted" in capsys.readouterr().out
