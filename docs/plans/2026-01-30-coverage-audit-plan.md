# Coverage Audit Tool — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать инструмент batch-аудита покрытия ключевых слов с детальной диагностикой (EXACT/NORM/LEMMA/SYNONYM/TOKENIZATION/PARTIAL/ABSENT).

**Architecture:** Новый модуль `coverage_matcher.py` с классом `MatchResult` и функциями матчинга. CLI-скрипт `audit_coverage.py` для batch/single режимов. Использует существующий `MorphAnalyzer` из `keyword_utils.py`.

**Tech Stack:** Python 3.11+, pymorphy3/Snowball (существующий), pytest.

**Design Doc:** `docs/plans/2026-01-30-coverage-audit-design.md`

---

## Критические изменения к плану

### 1. Пути RU-категорий — иерархическая структура
RU-категории лежат **вложенно** (не плоско):
```
categories/aksessuary/gubki-i-varezhki/data/gubki-i-varezhki_clean.json
categories/moyka-i-eksterer/aktivnaya-pena/data/aktivnaya-pena_clean.json
```

**Решение:** `load_category_data()` и `get_all_slugs()` для RU должны искать рекурсивно по дереву папок с `find` по slug.

### 2. Оптимизация производительности
`check_keyword()` на каждом ключе заново лемматизирует весь текст. На 100 текстов × 100 ключей = 10000 вызовов `morph.normalize_phrase(text)`.

**Решение:** В `audit_category()` однократно подготовить:
- `norm_text = normalize_text(text)`
- `text_lemmas = morph.normalize_phrase(text)`

Передавать в `check_keyword()` как `prepared_text: PreparedText`.

### 3. TOKENIZATION_PATTERNS — сузить паттерн `\w+-\w+`
Паттерн `\w+-\w+` ловит все дефисные слова (авто-хімія, пред-мийка), не только проблемные.

**Решение:** Заменить на более точные:
- `[a-zA-Z]+-[a-zA-Z]+` — латиница (wash-and-wax, pre-wash)
- `\d+-\w+` или `\w+-\d+` — числа в дефисных словах

### 4. SYNONYM сравнение через нормализацию
`syn["variant_of"] == keyword` — точное сравнение. При расхождении регистра/апострофов не сработает.

**Решение:** Сравнивать `normalize_text(syn["variant_of"]) == normalize_text(keyword)`.

### 5. Коммиты — опционально
Многочисленные коммиты после каждого Task избыточны для утилиты.

**Решение:** Убираем промежуточные коммиты. Один финальный коммит после Task 8.

---

## Task 1: MatchResult dataclass

**Files:**
- Create: `scripts/coverage_matcher.py`
- Test: `tests/unit/test_coverage_matcher.py`

**Step 1: Write failing test**

```python
# tests/unit/test_coverage_matcher.py
"""Unit tests for coverage_matcher.py"""

import pytest
from scripts.coverage_matcher import MatchResult


class TestMatchResult:
    def test_covered_exact(self):
        r = MatchResult(status="EXACT", covered=True)
        assert r.covered is True
        assert r.status == "EXACT"

    def test_not_covered_absent(self):
        r = MatchResult(status="ABSENT", covered=False)
        assert r.covered is False

    def test_synonym_with_details(self):
        r = MatchResult(
            status="SYNONYM",
            covered=True,
            covered_by="засоби для чорніння шин",
            syn_match_method="LEMMA",
        )
        assert r.covered_by == "засоби для чорніння шин"
        assert r.syn_match_method == "LEMMA"

    def test_partial_with_coverage(self):
        r = MatchResult(
            status="PARTIAL",
            covered=False,
            lemma_coverage=0.67,
            reason="67% lemmas found",
        )
        assert r.lemma_coverage == 0.67
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_coverage_matcher.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'scripts.coverage_matcher'`

**Step 3: Write minimal implementation**

```python
# scripts/coverage_matcher.py
"""
coverage_matcher.py — Keyword Coverage Matching with Detailed Diagnostics

Статусы COVERED: EXACT → NORM → LEMMA → SYNONYM
Статусы NOT COVERED: TOKENIZATION → PARTIAL → ABSENT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

MatchStatus = Literal[
    "EXACT", "NORM", "LEMMA", "SYNONYM",  # covered
    "TOKENIZATION", "PARTIAL", "ABSENT",  # not covered
]


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
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/unit/test_coverage_matcher.py::TestMatchResult -v
```
Expected: PASS

