# Scripts Refactoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать единый SSOT модуль text_utils.py и унифицировать валидаторы с полной UK поддержкой.

**Architecture:** Извлекаем дублирующийся код (clean_markdown, stopwords, extract_*) в text_utils.py. Все валидаторы импортируют оттуда. Добавляем --lang параметр для UK.

**Tech Stack:** Python 3.11+, pymorphy3, pytest

**Testing Strategy:** TDD (test-first), smoke tests, real data tests. Target: 80% coverage.

---

## Phase 0: Test Infrastructure Setup

### Task 0: Create test fixtures with real data

**Files:**
- Create: `tests/fixtures/real_data.py`
- Create: `tests/conftest.py` (update)

**Step 1: Create fixtures file with real category data**

```python
# tests/fixtures/real_data.py
"""Real data fixtures for smoke and integration tests."""

from pathlib import Path

# Paths to real category data
PROJECT_ROOT = Path(__file__).parent.parent.parent
CATEGORIES_DIR = PROJECT_ROOT / "categories"
UK_CATEGORIES_DIR = PROJECT_ROOT / "uk" / "categories"

# Sample RU categories for testing
SAMPLE_RU_CATEGORIES = [
    "aktivnaya-pena",
    "polirovalnye-pasty",
    "ochistiteli-stekol",
]

# Sample UK categories for testing
SAMPLE_UK_CATEGORIES = [
    "aktivnaya-pena",
    "cherniteli-shin",
]


def get_ru_content_path(slug: str) -> Path:
    """Get path to RU content file."""
    return CATEGORIES_DIR / slug / "content" / f"{slug}_ru.md"


def get_uk_content_path(slug: str) -> Path:
    """Get path to UK content file."""
    return UK_CATEGORIES_DIR / slug / "content" / f"{slug}_uk.md"


def get_ru_meta_path(slug: str) -> Path:
    """Get path to RU meta file."""
    return CATEGORIES_DIR / slug / "meta" / f"{slug}_meta.json"


def get_uk_meta_path(slug: str) -> Path:
    """Get path to UK meta file."""
    return UK_CATEGORIES_DIR / slug / "meta" / f"{slug}_meta.json"


def get_ru_clean_path(slug: str) -> Path:
    """Get path to RU clean JSON file."""
    return CATEGORIES_DIR / slug / "data" / f"{slug}_clean.json"


# Real content samples for unit tests
SAMPLE_RU_MARKDOWN = """---
title: Активная пена
---

# Активная пена для бесконтактной мойки

Активная пена — современное моющее средство для бесконтактной мойки автомобиля.

## Как выбрать активную пену

При выборе активной пены обратите внимание на концентрацию и pH-уровень.

## Как правильно использовать

1. Разведите средство согласно инструкции
2. Нанесите на кузов снизу вверх
3. Подождите 2-3 минуты
4. Смойте водой

## Частые ошибки

Никогда не наносите пену на горячий кузов. Не давайте высохнуть.
"""

SAMPLE_UK_MARKDOWN = """---
title: Активна піна
---

# Активна піна для безконтактної мийки

Активна піна — сучасний миючий засіб для безконтактної мийки автомобіля.

## Як обрати активну піну

При виборі активної піни зверніть увагу на концентрацію та pH-рівень.

## Як правильно використовувати

1. Розведіть засіб згідно з інструкцією
2. Нанесіть на кузов знизу вгору
3. Зачекайте 2-3 хвилини
4. Змийте водою

## Часті помилки

Ніколи не наносьте піну на гарячий кузов. Не давайте висохнути.
"""
```

**Step 2: Update conftest.py with fixtures**

```python
# tests/conftest.py
"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_ru_markdown():
    """Sample Russian markdown content."""
    from tests.fixtures.real_data import SAMPLE_RU_MARKDOWN
    return SAMPLE_RU_MARKDOWN


@pytest.fixture
def sample_uk_markdown():
    """Sample Ukrainian markdown content."""
    from tests.fixtures.real_data import SAMPLE_UK_MARKDOWN
    return SAMPLE_UK_MARKDOWN


@pytest.fixture
def real_ru_content_path():
    """Path to real RU content file (aktivnaya-pena)."""
    from tests.fixtures.real_data import get_ru_content_path
    path = get_ru_content_path("aktivnaya-pena")
    if not path.exists():
        pytest.skip(f"Real data not available: {path}")
    return path


@pytest.fixture
def real_uk_content_path():
    """Path to real UK content file (aktivnaya-pena)."""
    from tests.fixtures.real_data import get_uk_content_path
    path = get_uk_content_path("aktivnaya-pena")
    if not path.exists():
        pytest.skip(f"Real data not available: {path}")
    return path
```

**Step 3: Commit**

```bash
mkdir -p tests/fixtures
git add tests/fixtures/real_data.py tests/conftest.py
git commit -m "test: add real data fixtures for smoke tests

- Create tests/fixtures/real_data.py with sample content
- Add pytest fixtures for real category data
- Support for both RU and UK content

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 1: text_utils.py (SSOT)

### Task 1: Create text_utils.py with stopwords

**Files:**
- Create: `scripts/text_utils.py`
- Test: `tests/unit/test_text_utils.py`

**Step 1: Write the failing test for stopwords**

```python
# tests/unit/test_text_utils.py
"""Tests for text_utils.py — SSOT for text processing."""

import pytest


