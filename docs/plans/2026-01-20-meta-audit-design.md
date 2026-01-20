# Meta Tags Audit — Design Document

**Date:** 2026-01-20
**Status:** Approved
**Author:** Claude Code

---

## Goal

Комплексная проверка мета-тегов всех категорий на соответствие SEO-правилам 2026 года из CONTENT_GUIDE.md.

## Scope

| Параметр | Значение |
|----------|----------|
| Файлы | Все `*_meta.json` в `/categories/` (~52 файла) |
| Языки | Только русские (language: "ru") |
| Украинские версии | Отдельный аудит позже |

## Уровни проверки

| Уровень | Проверки |
|---------|----------|
| Техническая валидация | Длина title (50-60), description (120-160), обязательные поля |
| SEO-качество | Front-loading ВЧ в title, "купить" после ВЧ, H1 без "купить" |
| Полнота данных | keywords_in_content.primary, types, forms, volumes |
| Консистентность | Title ↔ H1 по теме, slug соответствует папке |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    audit_meta.py                        │
├─────────────────────────────────────────────────────────┤
│  1. MetaLoader      — сбор всех *_meta.json             │
│  2. TechnicalCheck  — длина, обязательные поля          │
│  3. SEOQualityCheck — front-loading, формулы title/desc │
│  4. CompletenessCheck — keywords, types, forms, volumes │
│  5. ReportGenerator — JSON + Markdown отчёты            │
└─────────────────────────────────────────────────────────┘
```

---

## Validation Rules

| Правило | Severity | Логика |
|---------|----------|--------|
| Title 50-60 chars | WARNING | `len(title) < 50 or len(title) > 60` |
| Title без двоеточия | CRITICAL | `":" in title` |
| Title front-loading | CRITICAL | ВЧ keyword не в начале title |
| Title "купить" не первым | CRITICAL | `title.lower().startswith("купить")` |
| H1 без "купить" | CRITICAL | `"купить" in h1.lower()` |
| Description 120-160 | WARNING | Длина за пределами |
| Description "от производителя" | WARNING | Паттерн отсутствует |
| Description "опт и розница" | WARNING | Паттерн отсутствует |
| keywords_in_content.primary | INFO | Массив пустой или отсутствует |

---

## Output Format

### JSON Report

```json
{
  "summary": {
    "total_categories": 52,
    "passed": 35,
    "warnings": 12,
    "critical": 5,
    "timestamp": "2026-01-20T..."
  },
  "by_severity": {
    "CRITICAL": [
      {
        "slug": "example-slug",
        "path": "categories/.../meta/example_meta.json",
        "issues": [
          {
            "rule": "title_front_loading",
            "message": "ВЧ keyword не в начале title",
            "current": "Current value..."
          }
        ]
      }
    ],
    "WARNING": [],
    "INFO": []
  }
}
```

### Markdown Report

```markdown
# Meta Tags Audit Report — YYYY-MM-DD

## Сводка
- Passed: X/Y (Z%)
- Warnings: N
- Critical: M

## Critical Issues (M)

### slug-name
- **Rule name:** Description
  - Сейчас: `current value`
  - Нужно: `expected value`
```

### File Locations

- `reports/meta-audit-YYYY-MM-DD.json`
- `reports/meta-audit-YYYY-MM-DD.md`

---

## CLI Interface

```bash
# Полный аудит с отчётами
python scripts/audit_meta.py

# Только JSON
python scripts/audit_meta.py --json

# Конкретная категория
python scripts/audit_meta.py --slug aktivnaya-pena

# Без INFO (только CRITICAL + WARNING)
python scripts/audit_meta.py --min-severity warning
```

---

## Implementation Plan

| # | Задача |
|---|--------|
| 1 | Создать `scripts/audit_meta.py` |
| 2 | Реализовать MetaLoader — сбор всех `*_meta.json` |
| 3 | Реализовать 9 правил проверки |
| 4 | Реализовать ReportGenerator (JSON + Markdown) |
| 5 | Создать папку `reports/` |
| 6 | Запустить аудит, сгенерировать первый отчёт |
| 7 | Проанализировать результаты |

---

## Dependencies

- Python 3.x (stdlib only: json, pathlib, re, datetime)
- No external packages required
