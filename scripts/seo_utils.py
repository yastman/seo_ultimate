#!/usr/bin/env python3
"""
seo_utils.py - Unified SEO utilities for validation and fixing

RULES 2025 v8.0 (Google December 2025 Update — Adaptive Approach):

ПРИНЦИП: Depth over Length, Editorial Content, Intent Matching

НЕ используем жёсткие tier-based требования по объёму!
Вместо этого:
- Структура важнее объёма (H1, Intro, H2, FAQ)
- Качество (Water 40-65%, Nausea ≤3.5)
- Адаптивный coverage по количеству ключей
- LLM определяет длину по теме

Функции:
- parse_front_matter() - парсинг YAML + body
- normalize_text() - единая нормализация для подсчёта слов
- count_chars_no_spaces() - символы без пробелов
- count_keyword_occurrences() - exact + partial с fallback
- safe_sentence_split() - Markdown-aware разбивка на предложения
- is_protected_section() - проверка защищённых зон
- get_adaptive_requirements() - NEW: адаптивные требования по keywords count
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

# Keyword utilities (SSOT) - import from keyword_utils
from scripts.keyword_utils import (
    get_adaptive_coverage_target as _get_adaptive_coverage_target,
)
from scripts.keyword_utils import (
    get_commercial_markers,
    get_stoplist_phrases,
)

# Text utilities (SSOT) - import from text_utils
# URL utilities moved to scripts/utils/url.py - re-export for backwards compatibility
from scripts.utils.url import is_blacklisted_domain  # noqa: F401

# Fix path for direct execution and legacy imports
if __name__ == "__main__" or __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from scripts import config as _config
except ImportError:
    # Fallback for some IDE execution contexts or if root is not in path
    import config as _config  # type: ignore

QUALITY_THRESHOLDS = _config.QUALITY_THRESHOLDS
COMMERCIAL_MODIFIERS = _config.COMMERCIAL_MODIFIERS
L3_TO_SLUG = _config.L3_TO_SLUG
SLUG_TO_L3 = _config.SLUG_TO_L3


def get_adaptive_coverage_target(keywords_count: int) -> int:
    """Get coverage target based on keywords count (SSOT from keyword_utils)."""
    return int(_get_adaptive_coverage_target(keywords_count))


# ============================================================================
# SEO Quality Thresholds (SSOT - Imported from config.py)
# ============================================================================

# QUALITY_THRESHOLDS is imported from scripts.config


# ============================================================================
# L3 Category Mapping (SSOT - avoid duplication)
# ============================================================================

# RU mappings are imported from scripts.config as L3_TO_SLUG and SLUG_TO_L3

# UK mappings
L3_TO_SLUG_UK = {
    "Активна піна": "aktivnaya-pena",
    "Для ручного миття": "dlya-ruchnoy-moyki",
    "Очисники скла": "ochistiteli-stekol",
    "Глина і автоскраби": "glina-i-avtoskraby",
    "Антикомаха": "antimoshka",
    "Антибітум": "antibitum",
    "Чорніння шин": "cherniteli-shin",
    "Очисники дисків": "ochistiteli-diskov",
    "Очисники шин": "ochistiteli-shin",
}

SLUG_TO_L3_UK = {v: k for k, v in L3_TO_SLUG_UK.items()}

# Commercial modifiers by language
# RU modifiers are imported from scripts.config as COMMERCIAL_MODIFIERS

COMMERCIAL_MODIFIERS_UK = [
    "купити",
    "ціна",
    "вартість",
    "замовити",
    "в наявності",
    "доставка",
    "недорого",
    "дешево",
    "інтернет-магазин",
    "магазин",
    "каталог",
]


def get_mappings_for_lang(lang: str = "ru") -> tuple[dict[str, str], dict[str, str]]:
    """Get L3_TO_SLUG and SLUG_TO_L3 mappings for specified language."""
    if lang == "uk":
        return L3_TO_SLUG_UK, SLUG_TO_L3_UK
    return L3_TO_SLUG, SLUG_TO_L3


def get_commercial_modifiers(lang: str = "ru") -> list[str]:
    """Get commercial modifiers for specified language."""
    if lang == "uk":
        return COMMERCIAL_MODIFIERS_UK
    return COMMERCIAL_MODIFIERS


# ============================================================================
# Transliteration for Dynamic Slug Generation
# ============================================================================

CYRILLIC_TO_LATIN = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
    # Ukrainian specific
    "і": "i",
    "ї": "yi",
    "є": "ye",
    "ґ": "g",
}


def slugify(text: str) -> str:
    """
    Convert text to URL-safe slug.

    Handles:
    - Cyrillic to Latin transliteration
    - Spaces to hyphens
    - Remove special characters
    - Lowercase

    Args:
        text: Input text (e.g., "Активная пена")

    Returns:
        URL-safe slug (e.g., "aktivnaya-pena")

    Example:
        >>> slugify("Активная пена")
        'aktivnaya-pena'
        >>> slugify("Очистители стёкол")
        'ochistiteli-stekol'
    """
    text = text.lower().strip()

    # Transliterate Cyrillic
    result = []
    for char in text:
        if char in CYRILLIC_TO_LATIN:
            result.append(CYRILLIC_TO_LATIN[char])
        elif char.isalnum() or char == " " or char == "-":
            result.append(char)
        else:
            result.append(" ")

    slug = "".join(result)

    # Replace spaces and multiple hyphens
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")

    return slug


def get_l3_slug(l3_name: str) -> str:
    """
    Get slug for L3 category name.
    Uses static mapping if exists, otherwise generates dynamically.

    Args:
        l3_name: L3 category name (e.g., "Активная пена")

    Returns:
        Slug (e.g., "aktivnaya-pena")
    """
    # Try static mapping first
    if l3_name in L3_TO_SLUG:
        return L3_TO_SLUG[l3_name]

    # Generate dynamically
    return slugify(l3_name)


def get_l3_name(slug: str) -> str | None:
    """
    Get L3 category name from slug.

    Args:
        slug: Category slug (e.g., "aktivnaya-pena")

    Returns:
        L3 name or None if not found
    """
    return SLUG_TO_L3.get(slug)


# ============================================================================
# JSON / File Utils
# ============================================================================


def load_json(path: Path | str) -> dict[str, Any]:
    """
    Safely load JSON file.

    Args:
        path: Path to JSON file

    Returns:
        Dictionary with data or empty dict on error

    Raises:
        FileNotFoundError: if strict=True (not implied here, but good to know)
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON {path}: {e}", file=sys.stderr)
        return {}


