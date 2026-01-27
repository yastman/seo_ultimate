# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Ultimate.net.ua — интернет-магазин автохимии и детейлинга.
**Язык ответов:** русский

---

## Архитектура данных

### Иерархия категорий
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
| `{slug}_ru.md` | Контент на русском (buyer guide формат) |
| `{slug}_uk.md` | Контент на украинском |
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

| Когда использовать | Команда | Описание |
| ------------------ | ------- | -------- |
| Новая категория нужна в проекте | `/category-init {slug}` | Создаёт структуру папок и базовые файлы |
| Нужны Title/Description/H1 | `/generate-meta {slug}` | Генерирует мета-теги на основе семантики |
| Нужен промпт для Perplexity | `/seo-research {slug}` | Анализирует товары, создаёт RESEARCH_PROMPT.md |
| Нужен текст категории | `/content-generator {slug}` | Генерирует buyer guide контент |
| Нужна ревизия контента | `content-reviewer {path}` | Проверяет и исправляет контент по плану v3.0 |
| Интерактивная проверка | `/verify-content {slug}` | Ручная верификация перед продакшеном |
| Готов к деплою, нужна проверка | `/quality-gate {slug}` | Валидирует все файлы перед публикацией |
| Всё готово, нужно залить на сайт | `/deploy-to-opencart {slug}` | Деплоит мета и контент в OpenCart |

---

## UK Pipeline

| Когда использовать | Команда | Описание |
| ------------------ | ------- | -------- |
| UK структура нужна | `/uk-content-init {slug}` | Создаёт UK папки и переводит ключи |
| UK мета-теги | `/uk-generate-meta {slug}` | Генерирует Title/Description/H1 украинские |
| UK research | `/uk-seo-research {slug}` | Промпт для Perplexity (UK) |
| UK контент | `/uk-content-generator {slug}` | Генерирует UK buyer guide |
| UK ревизия | `uk-content-reviewer {slug}` | Проверяет UK контент |
| UK валидация | `/uk-quality-gate {slug}` | Финальная проверка UK |
| UK деплой | `/uk-deploy {slug}` | Деплой UK на сайт (language_id=1) |
| Экспорт ключей | `/uk-keywords-export` | Собирает RU ключи, переводит на UK |
| Импорт частотности | `/uk-keywords-import` | Загружает UK ключи с частотой |

> **Note:** UK skills synced to v3.0 (January 2026) — повний паритет з RU pipeline.
> - uk-content-generator v3.3: Синхронізовано з RU, entities прибрано, профтерміни з RESEARCH_DATA.md
> - uk-generate-meta v15.0: IRON RULE, Producer/Shop patterns, List/Dict schema support
> - uk-quality-gate v3.0: docs links, keywords_in_content sync, розширена термінологія
> - uk-seo-research v13.0: 11 блоків, спірні твердження, незалежні осі класифікації
> - uk-deploy-to-opencart v3.0: Паритет з RU, language_id=1
> - uk-content-reviewer v2.0: NEW — ревізія UK контенту, UK термінологія check

---

## Superpowers скиллы (14 скиллов)

