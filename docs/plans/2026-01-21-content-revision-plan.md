# Content Revision v3.0: 50 Categories

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ревизия контента 50 категорий Ultimate.net.ua с проверкой распределения ключей и соответствия research данным.

**Architecture:**

1. Формальная валидация (4 скрипта: meta, content, density, water/nausea)
2. Качественная оценка buyer guide (6 критериев)
3. Проверка распределения ключей (ручная, с учётом склонений)
4. Сверка фактов контента с RESEARCH_DATA.md (источник истины)
5. Fix → re-validate → commit

**Tech Stack:** Python validators (validate_meta.py, validate_content.py, check_keyword_density.py, check_water_natasha.py), content-generator v3.4 skill references.

**Key Changes v3.0:**

- Убраны entities (сгенерированные, не несут пользы)
- Добавлена проверка Keywords coverage (ручная)
- Добавлена сверка Facts vs Research (RESEARCH_DATA.md — источник истины)
- Все статусы сброшены — проверяем с нуля

**START:** Категория #1 moyka-i-eksterer → последовательно до #50

---

## Prerequisites

**Step 1: Verify validation scripts work**

```bash
python3 scripts/validate_meta.py --help
python3 scripts/validate_content.py --help
python3 scripts/check_keyword_density.py --help 2>/dev/null || echo "OK"
python3 scripts/check_water_natasha.py --help 2>/dev/null || echo "OK"
```

**Step 2: Reference files location**

```
.claude/skills/content-generator/
├── skill.md                    # Main skill v3.4
└── references/
    ├── buyer-guide.md          # Паттерны buyer guide
    ├── templates.md            # Шаблоны по типам категорий
    ├── validation.md           # Checklist валидации
    ├── hub-pages.md            # Для Hub (parent_id=null)
    ├── lsi-synonyms.md         # Синонимы для разбавления
    └── research-mapping.md     # Research → Content
```

---

## Data Structure

Each category at `categories/{path}/` contains:

```
{slug}/
├── content/{slug}_ru.md        # Content to review
├── data/{slug}_clean.json      # name, parent_id, keywords
├── meta/{slug}_meta.json       # h1, keywords_in_content
└── research/RESEARCH_DATA.md   # Facts source (ИСТОЧНИК ИСТИНЫ!)
```

**Key fields:**

- `_clean.json` → `name` (for H1), `parent_id` (null=Hub, else=Product)
- `_meta.json` → `h1`, `keywords_in_content.primary/secondary/supporting`
- `RESEARCH_DATA.md` → факты, лайфхаки, меры предосторожности

---

## Category Review Template

For each category `{slug}` at path `{path}`:

### Step 1: Read data files (parallel)

```bash
# Read 4 files in parallel
cat categories/{path}/data/{slug}_clean.json
cat categories/{path}/meta/{slug}_meta.json
cat categories/{path}/research/RESEARCH_DATA.md
cat categories/{path}/content/{slug}_ru.md
```

**Extract:**

- `name` → H1 должен = name (множественное число!)
- `parent_id` → null=Hub Page, else=Product Page
- `keywords_in_content` → для проверки покрытия в контенте
- `RESEARCH_DATA.md` → ключевые факты (источник истины!)

### Step 2: Run 4 validators (parallel)

```bash
# 1. Meta validation
python3 scripts/validate_meta.py categories/{path}/meta/{slug}_meta.json

# 2. Content SEO validation
python3 scripts/validate_content.py categories/{path}/content/{slug}_ru.md "{primary}" --mode seo

# 3. Keyword density
python3 scripts/check_keyword_density.py categories/{path}/content/{slug}_ru.md

# 4. Water and nausea
python3 scripts/check_water_natasha.py categories/{path}/content/{slug}_ru.md
```

### Step 3: Keywords Coverage (ручная проверка)

**Метод:**

1. Выписать ключи из `_meta.json` → `keywords_in_content`
2. Для каждого ключа выделить основу (стем): "средство от битума" → "средств" + "битум"
3. Искать основу в контенте (любое склонение ОК)
4. Подсчитать: найдено/всего для каждой группы

**Критерии:**

- ✅ PASS: все primary, ≥80% secondary/supporting
- ⚠️ WARNING: 1-2 primary отсутствуют или <80% остальных
- ❌ BLOCKER: >2 primary отсутствуют

**Формат:**

