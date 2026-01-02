#!/usr/bin/env python3
"""
CLI tests for parse_hubs_logic.py
"""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from parse_hubs_logic import main

class TestParseHubsLogicCli:
    
    @patch("parse_hubs_logic.parse_structure")
    @patch("parse_hubs_logic.generate_hub_tasks")
    @patch("pathlib.Path.exists")
    def test_main_success_flow(self, mock_exists, mock_generate, mock_parse, capsys):
        """Test main execution flow when file exists."""
        mock_exists.return_value = True
        mock_parse.return_value = {"L1": {}}
        
        main()
        
        mock_parse.assert_called_once()
        mock_generate.assert_called_once()
        
        captured = capsys.readouterr()
        assert "Parsing structure from:" in captured.out
        assert "Generating Task Files..." in captured.out
        assert "Done." in captured.out

    @patch("pathlib.Path.exists")
    def test_main_file_not_found(self, mock_exists, capsys):
        """Test main execution when CSV file is missing."""
        mock_exists.return_value = False
        
        main()
        
        captured = capsys.readouterr()
        assert "Error: CSV file not found" in captured.out
