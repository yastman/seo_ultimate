from unittest.mock import patch

from scripts.validate_content import (
    check_blacklist_phrases,
    check_content_standards,
    check_keyword_coverage,
    check_keyword_coverage_split,
    check_primary_keyword,
    check_primary_keyword_semantic,
    check_quality,
    check_structure,
    count_faq,
    extract_h1,
    extract_h2s,
    extract_intro,
    keyword_matches_semantic,
)

# ============================================================================
# Text Processing
# ============================================================================


class TestTextProcessing:
    def test_extract_h1(self):
        assert extract_h1("# Main Title") == "Main Title"
        assert extract_h1("pre\n# Title\npost") == "Title"
        assert extract_h1("No h1") is None

    def test_extract_h2s(self):
        text = "## H2 One\nText\n## H2 Two"
        assert extract_h2s(text) == ["H2 One", "H2 Two"]
        assert extract_h2s("No h2") == []

    def test_extract_intro(self):
        text = "# H1\n\nIntro line 1.\nIntro line 2.\n\n## H2"
        intro = extract_intro(text)
        assert "Intro line 1." in intro
        assert "Intro line 2." in intro
        assert "## H2" not in intro

        # Test max lines limit
        text_long = "# H1\n" + "\n".join([f"Line {i}" for i in range(10)])
        intro_long = extract_intro(text_long)
        # Check max lines limit (logic takes first 5 non-empty lines)
        assert len(intro_long.split("\n")) <= 5

    def test_count_faq(self):
        text = "**Q: Question 1**\n**В: Вопрос 2**\nText"
        assert count_faq(text) == 2


# ============================================================================
# Core Checks
# ============================================================================


class TestStructureCheck:
    def test_valid_structure(self):
        intro = "word " * 35
        text = f"# H1\n\n{intro}\n\n## H2"
        res = check_structure(text)
        assert res["overall"] == "PASS"
        assert res["h1"]["passed"]
        assert res["intro"]["passed"]
        assert res["h2_count"]["passed"]

    def test_invalid_structure(self):
        res = check_structure("Just text")
        assert res["overall"] == "FAIL"
        assert not res["h1"]["passed"]


class TestPrimaryKeyword:
    def test_exact_match(self):
        text = "# Купить автошампунь\n\nКупить автошампунь выгодно."
        kw = "автошампунь"
        res = check_primary_keyword(text, kw)
        assert res["in_h1"]["passed"]
        assert res["in_intro"]["passed"]
        assert res["overall"] == "PASS"

    def test_semantic_match_logic(self):
        # Test helper function directly
        assert keyword_matches_semantic("автошампунь", "лучший автошампуни")  # plural stem match
        assert keyword_matches_semantic("купить пену", "купите пену")  # stem match

    def test_semantic_check_function(self):
        text = "# Лучшие автошампуни\n\nМы продаем автошампуни."
        kw = "автошампунь"

        res = check_primary_keyword_semantic(text, kw)
        assert res["semantic_h1"]
        assert res["semantic_intro"]
        assert res["confidence"] >= 90
        assert res["overall"] == "PASS"


class TestCoverage:
    def test_keyword_coverage(self):
        text = "word1 word2 word3"
        keywords = ["word1", "word2", "missing"]

        # 2/3 = 66%
        # Target for 3 keywords (<=5) is 70% by default
        # Patch CoverageChecker.get_adaptive_target since that's what's used internally
        with patch("scripts.keyword_utils.CoverageChecker.get_adaptive_target", return_value=50):
            res = check_keyword_coverage(text, keywords)
            assert res["passed"]
            assert res["coverage_percent"] > 60

    def test_coverage_split_semantic(self):
        text = "купить шампунь для мойки"
        core = ["шампунь", "пена"]
        comm = ["купить"]

        # Patch adaptive target to 50% so 1/2 keywords (50%) passes
        with patch("scripts.keyword_utils.CoverageChecker.get_adaptive_target", return_value=50):
            res = check_keyword_coverage_split(text, core, comm, use_semantic=True)
            assert res["core"]["found"] == 1  # шампунь found
            assert res["commercial"]["found"] == 1  # купить found
            assert res["passed"]  # 50% >= 50% target


# ============================================================================
# Quality & Standards
# ============================================================================


class TestQualityChecks:
    @patch("scripts.validate_content.calculate_water_and_nausea")
    def test_check_quality_pass(self, mock_calc):
        mock_calc.return_value = {
            "water_percent": 50.0,
            "classic_nausea": 2.5,
            "academic_nausea": 8.0,
        }
        res = check_quality("some text")
        assert res["overall"] == "PASS"
        assert res["water"]["status"] == "OK"

    @patch("scripts.validate_content.calculate_water_and_nausea")
    def test_check_quality_fail_water(self, mock_calc):
        mock_calc.return_value = {
            "water_percent": 80.0,  # High
            "classic_nausea": 2.5,
            "academic_nausea": 8.0,
        }
        res = check_quality("some text")
        assert res["water"]["status"] == "WARNING"
        assert res["overall"] == "WARNING"


class TestBlacklist:
    @patch("scripts.validate_content.check_blacklist")
    def test_check_blacklist_blocker(self, mock_bl):
        mock_bl.return_value = {
            "strict_phrases": ["bad word"],
            "brands": [],
            "cities": [],
            "ai_fluff": [],
        }
        res = check_blacklist_phrases("text")
        assert res["overall"] == "FAIL"

    @patch("scripts.validate_content.check_blacklist")
    def test_check_blacklist_warning(self, mock_bl):
        mock_bl.return_value = {
            "strict_phrases": [],
            "brands": [],
            "cities": [],
            "ai_fluff": ["fluff"],
        }
        res = check_blacklist_phrases("text")
        assert res["overall"] == "WARNING"


class TestContentStandards:
    def test_standards_patterns(self):
        text = """
## Safety
1. Step one
2. Step two
Расход 50 мл.
Никогда не делайте это.
        """
        res = check_content_standards(text, lang="ru")
        assert res["safety_block"]
        assert res["howto_steps"]
        assert res["evergreen_math"]
        assert res["warnings_present"]

    def test_standards_missing(self):
        text = "Just plain text"
        res = check_content_standards(text, lang="ru")
        assert not res["safety_block"]
        assert not res["howto_steps"]
