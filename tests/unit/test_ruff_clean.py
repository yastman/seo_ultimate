"""TDD test: ruff linting must report zero violations (issue #8)."""
import subprocess


def test_ruff_no_violations():
    """ruff check src/ tests/ must exit 0 — no style warnings."""
    result = subprocess.run(
        ["uv", "run", "ruff", "check", "src/", "tests/"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Ruff reported violations:\n{result.stdout}\n{result.stderr}"
    )
