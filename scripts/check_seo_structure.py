#!/usr/bin/env python3
"""
SEO Structure Check — проверка структурных SEO-требований

Проверяет:
1. Main keyword в первых 100 символах (INTRO)
2. Keywords в H2 заголовках (минимум 2 из 4)
3. Main keyword frequency (3-5 раз по тексту, не больше - антиспам)

Usage:
    python3 scripts/check_seo_structure.py <file.md> "<main_keyword>"

Exit codes:
    0 - PASS
    1 - WARN (продолжать)
    2 - FAIL (стоп)
"""

import re
import sys
from pathlib import Path

# Add project root to path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.keyword_utils import MorphAnalyzer
from scripts.text_utils import extract_h2s


def detect_language(file_path: str) -> str:
    """
    Определяет язык по пути файла.

    Args:
        file_path: Путь к файлу

    Returns:
        'uk' если путь содержит uk/categories/ или uk\\categories\\, иначе 'ru'
    """
    # Normalize path separators for consistent matching
    normalized = file_path.replace("\\", "/")
    if "uk/categories/" in normalized or "/uk/" in normalized:
        return "uk"
    return "ru"


def normalize_keyword(keyword: str) -> str:
    """Нормализация keyword для поиска (lowercase, убрать лишние пробелы)"""
    return " ".join(keyword.lower().split())


def get_keyword_variations(keyword: str) -> list[str]:
    """
    Генерирует вариации keyword для поиска.

    Пример: "активная пена" -> ["активная пена", "активную пену", "активной пены", ...]
    """
    variations = [normalize_keyword(keyword)]

    # Базовые окончания для русского языка (упрощённо)
    words = keyword.lower().split()

    if len(words) >= 2:
        # Для двухсловных: "активная пена"
        base1 = words[0][:-2] if len(words[0]) > 3 else words[0]
        base2 = words[1][:-1] if len(words[1]) > 3 else words[1]

        # Добавляем частичные совпадения
        variations.append(f"{base1}")
        variations.append(f"{base2}")

    return variations


def check_keyword_in_intro(text: str, keyword: str, limit: int = 150) -> dict:
    """
    Проверка 1: Main keyword в первых N символах (INTRO)

    Args:
        text: Полный текст
        keyword: Main keyword
        limit: Лимит символов для проверки (default 150)

    Returns:
        Dict с результатами
    """
    # Убираем H1 заголовок, берём только текст после него
    lines = text.split("\n")
    intro_text = ""
    found_h1 = False

    for line in lines:
        if line.startswith("# "):
            found_h1 = True
            continue
        if found_h1 and line.strip():
            intro_text = line.strip()
            break

    # Если не нашли структуру с H1, берём первые N символов
    if not intro_text:
        # Убираем markdown разметку
        clean_text = re.sub(r"^#+\s+.*$", "", text, flags=re.MULTILINE)
        clean_text = re.sub(r"\*\*(.+?)\*\*", r"\1", clean_text)
        intro_text = clean_text.strip()[:limit]

    intro_lower = intro_text.lower()
    keyword_lower = normalize_keyword(keyword)

    # Проверяем наличие keyword
    found = keyword_lower in intro_lower

    # Проверяем позицию (в первом предложении)
    first_sentence = intro_text.split(".")[0] if "." in intro_text else intro_text
    in_first_sentence = keyword_lower in first_sentence.lower()

    return {
        "passed": found,
        "in_first_sentence": in_first_sentence,
        "intro_preview": intro_text[:100] + "..." if len(intro_text) > 100 else intro_text,
        "keyword": keyword,
        "message": f"Keyword {'найден' if found else 'НЕ НАЙДЕН'} в INTRO"
        + (f" (в первом предложении: {'да' if in_first_sentence else 'нет'})" if found else ""),
    }


def get_russian_word_stems(keyword: str) -> list[str]:
    """
    Получает основы слов для поиска с учётом русских падежей.

    Для "активная пена" вернёт: ["активный", "пена"]
    Это позволит найти: активная/активную/активной + пена/пену/пены/пеной

    Uses MorphAnalyzer for accurate lemmatization.
    """
    morph = MorphAnalyzer("ru")
    words = re.findall(r"[а-яё]+", keyword.lower())
    return [morph.get_lemma(w) for w in words if len(w) > 2]