---

## Task 2: normalize_text function

**Files:**
- Modify: `scripts/coverage_matcher.py`
- Test: `tests/unit/test_coverage_matcher.py`

**Step 1: Write failing test**

```python
# Add to tests/unit/test_coverage_matcher.py
from scripts.coverage_matcher import normalize_text


class TestNormalizeText:
    def test_casefold(self):
        assert normalize_text("Активна Піна") == "активна піна"

    def test_apostrophes_unified(self):
        # Different apostrophes → single '
        assert normalize_text("зовнішнього") == normalize_text("зовнішнього")
        assert "'" not in normalize_text("п'ять")  or normalize_text("п'ять") == "п'ять"

    def test_yo_to_e(self):
        assert normalize_text("щётка") == "щетка"

    def test_preserves_hyphens(self):
        assert "-" in normalize_text("pH-нейтральний")

    def test_preserves_digits(self):
        assert "1:10" in normalize_text("розведення 1:10")
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_coverage_matcher.py::TestNormalizeText -v
```
Expected: FAIL — `ImportError: cannot import name 'normalize_text'`

**Step 3: Write implementation**

```python
# Add to scripts/coverage_matcher.py
import unicodedata


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
```

**Step 4: Run test**

```bash
pytest tests/unit/test_coverage_matcher.py::TestNormalizeText -v
```
Expected: PASS

---

## Task 3: has_tokenization_markers function

**Files:**
- Modify: `scripts/coverage_matcher.py`
- Test: `tests/unit/test_coverage_matcher.py`

**Step 1: Write failing test**

```python
# Add to tests/unit/test_coverage_matcher.py
from scripts.coverage_matcher import has_tokenization_markers


class TestTokenizationMarkers:
    def test_ph_marker(self):
        assert has_tokenization_markers("pH-нейтральний") is True
        assert has_tokenization_markers("pH 7") is True

    def test_ratio_marker(self):
        assert has_tokenization_markers("розведення 1:10") is True
        assert has_tokenization_markers("1:50") is True

    def test_range_marker(self):
        assert has_tokenization_markers("5-10 хвилин") is True

    def test_hyphenated_word(self):
        assert has_tokenization_markers("wash-and-wax") is True

    def test_units(self):
        assert has_tokenization_markers("100 мл") is True
        assert has_tokenization_markers("150 бар") is True

    def test_no_markers(self):
        assert has_tokenization_markers("активна піна") is False
        assert has_tokenization_markers("чорніння гуми") is False
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_coverage_matcher.py::TestTokenizationMarkers -v
```
Expected: FAIL

**Step 3: Write implementation**

```python
# Add to scripts/coverage_matcher.py
import re

# Более точные паттерны — только реально проблемные токены
TOKENIZATION_PATTERNS = [
    r"pH[-\s]?\d*",             # pH, pH-7, pH 7, pH-нейтральний
    r"\d+:\d+",                 # 1:10, 1:50 (ratios)
    r"\d+-\d+",                 # 5-10, 100-150 (ranges)
    r"[a-zA-Z]+-[a-zA-Z]+",     # wash-and-wax, pre-wash (латиница с дефисом)
    r"\d+-[a-zA-Zа-яіїєґА-ЯІЇЄҐ]+",  # 2-компонентный
    r"[a-zA-Zа-яіїєґА-ЯІЇЄҐ]+-\d+",  # ISO-9001
    r"RTU",                     # Ready-To-Use
    r"\d+\s*(мл|л|г|бар|bar)",  # 100 мл, 150 бар
]


def has_tokenization_markers(keyword: str) -> bool:
    """Check if keyword contains tokens that may cause matching issues."""
    for pattern in TOKENIZATION_PATTERNS:
        if re.search(pattern, keyword, re.IGNORECASE):
            return True
    return False
```

**Step 4: Run test**

```bash
pytest tests/unit/test_coverage_matcher.py::TestTokenizationMarkers -v
```
Expected: PASS

---

## Task 4: check_keyword function + PreparedText (core logic)