```
Keywords: primary 3/3 ✅, secondary 2/3 ⚠️, supporting 4/5 ✅
```

### Step 4: Facts vs Research (ручная проверка)

**Метод:**

1. Прочитать RESEARCH_DATA.md, выделить 5-7 ключевых фактов
2. Для каждого факта проверить в контенте:
    - ✅ Присутствует (может быть перефразирован)
    - ⚠️ Отсутствует (важный факт пропущен)
    - ❌ Противоречит (контент говорит обратное)
3. Проверить контент на факты, которых НЕТ в research (выдуманные?)

**Ключевые факты для проверки:**

- Классификация (типы продукта)
- Расход / дозировка
- Совместимость / ограничения
- Меры предосторожности (Safety)
- Лайфхаки (если есть в контенте — должны быть из research)

**Критерии:**

- ✅ PASS: Нет противоречий, ключевые факты использованы
- ⚠️ WARNING: 1-2 важных факта пропущены
- ❌ BLOCKER: Противоречия или выдуманные факты

### Step 5: Qualitative Buyer Guide Review (6 критериев)

**Ручная проверка — скрипты это НЕ ловят!**

| #   | Критерий                     | Как проверить                           | Severity |
| --- | ---------------------------- | --------------------------------------- | -------- |
| 1   | **Intro ≠ определение**      | Не начинается с "X — это Y, которое..." | BLOCKER  |
| 2   | **Обращения к читателю**     | Есть "вам", "если вы", "вам подойдёт"   | WARNING  |
| 3   | **Паттерны "Если X → Y"**    | Подсчитать количество (≥3)              | WARNING  |
| 4   | **Таблицы не дублируют**     | Сравнить контент таблиц                 | WARNING  |
| 5   | **FAQ не дублирует таблицы** | Вопрос уже есть в таблице?              | BLOCKER  |
| 6   | **Секции buyer-oriented**    | "К покупке или к использованию?"        | BLOCKER  |

### Step 6: Fill verdict table

| Критерий     | Результат    | Примечание                                 |
| ------------ | ------------ | ------------------------------------------ |
| Meta         | ✅/❌        |                                            |
| Density      | ✅/⚠️/❌     | stem max X%                                |
| Тошнота      | ✅/⚠️/❌     | classic X                                  |
| Вода         | ✅/⚠️        | X%                                         |
| Academic     | ✅/⚠️        | X%                                         |
| H1=name      | ✅/❌        |                                            |
| Intro        | ✅/❌        | buyer guide/определение                    |
| Обращения    | ✅/⚠️        | есть/нет                                   |
| Паттерны     | ✅/⚠️        | X шт                                       |
| Таблицы      | ✅/⚠️        | дубль/уникальные                           |
| FAQ          | ✅/❌        | дубль/уникальные                           |
| **Keywords** | ✅/⚠️/❌     | primary X/X, secondary X/X, supporting X/X |
| **Facts**    | ✅/⚠️/❌     | vs RESEARCH_DATA.md                        |
| **VERDICT**  | **✅/⚠️/❌** |                                            |

### Step 7: Fix if needed

**См. Quality Criteria и Typical Fixes Reference ниже**

### Step 8: Re-validate after fix

Run same 4 scripts + re-check qualitative criteria + keywords + facts.

### Step 9: Update progress

Mark status in batch table: ✅ PASS, ⚠️ WARNING (note), ❌ FIXED

---

## Quality Criteria v3.0

### BLOCKER (must fix before proceeding)

| Issue                           | Detection                                   | Fix                                     |
| ------------------------------- | ------------------------------------------- | --------------------------------------- |
| H1 ≠ name                       | H1 должен = name (мн.ч.)                    | Replace H1 in content + \_meta.json     |
| How-to sections                 | H2/H3: "Как наносить", "Техника применения" | Delete or convert to 1-2 sentences      |
| Stem >3.0%                      | check_keyword_density.py                    | Replace with synonyms (lsi-synonyms.md) |
| Nausea >4.0                     | check_water_natasha.py                      | Add variety, use synonyms               |
| Meta FAIL                       | validate_meta.py                            | Fix meta tags                           |
| Intro = определение             | "X — это Y, которое..."                     | Rewrite: польза + сценарий выбора       |
| 4+ таблиц                       | Count tables                                | Merge to 2-3                            |
| FAQ дублирует таблицу           | Same question in table                      | Replace with unique question            |
| **Противоречие с Research**     | Факт в контенте ≠ факт в RESEARCH_DATA      | Fix to match research                   |
| **Выдуманный факт**             | Утверждение не из research                  | Remove or verify externally             |
| **>2 primary keywords missing** | Keywords coverage check                     | Add missing keywords                    |

