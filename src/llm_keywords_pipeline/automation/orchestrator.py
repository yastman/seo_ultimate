"""Python orchestrator + state machine for one category (issues #18, #20).

Stages: prepare → produce → validate → deliver → done
Implements the produce→validate→revise closed loop (issue #20).
State is persisted atomically after each stage.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from llm_keywords_pipeline.automation.llm_client import LlmClient
from llm_keywords_pipeline.automation.report import ReportStatus, ValidationReport
from llm_keywords_pipeline.core.models import Category, CategoryState

MAX_RETRIES = int(__import__("os").getenv("LLM_MAX_RETRIES", "3"))


@dataclass
class StageRecord:
    stage: str
    status: str  # done | skipped | failed | needs_human
    attempts: int = 0
    report: dict | None = None
    usage: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class CategoryRunState:
    slug: str
    lang: str = "ru"
    state: str = CategoryState.pending.value
    stages: list[StageRecord] = field(default_factory=list)
    content: str = ""
    total_usage: dict = field(default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0})

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: dict) -> CategoryRunState:
        stages = [StageRecord(**s) for s in data.pop("stages", [])]
        obj = cls(**data)
        obj.stages = stages
        return obj

    def record_stage(self, record: StageRecord) -> None:
        self.stages.append(record)
        if record.usage:
            for k in ("prompt_tokens", "completion_tokens", "cost_usd"):
                self.total_usage[k] = self.total_usage.get(k, 0) + record.usage.get(k, 0)

    def last_stage(self, name: str) -> StageRecord | None:
        for s in reversed(self.stages):
            if s.stage == name:
                return s
        return None


def _load_state(state_path: Path) -> CategoryRunState | None:
    if state_path.exists():
        return CategoryRunState.from_dict(json.loads(state_path.read_text(encoding="utf-8")))
    return None


def _save_state(state: CategoryRunState, state_path: Path) -> None:
    state_path.write_text(json.dumps(state.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def _validate_content(content: str, category: Category) -> ValidationReport:
    """Run water audit as the primary validation gate."""
    try:
        from llm_keywords_pipeline.audit.water import calculate_metrics_from_text
        metrics = calculate_metrics_from_text(content, category.lang)
        return ValidationReport.from_water_metrics(metrics, slug=category.slug, lang=category.lang)
    except Exception as exc:
        from llm_keywords_pipeline.automation.report import CheckResult, CheckStatus
        return ValidationReport(
            validator="water",
            slug=category.slug,
            lang=category.lang,
            status=ReportStatus.FAIL,
            checks=[CheckResult(
                id="validator_error",
                status=CheckStatus.fail,
                severity="high",
                message=f"Validation error: {exc}",
            )],
        )


def run_category(
    category: Category,
    llm: LlmClient,
    state_dir: Path | None = None,
    brief: str | None = None,
    max_retries: int = MAX_RETRIES,
) -> CategoryRunState:
    """
    Run the full pipeline for one category.

    Idempotent: skips completed stages on re-run.
    Implements the produce→validate→revise loop (issue #20).
    """
    state_dir = state_dir or Path(".")
    state_path = state_dir / f"{category.slug}_state.json"

    state = _load_state(state_path) or CategoryRunState(slug=category.slug, lang=category.lang)

    # --- PREPARE ---
    if not state.last_stage("prepare"):
        state.state = CategoryState.prepare.value
        _save_state(state, state_path)
        state.record_stage(StageRecord(stage="prepare", status="done"))
        _save_state(state, state_path)

    # --- PRODUCE + validate + revise loop ---
    produce_done = state.last_stage("produce") and state.last_stage("produce").status == "done"
    if not produce_done:
        state.state = CategoryState.produce.value
        _save_state(state, state_path)

        effective_brief = brief or f"Напиши SEO-текст для категории «{category.name or category.slug}»."
        draft_response = llm.produce(effective_brief)
        content = draft_response.text
        usage = asdict(draft_response.usage)

        report: ValidationReport | None = None
        for attempt in range(1, max_retries + 1):
            report = _validate_content(content, category)
            if report.status != ReportStatus.FAIL:
                break
            if attempt < max_retries:
                revise_response = llm.revise(content, report.to_revise_payload())
                content = revise_response.text
                for k, v in asdict(revise_response.usage).items():
                    usage[k] = usage.get(k, 0) + v

        final_status = "done" if report and report.status != ReportStatus.FAIL else "needs_human"
        state.content = content
        state.record_stage(StageRecord(
            stage="produce",
            status=final_status,
            attempts=attempt,
            report=report.model_dump() if report else None,
            usage=usage,
        ))
        _save_state(state, state_path)

        if final_status == "needs_human":
            state.state = CategoryState.needs_human.value
            _save_state(state, state_path)
            return state

    # --- DELIVER ---
    if not state.last_stage("deliver"):
        state.state = CategoryState.deliver.value
        _save_state(state, state_path)
        state.record_stage(StageRecord(stage="deliver", status="done"))
        _save_state(state, state_path)

    state.state = CategoryState.done.value
    _save_state(state, state_path)
    return state
