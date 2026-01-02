# Final Vision — SEO Content Pipeline v2.0

**Автор:** Claude Opus 4.5 (личный аудит)
**Дата:** 2025-12-12
**Статус:** Финальное видение после полного изучения кода

---

## Executive Summary

**Проект:** SEO-контент для ~50 категорий интернет-магазина Ultimate.net.ua (автохимия).

**Цель:** `slug + tier` → `текст RU (~2000 chars) + meta tags`

**Текущее состояние:** 2/9 категорий готовы (22%). Блокер — сломанные keywords JSON.

**Моя оценка:** Проект хорошо спроектирован, но есть 3 критические проблемы, которые нужно решить перед масштабированием.

---

## Аудит скриптов (личная проверка)

### Оценка качества кода

| Скрипт | Строк | Coverage | Качество | Критичность |
|--------|-------|----------|----------|-------------|
| quality_runner.py | 687 | 10% | B | HIGH |
| check_water_natasha.py | 312 | 37% | A- | MEDIUM |
| check_simple_v2_md.py | 977 | 64% | B+ | HIGH |
| check_ner_brands.py | 353 | 89% | A | LOW |
| seo_utils.py | 799 | 76% | A | HIGH |
| parse_semantics_to_json.py | 526 | 68% | C | CRITICAL |
| setup_all.py | 379 | 40% | B | MEDIUM |
| extract_competitor_urls_v2.py | 549 | 0% | D | LOW |

**Общий Coverage:** 35% (нужно 60%+)

### Детальный анализ каждого скрипта

#### 1. quality_runner.py — Оркестратор валидации

**Что делает:** 6 проверок контента (Markdown, Grammar, Water/Nausea, Keywords, NER/Blacklist, Commercial)

**Архитектура:**
```python
class QualityCheck:
    def __init__(self, file_path, keyword, tier, skip_grammar, skip_water, skip_ner):
        self.results = {
            'markdown': {...},
            'grammar': {...},
            'water': {...},
            'keywords': {...},
            'ner': {...},
            'commercial': {...}
        }

    def run_all_checks(self) -> int:  # 0=PASS, 1=WARN, 2=FAIL
```

**Плюсы:**
- Чёткая структура (6 методов = 6 checks)
- Exit codes (0/1/2) для automation
- JSON report для машинного чтения
- Skip-флаги для отдельных проверок

**Минусы:**
- check_simple_v2_md.py вызывается через subprocess (inconsistent)
- Coverage 10% — почти нет тестов
- Tight coupling с другими скриптами

**Рекомендация:** Переписать `check_keyword_density()` на direct import вместо subprocess.

---

#### 2. check_water_natasha.py — Вода и тошнота

**Что делает:** Рассчитывает метрики качества текста по формулам Адвего

**Ключевая формула:**
```python
ADVEGO_MULTIPLIER = 2.4  # Natasha ~22% → Адвего ~52%
water_percent = (water_count / total_words) * 100 * ADVEGO_MULTIPLIER
classic_nausea = math.sqrt(max_frequency)
academic_nausea = (max_freq / total_significant) * 100
```

**Плюсы:**
- Единая точка калибровки (ADVEGO_MULTIPLIER)
- Использует normalize_text из seo_utils (SSOT)
- Хорошо документирован

**Минусы:**
- ADVEGO_MULTIPLIER hardcoded (лучше в config)
- Fallback на локальную normalize_text (дублирование)

**Рекомендация:** Вынести ADVEGO_MULTIPLIER в seo_utils.py как константу.

---

#### 3. check_simple_v2_md.py — Keywords & Density

**Что делает:** Проверка плотности и распределения keywords

**Ключевая логика:**
```python
def check_keyword_density_and_distribution(md_content, data_json_path, word_count):
    # Читает keywords из JSON
    # Считает exact и partial вхождения
    # Проверяет density <= 2%, coverage >= 50%
    # Возвращает детальный отчёт
```