### WARNING (should fix)

| Issue                            | Detection                   | Fix                              |
| -------------------------------- | --------------------------- | -------------------------------- |
| No H2 with secondary keyword     | Manual check vs \_meta.json | Rewrite 1 H2                     |
| Water >75%                       | check_water_natasha.py      | Remove filler words              |
| Academic <6%                     | check_water_natasha.py      | Add reader engagement, scenarios |
| <3 паттернов "Если X → Y"        | Count patterns              | Add choice scenarios             |
| Нет обращений к читателю         | Search "вам", "если вы"     | Add reader addressing            |
| Таблицы дублируют друг друга     | Compare content             | Merge or differentiate           |
| **1-2 primary keywords missing** | Keywords coverage check     | Add missing keywords             |
| **<80% secondary/supporting**    | Keywords coverage check     | Add missing keywords             |
| **Важный факт пропущен**         | Facts vs Research check     | Add fact from research           |

### INFO (optional, not blocking)

| Issue                | Detection              | Note                           |
| -------------------- | ---------------------- | ------------------------------ |
| Academic nausea 6-7% | check_water_natasha.py | Slightly dry, OK for Hub Pages |
| Water 60-75%         | check_water_natasha.py | Slightly high, usually OK      |

---

## Anti-patterns: Что НЕ должно быть в тексте

### BLOCKER: Дублирующие секции

| Паттерн                                                                | Проблема                               | Решение                                  |
| ---------------------------------------------------------------------- | -------------------------------------- | ---------------------------------------- |
| **Таблица "На что смотреть на этикетке" + Таблица "Как выбрать"**      | Обе про одно: типы, pH, безопасность   | Оставить ОДНУ таблицу, объединив колонки |
| **Секция "Особенности применения" с описанием каждого типа**           | Дублирует таблицу типов + how-to стиль | Удалить или сократить до 1 фразы         |
| **"Формы выпуска" как отдельный H2 + "Как выбрать" с теми же формами** | Двойной контент                        | Объединить в одну таблицу                |

### WARNING: Избыточные секции

| Паттерн                                         | Признак                                                             | Решение                           |
| ----------------------------------------------- | ------------------------------------------------------------------- | --------------------------------- |
| **>3 таблиц в тексте**                          | Визуально перегружено                                               | Объединить до 2-3                 |
| **Секция расшифровывает то, что уже в таблице** | "Щелочные средства — хит трасс..." после таблицы с типом "Щелочной" | Удалить текст, таблица достаточна |
| **FAQ повторяет вопрос из H2**                  | "Как выбрать?" в FAQ при наличии H2 "Как выбрать"                   | Заменить на уникальный вопрос     |

### Пример: antimoshka (ИСПРАВЛЕНО)

**❌ БЫЛО (избыточно):**

```markdown
## Как выбрать антимошку

| Тип | Скорость | Безопасность |
| Щелочной | Быстрая | Риск для хрома |
| Цитрусовый | Средняя | Безопасен |

### На что смотреть на этикетке ← ДУБЛЬ!

| Маркер | Расшифровка |
| pH высокий | Щелочной | ← то же что выше
| Цитрусовый | Безопасен | ← то же что выше

## Особенности применения ← HOW-TO!

**Щелочные средства** — хит трасс... ← дубль таблицы типов
**Цитрусовые очистители** — безопасная... ← дубль
```

**✅ СТАЛО (чисто):**

```markdown
## Как выбрать антимошку

| Тип | Скорость | Безопасность | Для кого |
| Щелочной | Быстрая | Риск для хрома | Экспресс-мойка |
| Цитрусовый | Средняя | Безопасен | PPF, керамика, хром |

**Важно:** антимошку наносят ДО основной мойки. Не давать высыхать.
```

### Правило проверки

При ревизии задать себе вопрос:

> "Если убрать эту секцию — потеряю ли я уникальную информацию?"

- **Да** → оставить
- **Нет** → удалить (дублирование)

---

## Typical Fixes Reference

### Fix 1: Intro энциклопедия → Buyer Guide

