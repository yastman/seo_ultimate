# ОПТИМИЗИРОВАННЫЙ WORKFLOW V2.0

**Версия:** 2.0 (индустриальные практики 2025)
**Дата:** 12 ноября 2025
**Статус:** PRODUCTION READY

---

## 📊 ОБЗОР

Оптимизированный workflow для генерации SEO-контента с использованием готовых данных:

- ✅ ТЗ от Perplexity (ручное)
- ✅ CSV мета-данных конкурентов (Screaming Frog)
- ✅ SERP keywords (поисковая выдача топ-10)

**Архивированные агенты:**

- ❌ competitor-scraping-agent (Stage -1) - нет полных текстов
- ❌ competitor-analysis-agent (Stage 5) - есть готовое ТЗ
- ❌ perplexity-research-agent (Stage 7) - ТЗ делается вручную

---

## 🚀 WORKFLOW (5 АВТОМАТИЧЕСКИХ + 1 РУЧНОЙ STAGE)

```
✅ Stage 0:  Инициализация
✅ Stage -3: URL Extraction (автоматически)
✅ Stage -2: URL Preparation (автоматически)
   ↓
🛑 MANUAL STAGE 3: Ручная подготовка данных (ПАУЗА WORKFLOW)
   ├─ Screaming Frog: Загрузить meta_competitors.csv
   └─ Perplexity: Создать perplexity_research.md вручную
   ↓
✅ Stage 4:  Data Preparation (продолжение после ручной работы)
   ↓
→ Stage 6:  Keyword Distribution + Technical Brief ← КРИТИЧЕСКИЙ
   ↓
  Stage 8:  Content Generation RU
   ↓
  Stage 9:  Ukrainian Translation
   ↓
  Stage 10: Meta Tags Generation
   ↓
  Stage 11: Packaging
```

**⚠️ ВАЖНО:** Workflow останавливается после Stage -2 для ручной подготовки данных. Возобновляется командой: **"продолжи после ручной работы для {slug}"**

---

## 🛑 MANUAL STAGE 3: РУЧНАЯ ПОДГОТОВКА ДАННЫХ

**После Stage -2 workflow останавливается — вы делаете 2 файла вручную:**

### Файл 1: meta_competitors.csv (Screaming Frog)

**Путь:** `categories/{slug}/competitors/meta_competitors.csv`

**Как:**

1. Открыть Screaming Frog → Mode: List
2. File → Upload → `categories/{slug}/urls.txt`
3. Start → дождаться завершения
4. Bulk Export → Response Codes → Indexable → фильтр 200 OK
5. Сохранить CSV (минимум 5 конкурентов с Title, Description, H1)

---

### Файл 2: perplexity_research.md (Perplexity ТЗ)

**Путь:** `categories/{slug}/research/perplexity_research.md`

**Как:**

1. Открыть Perplexity.ai
2. Промпт: "Создай ТЗ для категории {название}: структура H2 (3-4 секции), FAQ (4-5 вопросов), технические детали, источники 2024-2025"
3. Сохранить ответ как .md файл

**Требования:** ≥3 H2, ≥4 FAQ, конкретные цифры/характеристики

---

### Команда для возобновления

```
данные готовы, продолжай для {slug}
```

Claude автоматически запустит Stage 4 → 6 → 8-11

---

## 📋 STAGE 6: KEYWORD DISTRIBUTION + TECHNICAL BRIEF

**Цель:** Создать Technical Content Brief для content-agent

**Агент:** `keyword-distribution-agent` (расширенный)
**Валидатор:** `stage-5-6-analysis-validator`

### INPUT

```
- categories/{slug}/data/{slug}.json (16 keywords: 3 PRIMARY, 5 SECONDARY, 8 SUPPORTING)
- categories/{slug}/research/perplexity_research.md (ТЗ: структура H2, FAQ темы)
- categories/{slug}/competitors/meta_competitors.csv (Title/Desc/H1/H2 паттерны)
- tier: A/B/C
```

### ПРОЦЕСС (7 шагов)

#### 1. Анализ конкурентов

**Источник:** CSV (только indexable 200-страницы)

**Извлекаем:**

- Title length: median (целевой 50-60 chars)
- Description length: median (целевой 150-160 chars)
- H2 themes для semantic entities
- Title ≠ H1 (избегаем дублирования)

#### 2. Distribution Map

**Зоны размещения keywords:**

**Tier B (4500 слов):**

