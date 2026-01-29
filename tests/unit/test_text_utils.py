# tests/unit/test_text_utils.py
"""Tests for text_utils.py — SSOT for text processing."""


def test_get_stopwords_ru_returns_frozenset():
    """get_stopwords('ru') returns frozenset with Russian stopwords."""
    from scripts.text_utils import get_stopwords

    stopwords = get_stopwords("ru")
    assert isinstance(stopwords, frozenset)
    assert "и" in stopwords
    assert "в" in stopwords
    assert len(stopwords) >= 50


def test_get_stopwords_uk_returns_frozenset():
    """get_stopwords('uk') returns frozenset with Ukrainian stopwords."""
    from scripts.text_utils import get_stopwords

    stopwords = get_stopwords("uk")
    assert isinstance(stopwords, frozenset)
    assert "і" in stopwords
    assert "та" in stopwords
    assert len(stopwords) >= 50


def test_clean_markdown_removes_yaml_front_matter():
    """clean_markdown removes YAML front matter."""
    from scripts.text_utils import clean_markdown

    text = """---
title: Test
---

# Hello World
"""
    result = clean_markdown(text)
    assert "title" not in result
    assert "Hello World" in result


def test_clean_markdown_removes_headers_markup():
    """clean_markdown removes header markers but keeps text."""
    from scripts.text_utils import clean_markdown

    text = "# Header 1\n## Header 2\nSome text"
    result = clean_markdown(text)
    assert "#" not in result
    assert "Header 1" in result
    assert "Header 2" in result


def test_clean_markdown_removes_bold_italic():
    """clean_markdown removes bold/italic markers."""
    from scripts.text_utils import clean_markdown

    text = "**bold** and *italic* text"
    result = clean_markdown(text)
    assert "**" not in result
    assert "*" not in result
    assert "bold" in result
    assert "italic" in result


def test_clean_markdown_removes_links():
    """clean_markdown removes link syntax but keeps text."""
    from scripts.text_utils import clean_markdown

    text = "Click [here](https://example.com) for more"
    result = clean_markdown(text)
    assert "[" not in result
    assert "](" not in result
    assert "here" in result


def test_extract_h1_returns_heading():
    """extract_h1 returns H1 text without markup."""
    from scripts.text_utils import extract_h1

    text = "# Main Title\n\nSome content"
    result = extract_h1(text)
    assert result == "Main Title"


def test_extract_h1_returns_none_if_missing():
    """extract_h1 returns None if no H1."""
    from scripts.text_utils import extract_h1

    text = "## Only H2\n\nSome content"
    result = extract_h1(text)
    assert result is None


def test_extract_h2s_returns_list():
    """extract_h2s returns list of H2 headings."""
    from scripts.text_utils import extract_h2s

    text = "# Title\n## First\nText\n## Second\nMore text"
    result = extract_h2s(text)
    assert result == ["First", "Second"]


def test_extract_h2s_returns_empty_if_none():
    """extract_h2s returns empty list if no H2s."""
    from scripts.text_utils import extract_h2s

    text = "# Title\nNo H2 here"
    result = extract_h2s(text)
    assert result == []


def test_extract_intro_returns_first_paragraph():
    """extract_intro returns first paragraph after H1."""
    from scripts.text_utils import extract_intro

    text = "# Title\n\nThis is the intro paragraph.\n\n## Section"
    result = extract_intro(text)
    assert "This is the intro paragraph" in result


def test_extract_intro_max_lines():
    """extract_intro respects max_lines parameter."""
    from scripts.text_utils import extract_intro

    text = "# Title\n\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\n\n## Section"
    result = extract_intro(text, max_lines=3)
    assert "Line 1" in result
    assert "Line 3" in result
    assert "Line 6" not in result


def test_count_words_basic():
    """count_words returns word count."""
    from scripts.text_utils import count_words

    assert count_words("one two three") == 3
    assert count_words("  spaces  around  ") == 2


def test_count_words_empty():
    """count_words returns 0 for empty text."""
    from scripts.text_utils import count_words

    assert count_words("") == 0
    assert count_words("   ") == 0


def test_count_chars_no_spaces():
    """count_chars_no_spaces excludes whitespace."""
    from scripts.text_utils import count_chars_no_spaces

    assert count_chars_no_spaces("hello world") == 10  # no space
    assert count_chars_no_spaces("a b c") == 3


def test_tokenize_basic():
    """tokenize splits text into lowercase words."""
    from scripts.text_utils import tokenize

    result = tokenize("Hello World", lang="ru", remove_stopwords=False)
    assert result == ["hello", "world"]


def test_tokenize_removes_stopwords():
    """tokenize removes stopwords when requested."""
    from scripts.text_utils import tokenize

    result = tokenize("это и то", lang="ru", remove_stopwords=True)
    # "это", "и", "то" are all stopwords
    assert result == []


def test_tokenize_keeps_content_words():
    """tokenize keeps content words after stopword removal."""
    from scripts.text_utils import tokenize

    result = tokenize("купить активную пену для авто", lang="ru", remove_stopwords=True)
    assert "купить" in result
    assert "активную" in result
    assert "пену" in result
    # "для" should be removed as stopword
    assert "для" not in result