```markdown
❌ БЫЛО (энциклопедия):
"Очиститель двигателя удаляет масляные загрязнения и техническую
грязь из подкапотного пространства, при этом безопасен для
пластиковых элементов и электропроводки при правильном выборе pH."

✅ СТАЛО (buyer guide):
"Выбор очистителя двигателя зависит от состояния моторного отсека.
Если у вас лёгкая пыль — подойдёт водная основа с мягкой щёлочью,
для застарелого масла — активный щелочной концентрат, для битума
и нагара — сольвентный состав."
```

**Признаки энциклопедии:**

- "X — это Y, которое..."
- "Основные функции: ..."
- "Широко применяется для..."
- Нет обращения к читателю

**Признаки buyer guide:**

- Сразу польза + выбор
- "Если вам нужно...", "вам подойдёт"
- Сценарии "Если X → Y"

### Fix 2: Дублирование таблиц → Объединить

```markdown
❌ БЫЛО (2 таблицы с одинаковым смыслом):

## Как выбрать

| Тип | Особенности |
| Щелочной | Для масла |
| Нейтральный | Для пыли |

## На что смотреть

| Маркер | Значение |
| Alkaline | Щелочной |
| pH-neutral | Нейтральный |

✅ СТАЛО (1 таблица):

## Как выбрать очиститель

| Задача | Что искать на этикетке | Почему |
| Застарелое масло | Alkaline / Щелочной | Расщепляет жир |
| Лёгкая пыль | pH-neutral | Безопасен для алюминия |
```

### Fix 3: FAQ дублирует → Уникальные вопросы

```markdown
❌ БЫЛО (дубль таблицы):

### Чем отличается водная основа от сольвентной?

{то же что в таблице}

✅ СТАЛО (уникальный вопрос):

### Можно ли использовать на других поверхностях?

Нет. Химия для мотора содержит активные щёлочи, которые могут
смыть воск с кузова. Используйте только в подкапотном пространстве.
```

### Fix 4: Добавить Keywords (пропущенные ключи)

```markdown
❌ БЫЛО (ключ "удалитель битума" отсутствует):
"Антибитум растворяет дорожный битум..."

✅ СТАЛО (ключ добавлен органично):
"Антибитум — удалитель битума, который растворяет дорожные загрязнения..."
```

**Правило:** Добавлять ключи органично, не keyword stuffing. Можно в любом склонении.

### Fix 5: Противоречие с Research → Исправить факт

```markdown
❌ БЫЛО (контент):
"Безопасен для любого пластика"

RESEARCH_DATA.md:
"Избегайте попадания на текстурированный неокрашенный пластик"

✅ СТАЛО:
"Безопасен для окрашенного пластика. На текстурированных
неокрашенных деталях сначала проверьте на незаметном участке."
```

### Synonyms for spam reduction

| Слово       | Синонимы                   |
| ----------- | -------------------------- |
| средство    | состав, продукт, препарат  |
| очиститель  | состав, продукт, химия     |
| поверхность | покрытие, основа, материал |
| защита      | барьер, слой, покрытие     |
| автомобиль  | авто, машина, транспорт    |

---

## Task 1: Batch 1 — Мойка и экстерьер (18 categories)

**Scope:** 18 categories in `categories/moyka-i-eksterer/`

