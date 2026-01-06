# ТЗ: Покрытие скриптов проекта тестами (TDD)

**Дата создания:** 2026-01-05  
**Статус:** 🚧 Draft  
**Приоритет:** High  
**Владелец:** DevOps/QA

---

## 1. 🎯 Цели и Задачи

### Цель

Обеспечить стабильность и надёжность пайплайна генерации SEO-контента путём создания комплексного покрытия тестами всех критических скриптов проекта.

### Задачи

1. **Анализ текущего состояния** — провести аудит существующих тестов
2. **Приоритизация** — определить критичность скриптов для покрытия
3. **Разработка тестов** — создать unit и integration тесты
4. **CI/CD интеграция** — настроить автоматический запуск тестов
5. **Документация** — описать best practices и примеры

---

## 2. 📊 Текущее состояние (Audit)

### 2.1 Существующие тесты

| Тестовый файл                     | Покрываемый скрипт           | Оценка качества | Покрытие |
| --------------------------------- | ---------------------------- | --------------- | -------- |
| `test_seo_utils.py`               | `seo_utils.py`               | ⭐⭐⭐ Good     | ~15%     |
| `test_validate_content.py`        | `validate_content.py`        | ⭐⭐ Partial    | ~20%     |
| `test_validate_meta.py`           | `validate_meta.py`           | ⭐⭐ Partial    | ~25%     |
| `test_parse_semantics_to_json.py` | `parse_semantics_to_json.py` | ⭐⭐ Partial    | ~30%     |
| `test_fix_csv_structure.py`       | `fix_csv_structure.py`       | ⭐⭐ Partial    | ~40%     |
| `test_config.py`                  | `config.py`                  | ⭐⭐⭐ Good     | ~60%     |
| `test_check_ner_brands.py`        | `check_ner_brands.py`        | ⭐ Minimal      | ~10%     |
| `test_check_water_natasha.py`     | `check_water_natasha.py`     | ⭐ Minimal      | ~10%     |
| `test_synonym_tools.py`           | `synonym_tools.py`           | ⭐⭐ Partial    | ~20%     |

**Общее покрытие проекта:** ~18% (по экспертной оценке)

### 2.2 Скрипты БЕЗ тестов (Critical Gap)

#### 🔴 Критический приоритет (необходимы тесты ASAP)

1. `analyze_category.py` — 751 строк, сложная логика анализа
2. `batch_generate.py` — 22915 строк (!)
3. `csv_to_readable_md.py` — генератор структуры, ключевой скрипт
4. `generate_checklists.py` — автоматизация задач
5. `upload_to_db.py` — критичен для деплоя

#### 🟡 Средний приоритет (желательны тесты)

6. `check_seo_structure.py`
7. `check_h1_sync.py`
8. `check_cannibalization.py`
9. `find_duplicates.py`
10. `find_orphan_keywords.py`
11. `migrate_keywords.py`
12. `restore_from_csv.py`
13. `compare_raw_clean.py`

#### 🟢 Низкий приоритет (опциональные тесты)

14. `md_to_html.py` — простая конвертация
15. `generate_sql.py`
16. `show_keyword_distribution.py`
17. `cleanup_misplaced.py`
18. `export_uk_category_texts.py`
19. `uk_seed_from_ru.py`
20. `url_filters.py`
21. `products.py`
22. `competitors.py`
23. `setup_all.py`
24. `verify_structural_integrity.py`
25. `validate_uk.py`

---

## 3. 🏗️ Архитектура тестирования

### 3.1 Принципы

#### TDD (Test-Driven Development)

-   **Red → Green → Refactor** цикл
-   Тесты пишутся **до** кода (для новых функций)
-   Тесты — это спецификация поведения

#### DRY для тестов

-   Общие фикстуры в `conftest.py`
-   Параметризованные тесты (`@pytest.mark.parametrize`)
-   Вспомогательные функции в `tests/helpers/`

#### Категории тестов

1. **Unit Tests** — изолированные функции (без I/O)
2. **Integration Tests** — взаимодействие с файлами/БД
3. **Smoke Tests** — быстрая проверка работоспособности

### 3.2 Структура директории `tests/`

