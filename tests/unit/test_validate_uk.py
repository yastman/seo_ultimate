"""Tests for validate_uk.py"""

import json

from scripts.validate_uk import validate_uk_category


class TestValidateUkCategory:
    """Test UK category validation."""

    def test_fails_if_folder_missing(self, tmp_path, monkeypatch):
        """Should fail if UK folder doesn't exist."""
        monkeypatch.chdir(tmp_path)
        result = validate_uk_category("nonexistent")
        assert result == 2  # FAIL

    def test_fails_if_required_files_missing(self, tmp_path, monkeypatch):
        """Should fail if required files are missing."""
        monkeypatch.chdir(tmp_path)
        uk_path = tmp_path / "uk" / "categories" / "test-slug"
        uk_path.mkdir(parents=True)
        # Only create folder, no files
        result = validate_uk_category("test-slug")
        assert result == 2  # FAIL

    def test_warns_on_russian_words_in_meta(self, tmp_path, monkeypatch):
        """Should warn if Russian words found in UK meta."""
        monkeypatch.chdir(tmp_path)
        uk_path = tmp_path / "uk" / "categories" / "test-slug"
        (uk_path / "data").mkdir(parents=True)
        (uk_path / "meta").mkdir(parents=True)
        (uk_path / "content").mkdir(parents=True)

        # Create required files
        (uk_path / "data" / "test-slug_clean.json").write_text("{}", encoding="utf-8")

        meta = {
            "h1": "Тестовий заголовок",
            "meta": {
                "title": "Купить тест",  # Russian word!
                "description": "Опис категорії",
            },
        }
        (uk_path / "meta" / "test-slug_meta.json").write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8"
        )
        (uk_path / "content" / "test-slug_uk.md").write_text(
            "# Заголовок\n\n" + "Текст українською мовою. " * 50, encoding="utf-8"
        )

        result = validate_uk_category("test-slug")
        assert result == 1  # WARNING

    def test_passes_valid_category(self, tmp_path, monkeypatch):
        """Should pass if all checks are OK."""
        monkeypatch.chdir(tmp_path)
        uk_path = tmp_path / "uk" / "categories" / "test-slug"
        (uk_path / "data").mkdir(parents=True)
        (uk_path / "meta").mkdir(parents=True)
        (uk_path / "content").mkdir(parents=True)

        (uk_path / "data" / "test-slug_clean.json").write_text("{}", encoding="utf-8")

        meta = {
            "h1": "Тестовий заголовок",
            "meta": {
                "title": "Купити тест в Україні",
                "description": "Опис категорії українською",
            },
        }
        (uk_path / "meta" / "test-slug_meta.json").write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8"
        )
        (uk_path / "content" / "test-slug_uk.md").write_text(
            "# Заголовок\n\n" + "Текст українською мовою для тестування. " * 50,
            encoding="utf-8",
        )

        result = validate_uk_category("test-slug")
        assert result == 0  # PASS
