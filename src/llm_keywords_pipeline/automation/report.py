"""Unified ValidationReport schema for all validators (issue #17).

All validators/audits produce a stable JSON structure via ValidationReport.
This replaces human-readable stdout with machine-parseable data for the
automation loop (produce → validate → revise).
"""
from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class CheckStatus(StrEnum):
    pass_ = "pass"
    warn = "warn"
    fail = "fail"
    skip = "skip"


class ReportStatus(StrEnum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class CheckResult(BaseModel):
    id: str                          # e.g. "water_percent", "intro_keyword"
    status: CheckStatus
    severity: str = "medium"         # low | medium | high | critical
    message: str = ""
    locator: str = ""                # heading, line, or section reference
    expected: Any = None             # expected value / threshold
    actual: Any = None               # actual measured value


class ValidationReport(BaseModel):
    validator: str                   # "density" | "water" | "content" | "seo"
    slug: str = ""
    lang: str = "ru"
    status: ReportStatus
    checks: list[CheckResult] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

    @property
    def failures(self) -> list[CheckResult]:
        return [c for c in self.checks if c.status == CheckStatus.fail]

    @property
    def warnings(self) -> list[CheckResult]:
        return [c for c in self.checks if c.status == CheckStatus.warn]

    def to_revise_payload(self) -> list[dict]:
        """Minimal payload for LLM revise() — only failed checks."""
        return [
            {
                "id": c.id,
                "message": c.message,
                "locator": c.locator,
                "expected": c.expected,
                "actual": c.actual,
            }
            for c in self.failures
        ]

    @classmethod
    def from_water_metrics(cls, metrics: dict | None, slug: str = "", lang: str = "ru") -> ValidationReport:
        """Build a ValidationReport from audit.water.calculate_metrics() output."""
        if metrics is None:
            return cls(
                validator="water",
                slug=slug,
                lang=lang,
                status=ReportStatus.FAIL,
                checks=[CheckResult(
                    id="text_language",
                    status=CheckStatus.fail,
                    severity="high",
                    message="Text is empty or non-Cyrillic; cannot calculate water metrics.",
                )],
            )
        checks = []
        water = metrics.get("water_percent", 0)
        water_ok = 40 <= water <= 60
        checks.append(CheckResult(
            id="water_percent",
            status=CheckStatus.pass_ if water_ok else CheckStatus.warn,
            severity="medium",
            message=f"Water: {water:.1f}%",
            expected="40–60%",
            actual=round(water, 2),
        ))
        nausea = metrics.get("classic_nausea", 0)
        nausea_ok = nausea <= 3.5
        checks.append(CheckResult(
            id="classic_nausea",
            status=CheckStatus.pass_ if nausea_ok else CheckStatus.warn,
            severity="medium",
            message=f"Classic nausea: {nausea:.2f}",
            expected="≤3.5",
            actual=round(nausea, 2),
        ))
        any_fail = any(c.status == CheckStatus.fail for c in checks)
        any_warn = any(c.status == CheckStatus.warn for c in checks)
        status = ReportStatus.FAIL if any_fail else (ReportStatus.WARN if any_warn else ReportStatus.PASS)
        return cls(validator="water", slug=slug, lang=lang, status=status, checks=checks, metadata=metrics)
