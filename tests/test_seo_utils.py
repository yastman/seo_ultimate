"""
Tests for seo_utils.py — Unified SEO utilities

Tests cover:
1. YAML front matter parsing
2. Text normalization and counting
3. Keyword occurrence counting
4. Sentence splitting
5. Protected zones detection
6. Tier requirements
7. URL validation functions
"""

import sys
from pathlib import Path

import pytest


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from seo_utils import (
    DEFAULT_BLACKLIST_DOMAINS,
    count_chars_no_spaces,
    count_keyword_occurrences,
    count_words,
    fix_ua_in_url,
    get_protected_zones,
    get_tier_requirements,
    is_blacklisted_domain,
    is_category_page,
    is_in_protected_zone,
    is_protected_section,
    normalize_text,
    parse_front_matter,
    rebuild_document,
    safe_sentence_split,
)


class TestParseFrontMatter:
    """Test YAML front matter parsing"""

    def test_parse_valid_front_matter(self):
        """Should parse valid YAML front matter"""
        content = """---
title: Test Article
tier: B
keywords:
  - активная пена
  - мойка авто
---

# Article Content

This is the body text.
"""
        metadata, yaml_text, body = parse_front_matter(content)

        assert metadata is not None
        assert metadata["title"] == "Test Article"
        assert metadata["tier"] == "B"
        assert len(metadata["keywords"]) == 2
        assert "---" in yaml_text
        assert "# Article Content" in body

    def test_parse_no_front_matter(self):
        """Should handle content without front matter"""
        content = """# Just a Header

Regular markdown content without YAML.
"""
        metadata, yaml_text, body = parse_front_matter(content)

        assert metadata is None
        assert yaml_text == ""
        assert "# Just a Header" in body

    def test_parse_invalid_yaml(self):
        """Should handle invalid YAML gracefully"""
        content = """---
invalid: yaml: syntax: here
  - broken
---

Body content.
"""
        metadata, yaml_text, body = parse_front_matter(content)

        # Should return None for invalid YAML but still separate body
        assert metadata is None
        assert "Body content" in body

    def test_windows_line_endings(self):
        """Should handle Windows CRLF line endings"""
        content = "---\r\ntitle: Test\r\n---\r\n\r\nBody text."
        metadata, yaml_text, body = parse_front_matter(content)

        assert metadata is not None
        assert metadata["title"] == "Test"


class TestRebuildDocument:
    """Test document rebuilding"""

    def test_rebuild_with_yaml(self):
        """Should rebuild document with YAML"""
        yaml_text = "---\ntitle: Test\n---\n"
        body_text = "# Content\n\nBody here."

        result = rebuild_document(yaml_text, body_text)

        assert result.startswith("---")
        assert "title: Test" in result
        assert "# Content" in result

    def test_rebuild_without_yaml(self):
        """Should rebuild document without YAML"""
        result = rebuild_document("", "# Just content")

        assert result == "# Just content"
        assert "---" not in result


class TestNormalizeText:
    """Test text normalization for word counting"""

    def test_remove_code_blocks(self):
        """Should remove code blocks"""
        md = """Text before

```python
def foo():
    pass
```

Text after"""
        result = normalize_text(md)

        assert "def foo" not in result
        assert "Text before" in result
        assert "Text after" in result

    def test_remove_inline_code(self):
        """Should remove inline code"""
        md = "Use the `print()` function to output."
        result = normalize_text(md)

        assert "`print()`" not in result
        assert "Use the" in result

    def test_extract_link_text(self):
        """Should extract text from markdown links"""
        md = "Visit [our site](https://example.com) for more."
        result = normalize_text(md)

        assert "our site" in result
        assert "https://example.com" not in result

    def test_remove_headers(self):
        """Should remove header markers"""
        md = "# Header 1\n## Header 2\n### Header 3"
        result = normalize_text(md)

        assert result.strip().startswith("Header")
        assert "#" not in result

    def test_remove_tables(self):
        """Should remove or reduce table syntax"""
        md = "| Col1 | Col2 |\n|------|------|\n| A | B |"
        result = normalize_text(md)

        # Table content should be simplified (pipes reduced or removed)
        # At minimum, the content should be preserved
        assert result.count("|") < md.count("|")  # Pipes reduced

    def test_remove_bold_italic(self):
        """Should remove bold/italic markers"""
        md = "This is **bold** and *italic* and __also bold__."
        result = normalize_text(md)

        assert "bold" in result
        assert "**" not in result
        assert "*" not in result


class TestCountWords:
    """Test word counting"""

    def test_count_simple_text(self):
        """Should count words in simple text"""
        text = "This is a simple test with seven words"
        assert count_words(text) == 8

    def test_count_cyrillic_words(self):
        """Should count Cyrillic words"""
        text = "Это тест на русском языке"
        assert count_words(text) == 5

    def test_count_empty_string(self):
        """Should return 0 for empty string"""
        assert count_words("") == 0
        assert count_words("   ") == 0