```json
{
  "title": {
    "keywords": ["PRIMARY[0]", "SECONDARY[0]"],
    "format": "[Keyword] | [Modifier] – [Brand]",
    "length": "50-60 chars",
    "rule": "Title ≠ H1"
  },

  "h1": {
    "keyword": "PRIMARY[0]",
    "type": "exact",
    "count": 1,
    "rule": "NO модификаторы, NO бренд"
  },

  "description": {
    "keywords": ["commercial_keyword"],
    "intent": "commercial",
    "format": "Купить + ключ + от X грн + типы + ✅ Доставка 1-2 дня + ☎ Телефон",
    "length": "150-160 chars (допустимо 140-160)",
    "emoji": "2-3"
  },

  "h2_sections": {
    "count": 3,
    "keywords": ["SECONDARY[0]", "SECONDARY[1]", "SECONDARY[2]"],
    "rule": "1 ключ = 1 H2, отражает подинтент",
    "intent_required": 2,
    "examples": ["Как выбрать...", "Какая подходит..."]
  },

  "intro": {
    "length": "100-150 words",
    "paragraphs": 2,
    "keywords": {
      "PRIMARY[0]": 1,
      "SECONDARY[0]": 1
    },
    "rule": "Первые 150 слов, без цен, без брендов"
  },

  "body": {
    "keywords": "распределить остальные PRIMARY/SECONDARY",
    "rule": "max 1 keyword на абзац"
  },

  "faq": {
    "count": "4-5 (tier B)",
    "keywords": "SUPPORTING (8 шт)",
    "rule": "1-2 вопроса с ключами, остальные long-tail"
  }
}
```

#### 3. Density Targets

**Для 4500 слов, Tier B:**

| Type       | Keywords | Density    | Occurrences per keyword | Exact/Partial |
| ---------- | -------- | ---------- | ----------------------- | ------------- |
| PRIMARY    | 3        | 0.11-0.2%  | 5-9                     | 60% / 40%     |
| SECONDARY  | 5        | 0.07-0.13% | 3-6                     | 60% / 40%     |
| SUPPORTING | 8        | 0.02-0.07% | 1-3                     | —             |
| **TOTAL**  | **16**   | **≤2%**    | —                       | —             |

**⚠️ Примечание:** Проценты плотности рассчитываются от количества **слов**, а не символов. При 4500 словах:

- 5 вхождений = 0.11% (5/4500×100)
- 9 вхождений = 0.2% (9/4500×100)
- Общая плотность PRIMARY (3 ключа × 7 avg) = ~21 вхождений / 4500 = 0.47%

**Расчёт:**

```python
density = (occurrences / total_words) × 100

# Пример для PRIMARY:
# keyword: "активная пена"
# occurrences: 7
# total_words: 4500
# density: (7 / 4500) × 100 = 0.156% ✅ (target: 0.11-0.2%)

# Общая плотность PRIMARY (3 keywords):
# PRIMARY[0]: 7 occurrences = 0.156%
# PRIMARY[1]: 6 occurrences = 0.133%
# PRIMARY[2]: 8 occurrences = 0.178%
# Total PRIMARY density: 0.47% ✅ (well below 2% limit)
```

#### 4. Semantic Entities

**НЕ "LSI keywords"** - семантически связанные фразы для топикальной полноты

**Источник:** H2 конкурентов + синонимы

```json
{
  "semantic_entities": [
    {
      "main_keyword": "активная пена",
      "related_phrases": [
        "пена для мойки",
        "бесконтактная пена",
        "пеногенератор",
        "pH-нейтральная пена",
        "концентрат пены",
        "автохимия для мойки"
      ],
      "intent": "informational",
      "usage_zones": ["body", "h2", "faq"]
    }
  ]
}
```

**Важно:** Термин "LSI" используется как ярлык, но механика основана на релевантных темах/сущностях, а не на ранжирующем факторе Google.

#### 5. Coverage Calculation (КЛЮЧЕВОЙ KPI)

**Формула:**

```python
coverage = (keywords_used_in_assigned_zones / total_keywords) × 100
```

**Target zones:**

- Title
- H1
- H2 (по номерам секций)
- Intro
- Body (по секциям)
- FAQ (по вопросам)

**Правило ZONE-BASED:** Keyword засчитывается ТОЛЬКО если использован ≥1 раз в **назначенной** зоне из `distribution_map`

**⚠️ Строгие требования:**

- **PRIMARY[0]:** ОБЯЗАТЕЛЬНО в H1 (exact match) + Title + Intro
- **PRIMARY[1,2]:** ОБЯЗАТЕЛЬНО в Intro + минимум 2 зоны из назначенных
- **SECONDARY:** ОБЯЗАТЕЛЬНО в назначенном H2 (если role="h2") + минимум 1 зона из Body/FAQ
- **SUPPORTING:** Достаточно появления в любой назначенной зоне

**Порог:** ≥70% — **БЛОКЕР!**

**Пример:**

```json
{
  "keyword": "активная пена",
  "type": "PRIMARY",
  "role": "h1",
  "zones": ["h1", "title", "intro", "body-section-1"],
  "validation": {
    "h1": true, // ✅ Exact match found
    "title": true, // ✅ Found
    "intro": true, // ✅ Found in first 150 words
    "body-section-1": true, // ✅ Found
    "status": "PASS" // ✅ All mandatory zones covered
  }
}
```

**Coverage считается:**

