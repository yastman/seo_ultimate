# UK Content Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать полный pipeline для генерации украинского контента на основе существующих русских категорий.

**Architecture:** Адаптируем существующие RU скиллы и субагенты под UK через `/skill-creator` и `/subagent-creator`. UK контент создаётся путём адаптации RU контента + интеграции украинских ключей с собранной частотностью. Research используется из RU версии.

**Tech Stack:** Claude Code skills, subagents, Python scripts, TRANSLATION_RULES.md

---

## Фаза 0: Инфраструктура

### Task 0.1: Создать скилл uk-keywords-export

**Метод:** Использовать `/skill-creator`

**Step 1: Вызвать skill-creator**

```
/skill-creator

Создай скилл uk-keywords-export:
- Назначение: Экспорт всех ключевых слов из RU категорий, перевод на украинский, создание MD файла для сбора частотности
- Триггеры: /uk-keywords-export, экспортируй ключи для UK, підготуй ключі для частотності
- Workflow:
  1. Glob: categories/**/data/*_clean.json
  2. Extract: keywords, synonyms, variations
  3. Translate using .claude/skills/uk-content-init/TRANSLATION_RULES.md
  4. Deduplicate
  5. Write to data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
- Output: MD файл с украинскими ключами, каждый на новой строке
- Reference: ../uk-content-init/TRANSLATION_RULES.md
```

**Step 2: Проверить созданный скилл**

```bash
cat .claude/skills/uk-keywords-export/skill.md
```

**Step 3: Commit**

```bash
git add .claude/skills/uk-keywords-export/
git commit -m "feat(skills): add uk-keywords-export skill"
```

---

### Task 0.2: Создать скилл uk-keywords-import

**Метод:** Использовать `/skill-creator`

**Step 1: Вызвать skill-creator**

```
/skill-creator

Создай скилл uk-keywords-import:
- Назначение: Импорт UK ключей с частотностью из CSV файла, создание JSON для UK pipeline
- Триггеры: /uk-keywords-import, імпортуй ключі, завантаж частотність
- Input: CSV с колонками keyword,volume
- Workflow:
  1. Read input CSV
  2. Parse keyword + volume
  3. Match keywords to RU categories (by translation mapping)
  4. Group by category slug
  5. Write to uk/data/uk_keywords.json
- Output: JSON сгруппированный по категориям
```

**Step 2: Проверить созданный скилл**

```bash
cat .claude/skills/uk-keywords-import/skill.md
```

**Step 3: Commit**

```bash
git add .claude/skills/uk-keywords-import/
git commit -m "feat(skills): add uk-keywords-import skill"
```

---

### Task 0.3: Создать скилл uk-generate-meta

**Метод:** Использовать `/skill-creator` на основе существующего `generate-meta`

**Step 1: Прочитать RU скилл для референса**

```bash
cat .claude/skills/generate-meta/skill.md
```

**Step 2: Вызвать skill-creator**

```
/skill-creator

Создай скилл uk-generate-meta на основе generate-meta:
- Назначение: Генерация украинских мета-тегов (Title, Description, H1)
- Триггеры: /uk-generate-meta, генеруй UK мета, створи мета-теги українською
- UK Rules:
  - Title: 50-60 chars, "Купити" ОБОВ'ЯЗКОВО в начале
  - Description: 100-160 chars
  - H1: БЕЗ "Купити"
- Title Formula:
  - Если keyword ≤ 20 chars: "Купити {keyword} в Україні | Ultimate"
  - Иначе: "{keyword} — купити, ціни | Ultimate"
- Description Formula:
  - Producer: "{keyword} від виробника Ultimate. {types}. Опт і роздріб."
  - Shop: "{keyword} в інтернет-магазині Ultimate. {types}."
- H1 Formula: {primary_keyword} без "Купити"
- Input: uk/categories/{slug}/data/, categories/{slug}/meta/ (для types, volumes)
- Output: uk/categories/{slug}/meta/{slug}_meta.json
```

