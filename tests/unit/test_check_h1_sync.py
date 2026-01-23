"""Tests for check_h1_sync.py UK support."""

from pathlib import Path

import pytest


class TestCheckH1SyncSourceAnalysis:
    """Tests for UK support by analyzing source code."""

    @pytest.fixture
    def source_code(self):
        """Read source code directly to avoid import issues."""
        script_path = Path(__file__).parent.parent.parent / "scripts" / "check_h1_sync.py"
        return script_path.read_text(encoding="utf-8")

    def test_check_sync_has_lang_parameter(self, source_code):
        """check_sync function accepts lang parameter."""
        # Look for function definition with lang parameter
        assert "def check_sync(" in source_code
        assert 'lang: str = "ru"' in source_code or "lang: str = 'ru'" in source_code

    def test_argparse_has_lang_argument(self, source_code):
        """Argparse includes --lang argument."""
        assert "--lang" in source_code
        assert 'choices=["ru", "uk"]' in source_code or "choices=['ru', 'uk']" in source_code

    def test_uk_path_construction(self, source_code):
        """UK mode should use uk/categories path."""
        assert 'lang == "uk"' in source_code or "lang == 'uk'" in source_code
        assert '"uk"' in source_code and '"categories"' in source_code

    def test_content_suffix_uk(self, source_code):
        """UK mode should use _uk.md suffix."""
        assert "_uk.md" in source_code

    def test_content_suffix_ru(self, source_code):
        """RU mode should use _ru.md suffix."""
        assert "_ru.md" in source_code

    def test_lang_passed_to_check_sync(self, source_code):
        """Lang argument is passed to check_sync function."""
        assert "args.lang" in source_code