def get_ukrainian_word_stems(keyword: str) -> list[str]:
    """
    Получает основы слов для поиска с учётом украинских падежей.

    Для "активна піна" вернёт: ["активний", "піна"]
    Это позволит найти: активна/активну/активної + піна/піну/піни/піною

    Uses MorphAnalyzer for accurate lemmatization.
    """
    morph = MorphAnalyzer("uk")
    words = re.findall(r"[а-яёїієґ]+", keyword.lower())
    return [morph.get_lemma(w) for w in words if len(w) > 2]


def get_word_stems(keyword: str, lang: str = "ru") -> list[str]:
    """
    Универсальный стеммер — делегирует в RU или UK версию.

    Args:
        keyword: Ключевое слово или фраза
        lang: 'ru' или 'uk'

    Returns:
        Список основ слов
    """
    if lang == "uk":
        return get_ukrainian_word_stems(keyword)
    return get_russian_word_stems(keyword)


def check_keywords_in_h2(text: str, keyword: str, lang: str = "ru") -> dict:
    """
    Проверка 2: Keywords в H2 заголовках

    Требование: минимум 2 из H2 должны содержать keyword или вариацию
    Учитывает падежи через стемминг (RU или UK).

    Args:
        text: Полный текст
        keyword: Main keyword
        lang: 'ru' или 'uk' для выбора стеммера

    Returns:
        Dict с результатами
    """
    # Находим все H2 (используем text_utils SSOT)
    h2_matches = extract_h2s(text)

    keyword_lower = normalize_keyword(keyword)
    keyword_words = keyword_lower.split()
    keyword_stems = get_word_stems(keyword, lang)

    h2_with_keyword = []
    h2_without_keyword = []

    for h2 in h2_matches:
        h2_lower = h2.lower()

        # Проверяем полное совпадение
        has_exact = keyword_lower in h2_lower

        # Проверяем по основам слов (для падежей)
        # Требуем наличие ВСЕХ основ ключевого слова
        has_stems = all(stem in h2_lower for stem in keyword_stems if len(stem) > 2)

        # Проверяем частичное (любое значимое слово из keyword)
        has_partial = any(word in h2_lower for word in keyword_words if len(word) > 4)

        if has_exact or has_stems or has_partial:
            h2_with_keyword.append(h2)
        else:
            h2_without_keyword.append(h2)

    total_h2 = len(h2_matches)
    with_keyword = len(h2_with_keyword)
    min_required = 2

    passed = with_keyword >= min_required

    return {
        "passed": passed,
        "total_h2": total_h2,
        "with_keyword": with_keyword,
        "min_required": min_required,
        "h2_list": h2_matches,
        "h2_with_keyword": h2_with_keyword,
        "h2_without_keyword": h2_without_keyword,
        "message": f"H2 с keywords: {with_keyword}/{total_h2} (мин. {min_required})",
    }


def check_keyword_frequency(text: str, keyword: str) -> dict:
    """
    Проверка 3: Частота main keyword (антиспам)

    Требование: 3-7 раз по тексту (меньше = слабое SEO, больше = спам)

    Args:
        text: Полный текст
        keyword: Main keyword

    Returns:
        Dict с результатами
    """
    keyword_lower = normalize_keyword(keyword)
    text_lower = text.lower()

    # Считаем точные вхождения
    count = text_lower.count(keyword_lower)

    # Оптимальный диапазон
    min_freq = 3
    max_freq = 7
    spam_threshold = 10

    if count < min_freq:
        status = "LOW"
        message = f"Keyword '{keyword}' встречается {count} раз (мало, нужно {min_freq}-{max_freq})"
    elif count > spam_threshold:
        status = "SPAM"
        message = f"Keyword '{keyword}' встречается {count} раз (СПАМ! макс. {max_freq})"
    elif count > max_freq:
        status = "HIGH"
        message = f"Keyword '{keyword}' встречается {count} раз (многовато, оптимум {min_freq}-{max_freq})"
    else:
        status = "OK"
        message = f"Keyword '{keyword}' встречается {count} раз (оптимально)"

    return {
        "passed": status in ["OK", "HIGH"],  # HIGH = предупреждение, но не блокер
        "count": count,
        "min_freq": min_freq,
        "max_freq": max_freq,
        "spam_threshold": spam_threshold,
        "status": status,
        "is_spam": status == "SPAM",
        "message": message,
    }


