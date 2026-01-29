#!/usr/bin/env python3
"""
validate_content.py — Content Validation (Google 2025 Approach)

Валидирует контент категории по структуре и качеству.
НЕ использует жёсткие требования по объёму.

Подход:
- Структура важнее объёма
- Качество (water, nausea, blacklist)
- Coverage ключей (адаптивный)
- Primary keyword обязателен в H1 + intro

Usage:
    python3 scripts/validate_content.py <file.md> "<primary_keyword>"
    python3 scripts/validate_content.py <file.md> "<primary_keyword>" --json
    python3 scripts/validate_content.py <file.md> --with-analysis <slug>
    python3 scripts/validate_content.py <file.md> "<keyword>" --no-semantic  # exact match only
    python3 scripts/validate_content.py <file.md> "<keyword>" --mode seo     # simplified SEO mode

Exit codes:
    0 = PASS (all checks passed)
    1 = WARNING (minor issues)
    2 = FAIL (blockers found)
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

# Add scripts and project root to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

# Fix Windows encoding issues for emojis/Cyrillic
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

try:
    from check_water_natasha import calculate_metrics_from_text as calculate_water_and_nausea
except ImportError:
    calculate_water_and_nausea = None

try:
    from check_ner_brands import check_blacklist
except ImportError:
    check_blacklist = None

# SSOT: Use core functions from text_utils
try:
    from scripts.text_utils import (
        clean_markdown,
        count_chars_no_spaces,
        count_words,
        extract_h1,
        extract_h2s,
        extract_intro,
    )
except ImportError:
    from text_utils import (  # type: ignore
        clean_markdown,
        count_chars_no_spaces,
        count_words,
        extract_h1,
        extract_h2s,
        extract_intro,
    )

# SSOT: get_adaptive_requirements from seo_utils
try:
    from scripts.seo_utils import get_adaptive_requirements
except ImportError:
    from seo_utils import get_adaptive_requirements  # type: ignore

# Coverage targets (SSOT)
try:
    from scripts.config import CONTENT_STANDARDS, QUALITY_THRESHOLDS
except ImportError:
    from config import CONTENT_STANDARDS, QUALITY_THRESHOLDS  # type: ignore

# Unified keyword matching (keyword_utils)
try:
    from scripts.keyword_utils import (
        CoverageChecker,
        KeywordMatcher,
        keyword_matches_text,
    )
except ImportError:
    from keyword_utils import (  # type: ignore
        CoverageChecker,
        KeywordMatcher,
        keyword_matches_text,
    )

# Grammar check (language_tool_python)
try:
    import language_tool_python

    GRAMMAR_AVAILABLE = True
except ImportError:
    language_tool_python = None
    GRAMMAR_AVAILABLE = False

# MD-Linting (pymarkdownlnt)
try:
    from pymarkdown.api import PyMarkdownApi

    MDLINT_AVAILABLE = True
except ImportError:
    PyMarkdownApi = None
    MDLINT_AVAILABLE = False


VALIDATION_MODES = ("quality", "seo")


# =============================================================================
# Text Processing (extract_h1, extract_h2s, extract_intro imported from text_utils)
# =============================================================================


def count_faq(text: str) -> int:
    """Count FAQ questions."""
    # Look for **Q:** or **В:** patterns
    q_pattern = r"\*\*[QВ][:\.]"
    matches = re.findall(q_pattern, text)
    return len(matches)


# =============================================================================
# Validation Checks
# =============================================================================


def check_structure(text: str) -> dict:
    """
    Check content structure.

    Required:
    - H1 (one)
    - Intro (min 30 words)
    - At least 1 H2

    Optional (warnings):
    - FAQ section
    - Trust signals
    """
    results: dict[str, Any] = {
        "h1": {"passed": False, "value": None},
        "intro": {"passed": False, "words": 0},
        "h2_count": {"passed": False, "count": 0},
        "faq_count": {"info": True, "count": 0},
        "overall": "FAIL",
    }

    # H1
    h1 = extract_h1(text)
    results["h1"]["value"] = h1
    results["h1"]["passed"] = h1 is not None

    # Intro
    intro = extract_intro(text)
    intro_words = count_words(intro)
    results["intro"]["words"] = intro_words
    results["intro"]["passed"] = intro_words >= 30

    # H2s
    h2s = extract_h2s(text)
    results["h2_count"]["count"] = len(h2s)
    results["h2_count"]["passed"] = len(h2s) >= 1
    results["h2_count"]["h2s"] = h2s

    # FAQ (informational)
    faq_count = count_faq(text)
    results["faq_count"]["count"] = faq_count

    # Overall
    blockers = [
        not results["h1"]["passed"],
        not results["intro"]["passed"],
        not results["h2_count"]["passed"],
    ]

    if any(blockers):
        results["overall"] = "FAIL"
    else:
        results["overall"] = "PASS"

    return results


def check_primary_keyword(text: str, primary_keyword: str) -> dict:
    """
    Check primary keyword placement.

    BLOCKER:
    - Primary keyword in H1
    - Primary keyword in intro
    """
    results: dict[str, Any] = {
        "in_h1": {"passed": False},
        "in_intro": {"passed": False},
        "frequency": {"count": 0, "status": "OK"},
        "overall": "FAIL",
    }

    keyword_lower = primary_keyword.lower()

    # In H1
    h1 = extract_h1(text)
    if h1:
        results["in_h1"]["passed"] = keyword_lower in h1.lower()

    # In intro
    intro = extract_intro(text)
    results["in_intro"]["passed"] = keyword_lower in intro.lower()

    # Frequency (informational)
    text_lower = text.lower()
    count = text_lower.count(keyword_lower)
    results["frequency"]["count"] = count

    if count < 2:
        results["frequency"]["status"] = "LOW"
    elif count > 10:
        results["frequency"]["status"] = "HIGH"
    else:
        results["frequency"]["status"] = "OK"

    # Overall (H1 + intro = blockers)
    if results["in_h1"]["passed"] and results["in_intro"]["passed"]:
        results["overall"] = "PASS"
    else:
        results["overall"] = "FAIL"

    return results


def check_primary_keyword_semantic(text: str, primary_keyword: str, use_llm: bool = False) -> dict:
    """
    Semantic check for primary keyword using morphology-aware matching.

    Uses KeywordMatcher for proper Russian morphology instead of manual stemming.

    Instead of exact match, checks semantic equivalence:
    - "чернитель резины" ≈ "чернители шин" (singular/plural + synonym)
    - "очиститель дисков" ≈ "очистители дисков" (singular/plural)

    Args:
        text: Full content text
        primary_keyword: Target keyword
        use_llm: If True, generates prompt for external LLM check

    Returns:
        Dict with semantic analysis
    """
    h1 = extract_h1(text) or ""
    intro = extract_intro(text)

    results: dict[str, Any] = {
        "keyword": primary_keyword,
        "h1": h1,
        "intro_preview": intro[:200],
        "semantic_h1": False,
        "semantic_intro": False,
        "confidence": 0,
        "overall": "PENDING",
        "llm_prompt": None,
    }

    # Use KeywordMatcher for morphology-aware matching
    matcher = KeywordMatcher(lang="ru")

    # Check H1 semantically
    h1_matched, _ = matcher.find_in_text(primary_keyword, h1)
    results["semantic_h1"] = h1_matched

    # Check intro semantically
    intro_matched, _ = matcher.find_in_text(primary_keyword, intro)
    results["semantic_intro"] = intro_matched

    # Calculate confidence
    if results["semantic_h1"] and results["semantic_intro"]:
        results["confidence"] = 90
        results["overall"] = "PASS"
    elif results["semantic_h1"]:
        results["confidence"] = 60
        results["overall"] = "WARNING"
    else:
        results["confidence"] = 30
        results["overall"] = "FAIL"

    # Generate LLM prompt for verification
    if use_llm:
        results["llm_prompt"] = f"""Проверь семантическое покрытие ключевого слова.

