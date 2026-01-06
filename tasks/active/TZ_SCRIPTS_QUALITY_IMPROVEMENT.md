# ТЗ: Улучшение качества скриптов (Phase 2)

**Дата:** 2026-01-05  
**Статус:** 📝 План  
**Prerequisite:** ✅ TZ_SCRIPTS_REFACTORING.md (52→36)

---

## 🎯 Цели

После структурной консолидации (Phase 1) переходим к улучшению качества кода:

1. **Надежность** — тесты для критических функций (TDD где возможно)
2. **Типобезопасность** — полная типизация, проверка mypy
3. **Поддерживаемость** — чистая архитектура, документация
4. **Производительность** — профилирование и оптимизация узких мест
5. **CI/CD** — автоматизация проверок

---

## 📊 Текущее состояние

| Метрика            | Значение  | Цель             |
| ------------------ | --------- | ---------------- |
| **Скриптов**       | 36        | 36               |
| **С тестами**      | 0         | 20+ (core)       |
| **Type hints**     | ~30%      | 100%             |
| **MyPy чистые**    | 0         | 100%             |
| **Документация**   | Частичная | Полная           |
| **Error handling** | Базовый   | Продакшн-готовый |

---

## 🧪 Фаза 1: Тестирование (TDD для новых, Tests для старых)

### Приоритет А: Критические скрипты (Must Have Tests)

Эти скрипты используются в пайплайне и могут сломать весь процесс.

| #   | Скрипт                       | Тест-кейсы                                             | Приоритет   |
| --- | ---------------------------- | ------------------------------------------------------ | ----------- |
| 1   | `config.py`                  | Загрузка констант, валидация путей                     | 🔴 Critical |
| 2   | `seo_utils.py`               | `slugify()`, `clean_markdown()`, `normalize_keyword()` | 🔴 Critical |
| 3   | `validate_content.py`        | Все проверки (structure, keywords, quality)            | 🔴 Critical |
| 4   | `validate_meta.py`           | Title/Desc length, keyword presence                    | 🔴 Critical |
| 5   | `csv_to_readable_md.py`      | Парсинг CSV, генерация STRUCTURE.md                    | 🟡 High     |
| 6   | `parse_semantics_to_json.py` | CSV→JSON конвертация                                   | 🟡 High     |
| 7   | `synonym_tools.py`           | Нормализация, дедупликация                             | 🟡 High     |
| 8   | `generate_sql.py`            | MD→HTML, SQL escaping                                  | 🟡 High     |

### Структура тестов

```
tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures
├── test_config.py
├── test_seo_utils.py
│   ├── test_slugify()
│   ├── test_clean_markdown()
│   ├── test_normalize_keyword()
│   └── test_count_words()
├── test_validate_content.py
│   ├── test_check_structure()
│   ├── test_check_primary_keyword()
│   └── test_check_quality()
├── test_validate_meta.py
├── test_csv_parser.py
├── test_synonym_tools.py
└── fixtures/
    ├── sample_category.json
    ├── sample_content.md
    ├── sample_csv.csv
    └── expected_outputs/
```

### Пример теста (TDD Style)

```python
# tests/test_seo_utils.py
import pytest
from scripts.seo_utils import slugify, clean_markdown, normalize_keyword

class TestSlugify:
    """Тесты для функции slugify (транслитерация)."""

    def test_basic_cyrillic(self):
        assert slugify("Активная пена") == "aktivnaya-pena"

    def test_ukrainian_letters(self):
        assert slugify("Очищувач скла") == "ochyshchuvach-skla"

    def test_special_chars_removal(self):
        assert slugify("Товар №1 (новый)") == "tovar-1-novyy"

    def test_empty_string(self):
        assert slugify("") == ""

    def test_only_spaces(self):
        assert slugify("   ") == ""

    @pytest.mark.parametrize("input,expected", [
        ("Купить воск", "kupit-vosk"),
        ("L'oreal Paris", "loreal-paris"),
        ("100% результат", "100-rezultat"),
    ])
    def test_edge_cases(self, input, expected):
        assert slugify(input) == expected


class TestCleanMarkdown:
    """Тесты для очистки Markdown от HTML/форматирования."""

    def test_remove_headers(self):
        assert clean_markdown("# Title\nText") == "Text"

    def test_remove_bold(self):
        assert clean_markdown("**bold** text") == "bold text"

    def test_preserve_content(self):
        text = "Plain text without formatting"
        assert clean_markdown(text) == text
```