def test_get_stopwords_ru_returns_frozenset():
    """get_stopwords('ru') returns frozenset with Russian stopwords."""
    from scripts.text_utils import get_stopwords

    stopwords = get_stopwords("ru")
    assert isinstance(stopwords, frozenset)
    assert "и" in stopwords
    assert "в" in stopwords
    assert len(stopwords) >= 50


def test_get_stopwords_uk_returns_frozenset():
    """get_stopwords('uk') returns frozenset with Ukrainian stopwords."""
    from scripts.text_utils import get_stopwords

    stopwords = get_stopwords("uk")
    assert isinstance(stopwords, frozenset)
    assert "і" in stopwords
    assert "та" in stopwords
    assert len(stopwords) >= 50
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_text_utils.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'scripts.text_utils'"

**Step 3: Write minimal implementation**

```python
# scripts/text_utils.py
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

# =============================================================================
# STOPWORDS (RU + UK)
# =============================================================================

STOPWORDS_RU: frozenset[str] = frozenset({
    "и", "в", "на", "с", "по", "для", "из", "к", "у", "о", "от", "за", "при",
    "не", "но", "а", "же", "то", "это", "как", "что", "так", "все", "он", "она",
    "они", "мы", "вы", "его", "её", "их", "ее", "или", "если", "только", "уже",
    "ещё", "еще", "бы", "ли", "до", "без", "под", "над", "между", "через",
    "после", "перед", "около", "более", "менее", "также", "тоже", "очень",
    "может", "можно", "нужно", "есть", "был", "была", "были", "будет",
    "который", "которая", "которое", "которые", "этот", "эта", "эти", "тот",
    "та", "те", "свой", "своя", "свои", "наш", "ваш", "сам", "самый", "весь",
    "вся", "всё", "каждый", "любой", "другой", "такой", "какой", "чтобы",
    "потому", "поэтому", "когда", "где", "куда", "откуда", "почему", "зачем",
    "сколько", "кто", "чего", "чему", "кого", "кому", "чем", "кем", "ним",
    "ней", "них", "ему", "ей", "им", "вам", "нам", "себя", "себе", "собой",
    "мне", "меня", "мной", "тебя", "тебе", "тобой",
})

STOPWORDS_UK: frozenset[str] = frozenset({
    "і", "в", "на", "з", "по", "для", "із", "до", "у", "о", "від", "за", "при",
    "не", "але", "а", "ж", "то", "це", "як", "що", "так", "все", "він", "вона",
    "вони", "ми", "ви", "його", "її", "їх", "або", "якщо", "тільки", "вже",
    "ще", "би", "чи", "без", "під", "над", "між", "через", "після", "перед",
    "біля", "більше", "менше", "також", "теж", "дуже", "може", "можна",
    "потрібно", "є", "був", "була", "були", "буде", "який", "яка", "яке",
    "які", "цей", "ця", "ці", "той", "та", "ті", "свій", "своя", "свої",
    "наш", "ваш", "сам", "самий", "весь", "вся", "кожен", "будь", "інший",
    "такий", "щоб", "тому", "коли", "де", "куди", "звідки", "чому", "навіщо",
    "скільки", "хто", "чого", "кого", "кому", "чим", "ким", "ним", "ній",
    "них", "йому", "їй", "їм", "вам", "нам", "себе", "собі", "собою", "мені",
    "мене", "мною", "тебе", "тобі", "тобою",
})


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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_text_utils.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/text_utils.py tests/unit/test_text_utils.py
git commit -m "feat(text_utils): add stopwords SSOT module

- Create scripts/text_utils.py with STOPWORDS_RU and STOPWORDS_UK
- Add get_stopwords() function for language selection
- Add tests for stopwords functionality

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 2: Add clean_markdown to text_utils

**Files:**
- Modify: `scripts/text_utils.py`
- Test: `tests/unit/test_text_utils.py`

**Step 1: Write the failing test**

```python
# Add to tests/unit/test_text_utils.py

def test_clean_markdown_removes_yaml_front_matter():
    """clean_markdown removes YAML front matter."""
    from scripts.text_utils import clean_markdown

    text = """---
title: Test
---

# Hello World
"""
    result = clean_markdown(text)
    assert "title" not in result
    assert "Hello World" in result


def test_clean_markdown_removes_headers_markup():
    """clean_markdown removes header markers but keeps text."""
    from scripts.text_utils import clean_markdown

    text = "# Header 1\n## Header 2\nSome text"
    result = clean_markdown(text)
    assert "#" not in result
    assert "Header 1" in result
    assert "Header 2" in result


def test_clean_markdown_removes_bold_italic():
    """clean_markdown removes bold/italic markers."""
    from scripts.text_utils import clean_markdown

    text = "**bold** and *italic* text"
    result = clean_markdown(text)
    assert "**" not in result
    assert "*" not in result
    assert "bold" in result
    assert "italic" in result


def test_clean_markdown_removes_links():
    """clean_markdown removes link syntax but keeps text."""
    from scripts.text_utils import clean_markdown

    text = "Click [here](https://example.com) for more"
    result = clean_markdown(text)
    assert "[" not in result
    assert "](" not in result
    assert "here" in result
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_text_utils.py::test_clean_markdown_removes_yaml_front_matter -v`
Expected: FAIL with "cannot import name 'clean_markdown'"

**Step 3: Write implementation**

```python
# Add to scripts/text_utils.py after get_stopwords

import re

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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_text_utils.py -v -k clean_markdown`
Expected: PASS (all 4 tests)

**Step 5: Commit**

```bash
git add scripts/text_utils.py tests/unit/test_text_utils.py
git commit -m "feat(text_utils): add clean_markdown SSOT

