# W3-3: Smoke и Integration тесты

**Дата:** 2026-01-29
**Задачи:** Task 14, 15, 16, 17

## Выполненные задачи

### Task 14: Smoke tests для text_utils

**Файл:** `tests/smoke/test_text_utils_smoke.py`

**Тесты (10 шт.):**
- `test_clean_markdown_on_real_ru_content` - clean_markdown на реальном RU контенте
- `test_clean_markdown_on_real_uk_content` - clean_markdown на реальном UK контенте
- `test_extract_h1_on_real_content` - extract_h1 находит H1
- `test_extract_h2s_on_real_content` - extract_h2s находит H2s
- `test_extract_intro_on_real_content` - extract_intro находит intro
- `test_tokenize_ru_on_real_content` - tokenize с RU stopwords
- `test_tokenize_uk_on_real_content` - tokenize с UK stopwords
- `test_count_words_on_real_content` - count_words на реальном контенте
- `test_stopwords_ru_coverage` - RU stopwords set >= 50 слов
- `test_stopwords_uk_coverage` - UK stopwords set >= 50 слов

**Результат:** 10/10 PASSED

---

### Task 15: Smoke tests для validators

**Файл:** `tests/smoke/test_validators_smoke.py`

**Тесты (12 шт.):**

**TestValidateMetaSmoke:**
- `test_validate_meta_ru_real_file[aktivnaya-pena]` - validate_meta на реальном RU meta
- `test_validate_meta_ru_real_file[polirovalnye-pasty]`
- `test_validate_meta_ru_real_file[ochistiteli-stekol]`
- `test_validate_meta_uk_real_file` - validate_meta на UK meta

**TestValidateContentSmoke:**
- `test_validate_content_ru_real_file` - validate_content на RU контенте
- `test_validate_content_uk_real_file` - validate_content на UK контенте
- `test_validate_content_structure_checks` - проверка структуры

**TestValidateDensitySmoke:**
- `test_analyze_text_ru_real_file` - analyze_text на RU контенте
- `test_analyze_text_uk_real_file` - analyze_text на UK контенте
- `test_check_keyword_density_specific_keyword` - проверка конкретного ключа

**TestMultipleCategoriesSmoke:**
- `test_validate_content_multiple_categories[polirovalnye-pasty]`
- `test_validate_content_multiple_categories[ochistiteli-stekol]`

**Результат:** 12/12 PASSED

**Примечание:** Используется `validate_density.py` (текущее имя скрипта).

---

### Task 16: Integration tests для validation pipeline

**Файл:** `tests/integration/test_validation_pipeline.py`

**Тесты (8 шт.):**

**TestFullValidationPipeline:**
- `test_full_ru_validation_pipeline` - полный RU pipeline (meta → content → density)
- `test_full_uk_validation_pipeline` - полный UK pipeline

**TestCrossValidation:**
- `test_meta_content_h1_consistency` - H1 в meta и content имеют общие слова
- `test_keywords_in_content` - ключи из clean.json присутствуют в контенте

**TestValidationModes:**
- `test_seo_mode_returns_expected_structure` - SEO mode возвращает checks + summary
- `test_quality_mode_returns_expected_structure` - Quality mode

**TestLanguageSupport:**
- `test_meta_validation_respects_lang_parameter` - lang=uk корректно применяется
- `test_content_validation_respects_lang_parameter` - UK stopwords работают

**Результат:** 8/8 PASSED

---

### Task 17: Verify 80% test coverage

**Команда:**
```bash
pytest tests/smoke/ tests/integration/test_validation_pipeline.py --cov=scripts.text_utils --cov-report=term-missing
```

**Результаты coverage:**

| Модуль | Coverage |
|--------|----------|
| `scripts/text_utils.py` | **81.54%** ✅ |
| `scripts/validate_content.py` | 46.77% |
| `scripts/validate_meta.py` | 39.81% |
| `scripts/validate_density.py` | 40.70% |

**text_utils.py достигает целевых 80%+.**

Валидаторы имеют меньший coverage, так как smoke тесты тестируют только основные happy-path сценарии. Для полного 80% coverage валидаторов нужны дополнительные unit тесты (edge cases, error handling).

---

## Итог

| Task | Статус | Файл |
|------|--------|------|
| Task 14 | ✅ DONE | `tests/smoke/test_text_utils_smoke.py` |
| Task 15 | ✅ DONE | `tests/smoke/test_validators_smoke.py` |
| Task 16 | ✅ DONE | `tests/integration/test_validation_pipeline.py` |
| Task 17 | ✅ DONE | text_utils.py 81.54% coverage |

**Общий результат:** 30 тестов, 30 passed, 0 failed

```bash
pytest tests/smoke/ tests/integration/test_validation_pipeline.py -v
# ======================= 30 passed in 31.41s =======================
```