### Запуск тестов

```bash
# Установка
pip install pytest pytest-cov pytest-mock

# Запуск всех тестов
pytest tests/ -v

# С покрытием
pytest tests/ --cov=scripts --cov-report=html

# Только критические
pytest tests/ -m critical

# Watch mode (TDD)
pytest-watch tests/
```

---

## 🔍 Фаза 2: Типизация (Type Safety)

### Текущие проблемы

```python
# ❌ ПЛОХО: Без типов
def validate_meta_file(meta_path, keywords_path=None):
    data = json.load(open(meta_path))
    return data

# ✅ ХОРОШО: С типами
def validate_meta_file(
    meta_path: str | Path,
    keywords_path: str | Path | None = None
) -> dict[str, Any]:
    """
    Validates meta JSON file.

    Args:
        meta_path: Path to meta JSON
        keywords_path: Optional path to keywords JSON

    Returns:
        Validation results with status and errors

    Raises:
        FileNotFoundError: If meta_path doesn't exist
        JSONDecodeError: If file is not valid JSON
    """
    with open(meta_path, encoding="utf-8") as f:
        data = json.load(f)
    return data
```

### План типизации

| Скрипт             | Текущий % | Целевой % | Действия                        |
| ------------------ | --------- | --------- | ------------------------------- |
| `config.py`        | 80%       | 100%      | Добавить TypedDict для конфигов |
| `seo_utils.py`     | 40%       | 100%      | Все функции + перегрузки        |
| `validate_*.py`    | 20%       | 100%      | Typed returns, exceptions       |
| `synonym_tools.py` | 0%        | 100%      | С нуля (новый скрипт)           |
| `products.py`      | 0%        | 100%      | С нуля                          |
| `competitors.py`   | 0%        | 100%      | С нуля                          |

### Настройка MyPy

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_calls = true
disallow_any_generics = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true

[[tool.mypy.overrides]]
module = ["natasha.*", "pymorphy2.*", "pandas.*"]
ignore_missing_imports = true
```

### Проверка

```bash
# До фикса
mypy scripts/  # 285 errors

# После фикса
mypy scripts/  # 0 errors
```

---

## 🏗️ Фаза 3: Архитектурные улучшения

### 3.1 Разделение на модули

Текущая проблема: `seo_utils.py` содержит 1084 строки разнородного кода.

**Решение:** Разбить на модули по доменам.

```
scripts/
├── core/
│   ├── __init__.py
│   ├── config.py          # Конфиги (было: scripts/config.py)
│   ├── paths.py           # Path resolvers
│   └── exceptions.py      # Custom exceptions
│
├── text/
│   ├── __init__.py
│   ├── transliteration.py # slugify, translit
│   ├── normalization.py   # clean_markdown, normalize
│   ├── analysis.py        # count_words, keyword_density
│   └── nlp.py            # Natasha integrations
│
├── validators/
│   ├── __init__.py
│   ├── meta.py           # Meta validation
│   ├── content.py        # Content validation
│   └── structure.py      # Structure checks
│
├── parsers/
│   ├── __init__.py
│   ├── csv_parser.py     # CSV handling
│   └── json_generator.py # JSON generation
│
└── utils/
    ├── __init__.py
    ├── io.py             # File I/O helpers
    └── logging.py        # Logging setup
```

### 3.2 Dependency Injection

```python
# ❌ ПЛОХО: Жесткая зависимость
def validate_content(file_path: str):
    config = load_config()  # Глобальное состояние
    threshold = config.WATER_TARGET_MAX
    ...

# ✅ ХОРОШО: DI через параметры
def validate_content(
    file_path: str,
    config: ValidationConfig,
    logger: logging.Logger | None = None
):
    threshold = config.water_target_max
    ...

