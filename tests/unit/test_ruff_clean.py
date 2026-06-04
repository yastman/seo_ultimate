"""TDD test: ruff linting must report zero violations (issue #8)."""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _ruff_cmd() -> list[str]:
    """Prefer the installed ruff executable; fall back to `python -m ruff`."""
    ruff = shutil.which("ruff")
    if ruff:
        return [ruff]
    return [sys.executable, "-m", "ruff"]


def test_ruff_no_violations():
    """`ruff check src tests` must exit 0 — no style warnings (regression for #8)."""
    if shutil.which("ruff") is None:
        try:
            import ruff  # noqa: F401
        except ImportError:
            pytest.skip("ruff is not installed")

    result = subprocess.run(
        [*_ruff_cmd(), "check", "src", "tests"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Ruff reported violations:\n{result.stdout}\n{result.stderr}"
    )