def check_seo_structure(file_path: str, keyword: str) -> tuple[str, dict]:
    """
    Полная проверка SEO-структуры

    Args:
        file_path: Путь к MD файлу
        keyword: Main keyword

    Returns:
        (status, results) где status = 'PASS'/'WARN'/'FAIL'
    """
    # Определяем язык по пути файла
    lang = detect_language(file_path)

    # Читаем файл
    with open(file_path, encoding="utf-8") as f:
        text = f.read()

    # Запускаем проверки
    intro_check = check_keyword_in_intro(text, keyword)
    h2_check = check_keywords_in_h2(text, keyword, lang)
    freq_check = check_keyword_frequency(text, keyword)

    results = {"intro": intro_check, "h2": h2_check, "frequency": freq_check}

    # Определяем общий статус
    if freq_check["is_spam"]:
        status = "FAIL"  # Спам = блокер
    elif not intro_check["passed"]:
        status = "FAIL"  # Keyword не в INTRO = блокер
    elif not h2_check["passed"]:
        status = "WARN"  # H2 без keywords = предупреждение
    elif freq_check["status"] == "LOW":
        status = "WARN"  # Мало keywords = предупреждение
    else:
        status = "PASS"

    results["overall_status"] = status

    return status, results


def main(argv: list[str] | None = None) -> int:
    """CLI entry point (returns exit code)."""
    argv = sys.argv[1:] if argv is None else argv

    if len(argv) < 2:
        print('Usage: python3 check_seo_structure.py <file.md> "<main_keyword>"')
        print('Example: python3 check_seo_structure.py content.md "активная пена"')
        return 2

    file_path = argv[0]
    keyword = argv[1]

    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return 2

    lang = detect_language(file_path)
    print(f"\n{'=' * 60}")
    print("SEO Structure Check")
    print(f"{'=' * 60}")
    print(f"File: {file_path}")
    print(f"Keyword: {keyword}")
    print(f"Language: {lang.upper()}")
    print(f"{'=' * 60}\n")

    status, results = check_seo_structure(file_path, keyword)

    # Вывод результатов
    print("1. KEYWORD В INTRO:")
    intro = results["intro"]
    icon = "✅" if intro["passed"] else "❌"
    print(f"   {icon} {intro['message']}")
    if intro["passed"] and intro["in_first_sentence"]:
        print("   ✅ В первом предложении: да")
    elif intro["passed"]:
        print("   ⚠️  В первом предложении: нет (лучше переместить)")
    print(f'   Preview: "{intro["intro_preview"]}"')

    print("\n2. KEYWORDS В H2:")
    h2 = results["h2"]
    icon = "✅" if h2["passed"] else "⚠️"
    print(f"   {icon} {h2['message']}")
    if h2["h2_with_keyword"]:
        print(f"   ✅ С keyword: {h2['h2_with_keyword']}")
    if h2["h2_without_keyword"]:
        print(f"   ⚠️  Без keyword: {h2['h2_without_keyword']}")

    print("\n3. ЧАСТОТА KEYWORD:")
    freq = results["frequency"]
    if freq["status"] == "OK":
        icon = "✅"
    elif freq["status"] == "SPAM":
        icon = "❌"
    else:
        icon = "⚠️"
    print(f"   {icon} {freq['message']}")

    print(f"\n{'=' * 60}")
    if status == "PASS":
        print("✅ SEO STRUCTURE: PASS")
        exit_code = 0
    elif status == "WARN":
        print("⚠️  SEO STRUCTURE: WARNING")
        exit_code = 1
    else:
        print("❌ SEO STRUCTURE: FAIL")
        exit_code = 2
    print(f"{'=' * 60}\n")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
