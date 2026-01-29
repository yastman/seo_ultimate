# Keywords Coverage Audit — Design

## Проблема

После регенерации мета-тегов (commit 426c7e1) в `keywords_in_content` появились новые ключи, но тексты остались старыми. Нужно найти категории, где primary/secondary ключи из meta.json **не используются** в тексте.

## Текущее состояние

### Что есть

| Инструмент | Что делает | Ограничение |
|------------|------------|-------------|
| `content-reviewer` (скилл) | Проверяет 1 категорию, фиксит | Только 1 за раз |
| `verify-content` (скилл) | Интерактивная проверка | Ручной контроль |
| `validate_content.py` | Проверяет primary в H1/intro | Не проверяет keywords_in_content |
| `audit_keyword_consistency.py` | Проверяет _clean.json | НЕ проверяет текст |

### Чего нет (gap)

**Нет массового аудита keywords_in_content → текст:**
- Никто не проверяет все 53 категории за раз
- Нет отчёта "какие primary/secondary из meta.json отсутствуют в тексте"

## Решение

### Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│  audit_keywords_coverage.py                                  │
│  ─────────────────────────────────────────────────────────  │
│  1. Сканирует все categories/**/meta/*_meta.json            │
│  2. Читает соответствующий content/*_ru.md                  │
│  3. Проверяет coverage primary/secondary/supporting         │
│  4. Выводит отчёт KEYWORDS_COVERAGE_AUDIT.md               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  reports/KEYWORDS_COVERAGE_AUDIT.md                         │
│  ─────────────────────────────────────────────────────────  │
│  ## Summary                                                  │
│  - Total: 53 categories                                      │
│  - PASS: 45 (all keywords found)                            │
│  - BLOCKER: 8 (primary/secondary missing)                   │
│                                                              │
│  ## BLOCKER Categories (need fix)                           │
│  | Slug | Primary | Secondary | Missing |                   │
│  | sredstva-dlya-khimchistki-salona | 1/3 | 2/3 | ... |    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Parallel Workers (через spawn-claude)                      │
│  ─────────────────────────────────────────────────────────  │
│  W1: content-reviewer category1                             │
│  W2: content-reviewer category2                             │
│  ...                                                         │
│  WN: content-reviewer categoryN                             │
└─────────────────────────────────────────────────────────────┘
```

### Компоненты

#### 1. `scripts/audit_keywords_coverage.py`

```python
# Input: categories/**/meta/*_meta.json
# Output: reports/KEYWORDS_COVERAGE_AUDIT.md

def audit_category(meta_path):
    """
    1. Читает meta.json → keywords_in_content
    2. Находит content/{slug}_ru.md
    3. Проверяет каждый keyword (exact match, lowercase)
    4. Возвращает {slug, primary_coverage, secondary_coverage, missing}
    """

def generate_report(results):
    """
    Markdown отчёт:
    - Summary (total, pass, blocker)
    - BLOCKER table (categories to fix)
    - WARNING table (supporting <80%)
    - PASS list (all good)
    """
```

#### 2. Отчёт `KEYWORDS_COVERAGE_AUDIT.md`

```markdown
# Keywords Coverage Audit

**Date:** 2026-01-29
**Categories:** 53

## Summary

| Status | Count | % |
|--------|-------|---|
| ✅ PASS | 45 | 85% |
| ❌ BLOCKER | 8 | 15% |

## BLOCKER Categories

| # | Slug | Primary | Secondary | Missing Keywords |
|---|------|---------|-----------|------------------|
| 1 | sredstva-dlya-khimchistki-salona | 1/3 (33%) | 2/3 (66%) | химия для чистки салона, химия для химчистки авто, автохимия для салона |
| 2 | ... | ... | ... | ... |

## Fix Command

```bash
spawn-claude "W1: /content-reviewer ukhod-za-intererom/sredstva-dlya-khimchistki-salona" "$(pwd)"
```
```

#### 3. Параллельные воркеры

После аудита — запуск content-reviewer для BLOCKER категорий через spawn-claude:

```bash
# Генерируется скриптом или вручную
spawn-claude "W1: /content-reviewer {path1}. НЕ ДЕЛАЙ git commit" "$(pwd)"
spawn-claude "W2: /content-reviewer {path2}. НЕ ДЕЛАЙ git commit" "$(pwd)"
```

## Workflow

```
1. python3 scripts/audit_keywords_coverage.py
   → reports/KEYWORDS_COVERAGE_AUDIT.md

2. Изучить отчёт, подтвердить BLOCKER список

3. Запустить воркеров (по 3-4 параллельно):
   spawn-claude "W1: /content-reviewer {path}" "$(pwd)"

4. После завершения воркеров — review и commit
```

## Критерии coverage

| Группа | Требование | Severity |
|--------|------------|----------|
| primary | **100%** | BLOCKER |
| secondary | **100%** | BLOCKER |
| supporting | **≥80%** | WARNING |

## Примеры проблем (найдено)

### sredstva-dlya-khimchistki-salona

**meta.json:**
```json
"keywords_in_content": {
  "primary": ["химия для чистки салона", "химия для химчистки авто", "средство для чистки салона авто"],
  "secondary": ["химия для салона авто", "средство для химчистки салона авто", "автохимия для салона"]
}
```

**Текст (_ru.md):**
- ❌ "химия для чистки салона" — НЕТ
- ❌ "химия для химчистки авто" — НЕТ
- ✅ "средство для чистки салона авто" — строка 11
- ✅ "химия для салона авто" — строка 45
- ✅ "средство для химчистки салона авто" — строка 13
- ❌ "автохимия для салона" — НЕТ

**Вердикт:** PRIMARY 1/3, SECONDARY 2/3 → **BLOCKER**

## Ограничения

1. **Exact match** — проверка точного вхождения (lowercase)
2. **Не учитывает падежи** — "химия для салона" ≠ "химией для салона"
3. **Воркеры не коммитят** — commit делает оркестратор после review

## Риски

| Риск | Митигация |
|------|-----------|
| Ложные срабатывания (падежи) | Ручной review перед фиксом |
| Воркеры сломают текст | Re-validation после каждого воркера |
| Слишком много BLOCKER | Приоритизация по volume primary ключа |

## Альтернативы (отклонены)

1. **Semantic matching** — сложнее, требует natasha/pymorphy2
2. **LLM-based audit** — дорого для 53 категорий
3. **Ручная проверка** — слишком долго

## Deliverables

1. `scripts/audit_keywords_coverage.py` — скрипт аудита
2. `reports/KEYWORDS_COVERAGE_AUDIT.md` — отчёт
3. Исправленные тексты (через content-reviewer)