**Плюсы:**
- Детальный JSON report (_validation.json)
- Поддержка YAML front matter
- Zone-based coverage

**Минусы:**
- Зависит от корректного keywords JSON (который сломан!)
- Большой файл (977 строк) — можно разбить

**Рекомендация:** Модульный рефакторинг не критичен, но желателен.

---

#### 4. check_ner_brands.py — Blacklist & NER

**Что делает:** Находит запрещённые сущности (бренды, города, AI-fluff)

**Blacklists:**
```python
BRAND_BLACKLIST = {'koch chemie', 'grass', 'karcher', ...}  # 36 брендов
CITY_BLACKLIST = {'київ', 'киев', 'харків', ...}  # 30+ городов
AI_FLUFF_PATTERNS = [r'в этой статье', r'давайте разберёмся', ...]  # 19 паттернов
STRICT_PHRASES = ["в современном мире", ...]  # FAIL trigger
```

**Плюсы:**
- Coverage 89% — лучший покрытый скрипт
- NER через Natasha (опционально)
- Чёткое разделение WARNING vs FAIL

**Минусы:**
- Blacklists hardcoded (лучше в external file)
- NER медленный (но опциональный)

**Рекомендация:** Оставить как есть — работает хорошо.

---

#### 5. seo_utils.py — SSOT утилит

**Что делает:** Единый источник правды для SEO функций

**Ключевые функции:**
```python
def normalize_text(md: str) -> str  # Единая нормализация
def count_chars_no_spaces(content: str) -> int  # Символы без пробелов
def count_words(text: str) -> int  # Количество слов
def get_tier_requirements(tier: str) -> Dict  # Targets по tier (SSOT!)
def check_commercial_markers(text: str) -> Dict  # Коммерческие слова
```

**Плюсы:**
- SSOT для tier requirements
- Единая normalize_text для всех скриптов
- URL validation utilities
- Хорошо документирован

**Минусы:**
- 799 строк — можно разбить на модули
- Некоторые функции не используются (URL validation)

**Рекомендация:** Это ядро системы. Не трогать без необходимости.

---

#### 6. parse_semantics_to_json.py — КРИТИЧЕСКИЙ ПРОБЛЕМНЫЙ СКРИПТ

**Что делает:** Парсит CSV семантики → JSON для валидатора

**Проблема #1 — Hardcoded mapping:**
```python
L3_TO_SLUG = {
    "Активная пена": "aktivnaya-pena",
    "Для ручной мойки": "dlya-ruchnoy-moyki",
    # ... только 17 категорий из ~50!
}
```

**Проблема #2 — Неправильный CSV parsing:**
```
CSV структура:
L3: Для ручной мойки,5,    ← только 5 keywords
  автошампунь для мойки,,390
L2: Средства для стекол,59,  ← это L2, НЕ L3!
  Омыватель,35,                ← subsection header (пропускается)
  омыватель стекла зимний,,1000 ← keywords идут в НЕПРАВИЛЬНЫЙ L3!
```

**Результат:**
- `dlya-ruchnoy-moyki.json` содержит keywords про омыватели (WRONG!)
- `ochistiteli-shin.json` содержит keywords про обезжириватели (WRONG!)
- Только `aktivnaya-pena.json` корректен

**Рекомендация:** Это BLOCKER. Нужно либо:
1. Исправить парсер (сложно — CSV структура нестандартная)
2. Ручной ввод keywords (быстро для 9 категорий)
3. Новый чистый CSV (идеально для ~50 категорий)

---

#### 7. setup_all.py — Batch init

**Что делает:** Инициализирует все категории из CSV

**Логика:**
```python
def auto_detect_tier(keywords_count: int) -> str:
    if keywords_count > 30: return "A"
    elif keywords_count >= 10: return "B"
    else: return "C"
```