class TestCountCharsNoSpaces:
    """Test character counting without spaces"""

    def test_count_simple(self):
        """Should count characters excluding spaces"""
        text = "Hello World"  # 10 chars without space
        assert count_chars_no_spaces(text) == 10

    def test_count_with_newlines(self):
        """Should exclude newlines and tabs"""
        text = "Hello\nWorld\tTest"  # 14 chars
        assert count_chars_no_spaces(text) == 14

    def test_count_cyrillic(self):
        """Should count Cyrillic characters"""
        text = "Привет мир"  # 9 chars without space
        assert count_chars_no_spaces(text) == 9

    def test_count_markdown(self):
        """Should count markdown characters"""
        text = "# Header\n\n**Bold**"
        result = count_chars_no_spaces(text)
        # Includes #, *, etc.
        assert result > 0


class TestCountKeywordOccurrences:
    """Test keyword counting with variations"""

    def test_count_exact_matches(self):
        """Should count exact keyword matches"""
        text = "активная пена очищает. активная пена безопасна."
        variations = {"exact": ["активная пена"], "partial": []}

        exact, partial = count_keyword_occurrences(text, "активная пена", variations)

        assert exact == 2
        assert partial == 0

    def test_count_partial_matches(self):
        """Should count partial variations"""
        text = "активной пены достаточно. с активной пеной легко."
        variations = {"exact": ["активная пена"], "partial": ["активной пены", "активной пеной"]}

        exact, partial = count_keyword_occurrences(text, "активная пена", variations)

        assert exact == 0
        assert partial == 2

    def test_fallback_to_keyword(self):
        """Should use keyword as fallback when variations empty"""
        text = "test keyword appears test keyword again"
        variations = {"exact": [], "partial": []}

        exact, partial = count_keyword_occurrences(text, "test keyword", variations)

        # Should fallback to using "test keyword" as exact form
        assert exact == 2

    def test_case_insensitive(self):
        """Should match case-insensitively"""
        text = "АКТИВНАЯ ПЕНА и активная пена и Активная Пена"
        variations = {"exact": ["активная пена"], "partial": []}

        exact, partial = count_keyword_occurrences(text, "активная пена", variations)

        assert exact == 3


class TestSafeSentenceSplit:
    """Test Markdown-aware sentence splitting"""

    def test_split_simple_sentences(self):
        """Should split simple sentences"""
        text = "First sentence. Second sentence. Third one."
        sentences = safe_sentence_split(text)

        assert len(sentences) >= 3

    def test_preserve_code_blocks(self):
        """Should not split inside code blocks"""
        text = """Before code.

```python
x = 1. y = 2.
```

After code."""
        sentences = safe_sentence_split(text)

        # Code block should remain intact in one sentence
        code_found = False
        for s in sentences:
            if "```python" in s:
                code_found = True
                assert "x = 1" in s
                assert "y = 2" in s
        assert code_found

    def test_handle_questions(self):
        """Should split on question marks"""
        text = "Что это? Это тест. Правда?"
        sentences = safe_sentence_split(text)

        assert len(sentences) >= 3

    def test_handle_exclamations(self):
        """Should split on exclamation marks"""
        text = "Отлично! Это работает! Прекрасно."
        sentences = safe_sentence_split(text)

        assert len(sentences) >= 3


class TestIsProtectedSection:
    """Test protected section detection"""

    @pytest.mark.parametrize(
        "sentence",
        [
            "# Header",
            "## Subheader",
            "### FAQ Question",
            "- List item",
            "* Bullet point",
            "+ Another bullet",
            "> Quote",
            "```code",
            "1. Numbered",
            "2. Also numbered",
            "**Bold start**",
        ],
    )
    def test_protected_prefixes(self, sentence):
        """Should protect headers, lists, quotes, code, numbers, bold"""
        assert is_protected_section(sentence) is True

    def test_protect_questions(self):
        """Should protect sentences ending with ?"""
        assert is_protected_section("Как использовать?") is True
        assert is_protected_section("  What is this?") is True

    def test_regular_sentences_not_protected(self):
        """Regular sentences should not be protected"""
        assert is_protected_section("This is a regular sentence.") is False
        assert is_protected_section("Обычное предложение.") is False