# Использование
config = ValidationConfig.from_file("config.toml")
logger = setup_logger("validate_content")
validate_content("file.md", config, logger)
```

### 3.3 Error Handling

```python
# core/exceptions.py
class SEOValidationError(Exception):
    """Base exception for SEO validation errors."""
    pass

class MetaValidationError(SEOValidationError):
    """Meta tags validation failed."""
    pass

class ContentValidationError(SEOValidationError):
    """Content validation failed."""
    pass

# Использование
def validate_meta_file(path: Path) -> ValidationResult:
    if not path.exists():
        raise FileNotFoundError(f"Meta file not found: {path}")

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise MetaValidationError(f"Invalid JSON: {e}") from e

    # Validation logic...
    return ValidationResult(status="OK", errors=[])
```

---

## 📝 Фаза 4: Документация

### 4.1 Docstrings (Google Style)

```python
def analyze_category(slug: str, lang: str = "ru") -> CategoryAnalysis:
    """
    Performs full category analysis for LLM content generation.

    This function loads keywords using the D+E fallback pattern,
    splits them by intent (core vs commercial), and generates
    content guidelines based on SEO rules.

    Args:
        slug: Category slug (e.g., 'aktivnaya-pena')
        lang: Language code ('ru' or 'uk')

    Returns:
        CategoryAnalysis object containing:
            - keywords: Dict of categorized keywords
            - intent_split: Core vs commercial breakdown
            - guidelines: Content generation recommendations

    Raises:
        FileNotFoundError: If category data directory doesn't exist
        ValueError: If lang is not 'ru' or 'uk'

    Examples:
        >>> analysis = analyze_category("aktivnaya-pena")
        >>> print(analysis.keywords['primary'])
        [{'keyword': 'активная пена', 'volume': 1300}, ...]

        >>> analysis = analyze_category("dlya-ruchnoy-moyki", lang="uk")
        >>> print(analysis.intent_split)
        {'core': 15, 'commercial': 8}
    """
    if lang not in ("ru", "uk"):
        raise ValueError(f"Invalid language: {lang}")

    # Implementation...
```

### 4.2 README для каждого модуля

````markdown
# scripts/validators/

Модуль валидации контента и метаданных.

## Модули

-   `meta.py` — Валидация Title/Description/H1
-   `content.py` — Валидация структуры и качества контента
-   `structure.py` — Проверка файловой структуры

## Использование

```python
from scripts.validators.meta import validate_meta_file

result = validate_meta_file("categories/slug/meta/slug_meta.json")
if result.status == "FAIL":
    print(f"Errors: {result.errors}")
```
````

## Exit Codes

-   `0` — PASS
-   `1` — WARNING
-   `2` — FAIL

````

---

## ⚡ Фаза 5: Производительность

### 5.1 Профилирование

```python
# Добавить в критические скрипты
import cProfile
import pstats

def profile_function(func):
    """Decorator для профилирования."""
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumtime')
        stats.print_stats(10)  # Top 10
        return result
    return wrapper

@profile_function
def validate_all_categories():
    # Heavy operation...
````

### 5.2 Оптимизации

| Проблема                   | Решение                       | Выигрыш |
| -------------------------- | ----------------------------- | ------- |
| Многократное чтение файлов | Кэширование с `@lru_cache`    | 5-10x   |
| Синхронные операции I/O    | `asyncio` для батчей          | 3-5x    |
| Regex без компиляции       | `re.compile()` + reuse        | 2x      |
| JSON без streaming         | `ijson` для больших файлов    | Memory  |
| Pandas без chunksize       | `pd.read_csv(chunksize=1000)` | Memory  |

### 5.3 Пример оптимизации

```python
# ❌ ПЛОХО: Читает файл 100 раз
for slug in categories:
    config = json.load(open("config.json"))
    process(slug, config)

# ✅ ХОРОШО: Читает 1 раз
from functools import lru_cache

@lru_cache(maxsize=1)
def load_config():
    return json.load(open("config.json"))

for slug in categories:
    config = load_config()
    process(slug, config)
```

---

## 🔄 Фаза 6: CI/CD Integration

