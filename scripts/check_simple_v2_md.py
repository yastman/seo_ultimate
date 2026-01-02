"""
DEPRECATED: Use validate_content.py instead.

This script is kept for backwards compatibility only.
All functionality has been migrated to validate_content.py (SSOT).

Migration:
    OLD: python3 scripts/check_simple_v2_md.py file.md "keyword" B
    NEW: python3 scripts/validate_content.py file.md "keyword"

---

SEO Validator v2.0 MD - Google 2025 Compatible
Валидатор Markdown контента с YAML front matter

UPDATED: Использует seo_utils.py для унификации с RULES 2025
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

# Импортируем из seo_utils.py для унификации
try:
    from seo_utils import (
        count_chars_no_spaces,
        normalize_text,
        count_words,
        get_tier_requirements
    )
    UTILS_AVAILABLE = True
except ImportError:
    # Fallback если seo_utils.py не в пути
    UTILS_AVAILABLE = False
    print("⚠️  WARNING: seo_utils.py не найден, используется локальная реализация")

# Импортируем Nausea calculator (v7.1)
try:
    from check_water_natasha import calculate_metrics_from_text
    NAUSEA_AVAILABLE = True
except ImportError:
    NAUSEA_AVAILABLE = False


def parse_markdown_file(md_file: str) -> Tuple[Dict, str]:
    """
    Парсинг MD файла с YAML front matter

    Returns:
        (metadata_dict, markdown_content)
    """
    with open(md_file, encoding="utf-8") as f:
        content = f.read()

    # Нормализуем переносы строк (Windows CRLF → Unix LF)
    content = content.replace("\r\n", "\n").replace("\r", "\n")

    # Извлекаем YAML front matter
    yaml_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)

    if yaml_match:
        yaml_str = yaml_match.group(1)
        md_content = yaml_match.group(2)
        try:
            metadata = yaml.safe_load(yaml_str)
        except yaml.YAMLError:
            metadata = {}
    else:
        metadata = {}
        md_content = content

    return metadata, md_content


def extract_text_content(md: str) -> str:
    """
    Извлечь чистый текст из Markdown

    UNIFIED: Использует normalize_text() из seo_utils.py если доступен
    """
    if UTILS_AVAILABLE:
        return normalize_text(md)

    # Fallback - локальная реализация
    # Убираем ссылки [text](url) -> text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", md)
    # Убираем заголовки #
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
    # Убираем таблицы
    text = re.sub(r"\|[^\n]+\|", "", text)
    # Убираем разделители таблиц
    text = re.sub(r"\|-+\|", "", text)
    # Убираем жирный/курсив
    text = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", text)
    # Убираем множественные пробелы
    text = re.sub(r"\s+", " ", text).strip()
    return text


# NOTE: count_chars_no_spaces импортирован из seo_utils.py
# Если импорт не удался, используем fallback
if not UTILS_AVAILABLE:
    def count_chars_no_spaces(content: str) -> int:
        """
        Fallback: Подсчёт символов БЕЗ пробелов, переносов строк и табов

        EXACT FORMULA - совпадает с seo_utils.py
        """
        no_spaces = content.replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')
        return len(no_spaces)


def find_matches_longest_first(text: str, keywords_data: Dict) -> Dict:
    """
    Алгоритм Longest Match First для подсчёта keyword density.

    Решает проблему "семантического каннибализма":
    - Сначала ищем длинные фразы ("активная пена для мойки авто")
    - Маркируем найденные позиции
    - Короткие фразы ("пена") НЕ считаются внутри уже найденных

    Returns:
        Dict с unique_matches и per-keyword stats
    """
    text_lower = text.lower()

    # 1. Собираем ВСЕ уникальные фразы из всех keywords
    all_phrases = set()
    phrase_to_keywords = {}  # phrase -> list of keyword objects that contain it

    for kw_type in ["primary", "secondary", "supporting"]:
        for kw_obj in keywords_data.get(kw_type, []):
            keyword = kw_obj.get("keyword", "").lower()
            variations = kw_obj.get("variations", {})
            exact_forms = variations.get("exact", [])

            # Добавляем сам keyword
            if keyword:
                all_phrases.add(keyword)
                if keyword not in phrase_to_keywords:
                    phrase_to_keywords[keyword] = []
                phrase_to_keywords[keyword].append({
                    "keyword": kw_obj.get("keyword"),
                    "type": kw_type,
                    "is_exact": True
                })

            # Добавляем exact variations
            for form in exact_forms:
                form_lower = form.lower()
                all_phrases.add(form_lower)
                if form_lower not in phrase_to_keywords:
                    phrase_to_keywords[form_lower] = []
                phrase_to_keywords[form_lower].append({
                    "keyword": kw_obj.get("keyword"),
                    "type": kw_type,
                    "is_exact": True
                })

    # 2. Сортируем по длине (longest first)
    sorted_phrases = sorted(all_phrases, key=len, reverse=True)

    # 3. Ищем matches, исключая перекрытия
    used_ranges = []  # [(start, end), ...]
    unique_matches = []  # [{"phrase": ..., "start": ..., "end": ..., "keywords": [...]}]

    def is_overlapping(start: int, end: int) -> bool:
        """Проверяет, пересекается ли диапазон с уже найденными"""
        for used_start, used_end in used_ranges:
            # Проверяем пересечение
            if not (end <= used_start or start >= used_end):
                return True
        return False

    for phrase in sorted_phrases:
        if len(phrase) < 3:  # Пропускаем слишком короткие
            continue

        pattern = r'\b' + re.escape(phrase) + r'\b'

        for match in re.finditer(pattern, text_lower):
            start, end = match.start(), match.end()

            # Проверяем, не пересекается ли с уже найденными
            if not is_overlapping(start, end):
                used_ranges.append((start, end))
                unique_matches.append({
                    "phrase": phrase,
                    "start": start,
                    "end": end,
                    "keywords": phrase_to_keywords.get(phrase, [])
                })

    return {
        "unique_matches": unique_matches,
        "total_unique": len(unique_matches),
        "used_ranges": used_ranges
    }


def check_keyword_density_and_distribution(
    md_content: str, data_json_path: str, word_count: int, requirements: Dict = None
) -> Dict:
    """
    Проверка плотности и распределения keywords — v7.4 Longest Match First

    ИЗМЕНЕНИЯ v7.4:
    - Longest Match First: длинные фразы ищутся первыми
    - Короткие фразы НЕ считаются внутри уже найденных длинных
    - Total density считается по УНИКАЛЬНЫМ matches (без каннибализма)
    - Per-keyword density — информационная (для анализа coverage)

    Формула density: (unique_matches / word_count) × 100

    Targets:
    - TOTAL density: ≤2% (ideal), ≤3.5% (max), >3.5% = SPAM
    - Coverage: 50-60% keywords found (не 90%+ из-за overlapping!)

    Args:
        md_content: полный markdown контент
        data_json_path: путь к JSON файлу с keywords
        word_count: количество слов в тексте
        requirements: словарь с требованиями (из seo_utils)

    Returns:
        Dict with metrics: density, coverage, warnings, errors
    """
    result = {
        "total_density": 0.0,
        "coverage": 0.0,
        "keywords_found": 0,
        "keywords_total": 0,
        "warnings": [],
        "errors": [],
        "details": []
    }

    # Проверка существования JSON
    if not Path(data_json_path).exists():
        result["errors"].append(f"❌ JSON файл не найден: {data_json_path}")
        return result

    # Чтение keywords из JSON
    try:
        with open(data_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        result["errors"].append(f"❌ Ошибка чтения JSON: {e}")
        return result

    keywords_dict = data.get("keywords", {})
    if not keywords_dict:
        result["errors"].append("❌ Нет keywords в JSON")
        return result

    md_lower = md_content.lower()

    # === LONGEST MATCH FIRST ===
    lmf_result = find_matches_longest_first(md_content, keywords_dict)
    unique_matches = lmf_result["unique_matches"]

    # Собираем какие keywords были найдены (для coverage)
    keywords_found_set = set()
    for match in unique_matches:
        for kw_info in match["keywords"]:
            keywords_found_set.add(kw_info["keyword"])

    # === Per-keyword статистика (информационная) ===
    for kw_type in ["primary", "secondary", "supporting"]:
        keywords_list = keywords_dict.get(kw_type, [])

        for kw_obj in keywords_list:
            keyword = kw_obj.get("keyword", "")
            density_target_str = kw_obj.get("density_target", "0%")

            # Считаем сколько раз этот keyword найден в unique matches
            kw_count = sum(
                1 for m in unique_matches
                if any(k["keyword"] == keyword for k in m["keywords"])
            )

            # Density для информации (не для блокировки)
            if word_count > 0:
                actual_density = (kw_count / word_count) * 100
            else:
                actual_density = 0.0

            # Coverage: keyword найден хотя бы раз?
            is_found = keyword in keywords_found_set
            if is_found:
                result["keywords_found"] += 1

            # Статус для отображения
            kw_status = "✅" if is_found else "⚠️"

            result["details"].append({
                "keyword": keyword,
                "type": kw_type,
                "exact": kw_count,  # В новой логике всё считается как "exact"
                "partial": 0,
                "total": kw_count,
                "target": kw_obj.get("occurrences_target", 0),
                "density_actual": f"{actual_density:.2f}%",
                "density_target": density_target_str,
                "status": kw_status
            })

    result["keywords_total"] = (
        len(keywords_dict.get("primary", [])) +
        len(keywords_dict.get("secondary", [])) +
        len(keywords_dict.get("supporting", []))
    )

    # === Coverage (с учётом overlapping keywords) ===
    # При 52 keywords с перекрытием, реальный target 50-60%, не 90%+
    if result["keywords_total"] > 0:
        result["coverage"] = (result["keywords_found"] / result["keywords_total"]) * 100

    # === Total Density (ГЛАВНАЯ МЕТРИКА) ===
    # Считаем только УНИКАЛЬНЫЕ matches (без каннибализма)
    if word_count > 0:
        result["total_density"] = (len(unique_matches) / word_count) * 100

    density = result["total_density"]
    coverage = result["coverage"]

    # === Thresholds v7.5 (адаптивно по количеству keywords) ===
    # Clean JSON (≤20 kw): density blocker = 5.0%
    # Raw JSON (>20 kw): density blocker = 3.5%
    keywords_total = result["keywords_total"]
    if keywords_total <= 20:
        # Clean JSON с 12-15 ключами — выше порог density
        density_blocker = 5.0
        density_warning = 3.5
    else:
        # Raw JSON с 50+ ключами — стандартный порог
        density_blocker = 3.5
        density_warning = 2.5

    if density > density_blocker:
        result["errors"].append(
            f"❌ BLOCKER: Total density {density:.2f}% (>{density_blocker}% — спам)"
        )
    elif density > density_warning:
        result["warnings"].append(
            f"⚠️ REVIEW: Total density {density:.2f}% (высоковато, target ≤{density_warning}%)"
        )

    # Coverage — смягчённые требования для overlapping keywords
    coverage_min = 40.0  # Было 50%, снижено для overlapping
    coverage_max = 80.0  # >80% = возможно переспам

    if requirements:
        coverage_min = requirements.get("coverage", 0.40) * 100

    if coverage < coverage_min:
        result["warnings"].append(
            f"⚠️ Coverage {coverage:.1f}% (target ≥{coverage_min:.0f}%)"
        )
    elif coverage > coverage_max:
        result["warnings"].append(
            f"⚠️ Coverage {coverage:.1f}% (>80% — проверьте на переспам)"
        )

    return result


def check_intro_structure(md: str, words: List[str]) -> Tuple[bool, str]:
    """
    Проверка структуры интро (первые 100-150 слов)
    """
    intro_words = words[:150] if len(words) >= 150 else words
    intro_text = " ".join(intro_words)
    word_count = len(intro_words)

    if word_count < 100:
        return False, f"Интро слишком короткое: {word_count} слов (нужно 100-150)"

    # Проверка на AI-шаблоны
    ai_patterns = [
        r"в этой статье мы рассмотрим",
        r"добро пожаловать",
        r"в данном материале",
        r"давайте разберёмся",
        r"в современном мире",
    ]

    ai_detected = []
    for pattern in ai_patterns:
        if re.search(pattern, intro_text.lower()):
            ai_detected.append(pattern)

    if ai_detected:
        return (
            False,
            f"⚠️  AI-шаблоны в интро: {', '.join(ai_detected)}",
        )

    return True, f"✅ Интро: {word_count} слов, естественный язык"


def check_h2_intent_structure(md: str) -> Tuple[bool, str]:
    """
    Проверка H2 в Markdown (## заголовок)
    """
    h2_list = re.findall(r"^##\s+(.+)$", md, re.MULTILINE)

    if not h2_list:
        return False, "❌ Нет H2 заголовков"

    h2_count = len(h2_list)

    # Intent-ориентированные паттерны
    intent_patterns = [
        r"как выбрать",
        r"как использовать",
        r"как применять",
        r"что такое",
        r"виды",
        r"типы",
        r"чем отличается",
        r"преимущества",
        r"критерии выбора",
        r"советы",
        r"рекомендации",
        r"инструкция",
        r"ошибки",
        r"часто задаваемые",
    ]

    intent_h2_count = 0
    for h2 in h2_list:
        h2_lower = h2.lower()
        for pattern in intent_patterns:
            if re.search(pattern, h2_lower):
                intent_h2_count += 1
                break

    if intent_h2_count == 0:
        return (
            False,
            f"⚠️  H2: {h2_count} шт, но нет intent-ориентированных",
        )

    return True, f"✅ H2: {h2_count} шт, {intent_h2_count} под намерения пользователя"


def check_faq(md: str) -> Tuple[bool, str]:
    """
    Проверка FAQ (вопросы в ### с ? в конце)
    """
    faq_questions = re.findall(r"^###\s+([^#\n]*\?[^#\n]*)$", md, re.MULTILINE)

    total_questions = len(faq_questions)

    if total_questions < 3:
        return False, f"❌ FAQ: {total_questions} вопросов (нужно 3-6)"

    if total_questions > 6:
        return (
            False,
            f"⚠️  FAQ: {total_questions} вопросов (рекомендуется 3-6)",
        )

    return True, f"✅ FAQ: {total_questions} вопросов"


def check_keyword_stuffing(text: str, keyword: str) -> Tuple[bool, str]:
    """
    Проверка на keyword stuffing
    """
    # Нормализуем переносы строк (Windows CRLF → Unix LF)
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    text_lower = text.lower()
    keyword_lower = keyword.lower()

    matches = re.findall(r"\b" + re.escape(keyword_lower) + r"\b", text_lower)
    count = len(matches)

    # Проверка по абзацам (разделены двумя \n)
    paragraphs = text.split("\n\n")
    for para in paragraphs:
        para_lower = para.lower()
        para_matches = re.findall(r"\b" + re.escape(keyword_lower) + r"\b", para_lower)
        if len(para_matches) >= 3:
            return (
                False,
                f"❌ Keyword stuffing: '{keyword}' встречается {len(para_matches)} раз в одном абзаце",
            )

    # Проверка общей плотности
    words = text.split()
    if len(words) < 500 and count > 10:
        return (
            False,
            f"⚠️  Подозрение на переспам: '{keyword}' {count} раз в {len(words)} словах",
        )

    return True, f"✅ Ключевое слово: {count} упоминаний, естественно распределено"


def check_nausea_metrics(md_content: str, tier: str = "B") -> Dict:
    """
    Проверка метрик тошноты и воды (SEO 2025 v7.1 Адвего-калибровка).

    Targets (v7.1):
    - Water: 40-60% (Адвего норма)
    - Classic Nausea: ≤3.5 (BLOCKER >4.0)
    - Academic Nausea: 7-9.5% (Адвего оптимум)

    Args:
        md_content: Markdown контент
        tier: Tier для получения порогов из seo_utils

    Returns:
        Dict with pass/message/metrics
    """
    if not NAUSEA_AVAILABLE:
        return {
            "pass": True,
            "blocker": False,
            "message": "⚠️  Nausea check недоступен (natasha не установлена)"
        }

    try:
        metrics = calculate_metrics_from_text(md_content)
    except Exception as e:
        return {
            "pass": True,
            "blocker": False,
            "message": f"⚠️  Nausea check ошибка: {e}"
        }

    if not metrics:
        return {
            "pass": True,
            "blocker": False,
            "message": "⚠️  Nausea check: текст слишком короткий"
        }

    # Получаем пороги из seo_utils (v7.1)
    if UTILS_AVAILABLE:
        req = get_tier_requirements(tier)
        water_min = req.get("water_min", 40.0)
        water_max = req.get("water_max", 60.0)
        nausea_classic_max = req.get("nausea_classic_max", 3.5)
        nausea_classic_blocker = req.get("nausea_classic_blocker", 4.0)
        nausea_academic_min = req.get("nausea_academic_min", 7.0)
        nausea_academic_max = req.get("nausea_academic_max", 9.5)
    else:
        # Fallback defaults (v7.1)
        water_min, water_max = 40.0, 60.0
        nausea_classic_max, nausea_classic_blocker = 3.5, 4.0
        nausea_academic_min, nausea_academic_max = 7.0, 9.5

    water = metrics['water_percent']
    classic = metrics['classic_nausea']
    academic = metrics['academic_nausea']

    issues = []
    is_blocker = False

    # Water check (40-60%)
    if water < water_min:
        issues.append(f"Water {water:.1f}% < {water_min}% (сухой)")
    elif water > water_max:
        issues.append(f"Water {water:.1f}% > {water_max}%")

    # Classic Nausea check (≤3.5, BLOCKER >4.0)
    if classic > nausea_classic_blocker:
        issues.append(f"Classic Nausea {classic:.2f} > {nausea_classic_blocker} [BLOCKER]")
        is_blocker = True
    elif classic > nausea_classic_max:
        issues.append(f"Classic Nausea {classic:.2f} > {nausea_classic_max}")

    # Academic Nausea check (7-9.5%)
    if academic < nausea_academic_min:
        issues.append(f"Academic {academic:.1f}% < {nausea_academic_min}% (сухой)")
    elif academic > nausea_academic_max:
        if academic > 12.0:
            issues.append(f"Academic {academic:.1f}% > 12% [BLOCKER]")
            is_blocker = True
        else:
            issues.append(f"Academic {academic:.1f}% > {nausea_academic_max}%")

    # Формируем результат
    if not issues:
        status = "✅"
        message = f"{status} Nausea/Water: Water {water:.1f}% | Classic {classic:.2f} | Academic {academic:.1f}%"
        passed = True
    else:
        status = "❌" if is_blocker else "⚠️"
        message = f"{status} Nausea/Water: {', '.join(issues)}"
        passed = not is_blocker

    return {
        "pass": passed,
        "blocker": is_blocker,
        "message": message,
        "metrics": {
            "water_percent": water,
            "classic_nausea": classic,
            "academic_nausea": academic,
            "most_common_lemma": metrics.get('most_common_lemma', ''),
            "max_frequency": metrics.get('max_frequency', 0)
        }
    }


def check_internal_links(md: str) -> Tuple[bool, str]:
    """
    Проверка внутренних ссылок [text](url)
    """
    # Ищем ссылки вида [text](url) или [text](https://domain/path)
    all_links = re.findall(r"\[([^\]]+)\]\(([^\)]+)\)", md)

    # Внутренние ссылки начинаются с / или с доменом ultimate.net.ua
    internal_links = [
        link for link in all_links if link[1].startswith("/") or "ultimate.net.ua" in link[1]
    ]

    link_count = len(internal_links)

    if link_count < 2:
        return (
            True, # CHANGED to True (PASS with warning) for v7.3
            f"⚠️  Внутренние ссылки: {link_count} (нужно 2-5) [WARNING only]",
        )

    if link_count > 5:
        return (
            True, # CHANGED to True (PASS with warning)
            f"⚠️  Внутренние ссылки: {link_count} (рекомендуется 2-5)",
        )

    # Проверка анкоров
    bad_anchors = ["здесь", "тут", "читать далее", "подробнее", "перейти", "ссылка"]
    bad_found = []
    for anchor, _url in internal_links:
        anchor_clean = anchor.strip().lower()
        if anchor_clean in bad_anchors:
            bad_found.append(anchor)

    if bad_found:
        return (
            False,
            f"⚠️  Внутренние ссылки: {link_count} шт, но неописательные анкоры: {', '.join(bad_found)}",
        )

    return True, f"✅ Внутренние ссылки: {link_count} шт, описательные анкоры"


def check_content(md_file: str, keyword: str, tier: str = "B") -> Dict:
    """
    Основная проверка Markdown контента
    """
    try:
        metadata, md_content = parse_markdown_file(md_file)
    except FileNotFoundError:
        return {"status": "ERROR", "message": f"Файл не найден: {md_file}"}

    # Извлекаем текст
    text = extract_text_content(md_content)
    
    if UTILS_AVAILABLE:
        word_count = count_words(text)
        words = text.split() # Keep for other checks that need list of words
    else:
        words = text.split()
        word_count = len(words)

    # Подсчёт символов БЕЗ пробелов (RULES 2025 - BLOCKER!)
    char_count_no_spaces = count_chars_no_spaces(md_content)

    # Требования по Tier - UNIFIED через seo_utils.py (RULES 2025)
    if UTILS_AVAILABLE:
        req = get_tier_requirements(tier)
    else:
        # Critical Error: seo_utils MUST be available for v7.3 validation
        print("❌ CRITICAL ERROR: seo_utils.py not found. Validation cannot proceed reliably.")
        return {"status": "ERROR", "message": "seo_utils.py dependency missing"}


    results = {
        "file": Path(md_file).name,
        "tier": tier,
        "word_count": word_count,
        "char_count_no_spaces": char_count_no_spaces,
        "checks": {},
        "status": "PASS",
        "metadata": metadata,
    }

    # 0. Проверка символов БЕЗ пробелов (Google 2025 - advisory only, not blocker)
    char_count_ok = req["char_min"] <= char_count_no_spaces <= req["char_max"]
    results["checks"]["char_count"] = {
        "pass": char_count_ok,
        "blocker": False,  # Google 2025: depth > length, char count is advisory
        "message": f"{'✅' if char_count_ok else '⚠️ '} Символов (без пробелов): {char_count_no_spaces} (рекомендация: {req['char_min']}-{req['char_max']})",
    }

    # 1. Проверка объёма (слова - для справки)
    word_count_ok = req["min_words"] <= word_count <= req["max_words"]
    results["checks"]["word_count"] = {
        "pass": word_count_ok,
        "blocker": False,
        "message": f"{'✅' if word_count_ok else '⚠️ '} Слов: {word_count} (ориентир: {req['min_words']}-{req['max_words']})",
    }

    # 2. H1 (в Markdown это # заголовок)
    h1_list = re.findall(r"^#\s+(.+)$", md_content, re.MULTILINE)
    h1_count = len(h1_list)
    h1_text = h1_list[0] if h1_list else ""
    h1_ok = h1_count == 1
    results["checks"]["h1"] = {
        "pass": h1_ok,
        "message": f"{'✅' if h1_ok else '❌'} H1: {h1_count} шт (нужно 1)",
        "text": h1_text[:60] if h1_text else "",
    }

    # 3. Структура интро
    intro_ok, intro_msg = check_intro_structure(md_content, words)
    results["checks"]["intro"] = {"pass": intro_ok, "message": intro_msg}

    # 4. H2 структура
    h2_ok, h2_msg = check_h2_intent_structure(md_content)
    results["checks"]["h2_intent"] = {"pass": h2_ok, "message": h2_msg}

    # 5. FAQ
    faq_ok, faq_msg = check_faq(md_content)
    if tier == "C":
        results["checks"]["faq"] = {"pass": True, "message": f"ℹ️  {faq_msg} (опционально)"}
    else:
        results["checks"]["faq"] = {"pass": faq_ok, "message": faq_msg}

    # 6. Keyword stuffing (используем md_content с переносами строк)
    stuffing_ok, stuffing_msg = check_keyword_stuffing(md_content, keyword)
    results["checks"]["keyword_natural"] = {"pass": stuffing_ok, "message": stuffing_msg}

    # 6.5. Keyword Density & Distribution (RULES 2025)
    # Определяем путь к JSON на основе md_file
    # Например: categories/aktivnaya-pena/content/aktivnaya-pena_ru.md
    #        -> categories/aktivnaya-pena/data/aktivnaya-pena.json
    md_path = Path(md_file)
    if "categories" in md_path.parts:
        # Извлекаем slug из пути
        category_idx = md_path.parts.index("categories")
        if category_idx + 1 < len(md_path.parts):
            slug = md_path.parts[category_idx + 1]

            # D+E: Fallback — _clean.json (12 kw) → {slug}.json (52 kw)
            clean_json_path = md_path.parent.parent / "data" / f"{slug}_clean.json"
            raw_json_path = md_path.parent.parent / "data" / f"{slug}.json"

            if clean_json_path.exists():
                data_json_path = clean_json_path
            else:
                data_json_path = raw_json_path

            if data_json_path.exists():
                density_result = check_keyword_density_and_distribution(
                    md_content, str(data_json_path), word_count, req
                )

                density = density_result["total_density"]
                coverage = density_result["coverage"]
                keywords_total = density_result.get("keywords_total", 50)

                # Определяем severity по Google 2025 порогам (people-first)
                # v7.5: Адаптивный порог по количеству keywords
                # Clean JSON (≤20 kw): blocker = 5.0%, warning = 3.5%
                # Raw JSON (>20 kw): blocker = 3.5%, warning = 2.5%
                if keywords_total <= 20:
                    density_blocker = 5.0
                    density_warning = 3.5
                else:
                    density_blocker = 3.5
                    density_warning = 2.5

                coverage_min = req.get("coverage", 0.30) * 100  # Снижено для LMF
                if density > density_blocker:
                    severity = "FAIL"
                elif density > density_warning or coverage < coverage_min:
                    severity = "REVIEW"
                else:
                    severity = "PASS"

                density_pass = severity != "FAIL"

                status_icon = (
                    "✅" if severity == "PASS"
                    else "⚠️" if severity == "REVIEW"
                    else "❌"
                )

                status_msg = (
                    f"{status_icon} Density: {density:.2f}% | "
                    f"Coverage: {coverage:.0f}%"
                )

                if density_result.get("warnings"):
                    status_msg += f" | {len(density_result['warnings'])} предупреждений"

                if density_result.get("errors"):
                    status_msg += f" | {len(density_result['errors'])} ошибок"

                results["checks"]["density_distribution"] = {
                    "pass": density_pass,
                    "blocker": True,
                    "severity": severity,
                    "message": status_msg,
                    "details": density_result
                }
            else:
                results["checks"]["density_distribution"] = {
                    "pass": True,
                    "blocker": False,
                    "message": f"⚠️  JSON не найден: {data_json_path.name}"
                }
    else:
        results["checks"]["density_distribution"] = {
            "pass": True,
            "blocker": False,
            "message": "⚠️  Путь не содержит 'categories/', пропуск проверки density"
        }

    # 7. Первые 100 слов
    first_100 = " ".join(words[:100])
    keyword_in_first_100 = keyword.lower() in first_100.lower()
    results["checks"]["first_100"] = {
        "pass": keyword_in_first_100,
        "message": f"{'✅' if keyword_in_first_100 else '⚠️ '} Первые 100 слов: ключ {'найден' if keyword_in_first_100 else 'НЕ НАЙДЕН'}",
    }

    # 8. Внутренние ссылки
    links_ok, links_msg = check_internal_links(md_content)
    results["checks"]["internal_links"] = {"pass": links_ok, "message": links_msg}

    # 8.5. Nausea/Water check (SEO 2025 v7.1 Адвего-калибровка)
    nausea_result = check_nausea_metrics(md_content, tier)
    results["checks"]["nausea_water"] = nausea_result

    # 9. Title (из YAML)
    title_text = metadata.get("title", "")
    title_len = len(title_text)
    title_ok = 50 <= title_len <= 70
    results["checks"]["title"] = {
        "pass": title_ok,
        "message": f"{'✅' if title_ok else '⚠️ '} Title: {title_len} символов (рекомендуется 50-70)",
        "text": title_text,
    }

    # 10. Description (из YAML)
    desc_text = metadata.get("description", "")
    desc_len = len(desc_text)
    desc_ok = 140 <= desc_len <= 170
    results["checks"]["description"] = {
        "pass": desc_ok,
        "message": f"{'✅' if desc_ok else '⚠️ '} Description: {desc_len} символов (рекомендуется 140-170)",
        "text": desc_text[:80] if desc_text else "",
    }

    # 11. Schema.org (для MD пропускаем, т.к. будет в БД)
    results["checks"]["schema"] = {
        "pass": True,
        "message": "ℹ️  Schema.org: будет добавлено при интеграции в OpenCart",
    }

    # Итоговый статус
    # BLOCKER checks - Google 2025 (char_count removed - depth > length)
    blocker_checks = ["nausea_water"]  # char_count теперь advisory, density вынесен в severity
    # Critical checks
    critical_checks = ["h1", "intro", "h2_intent", "keyword_natural", "internal_links"]

    all_blocker_pass = all(
        results["checks"][check]["pass"]
        for check in blocker_checks
        if check in results["checks"]
    )
    all_critical_pass = all(
        results["checks"][check]["pass"]
        for check in critical_checks
        if check in results["checks"]
    )

    density_severity = results["checks"].get(
        "density_distribution", {}
    ).get("severity", "PASS")

    if not all_blocker_pass or not all_critical_pass or density_severity == "FAIL":
        results["status"] = "FAIL"
    else:
        optional_checks = ["word_count", "first_100"]
        optional_pass = sum(
            1
            for check in optional_checks
            if check in results["checks"] and results["checks"][check]["pass"]
        )

        if density_severity == "REVIEW" or optional_pass < len(optional_checks) * 0.7:
            results["status"] = "REVIEW"
        else:
            results["status"] = "PASS"

    return results


def print_report(results: Dict):
    """Вывод отчёта"""
    print(f"\n{'=' * 70}")
    print(f"📄 ПРОВЕРКА: {results['file']}")
    print(f"🎯 TIER: {results['tier']}")
    print(f"📊 Слов: {results['word_count']} | Символов (без пробелов): {results.get('char_count_no_spaces', 'N/A')}")
    print(f"{'=' * 70}\n")

    for check_name, check_data in results["checks"].items():
        print(check_data["message"])
        if "text" in check_data and check_data["text"]:
            print(f'   └─ "{check_data["text"]}..."')

        # Если это density check, показываем детализацию
        if check_name == "density_distribution" and "details" in check_data:
            density_details = check_data["details"]
            if density_details.get("details"):
                print(f"\n   📊 ДЕТАЛИЗАЦИЯ KEYWORDS (Top 10):")
                print(f"   {'Keyword':<40} {'Type':<10} {'Exact':<6} {'Partial':<7} {'Total':<6} {'Density':<8} {'Target'}")
                print(f"   {'-' * 100}")

                # Показываем первые 10 keywords
                for i, kw in enumerate(density_details["details"][:10]):
                    status = kw["status"]
                    print(f"   {status} {kw['keyword']:<38} {kw['type']:<10} {kw['exact']:<6} {kw['partial']:<7} {kw['total']:<6} {kw['density_actual']:<8} {kw['density_target']}")

                total_kw = len(density_details["details"])
                if total_kw > 10:
                    print(f"   ... и ещё {total_kw - 10} keywords")
                print()

            # Показываем warnings
            if density_details.get("warnings"):
                print(f"\n   ⚠️  ПРЕДУПРЕЖДЕНИЯ ({len(density_details['warnings'])}):")
                for warning in density_details["warnings"][:5]:  # Первые 5
                    print(f"      • {warning}")
                if len(density_details['warnings']) > 5:
                    print(f"      ... и ещё {len(density_details['warnings']) - 5} предупреждений")
                print()

            # Показываем errors
            if density_details.get("errors"):
                print(f"\n   ❌ ОШИБКИ ({len(density_details['errors'])}):")
                for error in density_details["errors"]:
                    print(f"      • {error}")
                print()

    print(f"\n{'=' * 70}")
    status_icons = {"PASS": "✅", "REVIEW": "⚠️ ", "FAIL": "❌"}
    print(f"{status_icons[results['status']]} РЕЗУЛЬТАТ: {results['status']}")

    if results["status"] == "PASS":
        print("   Контент соответствует Google Search Essentials 2025")
    elif results["status"] == "REVIEW":
        print("   Контент требует доработки optional параметров")
    else:
        print("   Контент требует исправлений перед публикацией")

    print(f"{'=' * 70}\n")


def save_json_report(results: Dict, md_file: str):
    """
    Сохранение результатов в JSON для машинного чтения

    Сохраняет в: <md_file>_validation.json

    Args:
        results: результаты check_content()
        md_file: путь к исходному MD файлу
    """
    md_path = Path(md_file)
    json_path = md_path.parent / f"{md_path.stem}_validation.json"

    # Упрощаем структуру для JSON (убираем текстовые сообщения, оставляем метрики)
    json_output = {
        "file": results["file"],
        "tier": results["tier"],
        "word_count": results["word_count"],
        "char_count_no_spaces": results.get("char_count_no_spaces", 0),
        "status": results["status"],
        "checks": {}
    }

    # Упрощаем checks для JSON
    for check_name, check_data in results["checks"].items():
        json_output["checks"][check_name] = {
            "pass": check_data["pass"],
            "blocker": check_data.get("blocker", False)
        }

        # Добавляем density детали если есть
        if check_name == "density_distribution" and "details" in check_data:
            density_details = check_data["details"]
            json_output["checks"][check_name]["metrics"] = {
                "total_density": density_details.get("total_density", 0.0),
                "coverage": density_details.get("coverage", 0.0),
                "keywords_found": density_details.get("keywords_found", 0),
                "keywords_total": density_details.get("keywords_total", 0),
                "warnings_count": len(density_details.get("warnings", [])),
                "errors_count": len(density_details.get("errors", [])),
                "details": density_details.get("details", [])
            }

    # Сохраняем JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)

    print(f"\n✅ JSON report сохранён: {json_path}")
    return str(json_path)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="SEO Validator v2.0 MD - Google 2025 Compatible",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  python check_simple_v2_md.py content.md "активная пена" A
  python check_simple_v2_md.py content.md "активная пена" B --json

Tier: A (премиум) / B (стандарт) / C (минимум)
        """
    )

    parser.add_argument("md_file", help="Путь к Markdown файлу")
    parser.add_argument("keyword", help="Ключевое слово для проверки")
    parser.add_argument("tier", nargs='?', default="B", help="Tier контента (A/B/C)")
    parser.add_argument("--json", action="store_true", help="Сохранить результаты в JSON")

    args = parser.parse_args()

    # Проверка существования файла
    if not Path(args.md_file).exists():
        print(f"❌ Файл не найден: {args.md_file}")
        sys.exit(1)

    tier = args.tier.upper()
    results = check_content(args.md_file, args.keyword, tier)

    # Текстовый отчёт (всегда)
    print_report(results)

    # JSON отчёт (опционально)
    if args.json:
        save_json_report(results, args.md_file)

    if results["status"] == "PASS":
        code = 0
    elif results["status"] == "REVIEW":
        code = 1
    else:
        code = 2

    sys.exit(code)


if __name__ == "__main__":
    main()
