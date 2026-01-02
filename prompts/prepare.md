# PREPARE Prompt — Category Initialization

**Sub-agent:** `general-purpose` (haiku)
**Этап:** 1/3 (PREPARE)
**Задача:** Подготовить структуру и данные для категории

---

## Input Parameters

- `slug`: {slug}
- `name`: {name}
- `tier`: {tier} (A/B/C)

---

## Steps

### Step 1: Init Folders

Создать структуру категории:

```bash
categories/{slug}/
├── content/
├── meta/
├── data/
├── deliverables/
└── .logs/
```

### Step 2: Create Task File

Создать `task_{slug}.json`:

```json
{
  "slug": "{slug}",
  "tier": "{tier}",
  "keywords_count": 0,
  "created_at": "ISO8601",
  "current_stage": "prepare",
  "stages": {
    "prepare": "completed",
    "produce": "pending",
    "deliver": "pending"
  },
  "paths": {
    "data": "categories/{slug}/data/{slug}.json",
    "content_ru": "categories/{slug}/content/{slug}_ru.md",
    "meta": "categories/{slug}/meta/{slug}_meta.json",
    "deliverables": "categories/{slug}/deliverables/"
  }
}
```

### Step 3: Generate Keywords JSON

Запустить скрипт парсинга:

```bash
source venv/bin/activate
PYTHONPATH=. python3 scripts/parse_semantics_to_json.py {slug} {tier}
```

**Output:** `categories/{slug}/data/{slug}.json`

**Формат JSON:**

```json
{
  "slug": "{slug}",
  "name": "{name}",
  "tier": "{tier}",
  "main_keyword": "...",
  "main_keyword_volume": 1234,
  "keywords": [
    {"keyword": "...", "volume": 123, "type": "exact"},
    ...
  ],
  "total_keywords": 52,
  "total_volume": 12345
}
```

### Step 4: CLEAN Keywords (Рекомендуется)

Кластеризация 52 ключей → 12 уникальных:

```bash
# Используйте seo-clean skill
# Input: {slug}.json (52 kw)
# Output: {slug}_clean.json (12 kw)
```

**D+E Pattern:** Все скрипты автоматически используют `_clean.json` если существует.

**Преимущества:**
- 100% coverage вместо ~40%
- Оптимальная density ~4%
- Без дубликатов ключей

### Step 5: Extract URLs (Optional)

Если нужен анализ конкурентов:

```bash
python3 scripts/extract_competitor_urls_v2.py {slug}
```

**Output:** `categories/{slug}/data/{slug}_urls.txt`

---

## Output Report

Вернуть Orchestrator:

```
✅ PREPARE завершён для {slug}

Структура:
- Папки созданы: categories/{slug}/
- Task file: task_{slug}.json
- Keywords JSON: categories/{slug}/data/{slug}.json

Keywords Stats:
- Main keyword: "{main_keyword}" (volume: {volume})
- Total keywords: {count}
- Total volume: {total_volume}

URLs (optional):
- Extracted: {url_count} URLs
- File: categories/{slug}/data/{slug}_urls.txt

Статус: stage=prepare completed
Следующий этап: PRODUCE
```

---

## Error Handling

### Если CSV не найден:

```
❌ ERROR: CSV file not found
Path: data/Структура Ultimate финал - Лист2.csv
Action: Check file path or download CSV
```

### Если venv не активирован:

```
❌ ERROR: venv not activated
Action: Run "source venv/bin/activate"
```

---

## Success Criteria

- [ ] Папки созданы
- [ ] task_{slug}.json существует
- [ ] categories/{slug}/data/{slug}.json создан
- [ ] **(Рекомендуется)** categories/{slug}/data/{slug}_clean.json создан
- [ ] JSON содержит min 3 keywords (12 в _clean.json)
- [ ] Stage "prepare" = "completed" в task file

---

**Version:** 5.1
**Spec:** SEO_MASTER.md v7.3
**D+E Pattern:** Includes CLEAN step for _clean.json
**Model:** haiku (fast init)
**Updated:** 2025-12-12
