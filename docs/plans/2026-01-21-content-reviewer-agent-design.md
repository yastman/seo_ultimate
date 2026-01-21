# Content Reviewer Agent Design

**Date:** 2026-01-21
**Status:** Draft

## Цель

Создать субагента `content-reviewer`, который выполняет план ревизии контента (`docs/plans/2026-01-21-content-revision-plan.md`) — проверяет и исправляет контент одной категории за вызов.

---

## Отличия от существующих агентов

| Агент | Задача | Output |
|-------|--------|--------|
| **content-generator** | Пишет контент **с нуля** | `{slug}_ru.md` (новый) |
| **quality-gate** | Только **проверка** | `QUALITY_REPORT.md` (PASS/FAIL) |
| **content-reviewer** (NEW) | **Проверка + исправление** | Исправленный `{slug}_ru.md` + verdict |

---

## Конфигурация

```yaml
name: content-reviewer
description: Ревизия и исправление контента категории. Use when нужно проверить контент, выполнить ревизию, пофиксить проблемы в тексте.
tools: Read, Grep, Glob, Bash, Edit
model: opus
```

---

## Input

```
categories/{path}/
├── content/{slug}_ru.md        # Контент для ревизии
├── data/{slug}_clean.json      # name, parent_id, keywords
├── meta/{slug}_meta.json       # h1, keywords_in_content
└── research/RESEARCH_DATA.md   # Источник истины для фактов
```

**Вызов:** `content-reviewer {path}` или `content-reviewer {slug}`

---

## Workflow (из плана v3.0)

### Step 1: Read data files (parallel)

```bash
cat categories/{path}/data/{slug}_clean.json
cat categories/{path}/meta/{slug}_meta.json
cat categories/{path}/research/RESEARCH_DATA.md
cat categories/{path}/content/{slug}_ru.md
```

**Extract:**
- `name` → H1 должен = name (множественное число)
- `parent_id` → null=Hub Page, else=Product Page
- `keywords_in_content` → для проверки покрытия
- `RESEARCH_DATA.md` → ключевые факты

### Step 2: Run 4 validators (parallel)

```bash
python3 scripts/validate_meta.py categories/{path}/meta/{slug}_meta.json
python3 scripts/validate_content.py categories/{path}/content/{slug}_ru.md "{primary}" --mode seo
python3 scripts/check_keyword_density.py categories/{path}/content/{slug}_ru.md
python3 scripts/check_water_natasha.py categories/{path}/content/{slug}_ru.md
```

### Step 3: Keywords Coverage (ручная проверка)

1. Выписать ключи из `_meta.json` → `keywords_in_content`
2. Для каждого ключа выделить основу (стем)
3. Искать основу в контенте (любое склонение ОК)
4. Подсчитать: найдено/всего для каждой группы

**Критерии:**
- ✅ PASS: все primary, ≥80% secondary/supporting
- ⚠️ WARNING: 1-2 primary отсутствуют или <80% остальных
- ❌ BLOCKER: >2 primary отсутствуют

### Step 4: Facts vs Research (ручная проверка)

1. Прочитать RESEARCH_DATA.md, выделить 5-7 ключевых фактов
2. Для каждого факта проверить в контенте:
   - ✅ Присутствует
   - ⚠️ Отсутствует (важный факт пропущен)
   - ❌ Противоречит (контент говорит обратное)
3. Проверить контент на факты, которых НЕТ в research (выдуманные?)

### Step 5: Qualitative Buyer Guide Review (6 критериев)

| # | Критерий | Как проверить | Severity |
|---|----------|---------------|----------|
| 1 | Intro ≠ определение | Не начинается с "X — это Y, которое..." | BLOCKER |
| 2 | Обращения к читателю | Есть "вам", "если вы", "вам подойдёт" | WARNING |
| 3 | Паттерны "Если X → Y" | Подсчитать количество (≥3) | WARNING |
| 4 | Таблицы не дублируют | Сравнить контент таблиц | WARNING |
| 5 | FAQ не дублирует таблицы | Вопрос уже есть в таблице? | BLOCKER |
| 6 | Секции buyer-oriented | "К покупке или к использованию?" | BLOCKER |