```
tests/
├── README.md                      # Документация
├── conftest.py                    # Глобальные фикстуры
├── pytest.ini                     # Конфигурация (уже есть)
├── .coveragerc                    # Coverage настройки (уже есть)
│
├── fixtures/                      # Тестовые данные
│   ├── csv/                       # Образцы CSV файлов
│   │   ├── valid_structure.csv
│   │   ├── invalid_structure.csv
│   │   └── edge_case_structure.csv
│   ├── json/                      # Образцы JSON
│   │   ├── valid_meta.json
│   │   ├── valid_clean.json
│   │   └── invalid_meta.json
│   ├── md/                        # Образцы Markdown контента
│   │   ├── valid_content_ru.md
│   │   ├── valid_content_uk.md
│   │   ├── invalid_structure.md
│   │   └── missing_keywords.md
│   └── expected/                  # Ожидаемые результаты
│       ├── structure_output.md
│       └── validation_report.json
│
├── helpers/                       # Вспомогательные утилиты для тестов
│   ├── __init__.py
│   ├── file_builders.py           # Билдеры тестовых файлов
│   ├── assertions.py              # Кастомные ассерты
│   └── mocks.py                   # Моки для LLM/DB
│
├── unit/                          # Unit-тесты (быстрые, изолированные)
│   ├── test_seo_utils.py          # ✅ Уже есть (переместить сюда)
│   ├── test_config.py             # ✅ Уже есть
│   ├── test_text_processing.py    # Новый (normalize, clean, count)
│   ├── test_slugify.py            # Новый (выделить из seo_utils)
│   ├── test_keyword_analysis.py   # Новый (анализ ключей)
│   └── test_coverage_calculations.py  # Новый
│
├── integration/                   # Интеграционные тесты (с I/O)
│   ├── test_csv_parser.py         # Парсинг CSV → JSON
│   ├── test_structure_generator.py # csv_to_readable_md
│   ├── test_validation_flow.py    # validate_meta + validate_content
│   ├── test_category_analysis.py  # analyze_category полный флоу
│   └── test_db_upload.py          # upload_to_db (с тестовой БД)
│
└── e2e/                           # End-to-End тесты (полный пайплайн)
    ├── test_full_pipeline.py      # CSV → Analysis → Content → Validation → DB
    └── test_batch_generate.py     # Batch генерация категорий
```

---

## 4. 📋 План реализации

### Phase 1: Foundation (Week 1-2)

**Цель:** Создать инфраструктуру и покрыть критичные утилиты

#### Week 1: Инфраструктура

-   [x] **Задача 1.1** Реорганизация `tests/`

    -   Создать `unit/`, `integration/`, `e2e/` директории
    -   Создать `fixtures/` с поддиректориями
    -   Создать `helpers/` модуль
    -   Переместить существующие тесты в `unit/`

-   [x] **Задача 1.2** Расширить `conftest.py`

    -   Фикстура `tmp_category_dir` — временная категория для тестов
    -   Фикстура `sample_csv_data` — валидные CSV данные
    -   Фикстура `sample_keywords` — список ключевых слов
    -   Фикстура `mock_llm_response` — мок для LLM

-   [x] **Задача 1.3** Создать `helpers/file_builders.py`

    ```python
    class CategoryBuilder:
        """Билдер для создания тестовых категорий"""
        def with_meta(self, **kwargs) -> Self
        def with_content(self, text: str) -> Self
        def with_keywords(self, keywords: list) -> Self
        def build(self, tmp_path: Path) -> Path
    ```

-   [x] **Задача 1.4** Создать базовые фикстуры
    -   `fixtures/csv/valid_structure.csv`
    -   `fixtures/json/valid_meta.json`
    -   `fixtures/md/valid_content_ru.md`

#### Week 2: Core Utils Coverage (приоритет 🔴)

-   [x] **Задача 2.1** `test_seo_utils.py` — расширить до 80%+ coverage

    -   [x] Тесты на `clean_markdown` (edge cases)
    -   [x] Тесты на `normalize_text` (спецсимволы, эмодзи)
    -   [x] Тесты на `count_words` (вся логика)
    -   [x] Тесты на `parse_front_matter` (валидный/инвалидный YAML)
    -   [x] Тесты на `slugify` (кириллица, украинский, edge cases)
    -   [x] **New:** Тесты на `load_json` / `save_json`