KEYWORD: "{primary_keyword}"
H1: "{h1}"
INTRO: "{intro[:300]}..."

ВОПРОСЫ:
1. H1 семантически покрывает keyword? (учитывай ед/мн число, синонимы)
2. Intro содержит keyword или семантический эквивалент?

Ответь: {{"h1_ok": bool, "intro_ok": bool, "reason": "..."}}"""

    return results


def check_keyword_coverage(text: str, keywords: list[str]) -> dict:
    """
    Check keyword coverage (legacy, for backwards compatibility).

    Uses CoverageChecker with morphology-aware matching.

    Adaptive targets:
    - ≤5 keywords: 70% coverage
    - 6-15 keywords: 60% coverage
    - >15 keywords: 50% coverage

    WARNING (not blocker) if below target.
    """
    if not keywords:
        return {
            "total": 0,
            "found": 0,
            "coverage_percent": 0,
            "target": 0,
            "passed": True,
            "overall": "PASS",
            "found_keywords": [],
            "missing_keywords": [],
        }

    checker = CoverageChecker(lang="ru")
    result = checker.check(keywords, text, use_lemma=True)

    # Convert to legacy format (found_keywords as list of strings, not dicts)
    found_kw_strings = [item["keyword"] for item in result["found_keywords"]]

    return {
        "total": result["total"],
        "found": result["found"],
        "coverage_percent": result["coverage_percent"],
        "target": result["target"],
        "passed": result["passed"],
        "overall": "PASS" if result["passed"] else "WARNING",
        "found_keywords": found_kw_strings[:10],  # First 10
        "missing_keywords": result["missing_keywords"][:10],  # First 10
    }


def keyword_matches_semantic(keyword: str, text: str) -> bool:
    """
    Check if keyword matches text semantically.

    Uses morphology-aware matching via keyword_utils.

    Args:
        keyword: Keyword to find
        text: Text to search in

    Returns:
        True if keyword matches (exact or morphological)
    """
    return keyword_matches_text(keyword, text, lang="ru")


def check_keyword_coverage_split(
    text: str, core_keywords: list[str], commercial_keywords: list[str], use_semantic: bool = True
) -> dict:
    """
    Check keyword coverage split by intent.

    Uses CoverageChecker with morphology-aware matching.

    Core keywords: target coverage applies (WARNING if below)
    Commercial keywords: INFO only (no penalty)

    Args:
        text: Content text
        core_keywords: Topic/editorial keywords
        commercial_keywords: Transactional keywords (купить, цена, etc.)
        use_semantic: Use semantic matching (default True)

    Returns:
        Dict with separate coverage metrics
    """
    checker = CoverageChecker(lang="ru")

    # Core coverage (with morphology if use_semantic=True)
    core_result = checker.check(core_keywords, text, use_lemma=use_semantic)

    # Commercial coverage (exact match only - these are transactional terms)
    comm_result = checker.check(commercial_keywords, text, use_lemma=False)

    # Overall based on core only
    overall = "PASS" if core_result["passed"] else "WARNING"

    return {
        "core": {
            "total": core_result["total"],
            "found": core_result["found"],
            "coverage_percent": core_result["coverage_percent"],
            "target": core_result["target"],
            "passed": core_result["passed"],
            "missing_keywords": core_result["missing_keywords"][:10],
        },
        "commercial": {
            "total": comm_result["total"],
            "found": comm_result["found"],
            "coverage_percent": comm_result["coverage_percent"],
            "note": "INFO only (for meta tags)",
            "missing_keywords": comm_result["missing_keywords"][:10],
        },
        "overall": overall,
        "passed": core_result["passed"],
    }


def check_quality(text: str, lang: str = "ru") -> dict:
    """
    Check content quality metrics.

    QA-only (not SEO). In `--mode quality` these metrics are informational and
    reported as WARNING when out of the recommended ranges.

    This check never returns FAIL: publication gating is handled by
    structure/keyword/strict-blacklist checks (and `--mode seo` disables this
    check entirely).

    Args:
        text: Markdown text to check
        lang: 'ru' or 'uk' for stopwords selection
    """
    results: dict[str, Any] = {
        "water": {"value": None, "passed": True, "status": "UNKNOWN"},
        "nausea_classic": {"value": None, "passed": True, "status": "UNKNOWN"},
        "nausea_academic": {"value": None, "passed": True, "status": "UNKNOWN"},
        "overall": "UNKNOWN",
    }

    if calculate_water_and_nausea is None:
        results["note"] = "Water/Nausea check unavailable (missing natasha)"
        return results

    try:
        clean_text = clean_markdown(text)
        metrics = calculate_water_and_nausea(clean_text, lang=lang)

        # Water
        water = metrics.get("water_percent", 0)
        results["water"]["value"] = round(water, 1)

        if water < QUALITY_THRESHOLDS["water_target_min"] or water > QUALITY_THRESHOLDS["water_target_max"]:
            results["water"]["status"] = "WARNING"
        else:
            results["water"]["status"] = "OK"

        # Classic Nausea
        nausea_classic = metrics.get("classic_nausea", 0)
        results["nausea_classic"]["value"] = round(nausea_classic, 2)

        if nausea_classic > QUALITY_THRESHOLDS["nausea_classic_target"]:
            results["nausea_classic"]["status"] = "WARNING"
        else:
            results["nausea_classic"]["status"] = "OK"

        # Academic Nausea
        nausea_academic = metrics.get("academic_nausea", 0)
        results["nausea_academic"]["value"] = round(nausea_academic, 1)

        if nausea_academic > QUALITY_THRESHOLDS["nausea_academic_max"]:
            results["nausea_academic"]["status"] = "WARNING"
        else:
            results["nausea_academic"]["status"] = "OK"

        # Overall
        warnings = [
            results["water"]["status"] == "WARNING",
            results["nausea_classic"]["status"] == "WARNING",
            results["nausea_academic"]["status"] == "WARNING",
        ]

        if any(warnings):
            results["overall"] = "WARNING"
        else:
            results["overall"] = "PASS"

    except Exception as e:
        results["error"] = str(e)
        results["overall"] = "ERROR"

    return results


def check_blacklist_phrases(text: str) -> dict:
    """
    Check for blacklisted phrases.

    BLOCKER:
    - Strict blacklist phrases
    - Brand mentions
    - City mentions

    WARNING:
    - AI-fluff phrases
    """
    results: dict[str, Any] = {
        "strict_phrases": [],
        "brands": [],
        "cities": [],
        "ai_fluff": [],
        "overall": "PASS",
    }

    if check_blacklist is None:
        results["note"] = "Blacklist check unavailable"
        return results

    try:
        blacklist_results = check_blacklist(text)

        results["strict_phrases"] = blacklist_results.get("strict_phrases", [])
        results["brands"] = blacklist_results.get("brands", [])
        results["cities"] = blacklist_results.get("cities", [])
        results["ai_fluff"] = blacklist_results.get("ai_fluff", [])

        # Only strict phrases = BLOCKER (AI-fluff like "в современном мире")
        # Brands/cities = WARNING only (LLM handles this via prompt, false positives common)
        if results["strict_phrases"]:
            results["overall"] = "FAIL"
        elif results["brands"] or results["cities"] or results["ai_fluff"]:
            results["overall"] = "WARNING"
        else:
            results["overall"] = "PASS"

    except Exception as e:
        results["error"] = str(e)

    return results


def check_strict_blacklist_only(text: str) -> dict:
    """
    Strict-only blacklist check (SEO mode).

    BLOCKER:
    - Strict blacklist phrases

    Everything else is informational (brands/cities/ai_fluff are not used for overall).
    """
    results: dict[str, Any] = {
        "strict_phrases": [],
        "brands": [],
        "cities": [],
        "ai_fluff": [],
        "overall": "PASS",
        "note": "SEO mode: only strict phrases are enforced.",
    }

    if check_blacklist is None:
        results["note"] = "Blacklist check unavailable"
        return results

    try:
        blacklist_results = check_blacklist(text)
        results["strict_phrases"] = blacklist_results.get("strict_phrases", [])

        # Keep for visibility, but don't use for overall.
        results["brands"] = blacklist_results.get("brands", [])
        results["cities"] = blacklist_results.get("cities", [])
        results["ai_fluff"] = blacklist_results.get("ai_fluff", [])

        results["overall"] = "FAIL" if results["strict_phrases"] else "PASS"

    except Exception as e:
        results["error"] = str(e)
        results["overall"] = "ERROR"

    return results


def check_length(text: str, keywords_count: int | None = None) -> dict:
    """
    Check content length (informational, not blocker).

    Adaptive recommended range by keywords count (if available).
    Default soft bounds (when keywords_count is unknown): 150-600 words.
    """
    clean_text = clean_markdown(text)
    words = count_words(clean_text)
    chars = count_chars_no_spaces(text)

    recommended_min = QUALITY_THRESHOLDS["words_soft_min"]
    recommended_max = QUALITY_THRESHOLDS["words_soft_max"]
    if keywords_count is not None:
        try:
            adaptive = get_adaptive_requirements(int(keywords_count))
            rec = adaptive.get("words_recommended")
            if rec and len(rec) == 2:
                recommended_min, recommended_max = int(rec[0]), int(rec[1])
        except Exception:  # noqa: S110
            pass

    status = "OK"
    if words < recommended_min:
        status = "WARNING_SHORT"
    elif words > recommended_max:
        status = "WARNING_LONG"

    return {
        "words": words,
        "chars_no_spaces": chars,
        "status": status,
        "keywords_count": keywords_count,
        "recommended_words": (recommended_min, recommended_max),
        "note": "Length is informational (adaptive by keywords_count when available).",
    }


def check_content_standards(text: str, lang: str = "ru") -> dict:
    """
    Check content against CONTENT_GUIDE.md requirements.

    Checks (in quality mode):
    - Safety block: ## Safety или test spot упоминание
    - How-to steps: нумерованные списки (1. 2. 3.)
    - Evergreen Math: расход/концентрация/разведение
    - "Так не делайте": никогда не, нельзя, не допускайте
    - Cross-links: внутренние ссылки ](/

    Returns:
        Dict with checks results
    """
    results: dict[str, Any] = {
        "safety_block": False,
        "howto_steps": False,
        "evergreen_math": False,
        "warnings_present": False,
        "crosslinks_count": 0,
        "issues": [],
        "overall": "OK",
    }

    text_lower = text.lower()

    # Patterns by language
    patterns = {
        "ru": {
            "safety": [
                r"##\s*важно\b",
                r"##\s*безопас",
                r"##\s*как\s+не\s+(сделать|испортить|навредить)",
                r"##\s*ошибк",
                r"##\s*предосторож",
                r"##\s*safety\b",  # language-independent
            ],
            "math": [r"расход", r"концентрац", r"разведен", r"\d+\s*(мл|литр|л\b|г\b)", r"\d+:\d+"],
            "warning": [
                r"никогда\s+не",
                r"нельзя",
                r"не\s+допускайте",
                r"не\s+наносите",
                r"не\s+используйте",
                r"не\s+работайте",
                r"так\s+не\s+делайте",
                r"не\s+пересушивайте",
                r"не\s+давайте\s+высохнуть",
                r"лучше\s+избегать",
                r"не\s+рекомендуется",
            ],
        },
        "uk": {
            "safety": [
                r"##\s*важливо\b",
                r"##\s*безпек",
                r"##\s*як\s+не\s+(зіпсувати|нашкодити)",
                r"##\s*помилк",
                r"##\s*застереж",
                r"##\s*safety\b",  # language-independent
            ],
            "math": [r"витрат", r"концентрац", r"розведен", r"\d+\s*(мл|літр|л\b|г\b)", r"\d+:\d+"],
            "warning": [
                r"ніколи\s+не",
                r"не\s+можна",
                r"не\s+допускайте",
                r"не\s+наносьте",
                r"не\s+використовуйте",
                r"не\s+працюйте",
                r"так\s+не\s+робіть",
                r"не\s+пересушуйте",
                r"не\s+давайте\s+висохнути",
                r"краще\s+уникати",
                r"не\s+рекомендується",
            ],
        },
    }

    # Fallback to RU if lang not found
    lang_patterns = patterns.get(lang, patterns["ru"])

    required = CONTENT_STANDARDS.get("required", {})

    # 1. Safety block
    if any(re.search(p, text_lower) for p in lang_patterns["safety"]) or "test spot" in text_lower:
        results["safety_block"] = True
    elif required.get("safety_block", True):
        results["issues"].append("Нет блока про безопасность/ошибки (Safety/Важливо)")

    # 2. How-to steps: нумерованные списки (Language independent)
    if re.search(r"^\d+\.\s+", text, re.MULTILINE):
        results["howto_steps"] = True
    elif required.get("howto_steps", True):
        results["issues"].append("Нет нумерованных шагов (How-to)")

    # 3. Evergreen Math
    for pattern in lang_patterns["math"]:
        if re.search(pattern, text_lower):
            results["evergreen_math"] = True
            break
    if not results["evergreen_math"] and required.get("evergreen_math", True):
        results["issues"].append("Нет Evergreen Math (расход/разведение/витрата)")

    # 4. "Так не делайте": предупреждения
    for pattern in lang_patterns["warning"]:
        if re.search(pattern, text_lower):
            results["warnings_present"] = True
            break
    if not results["warnings_present"] and required.get("warnings", True):
        results["issues"].append("Нет предупреждений ('так не делайте/не можна')")

    # 5. Cross-links
    crosslinks = re.findall(r"\]\(/", text)
    results["crosslinks_count"] = len(crosslinks)

    # Determine overall status
    critical_missing = required.get("safety_block", True) and not results["safety_block"]
    warnings_count = len(results["issues"])

    if critical_missing or warnings_count >= 3:
        results["overall"] = "WARNING"
    else:
        results["overall"] = "OK"

    return results


def check_grammar(text: str) -> dict:
    """
    Check grammar using language_tool_python.

    WARNING only (not blocker) - grammar issues don't stop workflow.

    Returns:
        Dict with errors list and overall status
    """
    results = {"errors": [], "error_count": 0, "overall": "UNKNOWN", "note": None}

    if not GRAMMAR_AVAILABLE:
        results["note"] = "Grammar check unavailable (install: pip install language-tool-python)"
        results["overall"] = "SKIPPED"
        return results

    try:
        # Initialize LanguageTool for Russian
        tool = language_tool_python.LanguageTool("ru-RU")

        # Clean markdown for grammar check
        clean_text = clean_markdown(text)

        # Check grammar
        matches = tool.check(clean_text)

        if not matches:
            results["overall"] = "PASS"
            return results

        # Parse errors (limit to 10)
        for match in matches[:10]:
            results["errors"].append(
                {
                    "message": match.message,
                    "context": match.context[:80] if match.context else "",
                    "rule": match.ruleId,
                    "suggestions": match.replacements[:3] if match.replacements else [],
                }
            )

        results["error_count"] = len(matches)

        if len(matches) > 5:
            results["overall"] = "WARNING"
        else:
            results["overall"] = "PASS"

        tool.close()

    except Exception as e:
        results["note"] = f"Grammar check error: {str(e)}"
        results["overall"] = "ERROR"

    return results


def check_markdown_lint(file_path: str) -> dict:
    """
    Check Markdown structure using pymarkdownlnt.

    WARNING only (not blocker) - MD lint issues don't stop workflow.

    Returns:
        Dict with violations list and overall status
    """
    results = {"violations": [], "violation_count": 0, "overall": "UNKNOWN", "note": None}

    if not MDLINT_AVAILABLE:
        results["note"] = "MD-Lint check unavailable (install: pip install pymarkdownlnt)"
        results["overall"] = "SKIPPED"
        return results

    try:
        # Create API instance and scan file
        api = PyMarkdownApi()
        scan_result = api.scan_path(file_path)

        # Check if scan was successful
        if not scan_result or not scan_result.scan_failures:
            results["overall"] = "PASS"
            return results

        # Parse violations (limit to 10)
        for failure in scan_result.scan_failures[:10]:
            results["violations"].append(
                {
                    "line": failure.line_number,
                    "column": failure.column_number,
                    "rule": failure.rule_id,
                    "description": failure.rule_description,
                }
            )

        results["violation_count"] = len(scan_result.scan_failures)

        if len(scan_result.scan_failures) > 5:
            results["overall"] = "WARNING"
        else:
            results["overall"] = "PASS"

    except Exception as e:
        results["note"] = f"MD-Lint check error: {str(e)}"
        results["overall"] = "ERROR"

    return results


# =============================================================================
# Main Validation
# =============================================================================


def validate_content(
    file_path: str,
    primary_keyword: str,
    all_keywords: list[str] | None = None,
    core_keywords: list[str] | None = None,
    commercial_keywords: list[str] | None = None,
    use_semantic: bool = True,
    mode: str = "quality",
    lang: str = "ru",
) -> dict:
    """
    Full content validation.

    Args:
        file_path: Path to markdown file
        lang: 'ru' or 'uk' for stopwords selection
        primary_keyword: Target keyword
        all_keywords: List of all keywords for coverage check (legacy)
        core_keywords: Topic/editorial keywords (v8.4)
        commercial_keywords: Transactional keywords (v8.4)
        use_semantic: If True (default), use semantic matching (hybrid approach)
        mode: "quality" (default) or "seo" (simplified SEO mode)

    Returns:
        Dict with all check results and overall status
    """
    if mode not in VALIDATION_MODES:
        return {"error": f"Invalid mode: {mode}. Expected one of: {', '.join(VALIDATION_MODES)}"}

    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    text = path.read_text(encoding="utf-8")

    # Run all checks
    # NOTE: In SEO mode, we keep structure output for visibility, but do not enforce
    # intro length / H2 count as blockers (blockers are defined below).
    structure = check_structure(text)

    semantic_allowed = use_semantic and lang != "uk"

    # Primary keyword: exact or semantic check
    primary_kw = check_primary_keyword(text, primary_keyword)
    semantic_kw = None

    if semantic_allowed and (use_semantic or primary_kw["overall"] == "FAIL"):
        # Run semantic check as fallback or if requested
        semantic_kw = check_primary_keyword_semantic(text, primary_keyword, use_llm=semantic_allowed)

        # If semantic passes but exact fails, upgrade status
        if primary_kw["overall"] == "FAIL" and semantic_kw["overall"] in ["PASS", "WARNING"]:
            primary_kw["semantic_override"] = True
            primary_kw["semantic_result"] = semantic_kw
            primary_kw["overall"] = semantic_kw["overall"]
            primary_kw["note"] = f"Semantic match (confidence: {semantic_kw['confidence']}%)"

    # Coverage: use split if available (v8.4), otherwise legacy
    if core_keywords is not None or commercial_keywords is not None:
        coverage = check_keyword_coverage_split(
            text, core_keywords or [], commercial_keywords or [], use_semantic=semantic_allowed
        )
    else:
        coverage = check_keyword_coverage(text, all_keywords or [])

    if mode == "seo":
        # SEO mode: don't enforce quality metrics, grammar, md-lint; keep coverage as INFO.
        if "core" in coverage:
            coverage["core"]["target"] = None
            coverage["core"]["passed"] = True
            coverage["commercial"]["note"] = "SEO mode: commercial keywords belong to meta/structured data."
        else:
            coverage["target"] = None
            coverage["passed"] = True
        coverage["overall"] = "INFO"
        coverage["note"] = "SEO mode: coverage is informational only (no targets, no warnings)."

        quality = {
            "water": {"value": None, "passed": True, "status": "SKIPPED"},
            "nausea_classic": {"value": None, "passed": True, "status": "SKIPPED"},
            "nausea_academic": {"value": None, "passed": True, "status": "SKIPPED"},
            "overall": "SKIPPED",
            "note": "SEO mode: Water/Nausea disabled.",
        }
        blacklist = check_strict_blacklist_only(text)
    else:
        quality = check_quality(text, lang=lang)
        blacklist = check_blacklist_phrases(text)
    inferred_keywords_count: int | None = None
    if core_keywords is not None or commercial_keywords is not None:
        inferred_keywords_count = len(set((core_keywords or []) + (commercial_keywords or [])))
    elif all_keywords:
        inferred_keywords_count = len(set(all_keywords))

    # Tests (and some integrations) monkeypatch `check_length` with a 1-arg lambda,
    # so keep the call signature tolerant.
    try:
        length = check_length(text, keywords_count=inferred_keywords_count)
    except TypeError:
        try:
            length = check_length(text, inferred_keywords_count)
        except TypeError:
            length = check_length(text)

    # FIX v8.5: Check CONTENT_STANDARDS_2025 requirements (quality mode only)
    if mode == "quality":
        try:
            content_standards = check_content_standards(text, lang=lang)
        except TypeError:
            content_standards = check_content_standards(text)
    else:
        content_standards = {
            "overall": "SKIPPED",
            "note": "SEO mode: content standards check disabled.",
            "issues": [],
        }

    if mode == "seo":
        length["status"] = "INFO"
        length["note"] = "SEO mode: length is informational only."
        grammar = {"overall": "SKIPPED", "note": "SEO mode: grammar check disabled."}
        md_lint = {
            "overall": "SKIPPED",
            "note": "SEO mode: markdown lint disabled.",
            "violations": [],
            "violation_count": 0,
        }
    else:
        grammar = check_grammar(text)
        md_lint = check_markdown_lint(file_path)

    # Determine overall status
    blockers = []
    warnings = []

    # Structure blockers (quality mode only)
    if mode != "seo" and structure["overall"] == "FAIL":
        blockers.append("structure")

    # Primary keyword blockers
    if primary_kw["overall"] == "FAIL":
        blockers.append("primary_keyword")

    # Quality blockers
    if quality["overall"] == "FAIL":
        blockers.append("quality")

    # Blacklist blockers
    if blacklist["overall"] == "FAIL":
        blockers.append("blacklist")

    # Warnings (quality mode only)
    if mode != "seo":
        if coverage["overall"] == "WARNING":
            warnings.append("coverage")
        if quality["overall"] == "WARNING":
            warnings.append("quality")
        if blacklist["overall"] == "WARNING":
            warnings.append("blacklist")
        if length["status"].startswith("WARNING"):
            warnings.append("length")
        if grammar["overall"] == "WARNING":
            warnings.append("grammar")
        if md_lint["overall"] == "WARNING":
            warnings.append("md_lint")
        # FIX v8.5: Add content standards warnings
        if content_standards["overall"] == "WARNING":
            warnings.append("content_standards")

    # Overall
    if blockers:
        overall = "FAIL"
    elif warnings:
        overall = "WARNING"
    else:
        overall = "PASS"

    # SEO mode: do not emit WARNING status at all (INFO metrics only)
    if mode == "seo" and overall == "WARNING":
        overall = "PASS"

    return {
        "file": str(path),
        "primary_keyword": primary_keyword,
        "mode": mode,
        "checks": {
            "structure": structure,
            "primary_keyword": primary_kw,
            "coverage": coverage,
            "quality": quality,
            "blacklist": blacklist,
            "length": length,
            "content_standards": content_standards,  # FIX v8.5
            "grammar": grammar,
            "md_lint": md_lint,
        },
        "summary": {"overall": overall, "blockers": blockers, "warnings": warnings},
    }


# =============================================================================
# CLI
# =============================================================================


def print_results(results: dict):
    """Print human-readable results."""
    print()
    print("=" * 60)
    print("CONTENT VALIDATION (Google 2025 Approach)")
    print("=" * 60)
    print(f"File: {results['file']}")
    print(f"Primary Keyword: {results['primary_keyword']}")
    if results.get("mode"):
        print(f"Mode: {results['mode']}")
    print()

    checks = results["checks"]

    # Structure
    struct = checks["structure"]
    icon = "✅" if struct["overall"] == "PASS" else "❌"
    print(f"{icon} STRUCTURE:")
    print(f"   H1: {'✓' if struct['h1']['passed'] else '✗'} {struct['h1']['value'] or 'missing'}")
    print(f"   Intro: {'✓' if struct['intro']['passed'] else '✗'} ({struct['intro']['words']} words)")
    print(f"   H2 count: {'✓' if struct['h2_count']['passed'] else '✗'} ({struct['h2_count']['count']})")
    print()

    # Primary Keyword
    pk = checks["primary_keyword"]
    icon = "✅" if pk["overall"] == "PASS" else "❌"
    print(f"{icon} PRIMARY KEYWORD:")
    print(f"   In H1: {'✓' if pk['in_h1']['passed'] else '✗'}")
    print(f"   In Intro: {'✓' if pk['in_intro']['passed'] else '✗'}")
    print(f"   Frequency: {pk['frequency']['count']} ({pk['frequency']['status']})")
    print()

    # Coverage (v8.4: split or legacy)
    cov = checks["coverage"]
    if cov["overall"] == "PASS":
        icon = "✅"
    elif cov["overall"] == "WARNING":
        icon = "⚠️"
    else:
        icon = "ℹ️"
    print(f"{icon} KEYWORD COVERAGE:")

    # Check if split format (v8.4)
    if "core" in cov:
        core = cov["core"]
        comm = cov["commercial"]
        if core.get("target") is None:
            print(f"   ┌─ Core (topic): {core['found']}/{core['total']} ({core['coverage_percent']}%)")
        else:
            print(
                f"   ┌─ Core (topic): {core['found']}/{core['total']} ({core['coverage_percent']}%) target={core['target']}%"
            )
        if core["missing_keywords"]:
            print(f"   │  Missing: {', '.join(core['missing_keywords'][:5])}...")
        print(f"   └─ Commercial: {comm['found']}/{comm['total']} ({comm['coverage_percent']}%) [INFO only]")
        if comm["missing_keywords"]:
            print(f"      → For meta: {', '.join(comm['missing_keywords'][:3])}...")
    else:
        # Legacy format
        print(f"   Found: {cov['found']}/{cov['total']} ({cov['coverage_percent']}%)")
        if cov.get("target") is not None:
            print(f"   Target: {cov['target']}%")
        if cov.get("missing_keywords"):
            print(f"   Missing: {', '.join(cov['missing_keywords'][:5])}...")
    if cov.get("note"):
        print(f"   Note: {cov['note']}")
    print()

    # Quality
    qual = checks["quality"]
    icon = "✅" if qual["overall"] == "PASS" else ("❌" if qual["overall"] == "FAIL" else "⚠️")
    print(f"{icon} QUALITY:")
    if qual["water"]["value"] is not None:
        print(f"   Water: {qual['water']['value']}% ({qual['water']['status']})")
        print(f"   Classic Nausea: {qual['nausea_classic']['value']} ({qual['nausea_classic']['status']})")
        print(f"   Academic Nausea: {qual['nausea_academic']['value']}% ({qual['nausea_academic']['status']})")
    else:
        print(f"   {qual.get('note', 'Unavailable')}")
    print()

    # Blacklist
    bl = checks["blacklist"]
    icon = "✅" if bl["overall"] == "PASS" else ("❌" if bl["overall"] == "FAIL" else "⚠️")
    print(f"{icon} BLACKLIST:")
    if bl["strict_phrases"]:
        print(f"   ❌ Strict phrases: {len(bl['strict_phrases'])}")
    if bl["brands"]:
        print(f"   ❌ Brands: {len(bl['brands'])}")
    if bl["ai_fluff"]:
        print(f"   ⚠️  AI-fluff: {len(bl['ai_fluff'])}")
    if bl["overall"] == "PASS":
        print("   No issues found")
    print()

    # Length
    length = checks["length"]
    icon = "ℹ️"
    print(f"{icon} LENGTH (informational):")
    print(f"   Words: {length['words']}")
    print(f"   Chars (no spaces): {length['chars_no_spaces']}")
    if length.get("recommended_words"):
        rec_min, rec_max = length["recommended_words"]
        kwc = length.get("keywords_count")
        if kwc is not None:
            print(f"   Target (by {kwc} keywords): {rec_min}-{rec_max} words")
        else:
            print(f"   Target: {rec_min}-{rec_max} words")
    print(f"   Status: {length['status']}")
    print()

    # Grammar
    gram = checks["grammar"]
    if gram["overall"] == "SKIPPED":
        icon = "⏭️"
    elif gram["overall"] == "PASS":
        icon = "✅"
    elif gram["overall"] == "WARNING":
        icon = "⚠️"
    else:
        icon = "ℹ️"
    print(f"{icon} GRAMMAR:")
    if gram.get("note"):
        print(f"   {gram['note']}")
    elif gram["error_count"] > 0:
        print(f"   Found {gram['error_count']} potential issues")
        for err in gram["errors"][:3]:
            print(f"   - {err['message']}")
    else:
        print("   No issues found")
    print()

    # MD-Lint
    mdl = checks["md_lint"]
    if mdl["overall"] == "SKIPPED":
        icon = "⏭️"
    elif mdl["overall"] == "PASS":
        icon = "✅"
    elif mdl["overall"] == "WARNING":
        icon = "⚠️"
    else:
        icon = "ℹ️"
    print(f"{icon} MARKDOWN LINT:")
    if mdl.get("note"):
        print(f"   {mdl['note']}")
    elif mdl["violation_count"] > 0:
        print(f"   Found {mdl['violation_count']} violations")
        for viol in mdl["violations"][:3]:
            print(f"   - Line {viol['line']}: {viol['rule']} - {viol['description']}")
    else:
        print("   No issues found")
    print()

    # Summary
    summary = results["summary"]
    print("=" * 60)
    if summary["overall"] == "PASS":
        print("✅ OVERALL: PASS")
    elif summary["overall"] == "WARNING":
        print(f"⚠️  OVERALL: WARNING ({', '.join(summary['warnings'])})")
    else:
        print(f"❌ OVERALL: FAIL ({', '.join(summary['blockers'])})")
    print("=" * 60)
    print()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nUsage: python3 validate_content.py <file.md> <keyword> [options]")
        print("\nOptions:")
        print("  --no-semantic  Disable semantic matching (exact match only)")
        print("  --json         Output results as JSON")
        print("  --with-analysis <slug>  Load keywords from analysis")
        print("  --mode <quality|seo>  Validation mode (default: quality)")
        print("  --lang <ru|uk>  Language for stopwords (default: ru)")
        sys.exit(1)

    file_path = sys.argv[1]
    primary_keyword = sys.argv[2]
    output_json = "--json" in sys.argv
    use_semantic = "--no-semantic" not in sys.argv  # semantic is default
    mode = "quality"
    lang = "ru"
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1].strip().lower()
    if "--lang" in sys.argv:
        idx = sys.argv.index("--lang")
        if idx + 1 < len(sys.argv):
            lang = sys.argv[idx + 1].strip().lower()

    # Optional: load all keywords from analysis
    all_keywords = []
    core_keywords = None
    commercial_keywords = None

    if "--with-analysis" in sys.argv:
        idx = sys.argv.index("--with-analysis")
        if idx + 1 < len(sys.argv):
            slug = sys.argv[idx + 1]
            try:
                from analyze_category import analyze_category

                try:
                    analysis = analyze_category(slug, lang=lang)
                except TypeError:
                    analysis = analyze_category(slug)
                if "keywords" in analysis:
                    all_keywords = [kw["keyword"] for kw in analysis["keywords"]["all_keywords"]]
                    # v8.4: Use split keywords if available
                    if "core_keywords" in analysis["keywords"]:
                        core_keywords = analysis["keywords"]["core_keywords"]
                        commercial_keywords = analysis["keywords"]["commercial_keywords"]
            except Exception as e:
                print(f"Warning: Could not load analysis for {slug}: {e}")

    results = validate_content(
        file_path,
        primary_keyword,
        all_keywords,
        core_keywords=core_keywords,
        commercial_keywords=commercial_keywords,
        use_semantic=use_semantic,
        mode=mode,
        lang=lang,
    )

    if "error" in results:
        print(f"❌ {results['error']}")
        sys.exit(2)

    if output_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_results(results)

    # Exit code contract:
    # - PASS    → 0
    # - WARNING → 1
    # - FAIL    → 2
    overall = results["summary"]["overall"]
    if overall == "PASS":
        sys.exit(0)
    if overall == "WARNING":
        sys.exit(1)
    sys.exit(2)


if __name__ == "__main__":
    main()
