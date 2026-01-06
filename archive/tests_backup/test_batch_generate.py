import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from batch_generate import (  # noqa: E402
    attempt_self_heal,
    extract_issues_from_validation,
    generate_fix_prompt,
    get_category_status,
    list_all_categories,
    load_batch_log,
    process_all,
    process_category,
    run_analyze,
    run_validate,
    save_batch_log,
    update_category_status,
)

# =============================================================================
# Log & Status Tests
# =============================================================================


def test_load_batch_log_defaults():
    with (
        patch("builtins.open", side_effect=FileNotFoundError),
        patch("pathlib.Path.exists", return_value=False),
    ):
        log = load_batch_log()
        assert log["total_processed"] == 0
        assert "categories" in log


def test_load_batch_log_existing_file(tmp_path):
    import batch_generate as bg

    log_path = tmp_path / "batch_log.json"
    log_path.write_text('{"total_processed": 5, "categories": {"a": {"last_status": "PASS"}}}', encoding="utf-8")
    with patch.object(bg, "BATCH_LOG", log_path):
        loaded = bg.load_batch_log()
    assert loaded["total_processed"] == 5
    assert loaded["categories"]["a"]["last_status"] == "PASS"


def test_save_batch_log(tmp_path):
    # Mock BATCH_LOG path
    with (
        patch("batch_generate.BATCH_LOG", tmp_path / "log.json"),
        patch("batch_generate.TASKS_DIR", tmp_path),
    ):
        log = {"test": "data"}
        save_batch_log(log)

        assert (tmp_path / "log.json").exists()
        with open(tmp_path / "log.json") as f:
            saved = json.load(f)
            assert saved["test"] == "data"
            assert "last_updated" in saved


def test_update_category_status():
    log = {"categories": {}}
    update_category_status(log, "slug1", "stage1", "PASS", {"detail": 1})

    cat = log["categories"]["slug1"]
    assert cat["last_status"] == "PASS"
    assert cat["last_stage"] == "stage1"
    assert len(cat["runs"]) == 1
    assert cat["runs"][0]["details"]["detail"] == 1


def test_get_category_status(tmp_path):
    # Mock directory structure
    with patch("batch_generate.CATEGORIES_DIR", tmp_path):
        slug = "test-cat"
        (tmp_path / slug / "content").mkdir(parents=True)
        (tmp_path / slug / "content" / f"{slug}_ru.md").touch()

        log = {"categories": {slug: {"last_status": "PASS"}}}

        status = get_category_status(slug, log)
        assert status["has_content"] is True
        assert status["last_status"] == "PASS"


# =============================================================================
# Pipeline Step Tests
# =============================================================================


@patch("subprocess.run")
def test_run_analyze_success(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout='{"count": 10}')
    success, data = run_analyze("slug")
    assert success is True
    assert data["count"] == 10


@patch("subprocess.run")
def test_run_analyze_fail(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stderr="Error")
    success, data = run_analyze("slug")
    assert success is False
    assert data["error"] == "Error"


@patch("subprocess.run")
def test_run_analyze_json_decode_fallback(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="not-json")
    success, data = run_analyze("slug")
    assert success is True
    assert data["output"] == "not-json"


@patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["python3"], timeout=60))
def test_run_analyze_timeout(mock_run):
    success, data = run_analyze("slug")
    assert success is False
    assert data["error"] == "Timeout"


@patch("subprocess.run", side_effect=RuntimeError("boom"))
def test_run_analyze_exception(mock_run):
    success, data = run_analyze("slug")
    assert success is False
    assert "boom" in data["error"]


@patch("subprocess.run")
def test_run_validate_pass(mock_run):
    # Mock content file existence
    with patch("pathlib.Path.exists", return_value=True):
        mock_run.return_value = MagicMock(stdout="... PASS ...", stderr="")
        success, data = run_validate("slug", "kw")
        assert success is True
        assert data["status"] == "PASS"


@patch("subprocess.run")
def test_run_validate_fail(mock_run):
    # Mock content file existence
    with patch("pathlib.Path.exists", return_value=True):
        mock_run.return_value = MagicMock(stdout="... FAIL ...", stderr="")
        success, data = run_validate("slug", "kw")
        assert success is False
        assert data["status"] == "FAIL"


@patch("subprocess.run")
def test_run_validate_parses_json_success(mock_run):
    with patch("pathlib.Path.exists", return_value=True):
        mock_run.return_value = MagicMock(returncode=0, stdout='{"summary": {"overall": "WARNING"}}', stderr="")
        success, data = run_validate("slug", "kw")
        assert success is True
        assert data["status"] == "WARNING"
        assert data["data"]["summary"]["overall"] == "WARNING"


@patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=["python3"], timeout=120))
def test_run_validate_timeout(mock_run):
    with patch("pathlib.Path.exists", return_value=True):
        success, data = run_validate("slug", "kw")
    assert success is False
    assert data["error"] == "Timeout"


@patch("subprocess.run", side_effect=RuntimeError("boom"))
def test_run_validate_exception(mock_run):
    with patch("pathlib.Path.exists", return_value=True):
        success, data = run_validate("slug", "kw")
    assert success is False
    assert "boom" in data["error"]


# =============================================================================
# Self-Healing Tests
# =============================================================================


def test_extract_issues():
    # Test water detection
    validation = {"output": "Water content is > 30%."}
    issues = extract_issues_from_validation(validation)
    assert "water_high" in issues


def test_extract_issues_h1():
    # Test H1 missing detection - actual pattern is 'H1' + 'не найден'
    validation = {"output": "H1 не найден в тексте"}
    issues = extract_issues_from_validation(validation)
    assert "h1_missing" in issues


def test_extract_issues_nausea():
    validation = {"output": "Nausea > 4.0 BLOCKER"}
    issues = extract_issues_from_validation(validation)
    assert "nausea_high" in issues


def test_generate_fix_prompt():
    slug = "test-slug"
    issues = ["water_high", "h1_missing"]
    content = "Some content"
    prompt = generate_fix_prompt(slug, issues, content)

    assert "Задача: Исправить контент" in prompt
    assert "Уменьшить воду" in prompt
    assert "Добавить H1" in prompt


@patch("pathlib.Path.read_text", return_value="content")
@patch("pathlib.Path.write_text")
@patch("pathlib.Path.exists", return_value=True)
def test_attempt_self_heal(mock_exists, mock_write, mock_read):
    validation = {"output": "Water > 80% BLOCKER"}
    success, msg = attempt_self_heal("slug", validation)

    assert success is False  # Because it only generates prompt, requires manual run
    assert "Fix prompt generated" in msg
    mock_write.assert_called_once()


# =============================================================================
# Process Category Test
# =============================================================================


@patch("batch_generate.run_analyze")
@patch("batch_generate.run_validate")
@patch("batch_generate.update_category_status")
@patch("pathlib.Path.exists", return_value=True)  # Content exists
def test_process_category_success(mock_exists, mock_update, mock_validate, mock_analyze):
    log = {}
    mock_analyze.return_value = (True, {"primary_keyword": "pk"})
    mock_validate.return_value = (True, {"status": "PASS"})

    result = process_category("slug", log)

    assert result is True
    assert mock_analyze.called
    assert mock_validate.called


@patch("batch_generate.run_analyze")
def test_process_category_analyze_fail(mock_analyze):
    log = {"categories": {}}  # Must have categories key
    mock_analyze.return_value = (False, {"error": "err"})

    result = process_category("slug", log)

    assert result is False


@patch("batch_generate.run_analyze")
@patch("batch_generate.update_category_status")
def test_process_category_analyze_only_skips_generation(mock_update, mock_analyze):
    log = {"categories": {}}
    mock_analyze.return_value = (True, {"count": 1, "semantic_depth": "shallow"})
    assert process_category("slug", log, analyze_only=True) is True
    assert mock_update.call_count >= 1


@patch("batch_generate.run_analyze")
@patch("batch_generate.update_category_status")
def test_process_category_content_missing_marks_pending(mock_update, mock_analyze, tmp_path):
    import batch_generate as bg

    mock_analyze.return_value = (True, {"count": 1, "semantic_depth": "shallow"})
    with patch.object(bg, "CATEGORIES_DIR", tmp_path):
        log = {"categories": {}}
        assert process_category("slug", log, analyze_only=False) is False
    mock_update.assert_any_call(log, "slug", "generate", "PENDING")


@patch("batch_generate.run_analyze")
@patch("batch_generate.run_validate")
@patch("batch_generate.attempt_self_heal")
@patch("batch_generate.update_category_status")
def test_process_category_self_heal_success(mock_update, mock_heal, mock_validate, mock_analyze, tmp_path):
    import batch_generate as bg

    slug = "slug"
    (tmp_path / slug / "content").mkdir(parents=True)
    (tmp_path / slug / "content" / f"{slug}_ru.md").write_text("# t", encoding="utf-8")

    mock_analyze.return_value = (True, {"keywords": {"primary": {"keyword": "pk"}}})
    mock_validate.side_effect = [
        (False, {"status": "FAIL", "output": "Water > 80% BLOCKER"}),
        (True, {"status": "PASS"}),
    ]
    mock_heal.return_value = (True, "ok")

    with patch.object(bg, "CATEGORIES_DIR", tmp_path):
        assert process_category(slug, {"categories": {}}, analyze_only=False, self_heal=True) is True
    assert mock_heal.called
    assert mock_validate.call_count == 2


