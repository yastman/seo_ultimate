# tests/unit/test_validate_master.py
"""Tests for validate_master.py"""

import pytest

from scripts.validate_master import (
    load_master_csv,
    validate_categories_exist,
    validate_columns,
    validate_has_keywords,
    validate_no_duplicates,
    validate_types,
    validate_volumes,
)


class TestLoadMasterCsv:
    """Test CSV loading."""

    def test_loads_valid_csv(self, tmp_path):
        """Should load CSV and return list of dicts."""
        csv_file = tmp_path / "master.csv"
        csv_file.write_text("keyword,volume,category,type,use_in\nтест,100,aktivnaya-pena,keyword,\n", encoding="utf-8")
        rows = load_master_csv(csv_file)
        assert len(rows) == 1
        assert rows[0]["keyword"] == "тест"
        assert rows[0]["volume"] == "100"

    def test_raises_on_missing_file(self, tmp_path):
        """Should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_master_csv(tmp_path / "nonexistent.csv")


class TestValidateColumns:
    """Test column validation."""

    def test_valid_columns(self):
        """Should pass with all required columns."""
        rows = [{"keyword": "a", "volume": "1", "category": "b", "type": "keyword", "use_in": ""}]
        errors = validate_columns(rows)
        assert errors == []

    def test_missing_column(self):
        """Should report missing column."""
        rows = [{"keyword": "a", "volume": "1", "category": "b"}]  # missing type, use_in
        errors = validate_columns(rows)
        assert len(errors) > 0
        assert "type" in errors[0].lower() or "use_in" in errors[0].lower()


class TestValidateCategoriesExist:
    """Test category existence validation."""

    def test_existing_category(self, tmp_path):
        """Should pass for existing category."""
        (tmp_path / "categories" / "aktivnaya-pena" / "data").mkdir(parents=True)
        rows = [{"category": "aktivnaya-pena"}]
        errors = validate_categories_exist(rows, tmp_path / "categories")
        assert errors == []

    def test_missing_category(self, tmp_path):
        """Should report missing category."""
        (tmp_path / "categories").mkdir()
        rows = [{"category": "nonexistent"}]
        errors = validate_categories_exist(rows, tmp_path / "categories")
        assert len(errors) == 1
        assert "nonexistent" in errors[0]

    def test_uncategorized_allowed(self, tmp_path):
        """Should allow 'uncategorized' without folder."""
        (tmp_path / "categories").mkdir()
        rows = [{"category": "uncategorized"}]
        errors = validate_categories_exist(rows, tmp_path / "categories")
        assert errors == []


class TestValidateNoDuplicates:
    """Test duplicate detection."""

    def test_no_duplicates(self):
        """Should pass with unique keywords."""
        rows = [{"keyword": "a"}, {"keyword": "b"}]
        errors = validate_no_duplicates(rows)
        assert errors == []

    def test_finds_duplicates(self):
        """Should report duplicate keywords."""
        rows = [{"keyword": "a"}, {"keyword": "a"}]
        errors = validate_no_duplicates(rows)
        assert len(errors) == 1
        assert "a" in errors[0]


class TestValidateTypes:
    """Test type field validation."""

    def test_valid_types(self):
        """Should pass for keyword and synonym."""
        rows = [{"keyword": "a", "type": "keyword"}, {"keyword": "b", "type": "synonym"}]
        errors = validate_types(rows)
        assert errors == []

    def test_invalid_type(self):
        """Should report invalid type."""
        rows = [{"keyword": "a", "type": "invalid"}]
        errors = validate_types(rows)
        assert len(errors) == 1


class TestValidateVolumes:
    """Test volume validation."""

    def test_valid_volumes(self):
        """Should pass for non-negative integers."""
        rows = [{"keyword": "a", "volume": "100"}, {"keyword": "b", "volume": "0"}]
        errors = validate_volumes(rows)
        assert errors == []

    def test_negative_volume(self):
        """Should report negative volume."""
        rows = [{"keyword": "a", "volume": "-1"}]
        errors = validate_volumes(rows)
        assert len(errors) == 1

    def test_non_integer_volume(self):
        """Should report non-integer volume."""
        rows = [{"keyword": "a", "volume": "abc"}]
        errors = validate_volumes(rows)
        assert len(errors) == 1


class TestValidateHasKeywords:
    """Test that each category has at least one keyword type."""

    def test_has_keyword(self):
        """Should pass when category has keyword type."""
        rows = [
            {"category": "cat1", "type": "keyword"},
            {"category": "cat1", "type": "synonym"},
        ]
        errors = validate_has_keywords(rows)
        assert errors == []

    def test_only_synonyms(self):
        """Should report category with only synonyms."""
        rows = [{"category": "cat1", "type": "synonym"}]
        errors = validate_has_keywords(rows)
        assert len(errors) == 1
        assert "cat1" in errors[0]
