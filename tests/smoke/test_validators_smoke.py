# tests/smoke/test_validators_smoke.py
"""Smoke tests for validators on real category data."""

from pathlib import Path

import pytest

# Real data paths
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


SAMPLE_CATEGORIES = [
    "aktivnaya-pena",
    "polirovalnye-pasty",
    "ochistiteli-stekol",
]


class TestValidateMetaSmoke:
    """Smoke tests for validate_meta on real data."""

    @pytest.mark.parametrize("slug", SAMPLE_CATEGORIES)
    def test_validate_meta_ru_real_file(self, slug):
        """validate_meta_file works on real RU meta."""
        meta_path = find_ru_meta(slug)
        if meta_path is None:
            pytest.skip(f"Meta file not found for: {slug}")

        from scripts.validate_meta import validate_meta_file

        result = validate_meta_file(str(meta_path), lang="ru")

        # Should return dict with results
        assert isinstance(result, dict)
        # Should have expected keys
        assert "title" in result
        assert "description" in result
        assert "overall" in result

    def test_validate_meta_uk_real_file(self):
        """validate_meta_file works on real UK meta."""
        meta_path = find_uk_meta("aktivnaya-pena")
        if meta_path is None:
            pytest.skip("UK meta file not found for aktivnaya-pena")

        from scripts.validate_meta import validate_meta_file

        result = validate_meta_file(str(meta_path), lang="uk")

        assert isinstance(result, dict)
        assert "title" in result
        assert "overall" in result


class TestValidateContentSmoke:
    """Smoke tests for validate_content on real data."""

    def test_validate_content_ru_real_file(self):
        """validate_content works on real RU content."""
        content_path = find_ru_content("aktivnaya-pena")
        if content_path is None:
            pytest.skip("Content file not found for aktivnaya-pena")

        from scripts.validate_content import validate_content

        result = validate_content(
            str(content_path),
            primary_keyword="активная пена",
            mode="seo",
            lang="ru",
        )

        assert isinstance(result, dict)
        # Should have summary key
        assert "summary" in result
        # Summary should have overall status
        assert "overall" in result["summary"]
        assert result["summary"]["overall"] in ("PASS", "WARN", "FAIL")

    def test_validate_content_uk_real_file(self):
        """validate_content works on real UK content."""
        content_path = find_uk_content("aktivnaya-pena")
        if content_path is None:
            pytest.skip("UK content file not found for aktivnaya-pena")

        from scripts.validate_content import validate_content

        result = validate_content(
            str(content_path),
            primary_keyword="активна піна",
            mode="seo",
            lang="uk",
        )

        assert isinstance(result, dict)
        assert "summary" in result
        assert "overall" in result["summary"]

    def test_validate_content_structure_checks(self):
        """validate_content returns structure checks."""
        content_path = find_ru_content("aktivnaya-pena")
        if content_path is None:
            pytest.skip("Content file not found")

        from scripts.validate_content import validate_content

        result = validate_content(
            str(content_path),
            primary_keyword="активная пена",
            mode="seo",
            lang="ru",
        )

        # Should have checks dict
        assert "checks" in result
        # Should have structure check
        assert "structure" in result["checks"]
        # Structure should have H1 info
        structure = result["checks"]["structure"]
        assert "h1" in structure


class TestValidateDensitySmoke:
    """Smoke tests for validate_density (formerly check_keyword_density) on real data."""

    def test_analyze_text_ru_real_file(self):
        """analyze_text works on real RU content."""
        content_path = find_ru_content("aktivnaya-pena")
        if content_path is None:
            pytest.skip("Content file not found")

        from scripts.validate_density import analyze_text

        text = content_path.read_text(encoding="utf-8")
        result = analyze_text(text, top_n=20, lang="ru")

        # Should have expected keys
        assert "total_words" in result
        assert result["total_words"] > 100
        assert "word_frequencies" in result
        assert "stem_frequencies" in result
        # Should not be spammy (no errors means content is OK)
        assert isinstance(result["spam_detected"], bool)

    def test_analyze_text_uk_real_file(self):
        """analyze_text works on real UK content."""
        content_path = find_uk_content("aktivnaya-pena")
        if content_path is None:
            pytest.skip("UK content file not found")

        from scripts.validate_density import analyze_text

        text = content_path.read_text(encoding="utf-8")
        result = analyze_text(text, top_n=20, lang="uk")

        assert "total_words" in result
        assert result["total_words"] > 100
        # Check UK stopwords were applied
        assert "word_frequencies" in result

    def test_check_keyword_density_specific_keyword(self):
        """check_keyword_density works for specific keyword."""
        content_path = find_ru_content("aktivnaya-pena")
        if content_path is None:
            pytest.skip("Content file not found")

        from scripts.validate_density import check_keyword_density

        text = content_path.read_text(encoding="utf-8")
        result = check_keyword_density(text, "пена", lang="ru")

        assert "keyword" in result
        assert "exact_count" in result
        assert "exact_density" in result
        assert "status" in result
        # Density should be reasonable
        assert 0 <= result["exact_density"] <= 10


class TestMultipleCategoriesSmoke:
    """Test validators across multiple real categories."""

    @pytest.mark.parametrize("slug", ["polirovalnye-pasty", "ochistiteli-stekol"])
    def test_validate_content_multiple_categories(self, slug):
        """validate_content works on multiple categories."""
        content_path = find_ru_content(slug)
        if content_path is None:
            pytest.skip(f"Content file not found for: {slug}")

        # Get primary keyword from slug
        keyword_map = {
            "polirovalnye-pasty": "полировальные пасты",
            "ochistiteli-stekol": "очистители стекол",
        }
        primary_keyword = keyword_map.get(slug, slug.replace("-", " "))

        from scripts.validate_content import validate_content

        result = validate_content(
            str(content_path),
            primary_keyword=primary_keyword,
            mode="seo",
            lang="ru",
        )

        assert isinstance(result, dict)
        assert "summary" in result
        # All real content should pass basic validation
        assert result["summary"]["overall"] in ("PASS", "WARN", "FAIL")
