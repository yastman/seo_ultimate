"""TDD test: issue #15 — prompts must reflect actual code thresholds.

Confirmed discrepancies:
1. seo.py docstring says "100 символов" but limit=150.
2. deliver.md uses density values that don't match SPAM/WARNING_THRESHOLD in density.py.
Fix: update seo.py docstring to 150; add a note in deliver.md that thresholds come from code.
"""
from pathlib import Path

ROOT = Path(__file__).parents[2]
SEO_PY = ROOT / "src" / "llm_keywords_pipeline" / "validate" / "seo.py"
DELIVER_MD = ROOT / "prompts" / "deliver.md"
DENSITY_PY = ROOT / "src" / "llm_keywords_pipeline" / "validate" / "density.py"


class TestCodeThresholdsConsistency:
    """Code constants must be self-consistent across modules."""

    def test_seo_intro_limit_in_docstring(self):
        """seo.py docstring must not claim 100 chars when code uses 150."""
        content = SEO_PY.read_text()
        # The docstring incorrectly says "в первых 100 символах"
        assert "в первых 100 символах" not in content, (
            "seo.py docstring claims 100-char intro limit but code uses 150"
        )

    def test_density_thresholds_documented(self):
        """density.py must have SPAM_THRESHOLD and WARNING_THRESHOLD as named constants."""
        content = DENSITY_PY.read_text()
        assert "SPAM_THRESHOLD" in content
        assert "WARNING_THRESHOLD" in content

    def test_deliver_md_acknowledges_code_thresholds(self):
        """deliver.md must note that actual thresholds come from code, not the table."""
        content = DELIVER_MD.read_text()
        # After fix: deliver.md should note SPAM/WARNING come from density.py
        assert "density.py" in content or "SPAM_THRESHOLD" in content or "код" in content.lower(), (
            "deliver.md must reference that density thresholds come from code constants"
        )
