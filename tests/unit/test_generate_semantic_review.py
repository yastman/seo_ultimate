"""Tests for generate_semantic_review.py"""


class TestGenerateSemanticReview:
    """Test semantic review generation."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.generate_semantic_review

        assert scripts.generate_semantic_review is not None

    def test_module_path_accessible(self):
        """Script module should be accessible via path."""
        from pathlib import Path

        script_path = Path(__file__).parent.parent.parent / "scripts" / "generate_semantic_review.py"
        assert script_path.exists()