**Step 3: Commit**

```bash
git add .claude/skills/uk-generate-meta/
git commit -m "feat(skills): add uk-generate-meta skill"
```

---

### Task 0.4: Создать скилл uk-content-adapter

**Метод:** Использовать `/skill-creator` на основе существующего `content-generator`

**Step 1: Прочитать RU скилл для референса**

```bash
cat .claude/skills/content-generator/skill.md
```

**Step 2: Вызвать skill-creator**

```
/skill-creator

Создай скилл uk-content-adapter на основе content-generator:
- Назначение: Адаптация RU контента на украинский с интеграцией UK ключей
- Триггеры: /uk-content-adapter, адаптуй контент на UK, переклади категорію
- Принцип: НЕ полный рерайт! Адаптация:
  1. Перевод RU → UK по TRANSLATION_RULES.md
  2. Интеграция UK ключей
  3. Сохранение структуры
- Input:
  - categories/{slug}/content/{slug}_ru.md (RU контент)
  - categories/{slug}/research/RESEARCH_DATA.md (Research)
  - uk/categories/{slug}/data/{slug}_clean.json (UK ключи)
  - uk/categories/{slug}/meta/{slug}_meta.json (UK H1)
- Output: uk/categories/{slug}/content/{slug}_uk.md
- Keyword Integration:
  - H1: primary (из meta)
  - Intro: primary + 1 secondary
  - H2 (мин. 1): secondary
  - Таблицы: supporting
  - FAQ: secondary/supporting
- Reference: ../uk-content-init/TRANSLATION_RULES.md
- Создай также references/adaptation-rules.md с терминологией
```

**Step 3: Commit**

```bash
git add .claude/skills/uk-content-adapter/
git commit -m "feat(skills): add uk-content-adapter skill"
```

---

### Task 0.5: Создать субагент uk-keywords-export

**Метод:** Использовать `/subagent-creator`

**Step 1: Вызвать subagent-creator**

```
/subagent-creator

Создай субагент uk-keywords-export:
- Назначение: Экспорт RU ключей с переводом на UK для сбора частотности
- Триггеры: /uk-keywords-export, експортуй ключі
- Tools: Read, Grep, Glob, Bash, Write
- Model: sonnet
- Workflow:
  1. Glob: categories/**/data/*_clean.json
  2. Для каждого файла извлечь: keywords, synonyms, variations
  3. Перевести по словарю из .claude/skills/uk-content-init/TRANSLATION_RULES.md
  4. Убрать дубликаты
  5. Сортировать по алфавиту
  6. Write: data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
- Output: Каждый ключ на новой строке
- Validation: резина → гума (проверить!)
```

**Step 2: Commit**

```bash
git add .claude/agents/uk-keywords-export.md
git commit -m "feat(agents): add uk-keywords-export agent"
```

---

### Task 0.6: Создать субагент uk-keywords-import

**Метод:** Использовать `/subagent-creator`

**Step 1: Вызвать subagent-creator**

```
/subagent-creator

Создай субагент uk-keywords-import:
- Назначение: Импорт UK ключей с частотностью в JSON
- Триггеры: /uk-keywords-import, імпортуй частотність
- Tools: Read, Grep, Glob, Bash, Write
- Model: sonnet
- Input: CSV файл с keyword,volume
- Workflow:
  1. Read input file
  2. Parse keyword + volume
  3. Match keywords to categories (обратный перевод)
  4. Group by category slug
  5. Write: uk/data/uk_keywords.json
- Category Matching:
  - "активна піна" → "активная пена" → aktivnaya-pena
  - "чорнитель гуми" → "чернитель резины" → cherniteli-shin
```

**Step 2: Commit**

```bash
git add .claude/agents/uk-keywords-import.md
git commit -m "feat(agents): add uk-keywords-import agent"
```

---

### Task 0.7: Создать субагент uk-category-init

**Метод:** Использовать `/subagent-creator` на основе `category-init`