**Files:**
- Modify: `scripts/coverage_matcher.py`
- Test: `tests/unit/test_coverage_matcher.py`

**Step 1: Write failing tests**

```python
# Add to tests/unit/test_coverage_matcher.py
from scripts.coverage_matcher import check_keyword, PreparedText


class TestCheckKeyword:
    def test_exact_match(self):
        prepared = PreparedText("Купуйте активна піна для авто", "uk")
        r = check_keyword("активна піна", prepared, [])
        assert r.status == "EXACT"
        assert r.covered is True

    def test_norm_match_case(self):
        prepared = PreparedText("купуйте активна піна", "uk")
        r = check_keyword("Активна Піна", prepared, [])
        assert r.status == "NORM"
        assert r.covered is True

    def test_lemma_match_uk(self):
        prepared = PreparedText("засоби для чорніння гуми тут", "uk")
        r = check_keyword("чорніння гуми", prepared, [])
        assert r.status in ("EXACT", "LEMMA")
        assert r.covered is True

    def test_synonym_match(self):
        synonyms = [
            {"keyword": "засоби для чорніння шин", "variant_of": "засіб для чорніння гуми"}
        ]
        prepared = PreparedText("Купуйте засоби для чорніння шин", "uk")
        r = check_keyword("засіб для чорніння гуми", prepared, synonyms)
        assert r.status == "SYNONYM"
        assert r.covered is True
        assert r.covered_by == "засоби для чорніння шин"

    def test_synonym_match_case_insensitive(self):
        """SYNONYM variant_of comparison должен быть case-insensitive."""
        synonyms = [
            {"keyword": "чорнитель шин", "variant_of": "Чорнитель Гуми"}
        ]
        prepared = PreparedText("Купуйте чорнитель шин", "uk")
        r = check_keyword("чорнитель гуми", prepared, synonyms)
        assert r.status == "SYNONYM"
        assert r.covered is True

    def test_tokenization_not_found(self):
        prepared = PreparedText("Звичайний засіб", "uk")
        r = check_keyword("pH-нейтральний", prepared, [])
        assert r.status == "TOKENIZATION"
        assert r.covered is False

    def test_partial_match(self):
        # 2 of 3 words found
        prepared = PreparedText("Активна речовина для авто", "uk")
        r = check_keyword("активна піна авто", prepared, [])
        assert r.status == "PARTIAL"
        assert r.covered is False
        assert r.lemma_coverage is not None
        assert r.lemma_coverage >= 0.5

    def test_absent(self):
        prepared = PreparedText("Текст без цього слова", "uk")
        r = check_keyword("неіснуюче слово", prepared, [])
        assert r.status == "ABSENT"
        assert r.covered is False
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_coverage_matcher.py::TestCheckKeyword -v
```
Expected: FAIL

**Step 3: Write implementation**

```python
# Add to scripts/coverage_matcher.py
from scripts.keyword_utils import MorphAnalyzer


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
            if _match_sequence(kw_lemmas[1:], prepared.lemmas[start_idx + 1:], max_gap):
                return True

    return False


def _match_sequence(remaining: list[str], text_lemmas: list[str], max_gap: int) -> bool:
    """Match remaining lemmas with gap tolerance."""
    if not remaining:
        return True

    target = remaining[0]
    for i, lemma in enumerate(text_lemmas[:max_gap + 1]):
        if lemma == target:
            return _match_sequence(remaining[1:], text_lemmas[i + 1:], max_gap)

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
                return MatchResult(
                    status="SYNONYM", covered=True,
                    covered_by=syn_kw, syn_match_method="EXACT"
                )
            if _normalized_match(syn_kw, prepared):
                return MatchResult(
                    status="SYNONYM", covered=True,
                    covered_by=syn_kw, syn_match_method="NORM"
                )
            if _lemma_match(syn_kw, prepared, morph):
                return MatchResult(
                    status="SYNONYM", covered=True,
                    covered_by=syn_kw, syn_match_method="LEMMA"
                )

    # === NOT COVERED — diagnose reason ===

    # 5. TOKENIZATION
    if has_tokenization_markers(keyword):
        return MatchResult(
            status="TOKENIZATION", covered=False,
            reason="Contains special tokens"
        )

    # 6. PARTIAL
    lemma_cov = _calculate_lemma_coverage(keyword, prepared, morph)
    if lemma_cov >= 0.5:
        return MatchResult(
            status="PARTIAL", covered=False,
            lemma_coverage=lemma_cov,
            reason=f"{int(lemma_cov * 100)}% lemmas found"
        )

    # 7. ABSENT
    return MatchResult(status="ABSENT", covered=False)
```

