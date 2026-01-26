"""Tests for uk_seed_from_ru.py"""


class TestUkSeedFromRu:
    """Test UK seed from RU."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.uk_seed_from_ru

        assert scripts.uk_seed_from_ru is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "uk_seed_from_ru.py"
        assert script_path.exists()
