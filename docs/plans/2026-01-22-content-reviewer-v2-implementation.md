# Content-Reviewer v2.0 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Обновить content-reviewer агент и скилл для полноценной ревизии контента как buyer guide с коммерческим интентом, 100% покрытием ключей и сравнением с RESEARCH_DATA.md.

**Architecture:** Расширяем существующий workflow добавлением 4 новых проверок: Commercial Intent, Dryness Diagnosis, Keywords 100%, Research Completeness. При обнаружении "сухого" текста — переписывание по образцу референсных текстов.

**Tech Stack:** Markdown агенты/скиллы, Python validators, Edit tool для исправлений.

**Design Doc:** `docs/plans/2026-01-22-content-reviewer-v2-design.md`

---

## Task 1: Update content-reviewer agent — Add Commercial Intent section

**Files:**
- Modify: `.claude/agents/content-reviewer.md:29-101` (после Workflow, перед Step 3)

**Step 1: Добавить секцию Commercial Intent после Data Files**

Вставить после строки 27 (`---`):

```markdown
## Commercial Intent (центральный принцип)

**Главный вопрос текста:** "Какой товар мне купить?"

**Тест каждой секции:**
> "Эта секция помогает ВЫБРАТЬ товар или УЧИТ его использовать?"

| Ответ | Действие |
|-------|----------|
| Помогает выбрать | ✅ Оставить |
| Учит использовать | ❌ Удалить или переделать |

### Коммерческий vs Информационный

| ✅ Коммерческий (оставлять) | ❌ Информационный (удалять) |
|----------------------------|----------------------------|
| "Если нужен X → выбирай Y" | "Как работает X" |
| Таблица "Тип → Когда брать" | Пошаговая инструкция 5+ шагов |
| "На что смотреть на этикетке" | "История создания" |
| Сценарии: новичок/профи/бюджет | Теория и принципы |
| FAQ про выбор | FAQ про процессы |
| "Чего избегать при выборе" | "Ошибки при нанесении" |
| "Что влияет на результат" | "Как правильно наносить" |

---
```

**Step 2: Verify change applied**

```bash
grep -n "Commercial Intent" .claude/agents/content-reviewer.md
```

Expected: Line number with "Commercial Intent"

---

## Task 2: Update agent — Add Dryness Diagnosis

**Files:**
- Modify: `.claude/agents/content-reviewer.md` (после Commercial Intent)

**Step 1: Добавить секцию Dryness Diagnosis**

```markdown
## Dryness Diagnosis (диагностика "сухости")

**Признаки "сухого" текста (справочника):**

| # | Признак | Как проверить | Weight |
|---|---------|---------------|--------|
| 1 | Intro = определение | Начинается с "X — это Y, которое..." | 2 |
| 2 | Нет обращений | Отсутствуют "вам", "если вы", "выбирайте" | 1 |
| 3 | <3 паттернов "Если X → Y" | Подсчёт сценариев | 1 |
| 4 | Таблицы без "Когда брать" | Колонки характеристик, не сценариев | 1 |
| 5 | FAQ про процесс | "Как наносить?" вместо "Какой выбрать?" | 2 |
| 6 | Academic <7% | check_water_natasha.py | 1 |
| 7 | Нет секции "Сценарии" | Отсутствует блок сценариев покупки | 1 |

**Verdict по сумме весов:**
- 0-2 → ✅ TEXT OK
- 3-4 → ⚠️ MINOR FIXES
- 5+ → ❌ REWRITE NEEDED

---
```

**Step 2: Verify change applied**

```bash
grep -n "Dryness Diagnosis" .claude/agents/content-reviewer.md
```

Expected: Line number with "Dryness Diagnosis"

---

## Task 3: Update agent — Strengthen Keywords Coverage to 100%

**Files:**
- Modify: `.claude/agents/content-reviewer.md` (секция Step 3: Keywords Coverage)

**Step 1: Заменить текущую секцию Keywords Coverage**

Найти и заменить секцию Step 3 на:

```markdown
### Step 3: Keywords Coverage (100% required)

**Источник:** `_meta.json` → `keywords_in_content`

**Требования:**

| Группа | Требование | Severity |
|--------|------------|----------|
| primary | **100%** — все в тексте | BLOCKER |
| secondary | **100%** — все в тексте | BLOCKER |
| supporting | **≥80%** | WARNING |

**Куда распределять ключи:**

| Место | Какие ключи | Приоритет |
|-------|-------------|-----------|
| Intro | primary + 1-2 secondary | HIGH |
| H2 заголовки | secondary (минимум 1 H2) | HIGH |
| Сценарии покупки | supporting | MEDIUM |
| Таблицы | supporting | MEDIUM |
| FAQ | secondary | MEDIUM |
| Итог | primary | LOW |

**Workflow:**

1. Выписать ВСЕ ключи из `_meta.json`
2. Для каждого — выделить стем (основу)
3. Grep в контенте — найдено/нет
4. Если не найдено → найти место, вставить органично
5. После вставки — проверить density (<3%)

**Формат:** `Keywords: primary 3/3 ✅, secondary 3/3 ✅, supporting 4/4 ✅`
```

