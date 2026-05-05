"""Audit utilities for SEO Ultimate."""

from llm_keywords_pipeline.audit.cannibalization import (
    find_full_duplicates,
    find_partial_intersections,
    load_keywords,
)
from llm_keywords_pipeline.audit.coverage import audit_category_coverage
from llm_keywords_pipeline.audit.h1 import audit_all as audit_h1_all
from llm_keywords_pipeline.audit.h1 import audit_category as audit_h1_category
from llm_keywords_pipeline.audit.h1 import validate_h1
from llm_keywords_pipeline.audit.h1_sync import check_sync as check_h1_sync
from llm_keywords_pipeline.audit.keyword_consistency import scan_actual_keywords
from llm_keywords_pipeline.audit.meta import audit_all as audit_meta_all
from llm_keywords_pipeline.audit.meta import audit_meta_file
from llm_keywords_pipeline.audit.ner_brands import analyze_file as analyze_ner
from llm_keywords_pipeline.audit.ner_brands import check_blacklist
from llm_keywords_pipeline.audit.semantic import analyze_ru_coverage, analyze_uk_coverage
from llm_keywords_pipeline.audit.synonyms import audit_category as audit_synonyms
from llm_keywords_pipeline.audit.unused import load_used_keywords
from llm_keywords_pipeline.audit.water import calculate_metrics_from_text, check_water

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
