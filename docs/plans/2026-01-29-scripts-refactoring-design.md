# Scripts Refactoring Design

**Дата:** 2026-01-29
**Статус:** Draft
**Автор:** Claude + User

---

## 1. Проблемы текущего состояния

### 1.1 Дублирование кода

| Функция | Дублируется в |
|---------|---------------|
| `clean_markdown()` | `seo_utils.py`, `check_keyword_density.py`, `validate_content.py` |
| `STOPWORDS_RU` | `check_keyword_density.py`, `check_water_natasha.py` |
| `STOPWORDS_UK` | `check_keyword_density.py` |
| Стемминг | `keyword_utils.py`, `check_seo_structure.py`, `check_keyword_density.py` |
| `extract_h1/h2/intro` | `validate_content.py`, `check_seo_structure.py` |
| `count_words()` | `seo_utils.py`, `validate_content.py` |

### 1.2 UK поддержка неполная

- `validate_uk.py` — 100 строк, базовая проверка
- `validate_meta.py` — 583 строки, полная валидация
- Нет паритета: UK не имеет всех проверок RU

### 1.3 Разрозненные валидаторы

5 разных скриптов валидации:
1. `validate_meta.py` — Title, Description, H1
2. `validate_content.py` — Structure, quality, coverage
3. `validate_uk.py` — Базовая UK проверка
4. `check_seo_structure.py` — SEO structure
5. `check_keyword_density.py` — Density/spam

### 1.4 Устаревшие скрипты

Примитивные скрипты без полной функциональности:
- `audit_keyword_consistency.py` (91 строка)
- Различные одноразовые `fix_*.py`, `migrate_*.py`

---

## 2. Решения

### 2.1 Требования

