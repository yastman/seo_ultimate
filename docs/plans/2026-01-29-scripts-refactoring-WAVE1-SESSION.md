# Wave 1: text_utils.py Foundation

> **Один воркер выполняет последовательно Tasks 0-4**

## Контекст

Создаём SSOT модуль `scripts/text_utils.py` с функциями, которые сейчас дублируются в нескольких скриптах.

## Задачи

1. **Task 0:** Создать `tests/fixtures/real_data.py` и обновить `tests/conftest.py`
2. **Task 1:** Создать `scripts/text_utils.py` с stopwords (STOPWORDS_RU, STOPWORDS_UK, get_stopwords)
3. **Task 2:** Добавить `clean_markdown()` и `normalize_text()`
4. **Task 3:** Добавить `extract_h1()`, `extract_h2s()`, `extract_intro()`
5. **Task 4:** Добавить `count_words()`, `count_chars_no_spaces()`, `tokenize()`

## Команда запуска

```bash
spawn-claude "W1: Создание text_utils.py (SSOT модуль).

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 0, Task 1, Task 2, Task 3, Task 4.

Это Phase 0 и Phase 1 — создание фундамента.

После выполнения каждой задачи запусти тесты:
pytest tests/unit/test_text_utils.py -v

Пиши лог в data/generated/audit-logs/W1_text_utils_log.md

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"
```

## Критерий завершения

- `scripts/text_utils.py` создан и содержит все функции
- `tests/unit/test_text_utils.py` проходит (pytest PASS)
- `tests/fixtures/real_data.py` создан
- Лог записан в `data/generated/audit-logs/W1_text_utils_log.md`

## После завершения Wave 1

Оркестратор:
1. Проверяет лог
2. Запускает `pytest tests/unit/test_text_utils.py -v`
3. Если PASS — коммитит и запускает Wave 2