def save_json(data: dict[str, Any], path: Path | str, indent: int = 2) -> None:
    """
    Save dictionary to JSON file with utf-8 encoding.

    Args:
        data: Data to save
        path: Path to output file
        indent: Indentation level
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


# ============================================================================
# YAML Front Matter Parsing
# ============================================================================


def parse_front_matter(content: str) -> tuple[dict[str, Any] | None, str, str]:
    """
    Парсинг Markdown с YAML front matter

    Args:
        content: полный MD файл

    Returns:
        (metadata_dict, yaml_text, body_text)
        - metadata_dict: распарсенный YAML (или None)
        - yaml_text: исходный YAML текст с разделителями "---"
        - body_text: MD контент без front matter
    """
    # Regex с поддержкой \r\n и пробелов после ---
    yaml_pattern = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)", re.DOTALL | re.MULTILINE)

    match = yaml_pattern.match(content)

    if match:
        yaml_str = match.group(1)
        body_text = match.group(2)

        try:
            metadata = yaml.safe_load(yaml_str)
        except yaml.YAMLError:
            metadata = None

        # Сохраняем исходный YAML блок для обратной сборки
        yaml_text = f"---\n{yaml_str}\n---\n"

        return metadata, yaml_text, body_text
    else:
        # Нет front matter
        return None, "", content


def rebuild_document(yaml_text: str, body_text: str) -> str:
    """
    Обратная сборка документа из YAML + body

    Args:
        yaml_text: YAML front matter с разделителями
        body_text: MD контент

    Returns:
        Полный документ
    """
    if yaml_text:
        return yaml_text + body_text
    else:
        return body_text


# ============================================================================
# Text Normalization & Counting (SSOT from scripts/text_utils.py)
# ============================================================================
# clean_markdown, normalize_text, count_words, count_chars_no_spaces
# are imported from scripts.text_utils at the top of this file.


# ============================================================================
# Keyword Counting (with fallback)
# ============================================================================


def count_keyword_occurrences(text: str, keyword: str, variations: dict[str, list[str]]) -> tuple[int, int]:
    """
    Подсчёт exact и partial вхождений keyword с fallback

    ВАЖНО: Если variations пусты - используем сам keyword как fallback

    Args:
        text: нормализованный текст
        keyword: базовая форма keyword
        variations: {"exact": [...], "partial": [...]}

    Returns:
        (exact_count, partial_count)
    """
    text_lower = text.lower()

    # Fallback: если variations пусты - используем keyword
    exact_forms = variations.get("exact", [])
    if not exact_forms:
        exact_forms = [keyword] if keyword else []

    partial_forms = variations.get("partial", [])

    exact_count = 0
    for form in exact_forms:
        if form:  # Проверка на пустую строку
            pattern = r"\b" + re.escape(form.lower()) + r"\b"
            exact_count += len(re.findall(pattern, text_lower))

    partial_count = 0
    for form in partial_forms:
        if form:
            pattern = r"\b" + re.escape(form.lower()) + r"\b"
            partial_count += len(re.findall(pattern, text_lower))

    return exact_count, partial_count


# ============================================================================
# Sentence Splitting (Markdown-aware)
# ============================================================================


def safe_sentence_split(md_body: str) -> list[str]:
    r"""
    Безопасное разбиение на предложения с учётом Markdown

    Особенности:
    - Не ломает код-блоки (```)
    - Учитывает вопросы (?) и восклицания (!)
    - Split только на границах с заглавной буквы после .\s

    Args:
        md_body: Markdown контент (без YAML front matter)

    Returns:
        Список предложений
    """
    # 1. Stash код-блоки (временно заменяем плейсхолдерами)
    fences: dict[str, str] = {}

    def stash_fence(match: re.Match[str]) -> str:
        key = f"__FENCE_{len(fences)}__"
        fences[key] = match.group(0)
        return key

    tmp = re.sub(r"```.*?```", stash_fence, md_body, flags=re.DOTALL)

    # 2. Split по границам предложений
    # Lookahead: [\.\!\?] followed by \s+ and then [A-ZА-Я#>\-\*`]
    SENT_SPLIT = re.compile(r"(?<=[\.\!\?])\s+(?=[A-ZА-Я#>\-\*`])")
    parts = SENT_SPLIT.split(tmp)

    # 3. Restore код-блоки
    restored = []
    for part in parts:
        for key, value in fences.items():
            part = part.replace(key, value)
        restored.append(part)

    return restored