**Плюсы:**
- Auto-tier detection
- Dry-run mode
- Force overwrite

**Минусы:**
- Зависит от parse_semantics_to_json (который сломан)
- Дублирует L3_TO_SLUG mapping

**Рекомендация:** Работает, но бесполезен пока не исправлен parse_semantics_to_json.

---

#### 8. extract_competitor_urls_v2.py — Извлечение конкурентов

**Что делает:** SERP топ-10 → URLs для Screaming Frog

**Плюсы:**
- CLI с параметрами (--slug, --top-n, --max-urls)
- Blacklist доменов
- Score ranking (частота × позиция)

**Минусы:**
- 0% coverage — НЕТ ТЕСТОВ ВООБЩЕ
- Зависит от CSV файлов с SERP данными
- Не используется в основном workflow

**Рекомендация:** Низкий приоритет. Тесты можно добавить позже.

---

## Критические проблемы (3 штуки)

### P1: Keywords JSON сломаны

**Симптом:** 7 из 9 categories имеют неправильные keywords.

**Причина:** parse_semantics_to_json.py неправильно обрабатывает L1/L2/L3 иерархию в CSV.

**Решение (3 варианта):**

| Вариант | Сложность | Время | Качество |
|---------|-----------|-------|----------|
| A: Ручной ввод | Низкая | 30 мин/категория | Среднее |
| B: Исправить парсер | Высокая | 4-8 часов | Высокое |
| C: Новый CSV | Средняя | 2-3 часа | Отличное |

**Моя рекомендация:** Вариант A для 9 текущих категорий, вариант C для ~50 будущих.

### P2: Test Coverage 35%

**Симптом:** quality_runner.py имеет 10% coverage, extract_competitor_urls_v2.py — 0%.

**Риск:** Регрессии при изменениях, нет уверенности в корректности.

**Решение:**
1. Написать тесты для quality_runner.py (target: 50%)
2. Написать базовые тесты для extract_competitor_urls_v2.py (target: 30%)
3. Общий target: 60%

### P3: Дублирование кода

**Симптом:**
- normalize_text() — 3 места (seo_utils + fallbacks в 2 скриптах)
- tier_requirements — разные значения в разных файлах
- ADVEGO_MULTIPLIER — hardcoded в check_water_natasha.py

**Решение:**
1. Убрать fallbacks — обязательный import из seo_utils
2. Добавить constants в seo_utils (ADVEGO_MULTIPLIER, etc.)
3. Единый config.json для параметров

---

## Моё видение правильного pipeline

### Архитектура (без оверхеда)

```
User: "контент для {slug}"
         │
         ▼
┌─────────────────────────┐
│  Оркестратор (Opus)     │
│  1. Читает task.md      │
│  2. Проверяет keywords  │
│  3. Делегирует          │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Skills (существующие)  │
│  seo-content-writer     │
│  seo-validate           │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Валидация              │
│  quality_runner.py      │
└─────────────────────────┘
         │
         ▼
    PASS/FAIL → Результат
```

### Файлы (минимум)

```
/
├── SEO_MASTER.md           # Спецификация (SSOT)
├── task.md                 # Текущие задачи
├── CLAUDE.md               # Инструкции для Claude
│
├── categories/{slug}/
│   ├── data/{slug}.json    # Keywords (ПРОВЕРЕННЫЕ!)
│   ├── content/{slug}_ru.md # Контент
│   └── meta/{slug}_meta.json
│
├── scripts/
│   ├── quality_runner.py   # Оркестратор валидации
│   ├── check_water_natasha.py
│   ├── check_simple_v2_md.py
│   ├── check_ner_brands.py
│   └── seo_utils.py        # SSOT утилит
│
└── tests/
    └── test_*.py           # Тесты (60%+ coverage)
```

### Workflow (3 шага)

