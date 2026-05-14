"""Tests for audit_h1_primary.py"""

import json


class TestAuditH1Primary:
    """Tests for H1 vs primary keyword audit."""

    def test_audit_single_category_ok(self, tmp_path):
        """Category with matching H1 returns OK status."""
        from llm_keywords_pipeline.audit.h1 import audit_category

        # Create category structure (for UK: uk/categories/)
        cat_dir = tmp_path / "uk" / "categories" / "test-slug"
        (cat_dir / "data").mkdir(parents=True)
        (cat_dir / "meta").mkdir(parents=True)

        # Write _clean.json
        (cat_dir / "data" / "test-slug_clean.json").write_text(
            json.dumps({"id": "test-slug", "keywords": [{"keyword": "активна піна", "volume": 1000}]})
        )

        # Write _meta.json with matching H1 (plural form)
        (cat_dir / "meta" / "test-slug_meta.json").write_text(json.dumps({"slug": "test-slug", "h1": "Активні піни"}))

        result = audit_category("test-slug", base_path=tmp_path, lang="uk")

        assert result["status"] == "OK"
        assert result["slug"] == "test-slug"

    def test_audit_single_category_mismatch(self, tmp_path):
        """Category with non-matching H1 returns MISMATCH status."""
        from llm_keywords_pipeline.audit.h1 import audit_category

        # Create category structure (for UK: uk/categories/)
        cat_dir = tmp_path / "uk" / "categories" / "test-slug"
        (cat_dir / "data").mkdir(parents=True)
        (cat_dir / "meta").mkdir(parents=True)

        (cat_dir / "data" / "test-slug_clean.json").write_text(
            json.dumps({"id": "test-slug", "keywords": [{"keyword": "рідке скло", "volume": 5400}]})
        )

        (cat_dir / "meta" / "test-slug_meta.json").write_text(
            json.dumps({"slug": "test-slug", "h1": "Кераміка для авто"})  # does not contain "рідке скло"
        )

        result = audit_category("test-slug", base_path=tmp_path, lang="uk")

        assert result["status"] == "MISMATCH"
        assert result["fix_needed"] is True

    def test_audit_category_missing_data(self, tmp_path):
        """Category with missing files returns MISSING_DATA status."""
        from llm_keywords_pipeline.audit.h1 import audit_category

        # Create empty category dir (for UK: uk/categories/)
        cat_dir = tmp_path / "uk" / "categories" / "test-slug"
        cat_dir.mkdir(parents=True)

        result = audit_category("test-slug", base_path=tmp_path, lang="uk")

        assert result["status"] == "MISSING_DATA"

    def test_audit_all_returns_list(self, tmp_path):
        """audit_all returns list of results for all categories."""
        from llm_keywords_pipeline.audit.h1 import audit_all

        # Create two categories
        for slug in ["cat1", "cat2"]:
            cat_dir = tmp_path / "categories" / slug
            (cat_dir / "data").mkdir(parents=True)
            (cat_dir / "meta").mkdir(parents=True)

            (cat_dir / "data" / f"{slug}_clean.json").write_text(
                json.dumps({"id": slug, "keywords": [{"keyword": "тест", "volume": 100}]})
            )
            (cat_dir / "meta" / f"{slug}_meta.json").write_text(json.dumps({"slug": slug, "h1": "Тести"}))

        results = audit_all(lang="ru", base_path=tmp_path)

        assert len(results) == 2
        assert all(r["status"] == "OK" for r in results)
