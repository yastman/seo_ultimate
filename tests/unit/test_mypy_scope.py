"""TDD test: issue #13 — mypy scope and CI step name must be honest.

The fix:
- Rename CI step from 'Type check maintained typed surface' to
  'Type check core/text.py' to match the actual scope.
- Set cov-fail-under to a value that won't flip on minor changes (20, not 24).
"""
from pathlib import Path

ROOT = Path(__file__).parents[2]
PYPROJECT = ROOT / "pyproject.toml"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


class TestMypyConfig:
    """pyproject.toml mypy config must honestly scope to core/text.py."""

    def test_mypy_files_lists_core_text(self):
        """mypy files must include core/text.py."""
        content = PYPROJECT.read_text()
        assert "core/text.py" in content

    def test_mypy_does_not_claim_full_package(self):
        """mypy files must NOT list the full src package as the only source."""
        content = PYPROJECT.read_text()
        # The misleading pattern would be files = ["src/llm_keywords_pipeline"]
        # without any module names — current config is core/text.py, that's fine.
        assert 'files = ["src/llm_keywords_pipeline"]' not in content


class TestCIHonesty:
    """CI workflow step name must reflect the actual mypy scope."""

    def test_ci_step_not_misleading(self):
        """CI step must NOT claim 'Type check maintained typed surface'."""
        content = CI_WORKFLOW.read_text()
        assert "Type check maintained typed surface" not in content, (
            "CI step name is misleading — rename to reflect actual scope (core/text.py)"
        )

    def test_ci_step_mentions_scope(self):
        """CI mypy step name must mention the actual file or surface."""
        content = CI_WORKFLOW.read_text()
        # Accept any honest name that mentions what is being checked
        assert any(
            phrase in content
            for phrase in ["core/text", "text.py", "core.text", "typed surface: core"]
        ), "CI mypy step name must mention the actual checked scope"

    def test_coverage_gate_not_equal_to_actual(self):
        """cov-fail-under must not be equal to current coverage (fragile gate).
        
        Current coverage is ~24%. A gate of 24 is fragile — set to 20 to give
        headroom while still catching large regressions.
        """
        content = CI_WORKFLOW.read_text()
        # 24 is the fragile value — we need something below current coverage
        assert "--cov-fail-under=24" not in content, (
            "Coverage gate --cov-fail-under=24 equals actual coverage; "
            "lower to 20 for a stable floor"
        )