```
Total keywords: 16
PRIMARY validated (H1+Title+Intro): 3/3 ✅
SECONDARY validated (assigned H2): 4/5 ⚠️
SUPPORTING validated (any assigned zone): 5/8 ⚠️
Total used in assigned zones: 12
Coverage: (12 / 16) × 100 = 75% ✅ PASS
```

#### 6. Variation Rules

**Exact vs Partial (60/40):**

```json
{
  "keyword": "активная пена",
  "occurrences_total": 7,
  "exact": {
    "count": 4,
    "percentage": 57,
    "forms": ["активная пена"]
  },
  "partial": {
    "count": 3,
    "percentage": 43,
    "forms": ["активной пены", "активную пену", "пена активная"]
  },
  "target_ratio": "60/40",
  "morphology": {
    "lemmatization": true,
    "case_forms": ["именительный", "родительный", "винительный"],
    "word_order_variations": true
  }
}
```

**⚠️ Морфология RU/UK:**

- Подсчет exact/partial учитывает **лемматизацию** (приведение к базовой форме)
- Склонения считаются как partial: "активной пены" → lemma "активный пена"
- Перестановки слов считаются как partial: "пена активная" → "активная пена"
- Для UK: учет специфики украинских флексий (миття/миттям vs мытьё/мытья)

#### 6a. Anti-Clustering Rule

**Правило минимальной дистанции:**

```python
min_distance_between_same_forms = 2-3 sentences
```

**Проверки:**

- Одинаковые формы keyword не должны появляться в соседних предложениях
- При обнаружении clustering → **WARNING** (не FAIL)
- Рекомендация: перефразировать или заменить на partial form

**Пример WARNING:**

```
⚠️ Clustering detected: "активная пена" found in sentence 3 and sentence 4 of Body-Section-1
   Recommendation: Replace one occurrence with "активной пены"
```

#### 7. Intent Mapping

**Типы интентов:**

- **commercial:** "купить", "цена", "заказать"
- **informational:** "как выбрать", "что такое", "виды"
- **navigational:** категория без модификаторов

**Zone-Intent Mapping:**

```json
{
  "title": ["commercial", "navigational"],
  "description": ["commercial"],
  "h1": ["navigational", "informational"],
  "h2": ["informational", "commercial"],
  "intro": ["informational"],
  "body": ["informational", "commercial"],
  "faq": ["informational"]
}
```

### OUTPUT (обновляет JSON IN-PLACE)

**Структура обновленного `{slug}.json`:**

```json
{
  "schema_version": "2.0.0",
  "generated_at": "2025-11-12T14:30:00Z",
  "generator_agent": "keyword-distribution-agent",
  "validator_version": "stage-5-6-analysis-validator@2.0",

  "slug": "aktivnaya-pena",
  "tier": "B",
  "language": "ru",

  "keywords": [
    {
      "text": "активная пена",
      "type": "PRIMARY",
      "role": "h1",
      "intent": "navigational",
      "zones": [
        "h1",
        "title",
        "intro",
        "body-section-1",
        "body-section-3",
        "faq-1"
      ],
      "density_target": "0.16%",
      "occurrences_target": 7,
      "occurrences_exact": 4,
      "occurrences_partial": 3,
      "variations": {
        "exact": ["активная пена"],
        "partial": ["активной пены", "активную пену", "пена активная"]
      },
      "morphology": {
        "lemma": "активный пена",
        "case_forms_allowed": [
          "именительный",
          "родительный",
          "винительный",
          "творительный"
        ]
      }
    }
    // ... остальные 15 keywords
  ],

  "semantic_entities": [
    {
      "main": "активная пена",
      "related": ["пена для мойки", "бесконтактная пена", "пеногенератор"],
      "intent": "informational",
      "usage_zones": ["body", "h2", "faq"]
    }
  ],

  "content_targets": {
    "length_words": 4500,
    "length_chars_no_spaces": "4000-5000",
    "h1_count": 1,
    "h2_count": 3,
    "faq_count": "4-5",
    "intro_words": "100-150",
    "table_required": true,
    "instruction_steps": "5-7",
    "errors_list": "3-4"
  },

  "coverage_calculation": {
    "total_keywords": 16,
    "keywords_used": 12,
    "coverage_percentage": 75,
    "coverage_target": 70,
    "status": "PASS"
  },

  "density_summary": {
    "primary_total": "0.47%",
    "primary_detail": "3 keywords × 7 avg occurrences = 21 / 4500 words",
    "secondary_total": "0.22%",
    "secondary_detail": "5 keywords × 4 avg occurrences = 20 / 4500 words",
    "supporting_total": "0.09%",
    "supporting_detail": "8 keywords × 2 avg occurrences = 16 / 4500 words",
    "total_density": "0.78%",
    "total_density_limit": "≤2%",
    "status": "PASS",
    "calculation_method": "by_words"
  },

  "meta_patterns_from_competitors": {
    "title": {
      "median_length": 52,
      "format_pattern": "[Keyword] для [применение] - [модификатор]",
      "avoid_duplication_with_h1": true
    },
    "description": {
      "median_length": 158,
      "required_elements": ["купить", "цена", "типы", "срок", "телефон"],
      "emoji_count": "2-3"
    }
  },

  "distribution_map": {
    "title": {
      "keywords": ["активная пена для бесконтактной мойки", "купить"],
      "format": "[Keyword] | [Modifier] – [Brand]",
      "example": "Активная пена для мойки авто | Купить в Украине – Ultimate"
    },
    "h1": {
      "keyword": "активная пена",
      "type": "exact",
      "rule": "Title ≠ H1"
    },
    "h2_sections": [
      {
        "h2_number": 1,
        "keyword": "как выбрать активную пену",
        "intent": "informational",
        "semantic_entities": ["pH-нейтральная пена", "концентрат пены"]
      },
      {
        "h2_number": 2,
        "keyword": "виды активной пены",
        "intent": "informational",
        "semantic_entities": ["щелочная пена", "кислотная пена"]
      },
      {
        "h2_number": 3,
        "keyword": "применение активной пены",
        "intent": "informational",
        "semantic_entities": ["пеногенератор", "давление"]
      }
    ],
    "intro": {
      "keywords": ["активная пена", "пена для мойки автомобиля"],
      "length": "100-150 words"
    },
    "faq": {
      "count": "4-5",
      "keywords_with_keys": [
        "какую пену выбрать",
        "можно ли использовать на керамике"
      ],
      "keywords_longtail": [
        "как часто мыть",
        "что делать если остались разводы"
      ]
    }
  },

  "quality_rules": {
    "title_ne_h1": true,
    "only_indexable_200_pages": true,
    "exact_partial_ratio": "60/40",
    "max_keyword_per_paragraph": 1,
    "bold_limit": "≤3 words, 1× per paragraph",
    "paragraph_length": "2-4 sentences (50-80 words)",
    "no_brands": true,
    "currency_only": "грн"
  }
}
```

