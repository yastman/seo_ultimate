# Матрица покрытия тестами (Test Coverage Matrix)

**Дата:** 2026-01-05  
**Статус:** Current State Analysis

---

## Легенда

| Символ | Значение                                | Действие      |
| ------ | --------------------------------------- | ------------- |
| ✅     | Тесты есть, покрытие хорошее (>60%)     | Maintain      |
| ⚠️     | Тесты есть, покрытие частичное (20-60%) | Expand        |
| ❌     | Тестов нет или минимальны (<20%)        | Create        |
| 🔴     | Критичный приоритет                     | Do First      |
| 🟡     | Средний приоритет                       | Do Second     |
| 🟢     | Низкий приоритет                        | Do Last       |
| 🔒     | Требует внешних зависимостей (DB, API)  | Special Setup |

---

## 📊 Полная матрица скриптов

| №                               | Скрипт                             | LoC   | Сложность  | Приоритет | Тесты                                | Покрытие | Требуется                    |
| ------------------------------- | ---------------------------------- | ----- | ---------- | --------- | ------------------------------------ | -------- | ---------------------------- |
| **CORE UTILITIES (Библиотеки)** |
| 1                               | `seo_utils.py`                     | 920   | ⭐⭐⭐⭐⭐ | 🔴        | ⚠️ `test_seo_utils.py`               | ~15%     | Expand to 80%+               |
| 2                               | `config.py`                        | 8884  | ⭐⭐⭐     | 🔴        | ✅ `test_config.py`                  | ~60%     | Expand to 80%                |
| 3                               | `utils/text.py`                    | ?     | ⭐⭐       | 🟡        | ❌                                   | 0%       | Create unit tests            |
| 4                               | `utils/url.py`                     | ?     | ⭐⭐       | 🟡        | ❌                                   | 0%       | Create unit tests            |
| **VALIDATION (Quality Gate)**   |
| 5                               | `validate_content.py`              | 1427  | ⭐⭐⭐⭐⭐ | 🔴        | ⚠️ `test_validate_content.py`        | ~20%     | Expand to 70%+               |
| 6                               | `validate_meta.py`                 | 20865 | ⭐⭐⭐⭐   | 🔴        | ⚠️ `test_validate_meta.py`           | ~25%     | Expand to 70%+               |
| 7                               | `validate_uk.py`                   | 3785  | ⭐⭐       | 🟡        | ❌                                   | 0%       | Create tests                 |
| 8                               | `check_seo_structure.py`           | 11942 | ⭐⭐⭐     | 🟡        | ❌                                   | 0%       | Create integration           |
| 9                               | `check_h1_sync.py`                 | 5198  | ⭐⭐       | 🟡        | ❌                                   | 0%       | Create tests                 |
| 10                              | `check_water_natasha.py`           | 18045 | ⭐⭐⭐⭐   | 🟡        | ⚠️ `test_check_water_natasha.py`     | ~10%     | Expand to 50%                |
| 11                              | `check_ner_brands.py`              | 17145 | ⭐⭐⭐⭐   | 🟡        | ⚠️ `test_check_ner_brands.py`        | ~10%     | Expand to 50%                |
| **SEMANTICS & STRUCTURE**       |
| 12                              | `csv_to_readable_md.py`            | 20812 | ⭐⭐⭐⭐⭐ | 🔴        | ❌                                   | 0%       | Create integration           |
| 13                              | `parse_semantics_to_json.py`       | 18154 | ⭐⭐⭐⭐   | 🔴        | ⚠️ `test_parse_semantics_to_json.py` | ~30%     | Expand to 70%                |
| 14                              | `fix_csv_structure.py`             | 3591  | ⭐⭐⭐     | 🔴        | ⚠️ `test_fix_csv_structure.py`       | ~40%     | Expand to 70%                |
| 15                              | `find_orphan_keywords.py`          | 21570 | ⭐⭐⭐⭐   | 🟡        | ❌                                   | 0%       | Create tests                 |
| 16                              | `compare_raw_clean.py`             | 19469 | ⭐⭐⭐     | 🟡        | ❌                                   | 0%       | Create tests                 |
| 17                              | `restore_from_csv.py`              | 8391  | ⭐⭐       | 🟡        | ❌                                   | 0%       | Create tests                 |
| 18                              | `transform_structure_alignment.py` | 24293 | ⭐⭐⭐⭐⭐ | 🟡        | ❌                                   | 0%       | Create tests                 |
| **ANALYSIS**                    |
| 19                              | `analyze_category.py`              | 27746 | ⭐⭐⭐⭐⭐ | 🔴        | ❌                                   | 0%       | Create integration           |
| 20                              | `find_duplicates.py`               | 16287 | ⭐⭐⭐⭐   | 🟡        | ❌                                   | 0%       | Create tests                 |
| 21                              | `check_cannibalization.py`         | 9609  | ⭐⭐⭐     | 🟡        | ❌                                   | 0%       | Create tests                 |
| 22                              | `synonym_tools.py`                 | 10604 | ⭐⭐⭐     | 🟡        | ⚠️ `test_synonym_tools.py`           | ~20%     | Expand to 60%                |
| 23                              | `show_keyword_distribution.py`     | 5591  | ⭐⭐       | 🟢        | ❌                                   | 0%       | Optional                     |
| **GENERATION**                  |
| 24                              | `batch_generate.py`                | 22915 | ⭐⭐⭐⭐⭐ | 🔴        | ❌                                   | 0%       | Create e2e (mock LLM)        |
| 25                              | `generate_checklists.py`           | 19686 | ⭐⭐⭐⭐   | 🔴        | ❌                                   | 0%       | Create integration           |
| 26                              | `generate_sql.py`                  | 7796  | ⭐⭐⭐     | 🟡        | ❌                                   | 0%       | Create tests                 |
| 27                              | `md_to_html.py`                    | 5780  | ⭐⭐       | 🟢        | ❌                                   | 0%       | Optional                     |
| **DATABASE & DEPLOY**           |
| 28                              | `upload_to_db.py` 🔒               | 8937  | ⭐⭐⭐⭐   | 🔴        | ❌                                   | 0%       | Create integration (mock DB) |
| 29                              | `products.py` 🔒                   | 6435  | ⭐⭐       | 🟢        | ❌                                   | 0%       | Optional                     |
| **DATA MIGRATION & CLEANUP**    |
| 30                              | `migrate_keywords.py`              | 6668  | ⭐⭐⭐     | 🟡        | ❌                                   | 0%       | Create tests                 |
| 31                              | `cleanup_misplaced.py`             | 7872  | ⭐⭐       | 🟢        | ❌                                   | 0%       | Optional                     |
| **LOCALIZATION (UK)**           |
| 32                              | `uk_seed_from_ru.py`               | 8628  | ⭐⭐⭐     | 🟡        | ❌                                   | 0%       | Create tests                 |
| 33                              | `export_uk_category_texts.py`      | 4443  | ⭐⭐       | 🟢        | ❌                                   | 0%       | Optional                     |
| **PARSERS & TOOLS**             |
| 34                              | `competitors.py`                   | 7961  | ⭐⭐⭐     | 🟢        | ❌                                   | 0%       | Optional                     |
| 35                              | `url_filters.py`                   | 2606  | ⭐⭐       | 🟢        | ❌                                   | 0%       | Optional                     |
| **SYSTEM**                      |
| 36                              | `setup_all.py`                     | 10009 | ⭐⭐       | 🟢        | ❌                                   | 0%       | Optional                     |
| 37                              | `verify_structural_integrity.py`   | 2968  | ⭐⭐       | 🟢        | ❌                                   | 0%       | Optional                     |

