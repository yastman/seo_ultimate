# Design: Keyword Utils Refactoring

**Date:** 2026-01-29
**Status:** Draft
**Author:** Claude + User

---

## Problem Statement

Текущий код проверки ключевых слов имеет критические проблемы:

1. **35+ точек дублирования** функционала проверки keywords
2. **5+ версий ручного стемминга** с разной логикой
3. **pymorphy2 установлен, но не используется** — вместо него `word[:-2]`
4. **Exact match не находит падежные формы**: "щётка для мытья" не найдёт "щётку для мытья"
5. **3x дублирование** `get_adaptive_coverage_target()` в разных файлах

---

## Goals

1. Создать единый модуль `scripts/keyword_utils.py` с морфологическим анализом
2. Использовать **pymorphy3** для корректной лемматизации RU/UK
3. Устранить все дубли — единый источник истины (SSOT)
4. Обратная совместимость — существующие скрипты продолжают работать

---

## Non-Goals

- Переписывать check_keyword_density.py полностью (только интеграция)
- Менять формат _clean.json или _meta.json
- Добавлять новые CLI команды

---

## Technical Decisions

### 1. Библиотека морфологии

**Выбор: pymorphy3** (drop-in replacement для pymorphy2)

```bash
# requirements.txt change
- pymorphy2==0.9.1
- pymorphy2-dicts-ru==2.4.417127.4579844
+ pymorphy3>=2.0.0
+ pymorphy3-dicts-ru>=2.4.0
+ pymorphy3-dicts-uk>=2.4.0  # для украинского
```

**Причины:**
- Активная поддержка (релиз Jun 2025)
- API идентичен pymorphy2
- Поддержка Python 3.9+
- RU + UK в одном пакете

### 2. Архитектура модуля

```
scripts/
├── keyword_utils.py          # NEW: единый модуль
├── config.py                 # оставляем get_adaptive_coverage_target()
├── validate_content.py       # рефакторим: импорт из keyword_utils
├── validate_meta.py          # рефакторим: импорт из keyword_utils
├── check_seo_structure.py    # рефакторим: импорт из keyword_utils
├── check_keyword_density.py  # рефакторим: импорт стеммера
├── seo_utils.py              # удаляем дубли, импорт из keyword_utils
└── utils/
    └── text.py               # удаляем дубли, импорт из keyword_utils
```

### 3. Fallback Strategy

```
pymorphy3 available?
  → YES: use lemmatization (точно)
  → NO:  use Snowball stemmer (быстро, но грубо)
```

---

## API Design

### scripts/keyword_utils.py