### ВАЛИДАЦИЯ

**Checks:**

```json
{
  "status": "PASS | WARNING | FAIL",
  "schema_version": "2.0.0",
  "validator_version": "stage-5-6-analysis-validator@2.0",
  "validated_at": "2025-11-12T14:35:00Z",

  "checks": {
    "keywords_distributed": "16/16",
    "coverage": "75% (≥70%)",
    "coverage_zone_based": {
      "PRIMARY_in_H1_Title_Intro": "3/3 ✅",
      "SECONDARY_in_assigned_H2": "4/5 ⚠️",
      "SUPPORTING_in_assigned_zones": "5/8 ⚠️"
    },
    "density_total": "0.78% (≤2%)",
    "density_by_type": {
      "PRIMARY": "0.47% (target 0.11-0.2% per keyword)",
      "SECONDARY": "0.22% (target 0.07-0.13% per keyword)",
      "SUPPORTING": "0.09% (target 0.02-0.07% per keyword)"
    },
    "exact_partial_ratio": "58/42 (target 60/40)",
    "distribution_map_complete": "ALL zones mapped",
    "semantic_entities_extracted": "6 entities",
    "intent_mapping": "ALL keywords tagged",
    "title_ne_h1": "✅ Different",
    "title_contains_PRIMARY": "✅ Yes",
    "h1_exact_PRIMARY": "✅ Yes",
    "intro_contains_PRIMARY_and_SECONDARY": "✅ Yes",
    "h2_contains_assigned_SECONDARY": "⚠️ 4/5 (H2-3 missing SECONDARY[4])",
    "meta_patterns_analyzed": "6 competitors (indexable 200 only)",
    "anti_clustering": "2 warnings (soft)",
    "morphology_enabled": "✅ Lemmatization active"
  },

  "errors": [],

  "warnings": [
    "SECONDARY[4] not found in assigned H2-3 - add to section or reassign zone",
    "PRIMARY[1] только 5 вхождений (target 5-9, low end) - consider adding 1-2 more",
    "Clustering: 'активная пена' in sentences 3,4 of Body-Section-1 - replace with partial form",
    "Coverage 75% близко к threshold (70%) - добавить 1-2 SUPPORTING в FAQ для запаса"
  ],

  "not_used_keywords": [
    {
      "text": "активная пена для мойки машин",
      "type": "SUPPORTING",
      "recommended_zones": ["faq-4", "body-section-2"],
      "reason": "Not found in any assigned zone"
    }
  ]
}
```

**Блокеры (FAIL):**

- ❌ Coverage <70% (zone-based)
- ❌ Density total >2%
- ❌ Distribution map incomplete (missing zones for keywords)
- ❌ No intent mapping
- ❌ PRIMARY[0] NOT in H1 (exact match)
- ❌ PRIMARY[0] NOT in Title
- ❌ PRIMARY NOT in Intro (first 150 words)
- ❌ SECONDARY with role="h2" NOT in assigned H2 section
- ❌ Title = H1 (duplication)
- ❌ Meta patterns from non-indexable pages (must filter 200 OK only)

