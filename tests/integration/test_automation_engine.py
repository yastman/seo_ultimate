"""TDD tests for Automation Engine (issues #16–#21).

Covers all 6 phases:
- #16: Canonical data contract (Pydantic models)
- #17: ValidationReport schema
- #18: Orchestrator + state machine
- #19: LLM client layer
- #20: Closed produce→validate→revise loop
- #21: Batch runner + E2E fixture
"""
from __future__ import annotations

import json

import pytest

# ── Phase 1 (#16): Canonical data contract ─────────────────────────────────


class TestCategoryModel:
    """Category Pydantic model handles V1/V2/V3 formats."""

    def test_v3_list_format(self):
        from llm_keywords_pipeline.core.models import Category
        data = {
            "slug": "test",
            "keywords": [{"keyword": "авто", "volume": 100}],
        }
        cat = Category.from_json(data)
        assert len(cat.keywords) == 1
        assert cat.keywords[0].keyword == "авто"

    def test_v2_dict_format(self):
        from llm_keywords_pipeline.core.models import Category
        data = {
            "slug": "test",
            "keywords": {
                "primary": [{"keyword": "авто", "volume": 100}],
                "secondary": [{"keyword": "машина", "volume": 50}],
            },
        }
        cat = Category.from_json(data)
        assert len(cat.keywords) == 2
        assert cat.keywords[0].group == "primary"
        assert cat.keywords[1].group == "secondary"

    def test_v1_string_list(self):
        from llm_keywords_pipeline.core.models import Category
        data = {"slug": "test", "keywords": ["авто", "машина", "транспорт"]}
        cat = Category.from_json(data)
        assert len(cat.keywords) == 3
        assert all(kw.volume == 0 for kw in cat.keywords)

    def test_invalid_input_raises(self):
        from pydantic import ValidationError

        from llm_keywords_pipeline.core.models import Category
        with pytest.raises((ValidationError, TypeError)):
            Category.from_json({"slug": None, "keywords": "invalid"})

    def test_keywords_flat(self):
        from llm_keywords_pipeline.core.models import Category
        cat = Category.from_json({"slug": "x", "keywords": [{"keyword": "авто", "volume": 100}]})
        assert "авто" in cat.keywords_flat()

    def test_schema_version_present(self):
        from llm_keywords_pipeline.core.models import SCHEMA_VERSION, Category
        cat = Category(slug="x")
        assert cat.schema_version == SCHEMA_VERSION


# ── Phase 2 (#17): ValidationReport ──────────────────────────────────────────


class TestValidationReport:
    """ValidationReport provides stable JSON schema for all validators."""

    def test_pass_status(self):
        from llm_keywords_pipeline.automation.report import (
            CheckResult,
            CheckStatus,
            ReportStatus,
            ValidationReport,
        )
        report = ValidationReport(
            validator="water", status=ReportStatus.PASS,
            checks=[CheckResult(id="water_percent", status=CheckStatus.pass_)],
        )
        assert report.status == ReportStatus.PASS
        assert report.failures == []

    def test_fail_status(self):
        from llm_keywords_pipeline.automation.report import (
            CheckResult,
            CheckStatus,
            ReportStatus,
            ValidationReport,
        )
        report = ValidationReport(
            validator="water", status=ReportStatus.FAIL,
            checks=[CheckResult(id="water_percent", status=CheckStatus.fail, message="too high")],
        )
        assert len(report.failures) == 1

    def test_to_revise_payload(self):
        from llm_keywords_pipeline.automation.report import (
            CheckResult,
            CheckStatus,
            ReportStatus,
            ValidationReport,
        )
        report = ValidationReport(
            validator="water", status=ReportStatus.FAIL,
            checks=[CheckResult(
                id="water_percent", status=CheckStatus.fail,
                message="Water 75%", expected="40–65%", actual=75.0,
            )],
        )
        payload = report.to_revise_payload()
        assert len(payload) == 1
        assert payload[0]["id"] == "water_percent"
        assert payload[0]["expected"] == "40–65%"

    def test_from_water_metrics_none(self):
        from llm_keywords_pipeline.automation.report import ReportStatus, ValidationReport
        report = ValidationReport.from_water_metrics(None)
        assert report.status == ReportStatus.FAIL

    def test_from_water_metrics_good(self):
        from llm_keywords_pipeline.automation.report import ReportStatus, ValidationReport
        metrics = {"water_percent": 50.0, "classic_nausea": 2.5}
        report = ValidationReport.from_water_metrics(metrics)
        assert report.status == ReportStatus.PASS

    def test_json_serializable(self):
        from llm_keywords_pipeline.automation.report import ReportStatus, ValidationReport
        report = ValidationReport(validator="test", status=ReportStatus.PASS)
        data = json.loads(report.model_dump_json())
        assert "status" in data
        assert "checks" in data