def is_protected_section(sentence: str) -> bool:
    """
    Проверка, является ли предложение защищённым (не удалять)

    Защищённые секции:
    - Заголовки (# ## ###)
    - Списки (- * +)
    - Цитаты (>)
    - Код-блоки (```)
    - Нумерованные списки (1. 2.)
    - Вопросы (заканчивается на ?)
    - Жирный текст в начале строки (**text**)

    Args:
        sentence: предложение для проверки

    Returns:
        True если защищено, False если можно удалить
    """
    stripped = sentence.lstrip()

    # Проверка префиксов
    protected_prefixes = (
        "#",  # Заголовки
        "- ",  # Списки
        "* ",
        "+ ",
        "> ",  # Цитаты
        "```",  # Код
        "1.",  # Нумерация
        "2.",
        "3.",
        "4.",
        "5.",
        "**",  # Жирный текст (часто важные термины)
    )

    if stripped.startswith(protected_prefixes):
        return True

    # Проверка суффиксов
    return stripped.endswith("?")

    return False


# ============================================================================
# Adaptive Requirements (Google 2025 Approach)
# ============================================================================


def get_adaptive_requirements(keywords_count: int = 10) -> dict[str, Any]:
    """
    Адаптивные требования на основе количества ключей (НЕ tier)

    Google December 2025 Update:
    - Depth over length
    - Editorial content
    - Intent matching

    Объём НЕ является blocker — только soft guidelines.
    Структура и качество — blockers.

    Args:
        keywords_count: количество ключей в категории

    Returns:
        Dict с требованиями
    """
    # Определяем semantic depth и длину (SSOT: tests + parse_semantics_to_json wrapper).
    #
    # Mapping used across the repo:
    # - <=5 keywords  → shallow → 150-250 words → 900-1500 chars (x6)
    # - <=15 keywords → medium  → 250-400 words → 1500-2400 chars (x6)
    # - >15 keywords  → deep    → 400-600 words → 2400-3600 chars (x6)
    if keywords_count <= 5:
        semantic_depth = "shallow"
        h2_min = 1
        faq_count = (0, 1)
        recommended_words = (150, 250)
    elif keywords_count <= 15:
        semantic_depth = "medium"
        h2_min = 2
        faq_count = (2, 3)
        recommended_words = (250, 400)
    else:
        semantic_depth = "deep"
        h2_min = 3
        faq_count = (3, 5)
        recommended_words = (400, 600)
    coverage_target = get_adaptive_coverage_target(keywords_count)

    return {
        # Semantic info
        "semantic_depth": semantic_depth,
        "keywords_count": keywords_count,
        # Length (SOFT GUIDELINES, not blockers!)
        # SSOT: CONTENT_GUIDE.md v6.1 (adaptive 300-700; tighter by keywords count)
        "words_recommended": recommended_words,
        "words_soft_min": QUALITY_THRESHOLDS["words_soft_min"],  # Warning if less (informational)
        "words_soft_max": QUALITY_THRESHOLDS["words_soft_max"],  # Warning if more (informational)
        "length_is_blocker": False,  # Important: length is NOT a blocker
        # Structure (REQUIRED)
        "h1_required": True,
        "intro_min_words": 30,
        "h2_min": h2_min,
        "faq_range": faq_count,
        # Keywords (Adaptive)
        "primary_in_h1": True,  # BLOCKER
        "primary_in_intro": True,  # BLOCKER
        "coverage_target": coverage_target,  # WARNING if below
        "density_info_only": True,  # Density is informational, not validated
        # Quality (BLOCKERS)
        "water_min": QUALITY_THRESHOLDS["water_target_min"],
        "water_max": QUALITY_THRESHOLDS["water_target_max"],
        "water_blocker_low": QUALITY_THRESHOLDS["water_blocker_low"],
        "water_blocker_high": QUALITY_THRESHOLDS["water_blocker_high"],
        "nausea_classic_max": QUALITY_THRESHOLDS["nausea_classic_target"],
        "nausea_classic_blocker": QUALITY_THRESHOLDS["nausea_classic_blocker"],
        "nausea_academic_blocker": QUALITY_THRESHOLDS["nausea_academic_blocker"],
        # Commercial
        "commercial_min": 1,  # At least one trust signal
        # Blacklist
        "blacklist_is_blocker": True,
        # Notes for LLM
        "llm_notes": {
            "principle": "Раскрой тему полностью, но без воды",
            "length_decision": "LLM определяет длину по семантической глубине",
            "avoid": ["универсальные фразы", "вода ради объёма", "AI-fluff"],
        },
    }


