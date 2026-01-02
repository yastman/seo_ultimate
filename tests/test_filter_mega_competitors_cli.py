#!/usr/bin/env python3
"""
CLI tests for filter_mega_competitors.py
"""

import sys
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from filter_mega_competitors import main

class TestFilterMegaCompetitorsCli:
    
    @patch("filter_mega_competitors.argparse.ArgumentParser.parse_args")
    def test_main_mega_csv_not_found(self, mock_args, capsys):
        mock_args.return_value = MagicMock(
            slug="test-slug", 
            mega_csv="nonexistent.csv",
            data_json=None,
            output_dir=None,
            min_competitors=None,
            tier=None,
            min_h2_themes=3
        )
        
        with patch("pathlib.Path.exists", side_effect=lambda: False): # Base dir exists, but file doesn't
             # We need base_dir to exist? No, Path.exists is called on files.
             pass
             
        # Mocking exists specifically for mega csv
        with patch("pathlib.Path.exists", return_value=False):
            assert main() == 2
            
        captured = capsys.readouterr()
        assert "MEGA CSV not found" in captured.err

    @patch("filter_mega_competitors.argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    def test_main_category_json_not_found(self, mock_exists, mock_args, capsys):
        mock_args.return_value = MagicMock(
            slug="test-slug", 
            mega_csv="exist.csv",
            data_json="missing.json",
            output_dir=None,
            min_competitors=None,
            tier=None,
            min_h2_themes=3
        )
        
        # mega_csv exists, data_json does not
        mock_exists.side_effect = [True, False, False] # mega_csv, clean_json, raw_json/data_json
        
        assert main() == 2
        
        captured = capsys.readouterr()
        assert "Category JSON not found" in captured.err

    @patch("filter_mega_competitors.argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    @patch("filter_mega_competitors.load_category_keywords")
    def test_main_no_keywords(self, mock_load_kw, mock_exists, mock_args, capsys):
        mock_args.return_value = MagicMock(slug="test", mega_csv="e.csv", data_json="e.json", output_dir=None, min_competitors=None, tier=None, min_h2_themes=3)
        mock_exists.return_value = True
        mock_load_kw.return_value = [] # No keywords
        
        with patch("pathlib.Path.mkdir"):
            assert main() == 2
            
        captured = capsys.readouterr()
        assert "No keywords found" in captured.err

    @patch("filter_mega_competitors.argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    @patch("filter_mega_competitors.load_category_keywords")
    @patch("filter_mega_competitors.load_url_mapping")
    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("csv.DictReader")
    @patch("filter_mega_competitors.is_category_page_simple", return_value=True)
    @patch("filter_mega_competitors.is_blacklisted_domain", return_value=False)
    def test_main_success_flow(self, mock_is_blacklist, mock_is_cat, mock_csv_reader, mock_path_open, mock_load_map, mock_load_kw, mock_exists, mock_args, capsys):
        mock_args.return_value = MagicMock(
            slug="test-slug", 
            mega_csv="mega.csv",
            data_json="data.json",
            output_dir="out",
            min_competitors=None,
            tier="B",
            min_h2_themes=1 # Low to pass
        )
        mock_exists.return_value = True
        mock_load_kw.return_value = ["test"]
        
        # 5 URLs to satisfy Tier B (min 4)
        urls = [f"http://example.com/test{i}" for i in range(5)]
        mock_load_map.return_value = set(urls)
        
        # Mock CSV rows
        rows = []
        for url in urls:
            rows.append({
                "Address": url, 
                "Status Code": "200", 
                "Title 1": "Test Page", 
                "H1-1": "Test H1", 
                "H2-1": "Theme 1"
            })
        mock_csv_reader.return_value = rows
        
        with patch("pathlib.Path.mkdir"):
            with patch("json.dump") as mock_json_dump:
                with patch("csv.DictWriter"):
                    assert main() == 0 # Success
        
        captured = capsys.readouterr()
        assert "SUCCESS: All thresholds met" in captured.out

    @patch("filter_mega_competitors.argparse.ArgumentParser.parse_args")
    @patch("pathlib.Path.exists")
    @patch("filter_mega_competitors.load_category_keywords")
    @patch("filter_mega_competitors.load_url_mapping")
    @patch("pathlib.Path.open", new_callable=mock_open)
    @patch("csv.DictReader")
    @patch("filter_mega_competitors.is_category_page_simple", return_value=True)
    @patch("filter_mega_competitors.is_blacklisted_domain", return_value=False)
    def test_main_fail_thresholds(self, mock_is_blacklist, mock_is_cat, mock_csv_reader, mock_path_open, mock_load_map, mock_load_kw, mock_exists, mock_args, capsys):
        mock_args.return_value = MagicMock(
            slug="test-slug", 
            mega_csv="mega.csv",
            data_json="data.json",
            output_dir="out",
            min_competitors=10, # High threshold to force fail
            tier="B",
            min_h2_themes=1
        )
        mock_exists.return_value = True
        mock_load_kw.return_value = ["test"]
        mock_load_map.return_value = {"http://example.com/test"}
        
        mock_csv_reader.return_value = [
            {"Address": "http://example.com/test", "Status Code": "200", "Title 1": "Test Page", "H1-1": "Test H1", "H2-1": "Theme 1"}
        ]
        
        with patch("pathlib.Path.mkdir"):
            with patch("json.dump"):
                with patch("csv.DictWriter"):
                    assert main() == 2 # Fail
        
        captured = capsys.readouterr()
        assert "FAIL: Minimum thresholds not met" in captured.out
