"""TDD test: issue #6 — targeted filterwarnings instead of --disable-warnings.

The fix replaces the global `--disable-warnings` flag in pytest.ini with
specific `filterwarnings` entries so new warnings from project code surface
in CI, while known third-party warnings (pymorphy2, runpy) stay suppressed.
"""
from pathlib import Path


PYTEST_INI = Path(__file__).parents[2] / "pytest.ini"


class TestPytestWarningConfig:
    """pytest.ini must use targeted filterwarnings, not --disable-warnings."""

    def test_no_global_disable_warnings(self):
        """--disable-warnings must not appear in addopts."""
        content = PYTEST_INI.read_text()
        assert "--disable-warnings" not in content, (
            "pytest.ini still has --disable-warnings; replace with filterwarnings"
        )

    def test_filterwarnings_section_present(self):
        """filterwarnings section must exist."""
        content = PYTEST_INI.read_text()
        assert "filterwarnings" in content

    def test_pymorphy2_deprecation_filtered(self):
        """DeprecationWarning from pymorphy2 must be suppressed."""
        content = PYTEST_INI.read_text()
        assert "pymorphy2" in content

    def test_runpy_runtime_warning_filtered(self):
        """RuntimeWarning from runpy must be suppressed."""
        content = PYTEST_INI.read_text()
        assert "runpy" in content


class TestAuditModulesImportClean:
    """Audit modules must be importable without errors."""

    def test_water_importable(self):
        import llm_keywords_pipeline.audit.water  # noqa: F401

    def test_coverage_importable(self):
        import llm_keywords_pipeline.audit.coverage  # noqa: F401

    def test_h1_sync_importable(self):
        import llm_keywords_pipeline.audit.h1_sync  # noqa: F401

    def test_keyword_consistency_importable(self):
        import llm_keywords_pipeline.audit.keyword_consistency  # noqa: F401