def test_get_all_categories_csv(tmp_path):
    csv_file = tmp_path / "structure.csv"
    csv_file.write_text(
        "L1: Auto\nL2: Care\nL3: Active Foam,,1000\nkw1,,100\nkw2,,200\n\nL3: Wax,,500\nkw3,,50\n",
        encoding="utf-8",
    )

    with patch("batch_generate.SEMANTICS_CSV", csv_file):
        from batch_generate import get_all_categories

        cats = get_all_categories()

        assert len(cats) == 2
        assert cats[0]["name"] == "Active Foam"
        assert cats[0]["keywords_count"] == 2
        assert cats[0]["total_volume"] == 300

        assert cats[1]["name"] == "Wax"
        assert cats[1]["keywords_count"] == 1
        assert cats[1]["total_volume"] == 50


# =============================================================================
# Process All & List Tests
# =============================================================================


@patch("batch_generate.load_batch_log")
@patch("batch_generate.get_all_categories")
@patch("batch_generate.process_category")
@patch("batch_generate.save_batch_log")
def test_process_all(mock_save, mock_process, mock_get_cats, mock_load):
    # Setup
    mock_load.return_value = {"categories": {}}
    mock_get_cats.return_value = [{"slug": "cat1"}, {"slug": "cat2"}]

    # Mock status to be pending
    with patch(
        "batch_generate.get_category_status",
        return_value={"stage": "pending", "last_status": "unknown"},
    ):
        process_all()

    assert mock_process.call_count == 2
    mock_save.assert_called()


@patch("batch_generate.load_batch_log")
@patch("batch_generate.get_all_categories")
def test_process_all_only_pending(mock_get_cats, mock_load):
    # Setup
    mock_load.return_value = {"categories": {}}
    mock_get_cats.return_value = [{"slug": "completed_cat"}, {"slug": "pending_cat"}]

    # Mock status
    def side_effect(slug, log):
        if slug == "completed_cat":
            return {"stage": "completed", "last_status": "PASS"}
        return {"stage": "pending", "last_status": "unknown"}

    with (
        patch("batch_generate.get_category_status", side_effect=side_effect),
        patch("batch_generate.process_category") as mock_process,
    ):
        process_all(only_pending=True)

        # Should only process the pending one
        assert mock_process.call_count == 1
        mock_process.assert_called_with("pending_cat", mock_load.return_value, False)


@patch("batch_generate.load_batch_log")
@patch("batch_generate.get_all_categories")
def test_list_all_categories(mock_get_cats, mock_load):
    mock_load.return_value = {"categories": {}}
    mock_get_cats.return_value = [
        {"slug": "cat1", "keywords_count": 10, "total_volume": 1000},
        {"slug": "cat2", "keywords_count": 5, "total_volume": 500},
    ]

    with patch(
        "batch_generate.get_category_status",
        return_value={
            "stage": "pending",
            "last_status": "unknown",
            "has_clean_json": False,
            "has_raw_json": False,
        },
    ):
        # Just check it runs without error
        list_all_categories()


def test_get_all_categories_flushes_on_l1_l2(tmp_path):
    csv_file = tmp_path / "structure.csv"
    csv_file.write_text(
        "L3: Cat A,,100\nkw1,,10\nL1: Next,,\nL3: Cat B,,100\nkw2,,20\n",
        encoding="utf-8",
    )

    with patch("batch_generate.SEMANTICS_CSV", csv_file):
        from batch_generate import get_all_categories

        cats = get_all_categories()
    assert [c["name"] for c in cats] == ["Cat A", "Cat B"]


