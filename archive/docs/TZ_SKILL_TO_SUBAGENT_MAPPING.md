# ТЗ: Маппинг Skills → Sub-агенты

**Цель:** Актуализировать использование Sub-агентов чтобы они были зеркалом существующих Skills.

---

## Проблема

**Существующие Sub-агенты** (из системы) — это GENERIC SEO агенты.

Они **НЕ знают** про:

- SEO 2025 v7.3 Shop Mode
- Наши скрипты (quality_runner.py, check_water_natasha.py)
- Адвего-калибровку (Water 40-60%, Nausea ≤3.5)
- Task file структуру
- Anti-Fluff правила
- Synonym Rotation (max 2x слово в параграфе)
- Commercial markers (купить, цена, доставка)
- Tier система (A/B/C)

**Решение:** Передавать ПОЛНЫЙ контекст в prompt каждому агенту.

---

## Сравнительная таблица

| # | Skill | Функционал | Sub-агент | Требует контекст |
|---|-------|------------|-----------|------------------|
| 1 | `seo-init` | Создание папок + task file | `general-purpose` | Структура папок |
| 2 | `seo-data` | Keywords JSON (скрипт) | `general-purpose` | Скрипт + формат |
| 3 | `seo-urls` | URLs из SERP (скрипты) | `general-purpose` | 2 скрипта |
| 4 | `seo-competitors` | Анализ meta (скрипт) | `seo-content-planner` | Скрипт + формат |
| 5 | `seo-research` | Perplexity MCP | `search-specialist` | 4 секции + Tier |
| 6 | `seo-content` | Контент v7.3 | `seo-content-writer` | **ВСЯ спецификация v7.3** |
| 7 | `seo-translator` | RU→UK перевод | `general-purpose` | Термины + ±5% |
| 8 | `seo-validate` | 5 checks (скрипты) | `seo-content-auditor` | Скрипты + targets |
| 9 | `seo-meta` | Title/Description | `seo-meta-optimizer` | Формат + длины |
| 10 | `seo-package` | Deliverables | `general-purpose` | Структура + templates |

---

## Детальный маппинг с промптами

### 1. seo-init → general-purpose (haiku)

**Skill функционал:**

- Создать папки: categories/{slug}/, content/, meta/, deliverables/, .logs/, competitors/scraped/, research/, data/
- Создать task_{slug}.json с начальным состоянием

**Prompt шаблон:**

```markdown
## Задача: Init категории

Создай структуру для SEO-категории:
- Slug: {slug}
- Name: {name}
- Tier: {tier} (A/B/C)

### Папки (создать):
```

categories/{slug}/
├── .logs/
├── competitors/scraped/
├── research/
├── data/
├── content/
├── meta/
└── deliverables/

```

### Task file (создать): task_{slug}.json
```json
{
  "slug": "{slug}",
  "name": "{name}",
  "tier": "{tier}",
  "status": "initialized",
  "current_stage": "url_extraction",
  "created": "{ISO_NOW}",
  "updated": "{ISO_NOW}",
  "schema_version": "3.0.0",
  "workflow_version": "SEO_2025_SKILLS",
  "paths": {
    "base": "categories/{slug}/",
    "urls_raw": "categories/{slug}/urls_raw.txt",
    "urls": "categories/{slug}/urls.txt",
    "logs": "categories/{slug}/.logs/",
    "scraped": "categories/{slug}/competitors/scraped/",
    "data_json": "categories/{slug}/data/{slug}.json",
    "content_ru": "categories/{slug}/content/{slug}_ru.md",
    "content_uk": "categories/{slug}/content/{slug}_uk.md",
    "meta_json": "categories/{slug}/meta/{slug}_meta.json",
    "research": "categories/{slug}/research/perplexity_research.md",
    "deliverables": "categories/{slug}/deliverables/"
  },
  "stages": {
    "init": "completed",
    "url_extraction": "pending",
    "url_prep": "pending",
    "data_prep": "pending",
    "keywords": "pending",
    "research": "pending",
    "content_ru": "pending",
    "content_uk": "pending",
    "meta": "pending",
    "packaging": "pending"
  }
}
```

Верни JSON с созданными путями.

```

**GAP:** Нет. Полный функционал передаётся в prompt.

---

### 2. seo-data → general-purpose (haiku)

**Skill функционал:**
- Запустить `python3 scripts/parse_semantics_to_json.py {slug} {tier}`
- Проверить output JSON

