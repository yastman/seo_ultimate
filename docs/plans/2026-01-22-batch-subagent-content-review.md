# Batch Content Review via Subagent — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Автоматически проверить и исправить все 50 русских категорий через субагента `content-reviewer` с полным автофиксом.

**Architecture:** Вызов субагента `Task(subagent_type="content-reviewer")` для каждой категории. Субагент выполняет полный workflow: валидаторы → анализ ключей/плотности/research → автофикс BLOCKERs → отчёт. Режим: автономный (без интерактивности).

**Tech Stack:** Task tool с `subagent_type="content-reviewer"`, Python validators, Edit tool

---

## Что делает субагент content-reviewer

Субагент `content-reviewer` (из `.claude/agents/content-reviewer.md`) выполняет:

1. **Чтение файлов** (parallel): `_clean.json`, `_meta.json`, `RESEARCH_DATA.md`, `{slug}_ru.md`
2. **4 валидатора** (parallel):
   - `validate_meta.py` — мета-теги
   - `validate_content.py --mode seo` — структура контента
   - `check_keyword_density.py` — плотность ключей (stem ≤3%, nausea ≤4)
   - `check_water_natasha.py` — вода, академичность (≥7%)
3. **Покрытие ключей**: primary 100%, secondary 100%, supporting ≥80%
4. **Соответствие Research**: все типы из Блок 2, нет противоречий
5. **Commercial Intent**: каждая секция → "выбор или использование?"
6. **Dryness Diagnosis**: intro, обращения, паттерны "Если X → Y"
7. **Verdict Table**: сводка критериев
8. **Автофикс BLOCKERs**: H1, density, how-to секции, ключи
9. **Re-validate**: повторная проверка
10. **Отчёт**: PASS/WARNING/FIXED

---

## Категории (50 шт)

```
categories/aksessuary/
categories/aksessuary/aksessuary-dlya-naneseniya-sredstv/
categories/aksessuary/gubki-i-varezhki/
categories/aksessuary/malyarniy-skotch/
categories/aksessuary/mikrofibra-i-tryapki/
categories/aksessuary/nabory/
categories/aksessuary/raspyliteli-i-penniki/
categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/
categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/
categories/aksessuary/vedra-i-emkosti/
categories/moyka-i-eksterer/
categories/moyka-i-eksterer/avtoshampuni/
categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/
categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/
categories/moyka-i-eksterer/ochistiteli-dvigatelya/
categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/
categories/moyka-i-eksterer/ochistiteli-kuzova/antimoshka/
categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/
categories/moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli/
categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov/
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin/
categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/
categories/moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol/
categories/moyka-i-eksterer/sredstva-dlya-stekol/omyvatel/
categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/
categories/oborudovanie/
categories/oborudovanie/apparaty-tornador/
categories/opt-i-b2b/
categories/polirovka/
categories/polirovka/polirovalnye-krugi/mekhovye/
categories/polirovka/polirovalnye-mashinki/akkumulyatornaya/
categories/polirovka/polirovalnye-pasty/
categories/ukhod-za-intererom/
categories/ukhod-za-intererom/neytralizatory-zapakha/
categories/ukhod-za-intererom/poliroli-dlya-plastika/
categories/ukhod-za-intererom/pyatnovyvoditeli/
categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/
categories/ukhod-za-intererom/sredstva-dlya-kozhi/
categories/ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi/
categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/
categories/zashchitnye-pokrytiya/
categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/
categories/zashchitnye-pokrytiya/kvik-deteylery/
categories/zashchitnye-pokrytiya/silanty/
categories/zashchitnye-pokrytiya/voski/
categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/
categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/
```

---

## Execution Strategy

### Option A: Sequential (рекомендуется)

Запуск субагентов **по одному** с паузой для review:

```
Task(subagent_type="content-reviewer", prompt="Review and fix: aksessuary")
→ Ожидание результата
→ Review отчёта
→ Task(subagent_type="content-reviewer", prompt="Review and fix: aksessuary-dlya-naneseniya-sredstv")
→ ...
```

**Преимущества:**
- Контроль на каждом шаге
- Можно прервать если что-то не так
- Легко отслеживать прогресс

### Option B: Batch Parallel (5-10 за раз)

Запуск **нескольких субагентов параллельно**:

```
Task(subagent_type="content-reviewer", prompt="aksessuary", run_in_background=true)
Task(subagent_type="content-reviewer", prompt="aksessuary-dlya-naneseniya-sredstv", run_in_background=true)
Task(subagent_type="content-reviewer", prompt="gubki-i-varezhki", run_in_background=true)
...
```

**Преимущества:**
- Быстрее
- Меньше ручного вмешательства

**Риски:**
- Сложнее отследить ошибки
- Конфликты при редактировании (маловероятно — разные файлы)

---

## Task Template

### Task N: Review {path}

**Step 1: Launch subagent**

