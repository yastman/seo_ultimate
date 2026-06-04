"""Batch runner with checkpoints and summary metrics (issue #21).

run_batch() processes a list of Category objects, one per slug.
One slug failure does NOT abort the batch.
Returns a BatchReport with per-category results and aggregate metrics.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from llm_keywords_pipeline.automation.llm_client import LlmClient
from llm_keywords_pipeline.automation.orchestrator import CategoryRunState, run_category
from llm_keywords_pipeline.core.models import Category


@dataclass
class CategoryResult:
    slug: str
    state: str
    attempts: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    error: str = ""


@dataclass
class BatchReport:
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    finished_at: str = ""
    total: int = 0
    passed: int = 0
    warned: int = 0
    failed: int = 0
    needs_human: int = 0
    total_cost_usd: float = 0.0
    results: list[CategoryResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def summary(self) -> str:
        lines = [
            f"Batch: {self.total} categories",
            f"  PASS:        {self.passed}",
            f"  WARN:        {self.warned}",
            f"  NEEDS_HUMAN: {self.needs_human}",
            f"  FAILED:      {self.failed}",
            f"  Cost:        ${self.total_cost_usd:.4f}",
        ]
        return "\n".join(lines)


def run_batch(
    categories: list[Category],
    llm: LlmClient,
    state_dir: Path | None = None,
    limit: int | None = None,
    max_retries: int = 3,
) -> BatchReport:
    """
    Process a batch of categories.

    Checkpointed: state_dir/<slug>_state.json persists progress.
    One failure does not abort the rest.
    """
    import time

    state_dir = state_dir or Path(".")
    state_dir.mkdir(parents=True, exist_ok=True)

    batch = categories[:limit] if limit else categories
    report = BatchReport(total=len(batch))

    for cat in batch:
        t0 = time.monotonic()
        error = ""
        run_state: CategoryRunState | None = None
        try:
            run_state = run_category(cat, llm, state_dir=state_dir, max_retries=max_retries)
        except Exception as exc:
            error = str(exc)

        duration_ms = int((time.monotonic() - t0) * 1000)
        cost = run_state.total_usage.get("cost_usd", 0.0) if run_state else 0.0
        attempts = 0
        if run_state:
            produce = run_state.last_stage("produce")
            attempts = produce.attempts if produce else 0

        final_state = run_state.state if run_state else "failed"

        result = CategoryResult(
            slug=cat.slug,
            state=final_state,
            attempts=attempts,
            cost_usd=cost,
            duration_ms=duration_ms,
            error=error,
        )
        report.results.append(result)
        report.total_cost_usd += cost

        if error or final_state == "failed":
            report.failed += 1
        elif final_state == "needs_human":
            report.needs_human += 1
        elif final_state == "done":
            report.passed += 1
        else:
            report.warned += 1

    report.finished_at = datetime.now(UTC).isoformat()

    # Write human-queue file
    human_queue = [r.slug for r in report.results if r.state == "needs_human"]
    if human_queue:
        queue_path = state_dir / "needs_human.json"
        queue_path.write_text(json.dumps(human_queue, ensure_ascii=False, indent=2), encoding="utf-8")

    # Write batch report
    report_path = state_dir / "batch_report.json"
    report_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    return report