```python
"""
keyword_utils.py — Unified Keyword Matching with Russian/Ukrainian Morphology

Единый модуль для:
- Лемматизации (pymorphy3)
- Поиска ключевых слов с учётом падежей
- Проверки coverage
- Генерации всех форм слова

Usage:
    from scripts.keyword_utils import KeywordMatcher, CoverageChecker

    matcher = KeywordMatcher(lang='ru')
    found, form = matcher.find_in_text("щётка для мытья", text)
    # found=True, form="щётку для мытья"

    checker = CoverageChecker(lang='ru')
    result = checker.check(keywords, text)
    # {found: [...], missing: [...], coverage: 85.0}
"""

from __future__ import annotations
import re
from functools import lru_cache
from typing import Literal

# =============================================================================
# Constants (SSOT)
# =============================================================================

COMMERCIAL_MARKERS_RU = [
    "купить", "цена", "стоимость", "заказать", "доставка",
    "интернет-магазин", "каталог", "в наличии", "со скидкой",
]

COMMERCIAL_MARKERS_UK = [
    "купити", "ціна", "вартість", "замовити", "доставка",
    "інтернет-магазин", "каталог", "в наявності", "зі знижкою",
]

STOPLIST_PHRASES_RU = [
    "лучший", "самый лучший", "номер один", "№1",
    "гарантируем", "100%", "обещаем",
]

STOPLIST_PHRASES_UK = [
    "найкращий", "номер один", "№1",
    "гарантуємо", "100%", "обіцяємо",
]

# =============================================================================
# Morphology Backend
# =============================================================================

class MorphAnalyzer:
    """
    Singleton морфологический анализатор.

    Использует pymorphy3 если доступен, иначе Snowball fallback.
    """

    _instances: dict[str, "MorphAnalyzer"] = {}

    def __new__(cls, lang: Literal["ru", "uk"] = "ru"):
        if lang not in cls._instances:
            instance = super().__new__(cls)
            instance._init_analyzer(lang)
            cls._instances[lang] = instance
        return cls._instances[lang]

    def _init_analyzer(self, lang: str):
        self.lang = lang
        self._morph = None
        self._stemmer = None
        self._use_pymorphy = False

        # Try pymorphy3 first
        try:
            import pymorphy3
            if lang == "uk":
                self._morph = pymorphy3.MorphAnalyzer(lang='uk')
            else:
                self._morph = pymorphy3.MorphAnalyzer()
            self._use_pymorphy = True
        except ImportError:
            pass

        # Fallback to pymorphy2
        if not self._use_pymorphy:
            try:
                import pymorphy2
                self._morph = pymorphy2.MorphAnalyzer()
                self._use_pymorphy = True
            except ImportError:
                pass

        # Fallback to Snowball
        if not self._use_pymorphy:
            try:
                from snowballstemmer import stemmer
                self._stemmer = stemmer("russian" if lang == "ru" else "russian")
            except ImportError:
                pass

    @lru_cache(maxsize=10000)
    def get_lemma(self, word: str) -> str:
        """
        Получить лемму (начальную форму) слова.

        щётки → щётка
        машинки → машинка
        грязеуловителем → грязеуловитель
        """
        word_lower = word.lower()

        if self._use_pymorphy and self._morph:
            parsed = self._morph.parse(word_lower)
            if parsed:
                return parsed[0].normal_form

        if self._stemmer:
            return self._stemmer.stemWord(word_lower)

        # Ultimate fallback: strip 2 chars
        if len(word_lower) > 4:
            return word_lower[:-2]
        return word_lower

    @lru_cache(maxsize=1000)
    def get_all_forms(self, word: str) -> set[str]:
        """
        Получить все формы слова (падежи, числа).

        щётка → {щётка, щётки, щётке, щётку, щёткой, щёткою, щётках, щёткам, щётками}
        """
        if not self._use_pymorphy or not self._morph:
            # Fallback: return just the word
            return {word.lower()}

        word_lower = word.lower()
        parsed = self._morph.parse(word_lower)
        if not parsed:
            return {word_lower}

        forms = set()
        for p in parsed[:1]:  # Take first parse (most likely)
            for form in p.lexeme:
                forms.add(form.word)

        return forms

    def normalize_phrase(self, phrase: str) -> list[str]:
        """
        Лемматизировать фразу (каждое значимое слово).

        "щётки для мытья машины" → ["щётка", "мытьё", "машина"]
        """
        words = re.findall(r'[а-яёїієґa-z]+', phrase.lower())
        lemmas = []
        for w in words:
            if len(w) > 2:  # Skip short words
                lemmas.append(self.get_lemma(w))
        return lemmas


# =============================================================================
# Keyword Matcher
# =============================================================================

class KeywordMatcher:
    """
    Поиск ключевых слов в тексте с учётом морфологии.
    """

    def __init__(self, lang: Literal["ru", "uk"] = "ru"):
        self.lang = lang
        self.morph = MorphAnalyzer(lang)

    def match_exact(self, keyword: str, text: str) -> bool:
        """Точное вхождение (case-insensitive)."""
        return keyword.lower() in text.lower()

    def match_lemma(self, keyword: str, text: str) -> tuple[bool, str | None]:
        """
        Поиск по леммам — основной метод.

        Returns:
            (found: bool, matched_form: str | None)

        Example:
            match_lemma("щётка для мытья", "используйте щётку для мытья")
            → (True, "щётку для мытья")
        """
        # 1. Try exact match first
        if self.match_exact(keyword, text):
            return (True, keyword)

        # 2. Single word keyword
        kw_words = keyword.lower().split()
        if len(kw_words) == 1:
            return self._match_single_word(kw_words[0], text)

        # 3. Multi-word phrase
        return self._match_phrase(kw_words, text)

    def _match_single_word(self, word: str, text: str) -> tuple[bool, str | None]:
        """Match single word using all its forms."""
        forms = self.morph.get_all_forms(word)
        text_lower = text.lower()

        for form in forms:
            # Word boundary check
            pattern = rf'\b{re.escape(form)}\b'
            match = re.search(pattern, text_lower)
            if match:
                return (True, form)

        return (False, None)

    def _match_phrase(self, kw_words: list[str], text: str) -> tuple[bool, str | None]:
        """
        Match multi-word phrase.

        Strategy:
        1. Get lemmas of keyword words
        2. Get lemmas of text words
        3. Check if all keyword lemmas appear in sequence (with gap tolerance)
        """
        kw_lemmas = [self.morph.get_lemma(w) for w in kw_words if len(w) > 2]

        if not kw_lemmas:
            return (False, None)

        # Tokenize text
        text_words = re.findall(r'[а-яёїієґa-z]+', text.lower())
        text_lemmas = [self.morph.get_lemma(w) for w in text_words]

        # Find sequence with gap tolerance (max 2 words between)
        max_gap = 2

        for start_idx in range(len(text_lemmas)):
            if text_lemmas[start_idx] == kw_lemmas[0]:
                # Try to match rest of phrase
                matched, end_idx = self._match_sequence(
                    kw_lemmas[1:],
                    text_lemmas[start_idx + 1:],
                    max_gap
                )
                if matched:
                    # Reconstruct matched form from original text
                    matched_words = text_words[start_idx:start_idx + end_idx + 1]
                    return (True, " ".join(matched_words))

        return (False, None)

    def _match_sequence(
        self,
        remaining_lemmas: list[str],
        text_lemmas: list[str],
        max_gap: int
    ) -> tuple[bool, int]:
        """Match remaining lemmas with gap tolerance."""
        if not remaining_lemmas:
            return (True, 0)

        target = remaining_lemmas[0]

        for i, lemma in enumerate(text_lemmas[:max_gap + 1]):
            if lemma == target:
                matched, end_idx = self._match_sequence(
                    remaining_lemmas[1:],
                    text_lemmas[i + 1:],
                    max_gap
                )
                if matched:
                    return (True, i + 1 + end_idx)

        return (False, 0)

    def find_in_text(self, keyword: str, text: str) -> tuple[bool, str | None]:
        """
        Unified method: find keyword in text.

        Returns (found, matched_form).
        """
        return self.match_lemma(keyword, text)


# =============================================================================
# Coverage Checker
# =============================================================================

class CoverageChecker:
    """
    Проверка покрытия ключевых слов в тексте.
    """

    def __init__(self, lang: Literal["ru", "uk"] = "ru"):
        self.lang = lang
        self.matcher = KeywordMatcher(lang)

    @staticmethod
    def get_adaptive_target(keyword_count: int) -> float:
        """
        Адаптивный target coverage (ЕДИНСТВЕННАЯ ВЕРСИЯ).

        <= 5 keywords: 70%
        6-15 keywords: 60%
        > 15 keywords: 50%
        """
        if keyword_count <= 5:
            return 70.0
        elif keyword_count <= 15:
            return 60.0
        else:
            return 50.0

    def check(
        self,
        keywords: list[str],
        text: str,
        use_lemma: bool = True
    ) -> dict:
        """
        Check keyword coverage in text.

        Returns:
            {
                "total": int,
                "found": int,
                "coverage_percent": float,
                "target": float,
                "passed": bool,
                "found_keywords": [{"keyword": str, "form": str}, ...],
                "missing_keywords": [str, ...]
            }
        """
        if not keywords:
            return {
                "total": 0,
                "found": 0,
                "coverage_percent": 100.0,
                "target": 0,
                "passed": True,
                "found_keywords": [],
                "missing_keywords": [],
            }

        found_keywords = []
        missing_keywords = []

        for kw in keywords:
            if use_lemma:
                matched, form = self.matcher.find_in_text(kw, text)
            else:
                matched = self.matcher.match_exact(kw, text)
                form = kw if matched else None

            if matched:
                found_keywords.append({"keyword": kw, "form": form})
            else:
                missing_keywords.append(kw)

        total = len(keywords)
        found = len(found_keywords)
        coverage = (found / total) * 100
        target = self.get_adaptive_target(total)

        return {
            "total": total,
            "found": found,
            "coverage_percent": round(coverage, 1),
            "target": target,
            "passed": coverage >= target,
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
        }

    def check_split(
        self,
        core_keywords: list[str],
        commercial_keywords: list[str],
        text: str
    ) -> dict:
        """
        Check coverage split by intent (core vs commercial).

        Core keywords: target applies (WARNING if below)
        Commercial keywords: INFO only (no penalty)
        """
        core_result = self.check(core_keywords, text)
        comm_result = self.check(commercial_keywords, text, use_lemma=False)

        return {
            "core": core_result,
            "commercial": comm_result,
            "overall_passed": core_result["passed"],
        }


# =============================================================================
# Utility Functions (for backward compatibility)
# =============================================================================

def get_adaptive_coverage_target(keyword_count: int) -> float:
    """Backward-compatible wrapper."""
    return CoverageChecker.get_adaptive_target(keyword_count)


def keyword_matches_text(keyword: str, text: str, lang: str = "ru") -> bool:
    """
    Backward-compatible function.

    Replaces:
    - validate_content.py: keyword_matches_semantic()
    - validate_meta.py: keyword_matches()
    """
    matcher = KeywordMatcher(lang)
    found, _ = matcher.find_in_text(keyword, text)
    return found


def find_keyword_form(keyword: str, text: str, lang: str = "ru") -> str | None:
    """
    Find which form of keyword appears in text.

    Example:
        find_keyword_form("щётка для мытья", text)
        → "щётку для мытья"
    """
    matcher = KeywordMatcher(lang)
    found, form = matcher.find_in_text(keyword, text)
    return form if found else None


def get_commercial_markers(lang: str = "ru") -> list[str]:
    """Get commercial markers for language (SSOT)."""
    return COMMERCIAL_MARKERS_UK if lang == "uk" else COMMERCIAL_MARKERS_RU


def get_stoplist_phrases(lang: str = "ru") -> list[str]:
    """Get stoplist phrases for language (SSOT)."""
    return STOPLIST_PHRASES_UK if lang == "uk" else STOPLIST_PHRASES_RU
```

