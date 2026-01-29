"""
text_utils.py — Unified Text Processing (SSOT)

Canonical implementations for:
- get_stopwords() — RU + UK stopwords
- clean_markdown() — remove markdown formatting
- extract_h1/h2s/intro — heading extraction
- count_words/chars — text metrics
- tokenize — word splitting with stopwords removal
"""

from __future__ import annotations

import re

# =============================================================================
# STOPWORDS (RU + UK)
# =============================================================================

STOPWORDS_RU: frozenset[str] = frozenset(
    {
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
)

STOPWORDS_UK: frozenset[str] = frozenset(
    {
        "і",
        "в",
        "на",
        "з",
        "по",
        "для",
        "із",
        "до",
        "у",
        "о",
        "від",
        "за",
        "при",
        "не",
        "але",
        "а",
        "ж",
        "то",
        "це",
        "як",
        "що",
        "так",
        "все",
        "він",
        "вона",
        "вони",
        "ми",
        "ви",
        "його",
        "її",
        "їх",
        "або",
        "якщо",
        "тільки",
        "вже",
        "ще",
        "би",
        "чи",
        "без",
        "під",
        "над",
        "між",
        "через",
        "після",
        "перед",
        "біля",
        "більше",
        "менше",
        "також",
        "теж",
        "дуже",
        "може",
        "можна",
        "потрібно",
        "є",
        "був",
        "була",
        "були",
        "буде",
        "який",
        "яка",
        "яке",
        "які",
        "цей",
        "ця",
        "ці",
        "той",
        "та",
        "ті",
        "свій",
        "своя",
        "свої",
        "наш",
        "ваш",
        "сам",
        "самий",
        "весь",
        "вся",
        "кожен",
        "будь",
        "інший",
        "такий",
        "щоб",
        "тому",
        "коли",
        "де",
        "куди",
        "звідки",
        "чому",
        "навіщо",
        "скільки",
        "хто",
        "чого",
        "кого",
        "кому",
        "чим",
        "ким",
        "ним",
        "ній",
        "них",
        "йому",
        "їй",
        "їм",
        "вам",
        "нам",
        "себе",
        "собі",
        "собою",
        "мені",
        "мене",
        "мною",
        "тебе",
        "тобі",
        "тобою",
    }
)


def get_stopwords(lang: str = "ru") -> frozenset[str]:
    """
    Get stopwords set for language.

    Args:
        lang: 'ru' (default) or 'uk'

    Returns:
        frozenset of stopwords
    """
    if lang == "uk":
        return STOPWORDS_UK
    return STOPWORDS_RU


# =============================================================================
# MARKDOWN CLEANING
# =============================================================================


def clean_markdown(text: str) -> str:
    """
    Remove markdown formatting for analysis (SSOT).

    This is the canonical function for cleaning markdown.
    All scripts should import from here.

    Removes:
    - YAML front matter
    - Headers markup (keeps text)
    - Links (keeps text)
    - Bold/italic
    - List markers
    - Code blocks
    - Tables

    Args:
        text: Raw markdown text

    Returns:
        Clean text without markdown formatting
    """
    # Remove YAML front matter
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)

    # Remove code blocks (triple backticks)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)

    # Remove inline code backticks but keep the code text
    text = re.sub(r"`([^`]+)`", r"\1", text)

    # Remove headers markup (keep text)
    text = re.sub(r"^#+\s+", "", text, flags=re.MULTILINE)

    # Remove links (keep text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Remove bold/italic
    text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)

    # Remove list markers (unordered and ordered)
    text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)

    # Remove tables
    text = re.sub(r"\|.*?\|", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def normalize_text(text: str) -> str:
    """Alias for clean_markdown (backwards compatibility)."""
    return clean_markdown(text)


# =============================================================================
# HEADING EXTRACTION
# =============================================================================


def extract_h1(text: str) -> str | None:
    """
    Extract H1 heading from markdown.

    Args:
        text: Markdown text

    Returns:
        H1 text without markup, or None if not found
    """
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def extract_h2s(text: str) -> list[str]:
    """
    Extract all H2 headings from markdown.

    Args:
        text: Markdown text

    Returns:
        List of H2 texts without markup
    """
    return re.findall(r"^##\s+(.+)$", text, re.MULTILINE)


def extract_intro(text: str, max_lines: int = 5) -> str:
    """
    Extract intro paragraph (first text after H1).

    Args:
        text: Markdown text
        max_lines: Maximum lines to include (default 5)

    Returns:
        Intro text as single string
    """
    lines = text.split("\n")
    intro_lines = []
    found_h1 = False

    for line in lines:
        if line.startswith("# "):
            found_h1 = True
            continue
        if found_h1 and line.startswith("## "):
            break
        if found_h1:
            if line.strip():
                intro_lines.append(line.strip())
            if len(intro_lines) >= max_lines:
                break

    return " ".join(intro_lines)


# =============================================================================
# TEXT METRICS
# =============================================================================


def count_words(text: str) -> int:
    """
    Count words in text.

    Args:
        text: Text (ideally after clean_markdown)

    Returns:
        Word count
    """
    words = text.split()
    return len(words)


def count_chars_no_spaces(text: str) -> int:
    """
    Count characters excluding whitespace.

    Args:
        text: Text to count

    Returns:
        Character count without spaces/newlines/tabs
    """
    no_spaces = text.replace(" ", "").replace("\n", "").replace("\t", "").replace("\r", "")
    return len(no_spaces)


def tokenize(text: str, lang: str = "ru", remove_stopwords: bool = True) -> list[str]:
    """
    Split text into words, optionally removing stopwords.

    Args:
        text: Text to tokenize
        lang: 'ru' or 'uk' for stopwords
        remove_stopwords: If True, filter out stopwords

    Returns:
        List of words (lowercase)
    """
    # Keep only Cyrillic, Latin letters and digits
    words = re.findall(r"[а-яёїієґa-z0-9]+", text.lower())

    if remove_stopwords:
        stopwords = get_stopwords(lang)
        words = [w for w in words if w not in stopwords and len(w) > 2]

    return words
