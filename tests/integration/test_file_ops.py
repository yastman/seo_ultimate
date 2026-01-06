from scripts.seo_utils import load_json
from tests.helpers.file_builders import CategoryBuilder


def test_category_builder_creates_structure(tmp_path):
    """
    Test that CategoryBuilder correctly creates file structure.
    This acts as an integration test for our test helpers.
    """
    slug = "test-category-integration"
    builder = (
        CategoryBuilder()
        .with_slug(slug)
        .with_meta(title="Integaration Test", description="Desc", h1="H1 Header")
        .with_keywords([{"keyword": "k1", "volume": 10}])
        .with_content("# Content")
    )

    cat_dir = builder.build(tmp_path)

    # Assert directories exist
    assert cat_dir.exists()
    assert (cat_dir / "meta").exists()
    assert (cat_dir / "data").exists()
    assert (cat_dir / "content").exists()

    # Assert files exist and content is correct
    meta_file = cat_dir / "meta" / f"{slug}_meta.json"
    assert meta_file.exists()

    clean_file = cat_dir / "data" / f"{slug}_clean.json"
    assert clean_file.exists()

    content_file = cat_dir / "content" / f"{slug}_ru.md"
    assert content_file.exists()

    # Verify content using project utility
    meta_data = load_json(meta_file)
    assert meta_data["title"] == "Integaration Test"

    clean_data = load_json(clean_file)
    assert clean_data["slug"] == slug
    assert clean_data["keywords"][0]["keyword"] == "k1"