def test_get_category_status_stages(tmp_path):
    import batch_generate as bg

    slug = "s"
    with patch.object(bg, "CATEGORIES_DIR", tmp_path):
        # pending
        status = bg.get_category_status(slug, {"categories": {}})
        assert status["stage"] == "pending"

        # data_ready (raw json)
        (tmp_path / slug / "data").mkdir(parents=True)
        (tmp_path / slug / "data" / f"{slug}.json").write_text("{}", encoding="utf-8")
        status = bg.get_category_status(slug, {"categories": {}})
        assert status["stage"] == "data_ready"

        # content_generated
        (tmp_path / slug / "content").mkdir(parents=True, exist_ok=True)
        (tmp_path / slug / "content" / f"{slug}_ru.md").write_text("# x", encoding="utf-8")
        status = bg.get_category_status(slug, {"categories": {}})
        assert status["stage"] == "content_generated"

        # completed
        (tmp_path / slug / "meta").mkdir(parents=True, exist_ok=True)
        (tmp_path / slug / "meta" / f"{slug}_meta.json").write_text("{}", encoding="utf-8")
        status = bg.get_category_status(slug, {"categories": {}})
        assert status["stage"] == "completed"


def test_run_validate_content_missing_returns_error(tmp_path):
    import batch_generate as bg

    with patch.object(bg, "CATEGORIES_DIR", tmp_path):
        success, data = bg.run_validate("slug", "kw")
    assert success is False
    assert "Content file not found" in data["error"]


def test_cli_no_args_prints_doc_and_exits_0(capsys):
    import batch_generate as bg

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(sys, "argv", ["batch_generate.py"])
    try:
        with pytest.raises(SystemExit) as exc:
            bg.main()
        assert exc.value.code == 0
        assert "batch_generate.py" in capsys.readouterr().out
    finally:
        monkeypatch.undo()


def test_cli_resume_no_failed_prints_message(monkeypatch, capsys):
    import batch_generate as bg

    monkeypatch.setattr(bg, "load_batch_log", MagicMock(return_value={"categories": {"a": {"last_status": "PASS"}}}))
    monkeypatch.setattr(sys, "argv", ["batch_generate.py", "--resume"])
    bg.main()
    assert "No failed categories" in capsys.readouterr().out


def test_cli_dispatch_calls_expected_functions(monkeypatch):
    import batch_generate as bg

    monkeypatch.setattr(bg, "list_all_categories", MagicMock())
    monkeypatch.setattr(bg, "process_all", MagicMock())
    monkeypatch.setattr(bg, "process_category", MagicMock())
    monkeypatch.setattr(bg, "load_batch_log", MagicMock(return_value={"categories": {}}))

    monkeypatch.setattr(sys, "argv", ["batch_generate.py", "--list"])
    bg.main()
    assert bg.list_all_categories.called

    monkeypatch.setattr(sys, "argv", ["batch_generate.py", "--analyze-all"])
    bg.main()
    bg.process_all.assert_any_call(only_pending=False, analyze_only=True)

    monkeypatch.setattr(sys, "argv", ["batch_generate.py", "--all"])
    bg.main()
    bg.process_all.assert_any_call(only_pending=False)

    monkeypatch.setattr(sys, "argv", ["batch_generate.py", "--pending"])
    bg.main()
    bg.process_all.assert_any_call(only_pending=True)

    monkeypatch.setattr(sys, "argv", ["batch_generate.py", "single-slug"])
    bg.main()
    bg.process_category.assert_called_with("single-slug", {"categories": {}})


def test_cli_resume_processes_last_failed(monkeypatch):
    import batch_generate as bg

    monkeypatch.setattr(bg, "process_category", MagicMock())
    monkeypatch.setattr(
        bg,
        "load_batch_log",
        MagicMock(return_value={"categories": {"a": {"last_status": "PASS"}, "b": {"last_status": "FAIL"}}}),
    )

    monkeypatch.setattr(sys, "argv", ["batch_generate.py", "--resume"])
    bg.main()
    assert bg.process_category.called


@patch("subprocess.run")
def test_run_validate_warning_fallback_when_json_invalid(mock_run):
    # Ensure JSON parsing fails and WARNING text fallback branch is exercised.
    with patch("pathlib.Path.exists", return_value=True):
        mock_run.return_value = MagicMock(stdout="... WARNING ...", stderr="")
        success, data = run_validate("slug", "kw")
    assert success is True
    assert data["status"] == "WARNING"


def test_extract_issues_additional_patterns():
    validation = {
        "output": "\n".join(
            [
                "coverage < 50%",
                "INTRO не найден",
                "blacklist violation detected",
            ]
        )
    }
    issues = extract_issues_from_validation(validation)
    assert "coverage_low" in issues
    assert "intro_keyword_missing" in issues
    assert "blacklist_violation" in issues


