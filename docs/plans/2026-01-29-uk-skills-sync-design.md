# UK Skills Sync — Design Document

## Problem Statement

UK скиллы были созданы как копии RU, но используют другую формулу Title для коротких keywords. Это приводит к тому, что UK meta-теги не проходят валидацию (5 WARNING из 60 файлов).

## Root Cause Analysis

### Расхождение формул Title

**RU (правильно):**
```
ЕСЛИ primary_keyword ≤ 20 chars:
  {primary_keyword} — купить в интернет-магазине Ultimate

ИНАЧЕ:
  {primary_keyword} — купить, цены | Ultimate
```

**UK (неправильно):**
```
ЯКЩО primary_keyword ≤ 20 chars:
  Купити {primary_keyword} в Україні | Ultimate    ← КОРОТКИЙ!

ІНАКШЕ:
  {primary_keyword} — купити, ціни | Ultimate
```

### Проблемы UK формулы

1. **"в Україні" вместо "в інтернет-магазині"** — короче на ~15 chars
2. **"Купити" в начале** вместо после ключа — нарушает Front-loading
3. **Результат:** Title 23-29 chars < 30 минимум

### Пример

| Формула | Title | Длина |
|---------|-------|-------|
| RU | `Силант — купить в интернет-магазине Ultimate` | 47 chars ✅ |
| UK | `Купити силант в Україні \| Ultimate` | 23 chars ❌ |

## Affected Files

### Скиллы (4 файла)

| Файл | Проблема |
|------|----------|
| `.claude/skills/uk-generate-meta/skill.md` | Неверная формула + примеры |
| `.claude/skills/uk-content-init/skill.md` | Неверная формула |
| `.claude/skills/quality-gate/skill.md` | Неверный пример UK Title |
| `.claude/skills/uk-quality-gate/skill.md` | Возможно тоже (проверить) |

### Meta-файлы (5 файлов с WARNING)

| Файл | Проблема |
|------|----------|
| `uk/categories/silanty/meta/silanty_meta.json` | Title 23 chars |
| `uk/categories/ochistiteli-shin/meta/ochistiteli-shin_meta.json` | Title 29 chars |
| `uk/categories/omyvatel/meta/omyvatel_meta.json` | Title 28 chars + fluff |
| `uk/categories/kvik-deteylery/meta/kvik-deteylery_meta.json` | fluff "швидко" |
| `uk/categories/ochistiteli-stekol/meta/ochistiteli-stekol_meta.json` | fluff "без розводів" |

## Solution

### Правильная UK формула

```
ЯКЩО primary_keyword ≤ 20 chars:
  {primary_keyword} — купити в інтернет-магазині Ultimate

ІНАКШЕ:
  {primary_keyword} — купити, ціни | Ultimate
```

### Примеры исправленных Title

| primary_keyword | Довжина | Title |
|-----------------|---------|-------|
| силант | 6 | Силант — купити в інтернет-магазині Ultimate |
| віск для авто | 13 | Віск для авто — купити в інтернет-магазині Ultimate |
| полірувальна машинка | 20 | Полірувальна машинка — купити в інтернет-магазині Ultimate |
| догляд за салоном авто | 22 | Догляд за салоном авто — купити, ціни \| Ultimate |

## Validation

После исправлений:
```bash
python3 scripts/validate_meta.py --all
# Expected: 60 PASS, 0 WARNING, 0 FAIL
```

## Out of Scope

- Полный аудит всех UK скиллов (content-generator, seo-research и т.д.)
- Изменение RU скиллов
- Добавление новых проверок в валидатор

---

**Version:** 1.0
**Date:** 2026-01-29
