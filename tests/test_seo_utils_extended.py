#!/usr/bin/env python3
"""
Extended unit tests for seo_utils.py
"""

import sys
import time
import requests
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from seo_utils import (
    check_url_accessibility,
    check_commercial_markers,
    check_stoplist
)

class TestCheckUrlAccessibility:
    def test_accessibility_success_head(self):
        with patch("requests.head") as mock_head:
            mock_head.return_value.status_code = 200
            assert check_url_accessibility("http://test.com") is True
            mock_head.assert_called_once()

    def test_accessibility_fallback_get(self):
        with patch("requests.head") as mock_head, \
             patch("requests.get") as mock_get:
            
            mock_head.return_value.status_code = 405 # Method Not Allowed
            mock_get.return_value.status_code = 200
            
            assert check_url_accessibility("http://test.com") is True
            mock_get.assert_called_once()

    def test_accessibility_retry_logic(self):
        with patch("requests.head") as mock_head, \
             patch("time.sleep") as mock_sleep:
            
            # Fail twice, succeed on third
            mock_head.side_effect = [
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                MagicMock(status_code=200)
            ]
            
            assert check_url_accessibility("http://test.com", max_retries=3) is True
            assert mock_head.call_count == 3
            assert mock_sleep.call_count == 2

    def test_accessibility_fail_all_retries(self):
        with patch("requests.head") as mock_head, \
             patch("time.sleep"):
            
            mock_head.side_effect = requests.exceptions.Timeout
            
            assert check_url_accessibility("http://test.com", max_retries=2) is False
            assert mock_head.call_count == 2

    def test_accessibility_fail_non_200(self):
        with patch("requests.head") as mock_head, \
             patch("requests.get") as mock_get:
            
            mock_head.return_value.status_code = 404
            mock_get.return_value.status_code = 404
            
            assert check_url_accessibility("http://test.com") is False

class TestCheckCommercialMarkers:
    def test_commercial_markers_found(self):
        text = "Купить этот товар. Цена отличная. Доставка быстрая."
        result = check_commercial_markers(text, min_required=3)
        
        assert result['passed'] is True
        assert result['found_count'] >= 3
        assert 'купить' in result['found_markers']
        assert 'цена' in result['found_markers']
        assert 'доставка' in result['found_markers']

    def test_commercial_markers_insufficient(self):
        text = "Просто описание товара."
        result = check_commercial_markers(text, min_required=2)
        
        assert result['passed'] is False
        assert result['found_count'] == 0

    def test_commercial_markers_case_insensitive(self):
        text = "ЦЕНА супер."
        result = check_commercial_markers(text, min_required=1)
        
        assert result['passed'] is True
        assert 'цена' in result['found_markers']

class TestCheckStoplist:
    def test_stoplist_clean(self):
        text = "Хороший текст без воды."
        result = check_stoplist(text)
        
        assert result['passed'] is True
        assert len(result['violations']) == 0

    def test_stoplist_violations(self):
        text = "В современном мире ни для кого не секрет, что вода мокрая."
        result = check_stoplist(text)
        
        assert result['passed'] is False
        assert len(result['violations']) >= 2
        assert "в современном мире" in result['violations']
        assert "ни для кого не секрет" in result['violations']

    def test_stoplist_ai_fluff(self):
        text = "Давайте разберёмся в этом вопросе. В заключение хочется сказать..."
        result = check_stoplist(text)
        
        assert result['passed'] is False
        assert "давайте разберёмся" in result['violations']
        assert "в заключение" in result['violations']