```
Task(
  subagent_type="content-reviewer",
  description="Review {slug}",
  prompt="Review and auto-fix category: {path}"
)
```

**Step 2: Subagent executes full workflow**

Субагент автономно:
1. Читает `data/`, `meta/`, `content/`, `research/`
2. Запускает 4 валидатора
3. Проверяет keywords coverage (100% primary/secondary, ≥80% supporting)
4. Сверяет с RESEARCH_DATA.md
5. Анализирует commercial intent
6. Оценивает "сухость" текста
7. Фиксит BLOCKERs через Edit
8. Re-validate
9. Выдаёт verdict

**Step 3: Review result**

Проверить отчёт субагента:
- PASS → next
- WARNING → note, next
- FIXED → verify changes, next

---

## BLOCKER Criteria (auto-fix)

| Issue | Detection | Auto-Fix |
|-------|-----------|----------|
| H1 ≠ name | H1 должен = `_clean.json`.name (мн.ч.) | Replace H1 |
| Stem >3.0% | check_keyword_density.py | Replace with synonyms |
| Nausea >4.0 | check_water_natasha.py | Add variety |
| Intro = definition | "X — это Y, которое..." | Rewrite: benefit + scenario |
| How-to sections | H2: "Как наносить", "Техника" | Delete or convert |
| >2 primary missing | Keywords coverage | Add organically |
| Research contradiction | Fact ≠ RESEARCH_DATA | Fix to match |

---

## WARNING Criteria (report only)

| Issue | Detection | Action |
|-------|-----------|--------|
| Water >75% | check_water_natasha.py | Report |
| Academic <7% | check_water_natasha.py | Report |
| <3 "Если X → Y" patterns | Count | Report |
| 1-2 primary missing | Coverage | Add if easy |

---

## Batch Execution Plan

### Batch 1: aksessuary (10 categories)

```
[ ] aksessuary
[ ] aksessuary-dlya-naneseniya-sredstv
[ ] gubki-i-varezhki
[ ] malyarniy-skotch
[ ] mikrofibra-i-tryapki
[ ] nabory
[ ] raspyliteli-i-penniki
[ ] kisti-dlya-deteylinga
[ ] shchetka-dlya-moyki-avto
[ ] vedra-i-emkosti
```

### Batch 2: moyka-i-eksterer (18 categories)

```
[ ] moyka-i-eksterer
[ ] avtoshampuni
[ ] aktivnaya-pena
[ ] shampuni-dlya-ruchnoy-moyki
[ ] ochistiteli-dvigatelya
[ ] antibitum
[ ] antimoshka
[ ] glina-i-avtoskraby
[ ] obezzhirivateli
[ ] ukhod-za-naruzhnym-plastikom
[ ] cherniteli-shin
[ ] keramika-dlya-diskov
[ ] ochistiteli-diskov
[ ] ochistiteli-shin
[ ] antidozhd
[ ] ochistiteli-stekol
[ ] omyvatel
[ ] polirol-dlya-stekla
```

### Batch 3: oborudovanie + polirovka (7 categories)

```
[ ] oborudovanie
[ ] apparaty-tornador
[ ] opt-i-b2b
[ ] polirovka
[ ] mekhovye
[ ] akkumulyatornaya
[ ] polirovalnye-pasty
```

### Batch 4: ukhod-za-intererom (8 categories)

```
[ ] ukhod-za-intererom
[ ] neytralizatory-zapakha
[ ] poliroli-dlya-plastika
[ ] pyatnovyvoditeli
[ ] sredstva-dlya-khimchistki-salona
[ ] sredstva-dlya-kozhi
[ ] ochistiteli-kozhi
[ ] ukhod-za-kozhey
```

### Batch 5: zashchitnye-pokrytiya (7 categories)

```
[ ] zashchitnye-pokrytiya
[ ] keramika-i-zhidkoe-steklo
[ ] kvik-deteylery
[ ] silanty
[ ] voski
[ ] tverdyy-vosk
[ ] zhidkiy-vosk
```

---

## Post-Execution

### Step 1: Generate summary report

После всех категорий — сводный отчёт:

```markdown
## Batch Review Summary

| Category | Verdict | Issues Fixed |
|----------|---------|--------------|
| aksessuary | PASS | — |
| ... | FIXED | H1, +3 keywords |

**Total:**
- PASS: X
- WARNING: Y
- FIXED: Z
```

### Step 2: Commit changes

```bash
git add categories/
git commit -m "refactor(content): batch review and fixes for all RU categories

- Fixed H1 mismatches
- Added missing keywords
- Improved commercial intent focus
- Removed how-to sections
- Normalized keyword density

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Important Notes

1. **НЕ коммитить автоматически** — только Edit файлы. Коммит после всего батча.
2. **RESEARCH_DATA.md — источник истины** для фактов.
3. **entities в _clean.json НЕ использовать** — автогенерированные.
4. **Buyer guide, не how-to** — секции про применение удалять.
5. **Субагент работает автономно** — не требует input от пользователя.
