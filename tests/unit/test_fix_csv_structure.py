import csv
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure scripts dir is in path for imports to work
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from scripts.fix_csv_structure import fix_csv, is_explicit_marker


class TestFixCsvStructure:
    @pytest.mark.parametrize(
        "col1, col2, expected",
        [
            ("L1: Category", "10", True),
            ("l2: Subcat", "5", True),
            ("L3: Cluster", "1", True),
            ("SEO-фильтр: Name", "100", True),
            ("seo-filter: filter", "1", True),
            ("Категория: Товары", "50", True),
            ("категория штук", "10", True),
            ("Mixed Case Keyword", "3/50", True),  # Slash format
            ("Implicit", "1/5", True),
            ("Just Keyword", "100", False),
            ("Low freq", "3", False),
            ("Empty", "", False),
        ],
    )
    def test_is_explicit_marker_logic(self, col1, col2, expected):
        assert is_explicit_marker(col1, col2) is expected

    def test_fix_csv_end_to_end(self, tmp_path):
        """
        Test the full fix_csv flow:
        1. Create a mock CSV with mixed valid/invalid lines.
        2. Run fix_csv().
        3. Verify invalid lines (col2=1-4) are cleared.
        4. Verify valid lines are kept.
        5. Verify backup is created.
        """
        # 1. Setup Data
        input_rows = [
            ["Header", "Count", "Volume"],
            ["L1: Valid Marker", "3", "0"],  # KEEP (Marker)
            ["Normal Keyword", "3", "0"],  # FIX (1-4 count, empty vol)
            ["High Freq", "5", "0"],  # KEEP (>4)
            ["Keyword with Vol", "3", "100"],  # KEEP (Col3 not empty)
            ["Split Cluster", "2/10", "0"],  # KEEP (slash)
            ["Low Keyword", "1", ""],  # FIX
            ["Clean Keyword", "4", "0"],  # FIX
        ]

        test_csv = tmp_path / "test_semantics.csv"
        backup_csv = tmp_path / "test_semantics_backup.csv"

        with open(test_csv, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(input_rows)

        # 2. Run with patches
        # We must patch the module-level variables in scripts.fix_csv_structure
        with (
            patch("scripts.fix_csv_structure.SEMANTICS_CSV", test_csv),
            patch("scripts.fix_csv_structure.BACKUP_CSV", backup_csv),
        ):
            fix_csv()

        # 3. Verify Output
        with open(test_csv, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            output_rows = list(reader)

        assert len(output_rows) == len(input_rows)

        # Check specific rows
        # Row 0: Header - Unchanged
        assert output_rows[0] == ["Header", "Count", "Volume"]

        # Row 1: Valid Marker - Unchanged
        assert output_rows[1] == ["L1: Valid Marker", "3", "0"]

        # Row 2: Normal Keyword - Fixed (col2 cleared)
        assert output_rows[2] == ["Normal Keyword", "", "0"]

        # Row 3: High Freq - Unchanged
        assert output_rows[3] == ["High Freq", "5", "0"]

        # Row 4: With Volume - Unchanged
        assert output_rows[4] == ["Keyword with Vol", "3", "100"]

        # Row 6: Low Keyword - Fixed (col2 cleared)
        assert output_rows[6] == ["Low Keyword", "", ""]

        # 4. Verify Backup
        assert backup_csv.exists()

        # Backup should be a copy of the ORIGINAL input
        with open(backup_csv, "r", encoding="utf-8", newline="") as f:
            backup_rows = list(csv.reader(f))
        assert backup_rows == input_rows

    def test_fix_csv_no_changes_needed(self, tmp_path):
        """Test flow when no rows need fixing."""
        input_rows = [
            ["Header", "Count", "Volume"],
            ["Good Keyword", "10", "100"],
        ]
        test_csv = tmp_path / "clean.csv"

        with open(test_csv, "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerows(input_rows)

        with (
            patch("scripts.fix_csv_structure.SEMANTICS_CSV", test_csv),
            patch("scripts.fix_csv_structure.BACKUP_CSV", tmp_path / "backup.csv"),
        ):
            # Capture print to verify message
            with patch("builtins.print"):
                fix_csv()

        # Verify file unchanged
        with open(test_csv, "r", encoding="utf-8", newline="") as f:
            assert list(csv.reader(f)) == input_rows

        # Verify no backup created (script logic: if changes: backup)
        # Actually script logic: "if changes: ... backup ... else: print 'no changes'".
        assert not (tmp_path / "backup.csv").exists()
