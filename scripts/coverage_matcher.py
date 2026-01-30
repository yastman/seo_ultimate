"""
coverage_matcher.py — Keyword Coverage Matching with Detailed Diagnostics

Статусы COVERED: EXACT → NORM → LEMMA → SYNONYM
Статусы NOT COVERED: TOKENIZATION → PARTIAL → ABSENT
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Literal

from scripts.keyword_utils import MorphAnalyzer


def normalize_text(text: str) -> str:
    """
    Normalize text for NORM-matching:
    - casefold (unicode-aware lowercase)
    - NFKC normalization
    - Unify apostrophes: ʼ ' ʹ ′ ` → '
    - ё → е (for RU)
    - Preserve hyphens and digits (for TOKENIZATION diagnostics)
    """
    text = text.casefold()
    text = unicodedata.normalize("NFKC", text)

    # Unify apostrophes
    for a in "ʼ'ʹ′`":
        text = text.replace(a, "'")

    # ё → е
    text = text.replace("ё", "е")

    return text


MatchStatus = Literal[
    "EXACT",
    "NORM",
    "LEMMA",
    "SYNONYM",  # covered
    "TOKENIZATION",
    "PARTIAL",
    "ABSENT",  # not covered
]


# Patterns for tokens that may cause matching issues
TOKENIZATION_PATTERNS = [
    r"pH[-\s]?\d*",  # pH, pH-7, pH 7, pH-нейтральний
    r"\d+:\d+",  # 1:10, 1:50 (ratios)
    r"\d+-\d+",  # 5-10, 100-150 (ranges)
    r"[a-zA-Z]+-[a-zA-Z]+",  # wash-and-wax, pre-wash (латиница с дефисом)
    r"\d+-[a-zA-Zа-яіїєґА-ЯІЇЄҐ]+",  # 2-компонентний
    r"[a-zA-Zа-яіїєґА-ЯІЇЄҐ]+-\d+",  # ISO-9001
    r"RTU",  # Ready-To-Use
    r"\d+\s*(мл|л|г|бар|bar)",  # 100 мл, 150 бар
]


def has_tokenization_markers(keyword: str) -> bool:
    """Check if keyword contains tokens that may cause matching issues."""
    for pattern in TOKENIZATION_PATTERNS:
        if re.search(pattern, keyword, re.IGNORECASE):
            return True
    return False


@dataclass
class MatchResult:
    """Result of keyword matching with diagnostic details."""

    status: MatchStatus
    covered: bool
    # For SYNONYM
    covered_by: str | None = None
    syn_match_method: Literal["EXACT", "NORM", "LEMMA"] | None = None
    # For PARTIAL
    lemma_coverage: float | None = None
    # For NOT COVERED
    reason: str | None = None


@dataclass
class PreparedText:
    """Pre-computed text data for efficient matching across many keywords."""

    raw: str
    lang: str
    norm: str = field(init=False)
    lemmas: list[str] = field(init=False)
    lemmas_set: set[str] = field(init=False)

    def __post_init__(self):
        self.norm = normalize_text(self.raw)
        morph = MorphAnalyzer(self.lang)
        self.lemmas = morph.normalize_phrase(self.raw)
        self.lemmas_set = set(self.lemmas)


def _exact_match(keyword: str, prepared: PreparedText) -> bool:
    """Check exact substring match (case-sensitive)."""
    return keyword in prepared.raw


def _normalized_match(keyword: str, prepared: PreparedText) -> bool:
    """Check match after normalization."""
    return normalize_text(keyword) in prepared.norm


def _lemma_match(keyword: str, prepared: PreparedText, morph: MorphAnalyzer) -> bool:
    """Check match using pre-computed lemmas."""
    kw_lemmas = morph.normalize_phrase(keyword)
    if not kw_lemmas:
        return False

    # All lemmas must be present
    if not set(kw_lemmas).issubset(prepared.lemmas_set):
        return False

    # For single-word: just presence is enough
    if len(kw_lemmas) == 1:
        return True

    # For multi-word: check sequence with gap
    max_gap = 2
    for start_idx, lemma in enumerate(prepared.lemmas):
        if lemma == kw_lemmas[0]:
            if _match_sequence(kw_lemmas[1:], prepared.lemmas[start_idx + 1 :], max_gap):
                return True

    return False


def _match_sequence(remaining: list[str], text_lemmas: list[str], max_gap: int) -> bool:
    """Match remaining lemmas with gap tolerance."""
    if not remaining:
        return True

    target = remaining[0]
    for i, lemma in enumerate(text_lemmas[: max_gap + 1]):
        if lemma == target:
            return _match_sequence(remaining[1:], text_lemmas[i + 1 :], max_gap)

    return False


def _calculate_lemma_coverage(keyword: str, prepared: PreparedText, morph: MorphAnalyzer) -> float:
    """Calculate what fraction of keyword lemmas are present in text."""
    kw_lemmas = morph.normalize_phrase(keyword)
    if not kw_lemmas:
        return 0.0

    found = sum(1 for lemma in kw_lemmas if lemma in prepared.lemmas_set)
    return found / len(kw_lemmas)


def check_keyword(
    keyword: str,
    prepared: PreparedText,
    synonyms: list[dict],
) -> MatchResult:
    """
    Check if keyword is covered in text with detailed diagnostics.

    Args:
        keyword: Target keyword to find
        prepared: Pre-computed text data (use PreparedText class)
        synonyms: List of synonym dicts with 'keyword' and 'variant_of' fields

    Returns:
        MatchResult with status and diagnostic details
    """
    morph = MorphAnalyzer(prepared.lang)

    # === COVERED checks ===

    # 1. EXACT
    if _exact_match(keyword, prepared):
        return MatchResult(status="EXACT", covered=True)

    # 2. NORM
    if _normalized_match(keyword, prepared):
        return MatchResult(status="NORM", covered=True)

    # 3. LEMMA
    if _lemma_match(keyword, prepared, morph):
        return MatchResult(status="LEMMA", covered=True)

    # 4. SYNONYM — case-insensitive variant_of comparison
    kw_norm = normalize_text(keyword)
    for syn in synonyms:
        variant_of = syn.get("variant_of", "")
        if normalize_text(variant_of) == kw_norm:
            syn_kw = syn["keyword"]

            if _exact_match(syn_kw, prepared):
                return MatchResult(status="SYNONYM", covered=True, covered_by=syn_kw, syn_match_method="EXACT")
            if _normalized_match(syn_kw, prepared):
                return MatchResult(status="SYNONYM", covered=True, covered_by=syn_kw, syn_match_method="NORM")
            if _lemma_match(syn_kw, prepared, morph):
                return MatchResult(status="SYNONYM", covered=True, covered_by=syn_kw, syn_match_method="LEMMA")

    # === NOT COVERED — diagnose reason ===

    # 5. TOKENIZATION
    if has_tokenization_markers(keyword):
        return MatchResult(status="TOKENIZATION", covered=False, reason="Contains special tokens")

    # 6. PARTIAL
    lemma_cov = _calculate_lemma_coverage(keyword, prepared, morph)
    if lemma_cov >= 0.5:
        return MatchResult(
            status="PARTIAL", covered=False, lemma_coverage=lemma_cov, reason=f"{int(lemma_cov * 100)}% lemmas found"
        )

    # 7. ABSENT
    return MatchResult(status="ABSENT", covered=False)


def audit_category(
    keywords: list[dict],
    synonyms: list[dict],
    text: str,
    lang: str = "uk",
) -> dict:
    """
    Audit keyword coverage for a category.

    Uses PreparedText for efficient matching across all keywords.

    Args:
        keywords: List of {"keyword": str, "volume": int}
        synonyms: List of {"keyword": str, "variant_of": str, ...}
        text: Content text
        lang: Language code

    Returns:
        {
            "total": int,
            "covered": int,
            "coverage_percent": float,
            "results": [...]
        }
    """
    # Pre-compute text data ONCE for all keywords
    prepared = PreparedText(text, lang)

    results = []
    for kw_data in keywords:
        kw = kw_data["keyword"]
        volume = kw_data.get("volume", 0)

        match = check_keyword(kw, prepared, synonyms)

        results.append(
            {
                "keyword": kw,
                "volume": volume,
                "status": match.status,
                "covered": match.covered,
                "covered_by": match.covered_by,
                "syn_match_method": match.syn_match_method,
                "lemma_coverage": match.lemma_coverage,
                "reason": match.reason,
            }
        )

    total = len(keywords)
    covered = sum(1 for r in results if r["covered"])
    coverage_percent = (covered / total * 100) if total > 0 else 100.0

    return {
        "total": total,
        "covered": covered,
        "coverage_percent": round(coverage_percent, 1),
        "results": results,
    }