### Step 6: Fill verdict table

| Критерий | Результат | Примечание |
|----------|-----------|------------|
| Meta | ✅/❌ | |
| Density | ✅/⚠️/❌ | stem max X% |
| Тошнота | ✅/⚠️/❌ | classic X |
| Вода | ✅/⚠️ | X% |
| Academic | ✅/⚠️ | X% |
| H1=name | ✅/❌ | |
| Intro | ✅/❌ | buyer guide/определение |
| Обращения | ✅/⚠️ | есть/нет |
| Паттерны | ✅/⚠️ | X шт |
| Таблицы | ✅/⚠️ | дубль/уникальные |
| FAQ | ✅/❌ | дубль/уникальные |
| Keywords | ✅/⚠️/❌ | primary X/X, secondary X/X |
| Facts | ✅/⚠️/❌ | vs RESEARCH_DATA.md |
| **VERDICT** | **✅/⚠️/❌** | |

### Step 7: Fix if needed

**BLOCKER fixes (must):**
- H1 ≠ name → Replace H1
- How-to sections → Delete or convert to 1-2 sentences
- Stem >3.0% → Replace with synonyms
- Nausea >4.0 → Add variety
- Intro = определение → Rewrite: польза + сценарий выбора
- FAQ дублирует таблицу → Replace with unique question
- Противоречие с Research → Fix to match research
- >2 primary keywords missing → Add missing keywords

**WARNING fixes (should):**
- No H2 with secondary keyword → Rewrite 1 H2
- Water >75% → Remove filler words
- Academic <6% → Add reader engagement
- <3 паттернов "Если X → Y" → Add choice scenarios
- Нет обращений к читателю → Add reader addressing

### Step 8: Re-validate after fix

Run same 4 scripts + re-check qualitative criteria.

### Step 9: Output verdict

```
✅ PASS: {slug} — контент валиден
⚠️ WARNING: {slug} — мелкие замечания, можно деплоить
❌ FIXED: {slug} — исправлено X проблем, re-validated OK
```

---

## Quality Criteria Reference

### BLOCKER (must fix)

| Issue | Detection | Fix |
|-------|-----------|-----|
| H1 ≠ name | H1 должен = name (мн.ч.) | Replace H1 |
| How-to sections | H2/H3: "Как наносить", "Техника" | Delete section |
| Stem >3.0% | check_keyword_density.py | Use synonyms |
| Nausea >4.0 | check_water_natasha.py | Add variety |
| Intro = определение | "X — это Y, которое..." | Rewrite |
| FAQ дублирует таблицу | Same question in table | Replace question |
| Противоречие с Research | Факт ≠ RESEARCH_DATA | Fix fact |
| >2 primary missing | Keywords coverage | Add keywords |

### WARNING (should fix)

| Issue | Detection | Fix |
|-------|-----------|-----|
| No H2 with secondary | Manual check | Rewrite 1 H2 |
| Water >75% | check_water_natasha.py | Remove filler |
| Academic <6% | check_water_natasha.py | Add engagement |
| <3 "Если X → Y" | Count patterns | Add scenarios |
| Нет обращений | Search "вам" | Add addressing |

---

## Synonyms for spam reduction

| Слово | Синонимы |
|-------|----------|
| средство | состав, продукт, препарат |
| очиститель | состав, продукт, химия |
| поверхность | покрытие, основа, материал |
| защита | барьер, слой, покрытие |
| автомобиль | авто, машина, транспорт |

---

## Output

После завершения агент выводит:

```
## Review: {slug}

**Verdict:** ✅ PASS / ⚠️ WARNING / ❌ FIXED

| Критерий | Результат |
|----------|-----------|
| ... | ... |

**Исправления:** (если были)
- {описание фикса 1}
- {описание фикса 2}

**Следующий шаг:** content-reviewer {next-slug}
```

---

## Открытые вопросы

1. **Batch mode?** — Нужен ли режим обработки нескольких категорий за раз?
2. **Auto-commit?** — Агент сам коммитит исправления или оставляет staged?
3. **Progress tracking?** — Обновлять статус в плане или отдельный файл?

---

**Version:** 1.0 | **Author:** Claude