**Step 2: Verify change applied**

```bash
grep -n "100% required" .claude/agents/content-reviewer.md
```

Expected: Line number with "100% required"

---

## Task 4: Update agent — Add Research Completeness check

**Files:**
- Modify: `.claude/agents/content-reviewer.md` (после Step 4: Facts vs Research)

**Step 1: Расширить секцию Facts vs Research**

Заменить Step 4 на:

```markdown
### Step 4: Research Completeness

**Источник истины:** `RESEARCH_DATA.md`

**Что проверять:**

| Блок Research | Что проверять | Severity |
|---------------|---------------|----------|
| Блок 2: Виды и типы | **Все типы** упомянуты в тексте? | BLOCKER |
| Блок 1: Что это | Ключевые факты использованы? | WARNING |
| Блок 3: Как выбрать | Сценарии выбора отражены? | WARNING |
| Блок 5: Ошибки | Важные предупреждения есть? | WARNING |
| Блок 6а: Спорные | НЕ использованы без подтверждения? | BLOCKER |

**Checklist:**

- [ ] Все типы товаров из Блок 2 в таблице или сценариях
- [ ] Нет противоречий с фактами из research
- [ ] Спорные утверждения (Блок 6а) НЕ использованы
- [ ] Цифры только подтверждённые (Блок 10)

**Формат:** `Research: types 4/4 ✅, facts 5/7 ⚠️, contradictions 0 ✅`
```

**Step 2: Verify change applied**

```bash
grep -n "Research Completeness" .claude/agents/content-reviewer.md
```

Expected: Line number with "Research Completeness"

---

## Task 5: Update agent — Add Reference-based Rewrite workflow

**Files:**
- Modify: `.claude/agents/content-reviewer.md` (перед Output Format)

**Step 1: Добавить секцию Reference-based Rewrite**

```markdown
## Reference-based Rewrite

**Когда:** Verdict = REWRITE NEEDED (Dryness score 5+)

### Референсные тексты (читать перед переписыванием)

```
categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/content/antibitum_ru.md
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/content/cherniteli-shin_ru.md
```

### Паттерны из референсов

| Элемент | Паттерн |
|---------|---------|
| **Intro** | польза + "если X → Y" сценарий + обращение |
| **Таблица типов** | колонка "Когда брать" |
| **Сценарии покупки** | **Жирное условие** → решение + почему |
| **На этикетке** | Маркер → Что означает → Рекомендация |
| **Что влияет** | Фактор → Влияние (НЕ how-to!) |
| **Чего избегать** | Антипаттерн покупки + почему |
| **FAQ** | Вопрос про ВЫБОР |
| **Итог** | "что вам покупать" + → сценарии |

### Структура buyer guide

```markdown
# {H1}

{Intro: польза + "если X → Y" + обращение}

## Как выбрать {категорию}

| Тип | {Параметр} | Когда брать |
|-----|------------|-------------|

**Сценарии покупки:**
- **{Условие}** → {решение + почему}

## На что смотреть на этикетке

| Маркер | Что означает | Рекомендация |
|--------|--------------|--------------|

## Что влияет на результат

| Фактор | Влияние |
|--------|---------|

## Чего избегать при выборе

**{Антипаттерн}** — {почему плохо}.

## FAQ

### {Вопрос про выбор}?
{Ответ}

---

**Итог — что вам покупать:**
- **{Сценарий}** → {рекомендация}
```

---
```

**Step 2: Verify change applied**

```bash
grep -n "Reference-based Rewrite" .claude/agents/content-reviewer.md
```

Expected: Line number with "Reference-based Rewrite"

---

## Task 6: Update agent — Update Verdict Table

**Files:**
- Modify: `.claude/agents/content-reviewer.md` (секция Step 6: Verdict table)

**Step 1: Заменить verdict table**

