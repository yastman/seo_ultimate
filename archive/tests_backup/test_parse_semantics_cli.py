#!/usr/bin/env python3
"""
CLI tests for parse_semantics_to_json.py
"""

import sys
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from parse_semantics_to_json import list_categories, main


@pytest.fixture
def mock_semantics_data():
    return {
        "Активная пена": [
            {"keyword": "активная пена", "volume": 1000},
            {"keyword": "купить пену", "volume": 500},
        ],
        "Для ручной мойки": [{"keyword": "шампунь", "volume": 200}],
    }


@pytest.fixture
def mock_generated_json():
    return {
        "schema_version": "3.0.0",
        "slug": "aktivnaya-pena",
        "keywords": {"primary": [], "secondary": [], "supporting": []},
        "stats": {
            "primary_count": 0,
            "secondary_count": 0,
            "supporting_count": 0,
            "total_keywords": 0,
            "total_volume": 0,
        },
    }


class TestListCategories:
    @patch("parse_semantics_to_json.read_semantics_csv")
    def test_list_categories_prints_output(self, mock_read, mock_semantics_data, capsys):
        mock_read.return_value = mock_semantics_data

        list_categories()

        captured = capsys.readouterr()
        assert "aktivnaya-pena" in captured.out
        assert "Активная пена" in captured.out
        assert "Keywords:   2" in captured.out
        assert "Volume:  1500" in captured.out


class TestMain:
    def test_main_no_args_exits(self, capsys):
        with patch.object(sys, "argv", ["script.py"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1

        captured = capsys.readouterr()
        assert "Usage:" in captured.out

    @patch("parse_semantics_to_json.list_categories")
    def test_main_list_arg(self, mock_list, capsys):
        with patch.object(sys, "argv", ["script.py", "--list"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
            mock_list.assert_called_once()

    def test_main_unknown_slug(self, capsys):
        with patch.object(sys, "argv", ["script.py", "unknown-slug"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1

        captured = capsys.readouterr()
        assert "Unknown slug: unknown-slug" in captured.out

    @patch("parse_semantics_to_json.read_semantics_csv")
    def test_main_category_not_in_csv(self, mock_read, capsys):
        mock_read.return_value = {}
        # 'aktivnaya-pena' maps to 'Активная пена'

        with patch.object(sys, "argv", ["script.py", "aktivnaya-pena"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1

        captured = capsys.readouterr()
        assert "Category not found: Активная пена" in captured.out

    @patch("parse_semantics_to_json.read_semantics_csv")
    @patch("parse_semantics_to_json.generate_full_json")
    @patch("pathlib.Path.mkdir")
    def test_main_success_flow(
        self,
        mock_mkdir,
        mock_gen,
        mock_read,
        mock_semantics_data,
        mock_generated_json,
        capsys,
        tmp_path,
    ):
        mock_read.return_value = mock_semantics_data
        mock_gen.return_value = mock_generated_json

        # We need to mock open to verify file writing, but since main constructs
        # path using Path, it's easier to patch 'builtins.open' or let it write to tmp_path
        # if we could inject it. But main uses hardcoded paths relative to CWD.
        # We will patch 'builtins.open' with mock_open.

        m_open = mock_open()

        with (
            patch.object(sys, "argv", ["script.py", "aktivnaya-pena", "A"]),
            patch("builtins.open", m_open),
        ):
            main()

        # Verify interactions
        mock_read.assert_called_once()
        mock_gen.assert_called_once()

        # Check generate_full_json args
        args, _ = mock_gen.call_args
        assert args[0] == "aktivnaya-pena"  # slug
        assert args[1] == "A"  # tier
        assert len(args[2]) == 2  # keywords list

        # Check file write
        m_open.assert_called()
        handle = m_open()
        handle.write.assert_called()

        # Check output
        captured = capsys.readouterr()
        assert "Generating JSON" in captured.out
        assert "Written:" in captured.out
