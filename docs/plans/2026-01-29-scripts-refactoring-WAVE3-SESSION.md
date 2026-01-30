# Wave 3: UK Support, Renames, Tests (3 воркера параллельно)

> **Запускать ТОЛЬКО после успешного завершения Wave 2**

## Предусловие

- `scripts/text_utils.py` существует и используется всеми валидаторами
- `pytest tests/unit/` проходит полностью
- Нет дублирования stopwords/clean_markdown

## Воркеры

### W1: UK Support + Archive + Docs (Tasks 9, 12, 13)

```bash
spawn-claude "W1: UK support, архивирование, документация.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 9, Task 12, Task 13.

Task 9: Добавить UK patterns в validate_meta.py, параметр --lang uk
Task 12: Создать scripts/archive/, переместить validate_uk.py
Task 13: Обновить CLAUDE.md с новыми командами

Верификация Task 9:
pytest tests/unit/test_validate_meta.py -v

Пиши лог в data/generated/audit-logs/W1_uk_archive_docs_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

### W2: Script Renames (Tasks 10, 11)

```bash
spawn-claude "W2: Переименование скриптов.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 10, Task 11.

Task 10: git mv check_seo_structure.py → validate_seo.py
Task 11: git mv check_keyword_density.py → validate_density.py
         git mv test_check_keyword_density.py → test_validate_density.py

После переименования обнови импорты в тестах.

Верификация:
python3 scripts/validate_seo.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md 'активная пена'
pytest tests/unit/test_validate_density.py -v

Пиши лог в data/generated/audit-logs/W2_renames_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

### W3: Smoke + Integration Tests (Tasks 14, 15, 16, 17)

```bash
spawn-claude "W3: Smoke и интеграционные тесты.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 14, Task 15, Task 16, Task 17.

Task 14: Создать tests/smoke/test_text_utils_smoke.py
Task 15: Создать tests/smoke/test_validators_smoke.py
Task 16: Создать tests/integration/test_validation_pipeline.py
Task 17: Проверить coverage ≥80%, добавить config в pyproject.toml

ВАЖНО: Тесты должны работать с ТЕКУЩИМИ именами скриптов!
- check_seo_structure.py (не validate_seo.py)
- check_keyword_density.py (не validate_density.py)

W2 переименует их позже, после чего тесты нужно будет обновить.

Верификация:
pytest tests/smoke/ -v
pytest tests/integration/ -v

Пиши лог в data/generated/audit-logs/W3_tests_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

## Критерий завершения Wave 3

- W1: `validate_meta.py --lang uk` работает, `scripts/archive/` создан
- W2: Скрипты переименованы, тесты обновлены
- W3: Smoke и integration тесты созданы и проходят
- Все тесты проходят: `pytest tests/ -v`

## После завершения Wave 3

Оркестратор:
1. Проверяет все 3 лога
2. **ВАЖНО:** Обновляет smoke/integration тесты если W2 переименовал скрипты
3. Запускает: `pytest tests/ --cov=scripts --cov-report=term-missing`
4. Если coverage ≥80% и все PASS — финальный коммит

## Финальная верификация

```bash
# Все тесты
pytest tests/ -v

# Coverage check
pytest tests/ --cov=scripts --cov-fail-under=80

# Validators работают
python3 scripts/validate_meta.py --all
python3 scripts/validate_meta.py --all --lang uk
python3 scripts/validate_seo.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md "активная пена"
python3 scripts/validate_density.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md
```
