# tests/integration/test_validation_pipeline.py
"""Integration tests for full validation pipeline."""

import json
import pytest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent.parent


def find_ru_content(slug: str) -> Path | None:
    """Find RU content file recursively in categories."""
    for p in PROJECT_ROOT.glob(f"categories/**/{slug}/content/{slug}_ru.md"):
        return p
    return None


def find_ru_meta(slug: str) -> Path | None:
    """Find RU meta file recursively in categories."""
    for p in PROJECT_ROOT.glob(f"categories/**/{slug}/meta/{slug}_meta.json"):
        return p
    return None


def find_ru_clean(slug: str) -> Path | None:
    """Find RU clean JSON recursively in categories."""
    for p in PROJECT_ROOT.glob(f"categories/**/{slug}/data/{slug}_clean.json"):
        return p
    return None


def find_uk_content(slug: str) -> Path | None:
    """Find UK content file in uk/categories."""
    path = PROJECT_ROOT / "uk" / "categories" / slug / "content" / f"{slug}_uk.md"
    return path if path.exists() else None


def find_uk_meta(slug: str) -> Path | None:
    """Find UK meta file in uk/categories."""
    path = PROJECT_ROOT / "uk" / "categories" / slug / "meta" / f"{slug}_meta.json"
    return path if path.exists() else None


def find_uk_clean(slug: str) -> Path | None:
    """Find UK clean JSON in uk/categories."""
    path = PROJECT_ROOT / "uk" / "categories" / slug / "data" / f"{slug}_clean.json"
    return path if path.exists() else None


class TestFullValidationPipeline:
    """Test complete validation workflow on real categories."""

    @pytest.fixture
    def category_slug(self):
        return "aktivnaya-pena"

    def test_full_ru_validation_pipeline(self, category_slug):
        """Full RU validation pipeline works end-to-end."""
        # Paths
        meta_path = find_ru_meta(category_slug)
        content_path = find_ru_content(category_slug)
        clean_path = find_ru_clean(category_slug)

        if not all([meta_path, content_path, clean_path]):
            pytest.skip("Category data not complete")

        # 1. Load clean.json for primary keyword
        clean_data = json.loads(clean_path.read_text(encoding="utf-8"))
        keywords = clean_data.get("keywords", [])
        if keywords and isinstance(keywords[0], dict):
            primary_keyword = keywords[0].get("keyword", "активная пена")
        else:
            primary_keyword = "активная пена"

        # 2. Validate meta
        from scripts.validate_meta import validate_meta_file
        meta_result = validate_meta_file(str(meta_path), lang="ru")
        assert meta_result is not None
        assert "overall" in meta_result

        # 3. Validate content
        from scripts.validate_content import validate_content
        content_result = validate_content(
            str(content_path),
            primary_keyword=primary_keyword,
            mode="seo",
            lang="ru",
        )
        assert "summary" in content_result
        assert "overall" in content_result["summary"]

        # 4. Check density
        from scripts.validate_density import analyze_text
        text = content_path.read_text(encoding="utf-8")
        density_result = analyze_text(text, lang="ru")
        assert density_result["total_words"] > 0

        # Integration assertion: pipeline completes without errors
        print(f"\nPipeline results for {category_slug}:")
        print(f"  Meta: {meta_result.get('overall', 'N/A')}")
        print(f"  Content: {content_result['summary']['overall']}")
        print(f"  Density: {density_result['total_words']} words")

    def test_full_uk_validation_pipeline(self, category_slug):
        """Full UK validation pipeline works end-to-end."""
        # Paths
        meta_path = find_uk_meta(category_slug)
        content_path = find_uk_content(category_slug)
        clean_path = find_uk_clean(category_slug)

        if not all([meta_path, content_path, clean_path]):
            pytest.skip("UK category data not complete")

        # 1. Load clean.json for primary keyword
        clean_data = json.loads(clean_path.read_text(encoding="utf-8"))
        keywords = clean_data.get("keywords", [])
        if keywords and isinstance(keywords[0], dict):
            primary_keyword = keywords[0].get("keyword", "активна піна")
        else:
            primary_keyword = "активна піна"

        # 2. Validate meta
        from scripts.validate_meta import validate_meta_file
        meta_result = validate_meta_file(str(meta_path), lang="uk")
        assert meta_result is not None
        assert "overall" in meta_result

        # 3. Validate content
        from scripts.validate_content import validate_content
        content_result = validate_content(
            str(content_path),
            primary_keyword=primary_keyword,
            mode="seo",
            lang="uk",
        )
        assert "summary" in content_result

        # Integration assertion
        print(f"\nUK Pipeline results for {category_slug}:")
        print(f"  Meta: {meta_result.get('overall', 'N/A')}")
        print(f"  Content: {content_result['summary']['overall']}")


