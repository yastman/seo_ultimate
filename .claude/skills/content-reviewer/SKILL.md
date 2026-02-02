---
name: content-reviewer
description: Ревизия и исправление контента категории по плану v3.0. Use when /content-reviewer {path}, нужно проверить контент, выполнить ревизию, пофиксить проблемы в тексте, review content. Автономный режим — находит и исправляет проблемы без интерактивности.
---

# Content Reviewer v2.2

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
Step 8a: Fix Density/Nausea (if BLOCKER)
Step 9: Re-validate Coverage (max 3 iterations)
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
python3 scripts/validate_density.py categories/{path}/content/{slug}_ru.md
python3 scripts/check_water_natasha.py categories/{path}/content/{slug}_ru.md
```

### Step 3: Keywords Coverage (audit_coverage.py)

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang ru --json --include-meta
```

**Два источника ключей:**
1. `keywords_in_content` из _meta.json (primary/secondary/supporting) — **строгая проверка**
2. `keywords[]` из _clean.json — **информативная проверка**

**Правила вердикта:**

| Источник | Группа | Требование | При фейле |
|----------|--------|------------|-----------|
| keywords_in_content | primary | 100% COVERED | BLOCKER |
| keywords_in_content | secondary | 100% COVERED | BLOCKER |
| keywords_in_content | supporting | ≥80% COVERED | WARNING |
| keywords[] | all | adaptive threshold | BLOCKER |

**Adaptive thresholds для keywords[]:** ≤5 ключей → 70%, 6-15 → 60%, >15 → 50%

**Статуси покриття:**
- ✅ COVERED: `EXACT`, `NORM`, `LEMMA`
- ❌ NOT COVERED: `SYNONYM`, `PARTIAL`, `ABSENT`

> **SYNONYM = NOT COVERED:** Синонім знайдено в тексті, але сам ключ — відсутній. Для SEO потрібен саме ключ.

**Формат вывода:**

```markdown
### Keywords Coverage

| Источник | Covered | Total | % | Status |
|----------|---------|-------|---|--------|
| primary+secondary | 8/8 | 100% | ✅ PASS |
| supporting | 4/5 | 80% | ✅ PASS |
| keywords[] | 8/15 | 53% | ⚠️ WARNING (threshold 50%) |

**NOT COVERED (primary/secondary):** нет
**NOT COVERED (keywords[]):** ключ1 (1200), ключ2 (800)
```

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

### Step 8a: Fix Density/Nausea (if BLOCKER)

**Trigger:** Step 2 validators show:
- `validate_density.py`: stem >3.0%
- `check_water_natasha.py`: classic nausea >4.0

**Algorithm:**

1. From validator output, identify overused word:
   - Density: `"пена*" — 15 раз (3.8%)`
   - Nausea: `Самое частое слово: 'пена' (15 раз)`

2. Find all occurrences in `{slug}_ru.md`

3. Decide which to keep (3-4 max):
   - ✅ Keep: first mention in intro
   - ✅ Keep: H2 headings
   - ✅ Keep: table headers
   - ❌ Replace: body text repetitions

4. Replace excess with contextual synonyms:
   - Choose synonym based on sentence context
   - Match grammatical case/gender
   - Common alternatives: "средство", "состав", "продукт", "формула"

5. Re-run validator:
   ```bash
   python3 scripts/validate_density.py categories/{path}/content/{slug}_ru.md
   ```

6. Repeat until ≤2.5% or max 3 iterations

7. Log all replacements made

**Example:**
```
Before: "пена" × 15 (3.8%)
After:  "пена" × 4 + "средство" × 5 + "состав" × 3 + "продукт" × 3 = 1.0%
```

---

## Step 9: Re-validate Coverage (MANDATORY)

**Обов'язково після будь-яких виправлень!**

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang ru --json --include-meta
```

**Цикл виправлень (max 3 ітерації):**

```
Iteration 1: Fix → Re-validate → check NOT COVERED
Iteration 2: Fix remaining → Re-validate → check NOT COVERED
Iteration 3: Fix remaining → Re-validate → STOP
```

**Якщо після 3 ітерацій залишаються NOT COVERED:**
- Задокументувати в логу які ключі не вдалося вставити
- Перейти до фінального verdict

**Куди вставляти непокриті ключі:**

| Пріоритет | Куди | Приклад |
|-----------|------|---------|
| **primary** | Intro (перший абзац) | "...{keyword} поможет..." |
| **secondary** | H2 заголовки | "## Как выбрать {keyword}" |
| **supporting** | Сценарии, таблицы, FAQ | "**Для {keyword}** — ..." |

**Техніка органічного впровадження:**
- Знайди речення за змістом близьке до ключа
- Переформулюй з включенням ключа
- НЕ додавай нові факти — використовуй RESEARCH_DATA.md

---

## BLOCKER Fixes

| Issue | Fix |
|-------|-----|
| H1 ≠ name | Replace H1 |
| How-to sections | Delete or convert |
| Stem >3.0% | Step 8a: auto-replace with synonyms |
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
6. **НЕ ВЫДУМЫВАЙ факты** — при добавлении ключей используй ТОЛЬКО информацию из RESEARCH_DATA.md. Если нет подходящего факта — внедряй ключ в существующий контекст без новых утверждений.

---

**Version:** 2.2 — February 2026

**Changelog v2.2:**
- **ADDED: Step 8a** — auto-fix density/nausea with synonym replacement
- Iterative cycle: fix → re-validate → repeat (max 3 iterations)

**Changelog v2.1:**
- **SYNCED with UK v2.3** — повний паритет
- ADDED: max 3 ітерації для циклу виправлень
- ADDED: SYNONYM = NOT COVERED (explicit)
- ADDED: Таблиця куди вставляти непокриті ключі
- ADDED: Техніка органічного впровадження