```
1. PREPARE (если нужно)
   └── Проверить keywords JSON → fix if wrong

2. PRODUCE
   ├── Skill: seo-content-writer
   └── Output: {slug}_ru.md + meta.json

3. VALIDATE
   ├── quality_runner.py (5 checks)
   └── Если FAIL → исправить → повтор
```

---

## План действий (Roadmap)

### Фаза 1: Разблокировать pipeline (TODAY)

**Задача:** Исправить keywords для 7 категорий

| Категория | Текущий keywords | Действие |
|-----------|------------------|----------|
| dlya-ruchnoy-moyki | WRONG (омыватели) | Manual fix |
| ochistiteli-shin | WRONG (обезжириватель) | Manual fix |
| glina-i-avtoskraby | Не проверено | Check + fix |
| cherniteli-shin | Не проверено | Check + fix |
| ochistiteli-diskov | Не проверено | Check + fix |
| ochistiteli-stekol | Не проверено | Check + fix |
| antimoshka | Не проверено | Check + fix |
| antibitum | Не проверено | Check + fix |
| aktivnaya-pena | OK | No action |

**Время:** 2-3 часа (ручная проверка + fix)

### Фаза 2: Тесты для качества (NEXT)

**Задача:** Coverage 35% → 60%

| Скрипт | До | После | Тесты нужны |
|--------|-----|-------|-------------|
| quality_runner.py | 10% | 50% | 15-20 |
| check_water_natasha.py | 37% | 60% | 5-8 |
| extract_competitor_urls_v2.py | 0% | 30% | 5-7 |

**Время:** 4-6 часов

### Фаза 3: Контент для 9 категорий

**Задача:** Завершить 9 категорий

| Slug | Tier | Status | Приоритет |
|------|------|--------|-----------|
| aktivnaya-pena | A | DONE | — |
| dlya-ruchnoy-moyki | A | pending | 1 |
| ochistiteli-shin | A | pending | 2 |
| glina-i-avtoskraby | A | pending | 3 |
| cherniteli-shin | B | pending | 4 |
| ochistiteli-diskov | B | pending | 5 |
| ochistiteli-stekol | B | pending | 6 |
| antimoshka | C | pending | 7 |
| antibitum | C | pending | 8 |

**Время:** ~30 мин/категория × 8 = 4 часа

### Фаза 4: Масштабирование (~50 категорий)

**Задача:** Подготовка к остальным категориям

1. Создать новый чистый CSV с правильной структурой
2. Исправить parse_semantics_to_json.py (или заменить)
3. Автоматизировать setup для batch processing

**Время:** 4-8 часов

---

## Чек-лист для начала работы

### Перед генерацией контента

- [ ] Keywords JSON проверен и корректен
- [ ] pytest tests/ проходит без ошибок
- [ ] task.md обновлён

### После генерации контента

- [ ] quality_runner.py даёт PASS (exit 0)
- [ ] Water 40-60%
- [ ] Nausea ≤3.5
- [ ] Commercial markers ≥ min
- [ ] task.md обновлён

### Финал

- [ ] Файлы в categories/{slug}/
- [ ] Meta JSON создан
- [ ] Результат записан в task.md

---

## Вывод

**Что хорошо:**
- SEO_MASTER.md — отличная спецификация
- seo_utils.py — хороший SSOT
- Skills работают — используйте их
- Валидация (5 checks) — полная и корректная

**Что нужно исправить:**
1. Keywords JSON (BLOCKER)
2. Test coverage (35% → 60%)
3. Дублирование кода (minor)

**Что НЕ нужно:**
- Удалять skills (они работают)
- Переписывать всё с нуля
- Создавать новые файлы документации

**Следующий шаг:**
1. Проверить и исправить keywords для 7 категорий
2. Сгенерировать контент для dlya-ruchnoy-moyki
3. Валидировать до PASS

---

**Version:** 2.0
**Author:** Claude Opus 4.5 (personal audit)
**Date:** 2025-12-12
