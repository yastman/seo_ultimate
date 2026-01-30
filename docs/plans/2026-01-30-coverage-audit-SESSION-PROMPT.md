# Coverage Audit Tool — Session Prompt

## Задача

Выполни план `docs/plans/2026-01-30-coverage-audit-plan.md` — создание инструмента batch-аудита покрытия ключевых слов.

## Команда

```
/superpowers:executing-plans docs/plans/2026-01-30-coverage-audit-plan.md
```

## Контекст

План создаёт:
- `scripts/coverage_matcher.py` — модуль матчинга с PreparedText и MatchResult
- `scripts/audit_coverage.py` — CLI для single/batch режимов
- `tests/unit/test_coverage_matcher.py` — юнит-тесты

## Критические моменты (уже в плане)

1. **RU-пути вложенные** — `categories/parent/slug/` (не плоские), используй `rglob()`
2. **PreparedText** — лемматизация текста один раз на категорию, не на каждый ключ
3. **TOKENIZATION** — только латиница с дефисом (`wash-and-wax`), не кириллица
4. **SYNONYM** — сравнение `variant_of` через `normalize_text()` (case-insensitive)
5. **Один коммит** — в конце после Task 8

## Верификация после каждой задачи

```bash
pytest tests/unit/test_coverage_matcher.py -v
```

## Финальная проверка (Task 8)

```bash
# UK
python3 scripts/audit_coverage.py --slug cherniteli-shin --lang uk --verbose
python3 scripts/audit_coverage.py --lang uk

# RU (nested paths)
python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang ru --verbose
python3 scripts/audit_coverage.py --lang ru

# CSV
ls -la reports/coverage_*.csv
```

## Лог

Пиши прогресс в `data/generated/audit-logs/coverage_audit_log.md`
