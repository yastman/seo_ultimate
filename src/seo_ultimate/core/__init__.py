"""Core utilities for SEO Ultimate."""

from seo_ultimate.core.config import (
    CATEGORIES_DIR,
    COMMERCIAL_MODIFIERS,
    CONTENT_STANDARDS,
    L3_TO_SLUG,
    PROJECT_ROOT,
    QUALITY_THRESHOLDS,
    SLUG_TO_L3,
)
from seo_ultimate.core.coverage import MatchResult, PreparedText, audit_category, check_keyword
from seo_ultimate.core.keywords import (
    CoverageChecker,
    KeywordMatcher,
    MorphAnalyzer,
    keyword_matches_text,
)
from seo_ultimate.core.seo import (
    count_keyword_occurrences,
    get_adaptive_requirements,
    parse_front_matter,
)
from seo_ultimate.core.text import (
    clean_markdown,
    count_chars_no_spaces,
    count_words,
    extract_h1,
    extract_h2s,
    extract_intro,
    get_stopwords,
    tokenize,
)

__all__ = [
    # Config
    "PROJECT_ROOT",
    "CATEGORIES_DIR",
    "QUALITY_THRESHOLDS",
    "CONTENT_STANDARDS",
    "L3_TO_SLUG",
    "SLUG_TO_L3",
    "COMMERCIAL_MODIFIERS",
    # Keywords
    "KeywordMatcher",
    "CoverageChecker",
    "MorphAnalyzer",
    "keyword_matches_text",
    # Coverage
    "MatchResult",
    "PreparedText",
    "audit_category",
    "check_keyword",
    # SEO
    "parse_front_matter",
    "count_keyword_occurrences",
    "get_adaptive_requirements",
    # Text
    "get_stopwords",
    "clean_markdown",
    "count_words",
    "count_chars_no_spaces",
    "extract_h1",
    "extract_h2s",
    "extract_intro",
    "tokenize",
]