---

## Migration Plan

### Phase 1: Create keyword_utils.py
- Создать новый модуль с полным API
- Написать unit tests
- Не трогать существующие скрипты

### Phase 2: Update dependencies
```bash
pip install pymorphy3 pymorphy3-dicts-ru pymorphy3-dicts-uk
# Update requirements.txt
```

### Phase 3: Migrate consumers (one by one)
1. `validate_content.py` — заменить `keyword_matches_semantic()` на импорт
2. `validate_meta.py` — заменить `keyword_matches()` на импорт
3. `check_seo_structure.py` — заменить ручной стемминг
4. `seo_utils.py` — удалить дубли, импортировать из keyword_utils
5. `utils/text.py` — удалить дубли, импортировать из keyword_utils
6. `config.py` — оставить `get_adaptive_coverage_target()` как SSOT

### Phase 4: Update check_keyword_density.py
- Интегрировать MorphAnalyzer для stem-based анализа
- Использовать общие константы

### Phase 5: Cleanup
- Удалить мёртвый код
- Обновить документацию

---

## Files to Modify

| File | Action | Changes |
|------|--------|---------|
| `scripts/keyword_utils.py` | CREATE | Новый модуль |
| `requirements.txt` | EDIT | pymorphy2 → pymorphy3 |
| `scripts/validate_content.py` | EDIT | Импорт из keyword_utils |
| `scripts/validate_meta.py` | EDIT | Импорт из keyword_utils |
| `scripts/check_seo_structure.py` | EDIT | Импорт из keyword_utils |
| `scripts/seo_utils.py` | EDIT | Удалить дубли |
| `scripts/utils/text.py` | EDIT | Удалить дубли |
| `scripts/check_keyword_density.py` | EDIT | Интеграция MorphAnalyzer |
| `tests/unit/test_keyword_utils.py` | CREATE | Unit tests |