| #   | Slug                         | Path                                                              | Type    | Status | Note |
| --- | ---------------------------- | ----------------------------------------------------------------- | ------- | ------ | ---- |
| 1   | moyka-i-eksterer             | moyka-i-eksterer                                                  | Hub     | ⬜     |      |
| 2   | avtoshampuni                 | moyka-i-eksterer/avtoshampuni                                     | Hub     | ⬜     |      |
| 3   | aktivnaya-pena               | moyka-i-eksterer/avtoshampuni/aktivnaya-pena                      | Product | ⬜     |      |
| 4   | shampuni-dlya-ruchnoy-moyki  | moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki         | Product | ⬜     |      |
| 5   | ochistiteli-dvigatelya       | moyka-i-eksterer/ochistiteli-dvigatelya                           | Product | ⬜     |      |
| 6   | glina-i-avtoskraby           | moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby            | Product | ⬜     |      |
| 7   | antibitum                    | moyka-i-eksterer/ochistiteli-kuzova/antibitum                     | Product | ⬜     |      |
| 8   | antimoshka                   | moyka-i-eksterer/ochistiteli-kuzova/antimoshka                    | Product | ⬜     |      |
| 9   | obezzhirivateli              | moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli               | Product | ⬜     |      |
| 10  | ukhod-za-naruzhnym-plastikom | moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom  | Product | ⬜     |      |
| 11  | cherniteli-shin              | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin      | Product | ⬜     |      |
| 12  | ochistiteli-diskov           | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov   | Product | ⬜     |      |
| 13  | ochistiteli-shin             | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin     | Product | ⬜     |      |
| 14  | keramika-dlya-diskov         | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov | Product | ⬜     |      |
| 15  | ochistiteli-stekol           | moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol          | Product | ⬜     |      |
| 16  | antidozhd                    | moyka-i-eksterer/sredstva-dlya-stekol/antidozhd                   | Product | ⬜     |      |
| 17  | omyvatel                     | moyka-i-eksterer/sredstva-dlya-stekol/omyvatel                    | Product | ⬜     |      |
| 18  | polirol-dlya-stekla          | moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla         | Product | ⬜     |      |

**After batch:**

```bash
git add categories/moyka-i-eksterer/
git commit -m "review(content): batch 1 moyka-i-eksterer - validated 18 categories v3.0"
```

---

## Task 2: Batch 2 — Аксессуары (10 categories)

**Scope:** 10 categories in `categories/aksessuary/`

| #   | Slug                               | Path                                                 | Type    | Status |
| --- | ---------------------------------- | ---------------------------------------------------- | ------- | ------ |
| 19  | aksessuary                         | aksessuary                                           | Hub     | ⬜     |
| 20  | mikrofibra-i-tryapki               | aksessuary/mikrofibra-i-tryapki                      | Product | ⬜     |
| 21  | gubki-i-varezhki                   | aksessuary/gubki-i-varezhki                          | Product | ⬜     |
| 22  | raspyliteli-i-penniki              | aksessuary/raspyliteli-i-penniki                     | Product | ⬜     |
| 23  | aksessuary-dlya-naneseniya-sredstv | aksessuary/aksessuary-dlya-naneseniya-sredstv        | Product | ⬜     |
| 24  | nabory                             | aksessuary/nabory                                    | Product | ⬜     |
| 25  | vedra-i-emkosti                    | aksessuary/vedra-i-emkosti                           | Product | ⬜     |
| 26  | shchetka-dlya-moyki-avto           | aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto | Product | ⬜     |
| 27  | kisti-dlya-deteylinga              | aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga    | Product | ⬜     |
| 28  | malyarniy-skotch                   | aksessuary/malyarniy-skotch                          | Product | ⬜     |

**After batch:**

```bash
git add categories/aksessuary/
git commit -m "review(content): batch 2 aksessuary - validated 10 categories v3.0"
```

---

## Task 3: Batch 3 — Уход за интерьером (8 categories)

| #   | Slug                             | Path                                                     | Type    | Status |
| --- | -------------------------------- | -------------------------------------------------------- | ------- | ------ |
| 29  | ukhod-za-intererom               | ukhod-za-intererom                                       | Hub     | ⬜     |
| 30  | sredstva-dlya-khimchistki-salona | ukhod-za-intererom/sredstva-dlya-khimchistki-salona      | Product | ⬜     |
| 31  | sredstva-dlya-kozhi              | ukhod-za-intererom/sredstva-dlya-kozhi                   | Hub     | ⬜     |
| 32  | ochistiteli-kozhi                | ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi | Product | ⬜     |
| 33  | ukhod-za-kozhey                  | ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey   | Product | ⬜     |
| 34  | poliroli-dlya-plastika           | ukhod-za-intererom/poliroli-dlya-plastika                | Product | ⬜     |
| 35  | pyatnovyvoditeli                 | ukhod-za-intererom/pyatnovyvoditeli                      | Product | ⬜     |
| 36  | neytralizatory-zapakha           | ukhod-za-intererom/neytralizatory-zapakha                | Product | ⬜     |

**After batch:**

```bash
git add categories/ukhod-za-intererom/
git commit -m "review(content): batch 3 ukhod-za-intererom - validated 8 categories v3.0"
```

---

## Task 4: Batch 4 — Защитные покрытия (7 categories)

