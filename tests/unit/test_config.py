from pathlib import Path

import pytest

from scripts import config


def test_critical_constants():
    """Verify essential constants are present and have correct types."""
    assert isinstance(config.PROJECT_ROOT, Path)
    assert isinstance(config.CATEGORIES_DIR, Path)
    assert isinstance(config.QUALITY_THRESHOLDS, dict)
    assert isinstance(config.L3_TO_SLUG, dict)
    assert isinstance(config.SLUG_TO_L3, dict)

    # Verify bidirectional mapping integrity
    assert len(config.L3_TO_SLUG) == len(config.SLUG_TO_L3)
    for l3, slug in config.L3_TO_SLUG.items():
        assert config.SLUG_TO_L3[slug] == l3


@pytest.mark.parametrize(
    "keywords_count, expected",
    [
        (1, config.QUALITY_THRESHOLDS["coverage_shallow"]),  # <= 5
        (5, config.QUALITY_THRESHOLDS["coverage_shallow"]),
        (6, config.QUALITY_THRESHOLDS["coverage_medium"]),  # 6-15
        (15, config.QUALITY_THRESHOLDS["coverage_medium"]),
        (16, config.QUALITY_THRESHOLDS["coverage_deep"]),  # > 15
        (100, config.QUALITY_THRESHOLDS["coverage_deep"]),
    ],
)
def test_get_adaptive_coverage_target(keywords_count, expected):
    assert config.get_adaptive_coverage_target(keywords_count) == int(expected)


@pytest.mark.parametrize(
    "keywords_count, expected_depth",
    [
        (1, "shallow"),
        (5, "shallow"),
        (6, "medium"),
        (15, "medium"),
        (20, "deep"),
    ],
)
def test_get_semantic_depth(keywords_count, expected_depth):
    assert config.get_semantic_depth(keywords_count) == expected_depth


def test_path_helpers():
    """Verify path helper functions return expected paths."""
    slug = "test-category"
    base = config.CATEGORIES_DIR

    assert config.get_category_path(slug) == base / slug
    assert config.get_content_path(slug) == base / slug / "content" / f"{slug}_ru.md"
    assert config.get_data_path(slug, clean=True) == base / slug / "data" / f"{slug}_clean.json"
    assert config.get_data_path(slug, clean=False) == base / slug / "data" / f"{slug}.json"


def test_blacklist_patterns():
    """Verify blacklist structure."""
    assert isinstance(config.AI_FLUFF_PATTERNS, list)
    assert len(config.AI_FLUFF_PATTERNS) > 0
    assert isinstance(config.STRICT_BLACKLIST_PHRASES, list)


def test_quality_thresholds_logic():
    """Verify logical consistency of thresholds."""
    # min < max
    assert config.QUALITY_THRESHOLDS["water_target_min"] < config.QUALITY_THRESHOLDS["water_target_max"]
    assert config.QUALITY_THRESHOLDS["words_soft_min"] < config.QUALITY_THRESHOLDS["words_soft_max"]