def get_tier_requirements(tier: str = "B") -> dict[str, Any]:
    """
    DEPRECATED: Используй get_adaptive_requirements()

    Оставлено для обратной совместимости.
    Конвертирует tier в примерное количество ключей и вызывает adaptive.
    """
    # Map tier to approximate keywords count
    tier_to_keywords = {
        "A": 30,  # Deep semantic
        "B": 15,  # Medium
        "C": 5,  # Shallow
    }

    keywords_count = tier_to_keywords.get(tier.upper(), 15)
    adaptive = get_adaptive_requirements(keywords_count)

    # Add legacy fields for compatibility
    legacy = {
        "char_min": adaptive["words_recommended"][0] * 6,
        "char_max": adaptive["words_recommended"][1] * 6,
        "min_words": adaptive["words_recommended"][0],
        "max_words": adaptive["words_recommended"][1],
        "h2_range": (adaptive["h2_min"], adaptive["h2_min"] + 2),
        "faq_range": adaptive["faq_range"],
        "coverage": adaptive["coverage_target"] / 100,
        "coverage_max": 0.80,
        "density_min": 0.5,
        "density_max": 2.0,
        "nausea_classic_max": adaptive["nausea_classic_max"],
        "nausea_classic_blocker": adaptive["nausea_classic_blocker"],
        "water_min": adaptive["water_min"],
        "water_max": adaptive["water_max"],
        "water_blocker_low": adaptive["water_blocker_low"],
        "water_blocker_high": adaptive["water_blocker_high"],
        "commercial_min": adaptive["commercial_min"],
        "table_required": keywords_count > 15,
    }

    return legacy


# ============================================================================
# Commercial Markers Validation (v7.3)
# ============================================================================


def find_commercial_markers(text: str, lang: str = "ru") -> dict[str, int]:
    """
    Find commercial markers in text (SSOT from keyword_utils).

    Args:
        text: текст для проверки
        lang: язык ('ru' или 'uk')

    Returns:
        {marker: count, ...} — найденные маркеры с количеством вхождений
    """
    markers = get_commercial_markers(lang)
    found: dict[str, int] = {}
    text_lower = text.lower()
    for marker in markers:
        if marker in text_lower:
            count = text_lower.count(marker)
            found[marker] = count
    return found


