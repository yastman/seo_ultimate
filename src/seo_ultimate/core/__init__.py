"""Core utilities for SEO Ultimate."""

from seo_ultimate.core.config import (
    CATEGORIES_DIR,
    COMMERCIAL_MODIFIERS,
    L3_TO_SLUG,
    PROJECT_ROOT,
    QUALITY_THRESHOLDS,
    SLUG_TO_L3,
)
from seo_ultimate.core.coverage import MatchResult, PreparedText, audit_category, check_keyword
from seo_ultimate.core.keywords import CoverageChecker, KeywordMatcher
from seo_ultimate.core.seo import count_keyword_occurrences, parse_front_matter
from seo_ultimate.core.text import clean_markdown, count_words, get_stopwords

__all__ = [
    # Config
    "PROJECT_ROOT",
    "CATEGORIES_DIR",
    "QUALITY_THRESHOLDS",
    "L3_TO_SLUG",
    "SLUG_TO_L3",
    "COMMERCIAL_MODIFIERS",
    # Keywords
    "KeywordMatcher",
    "CoverageChecker",
    # Coverage
    "MatchResult",
    "PreparedText",
    "audit_category",
    "check_keyword",
    # SEO
    "parse_front_matter",
    "count_keyword_occurrences",
    # Text
    "get_stopwords",
    "clean_markdown",
    "count_words",
]
