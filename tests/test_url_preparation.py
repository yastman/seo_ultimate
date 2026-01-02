"""
Tests for url_preparation_filter_and_validate.py — URL filtering and validation

Tests cover:
1. CLI arg handling (task JSON and legacy args)
2. Blacklist filtering via analyze_url_category()
3. Output JSON + output files
4. /ua/ fixing logic (via monkeypatched HTTP checker)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

import scripts.url_preparation_filter_and_validate as mod


class TestUrlPreparationCli:
    def test_missing_args_returns_json_error(self, capsys: pytest.CaptureFixture[str]):
        rc = mod.main([])
        out = capsys.readouterr().out
        assert rc == 2
        payload = json.loads(out)
        assert payload["status"] == "FAIL"
        assert "Usage" in payload["error"]

    def test_help_prints_usage(self, capsys: pytest.CaptureFixture[str]):
        rc = mod.main(["--help"])
        out = capsys.readouterr().out
        assert rc == 0
        assert "Usage:" in out

    def test_nonexistent_task_file(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]):
        rc = mod.main([str(tmp_path / "nonexistent.json")])
        out = capsys.readouterr().out
        assert rc == 2
        payload = json.loads(out)
        assert payload["status"] == "FAIL"
        assert "not found" in payload["error"].lower()

    def test_too_many_args_returns_json_error(self, capsys: pytest.CaptureFixture[str]):
        rc = mod.main(["a", "b", "c"])
        out = capsys.readouterr().out
        assert rc == 2
        payload = json.loads(out)
        assert payload["status"] == "FAIL"
        assert "Usage" in payload["error"]


def test_script_standalone_inserts_project_root(monkeypatch):
    script_path = (
        Path(__file__).parent.parent / "scripts" / "url_preparation_filter_and_validate.py"
    )
    monkeypatch.setattr(sys, "argv", ["url_preparation_filter_and_validate.py"])
    monkeypatch.setattr(sys, "path", ["__sentinel__"])

    code = script_path.read_text(encoding="utf-8")
    compiled = compile(code, str(script_path), "exec")
    globals_dict = {"__name__": "__main__", "__package__": None, "__file__": str(script_path)}
    with pytest.raises(SystemExit):
        exec(compiled, globals_dict)  # noqa: S102

    assert sys.path[0] == str(script_path.resolve().parent.parent)


class TestUrlPreparationIntegration:
    def test_missing_urls_raw_file_in_task(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ):
        cat_dir = tmp_path / "categories" / "test-slug"
        cat_dir.mkdir(parents=True)
        logs_dir = cat_dir / ".logs"
        logs_dir.mkdir()

        urls_raw_file = cat_dir / "urls_raw.txt"  # intentionally not created
        urls_out_file = cat_dir / "urls.txt"

        task = {
            "slug": "test-slug",
            "paths": {
                "urls_raw": str(urls_raw_file),
                "urls": str(urls_out_file),
                "logs": str(logs_dir),
            },
        }
        task_file = tmp_path / "task_test-slug.json"
        task_file.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")

        rc = mod.main([str(task_file)])
        out = capsys.readouterr().out
        payload = json.loads(out)

        assert rc == 2
        assert payload["status"] == "FAIL"
        assert "urls file not found" in payload["error"].lower()

    def test_processes_valid_task_file_success(
        self, tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]
    ):
        cat_dir = tmp_path / "categories" / "test-slug"
        cat_dir.mkdir(parents=True)
        logs_dir = cat_dir / ".logs"
        logs_dir.mkdir()

        urls_raw = [
            "https://shop1.com/catalog/pena",
            "https://shop2.com/category/foam",
            "https://shop3.com/ua/catalog/pena",
            "https://shop4.com/catalog/other",
            "https://shop5.com/category/x",
            "https://rozetka.com.ua/should-be-filtered",
            "https://shop6.com/contact",
        ]
        urls_raw_file = cat_dir / "urls_raw.txt"
        urls_raw_file.write_text("\n".join(urls_raw) + "\n", encoding="utf-8")

        urls_out_file = cat_dir / "urls.txt"

        task = {
            "slug": "test-slug",
            "paths": {
                "urls_raw": str(urls_raw_file),
                "urls": str(urls_out_file),
                "logs": str(logs_dir),
            },
        }
        task_file = tmp_path / "task_test-slug.json"
        task_file.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")

        def fake_accessibility(url: str, *args, **kwargs) -> bool:
            # Only the /ua/ removal should be checked; everything else should pass.
            return "/ua/" not in url

        monkeypatch.setattr(mod, "check_url_accessibility", fake_accessibility)
        monkeypatch.setattr(mod.time, "sleep", lambda *_args, **_kwargs: None)

        rc = mod.main([str(task_file)])
        out = capsys.readouterr().out
        payload = json.loads(out)

        assert rc == 0
        assert payload["status"] == "SUCCESS"
        assert payload["raw_urls"] == 7
        assert payload["excluded_count"] >= 1
        assert Path(payload["output_file"]).exists()
        assert Path(payload["log_file"]).exists()

        validated_urls = urls_out_file.read_text(encoding="utf-8").splitlines()
        assert any("rozetka.com.ua" in u for u in urls_raw)
        assert all("rozetka.com.ua" not in u for u in validated_urls)
        assert all("/ua/" not in u for u in validated_urls)

    def test_ua_fix_strategy_replaces_with_ru_when_remove_fails(
        self, tmp_path: Path, monkeypatch, capsys
    ):
        cat_dir = tmp_path / "categories" / "test-slug"
        cat_dir.mkdir(parents=True)
        logs_dir = cat_dir / ".logs"
        logs_dir.mkdir()

        urls_raw_file = cat_dir / "urls_raw.txt"
        urls_out_file = cat_dir / "urls.txt"
        urls_raw_file.write_text(
            "\n".join(
                [
                    "https://site.com/ua/catalog/pena",
                    "https://site.com/catalog/other1",
                    "https://site.com/catalog/other2",
                    "https://site.com/catalog/other3",
                    "https://site.com/catalog/other4",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        task = {
            "slug": "test-slug",
            "paths": {
                "urls_raw": str(urls_raw_file),
                "urls": str(urls_out_file),
                "logs": str(logs_dir),
            },
        }
        task_file = tmp_path / "task.json"
        task_file.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(mod, "analyze_url_category", lambda _url: (True, "ok"))

        original = "https://site.com/ua/catalog/pena"
        url_without_ua = original.replace("/ua/", "/")
        url_with_ru = original.replace("/ua/", "/ru/")

        def fake_access(url: str, *args, **kwargs) -> bool:
            # Force: remove fails, RU succeeds.
            if url == url_without_ua:
                return False
            if url == url_with_ru:
                return True
            return True

        monkeypatch.setattr(mod, "check_url_accessibility", fake_access)
        monkeypatch.setattr(mod.time, "sleep", lambda *_args, **_kwargs: None)

        rc = mod.main([str(task_file)])
        assert rc == 0
        err = capsys.readouterr().err
        assert "Replaced /ua/ → /ru/ → 200 OK" in err

    def test_ua_fix_strategy_keeps_original_when_ru_fails_but_original_ok(
        self, tmp_path: Path, monkeypatch, capsys
    ):
        cat_dir = tmp_path / "categories" / "test-slug"
        cat_dir.mkdir(parents=True)
        logs_dir = cat_dir / ".logs"
        logs_dir.mkdir()

        urls_raw_file = cat_dir / "urls_raw.txt"
        urls_out_file = cat_dir / "urls.txt"
        original = "https://site.com/ua/catalog/pena"
        urls_raw_file.write_text(
            "\n".join(
                [
                    original,
                    "https://site.com/catalog/other1",
                    "https://site.com/catalog/other2",
                    "https://site.com/catalog/other3",
                    "https://site.com/catalog/other4",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        task = {
            "slug": "test-slug",
            "paths": {
                "urls_raw": str(urls_raw_file),
                "urls": str(urls_out_file),
                "logs": str(logs_dir),
            },
        }
        task_file = tmp_path / "task.json"
        task_file.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")

        monkeypatch.setattr(mod, "analyze_url_category", lambda _url: (True, "ok"))

        url_without_ua = original.replace("/ua/", "/")
        url_with_ru = original.replace("/ua/", "/ru/")

        def fake_access(url: str, *args, **kwargs) -> bool:
            # Force: remove fails, RU fails, original succeeds.
            if url == original:
                return True
            return url not in {url_without_ua, url_with_ru}

        monkeypatch.setattr(mod, "check_url_accessibility", fake_access)
        monkeypatch.setattr(mod.time, "sleep", lambda *_args, **_kwargs: None)

        rc = mod.main([str(task_file)])
        assert rc == 0
        err = capsys.readouterr().err
        assert "Keeping original (200 OK)" in err

    def test_legacy_args_mode(
        self, tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]
    ):
        urls_raw_file = tmp_path / "urls_raw.txt"
        urls_raw_file.write_text(
            "\n".join(
                [
                    "https://shop.com/catalog/test",
                    "https://rozetka.com.ua/filtered",
                    "https://shop.com/contact",
                    "https://shop.com/category/x",
                    "https://shop.com/catalog/y",
                    "https://shop.com/catalog/z",
                    "https://shop.com/category/extra",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        urls_out_file = tmp_path / "urls.txt"

        monkeypatch.setattr(mod, "check_url_accessibility", lambda *_a, **_k: True)
        monkeypatch.setattr(mod.time, "sleep", lambda *_args, **_kwargs: None)

        rc = mod.main([str(urls_raw_file), str(urls_out_file)])
        out = capsys.readouterr().out
        payload = json.loads(out)

        assert rc == 0
        assert payload["status"] == "SUCCESS"
        assert urls_out_file.exists()
        assert (tmp_path / ".logs").exists()

    def test_invalid_url_format_is_reported_and_skipped(
        self, tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]
    ):
        urls_raw_file = tmp_path / "urls_raw.txt"
        urls_raw_file.write_text(
            "\n".join(
                [
                    "https://shop.com/catalog/a",
                    "shop.com/catalog/invalid-no-scheme",
                    "https://shop.com/catalog/b",
                    "https://shop.com/catalog/c",
                    "https://shop.com/catalog/d",
                    "https://shop.com/catalog/e",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        urls_out_file = tmp_path / "urls.txt"

        monkeypatch.setattr(mod, "analyze_url_category", lambda url: (True, "forced category"))
        monkeypatch.setattr(mod, "check_url_accessibility", lambda *_a, **_k: True)
        monkeypatch.setattr(mod.time, "sleep", lambda *_args, **_kwargs: None)

        rc = mod.main([str(urls_raw_file), str(urls_out_file)])
        out, err = capsys.readouterr()
        payload = json.loads(out)

        assert rc == 0
        assert payload["status"] == "SUCCESS"
        assert "INVALID FORMAT" in err

        validated_urls = urls_out_file.read_text(encoding="utf-8").splitlines()
        assert "shop.com/catalog/invalid-no-scheme" not in validated_urls

    def test_ua_fix_all_strategies_fail_records_failed_fix(
        self, tmp_path: Path, monkeypatch, capsys: pytest.CaptureFixture[str]
    ):
        cat_dir = tmp_path / "categories" / "test-slug"
        cat_dir.mkdir(parents=True)
        logs_dir = cat_dir / ".logs"
        logs_dir.mkdir()

        urls_raw = [
            "https://shop.com/ua/catalog/pena",
            "https://shop.com/catalog/x",
            "https://shop.com/catalog/y",
        ]
        urls_raw_file = cat_dir / "urls_raw.txt"
        urls_raw_file.write_text("\n".join(urls_raw) + "\n", encoding="utf-8")

        urls_out_file = cat_dir / "urls.txt"

        task = {
            "slug": "test-slug",
            "paths": {
                "urls_raw": str(urls_raw_file),
                "urls": str(urls_out_file),
                "logs": str(logs_dir),
            },
        }
        task_file = tmp_path / "task_test-slug.json"
        task_file.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")

        def always_fail_accessibility(_url: str, *args, **kwargs) -> bool:
            return False

        monkeypatch.setattr(mod, "check_url_accessibility", always_fail_accessibility)
        monkeypatch.setattr(mod.time, "sleep", lambda *_args, **_kwargs: None)

        rc = mod.main([str(task_file)])
        out = capsys.readouterr().out
        payload = json.loads(out)

        assert rc == 1  # only 3 URLs -> WARNING threshold
        assert payload["status"] == "WARNING"
        assert payload["failed_fixes"] == 1

        log_text = Path(payload["log_file"]).read_text(encoding="utf-8")
        assert "FAILED FIXES" in log_text

    @pytest.mark.parametrize(
        ("urls", "expected_status", "expected_rc"),
        [
            (
                [
                    "https://shop.com/catalog/a",
                    "https://shop.com/catalog/b",
                    "https://shop.com/catalog/c",
                ],
                "WARNING",
                1,
            ),
            (["https://shop.com/catalog/a", "https://shop.com/catalog/b"], "FAIL", 2),
        ],
    )
    def test_status_thresholds_warning_and_fail(
        self,
        tmp_path: Path,
        monkeypatch,
        capsys: pytest.CaptureFixture[str],
        urls: list[str],
        expected_status: str,
        expected_rc: int,
    ):
        urls_raw_file = tmp_path / "urls_raw.txt"
        urls_raw_file.write_text("\n".join(urls) + "\n", encoding="utf-8")
        urls_out_file = tmp_path / "urls.txt"

        monkeypatch.setattr(mod, "analyze_url_category", lambda url: (True, "forced category"))
        monkeypatch.setattr(mod, "check_url_accessibility", lambda *_a, **_k: True)
        monkeypatch.setattr(mod.time, "sleep", lambda *_args, **_kwargs: None)

        rc = mod.main([str(urls_raw_file), str(urls_out_file)])
        out = capsys.readouterr().out
        payload = json.loads(out)

        assert rc == expected_rc
        assert payload["status"] == expected_status
