"""Integration tests for llm_keywords_pipeline.validate.master module."""

import csv


class TestValidateMaster:
    """Tests for validate function."""

    def test_valid_master_csv(self, tmp_path):
        """Valid master CSV should pass validation."""
        from llm_keywords_pipeline.validate.master import validate

        csv_path = tmp_path / "master.csv"
        categories_dir = tmp_path / "categories"
        categories_dir.mkdir()

        # Create test category
        (categories_dir / "test-category").mkdir()

        # Create valid CSV with required columns: keyword, volume, category, type, use_in
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "category",
                    "keyword",
                    "type",
                    "volume",
                    "use_in",
                ],
            )
            writer.writeheader()
            writer.writerow(
                {
                    "category": "test-category",
                    "keyword": "тестовый ключ",
                    "type": "keyword",
                    "volume": "100",
                    "use_in": "",
                }
            )

        errors, warnings = validate(csv_path, categories_dir)

        assert len(errors) == 0

    def test_missing_required_column(self, tmp_path):
        """CSV without required column should fail."""
        from llm_keywords_pipeline.validate.master import validate_columns

        rows = [{"keyword": "test"}]  # Missing category_slug, type, etc.

        errors = validate_columns(rows)

        assert len(errors) > 0


class TestValidateNoduplicates:
    """Tests for validate_no_duplicates function."""

    def test_no_duplicates(self):
        """Unique keywords should pass."""
        from llm_keywords_pipeline.validate.master import validate_no_duplicates

        rows = [
            {"keyword": "unique key 1"},
            {"keyword": "unique key 2"},
            {"keyword": "unique key 3"},
        ]

        errors = validate_no_duplicates(rows)

        assert len(errors) == 0

    def test_with_duplicates(self):
        """Duplicate keywords should fail."""
        from llm_keywords_pipeline.validate.master import validate_no_duplicates

        rows = [
            {"keyword": "duplicate key"},
            {"keyword": "duplicate key"},  # Duplicate
        ]

        errors = validate_no_duplicates(rows)

        assert len(errors) > 0
