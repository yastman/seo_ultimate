# 📚 INDEX — Навигация по проекту

**Ultimate.net.ua — SEO Content Pipeline v5.0**

Быстрая навигация по всем документам проекта.

---

## 🎯 Главные документы

| Файл | Описание | Для кого |
|------|----------|----------|
| **[README.md](README.md)** | **Документация проекта** | Разработчики, пользователи |
| **[CLAUDE.md](CLAUDE.md)** | **Инструкции для AI Orchestrator** | AI Claude (Opus 4.5) |
| **[SEO_MASTER.md](SEO_MASTER.md)** | **Спецификация контента v7.3** | Sub-agents, контент |

---

## 📁 Структура проекта

### `prompts/` — Sub-agent Templates

| Файл | Описание |
|------|----------|
| [prompts/README.md](prompts/README.md) | Документация Sub-agents |
| [prompts/prepare.md](prompts/prepare.md) | PREPARE: init + data + urls |
| [prompts/produce.md](prompts/produce.md) | PRODUCE: content RU + meta |
| [prompts/deliver.md](prompts/deliver.md) | DELIVER: validate + package |

### `categories/` — Category Workspaces

| Файл/Папка | Описание |
|------------|----------|
| [categories/README.md](categories/README.md) | Документация структуры категорий |
| categories/{slug}/ | Workspace конкретной категории |
| └─ data/ | Keywords JSON |
| └─ content/ | Контент MD (RU) |
| └─ meta/ | Meta tags JSON |
| └─ deliverables/ | Финальные файлы |
| └─ .logs/ | Логи выполнения |

### `scripts/` — Python Utilities

| Файл | Описание |
|------|----------|
| [scripts/README.md](scripts/README.md) | Документация скриптов |
| [scripts/setup_all.py](scripts/setup_all.py) | Batch init всех категорий |
| [scripts/parse_semantics_to_json.py](scripts/parse_semantics_to_json.py) | CSV → Keywords JSON |
| [scripts/quality_runner.py](scripts/quality_runner.py) | Оркестратор качества |
| [scripts/check_water_natasha.py](scripts/check_water_natasha.py) | Вода/тошнота |
| [scripts/check_ner_brands.py](scripts/check_ner_brands.py) | NER + blacklist |
| [scripts/filter_mega_competitors.py](scripts/filter_mega_competitors.py) | Фильтрация конкурентов |
| [scripts/extract_competitor_urls_v2.py](scripts/extract_competitor_urls_v2.py) | Извлечение URLs |
| [scripts/seo_utils.py](scripts/seo_utils.py) | Core utilities |

### `data/` — Input Data

| Файл | Описание |
|------|----------|
| data/Структура Ultimate финал - Лист2.csv | Keywords + volumes |
| data/поисковая_выдача_топ_10.csv | SERP URLs (top 10) |
| data/mega/mega_competitors.csv | Scraped competitor data |

### `docs/` — Documentation

| Файл | Описание |
|------|----------|
| docs/SCREAMING_FROG_GUIDE.md | Инструкция по Screaming Frog |
| docs/archive/ | Архив старой документации |

---

## 🎯 Категории (9 штук)

| Slug | Название | Keywords | Tier | Task File | Статус |
|------|----------|----------|------|-----------|--------|
| `aktivnaya-pena` | Активная пена | 52 | A | task_aktivnaya-pena.json | ✅ |
| `dlya-ruchnoy-moyki` | Для ручной мойки | 58 | A | task_dlya-ruchnoy-moyki.json | - |
| `ochistiteli-shin` | Очистители шин | 108 | A | task_ochistiteli-shin.json | - |
| `glina-i-avtoskraby` | Глина и автоскрабы | 56 | A | task_glina-i-avtoskraby.json | - |
| `cherniteli-shin` | Чернители шин | 24 | B | task_cherniteli-shin.json | - |
| `ochistiteli-diskov` | Очистители дисков | 27 | B | task_ochistiteli-diskov.json | - |
| `ochistiteli-stekol` | Очистители стекол | 13 | B | task_ochistiteli-stekol.json | - |
| `antimoshka` | Антимошка | 6 | C | task_antimoshka.json | - |
| `antibitum` | Антибитум | 3 | C | task_antibitum.json | - |

---

## 📋 Команды (v5.0 — Sub-agents)

### Workflow (3 этапа)

```
PREPARE → PRODUCE → DELIVER
```

| Этап | Sub-agent | Что делает |
|------|-----------|------------|
| **PREPARE** | `general-purpose` | Папки + keywords JSON |
| **PRODUCE** | `seo-content-writer` | Контент RU + Meta |
| **DELIVER** | `seo-content-auditor` | Валидация + упаковка |

### Команды Orchestrator

```bash
# Полный цикл (все 3 этапа)
"полный dlya-ruchnoy-moyki tier A"

# Только контент
"контент для dlya-ruchnoy-moyki"

# Проверка
"проверь dlya-ruchnoy-moyki"
```

---

## 🔧 Development

### Python Environment

```bash
# Activate venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

### Quality Checks

```bash
# Полная проверка качества
PYTHONPATH=. python3 scripts/quality_runner.py \
  categories/{slug}/content/{slug}_ru.md \
  "keyword" \
  TIER
```

---

## 📊 Content Standards (v7.3)

| Tier | Chars | H2 | FAQ | Density | Water | Nausea |
|------|-------|----|-----|---------|-------|--------|
| **A** | 2000-2500 | 4-5 | 4-5 | 0.5-1.5% | 40-60% | ≤3.5 |
| **B** | 1500-2000 | 3-4 | 3-5 | 0.5-1.8% | 40-60% | ≤3.5 |
| **C** | 1000-1500 | 2-3 | 3-4 | 0.5-2.0% | 40-65% | ≤3.5 |

**Meta:** Title 50-70, Description 140-170

**Полная спецификация:** → `SEO_MASTER.md`

---

## 🔗 External Links

- [Ultimate.net.ua](https://ultimate.net.ua) — Интернет-магазин
- [Screaming Frog](https://www.screamingfrog.co.uk/seo-spider/) — SEO Spider Tool
- [Perplexity API](https://docs.perplexity.ai/) — Research API

---

## 📝 Архив

| Папка | Описание |
|-------|----------|
| .claude/agents_archive/ | Старые агенты (до v5.0) |
| .claude/skills_archive/ | Старые Skills (до Sub-agents v5.0) |
| docs/archive/ | Старая документация + TZ |

---

**Updated:** 2025-12-11
**Version:** 5.0 (Sub-agents Architecture)
**SEO Standard:** v7.3 (Shop Mode — Buying Guides для E-commerce)
