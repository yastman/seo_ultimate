#!/usr/bin/env python3
"""
test_setup_all.py — TDD tests for setup_all.py

Tests cover:
- auto_detect_tier: tier detection by keywords count
- create_category_folders: folder structure creation
- create_task_file: task JSON structure
- create_keywords_json: keywords JSON generation
- setup_category: full category setup
- Integration with parse_semantics_to_json

Run manually (pytest not installed):
    python3 tests/test_setup_all.py
"""

import json
import sys
import tempfile
from pathlib import Path

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from setup_all import (  # noqa: E402
    CATEGORY_SUBDIRS,
    TIER_THRESHOLDS,
    auto_detect_tier,
    create_category_folders,
    create_task_file,
    get_all_categories_with_keywords,
)

# =============================================================================
# Test: auto_detect_tier
# =============================================================================


class TestAutoDetectTier:
    """Tests for tier auto-detection based on keywords count."""

    def test_tier_a_high_keywords(self):
        """52 keywords → Tier A (>30)."""
        assert auto_detect_tier(52) == "A"

    def test_tier_a_boundary(self):
        """31 keywords → Tier A (>30)."""
        assert auto_detect_tier(31) == "A"

    def test_tier_b_upper_boundary(self):
        """30 keywords → Tier B (≤30)."""
        assert auto_detect_tier(30) == "B"

    def test_tier_b_middle(self):
        """20 keywords → Tier B (10-30)."""
        assert auto_detect_tier(20) == "B"

    def test_tier_b_lower_boundary(self):
        """10 keywords → Tier B (≥10)."""
        assert auto_detect_tier(10) == "B"

    def test_tier_c_below_threshold(self):
        """9 keywords → Tier C (<10)."""
        assert auto_detect_tier(9) == "C"

    def test_tier_c_low(self):
        """3 keywords → Tier C."""
        assert auto_detect_tier(3) == "C"

    def test_tier_c_zero(self):
        """0 keywords → Tier C."""
        assert auto_detect_tier(0) == "C"

    def test_tier_c_one(self):
        """1 keyword → Tier C."""
        assert auto_detect_tier(1) == "C"


# =============================================================================
# Test: create_category_folders
# =============================================================================


class TestCreateCategoryFolders:
    """Tests for folder structure creation."""

    def test_creates_all_subdirs(self):
        """Should create all required subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Temporarily override CATEGORIES_DIR
            import setup_all

            original_dir = setup_all.CATEGORIES_DIR
            setup_all.CATEGORIES_DIR = Path(tmpdir)

            try:
                slug = "test-category"
                create_category_folders(slug)

                # Check all subdirs exist
                for subdir in CATEGORY_SUBDIRS:
                    subdir_path = Path(tmpdir) / slug / subdir
                    assert subdir_path.exists(), f"{subdir} should exist"
                    assert subdir_path.is_dir(), f"{subdir} should be directory"
            finally:
                setup_all.CATEGORIES_DIR = original_dir

    def test_dry_run_no_create(self):
        """Dry run should not create folders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import setup_all

            original_dir = setup_all.CATEGORIES_DIR
            setup_all.CATEGORIES_DIR = Path(tmpdir)

            try:
                slug = "test-dry"
                create_category_folders(slug, dry_run=True)

                # Should not exist
                assert not (Path(tmpdir) / slug).exists()
            finally:
                setup_all.CATEGORIES_DIR = original_dir


# =============================================================================
# Test: create_task_file
# =============================================================================


class TestCreateTaskFile:
    """Tests for task file creation."""

    def test_task_file_structure(self):
        """Task file should have correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import setup_all

            original_root = setup_all.PROJECT_ROOT
            setup_all.PROJECT_ROOT = Path(tmpdir)

            try:
                slug = "test-task"
                tier = "B"
                keywords_count = 25

                create_task_file(slug, tier, keywords_count)

                task_path = Path(tmpdir) / f"task_{slug}.json"
                assert task_path.exists()

                with open(task_path, encoding="utf-8") as f:
                    data = json.load(f)

                # Check required fields
                assert data["slug"] == slug
                assert data["tier"] == tier
                assert data["keywords_count"] == keywords_count
                assert "stages" in data
                # New 3-stage schema (prepare/produce/deliver)
                assert data["stages"]["prepare"] == "completed"
                assert data["stages"]["produce"] == "pending"
                assert data["stages"]["deliver"] == "pending"
                assert "paths" in data
            finally:
                setup_all.PROJECT_ROOT = original_root

    def test_task_file_dry_run(self):
        """Dry run should not create task file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import setup_all

            original_root = setup_all.PROJECT_ROOT
            setup_all.PROJECT_ROOT = Path(tmpdir)

            try:
                create_task_file("test-dry", "B", 10, dry_run=True)
                assert not (Path(tmpdir) / "task_test-dry.json").exists()
            finally:
                setup_all.PROJECT_ROOT = original_root


# =============================================================================
# Test: Tier thresholds consistency
# =============================================================================