1. **Плоская структура** — без вложенных папок core/validators/cli
2. **Backwards compat НЕ нужен** — можно ломать старые CLI
3. **Старые скрипты → archive/** — не удалять, архивировать
4. **Инкрементальный подход** — фаза за фазой

### 2.2 Целевая архитектура

```
scripts/
├── __init__.py
│
├── # ===== CORE MODULES (SSOT) =====
├── text_utils.py              # НОВЫЙ: clean_markdown, stopwords, extract_*
├── keyword_utils.py           # СУЩЕСТВУЮЩИЙ: MorphAnalyzer, KeywordMatcher
├── seo_utils.py               # СУЩЕСТВУЮЩИЙ: → imports from text_utils
├── config.py                  # СУЩЕСТВУЮЩИЙ
│
├── # ===== VALIDATORS =====
├── validate_meta.py           # РЕФАКТОРИНГ: +UK support via --lang
├── validate_content.py        # РЕФАКТОРИНГ: +UK support via --lang
├── validate_seo.py            # НОВЫЙ: из check_seo_structure.py
├── validate_density.py        # НОВЫЙ: из check_keyword_density.py
│
├── # ===== UNIFIED CLI =====
├── validate.py                # НОВЫЙ: unified entry point
│
├── # ===== AUDIT & BATCH =====
├── audit_all.py               # НОВЫЙ: объединяет audit_*
├── batch_process.py           # РЕФАКТОРИНГ: из batch_*.py
│
├── # ===== EXTRACT & EXPORT =====
├── extract_ru_keywords_list.py # СОЗДАН ✅: RU ключи → RU_KEYWORDS.md
├── extract_uk_keywords_list.py # СОЗДАН ✅: UK ключи → UK_KEYWORDS.md
│
├── utils/
│   ├── __init__.py
│   └── url.py                 # СУЩЕСТВУЮЩИЙ
│
└── archive/                   # НОВЫЙ: старые версии
    ├── validate_uk.py
    ├── check_seo_structure.py
    ├── check_keyword_density.py
    └── audit_keyword_consistency.py
```

---

## 3. Детальный дизайн модулей

### 3.1 text_utils.py (НОВЫЙ)

Единый SSOT для текстовых операций.

```python
"""
text_utils.py — Unified Text Processing (SSOT)

Canonical implementations for:
- clean_markdown()
- stopwords (RU + UK)
- text extraction (H1, H2, intro)
- word/char counting
"""

# === CONSTANTS ===
STOPWORDS_RU: frozenset[str]  # ~180 слов (из check_keyword_density.py)
STOPWORDS_UK: frozenset[str]  # ~170 слов (из check_keyword_density.py)

# === FUNCTIONS ===
def get_stopwords(lang: str = "ru") -> frozenset[str]:
    """Get stopwords set for language."""

def clean_markdown(text: str) -> str:
    """
    Remove markdown formatting for analysis (CANONICAL).

    Removes: YAML, headers, links, bold/italic, lists, code, tables
    """

def normalize_text(text: str) -> str:
    """Alias for clean_markdown (backwards compat)."""

def count_words(text: str) -> int:
    """Count words in text (after clean_markdown)."""

def count_chars_no_spaces(text: str) -> int:
    """Count chars excluding whitespace."""

def tokenize(text: str, lang: str = "ru", remove_stopwords: bool = True) -> list[str]:
    """Split into words, optionally remove stopwords."""

def extract_h1(text: str) -> str | None:
    """Extract H1 heading from markdown."""

def extract_h2s(text: str) -> list[str]:
    """Extract all H2 headings."""

def extract_intro(text: str, max_lines: int = 5) -> str:
    """Extract intro paragraph after H1."""
```

**Миграция:**
- `seo_utils.py`: удалить `clean_markdown`, `normalize_text`, `count_words`, `count_chars_no_spaces` → import from `text_utils`
- `check_keyword_density.py`: удалить `clean_markdown`, `STOPWORDS_*`, `tokenize` → import from `text_utils`
- `validate_content.py`: удалить `extract_h1`, `extract_h2s`, `extract_intro` → import from `text_utils`
- `check_seo_structure.py`: удалить local implementations → import from `text_utils`

### 3.2 validate_meta.py (РЕФАКТОРИНГ)

Добавить полную UK поддержку.

```python
"""
validate_meta.py — Meta Tags Validation (RU + UK)

Usage:
    python3 validate_meta.py <meta.json> [--lang ru|uk]
    python3 validate_meta.py --all [--lang ru|uk]
"""

# === ИЗМЕНЕНИЯ ===
# 1. Параметр --lang для выбора языка
# 2. UK patterns для producer/wholesale
# 3. UK-specific длины (Title 30-55, Desc 100-155)
# 4. Удалить импорты дублей, использовать text_utils

PRODUCER_PATTERNS_RU = [r"от производителя", r"производителя ultimate", ...]
PRODUCER_PATTERNS_UK = [r"від виробника", r"виробника ultimate", ...]

WHOLESALE_PATTERNS_RU = [r"опт\b", r"розница", r"оптом"]
WHOLESALE_PATTERNS_UK = [r"опт\b", r"роздріб", r"оптом"]

def get_patterns(lang: str) -> dict:
    """Get validation patterns for language."""

def validate_title(title: str, primary_keywords: list[str], lang: str = "ru") -> dict:
    """Validate meta title with language support."""

def validate_description(desc: str, primary_keywords: list[str], lang: str = "ru") -> dict:
    """Validate meta description with language support."""
```

**CLI изменения:**
```bash
# Старый (убираем)
python3 validate_uk.py aktivnaya-pena

# Новый
python3 validate_meta.py categories/aktivnaya-pena/meta/aktivnaya-pena_meta.json
python3 validate_meta.py uk/categories/aktivnaya-pena/meta/aktivnaya-pena_meta.json --lang uk
python3 validate_meta.py --all --lang uk
```

### 3.3 validate_content.py (РЕФАКТОРИНГ)

Добавить полную UK поддержку.

```python
"""
validate_content.py — Content Validation (RU + UK)

Usage:
    python3 validate_content.py <file.md> "<keyword>" [--lang ru|uk]
"""

# === ИЗМЕНЕНИЯ ===
# 1. Параметр --lang для выбора языка (авто-определение по пути)
# 2. UK stopwords/patterns в check_quality()
# 3. UK patterns в check_content_standards()
# 4. Использовать text_utils для extract_*, clean_markdown

def detect_language(file_path: str) -> str:
    """Auto-detect language from file path (uk/categories/ → 'uk')."""

def check_quality(text: str, lang: str = "ru") -> dict:
    """Check water/nausea with language-specific stopwords."""

def check_content_standards(text: str, lang: str = "ru") -> dict:
    """Check CONTENT_GUIDE requirements with UK patterns."""
```

### 3.4 validate_seo.py (НОВЫЙ, из check_seo_structure.py)

Переименование + унификация.

```python
"""
validate_seo.py — SEO Structure Validation (RU + UK)

Checks:
1. Main keyword in intro (first 150 chars)
2. Keywords in H2 headings (min 2)
3. Keyword frequency (3-7, anti-spam)

Usage:
    python3 validate_seo.py <file.md> "<keyword>" [--lang ru|uk]
"""

# === ИЗМЕНЕНИЯ ===
# 1. Переименовать check_seo_structure.py → validate_seo.py
# 2. Импортировать extract_*, get_word_stems из text_utils/keyword_utils
# 3. Удалить локальные реализации стемминга
```

### 3.5 validate_density.py (НОВЫЙ, из check_keyword_density.py)

Переименование + очистка.

```python
"""
validate_density.py — Keyword Density & Spam Check (RU + UK)

Usage:
    python3 validate_density.py <file.md> [--lang ru|uk] [--top 20]
"""

# === ИЗМЕНЕНИЯ ===
# 1. Переименовать check_keyword_density.py → validate_density.py
# 2. Удалить STOPWORDS_*, clean_markdown, tokenize → import from text_utils
# 3. Сохранить stem analysis (Snowball)
```

### 3.6 validate.py (НОВЫЙ — Unified CLI)

Единая точка входа для всех валидаций.

```python
"""
validate.py — Unified Validation CLI

Usage:
    python3 validate.py meta <path> [--lang ru|uk]
    python3 validate.py content <path> "<keyword>" [--lang ru|uk]
    python3 validate.py seo <path> "<keyword>" [--lang ru|uk]
    python3 validate.py density <path> [--lang ru|uk]
    python3 validate.py all <slug> [--lang ru|uk]  # Run all validators
"""

import argparse
from validate_meta import validate_meta_file
from validate_content import validate_content
from validate_seo import check_seo_structure
from validate_density import analyze_text

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # meta
    meta_parser = subparsers.add_parser("meta")
    meta_parser.add_argument("path")
    meta_parser.add_argument("--lang", default="ru")

    # content
    content_parser = subparsers.add_parser("content")
    content_parser.add_argument("path")
    content_parser.add_argument("keyword")
    content_parser.add_argument("--lang", default="ru")

    # seo
    seo_parser = subparsers.add_parser("seo")
    seo_parser.add_argument("path")
    seo_parser.add_argument("keyword")
    seo_parser.add_argument("--lang", default="ru")

    # density
    density_parser = subparsers.add_parser("density")
    density_parser.add_argument("path")
    density_parser.add_argument("--lang", default="ru")

    # all
    all_parser = subparsers.add_parser("all")
    all_parser.add_argument("slug")
    all_parser.add_argument("--lang", default="ru")

    args = parser.parse_args()
    # dispatch to validators...
```

### 3.7 audit_all.py (НОВЫЙ — объединение audit_*)

```python
"""
audit_all.py — Unified Audit Tool

Combines:
- audit_keyword_consistency.py
- audit_meta.py
- audit_synonyms.py

Usage:
    python3 audit_all.py keywords    # Keyword consistency
    python3 audit_all.py meta        # Meta audit
    python3 audit_all.py synonyms    # Synonyms audit
    python3 audit_all.py all         # Run all audits
"""
```

### 3.8 extract_ru_keywords_list.py (СОЗДАН ✅)

Извлечение всех RU ключей для аудита и экспорта.

```python
"""
extract_ru_keywords_list.py — Извлечение всех RU ключей из categories/

Сканирует categories/**/*_clean.json и извлекает:
- keywords[].keyword
- synonyms[].keyword
- variations[].keyword