- Add clean_markdown() for markdown removal
- Add normalize_text() alias for backwards compat
- Tests for YAML, headers, bold/italic, links removal

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 3: Add extract_h1, extract_h2s, extract_intro

**Files:**
- Modify: `scripts/text_utils.py`
- Test: `tests/unit/test_text_utils.py`

**Step 1: Write the failing tests**

```python
# Add to tests/unit/test_text_utils.py

def test_extract_h1_returns_heading():
    """extract_h1 returns H1 text without markup."""
    from scripts.text_utils import extract_h1

    text = "# Main Title\n\nSome content"
    result = extract_h1(text)
    assert result == "Main Title"


def test_extract_h1_returns_none_if_missing():
    """extract_h1 returns None if no H1."""
    from scripts.text_utils import extract_h1

    text = "## Only H2\n\nSome content"
    result = extract_h1(text)
    assert result is None


def test_extract_h2s_returns_list():
    """extract_h2s returns list of H2 headings."""
    from scripts.text_utils import extract_h2s

    text = "# Title\n## First\nText\n## Second\nMore text"
    result = extract_h2s(text)
    assert result == ["First", "Second"]


def test_extract_h2s_returns_empty_if_none():
    """extract_h2s returns empty list if no H2s."""
    from scripts.text_utils import extract_h2s

    text = "# Title\nNo H2 here"
    result = extract_h2s(text)
    assert result == []


def test_extract_intro_returns_first_paragraph():
    """extract_intro returns first paragraph after H1."""
    from scripts.text_utils import extract_intro

    text = "# Title\n\nThis is the intro paragraph.\n\n## Section"
    result = extract_intro(text)
    assert "This is the intro paragraph" in result


def test_extract_intro_max_lines():
    """extract_intro respects max_lines parameter."""
    from scripts.text_utils import extract_intro

    text = "# Title\n\nLine 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\n\n## Section"
    result = extract_intro(text, max_lines=3)
    assert "Line 1" in result
    assert "Line 3" in result
    assert "Line 6" not in result
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_text_utils.py::test_extract_h1_returns_heading -v`
Expected: FAIL with "cannot import name 'extract_h1'"

**Step 3: Write implementation**

```python
# Add to scripts/text_utils.py

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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_text_utils.py -v -k extract`
Expected: PASS (all 6 tests)

**Step 5: Commit**

```bash
git add scripts/text_utils.py tests/unit/test_text_utils.py
git commit -m "feat(text_utils): add extract_h1, extract_h2s, extract_intro

- extract_h1() returns H1 text or None
- extract_h2s() returns list of H2 texts
- extract_intro() returns intro paragraph with max_lines

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 4: Add count_words, count_chars_no_spaces, tokenize

**Files:**
- Modify: `scripts/text_utils.py`
- Test: `tests/unit/test_text_utils.py`

**Step 1: Write the failing tests**

```python
# Add to tests/unit/test_text_utils.py

def test_count_words_basic():
    """count_words returns word count."""
    from scripts.text_utils import count_words

    assert count_words("one two three") == 3
    assert count_words("  spaces  around  ") == 2


def test_count_words_empty():
    """count_words returns 0 for empty text."""
    from scripts.text_utils import count_words

    assert count_words("") == 0
    assert count_words("   ") == 0


def test_count_chars_no_spaces():
    """count_chars_no_spaces excludes whitespace."""
    from scripts.text_utils import count_chars_no_spaces

    assert count_chars_no_spaces("hello world") == 10  # no space
    assert count_chars_no_spaces("a b c") == 3


def test_tokenize_basic():
    """tokenize splits text into lowercase words."""
    from scripts.text_utils import tokenize

    result = tokenize("Hello World", lang="ru", remove_stopwords=False)
    assert result == ["hello", "world"]


def test_tokenize_removes_stopwords():
    """tokenize removes stopwords when requested."""
    from scripts.text_utils import tokenize

    result = tokenize("это и то", lang="ru", remove_stopwords=True)
    # "это", "и", "то" are all stopwords
    assert result == []


def test_tokenize_keeps_content_words():
    """tokenize keeps content words after stopword removal."""
    from scripts.text_utils import tokenize

    result = tokenize("купить активную пену для авто", lang="ru", remove_stopwords=True)
    assert "купить" in result
    assert "активную" in result
    assert "пену" in result
    # "для" should be removed as stopword
    assert "для" not in result
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_text_utils.py::test_count_words_basic -v`
Expected: FAIL with "cannot import name 'count_words'"

**Step 3: Write implementation**

```python
# Add to scripts/text_utils.py

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
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_text_utils.py -v -k "count or tokenize"`
Expected: PASS (all 6 tests)

**Step 5: Commit**

```bash
git add scripts/text_utils.py tests/unit/test_text_utils.py
git commit -m "feat(text_utils): add count_words, count_chars_no_spaces, tokenize

- count_words() for word counting
- count_chars_no_spaces() for char counting without whitespace
- tokenize() for word splitting with optional stopword removal

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 2: Migrate imports

### Task 5: Migrate seo_utils.py to use text_utils

**Files:**
- Modify: `scripts/seo_utils.py`
- Test: `tests/unit/test_seo_utils.py`

**Step 1: Run existing tests to verify baseline**

Run: `pytest tests/unit/test_seo_utils.py -v`
Expected: PASS (all tests green before changes)