-   [x] **Задача 2.2** `test_parse_semantics_to_json.py` — расширить до 60%+

    -   [x] Тесты на парсинг CSV структуры Level1/Level2/Level3
    -   [x] Тесты на обработку пустых строк
    -   [ ] Тесты на некорректный формат
    -   [x] Интеграционный тест: CSV → JSON → валидация структуры

-   [ ] **Задача 2.3** `test_fix_csv_structure.py` — расширить до 70%+
    -   Тесты на детекцию ложных заголовков
    -   Тесты на нормализацию
    -   Тесты на сохранение валидных данных

### Phase 2: Validation Layer (Week 3-4)

**Цель:** Покрыть валидаторы (Quality Gate)

-   [x] **Задача 3.1** `test_validate_content.py` — расширить до 70%+

    -   [x] Unit тесты на каждую функцию проверки:
        -   `check_structure()`
        -   `check_primary_keyword()`
        -   `check_keyword_coverage()`
        -   `check_quality()`
        -   `check_blacklist_phrases()`
    -   [x] Параметризованные тесты для edge cases
    -   [ ] Тесты на режимы `--mode quality` vs `--mode seo`

-   [x] **Задача 3.2** `test_validate_meta.py` — расширить до 70%+

    -   [x] Тесты на проверку Title (length, format, keywords)
    -   [x] Тесты на проверку Description (length, commercial)
    -   [ ] Тесты на проверку H1 (uniqueness vs Title)

-   [ ] **Задача 3.3** Новый: `test_validate_uk.py`
    -   Тесты на соответствие RU ↔ UK версий
    -   Тесты на наличие украинских стоп-слов

### Phase 3: Analysis & Generation (Week 5-6)

**Цель:** Покрыть скрипты анализа и генерации

-   [ ] **Задача 4.1** Новый: `test_analyze_category.py` (integration)

    -   Тест загрузки keywords (D+E Fallback)
    -   Тест анализа семантики (`analyze_keywords`)
    -   Тест генерации guidelines (`generate_content_guidelines`)
    -   Интеграционный тест: slug → полный анализ → JSON output

-   [ ] **Задача 4.2** Новый: `test_csv_to_readable_md.py`

    -   Тест парсинга CSV
    -   Тест генерации Markdown структуры
    -   Тест валидации (Orphans detection)
    -   Snapshot тест (сравнение с эталонным STRUCTURE.md)

-   [ ] **Задача 4.3** Новый: `test_generate_checklists.py`

    -   Тест генерации MASTER_CHECKLIST.md
    -   Тест генерации category checklist
    -   Тест обновления PIPELINE_STATUS.md
    -   Тест на уникальность slugs (avoid duplicates)

-   [ ] **Задача 4.4** Новый: `test_batch_generate.py` (e2e, slow)
    -   Mock LLM ответов
    -   Тест генерации контента для тестовой категории
    -   Тест валидации сгенерированного контента
    -   Тест retry логики при ошибках

### Phase 4: Data Integrity & SEO Checks (Week 7-8)

**Цель:** Покрыть проверки качества данных

-   [ ] **Задача 5.1** Расширить `test_check_ner_brands.py`

    -   Тесты на детекцию брендов
    -   Тесты на false positives
    -   Тесты на кириллицу + латиницу

-   [ ] **Задача 5.2** Расширить `test_check_water_natasha.py`

    -   Тесты на подсчёт воды
    -   Тесты на стоп-слова
    -   Тесты на nausea calculations

-   [ ] **Задача 5.3** Новый: `test_check_cannibalization.py`

    -   Тест детекции пересечений интентов
    -   Тест расчёта similarity score
    -   Тест генерации рекомендаций

-   [ ] **Задача 5.4** Новый: `test_find_duplicates.py`

    -   Тест поиска дублей keywords между категориями
    -   Тест генерации отчёта
    -   Тест на edge cases (синонимы, склонения)

