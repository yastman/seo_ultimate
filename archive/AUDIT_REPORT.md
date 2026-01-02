# Audit Report — SEO Content Pipeline

**Дата:** 2025-12-12
**Автор:** Claude Opus 4.5 (Explore Agent)

---

## Резюме

### Сильные стороны
- Полная валидация (6 checks)
- Хорошее покрытие тестами (~70%)
- Чёткая архитектура Skills → Scripts
- Адвего-калибровка (ADVEGO_MULTIPLIER = 2.4)

### Критические проблемы

| Проблема | Где | Риск |
|----------|-----|------|
| Дублирование кода | normalize_text в 3 местах, tier_requirements в 4 местах | HIGH |
| CSV parser fragility | parse_semantics_to_json.py, extract_competitor_urls_v2.py | HIGH |
| Нет centralized config | Параметры разбросаны по файлам | HIGH |
| Tier targets inconsistency | seo_utils.py vs check_water_natasha.py vs SKILL.md | MEDIUM |
| L3_TO_SLUG incomplete | Только 17 категорий hardcoded | MEDIUM |
| Natasha dependency | NER может быть недоступен | MEDIUM |

---

## Scripts (11 штук)

| Скрипт | Размер | Coverage | Назначение | Проблемы |
|--------|--------|----------|------------|----------|
| quality_runner.py | 29 KB | 10% | Orchestrator 6 checks | Tight coupling |
| check_water_natasha.py | 13 KB | 37% | Water/Nausea Адвего | ADVEGO_MULTIPLIER hardcode |
| check_simple_v2_md.py | 38 KB | 64% | Density/Keywords | JSON path hardcode |
| check_ner_brands.py | 13 KB | 89% | NER/Blacklist | Natasha fallback |
| parse_semantics_to_json.py | 17 KB | 68% | CSV → JSON | L3_TO_SLUG incomplete |
| seo_utils.py | 26 KB | 76% | Utilities | Слишком большой |
| setup_all.py | 10 KB | 40% | Batch init | Дублирование |
| extract_competitor_urls_v2.py | 22 KB | 0% | SERP URLs | Нет тестов |
| filter_mega_competitors.py | 13 KB | ~30% | MEGA filter | Small tests |
| mega_url_extract.py | 10 KB | 0% | Legacy | Не используется |
| url_preparation_filter_and_validate.py | 10 KB | ~50% | URL validation | Slow |

---

## Skills (9 штук)

| Skill | Этап | Назначение | Дублирует |
|-------|------|------------|-----------|
| seo-init | 1 | Папки + task file | setup_all.py |
| seo-data | 2 | Keywords JSON | parse_semantics_to_json.py |
| seo-urls | 3 | SERP URLs | extract_competitor_urls_v2.py |
| seo-competitors | 4 | Meta patterns | filter_mega_competitors.py |
| seo-research | 5 | Perplexity data | — |
| seo-content | 6 | Контент RU | SEO_MASTER.md |
| seo-validate | 7 | 6 checks | quality_runner.py |
| seo-meta | 8 | Title/Description | — |
| seo-package | 9 | Deliverables | — |

---

## Дублирование

### Функции (копипаст)
- `normalize_text()` — 3 места
- `count_words()` — 2 места
- `get_tier_requirements()` — 2 места
- `check_commercial_markers()` — 2 места

### Tier targets (4 места!)
1. SEO_MASTER.md
2. seo_utils.py
3. parse_semantics_to_json.py
4. Каждый SKILL.md

---

## Рекомендации (Priority)

### P1: Критические
1. **Создать config.json** — единый источник параметров
2. **Refactor seo_utils.py** — разбить на модули
3. **CSV schema validation** — pydantic/marshmallow
4. **Structured logging** — logging вместо print()

### P2: Высокие
5. **E2E integration test** — полный workflow
6. **Direct import вместо subprocess** — quality_runner.py
7. **Error handling** — try/except везде
8. **Caching** — HTTP requests, Natasha

### P3: Средние
9. **Gradual validation** — только изменённые файлы
10. **Analytics dashboard** — progress по категориям

### P4: Низкие
11. **Архивировать legacy** — check_lsi_metrics.sh, url_filters.py
12. **Docker image** — reproducible environment

---

## Категории (9 штук)

| Slug | Tier | Keywords | Content | Meta | Status |
|------|------|----------|---------|------|--------|
| aktivnaya-pena | A | 52 ✓ | ✓ | ✓ | DONE |
| dlya-ruchnoy-moyki | A | 58 ✓ | ✓ | ✓ | DONE (keywords wrong) |
| ochistiteli-shin | A | 108 ✓ | — | — | pending |
| glina-i-avtoskraby | A | 56 ✓ | — | — | pending |
| cherniteli-shin | B | 24 ✓ | — | — | pending |
| ochistiteli-diskov | B | 27 ✓ | — | — | pending |
| ochistiteli-stekol | B | 13 ✓ | — | — | pending |
| antimoshka | C | 6 ✓ | — | — | pending |
| antibitum | C | 3 ✓ | — | — | pending |

**Progress:** 2/9 (22%)

---

## Опасные места

1. **extract_competitor_urls_v2.py** — CSV parsing без validation
2. **check_ner_brands.py** — Natasha.NER может быть недоступен
3. **parse_semantics_to_json.py** — L3_TO_SLUG incomplete
4. **quality_runner.py** — Tight coupling
5. **Tier targets** — разные значения в разных файлах