---

## Testing Strategy

### Unit Tests
```python
# tests/unit/test_keyword_utils.py

def test_get_lemma_noun():
    morph = MorphAnalyzer("ru")
    assert morph.get_lemma("щётки") == "щётка"
    assert morph.get_lemma("машинки") == "машинка"

def test_get_lemma_verb():
    morph = MorphAnalyzer("ru")
    assert morph.get_lemma("моющий") == "мыть"

def test_match_single_word():
    matcher = KeywordMatcher("ru")
    found, form = matcher.find_in_text("щётка", "используйте щётку")
    assert found is True
    assert form == "щётку"

def test_match_phrase():
    matcher = KeywordMatcher("ru")
    found, form = matcher.find_in_text(
        "щётка для мытья машины",
        "выберите щётку для мытья машины"
    )
    assert found is True

def test_coverage_check():
    checker = CoverageChecker("ru")
    result = checker.check(
        ["щётка", "губка", "микрофибра"],
        "используйте щётку и губку для мытья"
    )
    assert result["found"] == 2
    assert result["coverage_percent"] == pytest.approx(66.7, rel=0.1)

def test_uk_lemma():
    morph = MorphAnalyzer("uk")
    assert morph.get_lemma("щітки") == "щітка"
```

### Integration Tests
- Прогнать существующие тесты после миграции
- Проверить что результаты coverage улучшились (меньше false negatives)

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| pymorphy3 медленнее | LRU cache на 10000 слов |
| Breaking changes в API | Backward-compatible функции |
| Разные результаты после миграции | Сначала тесты, потом миграция |
| UK словарь недоступен | Fallback на RU стеммер |

---

## Success Metrics

1. **Coverage accuracy**: false negatives уменьшились на 80%+
2. **Code duplication**: 35 точек → 1 модуль
3. **All tests pass**: существующие + новые
4. **Performance**: < 100ms на проверку 50 keywords

---

## Open Questions

1. ~~Какую библиотеку использовать?~~ → pymorphy3
2. ~~Обновлять pymorphy2?~~ → Да, до pymorphy3
3. Нужен ли DensityAnalyzer в этом модуле? → Пока нет, оставить в check_keyword_density.py