**Prompt шаблон:**
```markdown
## Задача: Data Preparation

1. Активируй venv:
   ```bash
   source venv/bin/activate
   ```

2. Запусти скрипт:

   ```bash
   python3 scripts/parse_semantics_to_json.py {slug} {tier}
   ```

3. Проверь output:

   ```bash
   python3 -c "
   import json
   with open('categories/{slug}/data/{slug}.json') as f:
       data = json.load(f)
       print(f'Total keywords: {data[\"stats\"][\"total_keywords\"]}')
       print(f'PRIMARY: {data[\"stats\"][\"primary_count\"]}')
   "
   ```

Верни:

- Путь к созданному JSON
- Статистику keywords

```

**GAP:** Нет. Скрипт делает всю работу.

---

### 3. seo-urls → general-purpose (haiku)

**Skill функционал:**
- Stage -3: extract_competitor_urls_v2.py → urls_raw.txt
- Stage -2: url_preparation_filter_and_validate.py → urls.txt

**Prompt шаблон:**
```markdown
## Задача: URL Extraction

### Stage 1: Извлечение
```bash
source venv/bin/activate
python3 scripts/extract_competitor_urls_v2.py \
  --task task_{slug}.json \
  --out categories/{slug}/urls_raw.txt \
  --min 8 \
  --dedupe domains
```

### Stage 2: Валидация

```bash
python3 scripts/url_preparation_filter_and_validate.py \
  --task task_{slug}.json \
  --in categories/{slug}/urls_raw.txt \
  --out categories/{slug}/urls.txt \
  --https-only \
  --no-ua \
  --min 5
```

Правила:

- Минимум 8 URLs raw
- Минимум 5 validated
- HTTPS only
- Убрать /ua/ prefix
- Max 2 per domain

Верни:

- Количество raw URLs
- Количество validated URLs
- Путь к urls.txt

```

**GAP:** Нет. Скрипты делают работу.

---

### 4. seo-competitors → seo-content-planner (sonnet)

**Skill функционал:**
- Запустить `python3 scripts/filter_mega_competitors.py {slug}`
- Получить meta_patterns.json с H2 themes

**Prompt шаблон:**
```markdown
## Задача: Competitor Analysis

### Шаг 1: Проверить prerequisites
```bash
ls -la categories/{slug}/data/{slug}.json
ls -la data/mega/mega_competitors.csv
```

### Шаг 2: Запустить анализ

```bash
source venv/bin/activate
python3 scripts/filter_mega_competitors.py {slug}
```

### Шаг 3: Проверить output

```bash
cat categories/{slug}/competitors/meta_patterns.json
```

### Output формат

```json
{
  "competitors_count": N,
  "title_length_median": N,
  "description_length_median": N,
  "h2_themes": ["...", "..."],
  "title_ne_h1_rate": 0.X
}
```

Exit codes:

- 0 = OK (≥5 competitors, ≥3 H2 themes)
- 1 = WARNING
- 2 = FAIL

Верни meta_patterns.json содержимое.

```

**GAP:** Небольшой. Агент `seo-content-planner` ориентирован на планирование, а не анализ конкурентов. Но с правильным prompt справится.

---

### 5. seo-research → search-specialist (sonnet) ⭐

**Skill функционал:**
- Использовать Perplexity MCP tools
- Собрать 4 секции данных
- Записать perplexity_research.md

**Prompt шаблон:**
```markdown
## Задача: Perplexity Research

Категория: {category_name}
Tier: {tier}
Keywords: {keywords_list}

### MCP Tools для использования:
- `mcp__perplexity__perplexity_search` — top URLs
- `mcp__perplexity__perplexity_research` — deep facts
- `mcp__perplexity__perplexity_reason` — synthesis

### Собрать 4 секции:

#### 1. Technical Characteristics
- pH levels, температуры
- Dilution ratios
- КОНКРЕТНЫЕ цифры, не generic

#### 2. Safety & Limitations
- Warnings с параметрами
- Compatibility notes

#### 3. Selection Criteria
- Decision matrices
- Comparison factors

#### 4. FAQ
- Реальные вопросы с форумов
- Ответы с specs

### Tier Coverage:
| Секция | Tier A | Tier B | Tier C |
|--------|--------|--------|--------|
| Technical | 8+ | 6+ | 4+ |
| Safety | 6+ | 5+ | 3+ |
| Selection | 6+ | 5+ | 3+ |
| FAQ | 6+ | 5+ | 3+ |

### Output: categories/{slug}/research/perplexity_research.md

Формат:
```markdown
# Research: {Category}

## Technical Characteristics
- pH: 10-13
- Temperature: +15...+25°C
[Sources: url1, url2]

## Safety & Limitations
- Avoid hot surfaces (>40°C)
[Sources: ...]

