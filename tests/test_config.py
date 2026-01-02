#!/usr/bin/env python3
"""
TDD tests for scripts/config.py — unified configuration (SSOT).

Focus:
- Adaptive coverage targets
- Semantic depth
- Path helpers
"""

from __future__ import annotations

from pathlib import Path

from scripts import config


class TestAdaptiveTargets:
    def test_get_adaptive_coverage_target_shallow(self):
        assert config.get_adaptive_coverage_target(0) == config.QUALITY_THRESHOLDS["coverage_shallow"]
        assert config.get_adaptive_coverage_target(5) == config.QUALITY_THRESHOLDS["coverage_shallow"]

    def test_get_adaptive_coverage_target_medium(self):
        assert config.get_adaptive_coverage_target(6) == config.QUALITY_THRESHOLDS["coverage_medium"]
        assert config.get_adaptive_coverage_target(15) == config.QUALITY_THRESHOLDS["coverage_medium"]

    def test_get_adaptive_coverage_target_deep(self):
        assert config.get_adaptive_coverage_target(16) == config.QUALITY_THRESHOLDS["coverage_deep"]
        assert config.get_adaptive_coverage_target(999) == config.QUALITY_THRESHOLDS["coverage_deep"]

    def test_get_semantic_depth(self):
        assert config.get_semantic_depth(0) == "shallow"
        assert config.get_semantic_depth(5) == "shallow"
        assert config.get_semantic_depth(6) == "medium"
        assert config.get_semantic_depth(15) == "medium"
        assert config.get_semantic_depth(16) == "deep"


class TestPathHelpers:
    def test_category_paths(self):
        slug = "aktivnaya-pena"
        category_path = config.get_category_path(slug)
        assert category_path == config.CATEGORIES_DIR / slug

        content_path = config.get_content_path(slug)
        assert content_path == config.CATEGORIES_DIR / slug / "content" / f"{slug}_ru.md"

        data_clean = config.get_data_path(slug, clean=True)
        assert data_clean == config.CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"

        data_raw = config.get_data_path(slug, clean=False)
        assert data_raw == config.CATEGORIES_DIR / slug / "data" / f"{slug}.json"

    def test_project_paths_are_paths(self):
        assert isinstance(config.PROJECT_ROOT, Path)
        assert isinstance(config.CATEGORIES_DIR, Path)
        assert isinstance(config.DATA_DIR, Path)

