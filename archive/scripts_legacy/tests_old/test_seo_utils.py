import sys
import unittest
from pathlib import Path

# Adjust path to import scripts
sys.path.append(str(Path(__file__).parent.parent))

from seo_utils import count_chars_no_spaces, get_tier_requirements


class TestSeoUtils(unittest.TestCase):
    def test_tier_b_requirements(self):
        """Test that Tier B follows v7.3 standards (Shop Mode)"""
        reqs = get_tier_requirements("B")
        self.assertEqual(reqs["char_min"], 1500)
        self.assertEqual(reqs["char_max"], 2000)
        self.assertEqual(reqs["min_words"], 225)
        self.assertEqual(reqs["commercial_min"], 3)
        self.assertTrue(reqs["table_required"])

    def test_tier_a_requirements(self):
        """Test Tier A (Hubs)"""
        reqs = get_tier_requirements("A")
        self.assertEqual(reqs["char_min"], 2000)
        self.assertEqual(reqs["char_max"], 2500)

    def test_tier_c_requirements(self):
        """Test Tier C (Niche)"""
        reqs = get_tier_requirements("C")
        self.assertEqual(reqs["char_min"], 1000)
        self.assertEqual(reqs["char_max"], 1500)

    def test_char_counting(self):
        """Test NO SPACES counting"""
        text = "Hello World"  # 11 chars with space, 10 without
        self.assertEqual(count_chars_no_spaces(text), 10)

        text = "   "
        self.assertEqual(count_chars_no_spaces(text), 0)


if __name__ == "__main__":
    unittest.main()
