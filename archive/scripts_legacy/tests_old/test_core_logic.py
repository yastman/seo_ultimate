import sys
import unittest
from pathlib import Path

# Add scripts dir to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from check_simple_v2_md import check_keyword_density_and_distribution
    from parse_semantics_to_json import get_tier_targets
    from seo_utils import count_chars_no_spaces, get_tier_requirements
except ImportError:
    # Handle direct execution if needed
    sys.path.append(str(Path(__file__).parent.parent))
    from seo_utils import count_chars_no_spaces, get_tier_requirements

    # Note: check_simple_v2_md imports might need more mocking if they depend on file system
    pass


class TestSeoUtils(unittest.TestCase):
    def test_tier_b_targets(self):
        """Verify Tier B targets align with v7.3 Shop Mode"""
        reqs = get_tier_requirements("B")
        self.assertEqual(reqs["char_min"], 1500)
        self.assertEqual(reqs["char_max"], 2000)
        self.assertEqual(reqs["commercial_min"], 3)
        self.assertTrue(reqs["table_required"])

    def test_tier_a_targets(self):
        """Verify Tier A targets"""
        reqs = get_tier_requirements("A")
        self.assertEqual(reqs["char_min"], 2000)
        self.assertEqual(reqs["char_max"], 2500)
        self.assertEqual(reqs["commercial_min"], 4)

    def test_tier_c_targets(self):
        """Verify Tier C targets"""
        reqs = get_tier_requirements("C")
        self.assertEqual(reqs["char_min"], 1000)
        self.assertEqual(reqs["char_max"], 1500)
        self.assertEqual(reqs["commercial_min"], 2)

    def test_char_counting(self):
        """Verify character counting excludes spaces"""
        text = "Hello World"
        # "HelloWorld" = 10 chars
        self.assertEqual(count_chars_no_spaces(text), 10)

        text = "  A  B  "
        # "AB" = 2 chars
        self.assertEqual(count_chars_no_spaces(text), 2)


class TestParseSemanticsIntegration(unittest.TestCase):
    def test_data_generation_integration(self):
        """Verify parse_semantics_to_json uses seo_utils targets"""
        # Trigger the function that gets targets
        # It should now return strings "1500-2000" derived from seo_utils "char_min"/"char_max"
        from parse_semantics_to_json import get_tier_targets

        targets_b = get_tier_targets("B")
        self.assertEqual(targets_b["char_min"], 1500)
        self.assertEqual(targets_b["char_max"], 2000)
        self.assertEqual(targets_b["h2"], "3-4")


if __name__ == "__main__":
    unittest.main()
