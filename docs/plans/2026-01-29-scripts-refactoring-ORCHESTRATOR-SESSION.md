# Scripts Refactoring — Orchestrator Session

Ты оркестратор. Твоя задача — запустить воркеров для рефакторинга скриптов и координировать их работу.

## Контекст

**Цель:** Создать SSOT модуль `text_utils.py`, унифицировать валидаторы с UK поддержкой, достичь 80% test coverage.

**План:** `docs/plans/2026-01-29-scripts-refactoring-plan.md` (18 Tasks)

**Волны:**
- Wave 1: Tasks 0-4 (1 воркер, последовательно) — создание text_utils.py
- Wave 2: Tasks 5-8 (4 воркера параллельно) — миграция импортов
- Wave 3: Tasks 9-17 (3 воркера параллельно) — UK, renames, tests

## Инструкции

### 1. Запусти Wave 1

```bash
spawn-claude "W1: Создание text_utils.py (SSOT модуль).

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 0, Task 1, Task 2, Task 3, Task 4.

После каждой задачи запусти: pytest tests/unit/test_text_utils.py -v

Пиши лог в data/generated/audit-logs/W1_text_utils_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

### 2. После завершения Wave 1

Проверь:
```bash
# Читай лог
cat data/generated/audit-logs/W1_text_utils_log.md

# Запусти тесты
pytest tests/unit/test_text_utils.py -v

# Проверь что файл создан
ls -la scripts/text_utils.py
```

Если всё OK — коммить:
```bash
git add scripts/text_utils.py tests/unit/test_text_utils.py tests/fixtures/ tests/conftest.py
git commit -m "feat(text_utils): create SSOT module for text processing

- Add stopwords (RU + UK)
- Add clean_markdown, normalize_text
- Add extract_h1, extract_h2s, extract_intro
- Add count_words, count_chars_no_spaces, tokenize
- Add test fixtures with real data

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

### 3. Запусти Wave 2 (4 воркера параллельно)

```bash
spawn-claude "W1: Миграция seo_utils.py.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 5.

Верификация: pytest tests/unit/test_seo_utils.py -v

Пиши лог в data/generated/audit-logs/W2_1_seo_utils_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

```bash
spawn-claude "W2: Миграция check_keyword_density.py.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 6.

Верификация: pytest tests/unit/test_check_keyword_density.py -v

Пиши лог в data/generated/audit-logs/W2_2_density_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

```bash
spawn-claude "W3: Миграция validate_content.py.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 7.

Верификация: pytest tests/unit/test_validate_content.py -v

Пиши лог в data/generated/audit-logs/W2_3_validate_content_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

```bash
spawn-claude "W4: Миграция check_seo_structure.py.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 8.

Верификация: python3 scripts/check_seo_structure.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md 'активная пена'

Пиши лог в data/generated/audit-logs/W2_4_seo_structure_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

### 4. После завершения Wave 2

Проверь логи:
```bash
cat data/generated/audit-logs/W2_*.md
```

Запусти полный тест:
```bash
pytest tests/unit/ -v --tb=short
```

Если OK — коммить:
```bash
git add scripts/seo_utils.py scripts/check_keyword_density.py scripts/validate_content.py scripts/check_seo_structure.py
git commit -m "refactor: migrate all scripts to use text_utils SSOT

- seo_utils.py: import from text_utils
- check_keyword_density.py: remove 250 lines of duplicated code
- validate_content.py: import extract_* from text_utils
- check_seo_structure.py: use text_utils imports

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

### 5. Запусти Wave 3 (3 воркера параллельно)

```bash
spawn-claude "W1: UK support + Archive + Docs.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 9, Task 12, Task 13.

Task 9: UK patterns в validate_meta.py
Task 12: Создать scripts/archive/, mv validate_uk.py
Task 13: Обновить CLAUDE.md

Верификация: pytest tests/unit/test_validate_meta.py -v

Пиши лог в data/generated/audit-logs/W3_1_uk_archive_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

```bash
spawn-claude "W2: Переименование скриптов.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 10, Task 11.

Task 10: mv check_seo_structure.py → validate_seo.py
Task 11: mv check_keyword_density.py → validate_density.py

Верификация: python3 scripts/validate_seo.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md 'активная пена'

Пиши лог в data/generated/audit-logs/W3_2_renames_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

```bash
spawn-claude "W3: Smoke и Integration тесты.

/superpowers:executing-plans docs/plans/2026-01-29-scripts-refactoring-plan.md

Выполни ТОЛЬКО: Task 14, Task 15, Task 16, Task 17.

Создай:
- tests/smoke/test_text_utils_smoke.py
- tests/smoke/test_validators_smoke.py
- tests/integration/test_validation_pipeline.py

ВАЖНО: Используй ТЕКУЩИЕ имена скриптов (check_seo_structure, check_keyword_density).

Верификация: pytest tests/smoke/ tests/integration/ -v

Пиши лог в data/generated/audit-logs/W3_3_tests_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

### 6. После завершения Wave 3

Проверь логи:
```bash
cat data/generated/audit-logs/W3_*.md
```

**ВАЖНО:** W2 переименовал скрипты, обнови импорты в smoke/integration тестах:
```bash
# Проверь что скрипты переименованы
ls scripts/validate_seo.py scripts/validate_density.py

# Обнови импорты в тестах если нужно
# from check_seo_structure → from validate_seo
# from check_keyword_density → from validate_density
```

Запусти все тесты:
```bash
pytest tests/ -v --tb=short
```

Проверь coverage:
```bash
pytest tests/ --cov=scripts --cov-report=term-missing
```

### 7. Финальный коммит

```bash
git add -A
git commit -m "feat: complete scripts refactoring with 80% coverage

Wave 1: text_utils.py SSOT module
Wave 2: migrate imports from 4 scripts
Wave 3: UK support, renames, smoke/integration tests

- scripts/text_utils.py: stopwords, clean_markdown, extract_*, count_*, tokenize
- scripts/validate_meta.py: --lang uk support
- scripts/validate_seo.py: renamed from check_seo_structure.py
- scripts/validate_density.py: renamed from check_keyword_density.py
- scripts/archive/: old validate_uk.py
- tests/smoke/: smoke tests on real data
- tests/integration/: full pipeline tests
- 80%+ test coverage

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

## Мониторинг воркеров

```bash
# Список tmux окон
tmux list-windows

# Переключение между окнами
# Ctrl+A, w — список
# Ctrl+A, n — следующее
# Ctrl+A, p — предыдущее

# Проверка логов
ls -la data/generated/audit-logs/
```

## Критерии успеха

- [ ] `scripts/text_utils.py` создан и содержит все функции
- [ ] Все 4 скрипта мигрированы на text_utils
- [ ] `validate_meta.py --lang uk` работает
- [ ] Скрипты переименованы (validate_seo, validate_density)
- [ ] `scripts/archive/` содержит validate_uk.py
- [ ] Smoke тесты проходят
- [ ] Integration тесты проходят
- [ ] Coverage ≥80%
- [ ] Все коммиты сделаны

## Troubleshooting

**Воркер завис:** `Ctrl+C` в его окне, перезапусти spawn-claude

**Тесты падают после миграции:** Проверь импорты, возможно relative/absolute path issue

**Coverage < 80%:** Добавь тесты для непокрытых строк, смотри `--cov-report=term-missing`