---

## 📈 Статистика по приоритетам

### 🔴 Критичные (Critical) — 9 скриптов

Требуют тестов ASAP. Это Quality Gate и core logic:

1. `seo_utils.py` — библиотека всех утилит
2. `config.py` — конфигурация
3. `validate_content.py` — главный валидатор
4. `validate_meta.py` — валидатор мета
5. `csv_to_readable_md.py` — генератор структуры
6. `parse_semantics_to_json.py` — парсер семантики
7. `fix_csv_structure.py` — чистка CSV
8. `analyze_category.py` — анализатор категорий
9. `batch_generate.py` — массовая генерация
10. `generate_checklists.py` — генератор задач
11. `upload_to_db.py` — загрузка в БД

**Effort:** ~8 weeks  
**ROI:** Very High (предотвращение критичных багов)

### 🟡 Средние (Medium) — 13 скриптов

Желательны тесты для стабильности:

-   Все `check_*.py` скрипты
-   Все `find_*.py` скрипты
-   `synonym_tools.py`, `migrate_keywords.py`, etc.

**Effort:** ~4 weeks  
**ROI:** Medium (улучшение quality metrics)

### 🟢 Низкие (Low) — 15 скриптов

Опциональные, простые утилиты:

-   Конвертеры (`md_to_html.py`)
-   Экспортеры
-   Статистики

