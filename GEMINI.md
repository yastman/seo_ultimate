# GEMINI Instructions

## 1. Основные правила
- **Всегда делать коммиты** после каждого изменения (атомарные коммиты).
- **Отвечать на русском языке**.
- **Следовать стилю**: Python скрипты, Pytest для тестов, Markdown для документации.

## 2. О проекте
**Ultimate.net.ua SEO Pipeline** — автоматизированная система генерации контента для интернет-магазина автохимии.
- **Цель**: Генерация SEO-оптимизированного контента (RU + UK) для категорий.
- **Архитектура**: Skills-based Pipeline (последовательное выполнение этапов).
- **SSOT (Источник правды)**: `docs/CONTENT_GUIDE.md`.

## 3. Workflow & Команды (Skills)
Используй эти "слэш-команды" как описание задач:

| Команда | Описание | Скрипты / Действия |
|---------|----------|-------------------|
| `/category-init {slug}` | Создание структуры папок | Создает `categories/{slug}/` и `_clean.json` |
| `/generate-meta {slug}` | Генерация мета-тегов | Генерирует `_meta.json`, требует валидации |
| `/seo-research {slug}` | SEO исследование | Создает `research/RESEARCH_DATA.md` |
| `/content-generator {slug}` | Генерация контента (RU) | Создает `content/{slug}_ru.md` на основе research |
| `/uk-content-init {slug}` | Перевод на UK | Создает `uk/categories/{slug}/` |
| `/quality-gate {slug}` | Финальная проверка | Прогон всех валидаторов |
| `/deploy-to-opencart` | Деплой | SQL скрипты в `deploy/` |

## 4. Ключевые файлы
- **Статус задач**: `tasks/PIPELINE_STATUS.md` (читай перед началом работы).
- **Чеклисты категорий**: `tasks/categories/{slug}.md`.
- **Правила контента**: `docs/CONTENT_GUIDE.md`.
- **Гайд Claude**: `CLAUDE.md` (содержит детальные промпты и правила).

## 5. Валидация (Quality Gates)
Никогда не сдавай задачу без локальной проверки:
- **Meta**: `python scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json`
- **Content**: `python scripts/validate_content.py categories/{slug}/content/{slug}_ru.md "{keyword}" --mode seo`
- **Tests**: `pytest` (если менял логику скриптов).

## 6. SEO Требования (Dec 2025)
- **Title**: 50-60 символов, обязательно "Купить/Купити".
- **Description**: 120-160 символов, без эмодзи.
- **H1**: Не должен содержать "Купить", H1 != Title.
- **Intro**: 30-60 слов.