> **Источник:** [github.com/obra/superpowers](https://github.com/obra/superpowers/tree/main/skills)

### Планирование и дизайн

| Триггер | Скилл | Что делает |
|---------|-------|------------|
| **ПЕРЕД** любой креативной работой (фичи, компоненты, изменения поведения) | `superpowers:brainstorming` | Исследует намерения через вопросы, предлагает 2-3 подхода с trade-offs, валидирует дизайн по частям |
| Есть спецификация/требования, нужен план | `superpowers:writing-plans` | Создаёт bite-sized задачи (2-5 мин), TDD-формат, сохраняет в `docs/plans/` |

### Выполнение планов

| Триггер | Скилл | Что делает |
|---------|-------|------------|
| Есть план, выполнять **в отдельной сессии** с чекпоинтами | `superpowers:executing-plans` | Batch execution (3 задачи → review → следующий batch) |
| Есть план, выполнять **в текущей сессии** | `superpowers:subagent-driven-development` | Fresh subagent на задачу + двухэтапное ревью (spec → quality) |
| 2+ **независимых** задач без shared state | `superpowers:dispatching-parallel-agents` | Параллельные агенты на разные проблемы |

### Разработка и тестирование

| Триггер | Скилл | Что делает |
|---------|-------|------------|
| **ПЕРЕД** написанием любого кода (фича/багфикс) | `superpowers:test-driven-development` | RED-GREEN-REFACTOR: тест → fail → код → pass. **Железное правило:** нет кода без failing test |
| Баг, ошибка теста, неожиданное поведение | `superpowers:systematic-debugging` | 4-фазный анализ root cause. **НЕ фиксить без расследования!** |
| **ПЕРЕД** claim "готово/работает/fixed" | `superpowers:verification-before-completion` | Запустить команды, проверить output. Evidence before assertions |

### Code Review

| Триггер | Скилл | Что делает |
|---------|-------|------------|
| Завершил задачу/фичу, нужно ревью | `superpowers:requesting-code-review` | Pre-review checklist, проактивное ревью |
| Получил фидбек (особенно непонятный/спорный) | `superpowers:receiving-code-review` | Техническая верификация > слепое согласие |

### Git и завершение работы

| Триггер | Скилл | Что делает |
|---------|-------|------------|
| Нужна изоляция для фичи/плана | `superpowers:using-git-worktrees` | Создаёт изолированный worktree, smart directory selection |
| Код готов, тесты проходят, нужно интегрировать | `superpowers:finishing-a-development-branch` | Варианты: merge/PR/cleanup. Verify → Options → Execute |

### Мета-скиллы

| Триггер | Скилл | Что делает |
|---------|-------|------------|
| Нужен новый скилл или редактировать существующий | `superpowers:writing-skills` | TDD для документации: failing test → skill → verify → refactor |
| Понять как работает система скиллов | `superpowers:using-superpowers` | Введение в скиллы, правила discovery |

---

## Утилитарные скиллы

| Когда использовать | Скилл | Описание |
| ------------------ | ----- | -------- |
| Нужен новый скилл | `skill-creator` | Создаёт .skill файлы |
| Нужен специализированный агент | `subagent-creator` | Создаёт конфиг агента |
| Создаю UI/frontend | `frontend-design:frontend-design` | Качественный дизайн интерфейсов |
| Пишу документацию/тексты | `elements-of-style:writing-clearly-and-concisely` | Правила ясного письма |
| Нужно управлять браузером | `superpowers-chrome:browsing` | Chrome DevTools Protocol |
| Интерактивные команды (vim, repl) | `superpowers-lab:using-tmux-for-interactive-commands` | Tmux для интерактивных сессий |

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
python scripts/validate_meta.py --all
python scripts/validate_content.py categories/{slug}/content/{slug}_ru.md
python scripts/validate_uk.py categories/{slug}/content/{slug}_uk.md
python scripts/check_seo_structure.py categories/{slug}/content/{slug}_ru.md "main keyword"
python scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "ключове слово"  # UK auto-detected

# Валидация (UK)
python scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
python scripts/check_h1_sync.py --lang uk
python scripts/check_semantic_coverage.py --lang uk

# Аудит
python scripts/audit_keyword_consistency.py   # Проверка ключей в meta vs clean
python scripts/check_h1_sync.py               # Синхронизация H1 между файлами
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

> **Примечание:** Поле `entities` в `_clean.json` сгенерировано автоматически и не используется для контента. Профессиональные термины (E-E-A-T) берутся из `RESEARCH_DATA.md`.

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

## Правила

- **Context7 MCP** — использовать для документации библиотек/API без запроса

---

## Навигация

| Что              | Где                        |
| ---------------- | -------------------------- |
| Задачи (обзор)   | `tasks/README.md`          |
| Research TODO    | `tasks/TODO_RESEARCH.md`   |
| Content TODO     | `tasks/TODO_CONTENT.md`    |
| UK TODO          | `tasks/TODO_UK_CONTENT.md` |
| Аудит категорий  | `tasks/CONTENT_STATUS.md`  |
| SEO-гайд         | `docs/CONTENT_GUIDE.md`    |
| Данные категорий | `categories/{slug}/`       |
| UK ключи (база)  | `uk/data/uk_keywords.json` |
| UK синоніми        | `.claude/skills/uk-content-generator/references/uk-lsi-synonyms.md` |
| Скрипты          | `scripts/`                 |

---

## Parallel Claude Workers (spawn-claude)

Запуск автономных Claude-агентов в отдельных табах WezTerm для ускорения работы.

### Базовый синтаксис

```bash
spawn-claude "промпт" /path/to/project
```

**ОБЯЗАТЕЛЬНО:** Всегда передавай путь к проекту вторым аргументом при вызове из оркестратора.

### Правила параллелизации

| Правило | Хорошо | Плохо |
|---------|--------|-------|
| 1 воркер = 1 модуль | W1: cache.py, W2: qdrant.py | W1: cache.py строки 1-100, W2: cache.py строки 101-200 |
| Группируй мелкое | W1: metrics + otel + eval | W1: metrics, W2: otel, W3: eval (оверхед) |
| Тесты с кодом | W1: auth.py + test_auth.py | W1: auth.py, W2: test_auth.py |
| Общий файл — только чтение | Все читают план, оркестратор обновляет | Все пишут в один файл |

**Количество воркеров:** Не ограничено — 1 независимый набор файлов = 1 воркер.

### Архитектура

```
┌─────────────────────────────────────────────────────┐
│              ОРКЕСТРАТОР (главный Claude)           │
│  - Создаёт план: docs/plans/YYYY-MM-DD-task.md      │
│  - Дробит на независимые задачи                     │
│  - Запускает spawn-claude для каждого воркера       │
│  - Мониторит прогресс                               │
│  - Финальная проверка                               │
└──────────────────────┬──────────────────────────────┘
                       │
       ┌─────────┬─────┴─────┬─────────┐
       ▼         ▼           ▼         ▼
  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
  │Worker 1│ │Worker 2│ │Worker N│ │Worker M│
  │File: A │ │File: B │ │File: X │ │File: Y │
  └────────┘ └────────┘ └────────┘ └────────┘
```

### Шаблон промпта для воркера

```bash
spawn-claude "Ты Worker N. REQUIRED: используй superpowers:executing-plans

План: docs/plans/YYYY-MM-DD-task.md
Задачи: Tasks X.1-X.N (секция Track N)

Твои файлы (ТОЛЬКО ЭТИ):
- module.py
- test_module.py

Алгоритм:
1. Прочитай план, найди свои задачи
2. Выполни каждый Step по порядку
3. git commit после каждой задачи
4. НЕ ТРОГАЙ файлы других воркеров

Команда проверки: pytest tests/unit/ -q" /path/to/project
```

### Пример: 6 воркеров

```bash
PROJECT="/mnt/c/Users/user/Documents/Сайты/rag-fresh"

# Worker 1: filter_extractor
spawn-claude "W1: fix filter_extractor. Files: telegram_bot/services/filter_extractor.py, tests/unit/services/test_filter_extractor.py" $PROJECT

# Worker 2: metrics + otel + evaluator (сгруппированы — мелкие)
spawn-claude "W2: fix metrics_logger + otel + evaluator. Files: tests/unit/test_metrics_logger.py, test_otel_setup.py, test_evaluator.py" $PROJECT

# Worker 3: cache.py (большой модуль — отдельно)
spawn-claude "W3: write cache.py tests to 80%. Files: telegram_bot/services/cache.py, tests/unit/test_cache_service.py" $PROJECT
```

### Мониторинг

```bash
# Проверить статус задач
grep -c "\[x\]" docs/plans/*-tasks.md

# Проверить git commits от воркеров
git log --oneline -20

# Финальная проверка
pytest tests/unit/ -q
```

**Расположение скрипта:** `/mnt/c/Users/user/bin/spawn-claude`

---

**Version:** 45.0