**Step 1: Прочитать RU агент для референса**

```bash
cat .claude/agents/category-init.md
```

**Step 2: Вызвать subagent-creator**

```
/subagent-creator

Создай субагент uk-category-init на основе category-init:
- Назначение: Инициализация UK категории
- Триггеры: /uk-category-init {slug}, створи UK категорію
- Tools: Read, Grep, Glob, Bash, Write
- Model: sonnet
- Prerequisites:
  - categories/{slug}/ существует (RU готова)
  - uk/data/uk_keywords.json содержит ключи
- Workflow:
  1. Verify RU category exists
  2. Create folder structure:
     uk/categories/{slug}/
     ├── data/{slug}_clean.json
     ├── meta/
     ├── content/
     └── research/CONTEXT.md
  3. Copy UK keywords from uk/data/uk_keywords.json
  4. Create CONTEXT.md с ссылкой на RU research
```

**Step 2: Commit**

```bash
git add .claude/agents/uk-category-init.md
git commit -m "feat(agents): add uk-category-init agent"
```

---

### Task 0.8: Создать субагент uk-generate-meta

**Метод:** Использовать `/subagent-creator` на основе `generate-meta`

**Step 1: Прочитать RU агент для референса**

```bash
cat .claude/agents/generate-meta.md
```

**Step 2: Вызвать subagent-creator**

```
/subagent-creator

Создай субагент uk-generate-meta на основе generate-meta:
- Назначение: Генерація UK мета-тегів
- Триггеры: /uk-generate-meta {slug}, генеруй UK мета
- Tools: Read, Grep, Glob, Bash, Write
- Model: sonnet
- Data Files:
  - uk/categories/{slug}/data/{slug}_clean.json (UK ключі)
  - categories/{slug}/meta/{slug}_meta.json (RU: types, volumes)
- UK Meta Rules:
  - Title: "Купити {keyword} в Україні | Ultimate" (50-60 chars)
  - Description: "{keyword} від виробника Ultimate. {types}. Опт і роздріб." (100-160 chars)
  - H1: {keyword} БЕЗ "Купити"
- Output: uk/categories/{slug}/meta/{slug}_meta.json
- Validation: python3 scripts/validate_meta.py
```

**Step 3: Commit**

```bash
git add .claude/agents/uk-generate-meta.md
git commit -m "feat(agents): add uk-generate-meta agent"
```

---

### Task 0.9: Создать субагент uk-content-adapter

**Метод:** Использовать `/subagent-creator` на основе `content-generator`

**Step 1: Прочитать RU агент для референса**

```bash
cat .claude/agents/content-generator.md
```

**Step 2: Вызвать subagent-creator**

```
/subagent-creator

Создай субагент uk-content-adapter на основе content-generator:
- Назначение: Адаптація RU контенту на UK з інтеграцією ключів
- Триггеры: /uk-content-adapter {slug}, адаптуй контент
- Tools: Read, Grep, Glob, Bash, Write, Edit
- Model: opus (нужен для качественного перевода)
- Принцип: НЕ полный рерайт! Адаптация + интеграция ключей
- Data Files:
  - categories/{slug}/content/{slug}_ru.md (RU контент)
  - categories/{slug}/research/RESEARCH_DATA.md (Research)
  - uk/categories/{slug}/data/{slug}_clean.json (UK ключі)
  - uk/categories/{slug}/meta/{slug}_meta.json (UK H1)
- Workflow:
  1. Read RU content
  2. Read UK H1 from meta
  3. Read UK keywords (primary, secondary, supporting)
  4. Translate applying TRANSLATION_RULES
  5. Replace H1 with UK H1
  6. Integrate UK keywords
  7. Write: uk/categories/{slug}/content/{slug}_uk.md
  8. Validate
- Translation Quick Reference:
  резина → гума, мойка → миття, стекло → скло
  чернитель → чорнитель, очиститель → очищувач
```

**Step 3: Commit**