class TestGetTierRequirements:
    """Test tier-based requirements (DEPRECATED - now uses adaptive approach)

    Note: get_tier_requirements() is deprecated in favor of get_adaptive_requirements()
    These tests verify the legacy wrapper returns adaptive-derived values.

    Mapping:
    - Tier A → 30 keywords (deep) → words 400-600 → chars 2400-3600
    - Tier B → 15 keywords (medium) → words 250-400 → chars 1500-2400
    - Tier C → 5 keywords (shallow) → words 150-250 → chars 900-1500
    """

    def test_tier_a_requirements(self):
        """Tier A should map to deep semantic depth (30 keywords)"""
        req = get_tier_requirements("A")

        # Words 400-600 × 6 = chars 2400-3600
        assert req["char_min"] == 2400
        assert req["char_max"] == 3600
        # Deep: h2_min=3 → h2_range=(3, 5)
        assert req["h2_range"] == (3, 5)
        # Deep: faq_range=(3, 5)
        assert req["faq_range"] == (3, 5)

    def test_tier_b_requirements(self):
        """Tier B should map to medium semantic depth (15 keywords)"""
        req = get_tier_requirements("B")

        # Words 250-400 × 6 = chars 1500-2400
        assert req["char_min"] == 1500
        assert req["char_max"] == 2400
        # Medium: h2_min=2 → h2_range=(2, 4)
        assert req["h2_range"] == (2, 4)
        # Medium: faq_range=(2, 3)
        assert req["faq_range"] == (2, 3)

    def test_tier_c_requirements(self):
        """Tier C should map to shallow semantic depth (5 keywords)"""
        req = get_tier_requirements("C")

        # Words 150-250 × 6 = chars 900-1500
        assert req["char_min"] == 900
        assert req["char_max"] == 1500
        # Shallow: h2_min=1 → h2_range=(1, 3)
        assert req["h2_range"] == (1, 3)
        # Shallow: faq_range=(0, 1)
        assert req["faq_range"] == (0, 1)

    def test_case_insensitive_tier(self):
        """Should accept lowercase tier"""
        req_upper = get_tier_requirements("B")
        req_lower = get_tier_requirements("b")

        assert req_upper == req_lower

    def test_invalid_tier_fallback(self):
        """Should fallback to B for invalid tier"""
        req = get_tier_requirements("X")
        req_b = get_tier_requirements("B")

        assert req == req_b


class TestGetProtectedZones:
    """Test protected zones detection"""

    def test_intro_zone_detection(self):
        """Should detect intro zone"""
        md = """First paragraph intro.

## First H2

Content here.
"""
        zones = get_protected_zones(md)

        assert len(zones["intro"]) > 0

    def test_h2_zones_detection(self):
        """Should detect H2 header zones"""
        md = """Intro.

## First Section

Content.

## Second Section

More content.
"""
        zones = get_protected_zones(md)

        assert len(zones["h2_sections"]) == 2

    def test_faq_zones_detection(self):
        """Should detect FAQ question zones"""
        md = """## FAQ

### Question one?

Answer one.

### Question two?

Answer two.
"""
        zones = get_protected_zones(md)

        assert len(zones["faq"]) == 2


class TestIsInProtectedZone:
    """Test position-in-zone checking"""

    def test_position_in_intro(self):
        """Should detect position in intro zone"""
        zones = {"intro": [(0, 100)], "h2_sections": [], "faq": []}

        assert is_in_protected_zone(50, zones) is True
        assert is_in_protected_zone(150, zones) is False

    def test_position_in_h2(self):
        """Should detect position in H2 zone"""
        zones = {"intro": [], "h2_sections": [(100, 200), (300, 400)], "faq": []}

        assert is_in_protected_zone(150, zones) is True
        assert is_in_protected_zone(350, zones) is True
        assert is_in_protected_zone(250, zones) is False


class TestSeoUtilsUrlFunctions:
    """Test URL functions in seo_utils (duplicated from url_filters for consistency)"""

    def test_blacklist_default(self):
        """Should have default blacklist"""
        assert len(DEFAULT_BLACKLIST_DOMAINS) > 0
        assert "rozetka.com.ua" in DEFAULT_BLACKLIST_DOMAINS

    def test_is_blacklisted(self):
        """Should detect blacklisted domains"""
        assert is_blacklisted_domain("https://rozetka.com.ua/test") is True
        assert is_blacklisted_domain("https://shop.ua/test") is False

    def test_fix_ua_url(self):
        """Should fix /ua/ in URLs"""
        url = "https://shop.com/ua/catalog"
        fixed = fix_ua_in_url(url)
        assert "/ua/" not in fixed

    def test_is_category_page_tuple_return(self):
        """seo_utils.is_category_page returns (bool, reason)"""
        result = is_category_page("https://shop.com/catalog/foam")

        assert isinstance(result, tuple)
        assert len(result) == 2
        is_cat, reason = result
        assert isinstance(is_cat, bool)
        assert isinstance(reason, str)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_content_parsing(self):
        """Should handle empty content"""
        metadata, yaml_text, body = parse_front_matter("")

        assert metadata is None
        assert body == ""

    def test_unicode_normalization(self):
        """Should handle various Unicode characters"""
        text = "Привіт! Тест — проходить..."
        result = normalize_text(text)

        assert len(result) > 0

    def test_very_long_content(self):
        """Should handle very long content"""
        text = "Word " * 10000
        result = normalize_text(text)
        words = count_words(result)

        assert words == 10000

    def test_special_characters_in_keywords(self):
        """Should handle special characters in keywords"""
        text = "pH 10-13 средство и pH-нейтральный состав"
        variations = {"exact": ["pH 10-13"], "partial": []}

        exact, _ = count_keyword_occurrences(text, "pH 10-13", variations)
        assert exact == 1