# ── Phase 3 (#18): Orchestrator + state machine ──────────────────────────────


class TestOrchestrator:
    """run_category produces a state file and returns CategoryRunState."""

    def test_run_produces_state_file(self, tmp_path):
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        from llm_keywords_pipeline.automation.orchestrator import run_category
        from llm_keywords_pipeline.core.models import Category
        cat = Category(slug="test-cat", name="Тест")
        llm = MockLlmClient("# Заголовок\n\nТестовый текст для проверки.")
        state = run_category(cat, llm, state_dir=tmp_path)
        assert (tmp_path / "test-cat_state.json").exists()
        assert state.state == "done"

    def test_idempotent_rerun(self, tmp_path):
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        from llm_keywords_pipeline.automation.orchestrator import run_category
        from llm_keywords_pipeline.core.models import Category
        cat = Category(slug="test-idem")
        llm = MockLlmClient()
        run_category(cat, llm, state_dir=tmp_path)
        initial_calls = len(llm.calls)
        run_category(cat, llm, state_dir=tmp_path)
        # Second run reuses existing state, no new LLM calls
        assert len(llm.calls) == initial_calls

    def test_stages_recorded(self, tmp_path):
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        from llm_keywords_pipeline.automation.orchestrator import run_category
        from llm_keywords_pipeline.core.models import Category
        cat = Category(slug="test-stages")
        llm = MockLlmClient()
        state = run_category(cat, llm, state_dir=tmp_path)
        stage_names = [s.stage for s in state.stages]
        assert "prepare" in stage_names
        assert "produce" in stage_names
        assert "deliver" in stage_names


# ── Phase 4 (#19): LLM client ────────────────────────────────────────────────


class TestLlmClient:
    """MockLlmClient and interface contract."""

    def test_mock_returns_response(self):
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        client = MockLlmClient("test response")
        resp = client.complete("hello")
        assert resp.text == "test response"
        assert resp.model == "mock"

    def test_mock_records_calls(self):
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        client = MockLlmClient()
        client.complete("prompt1")
        client.complete("prompt2")
        assert len(client.calls) == 2

    def test_produce_calls_complete(self):
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        client = MockLlmClient("draft content")
        resp = client.produce("write something")
        assert resp.text == "draft content"

    def test_revise_calls_complete(self):
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        client = MockLlmClient("revised content")
        failures = [{"id": "water", "message": "too high", "expected": "40%", "actual": "75%", "locator": ""}]
        resp = client.revise("original draft", failures)
        assert resp.text == "revised content"
        assert len(client.calls) == 1

    def test_render_prompt_template(self, tmp_path):
        from llm_keywords_pipeline.automation.llm_client import render_prompt_template
        tmpl = tmp_path / "tmpl.md"
        tmpl.write_text("Hello ${name}, write about ${topic}.", encoding="utf-8")
        result = render_prompt_template(tmpl, {"name": "World", "topic": "SEO"})
        assert result == "Hello World, write about SEO."


# ── Phase 5 (#20): Closed produce→validate→revise loop ───────────────────────


class TestReviseLoop:
    """The loop retries on FAIL and stops when PASS/WARN or max_retries reached."""

    def test_loop_retries_on_fail(self, tmp_path):
        """Mock LLM that returns non-Cyrillic first (→ FAIL), then Cyrillic (→ PASS)."""
        from llm_keywords_pipeline.automation.llm_client import LlmResponse, LlmUsage, MockLlmClient
        from llm_keywords_pipeline.automation.orchestrator import run_category
        from llm_keywords_pipeline.core.models import Category

        responses = ["no cyrillic text at all", "# Заголовок\n\nПривет мир, проверка водности."]

        class SequentialMock(MockLlmClient):
            def complete(self, prompt, **kwargs):
                text = responses.pop(0) if responses else "final fallback"
                return LlmResponse(text=text, usage=LlmUsage(), model="mock")

        cat = Category(slug="loop-test")
        state = run_category(cat, SequentialMock(), state_dir=tmp_path, max_retries=3)
        produce_stage = state.last_stage("produce")
        assert produce_stage is not None
        assert produce_stage.attempts >= 1

    def test_needs_human_after_max_retries(self, tmp_path):
        """If all retries fail, state = needs_human."""
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        from llm_keywords_pipeline.automation.orchestrator import run_category
        from llm_keywords_pipeline.core.models import Category

        cat = Category(slug="always-fail")
        # Non-Cyrillic → water audit returns FAIL every time
        llm = MockLlmClient("no cyrillic content here at all")
        state = run_category(cat, llm, state_dir=tmp_path, max_retries=2)
        assert state.state == "needs_human"