```bash
git add .claude/agents/uk-content-adapter.md
git commit -m "feat(agents): add uk-content-adapter agent"
```

---

### Task 0.10: Создать субагент uk-content-reviewer

**Метод:** Использовать `/subagent-creator` на основе `content-reviewer`

**Step 1: Прочитать RU агент для референса**

```bash
cat .claude/agents/content-reviewer.md
```

**Step 2: Вызвать subagent-creator**

```
/subagent-creator

Создай субагент uk-content-reviewer на основе content-reviewer:
- Назначение: Ревізія UK контенту категорії
- Триггеры: uk-content-reviewer {slug}, перевір UK контент
- Tools: Read, Grep, Glob, Bash, Edit
- Model: opus
- Data Files:
  - uk/categories/{slug}/content/{slug}_uk.md (для ревізії)
  - uk/categories/{slug}/data/{slug}_clean.json (UK ключі)
  - uk/categories/{slug}/meta/{slug}_meta.json (UK мета)
  - categories/{slug}/research/RESEARCH_DATA.md (джерело істини)
- Workflow:
  1. Read files (parallel)
  2. Run validators:
     - validate_meta.py
     - validate_content.py --mode seo
     - check_keyword_density.py
  3. UK-specific checks:
     - Термінологія: резина→гума, мойка→миття, стекло→скло
     - H1 БЕЗ "Купити"
     - Title З "Купити"
     - UK keywords integrated
  4. Fill verdict table
  5. Fix if needed (Edit tool)
- UK Term Checklist:
  | Wrong | Correct |
  | резина | гума |
  | мойка | миття |
  | стекло | скло |
```

**Step 3: Commit**

```bash
git add .claude/agents/uk-content-reviewer.md
git commit -m "feat(agents): add uk-content-reviewer agent"
```

---

### Task 0.11: Обновить quality-gate для UK

**Метод:** Использовать `/skill-creator` для обновления

**Step 1: Прочитать текущий скилл**

```bash
cat .claude/skills/quality-gate/skill.md
```

**Step 2: Вызвать skill-creator для обновления**

```
/skill-creator

Обнови скилл quality-gate, добавь поддержку UK:

Добавить секцию "## UK Support":

При вызове с `--lang uk`:

1. Paths:
   - Data: `uk/categories/{slug}/data/`
   - Meta: `uk/categories/{slug}/meta/`
   - Content: `uk/categories/{slug}/content/{slug}_uk.md`

2. Additional checks:
   - UK terminology (резина→гума, мойка→миття, стекло→скло)
   - Title contains "Купити"
   - H1 does NOT contain "Купити"

3. Validation:
   python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
   python3 scripts/validate_content.py uk/categories/{slug}/content/{slug}_uk.md "{primary}" --mode seo
```

**Step 3: Commit**

```bash
git add .claude/skills/quality-gate/skill.md
git commit -m "feat(skills): add UK support to quality-gate"
```

---

### Task 0.12: Тест на aktivnaya-pena

**Step 1: Запустить полный UK pipeline на тестовой категории**

```bash
# 1. Вручную создать тестовые UK ключи для одной категории
# Read categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json
# Translate keywords manually → создать uk/data/uk_keywords.json с одной категорией

# 2. Init UK category
uk-category-init aktivnaya-pena

# 3. Generate meta
uk-generate-meta aktivnaya-pena

# 4. Adapt content
uk-content-adapter aktivnaya-pena

# 5. Review
uk-content-reviewer aktivnaya-pena

# 6. Quality gate
/quality-gate aktivnaya-pena --lang uk
```

**Step 2: Verify all files created**

```
uk/categories/aktivnaya-pena/
├── data/aktivnaya-pena_clean.json  ✓
├── meta/aktivnaya-pena_meta.json   ✓
├── content/aktivnaya-pena_uk.md    ✓
└── research/CONTEXT.md             ✓
```

**Step 3: Commit test results**

```bash
git add uk/categories/aktivnaya-pena/
git commit -m "test: verify UK pipeline on aktivnaya-pena"
```