### 6.1 GitHub Actions / GitLab CI

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
    test:
        runs-on: ubuntu-latest
        steps:
            - uses: actions/checkout@v3
            - uses: actions/setup-python@v4
              with:
                  python-version: "3.12"

            - name: Install dependencies
              run: |
                  pip install -r requirements.txt
                  pip install -r requirements-dev.txt

            - name: Run tests
              run: pytest tests/ --cov=scripts --cov-report=xml

            - name: Type check
              run: mypy scripts/

            - name: Lint
              run: ruff check scripts/

            - name: Upload coverage
              uses: codecov/codecov-action@v3
```

### 6.2 Pre-commit updates

```yaml
# .pre-commit-config.yaml
repos:
    # ... existing hooks ...

    - repo: local
      hooks:
          - id: pytest-check
            name: pytest-check
            entry: pytest tests/ -x
            language: system
            pass_filenames: false
            always_run: true
```

---

## 📋 План выполнения (Roadmap)

### Sprint 1: Тестирование базы (1 неделя)

-   [ ] Настроить pytest + fixtures
-   [ ] Написать тесты для `seo_utils.py` (10+ функций)
-   [ ] Написать тесты для `config.py`
-   [ ] Coverage ≥ 60% для core модулей

### Sprint 2: Критические валидаторы (1 неделя)

-   [ ] Тесты для `validate_content.py`
-   [ ] Тесты для `validate_meta.py`
-   [ ] Интеграционные тесты (end-to-end)
-   [ ] Coverage ≥ 75%

### Sprint 3: Типизация (3-5 дней)

-   [ ] Добавить type hints во все функции
-   [ ] Настроить mypy (strict mode)
-   [ ] Исправить все 285 ошибок mypy
-   [ ] Добавить mypy в CI

### Sprint 4: Рефакторинг архитектуры (1 неделя)

-   [ ] Разбить `seo_utils.py` на модули
-   [ ] Внедрить DI где возможно
-   [ ] Создать custom exceptions
-   [ ] Обновить импорты во всех скриптах

### Sprint 5: Документация + CI (2-3 дня)

-   [ ] Docstrings для всех публичных функций
-   [ ] README для каждого модуля
-   [ ] Настроить GitHub Actions
-   [ ] Pre-commit hooks update

---

## ✅ Критерии успеха

| Метрика       | До  | После      |
| ------------- | --- | ---------- |
| Test Coverage | 0%  | **≥80%**   |
| MyPy Errors   | 285 | **0**      |
| Type Hints    | 30% | **100%**   |
| Docstrings    | 40% | **100%**   |
| CI/CD         | ❌  | ✅         |
| Build Time    | N/A | **<5 min** |

---

## 🎓 Обучение команды

### Ресурсы

1. **TDD**: [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)
2. **Type Hints**: [mypy docs](https://mypy.readthedocs.io/)
3. **Clean Architecture**: [Architecture Patterns with Python](https://www.cosmicpython.com/)
4. **Pytest**: [pytest docs](https://docs.pytest.org/)

### Best Practices

-   **Red-Green-Refactor** для новых фич
-   **Test Pyramid**: 70% unit, 20% integration, 10% e2e
-   **Type-first development** для новых модулей
-   **Code review** перед каждым merge в main

---

## 🚨 Риски

| Риск                     | Вероятность | Митигация                                    |
| ------------------------ | ----------- | -------------------------------------------- |
| Сломать существующий код | Высокая     | Полное тестовое покрытие **до** рефакторинга |
| MyPy слишком строгий     | Средняя     | Постепенное включение strict checks          |
| Производительность       | Низкая      | Профилирование + benchmark tests             |
| Время на реализацию      | Средняя     | Поэтапный rollout, не всё сразу              |

---

## 💡 Следующие шаги

1. **Утвердить план** с командой
2. **Создать ветку** `feature/scripts-quality-improvement`
3. **Sprint 1**: Начать с тестов для `seo_utils.py`
4. **Weekly sync**: Tracking прогресса

**Estimated Time**: 4-5 недель (1 dev full-time)

**ROI**: Меньше багов в продакшене, быстрая разработка новых фич, легкая onboarding новых разработчиков.