**Step 2: Update seo_utils.py imports**

Replace the local `clean_markdown`, `normalize_text`, `count_words`, `count_chars_no_spaces` with imports from text_utils:

```python
# At the top of seo_utils.py, add:
from scripts.text_utils import (
    clean_markdown,
    count_chars_no_spaces,
    count_words,
    normalize_text,
)

# Then DELETE the local implementations of these functions
# (lines ~351-468 in current file)
```

**Step 3: Run tests to verify no regression**

Run: `pytest tests/unit/test_seo_utils.py -v`
Expected: PASS (all tests still green)

**Step 4: Run full test suite**

Run: `pytest tests/unit/ -v --tb=short`
Expected: PASS (no regressions)

**Step 5: Commit**

```bash
git add scripts/seo_utils.py
git commit -m "refactor(seo_utils): use text_utils SSOT

- Import clean_markdown, normalize_text from text_utils
- Import count_words, count_chars_no_spaces from text_utils
- Remove local implementations (DRY)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 6: Migrate check_keyword_density.py to use text_utils

**Files:**
- Modify: `scripts/check_keyword_density.py`
- Test: `tests/unit/test_check_keyword_density.py`

**Step 1: Run existing tests to verify baseline**

Run: `pytest tests/unit/test_check_keyword_density.py -v`
Expected: PASS

**Step 2: Update check_keyword_density.py imports**

```python
# At top of check_keyword_density.py, replace local STOPWORDS and clean_markdown:

from scripts.text_utils import (
    clean_markdown,
    get_stopwords,
    tokenize,
)

# DELETE:
# - STOPWORDS_RU definition (~lines 77-199)
# - STOPWORDS_UK definition (~lines 202-317)
# - get_stopwords() function (~lines 320-324)
# - clean_markdown() function (~lines 357-392)
# - tokenize() function (~lines 395-400)
# - remove_stopwords() function (~lines 403-406)

# Update analyze_text() to use imported tokenize:
# Change: words = remove_stopwords(all_words, lang)
# To: words = tokenize(clean_text, lang=lang, remove_stopwords=True)
#     all_words = tokenize(clean_text, lang=lang, remove_stopwords=False)
```

**Step 3: Run tests to verify no regression**

Run: `pytest tests/unit/test_check_keyword_density.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add scripts/check_keyword_density.py
git commit -m "refactor(check_keyword_density): use text_utils SSOT

- Import clean_markdown, get_stopwords, tokenize from text_utils
- Remove local STOPWORDS_RU, STOPWORDS_UK definitions
- Remove local clean_markdown, tokenize, remove_stopwords

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 7: Migrate validate_content.py to use text_utils

**Files:**
- Modify: `scripts/validate_content.py`
- Test: `tests/unit/test_validate_content.py`

**Step 1: Run existing tests to verify baseline**

Run: `pytest tests/unit/test_validate_content.py -v`
Expected: PASS

**Step 2: Update validate_content.py imports**

```python
# Update imports at top - replace:
from seo_utils import (
    clean_markdown,
    count_chars_no_spaces,
    count_words,
    get_adaptive_requirements,
)

# With:
from scripts.text_utils import (
    clean_markdown,
    count_chars_no_spaces,
    count_words,
    extract_h1,
    extract_h2s,
    extract_intro,
)
from seo_utils import get_adaptive_requirements

# DELETE local extract_h1, extract_h2s, extract_intro (~lines 113-142)
```

**Step 3: Run tests to verify no regression**

Run: `pytest tests/unit/test_validate_content.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add scripts/validate_content.py
git commit -m "refactor(validate_content): use text_utils SSOT

- Import extract_h1, extract_h2s, extract_intro from text_utils
- Remove local implementations (DRY)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 8: Migrate check_seo_structure.py to use text_utils

**Files:**
- Modify: `scripts/check_seo_structure.py`

**Step 1: Update check_seo_structure.py imports**

```python
# At top, add:
from scripts.text_utils import extract_h1, extract_h2s, extract_intro

# The script uses get_word_stems from MorphAnalyzer — keep that.
# Remove local normalize_keyword if similar function exists in text_utils.
```

**Step 2: Run check_seo_structure.py manually**

Run: `python3 scripts/check_seo_structure.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md "активная пена"`
Expected: Output shows SEO structure check results

**Step 3: Commit**

```bash
git add scripts/check_seo_structure.py
git commit -m "refactor(check_seo_structure): use text_utils imports

- Import from text_utils where applicable

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 3: UK Support in validate_meta.py

### Task 9: Add UK patterns to validate_meta.py

**Files:**
- Modify: `scripts/validate_meta.py`
- Test: `tests/unit/test_validate_meta.py`

**Step 1: Write the failing test**

```python
# Add to tests/unit/test_validate_meta.py

def test_validate_meta_uk_language():
    """validate_meta works with --lang uk."""
    from scripts.validate_meta import validate_meta_file
    import tempfile
    import json
    import os

    # Create temp UK meta file
    meta = {
        "slug": "test",
        "language": "uk",
        "meta": {
            "title": "Активна піна для безконтактної мийки - купити в Україні",
            "description": "Активна піна для авто. Вибір, застосування, ціни. Безкоштовна доставка."
        },
        "h1": "Активна піна для безконтактної мийки"
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='_meta.json', delete=False, encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False)
        temp_path = f.name

    try:
        result = validate_meta_file(temp_path, lang="uk")
        assert result is not None
        assert "errors" not in result or len(result.get("errors", [])) == 0
    finally:
        os.unlink(temp_path)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_validate_meta.py::test_validate_meta_uk_language -v`