class TestTierThresholds:
    """Tests for tier threshold constants."""

    def test_thresholds_order(self):
        """Thresholds should be A > B > C."""
        assert TIER_THRESHOLDS["A"] > TIER_THRESHOLDS["B"]
        assert TIER_THRESHOLDS["B"] > TIER_THRESHOLDS["C"]

    def test_tier_a_threshold(self):
        """Tier A threshold should be 30."""
        assert TIER_THRESHOLDS["A"] == 30

    def test_tier_b_threshold(self):
        """Tier B threshold should be 10."""
        assert TIER_THRESHOLDS["B"] == 10

    def test_tier_c_threshold(self):
        """Tier C threshold should be 0."""
        assert TIER_THRESHOLDS["C"] == 0


# =============================================================================
# Test: Category subdirs
# =============================================================================


class TestCategorySubdirs:
    """Tests for category subdirectory constants."""

    def test_required_subdirs_present(self):
        """Required subdirs should be in list."""
        required = ["data", "content", "meta", "competitors", "deliverables"]
        for subdir in required:
            assert subdir in CATEGORY_SUBDIRS, f"{subdir} should be in CATEGORY_SUBDIRS"

    def test_minimum_subdirs_count(self):
        """Should have at least 5 subdirs."""
        assert len(CATEGORY_SUBDIRS) >= 5


# =============================================================================
# Test: Integration with CSV
# =============================================================================


class TestCSVIntegration:
    """Tests for CSV reading integration."""

    def test_get_all_categories(self):
        """Should read categories from CSV."""
        categories = get_all_categories_with_keywords()

        # Should have categories
        assert len(categories) > 0

        # Known categories should be present
        assert "aktivnaya-pena" in categories or len(categories) >= 5

    def test_categories_have_keywords(self):
        """Each category should have keywords list."""
        categories = get_all_categories_with_keywords()

        for slug, keywords in categories.items():
            assert isinstance(keywords, list), f"{slug} should have list"
            assert len(keywords) > 0, f"{slug} should have keywords"

    def test_keywords_have_required_fields(self):
        """Keywords should have required fields."""
        categories = get_all_categories_with_keywords()

        if categories:
            first_slug = list(categories.keys())[0]
            first_kw = categories[first_slug][0]

            assert "keyword" in first_kw, "Should have 'keyword' field"
            assert "volume" in first_kw, "Should have 'volume' field"


# =============================================================================
# Test: Mapping consistency
# =============================================================================


class TestMappingConsistency:
    """Tests for L3 to slug mapping."""

    def test_known_mappings(self):
        """Known L3 names should map to correct slugs."""
        from parse_semantics_to_json import L3_TO_SLUG

        known = {
            "Активная пена": "aktivnaya-pena",
            "Антимошка": "antimoshka",
            "Антибитум": "antibitum",
        }

        for l3, expected_slug in known.items():
            assert l3 in L3_TO_SLUG, f"{l3} should be in mapping"
            assert L3_TO_SLUG[l3] == expected_slug


# =============================================================================
# Test: Expected categories tiers
# =============================================================================


class TestExpectedTiers:
    """Tests for expected tier assignment based on known data."""

    def test_aktivnaya_pena_tier_a(self):
        """aktivnaya-pena (52 kw) should be Tier A."""
        # 52 > 30 → A
        assert auto_detect_tier(52) == "A"

    def test_antimoshka_tier_c(self):
        """antimoshka (6 kw) should be Tier C."""
        # 6 < 10 → C
        assert auto_detect_tier(6) == "C"

    def test_antibitum_tier_c(self):
        """antibitum (3 kw) should be Tier C."""
        # 3 < 10 → C
        assert auto_detect_tier(3) == "C"

    def test_cherniteli_shin_tier_b(self):
        """cherniteli-shin (24 kw) should be Tier B."""
        # 10 <= 24 <= 30 → B
        assert auto_detect_tier(24) == "B"


# =============================================================================
# Run tests manually
# =============================================================================


def run_tests():
    """Run all tests without pytest."""
    test_classes = [
        TestAutoDetectTier,
        TestTierThresholds,
        TestCategorySubdirs,
        TestExpectedTiers,
        TestMappingConsistency,
        TestCSVIntegration,
        TestCreateCategoryFolders,
        TestCreateTaskFile,
    ]

    total = 0
    passed = 0
    failed = 0

    print("=" * 60)
    print("RUNNING TESTS: test_setup_all.py")
    print("=" * 60)
    print()

    for test_class in test_classes:
        class_name = test_class.__name__
        print(f"--- {class_name} ---")

        instance = test_class()
        methods = [m for m in dir(instance) if m.startswith("test_")]

        for method_name in methods:
            total += 1
            try:
                getattr(instance, method_name)()
                print(f"  ✅ {method_name}")
                passed += 1
            except AssertionError as e:
                print(f"  ❌ {method_name}: {e}")
                failed += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {type(e).__name__}: {e}")
                failed += 1

        print()

    print("=" * 60)
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
