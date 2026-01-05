from scripts.config import CATEGORIES_DIR, L3_TO_SLUG, PROJECT_ROOT, QUALITY_THRESHOLDS


class TestConfig:
    def test_paths_exist(self):
        """Verify critical project paths exist."""
        assert PROJECT_ROOT.exists()
        assert CATEGORIES_DIR.exists()

    def test_constants_types(self):
        """Verify constants have correct types."""
        assert isinstance(QUALITY_THRESHOLDS, dict)
        assert isinstance(QUALITY_THRESHOLDS["water_target_max"], (int, float))
        assert isinstance(L3_TO_SLUG, dict)

    def test_l3_clusters_structure(self):
        """Verify L3_CLUSTERS mapping validity."""
        if L3_TO_SLUG:
            # Check arbitrary item
            key = next(iter(L3_TO_SLUG))
            val = L3_TO_SLUG[key]
            assert isinstance(key, str)
            assert isinstance(val, str)