-   [ ] **Задача 5.5** Расширить `test_synonym_tools.py`
    -   Тест `report` команды
    -   Тест `cleanup` команды
    -   Тест детекции дублей синонимов

### Phase 5: Database & Deployment (Week 9)

**Цель:** Покрыть критичные скрипты деплоя

-   [ ] **Задача 6.1** Новый: `test_upload_to_db.py` (integration)

    -   Требует Docker с тестовой БД MySQL (или SQLite mock)
    -   Тест создания таблиц
    -   Тест загрузки категории
    -   Тест транзакций и rollback при ошибке
    -   **ВАЖНО:** Тесты изолированы, не трогают продакшн БД

-   [ ] **Задача 6.2** Новый: `test_generate_sql.py`
    -   Тест генерации SQL для meta
    -   Тест генерации SQL для content
    -   Тест SQL injection защиты (escaping)

### Phase 6: CI/CD Integration (Week 10)

**Цель:** Автоматизировать запуск тестов

-   [ ] **Задача 7.1** GitHub Actions workflow

    -   `.github/workflows/tests.yml`
    -   Запуск на каждый push в `develop`
    -   Запуск на каждый PR
    -   Генерация coverage report

-   [ ] **Задача 7.2** Pre-commit hook для тестов

    -   Добавить в `.pre-commit-config.yaml`:
        ```yaml
        - repo: local
          hooks:
              - id: pytest-check
                name: pytest-check
                entry: python -m pytest tests/unit --maxfail=1
                language: system
                pass_filenames: false
                always_run: true
        ```

-   [ ] **Задача 7.3** Coverage Badge
    -   Интеграция с codecov.io или coveralls
    -   Отображение badge в README.md

---

## 5. 🎯 KPI и метрики успеха

### Целевые метрики

| Метрика                       | Текущее | Цель Week 4 | Цель Week 8 | Цель Week 10 |
| ----------------------------- | ------- | ----------- | ----------- | ------------ |
| **Overall Coverage**          | ~18%    | 50%         | 70%         | 80%+         |
| **Critical Scripts Coverage** | ~10%    | 60%         | 80%         | 90%+         |
| **Unit Tests Count**          | 20      | 100         | 200         | 300+         |
| **Integration Tests Count**   | 5       | 15          | 30          | 50+          |
| **Test Execution Time**       | <5s     | <30s        | <60s        | <90s         |
| **Failed Tests on main**      | N/A     | 0           | 0           | 0            |

### Критичные скрипты для 80%+ coverage

-   `seo_utils.py` (библиотека всех утилит)
-   `validate_content.py` (Quality Gate)
-   `validate_meta.py` (Quality Gate)
-   `analyze_category.py` (анализ)
-   `csv_to_readable_md.py` (структура)
-   `upload_to_db.py` (деплой)

---

## 6. 🛠️ Технический стек

### Основные инструменты

-   **pytest** (~9.0) — тестовый фреймворк
-   **pytest-cov** (~7.0) — coverage измерение
-   **pytest-mock** — моки и патчи
-   **pytest-xdist** — параллельное выполнение
-   **faker** — генерация тестовых данных

### Дополнительные библиотеки

-   **responses** — мок HTTP запросов (для LLM API)
-   **freezegun** — мок времени/дат
-   **testcontainers** — Docker контейнеры для БД тестов

### Конфигурация pytest

```ini
[pytest]
# Test discovery
python_files = test_*.py
python_classes = Test*
python_functions = test_*

testpaths = tests

# Markers
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    e2e: marks tests as end-to-end tests
    requires_db: marks tests requiring database

# Coverage
addopts =
    -v
    --tb=short
    --strict-markers
    --cov=scripts
    --cov-report=term-missing:skip-covered
    --cov-report=html:artifacts/pytest/htmlcov
    --cov-report=json:artifacts/pytest/coverage.json
    -m "not slow"  # По умолчанию skip slow тесты
```

---

## 7. 📝 Best Practices

### 7.1 Naming Conventions

