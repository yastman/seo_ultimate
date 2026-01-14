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

| Когда | Команда |
|-------|---------|
| Новая категория | `/category-init {slug}` |
| Мета-теги | `/generate-meta {slug}` |
| Исследование | `/seo-research {slug}` |
| Контент | `/content-generator {slug}` |
| Украинская версия | `/uk-content-init {slug}` |
| Проверка | `/quality-gate {slug}` |
| Деплой | `/deploy-to-opencart {slug}` |

---

## Правила

- **Context7 MCP** — использовать для документации библиотек/API без запроса
- **Git** — коммит после любых изменений файлов

---

## Навигация

| Что | Где |
|-----|-----|
| Статус задач | `tasks/MASTER_CHECKLIST.md` |
| SEO-гайд | `docs/CONTENT_GUIDE.md` |
| Данные категорий | `categories/{slug}/` |
| Скрипты | `scripts/` |

---

**Version:** 29.0