Сохраняет уникальные ключи в data/generated/RU_KEYWORDS.md

Usage:
    python3 scripts/extract_ru_keywords_list.py
"""
```

**Возможности:**
- Обработка V3 формата (keywords — list)
- Обработка legacy формата (keywords — dict с группами)
- Создание data/generated/ если не существует
- Вывод статистики: файлов обработано, ключей найдено

**Результат:** `data/generated/RU_KEYWORDS.md` — один ключ на строку, сортировка по алфавиту

### 3.9 extract_uk_keywords_list.py (СОЗДАН ✅)

Извлечение всех UK ключей для аудита и экспорта.

```python
"""
extract_uk_keywords_list.py — Извлечение всех UK ключей из uk/categories/

Сканирует uk/categories/**/*_clean.json и извлекает:
- keywords[].keyword
- synonyms[].keyword
- variations[].keyword

Сохраняет уникальные ключи в data/generated/UK_KEYWORDS.md

Usage:
    python3 scripts/extract_uk_keywords_list.py
"""
```

**Возможности:**
- Обработка V3 формата (keywords — list)
- Обработка legacy формата (keywords — dict с группами)
- Создание data/generated/ если не существует
- Вывод статистики: файлов обработано, ключей найдено

**Результат:** `data/generated/UK_KEYWORDS.md` — один ключ на строку, сортировка по алфавиту

---

## 4. План миграции (фазы)

### Фаза 1: text_utils.py (SSOT)

**Файлы:** 1 новый
**Риск:** Низкий

1. Создать `scripts/text_utils.py`
2. Перенести STOPWORDS_RU/UK из `check_keyword_density.py`
3. Перенести `clean_markdown()` из `seo_utils.py` (canonical)
4. Перенести `extract_h1/h2s/intro` из `validate_content.py`
5. Добавить `tokenize()` из `check_keyword_density.py`
6. Написать тесты для text_utils

### Фаза 2: Миграция импортов

**Файлы:** 5 изменений
**Риск:** Средний

1. `seo_utils.py`: удалить функции → import from text_utils
2. `check_keyword_density.py`: удалить → import from text_utils
3. `validate_content.py`: удалить → import from text_utils
4. `check_seo_structure.py`: удалить → import from text_utils
5. Запустить все тесты

### Фаза 3: UK поддержка в validate_meta.py

**Файлы:** 1 изменение
**Риск:** Средний

1. Добавить UK patterns
2. Добавить --lang параметр
3. Обновить find_all_meta_files() для UK
4. Тесты с UK мета файлами

### Фаза 4: UK поддержка в validate_content.py

**Файлы:** 1 изменение
**Риск:** Средний

1. Добавить detect_language()
2. Обновить check_quality() с lang
3. Обновить check_content_standards() с UK patterns
4. Тесты с UK контентом

### Фаза 5: Переименование скриптов

**Файлы:** 3 переименования
**Риск:** Низкий

1. `check_seo_structure.py` → `validate_seo.py`
2. `check_keyword_density.py` → `validate_density.py`
3. Обновить импорты в skills

### Фаза 6: validate.py (Unified CLI)

**Файлы:** 1 новый
**Риск:** Низкий

1. Создать `scripts/validate.py`
2. Реализовать subcommands
3. Обновить CLAUDE.md с новыми командами

### Фаза 7: Архивирование

**Файлы:** перемещения
**Риск:** Низкий

1. Создать `scripts/archive/`
2. Переместить `validate_uk.py` → archive
3. Переместить старые audit_* → archive
4. Переместить одноразовые fix_*, migrate_* → archive

### Фаза 8: audit_all.py

**Файлы:** 1 новый
**Риск:** Низкий

1. Создать `scripts/audit_all.py`
2. Объединить audit_keyword_consistency, audit_meta, audit_synonyms
3. Переместить старые версии в archive

---

## 5. Файлы для архивирования

После миграции переместить в `scripts/archive/`:

**Валидаторы (заменены):**
- `validate_uk.py` → заменён --lang uk в validate_meta/content
- `check_seo_structure.py` → переименован в validate_seo.py
- `check_keyword_density.py` → переименован в validate_density.py

**Аудит (объединены):**
- `audit_keyword_consistency.py` → в audit_all.py
- `audit_meta.py` → в audit_all.py
- `audit_synonyms.py` → в audit_all.py

**Одноразовые:**
- `fix_csv_structure.py`
- `fix_keywords_order.py`
- `fix_missing_keywords.py`
- `fix_structure_and_legacy_json.py`
- `fix_structure_orphans.py`
- `migrate_keywords.py`
- `cleanup_misplaced.py`

**Legacy:**
- `restore_from_csv.py`
- `transform_structure_alignment.py`

---

## 6. Обновления CLAUDE.md

После миграции обновить:

```markdown
## Команды

```bash
# Валидация (NEW)
python3 scripts/validate.py meta <path> [--lang uk]
python3 scripts/validate.py content <path> "<keyword>" [--lang uk]
python3 scripts/validate.py seo <path> "<keyword>" [--lang uk]
python3 scripts/validate.py density <path> [--lang uk]
python3 scripts/validate.py all <slug> [--lang uk]

# Аудит (NEW)
python3 scripts/audit_all.py keywords
python3 scripts/audit_all.py meta
python3 scripts/audit_all.py all

# Экспорт ключей (NEW)
python3 scripts/extract_ru_keywords_list.py  # → data/generated/RU_KEYWORDS.md
python3 scripts/extract_uk_keywords_list.py  # → data/generated/UK_KEYWORDS.md
```
```

---

## 7. Тестирование

### Unit Tests

Добавить/обновить:
- `tests/unit/test_text_utils.py` — новый
- `tests/unit/test_validate_meta.py` — добавить UK тесты
- `tests/unit/test_validate_content.py` — добавить UK тесты
- `tests/unit/test_validate_seo.py` — новый (из test_check_seo_structure)
- `tests/unit/test_validate_density.py` — новый

### Integration Tests

- Прогнать все валидаторы на существующих категориях
- Проверить UK категории с --lang uk
- Проверить unified CLI

---

## 8. Оценка объёма работ

| Фаза | Сложность | Файлы |
|------|-----------|-------|
| 1. text_utils.py | Средняя | 1 новый |
| 2. Миграция импортов | Средняя | 5 изменений |
| 3. UK в validate_meta | Средняя | 1 изменение |
| 4. UK в validate_content | Средняя | 1 изменение |
| 5. Переименования | Низкая | 3 файла |
| 6. validate.py CLI | Низкая | 1 новый |
| 7. Архивирование | Низкая | ~15 перемещений |
| 8. audit_all.py | Низкая | 1 новый |
| ✅ extract_*_keywords_list.py | Завершено | 2 созданы |

**Итого:** ~8 новых/изменённых файлов + ~15 архивирований + 2 уже созданы

---

## 9. Зависимости между фазами

```
Фаза 1 (text_utils)
    ↓
Фаза 2 (миграция импортов)
    ↓
┌───────────────┬───────────────┐
Фаза 3         Фаза 4          Фаза 5
(UK meta)      (UK content)    (переименования)
└───────────────┴───────────────┘
    ↓
Фаза 6 (validate.py CLI)
    ↓
Фаза 7 (архивирование)
    ↓
Фаза 8 (audit_all.py)
```

Фазы 3, 4, 5 можно выполнять параллельно после Фазы 2.

---

**Готово к имплементации:** Да / Нет
