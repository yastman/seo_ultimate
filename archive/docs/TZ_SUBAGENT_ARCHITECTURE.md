# ТЗ: Архитектура на Суб-агентах v1.0

**Цель:** Заменить Skills на Task tool с суб-агентами для экономии контекста.

---

## Архитектура

```
┌─────────────────────────────────────────┐
│  ТЫ: "контент для aktivnaya-pena"       │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Я (Orchestrator / Opus 4.5)            │
│  • Парсю команду                        │
│  • Читаю task_{slug}.json               │
│  • Формирую PROMPT для суб-агента       │
│  • Task tool → агент в ОТДЕЛЬНОМ        │
│    контексте                            │
│  • Получаю ТОЛЬКО результат             │
│  • Сохраняю файлы                       │
│  • Обновляю task file                   │
└─────────────────────────────────────────┘
                    │
          ┌────────┴────────┐
          ▼                 ▼
┌─────────────────┐ ┌─────────────────┐
│ Sub-agent 1     │ │ Sub-agent 2     │
│ (отд. контекст) │ │ (отд. контекст) │
│ → результат     │ │ → результат     │
└─────────────────┘ └─────────────────┘
```

**Преимущество:** Суб-агенты работают в ИЗОЛИРОВАННОМ контексте. Оркестратор получает только финальный результат, не загружая свой контекст инструкциями.

---

## Маппинг: Skills → Sub-агенты

| Старый Skill | Новый Sub-агент | Модель |
|--------------|-----------------|--------|
| `seo-init` | `general-purpose` | haiku |
| `seo-data` | `general-purpose` | haiku |
| `seo-urls` | `general-purpose` | haiku |
| `seo-competitors` | `seo-content-creation:seo-content-planner` | sonnet |
| `seo-research` | `content-marketing:search-specialist` | sonnet |
| `seo-content` | `seo-content-creation:seo-content-writer` | **sonnet** |
| `seo-translator` | `general-purpose` | sonnet |
| `seo-validate` | `seo-content-creation:seo-content-auditor` | sonnet |
| `seo-meta` | `seo-technical-optimization:seo-meta-optimizer` | haiku |
| `seo-package` | `general-purpose` | haiku |

---

## Детальное описание каждого этапа

### 1. INIT (general-purpose, haiku)

**Команда:** `"init {slug} tier {A/B/C}"`

**Prompt для агента:**
```
Создай структуру папок для SEO-категории:
- Slug: {slug}
- Tier: {tier}

Создай:
1. categories/{slug}/
2. categories/{slug}/content/
3. categories/{slug}/meta/
4. categories/{slug}/deliverables/
5. categories/{slug}/.logs/
6. task_{slug}.json с начальным состоянием

Верни JSON с созданными путями.
```

**Результат:** JSON с путями созданных папок.

---

### 2. DATA (general-purpose, haiku)

**Команда:** `"данные для {slug}"`

**Prompt для агента:**
```
Запусти скрипт подготовки данных:
1. source venv/bin/activate
2. python3 scripts/parse_semantics_to_json.py {slug} {tier}

Верни результат выполнения и путь к созданному JSON.
```

**Результат:** Путь к keywords JSON.

---

### 3. URLs (general-purpose, haiku)

**Команда:** `"urls для {slug}"`

**Prompt для агента:**
```
Извлеки URLs конкурентов из SERP данных:
1. source venv/bin/activate
2. python3 scripts/extract_competitor_urls_v2.py {slug}
3. python3 scripts/url_preparation_filter_and_validate.py ...

Верни список валидных URLs.
```

**Результат:** Список URLs для анализа.

---

### 4. COMPETITORS (seo-content-planner, sonnet)

**Команда:** `"конкуренты для {slug}"`

**Prompt для агента:**
```
Проанализируй конкурентов для категории "{slug}":

Входные данные:
- URLs: [список из предыдущего шага]
- Tier: {tier}

Задачи:
1. Проанализируй meta-теги конкурентов
2. Выяви паттерны в Title и Description
3. Определи средние длины
4. Найди используемые ключевики

Результат сохрани в: categories/{slug}/meta_patterns.json

Формат:
{
  "avg_title_length": N,
  "avg_desc_length": N,
  "common_keywords": [],
  "title_patterns": [],
  "desc_patterns": []
}
```

