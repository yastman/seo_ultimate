#!/usr/bin/env python3
"""
check_keyword_density.py — Keyword Density & Spam Checker

Проверяет плотность ключевых слов и переспам в тексте.
Работает с Markdown файлами (.md) и JSON файлами (_clean.json).

Метрики:
- Плотность ключа = (вхождения ключа / общее кол-во слов) * 100%
- Переспам (>3% для одного ключа или >5% для группы)
- Stem-based анализ (аккумулятор* = аккумулятор, аккумуляторная, аккумуляторный, ...)

Usage:
    python3 scripts/check_keyword_density.py <file.md>
    python3 scripts/check_keyword_density.py <file.md> --with-keywords <slug>
    python3 scripts/check_keyword_density.py <file.md> --top 20
    python3 scripts/check_keyword_density.py <file.md> --json

Exit codes:
    0 = OK (no spam detected)
    1 = WARNING (density 2.5-3%)
    2 = SPAM (density >3%)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

# Snowball Stemmer для группировки словоформ по корню
try:
    from snowballstemmer import stemmer as snowball_stemmer

    STEMMER = snowball_stemmer("russian")
    HAS_STEMMER = True
except ImportError:
    HAS_STEMMER = False
    STEMMER = None

# Fix Windows encoding
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# =============================================================================
# Constants
# =============================================================================

SPAM_THRESHOLD = 3.0  # % - above this is spam
WARNING_THRESHOLD = 2.5  # % - above this is warning
OPTIMAL_RANGE = (1.0, 2.5)  # % - ideal keyword density

# Russian stopwords (common words to exclude from analysis)
STOPWORDS_RU = {
    "и",
    "в",
    "на",
    "с",
    "по",
    "для",
    "из",
    "к",
    "у",
    "о",
    "от",
    "за",
    "при",
    "не",
    "но",
    "а",
    "же",
    "то",
    "это",
    "как",
    "что",
    "так",
    "все",
    "он",
    "она",
    "они",
    "мы",
    "вы",
    "его",
    "её",
    "их",
    "ее",
    "или",
    "если",
    "только",
    "уже",
    "ещё",
    "еще",
    "бы",
    "ли",
    "до",
    "без",
    "под",
    "над",
    "между",
    "через",
    "после",
    "перед",
    "около",
    "более",
    "менее",
    "также",
    "тоже",
    "очень",
    "может",
    "можно",
    "нужно",
    "есть",
    "был",
    "была",
    "были",
    "будет",
    "который",
    "которая",
    "которое",
    "которые",
    "этот",
    "эта",
    "эти",
    "тот",
    "та",
    "те",
    "свой",
    "своя",
    "свои",
    "наш",
    "ваш",
    "сам",
    "самый",
    "весь",
    "вся",
    "всё",
    "каждый",
    "любой",
    "другой",
    "такой",
    "какой",
    "чтобы",
    "потому",
    "поэтому",
    "когда",
    "где",
    "куда",
    "откуда",
    "почему",
    "зачем",
    "сколько",
    "кто",
    "чего",
    "чему",
    "кого",
    "кому",
    "чем",
    "кем",
    "ним",
    "ней",
    "них",
    "ему",
    "ей",
    "им",
    "вам",
    "нам",
    "себя",
    "себе",
    "собой",
    "мне",
    "меня",
    "мной",
    "тебя",
    "тебе",
    "тобой",
}

# Legacy: Common Russian word stems for grouping (fallback if no stemmer)
STEM_PATTERNS = {
    "аккумулятор": r"аккумулятор\w*",
    "полиров": r"полиров\w*",
    "машин": r"машин\w*",
    "батаре": r"батаре\w*",
    "заряд": r"заряд\w*",
    "работ": r"работ\w*",
    "мотор": r"мотор\w*",
    "сетев": r"сетев\w*",
    "беспровод": r"беспровод\w*",
}

# Минимальная частота для включения stem-группы в отчёт
MIN_STEM_FREQUENCY = 3

# Ключевые подстроки для проверки каннибализации и основных ключей
# Формат: category_slug -> (primary_substrings, anti_substrings)
CATEGORY_KEYWORDS = {
    "aktivnaya-pena": (["пен", "активн"], ["ручн", "шампун"]),
    "shampuni-dlya-ruchnoy-moyki": (["ручн", "шампун"], ["пен"]),
    "avtoshampuni": (["автошампун", "шампун"], []),
}


# =============================================================================
# Text Processing
# =============================================================================


def clean_markdown(text: str) -> str:
    """Remove markdown formatting, keep only plain text."""
    # Remove code blocks
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)

    # Remove tables (keep cell content)
    text = re.sub(r"\|", " ", text)
    text = re.sub(r"[-:]+\s*\|", "", text)

    # Remove headers markers
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

    # Remove bold/italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"__([^_]+)__", r"\1", text)
    text = re.sub(r"_([^_]+)_", r"\1", text)

    # Remove links [text](url)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove images
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "", text)

    # Remove list markers
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    # Remove horizontal rules
    text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)

    # Clean extra whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize(text: str) -> list[str]:
    """Split text into words, lowercase."""
    text = text.lower()
    # Keep only Cyrillic, Latin letters and digits
    words = re.findall(r"[а-яёa-z0-9]+", text, re.IGNORECASE)
    return words


def remove_stopwords(words: list[str]) -> list[str]:
    """Remove stopwords from word list."""
    return [w for w in words if w not in STOPWORDS_RU and len(w) > 2]


# =============================================================================
# Density Analysis
# =============================================================================


def count_word_frequencies(words: list[str], top_n: int = 30) -> list[tuple[str, int]]:
    """Count word frequencies, return top N."""
    counter = Counter(words)
    return counter.most_common(top_n)


def count_stem_frequencies(words: list[str]) -> dict[str, dict]:
    """
    Count frequencies by stem (root) using Snowball Stemmer.

    Returns dict: {stem: {'count': N, 'forms': set(), 'example': str}}

    v3.0: Count ALL words (including stopwords) for accurate density.
    Stopwords are only excluded from stem grouping display, not from counting.
    """
    if HAS_STEMMER and STEMMER:
        # Новый метод: полный стемминг всех слов
        stem_groups: dict[str, dict] = {}

        for word in words:
            # Skip only very short words (1-2 chars) - они не несут смысла
            if len(word) < 3:
                continue

            stem = STEMMER.stemWord(word)

            # Не группируем стоп-слова в отчёт, но они уже учтены в total_words
            if word in STOPWORDS_RU:
                continue

            if stem not in stem_groups:
                stem_groups[stem] = {"count": 0, "forms": set(), "example": word}

            stem_groups[stem]["count"] += 1
            stem_groups[stem]["forms"].add(word)

        # Фильтруем: только stem-группы с частотой >= MIN_STEM_FREQUENCY
        return {stem: data for stem, data in stem_groups.items() if data["count"] >= MIN_STEM_FREQUENCY}
    else:
        # Fallback: старый метод с паттернами
        stem_counts: dict[str, dict] = {}

        for stem, pattern in STEM_PATTERNS.items():
            regex = re.compile(pattern, re.IGNORECASE)
            matches = [w for w in words if regex.match(w)]
            if matches:
                stem_counts[stem] = {"count": len(matches), "forms": set(matches), "example": matches[0]}

        return stem_counts


def calculate_density(count: int, total_words: int) -> float:
    """Calculate keyword density as percentage."""
    if total_words == 0:
        return 0.0
    return (count / total_words) * 100


def count_substring_frequencies(words: list[str], substrings: list[str]) -> dict[str, int]:
    """
    Count words containing each substring (user's methodology).

    This matches the user's analysis script:
    sum(1 for w in words if substring in w)
    """
    result = {}
    for substr in substrings:
        count = sum(1 for w in words if substr in w)
        result[substr] = count
    return result


def check_keyword_density(text: str, keyword: str) -> dict[str, Any]:
    """Check density of a specific keyword (exact + partial match)."""
    clean_text = clean_markdown(text)
    words = tokenize(clean_text)
    total_words = len(words)

    # Exact match count
    keyword_lower = keyword.lower()
    keyword_words = tokenize(keyword)

    # Single word keyword
    if len(keyword_words) == 1:
        exact_count = sum(1 for w in words if w == keyword_words[0])
        partial_count = sum(1 for w in words if keyword_words[0] in w)
    else:
        # Multi-word phrase
        text_lower = clean_text.lower()
        exact_count = len(re.findall(re.escape(keyword_lower), text_lower))
        # Partial: count if any word from phrase appears
        partial_count = sum(sum(1 for w in words if kw in w) for kw in keyword_words)

    exact_density = calculate_density(exact_count, total_words)

    return {
        "keyword": keyword,
        "exact_count": exact_count,
        "partial_count": partial_count,
        "total_words": total_words,
        "exact_density": round(exact_density, 2),
        "status": get_density_status(exact_density),
    }


def get_density_status(density: float) -> str:
    """Get status based on density value."""
    if density > SPAM_THRESHOLD:
        return "SPAM"
    elif density > WARNING_THRESHOLD:
        return "WARNING"
    elif density >= OPTIMAL_RANGE[0]:
        return "OK"
    else:
        return "LOW"


# =============================================================================
# Full Analysis
# =============================================================================


def analyze_text(text: str, top_n: int = 20, slug: str | None = None) -> dict[str, Any]:
    """Full keyword density analysis of text."""
    clean_text = clean_markdown(text)
    all_words = tokenize(clean_text)
    words = remove_stopwords(all_words)

    total_words = len(all_words)
    content_words = len(words)

    # Word frequencies
    word_freq = count_word_frequencies(words, top_n)

    # Stem frequencies
    stem_freq = count_stem_frequencies(all_words)

    # Substring analysis (user's methodology) - if slug provided
    substring_analysis = None
    if slug and slug in CATEGORY_KEYWORDS:
        primary_subs, anti_subs = CATEGORY_KEYWORDS[slug]
        primary_counts = count_substring_frequencies(all_words, primary_subs)
        anti_counts = count_substring_frequencies(all_words, anti_subs)

        substring_analysis = {
            "primary": {
                sub: {
                    "count": cnt,
                    "density": round(calculate_density(cnt, total_words), 2),
                    "status": get_density_status(calculate_density(cnt, total_words)),
                }
                for sub, cnt in primary_counts.items()
            },
            "anti": {
                sub: {
                    "count": cnt,
                    "density": round(calculate_density(cnt, total_words), 2),
                }
                for sub, cnt in anti_counts.items()
            },
            "primary_total": sum(primary_counts.values()),
            "primary_density": round(calculate_density(sum(primary_counts.values()), total_words), 2),
            "anti_total": sum(anti_counts.values()),
            "anti_density": round(calculate_density(sum(anti_counts.values()), total_words), 2),
        }

    # Build results
    word_analysis = []
    spam_detected = False
    warning_detected = False

    for word, count in word_freq:
        density = calculate_density(count, total_words)
        status = get_density_status(density)

        if status == "SPAM":
            spam_detected = True
        elif status == "WARNING":
            warning_detected = True

        word_analysis.append(
            {
                "word": word,
                "count": count,
                "density": round(density, 2),
                "status": status,
            }
        )

    stem_analysis = []
    for stem, data in sorted(stem_freq.items(), key=lambda x: -x[1]["count"]):
        count = data["count"]
        density = calculate_density(count, total_words)
        status = get_density_status(density)

        if status == "SPAM":
            spam_detected = True
        elif status == "WARNING":
            warning_detected = True

        # Формируем читаемое представление stem-группы
        forms_sample = sorted(data["forms"])[:3]  # Показываем до 3 форм
        forms_str = ", ".join(forms_sample)
        if len(data["forms"]) > 3:
            forms_str += f" (+{len(data['forms']) - 3})"

        stem_analysis.append(
            {
                "stem": stem + "*",
                "count": count,
                "density": round(density, 2),
                "status": status,
                "forms": forms_str,
                "example": data["example"],
            }
        )

    return {
        "total_words": total_words,
        "content_words": content_words,
        "stopwords_removed": total_words - content_words,
        "word_frequencies": word_analysis,
        "stem_frequencies": stem_analysis,
        "substring_analysis": substring_analysis,
        "spam_detected": spam_detected,
        "warning_detected": warning_detected,
    }


def load_keywords_from_json(slug: str) -> list[str]:
    """Load keywords from category _clean.json file."""
    base_dir = Path(__file__).parent.parent / "categories" / slug / "data"
    json_file = base_dir / f"{slug}_clean.json"

    if not json_file.exists():
        return []

    data = json.loads(json_file.read_text(encoding="utf-8"))
    keywords = []

    # V3 format: keywords is list
    if isinstance(data.get("keywords"), list):
        for kw in data["keywords"]:
            if isinstance(kw, dict):
                keywords.append(kw.get("keyword", ""))
        for kw in data.get("synonyms", []):
            if isinstance(kw, dict):
                keywords.append(kw.get("keyword", ""))

    # V2 format: keywords is dict
    elif isinstance(data.get("keywords"), dict):
        for role in ["primary", "secondary", "supporting"]:
            for kw in data["keywords"].get(role, []):
                if isinstance(kw, dict):
                    keywords.append(kw.get("keyword", ""))

    # V1 format: keywords_detailed
    elif "keywords_detailed" in data:
        for kw in data["keywords_detailed"]:
            if isinstance(kw, dict):
                keywords.append(kw.get("phrase", ""))

    return [k for k in keywords if k]


# =============================================================================
# Output Formatting
# =============================================================================


def format_report(analysis: dict[str, Any], keywords_check: list[dict] | None = None) -> str:
    """Format analysis as human-readable report."""
    lines = []

    lines.append("\n" + "=" * 70)
    lines.append("📊 KEYWORD DENSITY REPORT")
    lines.append("=" * 70)

    lines.append("\n📝 Text Statistics:")
    lines.append(f"   Total words: {analysis['total_words']}")
    lines.append(f"   Content words: {analysis['content_words']}")
    lines.append(f"   Stopwords removed: {analysis['stopwords_removed']}")

    # Stem analysis (most important for spam detection)
    lines.append("\n🌿 Stem Frequencies (grouped by root):")
    if HAS_STEMMER:
        lines.append("   ✅ Snowball Stemmer active — все словоформы сгруппированы")
    else:
        lines.append("   ⚠️  Fallback mode — только захардкоженные паттерны")

    lines.append(f"   {'Stem':<15} {'Count':>5} {'Density':>7} {'Status':<8} {'Forms'}")
    lines.append("   " + "-" * 70)

    for item in analysis["stem_frequencies"][:15]:  # Top 15 stem groups
        status_icon = "🔴" if item["status"] == "SPAM" else "🟡" if item["status"] == "WARNING" else "🟢"
        forms_str = item.get("forms", item.get("example", ""))
        lines.append(
            f"   {item['stem']:<15} {item['count']:>5} {item['density']:>6.2f}% {status_icon} {item['status']:<7} {forms_str}"
        )

    # Word frequencies
    lines.append("\n📖 Top Word Frequencies:")
    lines.append(f"   {'Word':<25} {'Count':>6} {'Density':>8} {'Status':<10}")
    lines.append("   " + "-" * 55)

    for item in analysis["word_frequencies"][:15]:
        status_icon = "🔴" if item["status"] == "SPAM" else "🟡" if item["status"] == "WARNING" else "🟢"
        lines.append(
            f"   {item['word']:<25} {item['count']:>6} {item['density']:>7.2f}% {status_icon} {item['status']:<10}"
        )

    # Substring analysis (user's methodology)
    if analysis.get("substring_analysis"):
        sa = analysis["substring_analysis"]
        lines.append("\n🎯 Substring Analysis (по методологии аудита):")
        lines.append("   Primary Keywords (целевые):")
        for sub, data in sa["primary"].items():
            status_icon = "🔴" if data["status"] == "SPAM" else "🟡" if data["status"] == "WARNING" else "🟢"
            lines.append(f"      '{sub}*': {data['count']} раз = {data['density']}% {status_icon} {data['status']}")
        lines.append(f"   → Итого primary: {sa['primary_total']} = {sa['primary_density']}%")

        if sa["anti"]:
            lines.append("   Anti Keywords (каннибализация):")
            for sub, data in sa["anti"].items():
                lines.append(f"      '{sub}*': {data['count']} раз = {data['density']}%")
            lines.append(f"   → Итого anti: {sa['anti_total']} = {sa['anti_density']}%")

    # Specific keywords check
    if keywords_check:
        lines.append("\n🔑 Target Keywords Check:")
        lines.append(f"   {'Keyword':<40} {'Count':>6} {'Density':>8} {'Status':<10}")
        lines.append("   " + "-" * 70)

        for item in keywords_check:
            status_icon = (
                "🔴"
                if item["status"] == "SPAM"
                else "🟡"
                if item["status"] == "WARNING"
                else "🟢"
                if item["status"] == "OK"
                else "⚪"
            )
            lines.append(
                f"   {item['keyword']:<40} {item['exact_count']:>6} {item['exact_density']:>7.2f}% {status_icon} {item['status']:<10}"
            )

    # Summary
    lines.append("\n" + "=" * 70)
    if analysis["spam_detected"]:
        lines.append("❌ RESULT: SPAM DETECTED — плотность >3%, требуется оптимизация")
    elif analysis["warning_detected"]:
        lines.append("⚠️  RESULT: WARNING — плотность 2.5-3%, близко к порогу")
    else:
        lines.append("✅ RESULT: OK — плотность в норме")
    lines.append("=" * 70)

    # Recommendations
    if analysis["spam_detected"] or analysis["warning_detected"]:
        lines.append("\n💡 Рекомендации:")
        lines.append("   1. Используйте синонимы вместо повторения одного слова")
        lines.append("   2. Замените часть вхождений на местоимения или описательные фразы")
        lines.append("   3. Оптимальная плотность: 1-2.5% для основного ключа")
        lines.append("   4. Stem-группа (аккумулятор*) не должна превышать 3%")

    return "\n".join(lines) + "\n"


# =============================================================================
# CLI
# =============================================================================


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check keyword density and spam in markdown content")
    parser.add_argument("file", help="Path to markdown file")
    parser.add_argument("--slug", metavar="SLUG", help="Category slug for substring analysis (e.g., aktivnaya-pena)")
    parser.add_argument("--with-keywords", metavar="SLUG", help="Load keywords from category slug")
    parser.add_argument("--top", type=int, default=20, help="Number of top words to show (default: 20)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return 2

    text = file_path.read_text(encoding="utf-8")

    # Auto-detect slug from file path if not provided
    slug = args.slug
    if not slug:
        # Try to extract slug from path like .../aktivnaya-pena/content/...
        parts = file_path.parts
        for i, part in enumerate(parts):
            if part == "content" and i > 0:
                slug = parts[i - 1]
                break

    # Main analysis
    analysis = analyze_text(text, top_n=args.top, slug=slug)

    # Check specific keywords if slug provided
    keywords_check = None
    if args.with_keywords:
        keywords = load_keywords_from_json(args.with_keywords)
        if keywords:
            keywords_check = [check_keyword_density(text, kw) for kw in keywords]

    # Output
    if args.json:
        output = {
            "analysis": analysis,
            "keywords_check": keywords_check,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(format_report(analysis, keywords_check))

    # Exit code
    if analysis["spam_detected"]:
        return 2
    elif analysis["warning_detected"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