## Selection Criteria
| Factor | Budget | Mid | Premium |
|--------|--------|-----|---------|
| pH | 9-10 | 10-11 | 12-13 |

## FAQ
**Q: Какое разведение для 120 бар?**
A: 1:60-1:80
```

Quality:

- Sources 2024-2025
- Concrete numbers
- URL citations

```

**GAP:** Средний. `search-specialist` знает как искать, но НЕ знает формат output и Tier coverage. Нужен полный prompt.

---

### 6. seo-content → seo-content-writer (sonnet) ⭐⭐⭐ КРИТИЧНЫЙ

**Skill функционал:**
- Полная спецификация v7.3 Shop Mode
- Synonym Rotation
- Commercial Markers
- Anti-Fluff
- Tier targets

**Prompt шаблон:**
```markdown
## Задача: SEO Content v7.3 Shop Mode

### Input Data
- Slug: {slug}
- Category: {category_name}
- Tier: {tier}
- Keywords: {keywords_json}
- Research: {research_data}

### Технические лимиты (Tier {tier})

| Параметр | Target |
|----------|--------|
| Символы (б/п) | {chars_min}-{chars_max} |
| Слова | {words_min}-{words_max} |
| H2 | {h2_min}-{h2_max} |
| FAQ | {faq_min}-{faq_max} |
| Density (Main Key) | {density_min}-{density_max}% |
| Water (Адвего) | 40-60% |
| Classic Nausea | ≤3.5 |

### Обязательная структура

#### Блок 1: H2 — Как выбрать [Категория]
- Критерии выбора (pH, объём, материал)
- Маркированный список

#### Блок 2: H2 — Виды / Ассортимент
- Подкатегории с внутренними ссылками

#### Блок 3: H2 — Таблица характеристик (Tier A/B only)
- Тип товара | Назначение | Особенности

#### Блок 4: H2 — FAQ (Частые вопросы)
- {faq_min}-{faq_max} вопросов

### Commercial Markers (ОБЯЗАТЕЛЬНО минимум {commercial_min})
- ✅ купить / купити
- ✅ цена / ціна
- ✅ интернет-магазин
- ✅ доставка
- ✅ заказать / замовити
- ✅ в наличии / оптом

### Synonym Rotation (КРИТИЧНО)
**Максимум 2 повтора одного слова в параграфе!**
```

❌ Пена очищает. Пена создаёт шапку. Пена безопасна.
✅ Пена очищает. Состав создаёт шапку. Средство безопасно.

```

### Anti-Fluff (ЗАПРЕЩЕНО)

❌ Вводные > 3 слов:
- "В современном мире..."
- "Ни для кого не секрет..."
- "На сегодняшний день..."

❌ AI-fluff:
- "В этой статье..."
- "Давайте рассмотрим..."
- "В заключение..."

❌ История/Энциклопедия:
- "Первые шампуни появились..."
- "История создания..."

### Tone & Style
- Expert & Direct
- No Fluff — каждое предложение добавляет ценность
- Inverted Pyramid — первый абзац = прямой ответ
- Коммерческий intent — продавать!

### Keyword Handling
- PRIMARY: EXACT MATCH в H1 и 1-м абзаце
- Дальше — естественные формы
- Supporting: Soft Match

### Output
Markdown файл. ТОЛЬКО контент, без мета-комментариев.
Сохранить в: categories/{slug}/content/{slug}_ru.md
```

**GAP:** КРИТИЧНЫЙ!

`seo-content-writer` — generic агент. Он НЕ знает:

- v7.3 Shop Mode
- Synonym Rotation правило (max 2x)
- Commercial Markers (конкретный список)
- Anti-Fluff (конкретные запрещённые фразы)
- Tier targets (конкретные цифры)
- Адвего-калибровку (Water/Nausea)

**Решение:** Передавать ПОЛНУЮ спецификацию в prompt (~2000 токенов).

---

### 7. seo-translator → general-purpose (sonnet)

**Skill функционал:**

- Перевод RU→UK
- Сохранение Markdown
- Терминология авто-детейлинга
- ±5% длины

**Prompt шаблон:**

```markdown
## Задача: Перевод RU → UK

### Input
Файл: categories/{slug}/content/{slug}_ru.md

### Output
Файл: categories/{slug}/content/{slug}_uk.md

### Правила

1. **Preserve Markup:** НЕ менять Markdown структуру
2. **Links:** НЕ переводить URLs, переводить только текст ссылок
3. **Терминология авто-детейлинга:**
   - Активная пена → Активна піна
   - Мойка высокого давления → Мийка високого тиску
   - Чернитель шин → Чорнитель шин
4. **Длина:** ±5% от оригинала
5. **Commercial Markers:**
   - купить → купити
   - цена → ціна
   - заказать → замовити
   - доставка → доставка (одинаково)

### Проверка после перевода
- Подсчитать символы
- Проверить все H2
- Проверить FAQ

### Style
- Естественный украинский, НЕ калька
- Коммерческий тон
```

