"""Tests for build_product_map.py"""


class TestBuildProductMap:
    """Test product map building."""

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "build_product_map.py"
        assert script_path.exists()

    def test_load_sql_cats_parses_format(self, tmp_path, monkeypatch):
        """Should parse 'ID: Name' format from dump file."""
        # Create mock dump file
        dump_content = """410: Excluded
411: Автохимия
420: Детейлинг
468: Excluded Too
"""
        dump_file = tmp_path / "sql_cats_dump.txt"
        dump_file.write_text(dump_content, encoding="utf-8")

        # Monkeypatch the DUMP_FILE
        import scripts.build_product_map as bpm

        monkeypatch.setattr(bpm, "DUMP_FILE", dump_file)

        result = bpm.load_sql_cats()
        # Only 411-467 range should be included
        assert 411 in result
        assert 420 in result
        assert 410 not in result
        assert 468 not in result
        assert result[411] == "Автохимия"

    def test_load_sql_cats_skips_invalid_lines(self, tmp_path, monkeypatch):
        """Should skip lines without ': ' separator."""
        dump_content = """Invalid line
411: Valid
"""
        dump_file = tmp_path / "sql_cats_dump.txt"
        dump_file.write_text(dump_content, encoding="utf-8")

        import scripts.build_product_map as bpm

        monkeypatch.setattr(bpm, "DUMP_FILE", dump_file)

        result = bpm.load_sql_cats()
        assert len(result) == 1
        assert 411 in result