| #   | Slug                      | Path                                            | Type    | Status |
| --- | ------------------------- | ----------------------------------------------- | ------- | ------ |
| 37  | zashchitnye-pokrytiya     | zashchitnye-pokrytiya                           | Hub     | ⬜     |
| 38  | keramika-i-zhidkoe-steklo | zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo | Product | ⬜     |
| 39  | voski                     | zashchitnye-pokrytiya/voski                     | Hub     | ⬜     |
| 40  | tverdyy-vosk              | zashchitnye-pokrytiya/voski/tverdyy-vosk        | Product | ⬜     |
| 41  | zhidkiy-vosk              | zashchitnye-pokrytiya/voski/zhidkiy-vosk        | Product | ⬜     |
| 42  | silanty                   | zashchitnye-pokrytiya/silanty                   | Product | ⬜     |
| 43  | kvik-deteylery            | zashchitnye-pokrytiya/kvik-deteylery            | Product | ⬜     |

**After batch:**

```bash
git add categories/zashchitnye-pokrytiya/
git commit -m "review(content): batch 4 zashchitnye-pokrytiya - validated 7 categories v3.0"
```

---

## Task 5: Batch 5 — Полировка (4 categories)

| #   | Slug               | Path                                             | Type    | Status |
| --- | ------------------ | ------------------------------------------------ | ------- | ------ |
| 44  | polirovka          | polirovka                                        | Hub     | ⬜     |
| 45  | polirovalnye-pasty | polirovka/polirovalnye-pasty                     | Product | ⬜     |
| 46  | mekhovye           | polirovka/polirovalnye-krugi/mekhovye            | Product | ⬜     |
| 47  | akkumulyatornaya   | polirovka/polirovalnye-mashinki/akkumulyatornaya | Product | ⬜     |

**After batch:**

```bash
git add categories/polirovka/
git commit -m "review(content): batch 5 polirovka - validated 4 categories v3.0"
```

---

## Task 6: Batch 6 — Оборудование и Опт (3 categories)

| #   | Slug              | Path                           | Type    | Status |
| --- | ----------------- | ------------------------------ | ------- | ------ |
| 48  | oborudovanie      | oborudovanie                   | Hub     | ⬜     |
| 49  | apparaty-tornador | oborudovanie/apparaty-tornador | Product | ⬜     |
| 50  | opt-i-b2b         | opt-i-b2b                      | Special | ⬜     |

**After batch:**

```bash
git add categories/oborudovanie/ categories/opt-i-b2b/
git commit -m "review(content): batch 6 oborudovanie + opt - validated 3 categories v3.0"
```

---

## Execution Checklist

| Batch                 | Categories | Reviewed | Status     |
| --------------------- | ---------- | -------- | ---------- |
| 1. Мойка и экстерьер  | 18         | 0        | ⬜ pending |
| 2. Аксессуары         | 10         | 0        | ⬜ pending |
| 3. Уход за интерьером | 8          | 0        | ⬜ pending |
| 4. Защитные покрытия  | 7          | 0        | ⬜ pending |
| 5. Полировка          | 4          | 0        | ⬜ pending |
| 6. Оборудование и Опт | 3          | 0        | ⬜ pending |
| **TOTAL**             | **50**     | **0**    | **0%**     |

---

## Final Validation

After all 50 categories reviewed:

```bash
# Run full validation
python3 scripts/validate_meta.py --all
python3 scripts/validate_content.py --all --mode seo 2>/dev/null || echo "Run per-category"

# Final commit
git add .
git commit -m "review(content): complete revision of 50 categories v3.0"
```

**Next steps:**

- `/quality-gate {slug}` for each category
- `/deploy-to-opencart {slug}` when ready

---

**Plan Version:** 3.0 | **Created:** 2026-01-21 | **Updated:** 2026-01-21

**Changelog v3.0:**

- Убраны entities (сгенерированные, не несут пользы)
- Добавлена **Keywords Coverage** (ручная проверка с учётом склонений)
- Добавлена **Facts vs Research** (RESEARCH_DATA.md — источник истины)
- Добавлены BLOCKER: противоречие с research, выдуманные факты, >2 primary missing
- Добавлены WARNING: пропущенные факты, <80% keywords coverage
- Добавлен Fix 4: добавление пропущенных ключей
- Добавлен Fix 5: исправление противоречий с research
- **Все статусы сброшены** — проверяем все 50 категорий с нуля
