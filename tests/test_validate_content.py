from scripts.validate_content import (
    check_length,
    check_primary_keyword,
    check_structure,
    extract_h1,
    extract_intro,
)


class TestExtract:
    def test_extract_h1(self):
        text = "# My Title\nText"
        assert extract_h1(text) == "My Title"
        
    def test_extract_h1_none(self):
        text = "No h1"
        assert extract_h1(text) is None
        
    def test_extract_intro(self):
        text = "# Title\n\nIntro line 1.\nIntro line 2.\n\n## H2"
        intro = extract_intro(text)
        assert "Intro line 1." in intro
        assert "Intro line 2." in intro
        assert "## H2" not in intro

class TestCheckStructure:
    def test_valid_structure(self):
        # Intro needs >= 30 words
        intro_text = "word " * 35
        text = f"# H1 Heading\n\n{intro_text}\n\n## H2 Heading"
        result = check_structure(text)
        assert result["h1"]["passed"]
        assert result["intro"]["passed"]
        assert result["h2_count"]["passed"]
        assert result["overall"] == "PASS"

    def test_missing_h1(self):
        text = "No H1 heading here.\n\n## H2"
        result = check_structure(text)
        assert not result["h1"]["passed"]
        assert result["overall"] == "FAIL"
        
    def test_short_intro(self):
        text = "# H1\n\nShort intro.\n\n## H2"
        result = check_structure(text)
        assert not result["intro"]["passed"] # < 30 words
        assert result["overall"] == "FAIL"
        
    def test_missing_h2(self):
        intro_text = "word " * 35
        text = f"# H1\n\n{intro_text}"
        result = check_structure(text)
        assert not result["h2_count"]["passed"]
        assert result["overall"] == "FAIL"

class TestCheckPrimaryKeyword:
    def test_valid_placement(self):
        text = "# Купить Активная пена\n\nАктивная пена — это круто."
        kw = "активная пена"
        result = check_primary_keyword(text, kw)
        assert result["in_h1"]["passed"]
        assert result["in_intro"]["passed"]
        assert result["overall"] == "PASS"

    def test_missing_in_h1(self):
        text = "# Просто пена\n\nАктивная пена работает."
        kw = "активная пена"
        result = check_primary_keyword(text, kw)
        assert not result["in_h1"]["passed"]
        assert result["overall"] == "FAIL"
        
    def test_missing_in_intro(self):
        text = "# Активная пена\n\nОбычная вода работает."
        kw = "активная пена"
        result = check_primary_keyword(text, kw)
        assert not result["in_intro"]["passed"]
        assert result["overall"] == "FAIL"

class TestCheckLength:
    def test_length_status_ok(self):
        text = "word " * 200 # within 150-600
        result = check_length(text)
        assert result["status"] == "OK"

    def test_length_status_short(self):
        text = "word " * 10
        result = check_length(text)
        assert result["status"] == "WARNING_SHORT"
