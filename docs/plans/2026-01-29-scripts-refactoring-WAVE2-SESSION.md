# Wave 2: Import Migration (4 воркера параллельно)

> **Запускать ТОЛЬКО после успешного завершения Wave 1**

## Предусловие

- `scripts/text_utils.py` существует и экспортирует: `get_stopwords`, `clean_markdown`, `normalize_text`, `extract_h1`, `extract_h2s`, `extract_intro`, `count_words`, `count_chars_no_spaces`, `tokenize`
- `pytest tests/unit/test_text_utils.py` проходит

## Воркеры

### W1: seo_utils.py (Task 5)

```bash
spawn-claude "W1: Миграция seo_utils.py на text_utils.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 5.

Задача: Заменить локальные clean_markdown, normalize_text, count_words, count_chars_no_spaces
на импорты из scripts.text_utils. Удалить локальные реализации.

Верификация:
pytest tests/unit/test_seo_utils.py -v

Пиши лог в data/generated/audit-logs/W1_seo_utils_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

### W2: check_keyword_density.py (Task 6)

```bash
spawn-claude "W2: Миграция check_keyword_density.py на text_utils.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 6.

Задача: Заменить локальные STOPWORDS_RU, STOPWORDS_UK, get_stopwords, clean_markdown, tokenize
на импорты из scripts.text_utils. Удалить локальные реализации (~250 строк).

Верификация:
pytest tests/unit/test_check_keyword_density.py -v

Пиши лог в data/generated/audit-logs/W2_density_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

### W3: validate_content.py (Task 7)

```bash
spawn-claude "W3: Миграция validate_content.py на text_utils.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 7.

Задача: Заменить локальные extract_h1, extract_h2s, extract_intro
на импорты из scripts.text_utils. Удалить локальные реализации (~30 строк).

Также обновить импорты clean_markdown, count_words — брать из text_utils.

Верификация:
pytest tests/unit/test_validate_content.py -v

Пиши лог в data/generated/audit-logs/W3_validate_content_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

### W4: check_seo_structure.py (Task 8)

```bash
spawn-claude "W4: Миграция check_seo_structure.py на text_utils.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 8.

Задача: Добавить импорты из scripts.text_utils где применимо.
Скрипт использует MorphAnalyzer из keyword_utils — это оставить.

Верификация (ручная):
python3 scripts/check_seo_structure.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md 'активная пена'

Пиши лог в data/generated/audit-logs/W4_seo_structure_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

## Критерий завершения Wave 2

- Все 4 воркера завершили работу
- Все тесты проходят: `pytest tests/unit/test_seo_utils.py tests/unit/test_check_keyword_density.py tests/unit/test_validate_content.py -v`
- Нет дублирования кода (clean_markdown, stopwords определены только в text_utils.py)

## После завершения Wave 2

Оркестратор:
1. Проверяет все 4 лога
2. Запускает полный тест-сьют: `pytest tests/unit/ -v --tb=short`
3. Если PASS — коммитит и запускает Wave 3