```python
# ✅ Good
def test_slugify_converts_cyrillic_to_latin():
    assert slugify("Активная пена") == "aktivnaya-pena"

def test_validate_content_fails_when_missing_h1():
    result = validate_content(content_without_h1)
    assert result["status"] == "FAIL"

# ❌ Bad
def test1():
    ...

def test_validation():
    ...  # Что именно тестируем?
```

### 7.2 AAA Pattern (Arrange-Act-Assert)

```python
def test_keyword_coverage_calculates_correctly():
    # Arrange
    text = "Купить активную пену для бесконтактной мойки"
    keywords = ["активная пена", "бесконтактная мойка", "шампунь"]

    # Act
    result = check_keyword_coverage(text, keywords)

    # Assert
    assert result["coverage_percent"] == 66.67  # 2/3 keywords found
    assert result["found"] == ["активная пена", "бесконтактная мойка"]
    assert result["missing"] == ["шампунь"]
```

### 7.3 Параметризация

```python
@pytest.mark.parametrize(
    "input_text,expected_slug",
    [
        ("Активная пена", "aktivnaya-pena"),
        ("Очистители стёкол", "ochistiteli-stekol"),
        ("100% результат", "100-rezultat"),
        ("Киев/Украина", "kiev-ukraina"),
    ],
)
def test_slugify_edge_cases(input_text, expected_slug):
    assert slugify(input_text) == expected_slug
```

### 7.4 Фикстуры для DRY

```python
# conftest.py
@pytest.fixture
def valid_category_structure(tmp_path):
    """Создаёт валидную структуру категории для тестов"""
    category_dir = tmp_path / "categories" / "aktivnaya-pena"
    category_dir.mkdir(parents=True)

    meta_dir = category_dir / "meta"
    meta_dir.mkdir()

    meta_file = meta_dir / "aktivnaya-pena_meta.json"
    meta_file.write_text(json.dumps({
        "title": "Купить активную пену | Ultimate",
        "description": "Активная пена для бесконтактной мойки...",
        "h1": "Активная пена для мойки автомобиля"
    }))

    return category_dir

# test_validate_meta.py
def test_validate_meta_passes_for_valid_structure(valid_category_structure):
    meta_file = valid_category_structure / "meta" / "aktivnaya-pena_meta.json"
    result = validate_meta(meta_file)
    assert result["status"] == "PASS"
```

### 7.5 Использование Mocks для внешних зависимостей

```python
from unittest.mock import patch, MagicMock

@patch("scripts.batch_generate.call_llm_api")
def test_batch_generate_retries_on_failure(mock_llm_api):
    # Arrange
    mock_llm_api.side_effect = [
        Exception("API Error"),  # First call fails
        Exception("API Error"),  # Second call fails
        {"content": "Generated text"}  # Third call succeeds
    ]

    # Act
    result = generate_content_with_retry(prompt="test", max_retries=3)

    # Assert
    assert result["content"] == "Generated text"
    assert mock_llm_api.call_count == 3
```

---

## 8. 🚀 Быстрый старт для разработчиков

### Установка зависимостей тестирования

```bash
pip install -r requirements-dev.txt
```

### Запуск всех тестов

```bash
python -m pytest
```

### Запуск только unit-тестов (быстро)

```bash
python -m pytest tests/unit -v
```

### Запуск с coverage отчётом

```bash
python -m pytest --cov=scripts --cov-report=html
# Открыть artifacts/pytest/htmlcov/index.html
```

### Запуск конкретного теста

```bash
python -m pytest tests/unit/test_seo_utils.py::TestSlugify::test_basic_cyrillic -v
```

### Запуск с игнорированием slow тестов

```bash
python -m pytest -m "not slow"
```

### Запуск только integration тестов

```bash
python -m pytest -m integration
```

---

## 9. 📚 Примеры тестов

### Пример 1: Unit Test (isolate function)