class TestCrossValidation:
    """Test validation consistency across components."""

    def test_meta_content_h1_consistency(self):
        """H1 in meta and content share core keyword."""
        slug = "aktivnaya-pena"

        meta_path = find_ru_meta(slug)
        content_path = find_ru_content(slug)

        if not meta_path or not content_path:
            pytest.skip("Data not available")

        # Load meta H1
        meta_data = json.loads(meta_path.read_text(encoding="utf-8"))
        meta_h1 = meta_data.get("h1", "")

        # Extract content H1
        from scripts.text_utils import extract_h1
        content_text = content_path.read_text(encoding="utf-8")
        content_h1 = extract_h1(content_text)

        # Both should exist
        assert meta_h1, "Meta H1 should exist"
        assert content_h1, "Content H1 should exist"

        # They should share at least one meaningful word (e.g., "пена")
        meta_words = set(meta_h1.lower().split())
        content_words = set(content_h1.lower().split())

        # Filter out short words (stopwords)
        meta_words = {w for w in meta_words if len(w) > 2}
        content_words = {w for w in content_words if len(w) > 2}

        # Should have at least one common word
        common = meta_words & content_words
        assert len(common) > 0, f"No common words between meta H1 '{meta_h1}' and content H1 '{content_h1}'"

    def test_keywords_in_content(self):
        """Keywords from clean.json appear in content."""
        slug = "aktivnaya-pena"

        clean_path = find_ru_clean(slug)
        content_path = find_ru_content(slug)

        if not clean_path or not content_path:
            pytest.skip("Data not available")

        # Load keywords
        clean_data = json.loads(clean_path.read_text(encoding="utf-8"))
        keywords = clean_data.get("keywords", [])

        if not keywords:
            pytest.skip("No keywords in clean.json")

        # Get first 3 keywords
        kw_list = []
        for kw in keywords[:3]:
            if isinstance(kw, dict):
                kw_list.append(kw.get("keyword", "").lower())
            else:
                kw_list.append(str(kw).lower())

        # Check they appear in content
        content_text = content_path.read_text(encoding="utf-8").lower()

        found_count = sum(1 for kw in kw_list if kw in content_text)

        # At least primary keyword should be present
        assert found_count >= 1, f"Expected at least 1 keyword from {kw_list} in content"


class TestValidationModes:
    """Test different validation modes."""

    def test_seo_mode_returns_expected_structure(self):
        """SEO mode returns expected validation structure."""
        content_path = find_ru_content("aktivnaya-pena")
        if content_path is None:
            pytest.skip("Content not available")

        from scripts.validate_content import validate_content

        result = validate_content(
            str(content_path),
            primary_keyword="активная пена",
            mode="seo",
            lang="ru",
        )

        # Should have expected keys
        assert "checks" in result
        assert "summary" in result

        # Checks should have structure and primary_keyword
        assert "structure" in result["checks"]
        assert "primary_keyword" in result["checks"]

    def test_quality_mode_returns_expected_structure(self):
        """Quality mode returns expected validation structure."""
        content_path = find_ru_content("aktivnaya-pena")
        if content_path is None:
            pytest.skip("Content not available")

        from scripts.validate_content import validate_content

        result = validate_content(
            str(content_path),
            primary_keyword="активная пена",
            mode="quality",
            lang="ru",
        )

        # Should have expected keys
        assert "checks" in result
        assert "summary" in result


class TestLanguageSupport:
    """Test RU/UK language switching."""

    def test_meta_validation_respects_lang_parameter(self):
        """validate_meta uses correct patterns for language."""
        uk_meta_path = find_uk_meta("aktivnaya-pena")

        if uk_meta_path is None:
            pytest.skip("UK meta not available")

        from scripts.validate_meta import validate_meta_file

        result = validate_meta_file(str(uk_meta_path), lang="uk")

        # Language should be detected/set
        assert result.get("lang") == "uk"

    def test_content_validation_respects_lang_parameter(self):
        """validate_content uses correct stopwords for language."""
        uk_content_path = find_uk_content("aktivnaya-pena")

        if uk_content_path is None:
            pytest.skip("UK content not available")

        from scripts.validate_content import validate_content

        result = validate_content(
            str(uk_content_path),
            primary_keyword="активна піна",
            mode="seo",
            lang="uk",
        )

        # Should complete without error
        assert "summary" in result
        assert result["summary"]["overall"] in ("PASS", "WARN", "FAIL")