**Step 4: Run test**

```bash
pytest tests/unit/test_coverage_matcher.py::TestCheckKeyword -v
```
Expected: PASS

---

## Task 5: audit_category function

**Files:**
- Modify: `scripts/coverage_matcher.py`
- Test: `tests/unit/test_coverage_matcher.py`

**Step 1: Write failing test**

```python
# Add to tests/unit/test_coverage_matcher.py
from scripts.coverage_matcher import audit_category


class TestAuditCategory:
    def test_returns_dict_structure(self):
        keywords = [
            {"keyword": "чорніння гуми", "volume": 390},
            {"keyword": "чорнитель гуми", "volume": 50},
        ]
        synonyms = []
        text = "Чорніння гуми повертає колір"

        result = audit_category(keywords, synonyms, text, "uk")

        assert "slug" not in result  # slug added by caller
        assert "total" in result
        assert "covered" in result
        assert "coverage_percent" in result
        assert "results" in result
        assert len(result["results"]) == 2

    def test_calculates_coverage(self):
        keywords = [
            {"keyword": "тест один", "volume": 100},
            {"keyword": "тест два", "volume": 50},
        ]
        text = "Тут є тест один але немає іншого"

        result = audit_category(keywords, [], text, "uk")

        assert result["total"] == 2
        assert result["covered"] == 1
        assert result["coverage_percent"] == 50.0
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/unit/test_coverage_matcher.py::TestAuditCategory -v
```
Expected: FAIL

**Step 3: Write implementation**

```python
# Add to scripts/coverage_matcher.py

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

        results.append({
            "keyword": kw,
            "volume": volume,
            "status": match.status,
            "covered": match.covered,
            "covered_by": match.covered_by,
            "syn_match_method": match.syn_match_method,
            "lemma_coverage": match.lemma_coverage,
            "reason": match.reason,
        })

    total = len(keywords)
    covered = sum(1 for r in results if r["covered"])
    coverage_percent = (covered / total * 100) if total > 0 else 100.0

    return {
        "total": total,
        "covered": covered,
        "coverage_percent": round(coverage_percent, 1),
        "results": results,
    }
```

**Step 4: Run test**

```bash
pytest tests/unit/test_coverage_matcher.py::TestAuditCategory -v
```
Expected: PASS

---

## Task 6: CLI script audit_coverage.py (single mode)

**Files:**
- Create: `scripts/audit_coverage.py`
- Test: `tests/unit/test_coverage_matcher.py` (add path resolution tests)

**Step 1: Write tests for path resolution**