def check_commercial_markers(text: str, min_required: int = 3, lang: str = "ru") -> dict[str, Any]:
    """
    Проверка наличия коммерческих маркеров в тексте

    Args:
        text: текст для проверки
        min_required: минимальное количество маркеров
        lang: язык ('ru' или 'uk')

    Returns:
        {
            "passed": bool,
            "found_count": int,
            "found_markers": List[str],
            "min_required": int,
            "message": str
        }
    """
    found_markers = find_commercial_markers(text, lang)
    found = list(found_markers.keys())

    passed = len(found) >= min_required

    return {
        "passed": passed,
        "found_count": len(found),
        "found_markers": found,
        "min_required": min_required,
        "message": f"Коммерческие маркеры: {len(found)}/{min_required} (найдены: {', '.join(found[:5])})"
        if found
        else f"Коммерческие маркеры: 0/{min_required} — FAIL",
    }


# ============================================================================
# Anti-Fluff Stoplist (v7.3)
# ============================================================================


def check_stoplist_phrases(text: str, lang: str = "ru") -> list[str]:
    """
    Find stoplist phrases in text (SSOT from keyword_utils).

    Args:
        text: текст для проверки
        lang: язык ('ru' или 'uk')

    Returns:
        List of found stoplist phrases
    """
    phrases = get_stoplist_phrases(lang)
    found = []
    text_lower = text.lower()
    for phrase in phrases:
        if phrase in text_lower:
            found.append(phrase)
    return found


def check_stoplist(text: str, lang: str = "ru") -> dict[str, Any]:
    """
    Проверка на стоп-фразы (Anti-Fluff)

    Args:
        text: текст для проверки
        lang: язык ('ru' или 'uk')

    Returns:
        {
            "passed": bool,
            "violations": List[str],
            "message": str
        }
    """
    violations = check_stoplist_phrases(text, lang)

    passed = len(violations) == 0

    return {
        "passed": passed,
        "violations": violations,
        "message": f"Стоп-фразы: {len(violations)} найдено" if violations else "Стоп-фразы: OK",
    }


# ============================================================================
# Protected Zones Detection
# ============================================================================


def get_protected_zones(md_body: str) -> dict[str, list[tuple[int, int]]]:
    r"""
    Определить защищённые зоны в документе (не удалять контент)

    Защищённые зоны:
    - Intro (первые 150 слов)
    - H2 разделы (заголовок + первый абзац)
    - FAQ (все вопросы и ответы)

    Args:
        md_body: MD контент без YAML

    Returns:
        {
            "intro": [(start, end)],
            "h2_sections": [(start, end), ...],
            "faq": [(start, end), ...]
        }
    """
    zones: dict[str, list[tuple[int, int]]] = {"intro": [], "h2_sections": [], "faq": []}

    # 1. Intro - только первый абзац ДО первого H2 (сохраняем PRIMARY keywords)
    first_h2_pos = md_body.find("\n## ")
    if first_h2_pos == -1:
        first_h2_pos = len(md_body)

    # Берём только первый абзац (до первого \n\n)
    first_para_end = md_body.find("\n\n")
    if first_para_end != -1 and first_para_end < first_h2_pos:
        zones["intro"].append((0, first_para_end))
    else:
        # Если нет \n\n, берём до H2
        zones["intro"].append((0, min(first_h2_pos, 500)))  # макс 500 chars

    # 2. H2 headers (ТОЛЬКО заголовки, НЕ контент после них)
    h2_pattern = re.compile(r"^##\s+([^\n]+)$", re.MULTILINE)
    for match in h2_pattern.finditer(md_body):
        # Защищаем только строку заголовка
        zones["h2_sections"].append((match.start(), match.end()))

    # 3. FAQ questions (ТОЛЬКО вопросы ###, НЕ ответы - ответы можно редактировать)
    faq_pattern = re.compile(r"^###\s+([^\n]*\?[^\n]*)$", re.MULTILINE)
    for match in faq_pattern.finditer(md_body):
        # Защищаем только строку вопроса
        zones["faq"].append((match.start(), match.end()))

    return zones


def is_in_protected_zone(pos: int, zones: dict[str, list[tuple[int, int]]]) -> bool:
    """
    Проверить, находится ли позиция в защищённой зоне

    Args:
        pos: позиция в тексте
        zones: Dict из get_protected_zones()

    Returns:
        True если в защищённой зоне
    """
    for zone_list in zones.values():
        for start, end in zone_list:
            if start <= pos <= end:
                return True
    return False


# ============================================================================
# Version
# ============================================================================

__version__ = "4.0.0"
__author__ = "Ultimate.net.ua SEO Team"
__updated__ = "2025-12-13"
__seo_standard__ = "v8.0 (Google 2025 — Adaptive Approach, Depth over Length)"