```python
# tests/unit/test_keyword_analysis.py
import pytest
from scripts.seo_utils import split_keywords_by_intent

class TestSplitKeywordsByIntent:
    def test_splits_commercial_keywords(self):
        keywords = [
            {"keyword": "активная пена", "volume": 1200},
            {"keyword": "купить активную пену", "volume": 500},
            {"keyword": "цена активной пены", "volume": 300},
        ]

        core, commercial = split_keywords_by_intent(keywords, lang="ru")

        assert len(core) == 1
        assert core[0]["keyword"] == "активная пена"
        assert len(commercial) == 2
        assert "купить" in commercial[0]["keyword"].lower()

    def test_handles_empty_list(self):
        core, commercial = split_keywords_by_intent([], lang="ru")
        assert core == []
        assert commercial == []

    @pytest.mark.parametrize("lang", ["ru", "uk"])
    def test_supports_multiple_languages(self, lang):
        keywords = [{"keyword": "тест", "volume": 100}]
        core, commercial = split_keywords_by_intent(keywords, lang=lang)
        assert len(core) == 1
```

### Пример 2: Integration Test (file I/O)

```python
# tests/integration/test_structure_generator.py
import pytest
from pathlib import Path
from scripts.csv_to_readable_md import parse_csv, generate_structure_md

class TestStructureGenerator:
    @pytest.fixture
    def sample_csv_file(self, tmp_path):
        csv_content = """Level1,Level2,Level3,Keyword,Volume
Мойка и Экстерьер,Автошампуни,Активная пена,активная пена,1200
Мойка и Экстерьер,Автошампуни,Активная пена,купить активную пену,500
"""
        csv_file = tmp_path / "test_structure.csv"
        csv_file.write_text(csv_content, encoding="utf-8")
        return csv_file

    def test_parses_csv_and_generates_markdown(self, sample_csv_file, tmp_path):
        # Act
        structure = parse_csv(sample_csv_file)
        output_file = tmp_path / "STRUCTURE.md"
        generate_structure_md(structure, output_file)

        # Assert
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert "## L1: Мойка и Экстерьер" in content
        assert "### L2: Автошампуни" in content
        assert "#### L3: Активная пена" in content
        assert "активная пена" in content
        assert "1200" in content
```

### Пример 3: E2E Test (full pipeline)

```python
# tests/e2e/test_full_pipeline.py
import pytest
from pathlib import Path
from scripts.analyze_category import analyze_category
from scripts.validate_content import validate_content_file
from scripts.upload_to_db import upload_category

@pytest.mark.slow
@pytest.mark.e2e
class TestFullCategoryPipeline:
    @pytest.fixture
    def test_category(self, tmp_path):
        # Setup full category structure
        category = CategoryBuilder()\
            .with_slug("test-category")\
            .with_keywords(["тест", "категория"])\
            .with_meta(title="Test Title")\
            .with_content("# Test\\n\\nTest content")\
            .build(tmp_path)
        return category

    def test_complete_pipeline_from_analysis_to_upload(self, test_category):
        slug = "test-category"

        # Step 1: Analyze
        analysis = analyze_category(slug)
        assert analysis["status"] == "success"

        # Step 2: Validate
        content_file = test_category / "content" / f"{slug}_ru.md"
        validation = validate_content_file(content_file, mode="seo")
        assert validation["overall"] == "PASS"

        # Step 3: Upload (mock)
        with patch("scripts.upload_to_db.get_db_connection"):
            result = upload_category(slug, dry_run=True)
            assert result["uploaded"] == True
```

---

## 10. ⚠️ Риски и Mitigation

| Риск                             | Вероятность | Влияние | Митигация                                                                        |
| -------------------------------- | ----------- | ------- | -------------------------------------------------------------------------------- |
| Медленные тесты (>2 min)         | Высокая     | Среднее | Использовать markers (`@pytest.mark.slow`), параллельный запуск (`pytest-xdist`) |
| Flaky тесты (нестабильные)       | Средняя     | Высокое | Изоляция тестов, моки для time/random, retry механизм                            |
| Тесты не ловят реальные баги     | Средняя     | Высокое | Code review тестов, mutation testing (опционально)                               |
| Покрытие растёт, качество падает | Низкая      | Среднее | Ревью качества тестов, assertion roulette prevention                             |
| Сложность поддержки тестов       | Средняя     | Среднее | DRY принципы, helper функции, документация                                       |

---

## 11. 📅 Timeline & Milestones

### Milestone 1: Foundation (Week 1-2)