**Результат:** meta_patterns.json

---

### 5. RESEARCH (search-specialist, sonnet)

**Команда:** `"research для {slug}"`

**Prompt для агента:**
```
Проведи исследование для SEO-контента категории "{category_name}":

Ключевые слова: {keywords_list}
Tier: {tier}

Используй Perplexity MCP для:
1. Технические характеристики товаров
2. Популярные бренды в нише
3. Критерии выбора для покупателя
4. Частые вопросы покупателей (для FAQ)
5. Преимущества/недостатки типов товаров

Формат ответа:
- Краткие факты (bullet points)
- Только проверенная информация
- Без истории и энциклопедии
- Фокус на E-commerce контекст

Сохрани в: categories/{slug}/research.json
```

**Результат:** research.json с фактами.

---

### 6. CONTENT (seo-content-writer, sonnet) ⭐ ГЛАВНЫЙ

**Команда:** `"контент для {slug}"`

**Prompt для агента:**
```
Напиши SEO-текст для категории интернет-магазина:

## Входные данные
- Slug: {slug}
- Категория: {category_name}
- Tier: {tier}
- Keywords: {keywords_json}
- Research: {research_json}

## Требования (SEO 2025 v7.3 — Shop Mode)

### Метрики для Tier {tier}:
| Метрика | Target |
|---------|--------|
| Символы | {chars_min}-{chars_max} |
| Слова | {words_min}-{words_max} |
| H2 | {h2_min}-{h2_max} |
| FAQ | {faq_min}-{faq_max} |
| Density | {density_min}-{density_max}% |
| Water | 40-60% |
| Classic Nausea | ≤3.5 |

### Synonym Rotation (КРИТИЧНО)
Правило: Максимум 2 повтора одного слова в параграфе.
```
❌ Пена очищает. Пена создаёт шапку. Пена безопасна.
✅ Пена очищает. Состав создаёт шапку. Средство безопасно.
```

### Commercial Markers (ОБЯЗАТЕЛЬНО)
Минимум {commercial_min} слов из списка:
- купить, цена, интернет-магазин, доставка, заказать, в наличии, оптом

### Anti-Fluff (ЗАПРЕЩЕНО)
❌ "В современном мире...", "Ни для кого не секрет..."
❌ "В этой статье...", "Давайте разберём...", "В заключение..."
❌ "Первые шампуни появились...", "История создания..."

### Структура
1. Intro (без H2, 2-3 предложения)
2. H2 секции с полезным контентом
3. FAQ (## Часто задаваемые вопросы)

### Формат вывода
Markdown файл. Только контент, без мета-комментариев.

Сохрани в: categories/{slug}/content/{slug}_ru.md
```

**Результат:** {slug}_ru.md

---

### 7. VALIDATE (seo-content-auditor, sonnet)

**Команда:** `"проверь {slug}"`

**Prompt для агента:**
```
Проведи аудит SEO-контента:

Файл: categories/{slug}/content/{slug}_ru.md
Tier: {tier}
Главный ключевик: {main_keyword}

## Проверки:

1. **Структура Markdown** — валидный MD
2. **Грамматика** — без ошибок
3. **Water %** — должен быть 40-60%
4. **Classic Nausea** — должен быть ≤3.5
5. **Academic Nausea** — должен быть 7-9.5%
6. **Keyword Density** — {density_min}-{density_max}%
7. **Commercial Markers** — минимум {commercial_min}
8. **Synonym Rotation** — max 2x слово в параграфе
9. **Anti-Fluff** — нет AI-шаблонов
10. **NER** — нет брендов/городов

Запусти:
```bash
PYTHONPATH=. python3 scripts/quality_runner.py {file} "{keyword}" {tier}
```

Формат ответа:
```json
{
  "status": "PASS/WARNING/FAIL",
  "checks": {
    "structure": {"status": "PASS", "details": "..."},
    "water": {"status": "PASS", "value": 52, "target": "40-60"},
    ...
  },
  "issues": [],
  "recommendations": []
}
```
```

