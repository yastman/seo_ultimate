# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Ultimate.net.ua — интернет-магазин автохимии и детейлинга.
**Язык ответов:** русский

---

## Pipeline

```
/category-init → /generate-meta → /seo-research → /content-generator → content-reviewer → /uk-content-init → /quality-gate → /deploy
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
| Нужна украинская версия | `/uk-content-init {slug}` | Переводит ключи и контент на украинский |
| Готов к деплою, нужна проверка | `/quality-gate {slug}` | Валидирует все файлы перед публикацией |
| Всё готово, нужно залить на сайт | `/deploy-to-opencart {slug}` | Деплоит мета и контент в OpenCart |

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

**Version:** 34.0
