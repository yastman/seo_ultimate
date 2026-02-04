"""Audit utilities for SEO Ultimate."""

from seo_ultimate.audit.cannibalization import (
    find_full_duplicates,
    find_partial_intersections,
    load_keywords,
)
from seo_ultimate.audit.coverage import audit_category_coverage
from seo_ultimate.audit.h1 import audit_all as audit_h1_all
from seo_ultimate.audit.h1 import audit_category as audit_h1_category
from seo_ultimate.audit.h1 import validate_h1
from seo_ultimate.audit.h1_sync import check_sync as check_h1_sync
from seo_ultimate.audit.keyword_consistency import scan_actual_keywords
from seo_ultimate.audit.meta import audit_all as audit_meta_all
from seo_ultimate.audit.meta import audit_meta_file
from seo_ultimate.audit.ner_brands import analyze_file as analyze_ner
from seo_ultimate.audit.ner_brands import check_blacklist
from seo_ultimate.audit.semantic import analyze_ru_coverage, analyze_uk_coverage
from seo_ultimate.audit.synonyms import audit_category as audit_synonyms
from seo_ultimate.audit.unused import load_used_keywords
from seo_ultimate.audit.water import calculate_metrics_from_text, check_water

__all__ = [
    # Coverage
    "audit_category_coverage",
    # H1
    "audit_h1_all",
    "audit_h1_category",
    "validate_h1",
    "check_h1_sync",
    # Meta
    "audit_meta_all",
    "audit_meta_file",
    # Keywords
    "scan_actual_keywords",
    "load_used_keywords",
    "audit_synonyms",
    # Cannibalization
    "load_keywords",
    "find_full_duplicates",
    "find_partial_intersections",
    # NER
    "analyze_ner",
    "check_blacklist",
    # Semantic
    "analyze_ru_coverage",
    "analyze_uk_coverage",
    # Water/Nausea
    "calculate_metrics_from_text",
    "check_water",
]