```python
# Add to tests/unit/test_coverage_matcher.py
import pytest
from pathlib import Path

# Import after creating the CLI script
# from scripts.audit_coverage import find_category_path, get_all_slugs


class TestPathResolution:
    """Test RU hierarchical and UK flat path resolution."""

    def test_uk_flat_structure(self, tmp_path):
        """UK categories are flat: uk/categories/{slug}/"""
        # Setup
        slug = "cherniteli-shin"
        uk_base = tmp_path / "uk" / "categories" / slug / "data"
        uk_base.mkdir(parents=True)
        (uk_base / f"{slug}_clean.json").write_text("{}")

        # Test find_category_path
        from scripts.audit_coverage import find_category_path
        # Monkey-patch PROJECT_ROOT for test
        import scripts.audit_coverage as module
        original_root = module.PROJECT_ROOT
        module.PROJECT_ROOT = tmp_path
        try:
            result = find_category_path(slug, "uk")
            assert result is not None
            assert result.name == slug
        finally:
            module.PROJECT_ROOT = original_root

    def test_ru_hierarchical_structure(self, tmp_path):
        """RU categories are nested: categories/parent/child/slug/"""
        # Setup: categories/moyka-i-eksterer/aktivnaya-pena/data/aktivnaya-pena_clean.json
        slug = "aktivnaya-pena"
        ru_base = tmp_path / "categories" / "moyka-i-eksterer" / slug / "data"
        ru_base.mkdir(parents=True)
        (ru_base / f"{slug}_clean.json").write_text("{}")

        # Test find_category_path
        from scripts.audit_coverage import find_category_path
        import scripts.audit_coverage as module
        original_root = module.PROJECT_ROOT
        module.PROJECT_ROOT = tmp_path
        try:
            result = find_category_path(slug, "ru")
            assert result is not None
            assert result.name == slug
        finally:
            module.PROJECT_ROOT = original_root

    def test_get_all_slugs_ru(self, tmp_path):
        """get_all_slugs should find all RU slugs recursively."""
        # Setup multiple nested categories
        for parent, slug in [
            ("moyka-i-eksterer", "aktivnaya-pena"),
            ("aksessuary", "gubki-i-varezhki"),
            ("aksessuary/gubki-i-varezhki", "nested-child"),  # deep nesting
        ]:
            path = tmp_path / "categories" / parent / slug / "data"
            path.mkdir(parents=True, exist_ok=True)
            (path / f"{slug}_clean.json").write_text("{}")

        from scripts.audit_coverage import get_all_slugs
        import scripts.audit_coverage as module
        original_root = module.PROJECT_ROOT
        module.PROJECT_ROOT = tmp_path
        try:
            slugs = get_all_slugs("ru")
            assert "aktivnaya-pena" in slugs
            assert "gubki-i-varezhki" in slugs
            assert "nested-child" in slugs
        finally:
            module.PROJECT_ROOT = original_root
```

**Step 2: Write script with --slug mode**

