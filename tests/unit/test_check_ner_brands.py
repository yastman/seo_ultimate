import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from scripts.check_ner_brands import (
    analyze_file,
    check_blacklist,
    clean_markdown,
    is_false_positive_location,
)


class TestCheckNerBrands(unittest.TestCase):
    def test_is_false_positive_location(self):
        # "ровно" is in FALSE_POSITIVE_CITIES

        # 1. No preposition -> False Positive (True)
        self.assertTrue(is_false_positive_location("ровно", "отрезал ровно половину"))
        self.assertTrue(is_false_positive_location("Ровно", "Лежит Ровно посередине"))

        # 2. With preposition -> Real City (False)
        self.assertFalse(is_false_positive_location("ровно", "поехал в ровно на машине"))
        self.assertFalse(is_false_positive_location("Ровно", "из Ровно привезли"))
        self.assertFalse(is_false_positive_location("ровно", "до ровно пять километров"))

        # 3. "суми" (mistake for "суммы" or city)
        self.assertTrue(is_false_positive_location("суми", "большие суми денег"))
        self.assertFalse(is_false_positive_location("суми", "в суми отличная погода"))

        # 4. Word NOT in false positive list -> Always Real City (False)
        self.assertFalse(is_false_positive_location("киев", "просто киев стоит"))

    def test_check_blacklist_brands(self):
        # Test detection of banned brands
        text = "Мы продаем технику Karcher и химию Grass для авто."
        results = check_blacklist(text)

        brands_found = [item["entity"] for item in results["brands"]]
        self.assertIn("karcher", brands_found)
        self.assertIn("grass", brands_found)
        self.assertEqual(len(results["brands"]), 2)

    def test_check_blacklist_cities(self):
        # Test detection of banned cities
        text = "Доставка в Киев, Харьков и Одессу возможна."
        results = check_blacklist(text)

        cities_found = [item["entity"] for item in results["cities"]]
        self.assertIn("киев", cities_found)
        self.assertIn("харьков", cities_found)
        # "одессу" matches "одесса" in blacklist?
        # The script uses `if city in text_lower`.
        # "одесса" is NOT in "одессу".
        # But "одеса" (ukr) might be?
        # Let's check regex logic in script: `re.finditer(re.escape(city), text_lower)`
        # If blacklist has "одесса", and text has "одессу", it won't match.
        # This confirms current strict matching behavior.

        # Let's test exact match
        text2 = "Город Одесса красивый."
        results2 = check_blacklist(text2)
        self.assertIn("одесса", [item["entity"] for item in results2["cities"]])

    def test_check_blacklist_ai_fluff(self):
        # Test AI fluff detection
        text = "В заключение, стоит отметить, что этот товар уникален."
        results = check_blacklist(text)

        fluff_found = [item["entity"] for item in results["ai_fluff"]]
        # expected matches based on patterns
        # "в заключение"
        # "стоит отметить"

        self.assertTrue(any("в заключение" in f for f in fluff_found))
        self.assertTrue(any("стоит отметить" in f for f in fluff_found))

    def test_clean_markdown(self):
        md_text = """
# Header
Some [link](url) here.
**Bold** text.
---
Frontmatter
---
* List item
"""
        cleaned = clean_markdown(md_text)
        self.assertNotIn("# Header", cleaned)  # Headers usually removed or hash removed
        self.assertNotIn("[link](url)", cleaned)  # Links simplified
        self.assertNotIn("**Bold**", cleaned)  # Formatting removed
        self.assertIn("Some link here", cleaned)
        self.assertIn("Bold text", cleaned)

    def test_analyze_file_safe_pass(self):
        # Create a clean temporary file
        temp_file = Path("temp_safe_test.md")
        temp_file.write_text(
            "Хороший текст про полировку автомобиля. Без брендов.", encoding="utf-8"
        )

        try:
            # Mock print to suppress output
            with patch("builtins.print"):
                exit_code = analyze_file(str(temp_file))
            self.assertEqual(exit_code, 0)
        finally:
            if temp_file.exists():
                temp_file.unlink()

    def test_analyze_file_warning(self):
        # Create a file with forbidden content
        temp_file = Path("temp_bad_test.md")
        temp_file.write_text("Мы продаем Karcher в Киеве. В заключение...", encoding="utf-8")

        try:
            with patch("builtins.print"):
                exit_code = analyze_file(str(temp_file))
            self.assertEqual(exit_code, 1)  # Expect warning
        finally:
            if temp_file.exists():
                temp_file.unlink()


if __name__ == "__main__":
    unittest.main()
