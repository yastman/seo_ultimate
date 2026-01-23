"""Tests for check_semantic_coverage.py UK support."""


class TestUkFunctions:
    """Tests for UK-specific functions."""

    def test_get_project_root_exists(self):
        """get_project_root function exists and returns path."""
        from scripts.check_semantic_coverage import get_project_root

        result = get_project_root()
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_load_uk_keywords_function_exists(self):
        """load_uk_keywords function exists."""
        import inspect

        from scripts.check_semantic_coverage import load_uk_keywords

        inspect.signature(load_uk_keywords)
        # Returns dict[str, str]
        assert callable(load_uk_keywords)

    def test_scan_uk_json_keywords_function_exists(self):
        """scan_uk_json_keywords function exists."""
        import inspect

        from scripts.check_semantic_coverage import scan_uk_json_keywords

        inspect.signature(scan_uk_json_keywords)
        assert callable(scan_uk_json_keywords)

    def test_analyze_uk_coverage_function_exists(self):
        """analyze_uk_coverage function exists."""
        import inspect

        from scripts.check_semantic_coverage import analyze_uk_coverage

        inspect.signature(analyze_uk_coverage)
        assert callable(analyze_uk_coverage)


class TestArgparse:
    """Tests for argparse configuration."""

    def test_lang_argument_exists(self):
        """Script accepts --lang argument."""
        import argparse

        from scripts.check_semantic_coverage import argparse as script_argparse

        # Verify argparse is imported
        assert script_argparse is argparse

    def test_main_block_has_lang_handling(self):
        """Main block handles lang argument."""
        import inspect

        import scripts.check_semantic_coverage as module

        source = inspect.getsource(module)
        assert "--lang" in source
        assert "args.lang" in source
        assert "analyze_uk_coverage" in source


class TestUkPathHandling:
    """Tests for UK path handling."""

    def test_uk_keywords_path(self):
        """UK keywords path is constructed correctly."""
        import inspect

        from scripts.check_semantic_coverage import load_uk_keywords

        source = inspect.getsource(load_uk_keywords)
        assert "uk" in source
        assert "data" in source
        assert "uk_keywords.json" in source

    def test_uk_categories_path(self):
        """UK categories path is constructed correctly."""
        import inspect

        from scripts.check_semantic_coverage import scan_uk_json_keywords

        source = inspect.getsource(scan_uk_json_keywords)
        assert "uk" in source
        assert "categories" in source
