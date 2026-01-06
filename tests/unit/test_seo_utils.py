import pytest

from scripts.seo_utils import (
    clean_markdown,
    count_words,
    get_commercial_modifiers,
    normalize_text,
    parse_front_matter,
    rebuild_document,
    slugify,
)


class TestSlugify:
    """Tests for slugify function."""

    def test_basic_cyrillic(self):
        assert slugify("Активная пена") == "aktivnaya-pena"

    def test_ukrainian_letters(self):
        assert slugify("Очищувач скла") == "ochishchuvach-skla"

    def test_special_chars_removal(self):
        assert slugify("Товар №1 (новый)") == "tovar-1-novyy"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_only_spaces(self):
        assert slugify("   ") == ""

    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("Купить воск", "kupit-vosk"),
            ("L'oreal Paris", "l-oreal-paris"),
            ("100% результат", "100-rezultat"),
            ("Киев/Украина", "kiev-ukraina"),
            ("mixed 123 text", "mixed-123-text"),
        ],
    )
    def test_edge_cases(self, input_text, expected):
        assert slugify(input_text) == expected


class TestCleanMarkdown:
    """Tests for clean_markdown function."""

    def test_remove_headers(self):
        assert clean_markdown("# Title\nText") == "Title Text"
        assert clean_markdown("## Subtitle") == "Subtitle"

    def test_remove_bold_italic(self):
        text = "Some **bold** and *italic* text"
        cleaned = clean_markdown(text)
        assert "**" not in cleaned
        assert "*" not in cleaned
        assert "bold" in cleaned

    def test_remove_links(self):
        text = "[Link](http://example.com)"
        cleaned = clean_markdown(text)
        assert "http" not in cleaned
        assert "Link" in cleaned

    def test_remove_lists(self):
        text = "- Item 1\n* Item 2\n1. Item 3"
        cleaned = clean_markdown(text)
        assert "Item 1 Item 2 Item 3" in cleaned

    def test_empty(self):
        assert clean_markdown("") == ""


class TestNormalizeText:
    def test_lowercase_preserved(self):
        # normalize_text does NOT lowercase by default based on previous expectation
        assert "TeSt" in normalize_text("TeSt")

    def test_strip_and_spaces(self):
        assert normalize_text("  test   text  ") == "test text"

    def test_remove_punctuation(self):
        text = "Hello, world! It's me."
        normalized = normalize_text(text)
        assert "," not in normalized
        assert "!" not in normalized
        assert "Hello world It's me" in normalized


class TestCountWords:
    """Tests for count_words function."""

    def test_basic_count(self):
        assert count_words("one two three") == 3

    def test_with_punctuation(self):
        assert count_words("one, two. three!") == 3

    def test_empty(self):
        assert count_words("") == 0
        assert count_words("   ") == 0

    def test_with_numbers(self):
        assert count_words("item 1 and 2") == 4


class TestFrontMatter:
    """Tests for front matter parsing."""

    def test_parse_valid_front_matter(self):
        content = """---
title: Test
---
Body content"""
        meta, yaml_raw, body = parse_front_matter(content)
        assert meta["title"] == "Test"
        assert "title: Test" in yaml_raw
        assert "Body content" in body.strip()

    def test_no_front_matter(self):
        content = "Just text"
        meta, yaml_raw, body = parse_front_matter(content)
        assert meta is None
        assert yaml_raw == ""
        assert body == "Just text"

    def test_rebuild_document(self):
        yaml_text = "---\ntitle: Rebuild\n---"
        body = "Content"
        doc = rebuild_document(yaml_text, body)
        assert doc.startswith("---")
        assert "title: Rebuild" in doc
        assert "Content" in doc


class TestCommercialModifiers:
    """Tests for commercial modifiers configuration."""

    def test_get_ru_modifiers(self):
        mods = get_commercial_modifiers("ru")
        assert "купить" in mods
        assert "цена" in mods

    def test_get_uk_modifiers(self):
        mods = get_commercial_modifiers("uk")
        assert "купити" in mods
        assert "ціна" in mods


class TestJsonUtils:
    """Tests for JSON load/save utilities."""

    def test_save_and_load_json(self, tmp_path):
        from scripts.seo_utils import load_json, save_json

        data = {"key": "value", "list": [1, 2, 3]}
        file_path = tmp_path / "test.json"

        # Test Save
        save_json(data, file_path)
        assert file_path.exists()

        # Test Load
        loaded = load_json(file_path)
        assert loaded == data

    def test_load_nonexistent_json(self, tmp_path):
        from scripts.seo_utils import load_json

        # Should return empty dict and print error (suppressed here)
        result = load_json(tmp_path / "nonexistent.json")
        assert result == {}