```python
#!/usr/bin/env python3
"""
audit_coverage.py — Keyword Coverage Audit Tool

Usage:
    python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --verbose
    python3 scripts/audit_coverage.py --lang uk  # batch all UK categories
    python3 scripts/audit_coverage.py --slug X --lang uk --json
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from coverage_matcher import audit_category


def find_category_path(slug: str, lang: str) -> Path | None:
    """
    Find category path by slug.

    UK: flat structure uk/categories/{slug}/
    RU: hierarchical categories/.../slug/  (need recursive search)
    """
    if lang == "uk":
        path = PROJECT_ROOT / "uk" / "categories" / slug
        if path.exists():
            return path
        return None
    else:
        # RU categories are nested: categories/parent/child/slug/
        # Search recursively for directory with matching slug
        base = PROJECT_ROOT / "categories"
        for clean_file in base.rglob(f"{slug}_clean.json"):
            # clean_file: categories/.../slug/data/slug_clean.json
            return clean_file.parent.parent  # .../slug/
        return None


def load_category_data(slug: str, lang: str) -> tuple[list, list, str] | None:
    """Load keywords, synonyms, and content for a category."""
    base = find_category_path(slug, lang)
    if base is None:
        return None

    if lang == "uk":
        content_file = base / "content" / f"{slug}_uk.md"
    else:
        content_file = base / "content" / f"{slug}_ru.md"

    clean_file = base / "data" / f"{slug}_clean.json"

    if not clean_file.exists():
        return None
    if not content_file.exists():
        return None

    with open(clean_file, encoding="utf-8") as f:
        data = json.load(f)

    keywords = data.get("keywords", [])
    synonyms = data.get("synonyms", [])

    content = content_file.read_text(encoding="utf-8")

    return keywords, synonyms, content


def get_all_slugs(lang: str) -> list[str]:
    """Get all category slugs for a language."""
    if lang == "uk":
        base = PROJECT_ROOT / "uk" / "categories"
        if not base.exists():
            return []
        slugs = []
        for d in base.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                clean_file = d / "data" / f"{d.name}_clean.json"
                if clean_file.exists():
                    slugs.append(d.name)
        return sorted(slugs)
    else:
        # RU: recursive search
        base = PROJECT_ROOT / "categories"
        if not base.exists():
            return []
        slugs = []
        for clean_file in base.rglob("*_clean.json"):
            # Extract slug from filename: slug_clean.json
            slug = clean_file.stem.replace("_clean", "")
            # Verify directory structure
            if clean_file.parent.name == "data" and clean_file.parent.parent.name == slug:
                slugs.append(slug)
        return sorted(slugs)


def print_verbose(slug: str, lang: str, result: dict):
    """Print human-readable audit report."""
    print(f"\n=== {slug} ({lang}) ===")
    print(f"Coverage: {result['covered']}/{result['total']} ({result['coverage_percent']}%)")

    # Group by status
    by_status: dict[str, list] = {}
    for r in result["results"]:
        status = r["status"]
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(r)

    # Print COVERED
    for status in ["EXACT", "NORM", "LEMMA", "SYNONYM"]:
        if status in by_status:
            items = by_status[status]
            print(f"\n✓ {status} ({len(items)}):")
            for r in items[:5]:
                if status == "SYNONYM":
                    print(f"  - {r['keyword']} ({r['volume']}) ← {r['covered_by']} [{r['syn_match_method']}]")
                else:
                    print(f"  - {r['keyword']} ({r['volume']})")
            if len(items) > 5:
                print(f"  ... and {len(items) - 5} more")

    # Print NOT COVERED
    not_covered = []
    for status in ["TOKENIZATION", "PARTIAL", "ABSENT"]:
        if status in by_status:
            not_covered.extend(by_status[status])

    if not_covered:
        print(f"\n✗ NOT COVERED ({len(not_covered)}):")
        # Sort by volume desc
        not_covered.sort(key=lambda x: x["volume"], reverse=True)
        for r in not_covered[:10]:
            extra = f" — {r['reason']}" if r.get("reason") else ""
            print(f"  - [{r['status']}] {r['keyword']} ({r['volume']}){extra}")
        if len(not_covered) > 10:
            print(f"  ... and {len(not_covered) - 10} more")


def main():
    parser = argparse.ArgumentParser(description="Audit keyword coverage")
    parser.add_argument("--slug", help="Single category slug")
    parser.add_argument("--lang", choices=["ru", "uk", "all"], default="uk")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.slug:
        # Single category mode
        langs = ["ru", "uk"] if args.lang == "all" else [args.lang]

        for lang in langs:
            data = load_category_data(args.slug, lang)
            if data is None:
                print(f"Category {args.slug} ({lang}) not found", file=sys.stderr)
                continue

            keywords, synonyms, content = data
            result = audit_category(keywords, synonyms, content, lang)
            result["slug"] = args.slug
            result["lang"] = lang

            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif args.verbose:
                print_verbose(args.slug, lang, result)
            else:
                print(f"{args.slug} ({lang}): {result['covered']}/{result['total']} ({result['coverage_percent']}%)")
    else:
        # Batch mode - will be implemented in Task 7
        print("Batch mode: use --slug for single category or wait for Task 7")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Step 2: Test manually**

```bash
python3 scripts/audit_coverage.py --slug cherniteli-shin --lang uk --verbose
```
Expected: Human-readable output with coverage stats

**Step 3: Test JSON output**

```bash
python3 scripts/audit_coverage.py --slug cherniteli-shin --lang uk --json
```
Expected: JSON output

---

## Task 7: CLI batch mode + CSV output

**Files:**
- Modify: `scripts/audit_coverage.py`

**Step 1: Add batch mode and CSV generation**

```python
# Add imports at top
import csv
from datetime import date

# Add CSV writing functions
def write_summary_csv(results: list[dict], lang: str):
    """Write coverage_summary.csv"""
    today = date.today().isoformat()
    filename = PROJECT_ROOT / "reports" / f"coverage_summary_{lang}_{today}.csv"
    filename.parent.mkdir(exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "slug", "lang", "total_keywords", "covered",
            "not_covered", "coverage_percent", "top_missing"
        ])

        for r in results:
            # Get top 3 missing by volume
            missing = [x for x in r["results"] if not x["covered"]]
            missing.sort(key=lambda x: x["volume"], reverse=True)
            top_missing = ";".join(
                f"{x['keyword']} ({x['volume']})" for x in missing[:3]
            )

            writer.writerow([
                r["slug"],
                r["lang"],
                r["total"],
                r["covered"],
                r["total"] - r["covered"],
                r["coverage_percent"],
                top_missing,
            ])

    print(f"Written: {filename}")
    return filename