**Результат:** Validation report JSON.

---

### 8. TRANSLATOR (general-purpose, sonnet)

**Команда:** `"переведи {slug}"`

**Prompt для агента:**
```
Переведи SEO-текст с русского на украинский:

Исходный файл: categories/{slug}/content/{slug}_ru.md
Целевой файл: categories/{slug}/content/{slug}_uk.md

## Правила перевода:

1. **Длина:** ±5% от оригинала
2. **Ключевики:** Перевод с сохранением SEO-intent
   - купить → купити
   - цена → ціна
   - доставка → доставка (одинаково)
   - заказать → замовити

3. **Структура:** Сохранить все H2, FAQ
4. **Стиль:** Естественный украинский, не калька
5. **Commercial markers:** Сохранить все маркеры

## Проверка после перевода:
- Подсчитай символы (должно быть ±5%)
- Проверь наличие всех H2
- Проверь FAQ вопросы

Сохрани в: categories/{slug}/content/{slug}_uk.md
```

**Результат:** {slug}_uk.md

---

### 9. META (seo-meta-optimizer, haiku)

**Команда:** `"meta для {slug}"`

**Prompt для агента:**
```
Сгенерируй мета-теги для категории:

Категория: {category_name}
Slug: {slug}
Главный ключевик: {main_keyword}
Паттерны конкурентов: {meta_patterns_json}

## Требования:

### Title (RU + UK)
- Длина: 50-70 символов
- Формат: "{Ключевик} купить в Украине | Ultimate"
- Включить: главный ключевик + коммерческий intent

### Description (RU + UK)
- Длина: 140-170 символов
- Включить: ключевик, выгоды, CTA
- Формат: "{Ключевик} ✓ Большой выбор ✓ Доставка по Украине ✓ Лучшие цены в Ultimate"

## Формат вывода:
```json
{
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

Сохрани в: categories/{slug}/meta/meta_tags.json
```

**Результат:** meta_tags.json

---

### 10. PACKAGE (general-purpose, haiku)

**Команда:** `"упакуй {slug}"`

**Prompt для агента:**
```
Упакуй deliverables для категории {slug}:

## Собрать файлы:
1. categories/{slug}/content/{slug}_ru.md
2. categories/{slug}/content/{slug}_uk.md
3. categories/{slug}/meta/meta_tags.json

## Создать:
categories/{slug}/deliverables/
├── content_ru.md (копия)
├── content_uk.md (копия)
├── meta.json (копия)
└── summary.json

## summary.json:
```json
{
  "slug": "{slug}",
  "tier": "{tier}",
  "created": "ISO date",
  "files": [...],
  "validation_status": "PASS",
  "metrics": {
    "ru": {"chars": N, "words": N, "h2": N},
    "uk": {"chars": N, "words": N, "h2": N}
  }
}
```

Верни путь к deliverables/ и summary.
```

**Результат:** Путь к deliverables/.

---

## Оркестрация: Полный Workflow

**Команда:** `"полный workflow {slug} tier {tier}"`

**Логика оркестратора:**

```python
async def full_workflow(slug, tier):
    # 1. Init
    result = await Task(
        subagent_type="general-purpose",
        model="haiku",
        prompt=INIT_PROMPT.format(slug=slug, tier=tier)
    )
    update_task_file(slug, "init", "completed")

    # 2. Data
    result = await Task(
        subagent_type="general-purpose",
        model="haiku",
        prompt=DATA_PROMPT.format(slug=slug, tier=tier)
    )
    update_task_file(slug, "data_prep", "completed")

    # 3. URLs
    result = await Task(
        subagent_type="general-purpose",
        model="haiku",
        prompt=URLS_PROMPT.format(slug=slug)
    )
    update_task_file(slug, "url_extraction", "completed")

    # 4. Competitors
    result = await Task(
        subagent_type="seo-content-creation:seo-content-planner",
        model="sonnet",
        prompt=COMPETITORS_PROMPT.format(slug=slug, urls=urls)
    )
    update_task_file(slug, "competitors", "completed")

    # 5. Research (optional)
    result = await Task(
        subagent_type="content-marketing:search-specialist",
        model="sonnet",
        prompt=RESEARCH_PROMPT.format(slug=slug, keywords=keywords)
    )
    update_task_file(slug, "research", "completed")

    # 6. Content
    result = await Task(
        subagent_type="seo-content-creation:seo-content-writer",
        model="sonnet",
        prompt=CONTENT_PROMPT.format(...)
    )
    update_task_file(slug, "content_ru", "completed")

    # 7. Validate
    result = await Task(
        subagent_type="seo-content-creation:seo-content-auditor",
        model="sonnet",
        prompt=VALIDATE_PROMPT.format(slug=slug, tier=tier)
    )

    if result.status == "FAIL":
        # Regenerate content
        ...

    update_task_file(slug, "validation", "completed")

    # 8. Translate
    result = await Task(
        subagent_type="general-purpose",
        model="sonnet",
        prompt=TRANSLATE_PROMPT.format(slug=slug)
    )
    update_task_file(slug, "content_uk", "completed")

    # 9. Meta
    result = await Task(
        subagent_type="seo-technical-optimization:seo-meta-optimizer",
        model="haiku",
        prompt=META_PROMPT.format(slug=slug)
    )
    update_task_file(slug, "meta", "completed")

    # 10. Package
    result = await Task(
        subagent_type="general-purpose",
        model="haiku",
        prompt=PACKAGE_PROMPT.format(slug=slug)
    )
    update_task_file(slug, "packaging", "completed")

    return "✅ Готово!"
```

---

## Параллельное выполнение

Некоторые этапы можно запускать параллельно:

```
Sequential:
init → data → urls → competitors → research → content → validate
                                                           ↓
                                                    [if PASS]
                                                           ↓
Parallel after validation:
├── translate (sonnet)
├── meta (haiku)
└── [wait for both]
         ↓
      package
```

**Код:**
```python
# После успешной валидации — параллельно
translate_task = Task(
    subagent_type="general-purpose",
    model="sonnet",
    prompt=TRANSLATE_PROMPT,
    run_in_background=True
)

meta_task = Task(
    subagent_type="seo-technical-optimization:seo-meta-optimizer",
    model="haiku",
    prompt=META_PROMPT,
    run_in_background=True
)

# Дождаться обоих
translate_result = await TaskOutput(translate_task.id)
meta_result = await TaskOutput(meta_task.id)

# Потом package
```

---

## Экономия контекста

| Подход | Контекст оркестратора |
|--------|----------------------|
| **Skills (старый)** | +5-10K токенов на каждый skill |
| **Sub-agents (новый)** | ~500 токенов (только результат) |

**Экономия на полном workflow:** ~50-80K токенов

---

## Миграция

### Шаг 1: Обновить CLAUDE.md
- Убрать секцию Skills
- Добавить секцию Sub-agents

### Шаг 2: Удалить .claude/skills/
- Или оставить как reference

### Шаг 3: Создать prompt templates
- `prompts/init.md`
- `prompts/content.md`
- `prompts/validate.md`
- etc.

### Шаг 4: Тестирование
- Прогнать один slug через новую архитектуру
- Сравнить качество и время

---

## Риски и митигация

| Риск | Митигация |
|------|-----------|
| Агент не знает контекст проекта | Подробный prompt с требованиями |
| Агент не может читать файлы | Передавать данные в prompt |
| Качество ниже Opus | Использовать sonnet для критичных задач |
| Агент игнорирует требования | Добавить примеры в prompt |

---

## Готовность к внедрению

- [ ] Утвердить архитектуру
- [ ] Создать prompt templates
- [ ] Обновить CLAUDE.md
- [ ] Тестовый прогон
- [ ] Полная миграция

---

**Version:** 1.0
**Author:** Orchestrator (Opus 4.5)
**Date:** 2025-12-11