**GAP:** Небольшой. `general-purpose` с правильным prompt справится.

---

### 8. seo-validate → seo-content-auditor (sonnet) ⭐⭐

**Skill функционал:**

- 5 checks через скрипты
- Water/Nausea v7.3 targets
- NER/Blacklist

**Prompt шаблон:**

```markdown
## Задача: Validation (5 Checks)

### Input
- Файл: categories/{slug}/content/{slug}_ru.md
- Tier: {tier}
- Primary keyword: {keyword}

### Запустить валидацию
```bash
source venv/bin/activate
PYTHONPATH=. python3 scripts/quality_runner.py \
  categories/{slug}/content/{slug}_ru.md \
  "{keyword}" \
  {tier}
```

### 5 Checks

1. **Markdown structure** (pymarkdownlnt)
2. **Grammar** (language_tool_python)
3. **Water/Nausea v7.3** (check_water_natasha.py)
4. **Keyword density** (check_simple_v2_md.py)
5. **NER/Blacklist** (check_ner_brands.py)

### Targets v7.3 (Tier {tier})

| Метрика | Target | BLOCKER |
|---------|--------|---------|
| Water % | 40-60% | <30% / >70% |
| Classic Nausea | ≤3.5 | >4.0 |
| Academic Nausea | 7-9.5% | >12% |
| Density | {density_min}-{density_max}% | >3% |

### Exit Codes

- 0 = ALL PASS
- 1 = WARNINGS
- 2 = ERRORS (stop)

### Troubleshooting

**Water too low (<40%):**

- Добавить connector words (и, или, для)
- Longer sentences

**Water too high (>60%):**

- Добавить technical terms
- Убрать filler phrases

**Nausea too high (>3.5):**

- Synonym rotation (max 2x per paragraph)
- Distribute keywords evenly

### Output Format

```json
{
  "status": "PASS/WARNING/FAIL",
  "checks": {
    "markdown": {"status": "PASS"},
    "grammar": {"status": "PASS"},
    "water_nausea": {"status": "PASS", "water": 52, "nausea": 3.2},
    "keywords": {"status": "PASS", "density": 1.5},
    "ner": {"status": "PASS"}
  },
  "issues": []
}
```

```

**GAP:** Средний. `seo-content-auditor` знает E-E-A-T, но НЕ знает наши скрипты и Адвего-калибровку. Нужен полный prompt с командами.

---

### 9. seo-meta → seo-meta-optimizer (haiku)

**Skill функционал:**
- Title 50-70 chars
- Description 140-170 chars
- RU + UK версии
- Title ≠ H1

**Prompt шаблон:**
```markdown
## Задача: Meta Tags

### Input
- Slug: {slug}
- Category: {category_name}
- Primary keyword: {keyword}
- H1 из контента: {h1}

### Title Rules
- Length: 50-70 chars
- Format: `[Keyword] | [Modifier] – Ultimate`
- MUST contain PRIMARY keyword (1x only)
- MUST be different from H1

### Description Rules
- Length: 140-170 chars
- Start with: "Купить" / "Купити"
- Include: keyword, price hint, delivery

### Output: categories/{slug}/meta/{slug}_meta.json

```json
{
  "category": "{slug}",
  "generated_at": "{ISO_NOW}",
  "ru": {
    "title": "...",
    "title_length": N,
    "description": "...",
    "description_length": N
  },
  "uk": {
    "title": "...",
    "title_length": N,
    "description": "...",
    "description_length": N
  }
}
```

### Validation

- Title length: 50-70 chars ✓
- Title ≠ H1 ✓
- Description length: 140-170 chars ✓
- PRIMARY in title ✓
- Starts with "Купить" ✓

```

**GAP:** Минимальный. `seo-meta-optimizer` хорошо подходит, нужен только формат output.

---

### 10. seo-package → general-purpose (haiku)

**Skill функционал:**
- Копировать файлы в deliverables/
- Создать README.md
- Создать QUALITY_REPORT.md

**Prompt шаблон:**
```markdown
## Задача: Package Deliverables

### Собрать файлы в: categories/{slug}/deliverables/

```