**Effort:** ~2 weeks  
**ROI:** Low (nice to have)

---

## 🎯 Приоритетный план (Top 10 Most Important)

| Ранг | Скрипт                       | Почему критично                           | Effort | Impact    |
| ---- | ---------------------------- | ----------------------------------------- | ------ | --------- |
| 1    | `seo_utils.py`               | Используется ВЕЗДЕ, база всего            | High   | Very High |
| 2    | `validate_content.py`        | Quality Gate для контента                 | High   | Very High |
| 3    | `validate_meta.py`           | Quality Gate для мета                     | High   | Very High |
| 4    | `analyze_category.py`        | Ключевой анализ перед генерацией          | High   | Very High |
| 5    | `csv_to_readable_md.py`      | Генератор структуры, критичен             | Medium | High      |
| 6    | `parse_semantics_to_json.py` | Парсинг семантики, основа                 | Medium | High      |
| 7    | `batch_generate.py`          | Массовая генерация, дорого если сломается | High   | High      |
| 8    | `upload_to_db.py`            | Деплой, критично для продакшена           | Medium | Very High |
| 9    | `generate_checklists.py`     | Автоматизация workflow                    | Low    | Medium    |
| 10   | `fix_csv_structure.py`       | Чистка данных, база pipeline              | Low    | Medium    |

---

## 📅 Рекомендуемая последовательность (Wave-based)

### Wave 1 (Week 1-3): Core Foundation

**Goal:** Покрыть фундамент — утилиты и валидаторы

1. ✅ Expand `test_seo_utils.py` → 80%+ coverage
2. ✅ Expand `test_config.py` → 80%+ coverage
3. ✅ Expand `test_validate_content.py` → 70%+ coverage
4. ✅ Expand `test_validate_meta.py` → 70%+ coverage

**Deliverable:** Core utilities stable, Quality Gate tested

### Wave 2 (Week 4-6): Semantics & Analysis

**Goal:** Покрыть работу с данными

5. ✅ Expand `test_parse_semantics_to_json.py` → 70%+
6. ✅ Expand `test_fix_csv_structure.py` → 70%+
7. ✅ Create `test_csv_to_readable_md.py` (integration)
8. ✅ Create `test_analyze_category.py` (integration)

**Deliverable:** Data pipeline tested, structure generation stable

### Wave 3 (Week 7-9): Generation & Deploy

**Goal:** Покрыть критичные процессы деплоя

9. ✅ Create `test_batch_generate.py` (e2e, mock LLM)
10. ✅ Create `test_generate_checklists.py` (integration)
11. ✅ Create `test_upload_to_db.py` (integration, mock DB)

**Deliverable:** Generation and deploy processes tested

