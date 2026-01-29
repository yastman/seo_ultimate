# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Ultimate.net.ua — интернет-магазин автохимии и детейлинга.
**Язык ответов:** русский

---

## Архитектура данных

### Иерархия категорий (53 RU категории)
```
categories/
├── {L1-slug}/                    # Корневая категория (aksessuary, moyka-i-eksterer)
│   ├── data/                     # {L1}_clean.json — семантика L1
│   ├── meta/                     # {L1}_meta.json — мета-теги L1
│   ├── content/                  # {L1}_ru.md, {L1}_uk.md
│   ├── research/                 # RESEARCH_PROMPT.md, RESEARCH_DATA.md
│   └── {L2-slug}/                # Дочерняя категория
│       ├── data/, meta/, content/, research/
│       └── {L3-slug}/            # Листовая категория (товары)
│           └── data/, meta/, content/, research/
```

### Структура polirovka/ (полный пример)
```
polirovka/
├── data/polirovka_clean.json
├── polirovalnye-pasty/
│   └── data/polirovalnye-pasty_clean.json
├── polirovalnye-mashinki/
│   ├── data/polirovalnye-mashinki_clean.json
│   └── akkumulyatornaya/
│       └── data/akkumulyatornaya_clean.json
└── polirovalnye-krugi/
    ├── data/polirovalnye-krugi_clean.json
    └── mekhovye/
        └── data/mekhovye_clean.json
```

### UK структура (зеркало RU)
```
uk/
├── data/
│   └── uk_keywords.json          # База UK ключей (из RU с переводом)
└── categories/
    └── {slug}/
        ├── data/{slug}_clean.json   # UK семантика
        ├── meta/{slug}_meta.json    # UK мета-теги
        ├── content/{slug}_uk.md     # UK контент
        └── research/CONTEXT.md      # Ссылка на RU research
```

### Файлы категории

| Файл | Назначение |
|------|------------|
| `{slug}_clean.json` | Семантическое ядро: keywords, synonyms, micro_intents |
| `{slug}_meta.json` | Title, Description, H1, keywords_in_content |
| `{slug}_ru.md` / `{slug}_uk.md` | Контент (buyer guide формат) |
| `RESEARCH_PROMPT.md` | Промпт для Perplexity Deep Research |
| `RESEARCH_DATA.md` | Результаты research |

---

## Pipeline

```
RU: /category-init → /generate-meta → /seo-research → /content-generator → content-reviewer → /verify-content → /quality-gate → /deploy

UK: /uk-content-init → /uk-generate-meta → /uk-seo-research → /uk-content-generator → uk-content-reviewer → /uk-quality-gate → /uk-deploy
```

---

## Скиллы проекта

### RU Pipeline

| Команда | Описание |
| ------- | -------- |
| `/category-init {slug}` | Создаёт структуру папок и базовые файлы |
| `/generate-meta {slug}` | Генерирует мета-теги на основе семантики |
| `/seo-research {slug}` | Анализирует товары, создаёт RESEARCH_PROMPT.md |
| `/content-generator {slug}` | Генерирует buyer guide контент |
| `content-reviewer {path}` | Проверяет и исправляет контент |
| `/verify-content {slug}` | Ручная верификация перед продакшеном |
| `/quality-gate {slug}` | Валидирует все файлы перед публикацией |
| `/deploy-to-opencart {slug}` | Деплоит мета и контент в OpenCart |

### UK Pipeline

| Команда | Описание |
| ------- | -------- |
| `/uk-content-init {slug}` | Создаёт UK папки и переводит ключи |
| `/uk-generate-meta {slug}` | Генерирует Title/Description/H1 украинские |
| `/uk-seo-research {slug}` | Промпт для Perplexity (UK) |
| `/uk-content-generator {slug}` | Генерирует UK buyer guide |
| `uk-content-reviewer {slug}` | Проверяет UK контент |
| `/uk-quality-gate {slug}` | Финальная проверка UK |
| `/uk-deploy {slug}` | Деплой UK на сайт (language_id=1) |
| `/uk-keywords-export` | Собирает RU ключи, переводит на UK |
| `/uk-keywords-import` | Загружает UK ключи с частотой |

---

## Команды

```bash
# Тесты
pytest                        # Все
pytest -k "test_meta"         # По имени

# Линтинг
ruff check scripts/
ruff format scripts/

# Валидация
python3 scripts/validate_meta.py --all
python3 scripts/validate_content.py categories/{slug}/content/{slug}_ru.md
python3 scripts/check_seo_structure.py categories/{slug}/content/{slug}_ru.md "main keyword"

# Валидация (UK)
python3 scripts/validate_uk.py uk/categories/{slug}/content/{slug}_uk.md
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

# Аудит
python3 scripts/audit_keyword_consistency.py   # Ключи в meta vs clean
python3 scripts/check_h1_sync.py               # Синхронизация H1
```

---

## Семантика RU (Master CSV)

**Источник истины:** `data/ru_semantics_master.csv`

```bash
# Обновление частотности
python3 scripts/merge_to_master.py --excel reports/new.xlsx
python3 scripts/validate_master.py
python3 scripts/sync_semantics.py --apply

# Добавление ключей
# 1. Редактировать data/ru_semantics_master.csv (keyword,volume,category,type,use_in)
# 2. python3 scripts/validate_master.py
# 3. python3 scripts/sync_semantics.py --apply
```

---

## Формат JSON файлов

### _clean.json (семантика)
```json
{
  "id": "aktivnaya-pena",
  "name": "Активная пена",
  "keywords": [{"keyword": "...", "volume": 1000}],
  "synonyms": [{"keyword": "...", "volume": 100, "use_in": "meta_only"}],
  "micro_intents": ["как разводить", "расход"]
}
```

### _meta.json (мета-теги)
```json
{
  "slug": "aktivnaya-pena",
  "language": "ru",
  "meta": {"title": "...", "description": "..."},
  "h1": "...",
  "keywords_in_content": {"primary": [], "secondary": [], "supporting": []}
}
```

---

## Навигация

| Что | Где |
| --- | --- |
| Задачи | `tasks/README.md` |
| SEO-гайд | `docs/CONTENT_GUIDE.md` |
| Данные категорий | `categories/{slug}/` |
| UK ключи | `uk/data/uk_keywords.json` |
| UK синоніми | `.claude/skills/uk-content-generator/references/uk-lsi-synonyms.md` |
| Скрипты | `scripts/` |
| Планы | `docs/plans/` |
| Воркеры | `docs/PARALLEL_WORKERS.md` |
| Логи воркеров | `data/generated/audit-logs/` |

---

## Parallel Claude Workers

См. **[docs/PARALLEL_WORKERS.md](docs/PARALLEL_WORKERS.md)** — полная документация.

### Быстрый старт

```bash
spawn-claude "W1: Описание задачи.

/superpowers:executing-plans docs/plans/YYYY-MM-DD-plan.md

Выполни ТОЛЬКО Task 1.

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

### Ключевые правила

- **1 воркер = 1 набор файлов** — без пересечений
- **Воркеры пишут логи** в `data/generated/audit-logs/W{N}_log.md`
- **Воркеры НЕ коммитят** — коммиты делает оркестратор
- **tmux:** `Ctrl+A, w` — список окон

---

## Правила

- **Context7 MCP** — использовать для документации библиотек/API без запроса
- **python3** — использовать вместо python в командах

---

**Version:** 51.0
