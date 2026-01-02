#!/usr/bin/env python3
"""
Extended unit tests for quality_runner.py covering edge cases and error handling.
"""

import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from quality_runner import QualityCheck, main

@pytest.fixture
def mock_file(tmp_path):
    f = tmp_path / "test.md"
    f.write_text("# Test\nContent", encoding="utf-8")
    return f

class TestQualityCheckMarkdownExtended:
    def test_markdown_import_error_fallback_success(self, mock_file, capsys):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch.dict(sys.modules, {'pymarkdown.api': None}):
            # Remove from modules if present to trigger ImportError
            # But sys.modules[name]=None works for many import mechanisms
            
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="")
                
                status, errors = qc.check_markdown_structure()
                assert status == 'PASS'
                
        captured = capsys.readouterr()
        assert "pymarkdownlnt not installed, using markdownlint CLI" in captured.out

    def test_markdown_import_error_fallback_fail(self, mock_file, capsys):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch.dict(sys.modules, {'pymarkdown.api': None}):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=1, stdout="Error 1\nError 2")
                
                status, errors = qc.check_markdown_structure()
                assert status == 'WARN'
                assert len(errors) == 2

    def test_markdown_all_tools_missing(self, mock_file, capsys):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch.dict(sys.modules, {'pymarkdown.api': None}):
            with patch("subprocess.run", side_effect=FileNotFoundError):
                status, errors = qc.check_markdown_structure()
                assert status == 'FAIL'
                assert "Neither pymarkdownlnt nor markdownlint CLI found" in errors[0]

class TestQualityCheckGrammarExtended:
    def test_grammar_exception(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        # Mock the module first
        mock_module = MagicMock()
        mock_tool_class = MagicMock()
        mock_tool_instance = MagicMock()
        mock_tool_instance.check.side_effect = Exception("Boom")
        mock_tool_class.return_value = mock_tool_instance
        mock_module.LanguageTool = mock_tool_class
        
        with patch.dict(sys.modules, {'language_tool_python': mock_module}):
            status, errors = qc.check_grammar()
            assert status == 'FAIL'
            assert "Grammar check failed: Boom" in errors[0]

class TestQualityCheckWaterExtended:
    def test_water_import_error(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch.dict(sys.modules, {'scripts.check_water_natasha': None}):
            status, metrics = qc.check_water_nausea()
            assert status == 'FAIL'
    
    def test_water_calculation_returns_none(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch("scripts.check_water_natasha.calculate_metrics_from_text", return_value=None):
            status, metrics = qc.check_water_nausea()
            assert status == 'FAIL'

    def test_water_exception(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch("scripts.check_water_natasha.calculate_metrics_from_text", side_effect=Exception("Error")):
            status, metrics = qc.check_water_nausea()
            assert status == 'FAIL'

class TestQualityCheckKeywordDensityExtended:
    def test_keyword_script_missing(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        # We need to preserve original exists behavior for the markdown file
        # but fail for the script file.
        
        with patch("pathlib.Path.exists") as mock_exists:
            
            def new_exists(*args, **kwargs):
                # args[0] should be the Path instance
                if args and "check_simple_v2_md.py" in str(args[0]):
                    return False
                return True
                
            mock_exists.side_effect = new_exists
            
            status, metrics = qc.check_keyword_density()
            assert status == 'FAIL'

    def test_keyword_json_report_missing(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            
            with patch("pathlib.Path.exists") as mock_exists:
                # 1. script check (True)
                # 2. json check (False)
                mock_exists.side_effect = [True, False] 
                
                status, metrics = qc.check_keyword_density()
                assert status == 'FAIL'

    def test_keyword_json_invalid(self, mock_file, capsys):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("subprocess.run", return_value=MagicMock(returncode=0)), \
             patch("builtins.open", mock_open(read_data="invalid json")):
             
            status, metrics = qc.check_keyword_density()
            # Current logic: Invalid JSON sets WARN, but then returncode 0 overwrites it to PASS.
            assert status == 'PASS' 
            captured = capsys.readouterr()
            assert "Could not parse JSON report" in captured.out

    def test_keyword_subprocess_fail(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch("pathlib.Path.exists", return_value=True), \
             patch("subprocess.run", return_value=MagicMock(returncode=2, stdout="Error")):
             # mock open for json (must exist to reach returncode check? No)
             # Code logic:
             # run subprocess
             # check json path exists
             # ...
             # check returncode
             
             # If we want to test returncode=2 branch, JSON must ideally exist or not?
             # Code tries to read JSON first.
             # If JSON exists, it reads metrics.
             # Then checks returncode.
             
             # Let's say JSON exists
             with patch("builtins.open", mock_open(read_data="{}")):
                 status, metrics = qc.check_keyword_density()
                 assert status == 'FAIL'

class TestQualityCheckNerExtended:
    def test_ner_import_error(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch.dict(sys.modules, {'scripts.check_ner_brands': None}):
            status, findings = qc.check_ner_blacklist()
            assert status == 'WARN' # Returns WARN on import error

    def test_ner_exception(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch("scripts.check_ner_brands.check_blacklist", side_effect=Exception("Error")):
            status, findings = qc.check_ner_blacklist()
            assert status == 'WARN'

    def test_ner_print_many_findings(self, mock_file, capsys):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        findings = {
            'brands': [{'entity': f'B{i}'} for i in range(5)],
            'cities': [],
            'ai_fluff': [],
            'strict_phrases': [],
            'ner_entities': []
        }
        
        with patch("scripts.check_ner_brands.check_blacklist", return_value=findings), \
             patch("scripts.check_ner_brands.check_ner", return_value={}):
             
            qc.check_ner_blacklist()
            
        captured = capsys.readouterr()
        assert "... и ещё 2" in captured.out

class TestQualityCheckCommercialExtended:
    def test_commercial_fail(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch("scripts.seo_utils.check_commercial_markers") as mock_check:
            mock_check.return_value = {
                'passed': False,
                'found_count': 0,
                'found_markers': [],
                'message': 'Fail'
            }
            status, result = qc.check_commercial_markers()
            assert status == 'FAIL'

    def test_commercial_exception(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch("scripts.seo_utils.check_commercial_markers", side_effect=Exception("Error")):
            status, result = qc.check_commercial_markers()
            assert status == 'FAIL'

class TestQualityCheckSeoStructureExtended:
    def test_seo_structure_fail(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch("scripts.check_seo_structure.check_seo_structure") as mock_check:
            mock_check.return_value = ('FAIL', {
                'intro': {'passed': False, 'message': 'Bad intro'},
                'h2': {'passed': False, 'message': 'Bad h2', 'h2_with_keyword': [], 'h2_without_keyword': []},
                'frequency': {'status': 'BAD', 'message': 'Bad freq', 'is_spam': False}
            })
            
            status, result = qc.check_seo_structure()
            assert status == 'FAIL'

    def test_seo_structure_exception(self, mock_file):
        qc = QualityCheck(str(mock_file), "keyword", "B")
        
        with patch("scripts.check_seo_structure.check_seo_structure", side_effect=Exception("Error")):
            status, result = qc.check_seo_structure()
            assert status == 'FAIL'