---

## Фаза 1: Сбор UK ключей

### Task 1.1: Экспорт всех RU ключей

**Step 1: Запустить субагент uk-keywords-export**

```
uk-keywords-export
```

**Step 2: Verify output**

```bash
cat data/generated/UK_KEYWORDS_FOR_FREQUENCY.md | head -20
# Должны быть украинские ключи
```

**Step 3: Commit**

```bash
git add data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
git commit -m "data: export UK keywords for frequency collection"
```

---

### Task 1.2: Ручной сбор частотности

**Действие:** Пользователь загружает `UK_KEYWORDS_FOR_FREQUENCY.md` в сервис сбора частотности.

**Результат:** CSV файл с колонками `keyword,volume`

**Checkpoint:** Дождаться файл от пользователя перед продолжением.

---

### Task 1.3: Импорт UK ключей с частотностью

**Step 1: Запустить субагент uk-keywords-import**

```
uk-keywords-import {path-to-csv}
```

**Step 2: Verify output**

```bash
cat uk/data/uk_keywords.json | head -50
```

**Step 3: Commit**

```bash
git add uk/data/uk_keywords.json
git commit -m "data: import UK keywords with frequency"
```

---

## Фаза 2: Генерация UK контента (×50 категорий)

### Task 2.x: Batch processing template

Для каждой категории {slug}:

**Step 1: Init**
```
uk-category-init {slug}
```

**Step 2: Meta**
```
uk-generate-meta {slug}
```

**Step 3: Content**
```
uk-content-adapter {slug}
```

**Step 4: Review**
```
uk-content-reviewer {slug}
```

**Step 5: Quality gate**
```
/quality-gate {slug} --lang uk
```

**Step 6: Commit**
```bash
git add uk/categories/{slug}/
git commit -m "content(uk): add {slug} category"
```

---

## Список категорий для обработки

```
L1 Categories (7):
- aksessuary
- moyka-i-eksterer
- oborudovanie
- opt-i-b2b
- polirovka
- ukhod-za-intererom
- zashchitnye-pokrytiya

L2/L3 Categories (43):
- aktivnaya-pena
- antibitum
- antimoshka
- antidozhd
- apparaty-tornador
- aksessuary-dlya-naneseniya-sredstv
- akkumulyatornaya
- avtoshampuni
- cherniteli-shin
- glina-i-avtoskraby
- gubki-i-varezhki
- keramika-dlya-diskov
- keramika-i-zhidkoe-steklo
- kisti-dlya-deteylinga
- kvik-deteylery
- malyarniy-skotch
- mekhovye
- mikrofibra-i-tryapki
- nabory
- neytralizatory-zapakha
- obezzhirivateli
- ochistiteli-diskov
- ochistiteli-dvigatelya
- ochistiteli-kozhi
- ochistiteli-shin
- ochistiteli-stekol
- ochistiteli-kuzova
- omyvatel
- polirol-dlya-stekla
- poliroli-dlya-plastika
- polirovalnye-krugi
- polirovalnye-mashinki
- polirovalnye-pasty
- pyatnovyvoditeli
- raspyliteli-i-penniki
- shampuni-dlya-ruchnoy-moyki
- shchetka-dlya-moyki-avto
- shchetki-i-kisti
- silanty
- sredstva-dlya-diskov-i-shin
- sredstva-dlya-khimchistki-salona
- sredstva-dlya-kozhi
- sredstva-dlya-stekol
- tverdyy-vosk
- ukhod-za-kozhey
- ukhod-za-naruzhnym-plastikom
- vedra-i-emkosti
- voski
- zhidkiy-vosk
```

---

## Финальная валидация

После обработки всех 50 категорий:

```bash
# Проверить все UK файлы
python3 scripts/validate_meta.py --all --lang uk
python3 scripts/validate_content.py --all --lang uk

# Commit
git add uk/
git commit -m "content(uk): complete UK content for all 50 categories"
```
