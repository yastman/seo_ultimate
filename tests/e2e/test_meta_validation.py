"""
E2E tests for meta validation on real data.

Run with: pytest -m e2e -v
Skip with: pytest -m "not e2e"
"""

import subprocess

import pytest


@pytest.mark.e2e
class TestMetaValidationE2E:
    """E2E tests that run on actual category data."""

    def test_validate_all_ru_finds_categories(self):
        """validate_meta.py --all --lang ru should find 50+ RU categories."""
        result = subprocess.run(
            ["python3", "scripts/validate_meta.py", "--all", "--lang", "ru"],
            capture_output=True,
            text=True,
        )
        # Check output contains summary
        assert "Total files:" in result.stdout
        # Extract count from "Total files: N"
        for line in result.stdout.split("\n"):
            if "Total files:" in line:
                count = int(line.split(":")[1].strip())
                assert count >= 50, f"Expected 50+ RU files, got {count}"
                break

    def test_validate_all_uk_finds_categories(self):
        """validate_meta.py --all --lang uk should find 50+ UK categories."""
        result = subprocess.run(
            ["python3", "scripts/validate_meta.py", "--all", "--lang", "uk"],
            capture_output=True,
            text=True,
        )
        assert "Total files:" in result.stdout
        for line in result.stdout.split("\n"):
            if "Total files:" in line:
                count = int(line.split(":")[1].strip())
                assert count >= 50, f"Expected 50+ UK files, got {count}"
                break

    def test_audit_h1_ru_runs(self):
        """audit_h1_primary.py --lang ru should run without errors."""
        result = subprocess.run(
            ["python3", "scripts/audit_h1_primary.py", "--lang", "ru"],
            capture_output=True,
            text=True,
        )
        # Should have summary output (in stdout or stderr)
        combined = result.stdout + result.stderr
        assert "Audit Results:" in combined or "OK:" in combined

    def test_audit_h1_uk_runs(self):
        """audit_h1_primary.py --lang uk should run without errors."""
        result = subprocess.run(
            ["python3", "scripts/audit_h1_primary.py", "--lang", "uk"],
            capture_output=True,
            text=True,
        )
        combined = result.stdout + result.stderr
        assert "Audit Results:" in combined or "OK:" in combined