**Warnings (PASS):**

- ⚠️ Coverage 70-75% (close to threshold, рекомендуется добавить запас)
- ⚠️ Exact/partial ratio вне 55-65% диапазона (target 60/40)
- ⚠️ Некоторые keywords at minimum occurrences (5/9 range)
- ⚠️ Anti-clustering detected (same forms in adjacent sentences)
- ⚠️ SECONDARY not in assigned H2 (but found in other zones)
- ⚠️ Not used keywords list не пуст (рекомендации для добора coverage)

---

## 📋 STAGE 8: CONTENT GENERATION RU

**Агент:** `content-generation-agent`
**Валидатор:** `stage-8-11-content-validator`

### INPUT

```
- categories/{slug}/data/{slug}.json (Technical Brief от Stage 6)
- categories/{slug}/research/perplexity_research.md (ТЗ: темы, структура, FAQ)
```

### ПРОЦЕСС

**Агент читает Technical Brief и ТОЧНО следует:**

#### 1. Мета-данные (из distribution_map)

```yaml
title: "Активная пена для мойки авто | Купить в Украине – Ultimate"
description: "Купить активную пену от 150 грн. Щелочная, нейтральная, кислотная. ✅ Доставка 1-2 дня. ☎ (096) 202-02-32"
h1: "Активная пена"
```

**Правила:**

- Title: keywords из `distribution_map.title`, формат `[Keyword] | [Modifier] – [Brand]`
- Description: формат из rules_2025, keywords из `distribution_map.description`
- H1: exact keyword из `distribution_map.h1`, **Title ≠ H1**

#### 2. Структура (Tier B)

**Intro (100-150 слов):**

- 2 абзаца по 50-80 слов
- Keywords: из `distribution_map.intro`
- Первые 150 слов содержат PRIMARY keyword
- Без цен, без брендов, без AI-клише

**H2 sections (3):**

- Используя `distribution_map.h2_sections`
- Каждый H2 содержит SECONDARY keyword + intent
- Semantic entities из brief
- 2 абзаца по 50-80 слов на секцию

**Table (обязательно для tier B):**

```html
<table border="1" cellpadding="8" cellspacing="0">
  <caption>
    Сравнение типов активной пены
  </caption>
  <thead>
    <tr>
      <th>Тип</th>
      <th>pH</th>
      <th>Применение</th>
    </tr>
  </thead>
  <tbody>
    <!-- 3-5 строк -->
  </tbody>
</table>
```

**Instructions (<ol> 5-7 шагов):**

```html
<li><strong>Название.</strong> Описание 2-3 предложения с цифрами.</li>
```

**Errors (<ul> 3-4 пункта):**

```html
<li><strong>Ошибка.</strong> Объяснение + последствия.</li>
```

**FAQ (4-5 вопросов):**

```html
<h3>Вопрос?</h3>
<p>Ответ 2-4 предложения с SUPPORTING keywords.</p>
```

**E-E-A-T + CTA:**

```html
<p>
  <strong>Команда Ultimate.net.ua</strong> с 2015 года консультирует владельцев
  автомоек...
</p>
<p>
  Консультация: <strong>(096) 202-02-32</strong>. Доставка по Киеву, Харькову...
</p>
<p><em>Обновлено: 12 ноября 2025</em></p>
```

#### 3. Keyword Usage (по зонам из brief)

**Для каждого keyword:**

- Проверяет `zones` (где использовать)
- Соблюдает `occurrences_target` (сколько раз)
- Использует `exact/partial ratio` 60/40
- Берет формы из `variations`
- Max 1 keyword на абзац

**Пример:**

```json
{
  "text": "активная пена",
  "zones": [
    "h1",
    "title",
    "intro",
    "body-section-1",
    "body-section-3",
    "faq-1"
  ],
  "occurrences_target": 7,
  "occurrences_exact": 4,
  "occurrences_partial": 3
}
```

Агент размещает:

- H1: "Активная пена" (exact)
- Title: "Активная пена для мойки..." (exact)
- Intro: "активной пены" (partial)
- Body-section-1: "Активная пена" (exact)
- Body-section-3: "активную пену" (partial)
- FAQ-1: "Активная пена" (exact)

**Итого:** 4 exact + 3 partial = 7 ✅

#### 4. Semantic Entities

**Использование:**

- Добавляет фразы из `semantic_entities` в body/h2/faq
- НЕ считает их как "LSI keywords" для ранжирования
- Использует для топикальной полноты

**Пример:**

```
H2: "Как выбрать активную пену"
Body: "При выборе обращайте внимание на pH-нейтральную пену для регулярной мойки
       или концентрат пены для экономичного использования..."
```

#### 5. Coverage Check (КЛЮЧЕВОЙ KPI)

**Pre-save validation:**

```python
coverage = (keywords_used / total_keywords) × 100
if coverage < 70:
    return ERROR "Coverage below threshold: {coverage}%"
```