### Wave 4 (Week 10+): Extended Coverage

**Goal:** Покрыть остальные скрипты по приоритету

12. Create tests for `check_*.py` scripts
13. Create tests for `find_*.py` scripts
14. Create tests for `synonym_tools.py`, `migrate_keywords.py`
15. Optional: tests for parsers and converters

**Deliverable:** Overall coverage 80%+, all critical paths tested

---

## 🔢 Метрики прогресса

### Current State (2026-01-05)

```
📊 Coverage Stats:
├─ Overall Project Coverage: ~18%
├─ Critical Scripts (11): ~20%
├─ Medium Scripts (13): ~5%
└─ Low Scripts (15): ~0%

✅ Tests Passing: 9/9 (из существующих)
❌ Scripts Without Tests: 28/37 (76%)
📝 Total Test Files: 9
📝 Total Test Functions: ~50 (estimate)
```

### Target State (Week 10)

```
📊 Coverage Stats:
├─ Overall Project Coverage: 80%+
├─ Critical Scripts (11): 90%+
├─ Medium Scripts (13): 70%+
└─ Low Scripts (15): 40%+

✅ Tests Passing: 300+/300+
❌ Scripts Without Tests: 5/37 (13%)
📝 Total Test Files: 40+
📝 Total Test Functions: 300+
```

---

## 🚦 Quality Gates

### Minimum viable coverage для каждой категории:

| Категория скриптов                             | Min Coverage | Rationale          |
| ---------------------------------------------- | ------------ | ------------------ |
| **Core Utils** (`seo_utils.py`, `config.py`)   | 85%          | Используются везде |
| **Validators** (`validate_*.py`)               | 75%          | Quality Gate       |
| **Semantics** (`parse_*.py`, `csv_*.py`)       | 70%          | Data integrity     |
| **Analyzers** (`analyze_*.py`, `check_*.py`)   | 60%          | Complex logic      |
| **Generators** (`generate_*.py`, `batch_*.py`) | 50%          | E2E testing        |
| **Deploy** (`upload_*.py`, SQL)                | 80%          | Critical           |
| **Utils & Helpers**                            | 40%          | Nice to have       |

---

## 📝 Notes & Recommendations

### 1. Начать с `seo_utils.py`

Это самый важный модуль. Покрытие его на 80%+ даст сразу большой буст общего coverage, т.к. он используется во всех скриптах.

### 2. Mock external dependencies

-   **LLM API** — использовать `responses` или `pytest-mock`
-   **Database** — использовать SQLite in-memory или `testcontainers`
-   **File I/O** — использовать `tmp_path` фикстуру

### 3. Приоритет integration tests для генераторов

Для скриптов типа `csv_to_readable_md.py`, `analyze_category.py` важнее integration тесты (проверка полного флоу), чем unit тесты каждой функции.

### 4. Snapshot testing для Markdown output

Использовать `pytest-snapshot` для проверки генерируемых MD файлов:

```python
def test_structure_generation_matches_snapshot(snapshot):
    result = generate_structure_md(data)
    snapshot.assert_match(result, "structure.md")
```

### 5. Property-based testing для парсеров

Для CSV/JSON парсеров использовать `hypothesis`:

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_slugify_never_crashes(text):
    result = slugify(text)
    assert isinstance(result, str)
```

---

## 🎓 Learning Resources

-   [ ] **pytest docs:** https://docs.pytest.org/
-   [ ] **Coverage.py:** https://coverage.readthedocs.io/
-   [ ] **pytest-mock:** https://pytest-mock.readthedocs.io/
-   [ ] **testcontainers-python:** https://testcontainers-python.readthedocs.io/
-   [ ] **TDD by Example (Kent Beck):** Classic book
-   [ ] **Python Testing with pytest (Brian Okken):** Modern guide

---

**Документ:** Test Coverage Matrix v1.0  
**Дата:** 2026-01-05  
**Next Review:** After Wave 1 completion
