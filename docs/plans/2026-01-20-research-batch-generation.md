# Research Batch Generation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate RESEARCH_PROMPT.md for 16 categories without research data, in batches of 4 using parallel subagents.

**Architecture:** Launch 4 parallel Task agents per batch, each running seo-research workflow for one category. After each batch, user takes RESEARCH_PROMPT.md files to Perplexity Deep Research.

**Tech Stack:** Task tool (subagent_type: general-purpose), Read/Write tools, seo-research agent instructions

---

## Categories Without Research (16 total)

### Batch 1
| Slug | Full Path |
|------|-----------|
| antidozhd | `categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/` |
| keramika-dlya-diskov | `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/` |
| kislotnyy | `categories/moyka-i-eksterer/avtoshampuni/kislotnyy/` |
| polirol-dlya-stekla | `categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/` |

### Batch 2
| Slug | Full Path |
|------|-----------|
| kvik-deteylery | `categories/zashchitnye-pokrytiya/kvik-deteylery/` |
| silanty | `categories/zashchitnye-pokrytiya/silanty/` |
| zhidkiy-vosk | `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/` |
| tverdyy-vosk | `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/` |

### Batch 3
| Slug | Full Path |
|------|-----------|
| vedra-i-emkosti | `categories/aksessuary/vedra-i-emkosti/` |
| nabory-dlya-moyki | `categories/aksessuary/nabory/nabory-dlya-moyki/` |
| nabory-dlya-salona | `categories/aksessuary/nabory/nabory-dlya-salona/` |
| podarochnyy | `categories/aksessuary/nabory/podarochnyy/` |

### Batch 4
| Slug | Full Path |
|------|-----------|
| kisti-dlya-deteylinga | `categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/` |
| shchetka-dlya-moyki-avto | `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/` |
| opt-i-b2b | `categories/opt-i-b2b/` |
| zashchitnye-pokrytiya | `categories/zashchitnye-pokrytiya/` (hub category — already has RESEARCH_PROMPT.md, skip if exists) |

---

## Data Dependencies

**Input files per category:**
- `{category_path}/data/{slug}_clean.json` — keywords, entities, micro_intents
- `data/category_ids.json` — slug → section ID mapping
- `data/generated/PRODUCTS_LIST.md` — products by section ID

**Output files per category:**
- `{category_path}/research/RESEARCH_PROMPT.md` — prompt for Perplexity
- `{category_path}/research/RESEARCH_DATA.md` — skeleton for results

---

## Task 1: Run Batch 1 (4 categories)

**Step 1: Launch 4 parallel agents**

```
Use Task tool with 4 parallel calls:

Agent 1 - antidozhd:
- subagent_type: general-purpose
- prompt: "Generate RESEARCH_PROMPT.md for category antidozhd.

  Path: categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/

  Steps:
  1. Read data/antidozhd_clean.json
  2. Read data/category_ids.json to get section ID (if available)
  3. Read data/generated/PRODUCTS_LIST.md and find section by ID
  4. Extract product insights (forms, volumes, base, effects)
  5. Generate research/RESEARCH_PROMPT.md following .claude/agents/seo-research.md format
  6. Create research/RESEARCH_DATA.md skeleton

  Output: Write both files and confirm."

Agent 2 - keramika-dlya-diskov:
- subagent_type: general-purpose
- prompt: "Generate RESEARCH_PROMPT.md for category keramika-dlya-diskov.

  Path: categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/

  [same steps as above]"

Agent 3 - kislotnyy:
- subagent_type: general-purpose
- prompt: "Generate RESEARCH_PROMPT.md for category kislotnyy.

  Path: categories/moyka-i-eksterer/avtoshampuni/kislotnyy/

  [same steps as above]"

Agent 4 - polirol-dlya-stekla:
- subagent_type: general-purpose
- prompt: "Generate RESEARCH_PROMPT.md for category polirol-dlya-stekla.

  Path: categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/

  [same steps as above]"
```

**Step 2: Verify outputs**

Check that all 4 files exist:
```
categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/research/RESEARCH_PROMPT.md
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/research/RESEARCH_PROMPT.md
categories/moyka-i-eksterer/avtoshampuni/kislotnyy/research/RESEARCH_PROMPT.md
categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/research/RESEARCH_PROMPT.md
```

**Step 3: User action**

User copies each RESEARCH_PROMPT.md to Perplexity Deep Research and saves results to RESEARCH_DATA.md.

---

## Task 2: Run Batch 2 (4 categories)

**Step 1: Launch 4 parallel agents**

Same pattern for:
- kvik-deteylery (`categories/zashchitnye-pokrytiya/kvik-deteylery/`)
- silanty (`categories/zashchitnye-pokrytiya/silanty/`)
- zhidkiy-vosk (`categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/`)
- tverdyy-vosk (`categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/`)

**Step 2: Verify outputs**

**Step 3: User action**

---

## Task 3: Run Batch 3 (4 categories)

**Step 1: Launch 4 parallel agents**

Same pattern for:
- vedra-i-emkosti (`categories/aksessuary/vedra-i-emkosti/`)
- nabory-dlya-moyki (`categories/aksessuary/nabory/nabory-dlya-moyki/`)
- nabory-dlya-salona (`categories/aksessuary/nabory/nabory-dlya-salona/`)
- podarochnyy (`categories/aksessuary/nabory/podarochnyy/`)

**Step 2: Verify outputs**