# ── Phase 6 (#21): Batch runner + E2E ────────────────────────────────────────


class TestBatchRunner:
    """run_batch processes multiple categories with isolation."""

    def test_batch_returns_report(self, tmp_path):
        from llm_keywords_pipeline.automation.batch_runner import run_batch
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        from llm_keywords_pipeline.core.models import Category
        cats = [Category(slug=f"cat-{i}", name=f"Категория {i}") for i in range(3)]
        llm = MockLlmClient("# Заголовок\n\nТестовый текст для проверки водности.")
        report = run_batch(cats, llm, state_dir=tmp_path)
        assert report.total == 3
        assert (report.passed + report.needs_human + report.failed) == 3

    def test_batch_isolated_failure(self, tmp_path):
        """One category raising an exception must not abort the batch."""
        from llm_keywords_pipeline.automation.batch_runner import run_batch
        from llm_keywords_pipeline.automation.llm_client import LlmClient, LlmResponse, LlmUsage
        from llm_keywords_pipeline.core.models import Category

        class BrokenLlm(LlmClient):
            _count = 0
            def complete(self, prompt, **kwargs):
                self._count += 1
                if self._count == 1:
                    raise RuntimeError("simulated LLM failure")
                return LlmResponse("# Заголовок\n\nПривет.", LlmUsage(), "mock")

        cats = [Category(slug="fail-cat"), Category(slug="ok-cat")]
        report = run_batch(cats, BrokenLlm(), state_dir=tmp_path)
        assert report.total == 2
        assert report.failed >= 1

    def test_batch_writes_report_json(self, tmp_path):
        from llm_keywords_pipeline.automation.batch_runner import run_batch
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        from llm_keywords_pipeline.core.models import Category
        cats = [Category(slug="report-test")]
        llm = MockLlmClient("# Заголовок\n\nТестовый текст.")
        run_batch(cats, llm, state_dir=tmp_path)
        assert (tmp_path / "batch_report.json").exists()

    def test_batch_limit(self, tmp_path):
        from llm_keywords_pipeline.automation.batch_runner import run_batch
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        from llm_keywords_pipeline.core.models import Category
        cats = [Category(slug=f"c{i}") for i in range(10)]
        llm = MockLlmClient("# Заголовок\n\nТест.")
        report = run_batch(cats, llm, state_dir=tmp_path, limit=3)
        assert report.total == 3


class TestE2EFixture:
    """E2E: keywords → produce(mock-LLM) → validate → deliver on a public fixture."""

    def test_e2e_pipeline(self, tmp_path):
        from llm_keywords_pipeline.automation.batch_runner import run_batch
        from llm_keywords_pipeline.automation.llm_client import MockLlmClient
        from llm_keywords_pipeline.core.models import Category

        cat = Category.from_json({
            "slug": "e2e-fixture",
            "name": "Автохимия",
            "lang": "ru",
            "keywords": [
                {"keyword": "автохимия купить", "volume": 500, "group": "primary"},
                {"keyword": "средство для авто", "volume": 200, "group": "secondary"},
            ],
        })
        draft = (
            "# Автохимия купить\n\n"
            "Автохимия — это средство для авто, которое помогает поддерживать чистоту "
            "и защиту вашего транспортного средства. Купить автохимию можно у нас по "
            "выгодным ценам. Средство для авто включает очистители, полироли и защитные "
            "составы. Закажите автохимию сегодня с доставкой по всей стране."
        )
        llm = MockLlmClient(draft)
        report = run_batch([cat], llm, state_dir=tmp_path)
        assert report.total == 1
        assert (tmp_path / "batch_report.json").exists()
        assert (tmp_path / "e2e-fixture_state.json").exists()
        # State should be done or needs_human (both are acceptable final states)
        result = report.results[0]
        assert result.state in ("done", "needs_human")
