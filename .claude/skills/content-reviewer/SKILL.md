---
name: content-reviewer
description: Ревизия и исправление контента категории по плану v3.0. Use when /content-reviewer {path}, нужно проверить контент, выполнить ревизию, пофиксить проблемы в тексте, review content. Автономный режим — находит и исправляет проблемы без интерактивности.
---

# Content Reviewer v2.0

Проверка и исправление контента **одной категории** за вызов.

## Input

```
/content-reviewer {path}
/content-reviewer moyka-i-eksterer/avtoshampuni/aktivnaya-pena
```

## Data Files

```
categories/{path}/
├── content/{slug}_ru.md        # Контент для ревизии
├── data/{slug}_clean.json      # name, parent_id, keywords
├── meta/{slug}_meta.json       # h1, keywords_in_content
└── research/RESEARCH_DATA.md   # Источник истины для фактов
```

---

## Commercial Intent (центральный принцип)

**Главный вопрос текста:** "Какой товар мне купить?"

**Тест каждой секции:**
> "Эта секция помогает ВЫБРАТЬ товар или УЧИТ его использовать?"

| Ответ | Действие |
|-------|----------|
| Помогает выбрать | ✅ Оставить |
| Учит использовать | ❌ Удалить или переделать |

### Коммерческий vs Информационный

| ✅ Коммерческий | ❌ Информационный |
|-----------------|-------------------|
| "Если нужен X → выбирай Y" | "Как работает X" |
| Таблица "Тип → Когда брать" | Пошаговая инструкция |
| Сценарии: новичок/профи/бюджет | Теория и принципы |
| FAQ про выбор | FAQ про процессы |

---

## Dryness Diagnosis

| # | Признак | Weight |
|---|---------|--------|
| 1 | Intro = определение "X — это Y..." | 2 |
| 2 | Нет обращений "вам", "если вы" | 1 |
| 3 | <3 паттернов "Если X → Y" | 1 |
| 4 | Таблицы без "Когда брать" | 1 |
| 5 | FAQ про процесс | 2 |
| 6 | Academic <7% | 1 |
| 7 | Нет секции "Сценарии покупки" | 1 |

**Verdict:**
- 0-2 → ✅ TEXT OK
- 3-4 → ⚠️ MINOR FIXES
- 5+ → ❌ REWRITE NEEDED

---

## Workflow

```
Step 1: Read files (parallel)
Step 2: Run validators (parallel)
Step 3: Keywords Coverage (100% required)
Step 4: Research Completeness
Step 5: Commercial Intent Check
Step 6: Dryness Diagnosis
Step 7: Verdict table
Step 8: Fix if BLOCKER or REWRITE if needed
Step 9: Re-validate
Step 10: Output verdict
```

### Step 1: Read files (parallel)

- `_clean.json` → name, parent_id
- `_meta.json` → h1, keywords_in_content
- `RESEARCH_DATA.md` → источник истины
- `{slug}_ru.md` → контент

### Step 2: Run validators (parallel)

```bash
python3 scripts/validate_meta.py categories/{path}/meta/{slug}_meta.json
python3 scripts/validate_content.py categories/{path}/content/{slug}_ru.md "{primary}" --mode seo
python3 scripts/check_keyword_density.py categories/{path}/content/{slug}_ru.md
python3 scripts/check_water_natasha.py categories/{path}/content/{slug}_ru.md
```

### Step 3: Keywords Coverage (100% required)

| Группа | Требование | Severity |
|--------|------------|----------|
| primary | **100%** | BLOCKER |
| secondary | **100%** | BLOCKER |
| supporting | **≥80%** | WARNING |

**Куда распределять:** Intro (primary), H2 (secondary), Сценарии/Таблицы (supporting)

### Step 4: Research Completeness

| Блок Research | Проверка | Severity |
|---------------|----------|----------|
| Блок 2: Виды и типы | **Все типы** в тексте | BLOCKER |
| Блок 6а: Спорные | НЕ использованы | BLOCKER |
| Блок 1, 3, 5 | Факты отражены | WARNING |

### Step 5: Commercial Intent Check

Каждая секция про ВЫБОР, не про использование?

### Step 6: Dryness Diagnosis

Подсчёт признаков → verdict (TEXT OK / MINOR / REWRITE)

### Step 7: Verdict table

| Критерий | Результат | Примечание |
|----------|-----------|------------|
| Meta | ✅/❌ | validate_meta.py |
| Density | ✅/⚠️/❌ | stem max X% |
| Academic | ✅/⚠️ | X% (≥7%) |
| **Keywords** | ✅/⚠️/❌ | **primary X/X, secondary X/X** |
| **Research Types** | ✅/❌ | **все типы из Блок 2** |
| **Commercial Intent** | ✅/❌ | все секции про выбор |
| **Dryness** | ✅/⚠️/❌ | TEXT OK / MINOR / REWRITE |
| Intro | ✅/❌ | buyer guide / определение |
| Сценарии покупки | ✅/❌ | есть секция |
| FAQ | ✅/❌ | про выбор / про процесс |
| **VERDICT** | **✅/⚠️/❌** | |

---

## Reference-based Rewrite

**Когда:** REWRITE NEEDED (Dryness 5+)

### Референсные тексты

```
categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/content/antibitum_ru.md
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/content/cherniteli-shin_ru.md
```

### Паттерны из референсов

| Элемент | Паттерн |
|---------|---------|
| **Intro** | польза + "если X → Y" + обращение |
| **Таблица типов** | колонка "Когда брать" |
| **Сценарии покупки** | **Жирное условие** → решение |
| **FAQ** | Вопрос про ВЫБОР |
| **Итог** | → сценарии |

---

## BLOCKER Fixes

| Issue | Fix |
|-------|-----|
| H1 ≠ name | Replace H1 |
| How-to sections | Delete or convert |
| Stem >3.0% | Replace with synonyms |
| Intro = определение | Rewrite: польза + сценарий |
| >2 primary missing | Add keywords organically |
| Research types missing | Add all types |

## How-to STOP-LIST

| ❌ Запрещено | ✅ Альтернатива |
|--------------|-----------------|
| "Как наносить X" | "Что учесть при выборе" |
| "Техника применения" | Убрать секцию |
| "Пошаговая инструкция" | Удалить |

---

## Output Format

```markdown
## Review: {slug}

**Path:** categories/{path}
**Verdict:** ✅ PASS / ⚠️ WARNING / ❌ FIXED

### Verdict Table

| Критерий | Результат | Примечание |
|----------|-----------|------------|
| ... | ... | ... |

### Исправления (если были)

1. ...
2. ...

### Re-validation

✅ All validators passed after fixes
```

---

## ВАЖНО

1. **НЕ коммитить** — только Edit. Коммит вручную.
2. **RESEARCH_DATA.md — источник истины** для фактов.
3. **Одна категория за вызов**.
4. **Buyer guide, не how-to**.
5. **Academic ≥7%** — если ниже, добавить обращения.