```markdown
### Step 6: Verdict table

| Критерий | Результат | Примечание |
|----------|-----------|------------|
| Meta | ✅/❌ | validate_meta.py |
| Density | ✅/⚠️/❌ | stem max X% |
| Тошнота | ✅/⚠️/❌ | classic X |
| Вода | ✅/⚠️ | X% |
| Academic | ✅/⚠️ | X% (≥7%) |
| H1=name | ✅/❌ | |
| **Keywords** | ✅/⚠️/❌ | **primary X/X, secondary X/X, supporting X/X** |
| **Research Types** | ✅/❌ | **все типы из Блок 2** |
| **Research Facts** | ✅/⚠️ | ключевые факты |
| **Commercial Intent** | ✅/❌ | все секции про выбор |
| **Dryness** | ✅/⚠️/❌ | TEXT OK / MINOR / REWRITE |
| Intro | ✅/❌ | buyer guide / определение |
| Обращения | ✅/⚠️ | есть / нет |
| Паттерны | ✅/⚠️ | X шт (≥3) |
| Сценарии покупки | ✅/❌ | есть секция |
| FAQ | ✅/❌ | про выбор / про процесс |
| **VERDICT** | **✅/⚠️/❌** | |
```

**Step 2: Verify change applied**

```bash
grep -n "Research Types" .claude/agents/content-reviewer.md
```

Expected: Line number with "Research Types"

---

## Task 7: Update agent — Update Workflow Steps

**Files:**
- Modify: `.claude/agents/content-reviewer.md` (секция Workflow)

**Step 1: Обновить список шагов workflow**

Заменить начало Workflow на:

```markdown
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
```

**Step 2: Verify final agent structure**

```bash
wc -l .claude/agents/content-reviewer.md
```

Expected: ~400-450 lines (was 274)

---

## Task 8: Sync changes to skill file

**Files:**
- Modify: `.claude/skills/content-reviewer/SKILL.md`

**Step 1: Обновить skill файл с теми же изменениями**

Skill файл должен содержать:
- Commercial Intent section (компактная версия)
- Dryness Diagnosis (компактная версия)
- Keywords 100% requirement
- Research Completeness
- Reference texts paths
- Updated verdict table

**Step 2: Verify skill updated**

```bash
wc -l .claude/skills/content-reviewer/SKILL.md
```

Expected: ~280-320 lines (was 181)

---

## Task 9: Update UK content-reviewer agent

**Files:**
- Modify: `.claude/agents/uk-content-reviewer.md`

**Step 1: Добавить те же секции с UK терминологией**

- Commercial Intent → "Комерційний інтент"
- Dryness Diagnosis → "Діагностика сухості"
- Keywords 100% → same logic
- Research Completeness → same logic
- Reference texts → UK versions when available

**Step 2: Verify UK agent updated**

```bash
wc -l .claude/agents/uk-content-reviewer.md
```

Expected: ~450-500 lines (was 327)

---

## Task 10: Test on real category

**Files:**
- Test: `categories/moyka-i-eksterer/ochistiteli-kuzova/antimoshka/`

**Step 1: Run updated content-reviewer**

```bash
# Invoke content-reviewer agent on test category
```

**Step 2: Verify all new checks work**

- [ ] Commercial Intent check runs
- [ ] Dryness Diagnosis calculates score
- [ ] Keywords shows 100% requirement
- [ ] Research Types checked
- [ ] If REWRITE → references are read

**Step 3: Check output format**

Verify verdict table contains new rows:
- Keywords (primary X/X, secondary X/X, supporting X/X)
- Research Types
- Commercial Intent
- Dryness

---

## Task 11: Commit all changes

**Files:**
- All modified agent and skill files

**Step 1: Stage changes**

```bash
git add .claude/agents/content-reviewer.md
git add .claude/skills/content-reviewer/SKILL.md
git add .claude/agents/uk-content-reviewer.md
git add docs/plans/2026-01-22-content-reviewer-v2-design.md
git add docs/plans/2026-01-22-content-reviewer-v2-implementation.md
```

**Step 2: Commit**

```bash
git commit -m "feat(agents): content-reviewer v2.0 with commercial intent and 100% keywords

- Add Commercial Intent check (buyer guide vs how-to)
- Add Dryness Diagnosis (7 criteria scoring)
- Require 100% primary/secondary keywords coverage
- Add Research Completeness check (all types from RESEARCH_DATA.md)
- Add Reference-based Rewrite workflow with 3 reference texts
- Update verdict table with new criteria
- Sync changes to skill and UK agent

Design: docs/plans/2026-01-22-content-reviewer-v2-design.md

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Execution Checklist

| Task | Description | Status |
|------|-------------|--------|
| 1 | Add Commercial Intent section | ⬜ |
| 2 | Add Dryness Diagnosis | ⬜ |
| 3 | Strengthen Keywords to 100% | ⬜ |
| 4 | Add Research Completeness | ⬜ |
| 5 | Add Reference-based Rewrite | ⬜ |
| 6 | Update Verdict Table | ⬜ |
| 7 | Update Workflow Steps | ⬜ |
| 8 | Sync to skill file | ⬜ |
| 9 | Update UK agent | ⬜ |
| 10 | Test on real category | ⬜ |
| 11 | Commit all changes | ⬜ |

---

**Plan Version:** 1.0 | **Created:** 2026-01-22
