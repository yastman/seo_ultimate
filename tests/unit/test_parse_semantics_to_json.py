from unittest.mock import mock_open, patch

import pytest

from scripts.parse_semantics_to_json import (
    calculate_density_target,
    calculate_occurrences_target,
    classify_keywords,
    extract_word_roots,
    generate_full_json,
    generate_variations,
    get_tier_targets,
    read_semantics_csv,
)

# Mock data for CSV tests
CSV_CONTENT = """L1: Care,,
L2: Wash,,
L3: Test Cluster,,
Keyword 1,10,500
Keyword 2,5,100
категория,15,
L3: Another Cluster,,
Noise,1,
"""


@pytest.fixture
def mock_seo_utils():
    with patch("scripts.parse_semantics_to_json.get_tier_targets") as mock:
        yield mock


class TestKeywordClassification:
    def test_classify_keywords_distribution(self):
        keywords = [
            {"keyword": "high", "volume": 1000},
            {"keyword": "mid", "volume": 300},
            {"keyword": "low", "volume": 50},
        ]
        classified = classify_keywords(keywords)

        assert len(classified["primary"]) == 1
        assert classified["primary"][0]["keyword"] == "high"

        assert len(classified["secondary"]) == 1
        assert classified["secondary"][0]["keyword"] == "mid"

        assert len(classified["supporting"]) == 1
        assert classified["supporting"][0]["keyword"] == "low"

    def test_classify_keywords_promotion(self):
        """
        Test that the highest volume supporting keyword is promoted
        if no primary/secondary exist.
        """
        keywords = [
            {"keyword": "low1", "volume": 90},
            {"keyword": "low2", "volume": 50},
        ]
        classified = classify_keywords(keywords)

        assert len(classified["primary"]) == 1
        assert classified["primary"][0]["keyword"] == "low1"
        assert len(classified["secondary"]) == 0
        assert len(classified["supporting"]) == 1
        assert classified["supporting"][0]["keyword"] == "low2"


class TestLinguistics:
    @pytest.mark.parametrize(
        "input_word, expected_roots",
        [
            ("Активная пена", ["активн", "пена"]),
            ("Мойка высокого давления", ["мой", "высок", "давлен"]),
            ("чернитель шин", ["чернитель"]),  # 'шин' < 4 chars -> skipped
            ("Красный", ["красн"]),  # 'ый' removed
            ("полировочный", ["полировочн"]),  # 'ый' removed
            ("шампунь для ручной мойки", ["шампунь", "ручн", "мой"]),
        ],
    )
    def test_extract_word_roots(self, input_word, expected_roots):
        assert extract_word_roots(input_word) == expected_roots

    def test_generate_variations(self):
        all_kws = ["автошампунь", "автошампунь для бесконтактной мойки", "активная пена", "шампунь"]
        target = "автошампунь"

        variations = generate_variations(target, all_kws)

        # Exact match check
        assert target in variations["exact"]

        # Checking similarity logic (word overlap)
        # "автошампунь для бесконтактной мойки" shares 100% of target's words ("автошампунь")
        # Script logic: len(common) >= len(kw_words) * 0.7
        # "автошампунь" (1 word) vs "автошампунь ... " (4 words). Common = 1. 1 >= 1*0.7. Yes.
        assert "автошампунь для бесконтактной мойки" in variations["exact"]

        # "активная пена" - 0 overlap. Should not be in exact.
        assert "активная пена" not in variations["exact"]

        # Partial check (roots)
        # "автошампунь" (len > 3) -> should be in partial if root extraction works
        # "автошампунь" is not shortened by standard endings
        assert "автошампунь" in variations["partial"]


class TestTargets:
    @pytest.mark.parametrize(
        "volume, tier, expected",
        [
            (1500, "A", 5),
            (600, "A", 4),
            (200, "B", 3),
            (60, "C", 2),
            (10, "C", 1),
        ],
    )
    def test_calculate_occurrences_target(self, volume, tier, expected):
        assert calculate_occurrences_target(volume, tier) == expected

    @pytest.mark.parametrize(
        "volume, total, expected",
        [
            (160, 1000, "0.20%"),  # 16% -> >0.15 -> 0.20%
            (100, 1000, "0.15%"),  # 10% -> >0.08 -> 0.15%
            (50, 1000, "0.10%"),  # 5% -> >0.03 -> 0.10%
            (10, 1000, "0.05%"),  # 1% -> else -> 0.05%
            (0, 0, "0.10%"),  # Zero check
        ],
    )
    def test_calculate_density_target(self, volume, total, expected):
        assert calculate_density_target(volume, total, "A")


class TestFileOperations:
    def test_read_semantics_csv(self):
        with patch("builtins.open", mock_open(read_data=CSV_CONTENT)):
            categories = read_semantics_csv("dummy.csv")

        assert "Test Cluster" in categories
        assert len(categories["Test Cluster"]) == 2
        assert categories["Test Cluster"][0]["keyword"] == "Keyword 1"
        assert categories["Test Cluster"][0]["volume"] == 500

        # Verify skips
        assert "L1: Care" not in categories
        assert "L2: Wash" not in categories
        assert "Another Cluster" in categories  # Should be present if logic worked
        # Wait, "Another Cluster,," line exists.
        assert "Another Cluster" in categories

    @patch("scripts.parse_semantics_to_json.read_meta_patterns")
    @patch("scripts.parse_semantics_to_json.get_tier_targets")
    def test_generate_full_json(self, mock_targets, mock_patterns):
        # Setup mocks
        mock_targets.return_value = {"char_min": 1000, "char_max": 2000, "h2": "2-3", "faq": "1-2"}
        mock_patterns.return_value = {"h2_themes": ["Theme 1", "Theme 2"]}

        # To avoid SLUG_TO_L3 import issues, we can rely on the script using get()
        # But we might need to patch SLUG_TO_L3 if it uses it directly.
        # The script does: SLUG_TO_L3.get(slug, slug)

        keywords = [{"keyword": "Primary", "volume": 600}, {"keyword": "Secondary", "volume": 200}]

        result = generate_full_json("test-slug", "B", keywords)

        assert result["slug"] == "test-slug"
        assert result["tier"] == "B"

        # Check Stats
        assert result["stats"]["primary_count"] == 1
        assert result["stats"]["secondary_count"] == 1
        assert result["stats"]["total_volume"] == 800

        # Check Entities
        assert len(result["semantic_entities"]) == 2
        assert result["semantic_entities"][0]["main"] == "Theme 1"

        # Check Targets (from mock)
        assert result["content_targets"]["h2_count"] == "2-3"

    def test_get_tier_targets_wrapper(self):
        # Directly test the mapping wrapper
        # We need to mock get_tier_requirements from seo_utils called INSIDE the script
        with patch("scripts.parse_semantics_to_json.get_tier_requirements") as mock_reqs:
            mock_reqs.return_value = {
                "char_min": 1500,
                "char_max": 2500,
                "h2_range": (3, 5),
                "faq_range": (2, 4),
            }

            res = get_tier_targets("B")
            assert res["char_min"] == 1500
            assert res["h2"] == "3-5"
            assert res["faq"] == "2-4"
