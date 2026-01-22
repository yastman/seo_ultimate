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

---

## Superpowers скиллы

| Когда использовать | Скилл | Описание |
| ------------------ | ----- | -------- |
| Перед созданием фичи/компонента | `superpowers:brainstorming` | Исследует намерения и требования перед кодом |
| Есть спецификация, нужен план | `superpowers:writing-plans` | Создаёт пошаговый план реализации |
| Есть готовый план, нужно выполнить | `superpowers:executing-plans` | Выполняет план с чекпоинтами |
| Перед написанием кода | `superpowers:test-driven-development` | TDD: сначала тесты, потом код |
| Баг, ошибка, неожиданное поведение | `superpowers:systematic-debugging` | Систематический дебаггинг |
| Перед коммитом/PR | `superpowers:verification-before-completion` | Проверяет что всё работает |
| Завершил задачу, нужно ревью | `superpowers:requesting-code-review` | Запрашивает code review |
| Получил фидбек на код | `superpowers:receiving-code-review` | Обрабатывает замечания правильно |
| Нужна изоляция для фичи | `superpowers:using-git-worktrees` | Создаёт изолированный worktree |
| 2+ независимых задачи | `superpowers:dispatching-parallel-agents` | Запускает параллельных агентов |
| Ветка готова к мержу | `superpowers:finishing-a-development-branch` | Завершение работы с веткой |

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
python scripts/check_seo_structure.py categories/{slug}/

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

| Что              | Где                       |
| ---------------- | ------------------------- |
| Задачи (обзор)   | `tasks/README.md`         |
| Research TODO    | `tasks/TODO_RESEARCH.md`  |
| Content TODO     | `tasks/TODO_CONTENT.md`   |
| Аудит категорий  | `tasks/CONTENT_STATUS.md` |
| SEO-гайд         | `docs/CONTENT_GUIDE.md`   |
| Данные категорий | `categories/{slug}/`      |
| Скрипты          | `scripts/`                |

---

**Version:** 38.0