**Step 3: User action**

---

## Task 4: Run Batch 4 (3-4 categories)

**Step 1: Check if zashchitnye-pokrytiya already has RESEARCH_PROMPT.md**

If exists and has content, skip. Otherwise include.

**Step 2: Launch parallel agents**

Same pattern for:
- kisti-dlya-deteylinga (`categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/`)
- shchetka-dlya-moyki-avto (`categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/`)
- opt-i-b2b (`categories/opt-i-b2b/`)
- zashchitnye-pokrytiya (if needed)

**Step 3: Verify outputs**

**Step 4: User action**

---

## Agent Prompt Template

```markdown
Generate RESEARCH_PROMPT.md for category {SLUG}.

**Category path:** {FULL_PATH}

**Workflow:**

1. **Read semantic data:**
   - Read `{FULL_PATH}/data/{SLUG}_clean.json`
   - Extract: keywords, synonyms, entities, micro_intents, parent_id

2. **Find section ID:**
   - Read `data/category_ids.json`
   - Look up section ID for this slug

3. **Extract products (if section ID found):**
   - Read `data/generated/PRODUCTS_LIST.md`
   - Find section `## ... (ID: {SECTION_ID})`
   - Extract product names and descriptions

4. **Extract Product Insights from products:**
   - Forms: гель, спрей, аэрозоль, паста, жидкость
   - Volumes: 100мл, 250мл, 500мл, 1л, 5л
   - Base: водная, силиконовая, растворитель
   - Effects: матовый, глянцевый, сатиновый
   - pH/type: кислотный, щелочной, нейтральный

5. **Generate RESEARCH_PROMPT.md:**

   Follow this structure:

   ```
   # {Category Name} ({slug}) — SEO Research

   ## ТЗ для Perplexity Deep Research

   **Задача:** Buyer guide по {category name}.

   ---

   ## Контекст

   | Параметр | Значение |
   | -------- | -------- |
   | Название | {name} |
   | Slug | {slug} |
   | Parent | {parent_id} |

   ---

   ## Семантическое ядро

   | Ключ | Объём |
   | ---- | ----- |
   {keywords table}

   ### Entities
   {entities list}

   ---

   ## Product Insights

   | Характеристика | Значения в ассортименте |
   | -------------- | ----------------------- |
   | Формы выпуска | {forms} |
   | Объёмы | {volumes} |
   | База | {base types} |
   | Эффект/финиш | {effects} |

   ---

   ## Промпт для исследования

   ### Блок 1: Что это и зачем
   1. Что такое {category}?
   2. Зачем нужен {category}?
   3. Какие проблемы решает?

   ### Блок 2: Виды и типы (классификация)

   НЕ смешивать оси:
   - Ось 1 — Носитель: водная / растворитель
   - Ось 2 — Активный компонент: {specific to category}
   - Ось 3 — Финиш: {if applicable}

   ### Блок 3: Как выбрать
   1. По типу поверхности
   2. По желаемому эффекту
   3. По бюджету

   ### Блок 4: Применение
   1. Подготовка поверхности
   2. Процесс нанесения
   3. Время выдержки
   4. Финишная обработка

   ### Блок 5: Типичные ошибки
   1. {error 1}
   2. {error 2}

   ### Блок 6: Безопасность
   1. Защита кожи
   2. Вентиляция
   3. Хранение

   ### Блок 6а: Спорные утверждения
   Проверить мифы:
   - "{myth 1}"
   - "{myth 2}"

   ### Блок 7: FAQ (из micro_intents)
   {micro_intents as questions}

   ### Блок 8: Troubleshooting
   1. Если не работает...
   2. Если появились разводы...

   ### Блок 9: Совместимость
   1. С какими покрытиями совместим
   2. С чем нельзя использовать

   ### Блок 10: Цифры и метрики
   1. Расход на 1 авто
   2. Время работы
   3. Стойкость результата

   ---

   ## Шаблон вывода

   ```markdown
   # Research Data: {Category Name}

   ## Sources
   | # | URL | Тип | Что подтверждает |

   **Дата:** YYYY-MM-DD
   ```
   ```

6. **Create RESEARCH_DATA.md skeleton:**

   ```markdown
   # Research Data: {Category Name}

   **Slug:** {slug}
   **Дата исследования:** ___

   ---

   ## Sources

   | # | URL | Тип | Что подтверждает |
   |---|-----|-----|------------------|
   | 1 | | | |

   ---

   ## Блок 1: Что это и зачем

   [TODO: заполнить из Perplexity]

   ## Блок 2: Виды и типы

   [TODO: заполнить из Perplexity]

   ...
   ```

7. **Write files:**
   - Write `{FULL_PATH}/research/RESEARCH_PROMPT.md`
   - Write `{FULL_PATH}/research/RESEARCH_DATA.md`

8. **Confirm completion**
```

---

## Verification Checklist

After all batches:

- [ ] 16 RESEARCH_PROMPT.md files created
- [ ] 16 RESEARCH_DATA.md skeletons created
- [ ] Each RESEARCH_PROMPT.md has:
  - [ ] Semantic core table
  - [ ] Product insights table
  - [ ] 10+ research blocks
- [ ] Files are in correct paths

---

## Execution Command

To start Batch 1, say: **"запускай batch 1"**

This will launch 4 parallel agents for:
- antidozhd
- keramika-dlya-diskov
- kislotnyy
- polirol-dlya-stekla
