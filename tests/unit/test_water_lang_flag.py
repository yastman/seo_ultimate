"""TDD test: issue #10 — audit.water main() must handle --lang flag.

The bug: main() tries int(argv[1]) before stripping --lang,
causing ValueError when --lang appears right after the filename.
Fix: use argparse (as done in validate/density.py).
"""
import pytest
from llm_keywords_pipeline.audit.water import main


class TestWaterMainLangFlag:
    """main() must parse --lang without ValueError."""

    def test_lang_uk_after_filename(self, tmp_path):
        """<file> --lang uk must not raise ValueError."""
        f = tmp_path / "test.md"
        f.write_text("Привіт, це тестовий текст для перевірки водності.")
        result = main([str(f), "--lang", "uk"])
        assert isinstance(result, int)

    def test_lang_ru_after_filename(self, tmp_path):
        """<file> --lang ru must work."""
        f = tmp_path / "test.md"
        f.write_text("Привет, это тестовый текст для проверки водности.")
        result = main([str(f), "--lang", "ru"])
        assert isinstance(result, int)

    def test_lang_default_is_ru(self, tmp_path):
        """Without --lang, default language is ru (no crash)."""
        f = tmp_path / "test.md"
        f.write_text("Привет, это тестовый текст.")
        result = main([str(f)])
        assert isinstance(result, int)

    def test_custom_targets_with_lang(self, tmp_path):
        """<file> 30 70 --lang uk must work (positional args + flag)."""
        f = tmp_path / "test.md"
        f.write_text("Привіт, це тестовий текст.")
        result = main([str(f), "30", "70", "--lang", "uk"])
        assert isinstance(result, int)

    def test_missing_file_returns_1(self, tmp_path):
        """Non-existent file must return exit code 1."""
        result = main([str(tmp_path / "nonexistent.md"), "--lang", "ru"])
        assert result == 1

    def test_no_args_returns_1(self):
        """No arguments must exit with non-zero code (argparse exits with 2)."""
        import pytest
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code != 0