**Агент проверяет:**

- Keyword использован ≥1 раз в target zone → засчитывается
- Coverage ≥70% → PASS
- Coverage <70% → FAIL, добавить keywords

#### 6. Quality Rules 2025

**Источник:** `docs/01_RULES_2025_UPDATES.md`

- **Bold:** ≤3 слова подряд, 1× на абзац
- **Абзацы:** 2-4 предложения (50-80 слов)
- **Density:** ориентировочно, естественность важнее процента
- **NO AI-клише:** "В этой статье...", "Давайте разберёмся..."
- **NO бренды:** Koch Chemie, Grass, Chemical Guys
- **Валюта:** только "грн"

### OUTPUT

**Файл:** `categories/{slug}/content/{slug}_ru.md`

**YAML frontmatter:**

```yaml
---
title: "Активная пена для мойки авто | Купить в Украине – Ultimate"
description: "Купить активную пену от 150 грн. Щелочная, нейтральная, кислотная. ✅ Доставка 1-2 дня. ☎ (096) 202-02-32"
h1: "Активная пена"
category: "Активная пена"
language: "ru"
tier: "B"
updated: "2025-11-12"
keywords:
  primary: "активная пена, активная пена для бесконтактной мойки, активная пена для мойки авто"
  secondary: "купить активную пену, бесконтактная пена для мойки авто, ..."
  supporting: "активная пена цена, ..."
content_stats:
  chars_no_spaces: 4350
  words: 920
  coverage: 75%
  density_primary: 0.7%
  density_total: 1.5%
---
```

### ВАЛИДАЦИЯ

**Блокеры (FAIL):**

- ❌ Coverage <70%
- ❌ Length <4000 или >5000 chars (no spaces)
- ❌ Title вне 50-70 chars
- ❌ Description вне 140-170 chars или missing элементы
- ❌ H2 count вне tier range (B: 2-3)
- ❌ FAQ count вне tier range (B: 4-5)
- ❌ Brands mentioned
- ❌ Currency ≠ "грн"
- ❌ Title = H1 (дублирование)

**Warnings (PASS):**

- ⚠️ Coverage 70-75% (close to threshold)
- ⚠️ Density primary >1.5%
- ⚠️ Bold >3 слова
- ⚠️ Абзац >100 слов

---

## 📋 STAGE 9: UKRAINIAN TRANSLATION

**Агент:** `ukrainian-translator`
**Валидатор:** `stage-8-11-content-validator`

### INPUT

```
categories/{slug}/content/{slug}_ru.md
```

### ПРОЦЕСС

**Перевод RU → UK:**

- Сохраняет структуру (H1/H2/таблицы/списки)
- Сохраняет HTML-теги
- Сохраняет контакты (телефон, адреса)
- Использует ЕСТЕСТВЕННЫЙ украинский (НЕ калька!)
- Длина ±5% от RU версии

**Примеры естественного перевода:**

```
RU: "активная пена для бесконтактной мойки"
UK: "активна піна для безконтактного миття" ✅
UK: "активна піна для безконтактної мийки" ❌ (калька)

RU: "купить активную пену"
UK: "купити активну піну" ✅
```

### OUTPUT

```
categories/{slug}/content/{slug}_uk.md
```

### ВАЛИДАЦИЯ

**Checks:**

- ✅ Length chars (no spaces): 4000-5000 ±5%
- ✅ Structure preserved (H2 count = RU count)
- ✅ HTML tags valid
- ✅ NO русизмы ("бесконтактная" → "безконтактного" ✅)
- ✅ Contacts preserved

---

## 📋 STAGE 10: META TAGS GENERATION

**Агент:** `meta-tags-generator`
**Валидатор:** `stage-8-11-content-validator`

### INPUT

```
- categories/{slug}/data/{slug}.json
- categories/{slug}/content/{slug}_ru.md
- categories/{slug}/content/{slug}_uk.md
```

### ПРОЦЕСС

**Генерация RU/UK мета в ОДИН JSON:**

**Rules 2025:**

- Title: 50-60 chars (допустимо 50-70)
- Description: 150-160 chars (допустимо 140-170)
- Description elements: купить + цена + типы + срок + телефон
- Title RU ≠ Title UK (локализация)
- Title ≠ H1 (для RU и UK)

### OUTPUT

**Файл:** `categories/{slug}/meta/{slug}_meta.json`

```json
{
  "ru": {
    "title": "Активная пена для мойки авто | Купить в Украине – Ultimate",
    "title_length": 59,
    "description": "Купить активную пену от 150 грн. Щелочная, нейтральная, кислотная. ✅ Доставка 1-2 дня. ☎ (096) 202-02-32",
    "description_length": 158,
    "h1": "Активная пена",
    "language": "ru",
    "url_slug": "/aktivnaya-pena"
  },
  "uk": {
    "title": "Активна піна для миття авто | Купити в Україні – Ultimate",
    "title_length": 57,
    "description": "Купити активну піну від 150 грн. Лужна, нейтральна, кислотна. ✅ Доставка 1-2 дні. ☎ (096) 202-02-32",
    "description_length": 155,
    "h1": "Активна піна",
    "language": "uk",
    "url_slug": "/ua/aktivna-pina"
  }
}
```

