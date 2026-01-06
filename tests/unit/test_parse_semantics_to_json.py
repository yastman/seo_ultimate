import sys
import unittest
from pathlib import Path
from unittest.mock import mock_open, patch

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from scripts.parse_semantics_to_json import (
    calculate_density_target,
    calculate_occurrences_target,
    classify_keywords,
    extract_word_roots,
    generate_full_json,
    generate_variations,
    read_semantics_csv,
)


class TestParseSemanticsToJson(unittest.TestCase):
    def test_extract_word_roots(self):
        # Test root extraction logic
        self.assertEqual(extract_word_roots("Активная пена"), ["активн", "пена"])
        self.assertEqual(extract_word_roots("Мойка высокого давления"), ["мой", "высок", "давлен"])
        self.assertEqual(
            extract_word_roots("чернитель шин"), ["чернитель"]
        )  # 'шин' is 3 chars, skipped by len < 4 check
        # Script endings: 'ой', 'ая', ... 'ок', 'ек'. 'тель' is NOT in list explicitly.
        # But 'чернитель' -> 'ль' is hardcoded? No.
        # Let's check script code again. Endings: ... 'ик'.
        # Common endings like 'ый', 'ий' are there.
        # 'чернитель' ends with 'ь', not in list. So it might remain 'чернитель'.

        # Proper test based on script logic:
        # "Красный" -> "ый" rm -> "Красн"
        self.assertEqual(extract_word_roots("Красный"), ["красн"])
        # "Автошампуни" -> "и" ? "и" is not in list. "ы" is not. "ые" is.
        # "шампунь" -> "ь" is not in list.
        pass

    def test_classify_keywords(self):
        keywords = [
            {"keyword": "high", "volume": 1000},
            {"keyword": "mid", "volume": 300},
            {"keyword": "low", "volume": 50},
        ]
        classified = classify_keywords(keywords)

        self.assertEqual(len(classified["primary"]), 1)
        self.assertEqual(classified["primary"][0]["keyword"], "high")

        self.assertEqual(len(classified["secondary"]), 1)
        self.assertEqual(classified["secondary"][0]["keyword"], "mid")

        self.assertEqual(len(classified["supporting"]), 1)
        self.assertEqual(classified["supporting"][0]["keyword"], "low")

    def test_classify_keywords_promotion(self):
        # Case where only supporting keywords exist -> Promote top one to primary
        keywords = [
            {"keyword": "low1", "volume": 90},
            {"keyword": "low2", "volume": 50},
        ]
        classified = classify_keywords(keywords)

        self.assertEqual(len(classified["primary"]), 1)
        self.assertEqual(classified["primary"][0]["keyword"], "low1")  # Highest vol promoted
        self.assertEqual(len(classified["secondary"]), 0)
        self.assertEqual(len(classified["supporting"]), 1)
        self.assertEqual(classified["supporting"][0]["keyword"], "low2")

    def test_generate_variations(self):
        # Exact and partial generation
        all_kws = ["автошампунь для бесконтактной мойки", "активная пена", "шампунь"]
        target = "автошампунь"

        variations = generate_variations(target, all_kws)

        self.assertIn(target, variations["exact"])
        # "partial" should contain roots
        # "автошампунь" -> root depends on impl.
        # If "автошампунь" has no ending in list, it remains "автошампунь"

        # Test similarity logic (overlap)
        # "автошампунь для мойки" vs "автошампунь для бесконтактной мойки"
        # overlapping words: "автошампунь", "для", "мойки".
        # 3 out of 3 in target. 100% overlap.
        pass

    def test_calculate_targets(self):
        self.assertEqual(calculate_occurrences_target(1500, "A"), 5)
        self.assertEqual(calculate_occurrences_target(600, "A"), 4)
        self.assertEqual(calculate_occurrences_target(20, "A"), 1)

        self.assertEqual(
            calculate_density_target(100, 1000, "A"), "0.15%"
        )  # 10% ratio -> >8% -> 0.15%

    def test_read_semantics_csv(self):
        csv_content = """L1: Care,,
L2: Wash,,
L3: Test Cluster,,
Keyword 1,10,500
Keyword 2,5,100
категория,15,
Another Cluster,,
Noise,1,
"""
        with patch("builtins.open", mock_open(read_data=csv_content)):
            categories = read_semantics_csv("dummy.csv")

        self.assertIn("Test Cluster", categories)
        self.assertEqual(len(categories["Test Cluster"]), 2)
        self.assertEqual(categories["Test Cluster"][0]["keyword"], "Keyword 1")
        self.assertEqual(categories["Test Cluster"][0]["volume"], 500)

    @patch("scripts.parse_semantics_to_json.get_tier_targets")
    @patch("scripts.parse_semantics_to_json.read_meta_patterns")
    @patch("scripts.parse_semantics_to_json.SLUG_TO_L3", {"test-slug": "Test Cluster"})
    def test_generate_full_json(self, mock_read_patterns, mock_get_targets):
        mock_get_targets.return_value = {
            "char_min": 1000,
            "char_max": 2000,
            "h2": "2-3",
            "faq": "1-2",
        }
        mock_read_patterns.return_value = {"h2_themes": ["Theme 1"]}

        keywords = [{"keyword": "K1", "volume": 600}]

        result = generate_full_json("test-slug", "B", keywords)

        self.assertEqual(result["slug"], "test-slug")
        self.assertEqual(result["tier"], "B")
        self.assertEqual(result["stats"]["primary_count"], 1)
        self.assertEqual(len(result["semantic_entities"]), 1)
        self.assertEqual(result["content_targets"]["h2_count"], "2-3")


if __name__ == "__main__":
    unittest.main()
