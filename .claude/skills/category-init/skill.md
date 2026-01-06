---
name: category-init
description: Initialize new SEO category structure for Ultimate.net.ua. Creates folder hierarchy, extracts keywords from CSV, generates clustered _clean.json. Use when you see /category-init, создай категорию, инициализируй категорию, новая категория, подготовь папку для категории.
---

# Category Init v2.0

Initialize new category for SEO content pipeline with **proper keyword clustering**.

---

## Проблема, которую решаем

CSV содержит 50+ сырых ключей с дублями:

- "пена для мойки авто" (1300)
- "пена для мойки автомобиля" (1300)
- "активная пена для мойки авто" (1000)

Это **одно и то же** — нельзя использовать все в тексте (переспам).

**Решение:** Кластеризация до 10-15 уникальных ключей с правилами использования.

---

## Workflow

### Step 1: Validate Input

```
Input: slug (e.g., "aktivnaya-pena", "cherniteli-shin")
Validate:
- slug is kebab-case (lowercase, hyphens)
- slug exists in Структура _Ultimate.csv
- folder categories/{slug}/ does not exist
```

### Step 2: Find Category in CSV

Parse `Структура _Ultimate.csv`:

- Find L2/L3 category matching slug
- Extract ALL keywords with search volumes
- Note parent L1 and L2 categories

CSV structure:

```
L1: Мойка и Экстерьер,24/338,
L2: Автошампуни,5/59,
L3: Активная пена,52,
keyword1,,volume
keyword2,,volume
```

### Step 3: Create Folder Structure

```bash
categories/{slug}/
├── data/
│   └── {slug}_clean.json    # Clustered keywords
├── meta/
│   └── {slug}_meta.json     # Meta tags template
├── content/
│   └── {slug}_ru.md         # Content (empty)
└── research/
    └── RESEARCH_DATA.md     # Research template
```

### Step 4: Cluster Keywords (КРИТИЧЕСКИ ВАЖНО!)

**Цель:** Сократить 50+ ключей до 10-15 уникальных

#### 4.1 Слияние дублей

Объединяем семантически идентичные ключи:

```
"пена для мойки авто" (1300)
"пена для мойки автомобиля" (1300)
"активная пена для мойки авто" (1000)
→ ОДИН ключ: "активная пена" (main cluster)
```

#### 4.2 Выделение Commercial

Все ключи с "купить/цена/заказать" → отдельная группа с `use_in: "meta_only"`:

```json
{
  "keyword": "купить активную пену",
  "volume": 210,
  "cluster": "commercial",
  "use_in": "meta_only"  // ← НЕ использовать в тексте!
}
```

#### 4.3 Семантические кластеры

| Кластер | Описание | Пример |
|---------|----------|--------|
| main | Основной запрос категории | "активная пена" |
| method | Способ/метод применения | "для бесконтактной мойки" |
| equipment | Оборудование | "для минимойки", "для керхера" |
| material | Материал/поверхность | "для ткани", "для кожи" |
| B2B | Профессиональное | "для автомойки", "профессиональная" |
| pro | Премиум сегмент | "профессиональная химия" |
| product_type | Разные продукты в одной категории | "нанокерамика" vs "жидкое стекло" |
| spelling_variant | Вариант написания | "нано керамика" vs "нанокерамика" |
| commercial | Транзакционный | "купить", "цена" |

> ⚠️ **ВАЖНО:** `synonym` используется ТОЛЬКО для настоящих синонимов (одно и то же).
> Для разных продуктов в одной категории используйте `product_type`!

### Step 5: Generate _clean.json

**Формат файла:**

```json
{
  "slug": "aktivnaya-pena",
  "language": "ru",
  "clustered_at": "2025-12-30",

  "keywords": {
    "primary": [
      {
        "keyword": "активная пена",
        "volume": 170,
        "cluster": "main"
      },
      {
        "keyword": "пена для мойки автомобиля",
        "volume": 140,
        "cluster": "main"
      }
    ],

    "secondary": [
      {
        "keyword": "активная пена для бесконтактной мойки",
        "volume": 30,
        "cluster": "method"
      },
      {
        "keyword": "пена для автомойки",
        "volume": 20,
        "cluster": "B2B"
      }
    ],

    "supporting": [
      {
        "keyword": "шампунь для бесконтактной мойки",
        "volume": 10,
        "cluster": "product_type",
        "note": "шампунь ≠ пена, разные продукты"
      },
      {
        "keyword": "пена для минимойки",
        "volume": 10,
        "cluster": "equipment"
      },
      {
        "keyword": "профессиональная пена для мойки авто",
        "volume": 10,
        "cluster": "pro"
      }
    ],

    "commercial": [
      {
        "keyword": "купить пену для мойки авто",
        "volume": 40,
        "cluster": "commercial",
        "use_in": "meta_only"
      },
      {
        "keyword": "купить активную пену",
        "volume": 20,
        "cluster": "commercial",
        "use_in": "meta_only"
      }
    ]
  },

  "stats": {
    "before": 52,
    "after": 12
  },

  "usage_rules": {
    "primary": "H1 + intro (первые 150 слов)",
    "secondary": "H2 заголовки, buying guide (выбор, виды, применение)",
    "supporting": "FAQ, таблицы, естественные упоминания в тексте",
    "commercial": "ТОЛЬКО meta title/description, НЕ в текст статьи!"
  },

  "clustering_notes": {
    "merged_main": [
      "пена для мойки авто (1300)",
      "активная пена для мойки авто (1000)",
      "активная пена для мойки автомобиля (880)"
    ],
    "merged_commercial": [
      "купить активную пену для мойки авто (210)",
      "купить активную пену для мойки автомобиля (170)"
    ]
  }
}
```

### Step 6: Create Templates

**meta/{slug}_meta.json:**

```json
{"slug": "{slug}", "language": "ru", "status": "template"}
```

**research/RESEARCH_DATA.md:**

```markdown
# Research: {slug}

## Status: PENDING
```

### Step 7: Validate Output

Check:

- [ ] JSON is valid
- [ ] Keywords clustered (before > after в stats)
- [ ] Commercial имеют `use_in: "meta_only"`
- [ ] usage_rules присутствуют
- [ ] clustering_notes показывают логику слияния
- [ ] Итого 10-15 уникальных ключей (не 50+)

---

## Правила кластеризации

### Primary (2-3 ключа)

- Главный запрос категории
- Самый высокий volume после слияния дублей
- Использовать в H1 и intro

### Secondary (3-5 ключей)

- Вариации по методу/оборудованию/сегменту
- Volume 20-100
- Для H2 заголовков

### Supporting (5-7 ключей)

- Long-tail запросы
- Синонимы
- Volume 10-20
- Для FAQ и таблиц

### Commercial (2-4 ключа)

- ВСЕ с "купить/цена/заказать"
- **ОБЯЗАТЕЛЬНО** `use_in: "meta_only"`
- НИКОГДА не использовать в тексте статьи

---

## Output

```
categories/{slug}/
  - data/{slug}_clean.json (CLUSTERED, 10-15 keywords)
  - meta/{slug}_meta.json (template)
  - content/{slug}_ru.md (empty)
  - research/RESEARCH_DATA.md (template)

Stats: 52 raw → 12 clustered keywords
Status: ready for /generate-meta
```

---

## Next Step

After category-init, run `/generate-meta {slug}` to generate meta tags.

---

**Version:** 2.0 — December 2025
**Change:** Added proper clustering format with usage_rules and clustering_notes