def write_details_csv(results: list[dict], lang: str):
    """Write coverage_details.csv"""
    today = date.today().isoformat()
    filename = PROJECT_ROOT / "reports" / f"coverage_details_{lang}_{today}.csv"

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "slug", "lang", "keyword", "volume", "status", "covered",
            "covered_by", "syn_match_method", "lemma_coverage", "reason"
        ])

        for cat in results:
            for r in cat["results"]:
                writer.writerow([
                    cat["slug"],
                    cat["lang"],
                    r["keyword"],
                    r["volume"],
                    r["status"],
                    r["covered"],
                    r["covered_by"] or "",
                    r["syn_match_method"] or "",
                    r["lemma_coverage"] or "",
                    r["reason"] or "",
                ])

    print(f"Written: {filename}")
    return filename


# Update main() batch section:
    else:
        # Batch mode
        langs = ["ru", "uk"] if args.lang == "all" else [args.lang]

        for lang in langs:
            slugs = get_all_slugs(lang)
            if not slugs:
                print(f"No categories found for {lang}", file=sys.stderr)
                continue

            print(f"\nAuditing {len(slugs)} {lang.upper()} categories...")

            all_results = []
            for slug in slugs:
                data = load_category_data(slug, lang)
                if data is None:
                    continue

                keywords, synonyms, content = data
                result = audit_category(keywords, synonyms, content, lang)
                result["slug"] = slug
                result["lang"] = lang
                all_results.append(result)

                if args.verbose:
                    print_verbose(slug, lang, result)
                else:
                    status = "✓" if result["coverage_percent"] >= 60 else "✗"
                    print(f"  {status} {slug}: {result['coverage_percent']}%")

            # Write CSVs
            write_summary_csv(all_results, lang)
            write_details_csv(all_results, lang)
```

**Step 2: Test batch mode**

```bash
python3 scripts/audit_coverage.py --lang uk
```
Expected: Creates `reports/coverage_summary_uk_*.csv` and `reports/coverage_details_uk_*.csv`

**Step 3: Verify CSV content**

```bash
head -5 reports/coverage_summary_uk_*.csv
head -10 reports/coverage_details_uk_*.csv
```

---

## Task 8: Final integration test

**Files:**
- Test on real data

**Step 1: Run full audit**

```bash
python3 scripts/audit_coverage.py --lang uk --verbose
```

**Step 2: Verify cherniteli-shin (known good)**

```bash
python3 scripts/audit_coverage.py --slug cherniteli-shin --lang uk --verbose
```
Expected: High coverage (should be close to 100%)

**Step 3: Check CSV reports**

```bash
# Summary
cat reports/coverage_summary_uk_*.csv

# Details for specific category
grep "cherniteli-shin" reports/coverage_details_uk_*.csv
```

**Step 4: Run all tests**

```bash
pytest tests/unit/test_coverage_matcher.py -v
```
Expected: All tests PASS

**Step 5: Final commit (один на весь план)**

```bash
git add scripts/coverage_matcher.py scripts/audit_coverage.py tests/unit/test_coverage_matcher.py
git commit -m "feat(coverage): add coverage audit tool with diagnostics

- MatchResult dataclass with status types
- PreparedText for efficient batch matching
- check_keyword with EXACT/NORM/LEMMA/SYNONYM cascade
- has_tokenization_markers for special tokens detection
- audit_category with coverage calculation
- CLI single mode (--slug) and batch mode
- CSV output (summary + details)
- RU hierarchical path resolution"
```

---

## Acceptance Criteria Checklist

After completing all tasks, verify:

- [ ] `pytest tests/unit/test_coverage_matcher.py -v` — all pass
- [ ] `audit_coverage.py --slug cherniteli-shin --lang uk --verbose` — human-readable output
- [ ] `audit_coverage.py --slug cherniteli-shin --lang uk --json` — valid JSON
- [ ] `audit_coverage.py --lang uk` — generates 2 CSV files
- [ ] `audit_coverage.py --slug aktivnaya-pena --lang ru --verbose` — RU nested path works
- [ ] `audit_coverage.py --lang ru` — finds all RU categories recursively
- [ ] EXACT/NORM/LEMMA/SYNONYM statuses work correctly
- [ ] TOKENIZATION detects pH-, 1:10, wash-and-wax (латиница)
- [ ] PARTIAL shows lemma coverage percentage
- [ ] SYNONYM shows `covered_by` and `syn_match_method`
- [ ] SYNONYM variant_of comparison is case-insensitive