Expected: FAIL (function doesn't support lang parameter yet)

**Step 3: Add UK support to validate_meta.py**

```python
# Add UK patterns near the top of validate_meta.py

PRODUCER_PATTERNS_RU = [r"от производителя", r"производителя ultimate"]
PRODUCER_PATTERNS_UK = [r"від виробника", r"виробника ultimate"]

WHOLESALE_PATTERNS_RU = [r"опт\b", r"розница", r"оптом"]
WHOLESALE_PATTERNS_UK = [r"опт\b", r"роздріб", r"оптом"]

def get_validation_patterns(lang: str = "ru") -> dict:
    """Get validation patterns for language."""
    if lang == "uk":
        return {
            "producer": PRODUCER_PATTERNS_UK,
            "wholesale": WHOLESALE_PATTERNS_UK,
        }
    return {
        "producer": PRODUCER_PATTERNS_RU,
        "wholesale": WHOLESALE_PATTERNS_RU,
    }

# Update validate_meta_file signature:
def validate_meta_file(file_path: str, lang: str = "ru") -> dict:
    ...

# Update CLI to accept --lang parameter
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_validate_meta.py::test_validate_meta_uk_language -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `pytest tests/unit/test_validate_meta.py -v`
Expected: PASS

**Step 6: Commit**

```bash
git add scripts/validate_meta.py tests/unit/test_validate_meta.py
git commit -m "feat(validate_meta): add UK language support

- Add PRODUCER_PATTERNS_UK, WHOLESALE_PATTERNS_UK
- Add get_validation_patterns(lang) function
- Update validate_meta_file with lang parameter
- Add --lang CLI argument

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 4: Rename Scripts

### Task 10: Rename check_seo_structure.py to validate_seo.py

**Files:**
- Rename: `scripts/check_seo_structure.py` → `scripts/validate_seo.py`
- Update: `.claude/skills/*/skill.md` (any references)

**Step 1: Rename the file**

```bash
git mv scripts/check_seo_structure.py scripts/validate_seo.py
```

**Step 2: Update any imports in other scripts**

Search and replace `from check_seo_structure import` → `from validate_seo import`
Search and replace `import check_seo_structure` → `import validate_seo`

**Step 3: Verify the script works**

Run: `python3 scripts/validate_seo.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md "активная пена"`
Expected: Same output as before

**Step 4: Commit**

```bash
git add -A
git commit -m "refactor: rename check_seo_structure.py to validate_seo.py

- Consistent naming with other validators

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 11: Rename check_keyword_density.py to validate_density.py

**Files:**
- Rename: `scripts/check_keyword_density.py` → `scripts/validate_density.py`
- Update: `tests/unit/test_check_keyword_density.py` → `tests/unit/test_validate_density.py`

**Step 1: Rename files**

```bash
git mv scripts/check_keyword_density.py scripts/validate_density.py
git mv tests/unit/test_check_keyword_density.py tests/unit/test_validate_density.py
```

**Step 2: Update imports in test file**

Update `from check_keyword_density import` → `from validate_density import`

**Step 3: Run tests**

Run: `pytest tests/unit/test_validate_density.py -v`
Expected: PASS

**Step 4: Commit**

```bash
git add -A
git commit -m "refactor: rename check_keyword_density.py to validate_density.py

- Consistent naming with other validators
- Update test file name

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 5: Archive Old Scripts

### Task 12: Create archive directory and move old scripts

**Files:**
- Create: `scripts/archive/`
- Move: `scripts/validate_uk.py` → `scripts/archive/`

**Step 1: Create archive directory**

```bash
mkdir -p scripts/archive
```

**Step 2: Move validate_uk.py to archive**

```bash
git mv scripts/validate_uk.py scripts/archive/validate_uk.py
```

**Step 3: Create archive README**

```bash
cat > scripts/archive/README.md << 'EOF'
# Archived Scripts

These scripts have been superseded by unified validators with `--lang` support.

## Archived Files

| File | Replaced By |
|------|-------------|
| `validate_uk.py` | `validate_meta.py --lang uk` |

## Usage

Do not use scripts from this directory. Use the main scripts with appropriate `--lang` parameter.
EOF
```

**Step 4: Commit**

```bash
git add -A
git commit -m "chore: archive validate_uk.py (replaced by --lang uk)

- Create scripts/archive/ directory
- Move validate_uk.py to archive
- Add archive README

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 6: Update CLAUDE.md

### Task 13: Update CLAUDE.md with new commands

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Update the Commands section**

```markdown
## Команды

```bash
# Тесты
pytest                        # Все
pytest -k "test_meta"         # По имени

# Линтинг
ruff check scripts/
ruff format scripts/

# Валидация (Unified)
python3 scripts/validate_meta.py <path> [--lang ru|uk]
python3 scripts/validate_meta.py --all [--lang ru|uk]
python3 scripts/validate_content.py <path> "<keyword>" [--lang ru|uk]
python3 scripts/validate_seo.py <path> "<keyword>" [--lang ru|uk]
python3 scripts/validate_density.py <path> [--lang ru|uk]

# Аудит
python3 scripts/audit_keyword_consistency.py
python3 scripts/check_h1_sync.py
```
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(CLAUDE.md): update commands for renamed validators

- Add --lang parameter documentation
- Update script names (validate_seo, validate_density)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 7: Smoke Tests and Real Data Tests (80% Coverage)

### Task 14: Add smoke tests for text_utils

**Files:**
- Create: `tests/smoke/test_text_utils_smoke.py`

**Step 1: Write smoke tests with real data**

```python
# tests/smoke/test_text_utils_smoke.py
"""Smoke tests for text_utils on real category data."""

import pytest
from pathlib import Path


class TestTextUtilsSmoke:
    """Smoke tests using real category content."""

    @pytest.fixture
    def real_ru_content(self):
        """Load real RU content file."""
        path = Path("categories/aktivnaya-pena/content/aktivnaya-pena_ru.md")
        if not path.exists():
            pytest.skip("Real data not available")
        return path.read_text(encoding="utf-8")

    @pytest.fixture
    def real_uk_content(self):
        """Load real UK content file."""
        path = Path("uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md")
        if not path.exists():
            pytest.skip("Real data not available")
        return path.read_text(encoding="utf-8")

    def test_clean_markdown_on_real_ru_content(self, real_ru_content):
        """clean_markdown works on real RU content."""
        from scripts.text_utils import clean_markdown

        result = clean_markdown(real_ru_content)

        # Should produce non-empty text
        assert len(result) > 100
        # Should remove markdown markers
        assert "##" not in result
        assert "**" not in result
        # Should preserve content words
        assert "пен" in result.lower() or "активн" in result.lower()

    def test_clean_markdown_on_real_uk_content(self, real_uk_content):
        """clean_markdown works on real UK content."""
        from scripts.text_utils import clean_markdown

        result = clean_markdown(real_uk_content)

        assert len(result) > 100
        assert "##" not in result
        assert "піна" in result.lower() or "активн" in result.lower()

    def test_extract_h1_on_real_content(self, real_ru_content):
        """extract_h1 finds H1 in real content."""
        from scripts.text_utils import extract_h1

        h1 = extract_h1(real_ru_content)

        assert h1 is not None
        assert len(h1) > 5
        # H1 should contain main keyword
        assert "пен" in h1.lower() or "активн" in h1.lower()

    def test_extract_h2s_on_real_content(self, real_ru_content):
        """extract_h2s finds H2s in real content."""
        from scripts.text_utils import extract_h2s

        h2s = extract_h2s(real_ru_content)

        # Content should have multiple H2s
        assert len(h2s) >= 2
        # H2s should be meaningful text
        for h2 in h2s:
            assert len(h2) > 3

    def test_extract_intro_on_real_content(self, real_ru_content):
        """extract_intro finds intro in real content."""
        from scripts.text_utils import extract_intro

        intro = extract_intro(real_ru_content)

        assert len(intro) > 50
        # Intro should contain keyword
        assert "пен" in intro.lower() or "активн" in intro.lower()

    def test_tokenize_ru_on_real_content(self, real_ru_content):
        """tokenize produces tokens from real RU content."""
        from scripts.text_utils import clean_markdown, tokenize

        clean = clean_markdown(real_ru_content)
        tokens = tokenize(clean, lang="ru", remove_stopwords=True)

        # Should have meaningful tokens
        assert len(tokens) > 50
        # Should not contain stopwords
        assert "и" not in tokens
        assert "в" not in tokens
        # Should contain content words
        assert any("пен" in t for t in tokens) or any("активн" in t for t in tokens)

    def test_tokenize_uk_on_real_content(self, real_uk_content):
        """tokenize produces tokens from real UK content."""
        from scripts.text_utils import clean_markdown, tokenize

        clean = clean_markdown(real_uk_content)
        tokens = tokenize(clean, lang="uk", remove_stopwords=True)

        assert len(tokens) > 50
        # Should not contain UK stopwords
        assert "і" not in tokens
        assert "та" not in tokens

    def test_count_words_on_real_content(self, real_ru_content):
        """count_words returns reasonable count for real content."""
        from scripts.text_utils import clean_markdown, count_words

        clean = clean_markdown(real_ru_content)
        words = count_words(clean)

        # Real content should have substantial word count
        assert words >= 150
        assert words <= 2000  # Not unreasonably large
```

**Step 2: Run smoke tests**

Run: `pytest tests/smoke/test_text_utils_smoke.py -v`
Expected: PASS (all tests)

**Step 3: Commit**

```bash
mkdir -p tests/smoke
git add tests/smoke/test_text_utils_smoke.py
git commit -m "test: add smoke tests for text_utils on real data

- Test clean_markdown on real RU/UK content
- Test extract_h1, extract_h2s, extract_intro
- Test tokenize with stopwords removal
- Test count_words with reasonable bounds

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 15: Add smoke tests for validators

**Files:**
- Create: `tests/smoke/test_validators_smoke.py`

**Step 1: Write smoke tests for validators**

```python
# tests/smoke/test_validators_smoke.py
"""Smoke tests for validators on real category data."""

import pytest
from pathlib import Path


SAMPLE_CATEGORIES = [
    "aktivnaya-pena",
    "polirovalnye-pasty",
    "ochistiteli-stekol",
]


class TestValidateMetaSmoke:
    """Smoke tests for validate_meta on real data."""

    @pytest.mark.parametrize("slug", SAMPLE_CATEGORIES)
    def test_validate_meta_ru_real_file(self, slug):
        """validate_meta_file works on real RU meta."""
        meta_path = Path(f"categories/{slug}/meta/{slug}_meta.json")
        if not meta_path.exists():
            pytest.skip(f"Meta file not found: {meta_path}")

        from scripts.validate_meta import validate_meta_file

        result = validate_meta_file(str(meta_path), lang="ru")

        # Should return dict with results
        assert isinstance(result, dict)
        # Should have status
        assert "status" in result or "passed" in result or "errors" in result

    def test_validate_meta_uk_real_file(self):
        """validate_meta_file works on real UK meta."""
        meta_path = Path("uk/categories/aktivnaya-pena/meta/aktivnaya-pena_meta.json")
        if not meta_path.exists():
            pytest.skip(f"UK meta file not found: {meta_path}")

        from scripts.validate_meta import validate_meta_file

        result = validate_meta_file(str(meta_path), lang="uk")

        assert isinstance(result, dict)


class TestValidateContentSmoke:
    """Smoke tests for validate_content on real data."""

    def test_validate_content_ru_real_file(self):
        """validate_content works on real RU content."""
        content_path = Path("categories/aktivnaya-pena/content/aktivnaya-pena_ru.md")
        if not content_path.exists():
            pytest.skip(f"Content file not found: {content_path}")

        from scripts.validate_content import validate_content

        result = validate_content(
            str(content_path),
            primary_keyword="активная пена",
            mode="seo",
            lang="ru",
        )

        assert isinstance(result, dict)
        assert "checks" in result or "error" not in result
        assert "summary" in result

    def test_validate_content_uk_real_file(self):
        """validate_content works on real UK content."""
        content_path = Path("uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md")
        if not content_path.exists():
            pytest.skip(f"UK content file not found: {content_path}")

        from scripts.validate_content import validate_content

        result = validate_content(
            str(content_path),
            primary_keyword="активна піна",
            mode="seo",
            lang="uk",
        )

        assert isinstance(result, dict)
        assert "summary" in result


class TestValidateSeoSmoke:
    """Smoke tests for validate_seo (check_seo_structure) on real data."""

    def test_check_seo_structure_ru_real_file(self):
        """check_seo_structure works on real RU content."""
        content_path = Path("categories/aktivnaya-pena/content/aktivnaya-pena_ru.md")
        if not content_path.exists():
            pytest.skip(f"Content file not found: {content_path}")

        from scripts.check_seo_structure import check_seo_structure

        status, results = check_seo_structure(str(content_path), "активная пена")

        assert status in ("PASS", "WARN", "FAIL")
        assert "intro" in results
        assert "h2" in results
        assert "frequency" in results

    def test_check_seo_structure_uk_real_file(self):
        """check_seo_structure works on real UK content."""
        content_path = Path("uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md")
        if not content_path.exists():
            pytest.skip(f"UK content file not found: {content_path}")

        from scripts.check_seo_structure import check_seo_structure

        status, results = check_seo_structure(str(content_path), "активна піна")

        assert status in ("PASS", "WARN", "FAIL")


class TestValidateDensitySmoke:
    """Smoke tests for validate_density (check_keyword_density) on real data."""

    def test_analyze_text_ru_real_file(self):
        """analyze_text works on real RU content."""
        content_path = Path("categories/aktivnaya-pena/content/aktivnaya-pena_ru.md")
        if not content_path.exists():
            pytest.skip(f"Content file not found: {content_path}")

        from scripts.check_keyword_density import analyze_text

        text = content_path.read_text(encoding="utf-8")
        result = analyze_text(text, top_n=20, lang="ru")

        assert "total_words" in result
        assert result["total_words"] > 100
        assert "word_frequencies" in result
        assert "stem_frequencies" in result

    def test_analyze_text_uk_real_file(self):
        """analyze_text works on real UK content."""
        content_path = Path("uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md")
        if not content_path.exists():
            pytest.skip(f"UK content file not found: {content_path}")

        from scripts.check_keyword_density import analyze_text

        text = content_path.read_text(encoding="utf-8")
        result = analyze_text(text, top_n=20, lang="uk")

        assert "total_words" in result
        assert result["total_words"] > 100
```

**Step 2: Run smoke tests**

Run: `pytest tests/smoke/test_validators_smoke.py -v`
Expected: PASS

**Step 3: Commit**

```bash
git add tests/smoke/test_validators_smoke.py
git commit -m "test: add smoke tests for validators on real data

- Test validate_meta on real RU/UK meta files
- Test validate_content on real RU/UK content
- Test check_seo_structure on real content
- Test analyze_text (density) on real content

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 16: Add integration tests for full pipeline

**Files:**
- Create: `tests/integration/test_validation_pipeline.py`

**Step 1: Write integration tests**

```python
# tests/integration/test_validation_pipeline.py
"""Integration tests for full validation pipeline."""

import pytest
from pathlib import Path


class TestFullValidationPipeline:
    """Test complete validation workflow on real categories."""

    @pytest.fixture
    def category_slug(self):
        return "aktivnaya-pena"

    def test_full_ru_validation_pipeline(self, category_slug):
        """Full RU validation pipeline works end-to-end."""
        # Paths
        meta_path = Path(f"categories/{category_slug}/meta/{category_slug}_meta.json")
        content_path = Path(f"categories/{category_slug}/content/{category_slug}_ru.md")
        clean_path = Path(f"categories/{category_slug}/data/{category_slug}_clean.json")

        if not all(p.exists() for p in [meta_path, content_path, clean_path]):
            pytest.skip("Category data not complete")

        import json

        # 1. Load clean.json for primary keyword
        clean_data = json.loads(clean_path.read_text(encoding="utf-8"))
        keywords = clean_data.get("keywords", [])
        primary_keyword = keywords[0]["keyword"] if keywords else "активная пена"

        # 2. Validate meta
        from scripts.validate_meta import validate_meta_file
        meta_result = validate_meta_file(str(meta_path), lang="ru")
        assert meta_result is not None

        # 3. Validate content
        from scripts.validate_content import validate_content
        content_result = validate_content(
            str(content_path),
            primary_keyword=primary_keyword,
            mode="seo",
            lang="ru",
        )
        assert "summary" in content_result

        # 4. Check SEO structure
        from scripts.check_seo_structure import check_seo_structure
        seo_status, seo_result = check_seo_structure(str(content_path), primary_keyword)
        assert seo_status in ("PASS", "WARN", "FAIL")

        # 5. Check density
        from scripts.check_keyword_density import analyze_text
        text = content_path.read_text(encoding="utf-8")
        density_result = analyze_text(text, lang="ru")
        assert density_result["total_words"] > 0

        # Integration assertion: pipeline completes without errors
        print(f"\nPipeline results for {category_slug}:")
        print(f"  Meta: {meta_result.get('status', 'N/A')}")
        print(f"  Content: {content_result['summary']['overall']}")
        print(f"  SEO: {seo_status}")
        print(f"  Density: {density_result['total_words']} words")

    def test_full_uk_validation_pipeline(self, category_slug):
        """Full UK validation pipeline works end-to-end."""
        # Paths
        meta_path = Path(f"uk/categories/{category_slug}/meta/{category_slug}_meta.json")
        content_path = Path(f"uk/categories/{category_slug}/content/{category_slug}_uk.md")
        clean_path = Path(f"uk/categories/{category_slug}/data/{category_slug}_clean.json")

        if not all(p.exists() for p in [meta_path, content_path, clean_path]):
            pytest.skip("UK category data not complete")

        import json

        # 1. Load clean.json for primary keyword
        clean_data = json.loads(clean_path.read_text(encoding="utf-8"))
        keywords = clean_data.get("keywords", [])
        primary_keyword = keywords[0]["keyword"] if keywords else "активна піна"

        # 2. Validate meta
        from scripts.validate_meta import validate_meta_file
        meta_result = validate_meta_file(str(meta_path), lang="uk")
        assert meta_result is not None

        # 3. Validate content
        from scripts.validate_content import validate_content
        content_result = validate_content(
            str(content_path),
            primary_keyword=primary_keyword,
            mode="seo",
            lang="uk",
        )
        assert "summary" in content_result

        # 4. Check SEO structure
        from scripts.check_seo_structure import check_seo_structure
        seo_status, seo_result = check_seo_structure(str(content_path), primary_keyword)
        assert seo_status in ("PASS", "WARN", "FAIL")

        # Integration assertion
        print(f"\nUK Pipeline results for {category_slug}:")
        print(f"  Meta: {meta_result.get('status', 'N/A')}")
        print(f"  Content: {content_result['summary']['overall']}")
        print(f"  SEO: {seo_status}")
```

**Step 2: Run integration tests**

Run: `pytest tests/integration/test_validation_pipeline.py -v`
Expected: PASS

**Step 3: Commit**

```bash
mkdir -p tests/integration
git add tests/integration/test_validation_pipeline.py
git commit -m "test: add integration tests for full validation pipeline

- Test complete RU validation workflow
- Test complete UK validation workflow
- Verify all validators work together

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 17: Verify 80% test coverage

**Files:**
- None (verification only)

**Step 1: Install coverage tool**

Run: `pip install pytest-cov`

**Step 2: Run tests with coverage**

Run: `pytest tests/ --cov=scripts --cov-report=term-missing --cov-report=html`
Expected: Coverage report showing ≥80% for text_utils.py and validators

**Step 3: Check coverage report**

```bash
# View coverage for specific modules
pytest tests/ --cov=scripts.text_utils --cov=scripts.validate_meta --cov=scripts.validate_content --cov=scripts.check_seo_structure --cov=scripts.check_keyword_density --cov-report=term-missing
```

**Step 4: Add missing tests if coverage < 80%**

If coverage is below 80%, identify uncovered lines and add tests.

**Step 5: Commit coverage config**

```bash
# Add to pyproject.toml or setup.cfg if not exists
cat >> pyproject.toml << 'EOF'

[tool.coverage.run]
source = ["scripts"]
omit = ["scripts/archive/*", "scripts/*_test.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
EOF

git add pyproject.toml
git commit -m "chore: add coverage configuration (80% target)

- Configure pytest-cov for scripts/
- Exclude archive from coverage
- Set fail_under = 80%

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Summary

After completing all tasks:

1. **text_utils.py** — SSOT for text processing
2. **All validators** — use text_utils imports
3. **UK support** — via `--lang uk` parameter
4. **Consistent naming** — validate_*.py pattern
5. **Archive** — old scripts in scripts/archive/
6. **Tests** — smoke + integration + unit = 80% coverage

**Verification:**

```bash
# Run full test suite with coverage
pytest tests/ --cov=scripts --cov-report=term-missing -v

# Verify 80% coverage
pytest tests/ --cov=scripts --cov-fail-under=80

# Run only smoke tests
pytest tests/smoke/ -v

# Run only integration tests
pytest tests/integration/ -v

# Verify validators work
python3 scripts/validate_meta.py --all
python3 scripts/validate_meta.py --all --lang uk
python3 scripts/validate_seo.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md "активная пена"
python3 scripts/validate_density.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md
```
