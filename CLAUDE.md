# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Ultimate.net.ua — интернет-магазин автохимии и детейлинга.
**Язык ответов:** русский

---

## Pipeline

```
/category-init → /generate-meta → /seo-research → /content-generator → /uk-content-init → /quality-gate → /deploy
```

---

## Скиллы

| Когда             | Команда                      |
| ----------------- | ---------------------------- |
| Новая категория   | `/category-init {slug}`      |
| Мета-теги         | `/generate-meta {slug}`      |
| Исследование      | `/seo-research {slug}`       |
| Контент           | `/content-generator {slug}`  |
| Украинская версия | `/uk-content-init {slug}`    |
| Проверка          | `/quality-gate {slug}`       |
| Деплой            | `/deploy-to-opencart {slug}` |

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

**Version:** 32.0
