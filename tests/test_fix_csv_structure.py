import csv
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

# Add scripts directory to path to allow 'import config' to work inside scripts
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

# Import the module to be tested
# We need to handle potential import errors if config is not in pythonpath,
# but assuming standard environment described in instructions.
from scripts.fix_csv_structure import fix_csv, is_explicit_marker


class TestFixCsvStructure(unittest.TestCase):
    def test_is_explicit_marker(self):
        # Explicit L-markers
        self.assertTrue(is_explicit_marker("L1: Category", "10"))
        self.assertTrue(is_explicit_marker("l2: Category", "5"))
        self.assertTrue(is_explicit_marker("L3: Cluster", "1"))

        # SEO filters
        self.assertTrue(is_explicit_marker("SEO-фильтр: Brand", "100"))
        self.assertTrue(is_explicit_marker("seo-filter: Type", "1"))

        # Explicit "Категория"
        self.assertTrue(is_explicit_marker("Категория: Name", "50"))
        self.assertTrue(is_explicit_marker("категория товара", "50"))

        # Slash format in col2 (implicit marker)
        self.assertTrue(is_explicit_marker("Some Keywords", "3/50"))
        self.assertTrue(is_explicit_marker("Anything", "1/5"))

        # Non-markers
        self.assertFalse(is_explicit_marker("Just a keyword", "100"))
        self.assertFalse(is_explicit_marker("Low freq keyword", "3"))
        self.assertFalse(is_explicit_marker("Empty count", ""))

    def test_fix_csv_logic(self):
        # Define test data
        # Format: col1, col2, col3
        input_rows = [
            ["Header", "Count", "Volume"],
            ["L1: Valid Marker", "3", "0"],  # Should KEEP (Marker)
            ["Normal Keyword", "3", "0"],  # Should FIX (1-4 count, empty vol)
            ["High Freq Keyword", "5", "0"],  # Should KEEP (>4)
            ["Keyword with Vol", "3", "100"],  # Should KEEP (Col3 not empty)
            ["Split Cluster", "2/10", "0"],  # Should KEEP (slash in col2)
            ["Very Low Keyword", "1", ""],  # Should FIX
            ["Edge Case 4", "4", "0"],  # Should FIX
            ["Edge Case 5", "5", "0"],  # Should KEEP
        ]

        # Expected output after fix
        # Note: fix_csv only clears col2, col3 remains unchanged
        expected_rows = [
            ["Header", "Count", "Volume"],
            ["L1: Valid Marker", "3", "0"],
            ["Normal Keyword", "", "0"],  # Fixed: col2 cleared, col3 stays "0"
            ["High Freq Keyword", "5", "0"],
            ["Keyword with Vol", "3", "100"],
            ["Split Cluster", "2/10", "0"],
            ["Very Low Keyword", "", ""],  # Fixed: col2 cleared, col3 was ""
            ["Edge Case 4", "", "0"],  # Fixed: col2 cleared, col3 stays "0"
            ["Edge Case 5", "5", "0"],
        ]

        # Use a temporary file for testing
        test_file = Path("test_semantics.csv")
        backup_file = Path("test_semantics_backup.csv")

        # Write input data
        with open(test_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(input_rows)

        try:
            # Mock SEMANTICS_CSV to point to our test file
            # We also need to patch the BACKUP path logic or just let it happen in the cwd
            # Since fix_csv uses SEMANTICS_CSV.parent, if we use a local Path("test.csv"),
            # parent is "." so it works.

            with patch("scripts.fix_csv_structure.SEMANTICS_CSV", test_file):
                # Also patch print to avoid cluttering output
                with patch("builtins.print"):
                    fix_csv()

            # Read back the file
            with open(test_file, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                output_rows = list(reader)

            # Compare rows
            # Note: fix_csv might add extra columns if input had fewer than 3, but our input has 3.
            # However, fix_csv does `current_row[1] = ""` so it preserves column count of 3.

            self.assertEqual(len(output_rows), len(expected_rows))

            for i, (out, exp) in enumerate(zip(output_rows, expected_rows, strict=False)):
                self.assertEqual(out, exp, f"Row {i} mismatch: {out} != {exp}")

        finally:
            # Cleanup
            if test_file.exists():
                test_file.unlink()
            # The script creates a backup file
            if backup_file.exists():
                backup_file.unlink()


if __name__ == "__main__":
    unittest.main()