-   **Deliverable:** Инфраструктура тестов готова
-   **Acceptance Criteria:**
    -   ✅ Структура `tests/` реорганизована
    -   ✅ Фикстуры созданы
    -   ✅ Helpers созданы
    -   ✅ `seo_utils.py` покрытие 80%+

### Milestone 2: Validation Layer (Week 3-4)

-   **Deliverable:** Валидаторы покрыты на 70%+
-   **Acceptance Criteria:**
    -   ✅ `validate_content.py` — 70%+
    -   ✅ `validate_meta.py` — 70%+
    -   ✅ Overall coverage 50%+

### Milestone 3: Analysis & Generation (Week 5-6)

-   **Deliverable:** Анализаторы покрыты
-   **Acceptance Criteria:**
    -   ✅ `analyze_category.py` — integration тесты
    -   ✅ `csv_to_readable_md.py` — тесты
    -   ✅ `generate_checklists.py` — тесты

### Milestone 4: SEO Checks (Week 7-8)

-   **Deliverable:** SEO проверки покрыты
-   **Acceptance Criteria:**
    -   ✅ Overall coverage 70%+
    -   ✅ Все критичные скрипты покрыты 80%+

### Milestone 5: Deploy & DB (Week 9)

-   **Deliverable:** Деплой скрипты протестированы
-   **Acceptance Criteria:**
    -   ✅ `upload_to_db.py` — тесты с mock БД
    -   ✅ `generate_sql.py` — тесты

### Milestone 6: CI/CD (Week 10)

-   **Deliverable:** Автоматизация + финализация
-   **Acceptance Criteria:**
    -   ✅ GitHub Actions настроены
    -   ✅ Coverage badge в README
    -   ✅ Overall coverage 80%+
    -   ✅ Документация завершена

---

## 12. 🎓 Обучение и Onboarding

### Ресурсы для команды

-   **pytest Documentation:** https://docs.pytest.org/
-   **Testing Best Practices:** https://testdriven.io/
-   **TDD Tutorial:** https://github.com/pytest-dev/pytest/wiki/Talks-and-Tutorials

### Внутренние гайды (создать)

-   [ ] `docs/TESTING_GUIDE.md` — как писать тесты для проекта
-   [ ] `tests/EXAMPLES.md` — примеры тестов с комментариями
-   [ ] Video walkthrough — запись скринкаста по TDD процессу

---

## 13. ✅ Definition of Done

Этап считается завершённым, когда:

1. **Coverage:**

    - Overall coverage ≥ 80%
    - Все критичные скрипты ≥ 90%
    - Все валидаторы ≥ 70%

2. **Quality:**

    - Все тесты проходят на `develop` ветке
    - Нет flaky тестов (1000 runs без failures)
    - Code review пройден минимум 2 разработчиками

3. **CI/CD:**

    - GitHub Actions запускается автоматически
    - Pre-commit hook работает
    - Coverage отчёты генерируются

4. **Documentation:**
    - README.md обновлён
    - `TESTING_GUIDE.md` создан
    - Все тесты имеют docstrings

---

## 14. 🔄 Поддержка и Maintenance

### Ongoing Activities

-   **Еженедельный review** coverage метрик
-   **Ежемесячный audit** flaky тестов
-   **Квартальный refactoring** устаревших тестов

### Ответственность

-   **DevOps:** Поддержка CI/CD, инфраструктуры
-   **Разработчики:** Написание тестов для новых фич
-   **QA:** Review тестов, mutation testing

---

## 15. 🏁 Следующие шаги

### Немедленные действия (This Week)

1. [ ] Review этого ТЗ с командой
2. [ ] Approve приоритеты и timeline
3. [ ] Создать GitHub Issues для каждой задачи
4. [ ] Начать Week 1 — Инфраструктура

### Долгосрочные улучшения (Post Week 10)

-   [ ] Property-based testing (Hypothesis)
-   [ ] Mutation testing (mutmut)
-   [ ] Performance benchmarks (pytest-benchmark)
-   [ ] Visual regression тесты для HTML output

---

**Документ составлен:** 2026-01-05  
**Автор:** Antigravity AI  
**Версия:** 1.0  
**Статус:** Ready for Review