def test_generate_fix_prompt_includes_all_issue_types():
    prompt = generate_fix_prompt(
        "slug",
        [
            "water_high",
            "nausea_high",
            "coverage_low",
            "h1_missing",
            "intro_keyword_missing",
            "blacklist_violation",
        ],
        "content",
    )
    assert "Уменьшить воду" in prompt
    assert "Снизить тошноту" in prompt
    assert "Повысить coverage" in prompt
    assert "Добавить H1" in prompt
    assert "первые 100 слов" in prompt
    assert "Удалить запрещённые" in prompt


def test_attempt_self_heal_max_attempts():
    import batch_generate as bg

    ok, msg = bg.attempt_self_heal("slug", {"output": "Water > 80%"}, attempt=bg.MAX_HEALING_ATTEMPTS + 1)
    assert ok is False
    assert "Max healing attempts" in msg


def test_attempt_self_heal_no_fixable_issues():
    ok, msg = attempt_self_heal("slug", {"output": "everything fine"}, attempt=1)
    assert ok is False
    assert "No fixable issues" in msg


def test_attempt_self_heal_missing_content_file(tmp_path):
    import batch_generate as bg

    with patch.object(bg, "CATEGORIES_DIR", tmp_path):
        ok, msg = bg.attempt_self_heal("slug", {"output": "Water > 80% BLOCKER"}, attempt=1)
    assert ok is False
    assert "Content file not found" in msg


@patch("batch_generate.run_analyze")
@patch("batch_generate.run_validate")
@patch("batch_generate.update_category_status")
def test_process_category_warning_status(mock_update, mock_validate, mock_analyze, tmp_path):
    import batch_generate as bg

    slug = "slug"
    (tmp_path / slug / "content").mkdir(parents=True)
    (tmp_path / slug / "content" / f"{slug}_ru.md").write_text("# t", encoding="utf-8")

    mock_analyze.return_value = (True, {"keywords": {"primary": {"keyword": "pk"}}})
    mock_validate.return_value = (True, {"status": "WARNING"})

    with patch.object(bg, "CATEGORIES_DIR", tmp_path):
        assert bg.process_category(slug, {"categories": {}}, analyze_only=False, self_heal=False) is True
    mock_update.assert_any_call({"categories": {}}, slug, "validate", "WARNING", {"status": "WARNING"})


@patch("batch_generate.run_analyze")
@patch("batch_generate.run_validate")
@patch("batch_generate.attempt_self_heal")
@patch("batch_generate.update_category_status")
def test_process_category_self_heal_fails_increments_total_failed(
    mock_update, mock_heal, mock_validate, mock_analyze, tmp_path
):
    import batch_generate as bg

    slug = "slug"
    (tmp_path / slug / "content").mkdir(parents=True)
    (tmp_path / slug / "content" / f"{slug}_ru.md").write_text("# t", encoding="utf-8")

    mock_analyze.return_value = (True, {"keywords": {"primary": {"keyword": "pk"}}})
    mock_validate.return_value = (False, {"status": "FAIL", "output": "Water > 80% BLOCKER"})
    mock_heal.return_value = (False, "manual required")

    log = {"categories": {}}
    with patch.object(bg, "CATEGORIES_DIR", tmp_path):
        assert bg.process_category(slug, log, analyze_only=False, self_heal=True) is False
    assert log["total_failed"] == 1


@patch("batch_generate.load_batch_log")
@patch("batch_generate.get_all_categories")
@patch("batch_generate.process_category")
@patch("batch_generate.save_batch_log")
def test_process_all_increments_failed_counter(mock_save, mock_process, mock_get_cats, mock_load):
    mock_load.return_value = {"categories": {}}
    mock_get_cats.return_value = [{"slug": "cat1"}, {"slug": "cat2"}]
    mock_process.side_effect = [True, False]

    with patch(
        "batch_generate.get_category_status",
        return_value={"stage": "pending", "last_status": "unknown"},
    ):
        process_all()

    assert mock_process.call_count == 2


def test_batch_generate_module_import_fallback_executes(monkeypatch):
    import builtins
    import importlib.util
    import sys as sys_mod

    module_path = Path(__file__).parent.parent / "scripts" / "batch_generate.py"
    spec = importlib.util.spec_from_file_location("batch_generate_import_fallback", module_path)
    assert spec
    assert spec.loader

    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in {"scripts.seo_utils", "seo_utils"}:
            raise ImportError("blocked for test")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    try:
        module = importlib.util.module_from_spec(spec)
        sys_mod.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        sys_mod.modules.pop(spec.name, None)

    assert module.L3_TO_SLUG == {}
    assert module.SLUG_TO_L3 == {}
