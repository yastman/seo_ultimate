"""Tests for analyze_keywords_synonyms.py"""


class TestAnalyzeKeywordsSynonyms:
    """Test keywords synonyms analysis."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.analyze_keywords_synonyms

        assert scripts.analyze_keywords_synonyms is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "analyze_keywords_synonyms.py"
        assert script_path.exists()