### ВАЛИДАЦИЯ

**Checks:**

- ✅ Title RU: 50-70 chars
- ✅ Title UK: 50-70 chars
- ✅ Description RU: 140-170, elements (купить/цена/срок/телефон)
- ✅ Description UK: 140-170, elements
- ✅ Title RU ≠ H1 RU
- ✅ Title UK ≠ H1 UK
- ✅ Emoji count: 2-3

---

## 📋 STAGE 11: PACKAGING

**Агент:** `packaging-agent`
**Валидатор:** `stage-8-11-content-validator`

### INPUT

```
- categories/{slug}/content/{slug}_ru.md
- categories/{slug}/content/{slug}_uk.md
- categories/{slug}/meta/{slug}_meta.json
- categories/{slug}/data/{slug}.json
```

### ПРОЦЕСС

**Копирование в deliverables:**

1. Копирует контент RU/UK
2. Копирует мета-теги
3. Генерирует README.md (описание категории)
4. Генерирует QUALITY_REPORT.md (метрики)

### OUTPUT (5 файлов)

```
categories/{slug}/deliverables/
  ├── {slug}_ru.md (контент RU)
  ├── {slug}_uk.md (контент UK)
  ├── {slug}_meta.json (мета RU/UK)
  ├── README.md (описание)
  └── QUALITY_REPORT.md (метрики)
```

**QUALITY_REPORT.md:**

```markdown
# Quality Report: Активная пена

## Metrics

- **Coverage:** 75% ✅ (target ≥70%)
- **Density Primary:** 0.7% ✅ (target 0.5-1%)
- **Density Total:** 1.5% ✅ (limit ≤2%)
- **Length RU:** 4350 chars ✅ (target 4000-5000)
- **Length UK:** 4280 chars ✅ (±5% from RU)
- **H2 count:** 3 ✅ (tier B: 2-3)
- **FAQ count:** 5 ✅ (tier B: 4-5)
- **Title length RU:** 59 chars ✅ (50-70)
- **Description length RU:** 158 chars ✅ (140-170)
- **Title ≠ H1:** ✅ Different
- **Brands:** ✅ NONE
- **Currency:** ✅ грн only

## Keywords Used (12/16 = 75%)

### PRIMARY (3/3): ✅

- активная пена: 7× (4 exact, 3 partial)
- активная пена для бесконтактной мойки: 5× (3 exact, 2 partial)
- активная пена для мойки авто: 6× (4 exact, 2 partial)

### SECONDARY (5/5): ✅

- купить активную пену: 4× (description, h2-1, body, cta)
- бесконтактная пена для мойки авто: 3× (body)
- активная пена для мойки автомобиля: 3× (body)
- активная пена для автомойки: 2× (body)
- пена для мойки машин: 2× (faq)

### SUPPORTING (4/8): ⚠️

- активная пена цена: 1× (faq)
- купить активную пену для мойки авто: 2× (body, cta)
- лучшая активная пена: 1× (faq)
- активная пена для ручной мойки: 1× (faq)

**Not used (4):**

- активная пена для мойки машин
- активная пена для мытья машины
- купить активную пену для бесконтактной мойки
- купить активную пену для мойки машин

## Warnings

- SUPPORTING coverage: 50% (4/8) - consider adding 1-2 more in FAQ
```

### ВАЛИДАЦИЯ

**Checks:**

- ✅ 5 files created
- ✅ README valid markdown
- ✅ QUALITY_REPORT complete
- ✅ All content files present

---

## 📊 ПОЛНАЯ ТАБЛИЦА WORKFLOW

| Stage | Агент                    | Валидатор     | Input             | Output             | KPI                            | Status     |
| ----- | ------------------------ | ------------- | ----------------- | ------------------ | ------------------------------ | ---------- |
| 0     | category-init            | —             | slug, tier        | task.json, folders | —                              | ✅ DONE    |
| -3    | url-extraction           | stage-minus-3 | SERP CSV          | urls_raw.txt       | ≥8 URLs, ≥6 domains            | ✅ DONE    |
| -2    | url-preparation          | stage-2       | urls_raw.txt      | urls.txt           | ≥5 URLs, 0 /ua/                | ✅ DONE    |
| 4     | data-preparation         | stage-4       | SERP, CSV         | {slug}.json        | ≥10 keywords                   | ✅ DONE    |
| **6** | **keyword-distribution** | **stage-5-6** | **JSON, ТЗ, CSV** | **JSON + Brief**   | **Coverage ≥70%**              | **→ NEXT** |
| 8     | content-generation       | stage-8-11    | JSON, ТЗ          | \_ru.md            | 4000-5000 chars, coverage ≥70% | PENDING    |
| 9     | ukrainian-translator     | stage-8-11    | \_ru.md           | \_uk.md            | ±5% length                     | PENDING    |
| 10    | meta-tags-generator      | stage-8-11    | JSON, \_ru, \_uk  | \_meta.json        | Title 50-70, Desc 140-170      | PENDING    |
| 11    | packaging                | stage-8-11    | all               | deliverables/      | 5 files                        | PENDING    |

