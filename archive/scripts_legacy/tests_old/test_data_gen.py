import sys
import unittest
from pathlib import Path

# Adjust path to import scripts
sys.path.append(str(Path(__file__).parent.parent))

# Import the function we modified
from parse_semantics_to_json import get_tier_targets


class TestDataGenerator(unittest.TestCase):
    def test_get_tier_targets_integration(self):
        """
        Verify that parse_semantics_to_json.get_tier_targets
        correctly pulls data from seo_utils.
        """
        # Test Tier B (should be 1500-2000, NOT 4000-4500)
        targets = get_tier_targets("B")

        self.assertEqual(targets["char_min"], 1500)
        self.assertEqual(targets["char_max"], 2000)

        # Check range string format
        self.assertEqual(targets["h2"], "3-4")
        self.assertEqual(targets["faq"], "3-5")

    def test_tier_a_integration(self):
        targets = get_tier_targets("A")
        self.assertEqual(targets["char_min"], 2000)
        self.assertEqual(targets["char_max"], 2500)


if __name__ == "__main__":
    unittest.main()