├── README.md
├── QUALITY_REPORT.md
├── {slug}_ru.md (copy)
├── {slug}_uk.md (copy)
└── {slug}_meta.json (copy)

```

### README.md Template
```markdown
# Deliverables: {category_name}

**Slug:** {slug}
**Tier:** {tier}
**Generated:** {date}

## Files
1. `{slug}_ru.md` — Russian content
2. `{slug}_uk.md` — Ukrainian content
3. `{slug}_meta.json` — Meta tags

## How to Use (OpenCart)
1. Content: Admin → Categories → Edit → Description
2. Meta: Copy title/description from JSON
3. URL: Set to `/{slug}/`
```

### QUALITY_REPORT.md Template

```markdown
# Quality Report: {category_name}

**Tier:** {tier}
**Status:** APPROVED
**SEO Standard:** v7.3

## Content Metrics (RU)
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Chars | {chars} | {target} | ✓ |
| Words | {words} | {target} | ✓ |
| Density | {density}% | {target} | ✓ |
| Water | {water}% | 40-60% | ✓ |
| Nausea | {nausea} | ≤3.5 | ✓ |

## Meta Tags
| Field | Length | Target |
|-------|--------|--------|
| Title | {len} | 50-70 |
| Description | {len} | 140-170 |
```

### Update task file

- stages.packaging = "completed"
- status = "completed"

```

**GAP:** Нет. Чистая file operations.

---

## Summary: GAP Analysis

| Skill | Sub-agent | GAP Level | Решение |
|-------|-----------|-----------|---------|
| seo-init | general-purpose | **Нет** | Структура в prompt |
| seo-data | general-purpose | **Нет** | Скрипт делает работу |
| seo-urls | general-purpose | **Нет** | Скрипты делают работу |
| seo-competitors | seo-content-planner | **Низкий** | Скрипт + формат |
| seo-research | search-specialist | **Средний** | 4 секции + Tier coverage |
| **seo-content** | seo-content-writer | **КРИТИЧНЫЙ** | Вся v7.3 спецификация |
| seo-translator | general-purpose | **Низкий** | Терминология + ±5% |
| seo-validate | seo-content-auditor | **Средний** | Скрипты + targets |
| seo-meta | seo-meta-optimizer | **Минимальный** | Формат output |
| seo-package | general-purpose | **Нет** | Templates в prompt |

---

## Что нужно актуализировать

### Вариант A: Prompt Templates (рекомендуется)

Создать файлы промптов:
```

prompts/
├── init.md
├── data.md
├── urls.md
├── competitors.md
├── research.md
├── content_v73.md      ← КРИТИЧНЫЙ (2000+ токенов)
├── translator.md
├── validate.md
├── meta.md
└── package.md

```

Оркестратор читает prompt template → подставляет переменные → отправляет агенту.

### Вариант B: Custom Agents (если возможно)

Создать кастомных агентов с прешитой спецификацией v7.3. Но это требует изменения системы.

---

## Приоритет актуализации

| # | Что | Почему | Effort |
|---|-----|--------|--------|
| 1 | **content_v73.md** | Критичный GAP, вся спецификация | High |
| 2 | **validate.md** | Скрипты + targets | Medium |
| 3 | **research.md** | 4 секции + coverage | Medium |
| 4 | Остальные | Минимальный GAP | Low |

---

## Action Plan

1. [ ] Создать папку `prompts/`
2. [ ] Написать `content_v73.md` (полная v7.3 спецификация) — **КРИТИЧНЫЙ**
3. [ ] Написать `validate.md` (скрипты + targets)
4. [ ] Написать `research.md` (4 секции)
5. [ ] Написать остальные prompts (init, data, urls, competitors, translator, meta, package)
6. [x] Обновить CLAUDE.md — убрать Skills, добавить Sub-agents ✓ DONE
7. [ ] Тестовый прогон на одной категории
8. [ ] Полная миграция

### Дополнительно создано:
- [x] `SEO_MASTER.md` — единый файл спецификации v7.3 ✓ DONE

---

## Оценка затрат контекста

### Skills (было):
- Каждый Skill: ~1000-3000 токенов
- Полный workflow (10 skills): ~15000 токенов В контекст оркестратора

### Sub-agents с prompts (будет):
- Prompt отправляется В агента (не в оркестратор)
- Оркестратор получает только результат: ~200-500 токенов
- Полный workflow: ~3000-5000 токенов В контекст оркестратора

**Экономия: ~70%**

---

**Version:** 1.1 (Action Plan updated)
**Author:** Orchestrator (Opus 4.5)
**Date:** 2025-12-11
**Status:** IN PROGRESS — prompts/ не создана