---

## 🎯 КЛЮЧЕВЫЕ KPI (измеримые)

### 1. Coverage (БЛОКЕР)

```
Formula: (keywords_used_in_assigned_zones / total_keywords) × 100
Target: ≥70%
Measurement: Zone-based validation (automatic)

Zone requirements:
- PRIMARY[0]: MUST be in H1 (exact) + Title + Intro
- PRIMARY[1,2]: MUST be in Intro + min 2 assigned zones
- SECONDARY: MUST be in assigned H2 (if role="h2") + min 1 Body/FAQ zone
- SUPPORTING: Any assigned zone
```

### 2. Density (по словам, строгий контроль)

```
PRIMARY: 0.11-0.2% per keyword (5-9 occurrences per 4500 words)
SECONDARY: 0.07-0.13% per keyword (3-6 occurrences)
SUPPORTING: 0.02-0.07% per keyword (1-3 occurrences)
TOTAL: ≤2% (HARD LIMIT)

Calculation method: by_words
Formula: (occurrences / total_words) × 100

Example (4500 words):
- 7 occurrences = 0.156% ✅
- Total PRIMARY (3 keywords × 7 avg) = 21/4500 = 0.47% ✅
```

### 3. Length

```
RU: 4000-5000 chars (no spaces)
UK: ±5% from RU
```

### 4. Meta

```
Title: 50-60 chars (допустимо 50-70)
Description: 150-160 chars (допустимо 140-170)
Title ≠ H1 (обязательно)
```

### 5. Structure (Tier B)

```
H2: 2-3 sections
FAQ: 4-5 questions
Table: REQUIRED
Instructions: 5-7 steps
Errors: 3-4 items
```

---

## 🚀 СЛЕДУЮЩИЙ ШАГ

**Stage 6: Keyword Distribution + Technical Brief**

**Команда для запуска:**

```bash
claude run keyword-distribution-agent \
  --slug aktivnaya-pena \
  --tier B \
  --input categories/aktivnaya-pena/data/aktivnaya-pena.json \
  --research categories/aktivnaya-pena/research/perplexity_research.md \
  --competitors categories/aktivnaya-pena/competitors/meta_competitors.csv
```

**Ожидаемый результат:**

1. ✅ Обновленный JSON с Technical Brief
2. ✅ Distribution Map (где какой keyword)
3. ✅ Density Targets (сколько раз)
4. ✅ Semantic Entities (6+ фраз)
5. ✅ Coverage ≥70%
6. ✅ Validation PASS

**После Stage 6:**
→ Stage 8 (content-generation-agent) получит готовый Technical Brief и сгенерирует контент с coverage ≥70%

---

## 📚 ИСТОЧНИКИ

### Индустриальные практики

- [Clearscope: SEO Content Brief](https://www.clearscope.io/blog/SEO-content-brief)
- [Semrush: Keyword Mapping](https://www.semrush.com/blog/keyword-mapping/)
- [Moz: Keyword Map for SEO](https://moz.com/blog/build-content-keyword-map-for-seo-whiteboard-friday)
- [SEO Monitor: Perfect Content Brief](https://www.seomonitor.com/learning-hub/the-perfect-seo-content-brief-template/)

### LSI Keywords (терминология)

- [Google: No LSI Keywords](https://www.seroundtable.com/google-lsi-keywords-27970.html)
- [Builder Society: LSI Myth](https://www.buildersociety.com/threads/john-mueller-says-there-is-no-such-thing-as-lsi-keywords.4419/)

### Keyword Density 2025

- [Content Hero: Best Keyword Density](https://www.contenthero.co.uk/best-keyword-density-for-seo/)
- [WriteSonic: Keywords Per Page](https://writesonic.com/blog/how-many-seo-keywords-per-page)

### Screaming Frog

- [Configuration Guide](https://www.screamingfrog.co.uk/seo-spider/user-guide/configuration/)
- [Title Same as H1 Issue](https://www.screamingfrog.co.uk/seo-spider/issues/page-titles/same-as-h1/)

### Внутренняя документация

- `docs/01_RULES_2025_UPDATES.md` - SEO правила 2025
- `docs/02_CONTENT_GENERATION.md` - Спецификация генерации
- `docs/06_QUALITY_CHECKLIST.md` - Чеклист качества
- `CLAUDE.md` - Orchestrator инструкции v9.2

---

**Updated:** 2025-11-17 | **Version:** 2.0 | **Status:** PRODUCTION READY
