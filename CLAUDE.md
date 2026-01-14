# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Ultimate.net.ua — интернет-магазин автохимии и детейлинга.
**Язык ответов:** русский

---

## Pipeline

```
CSV → /category-init → /generate-meta → /seo-research → /content-generator → /uk-content-init → /quality-gate → /deploy
```

---

## Архитектура

### Структура категории

```
categories/{slug}/
├── data/{slug}_clean.json    # Ключевые слова, синонимы, entities, micro_intents
├── meta/{slug}_meta.json     # Title, Description, H1 (RU + UK)
├── content/{slug}_ru.md      # SEO-контент
└── research/
    ├── RESEARCH_PROMPT.md    # Промпт для Perplexity
    └── RESEARCH_DATA.md      # Результат исследования
```

### Формат _clean.json

```json
{
  "id": "slug",
  "name": "Название",
  "type": "category|cluster|filter",
  "parent_id": "parent-slug",
  "keywords": [{"keyword": "...", "volume": 1000}],
  "synonyms": [{"keyword": "...", "volume": 100, "use_in": "meta_only"}],
  "entities": ["бренды", "термины"],
  "micro_intents": ["вопросы пользователей"]
}
```

### Центральные данные

```
data/
├── all_keywords.json       # Все ключи всех категорий
├── catalog_structure.json  # Иерархия каталога
├── category_ids.json       # ID категорий OpenCart
└── generated/PRODUCTS_LIST.md  # Список товаров
```

---

## Команды

### Валидация

```bash
# Meta-теги
python scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json
python scripts/validate_meta.py --all          # Все категории
python scripts/validate_meta.py --all --fix    # Автофикс

# Контент
python scripts/validate_content.py categories/{slug}/content/{slug}_ru.md "{keyword}" --mode seo

# HTML превью
python scripts/md_to_html.py categories/{slug}/content/{slug}_ru.md
```

### Анализ

```bash
# Анализ категории
python scripts/analyze_category.py {slug}

# Дубликаты ключей
python scripts/analyze_keyword_duplicates.py

# Синонимы
python scripts/analyze_keywords_synonyms.py
```

### Тесты

```bash
pytest                           # Все тесты
pytest tests/test_validate.py    # Конкретный файл
pytest -k "test_name"            # По имени
```

---

## Скиллы

| Триггер           | Скилл                        |
| ----------------- | ---------------------------- |
| Новая категория   | `/category-init {slug}`      |
| Мета-теги         | `/generate-meta {slug}`      |
| Исследование      | `/seo-research {slug}`       |
| Контент           | `/content-generator {slug}`  |
| Украинская версия | `/uk-content-init {slug}`    |
| Проверка          | `/quality-gate {slug}`       |
| Деплой            | `/deploy-to-opencart {slug}` |

---

## Система задач

**Главный файл:** `tasks/MASTER_CHECKLIST.md`

```
tasks/
├── active/                 # Активные ТЗ
├── completed/              # Выполненные
├── categories/{slug}.md    # Чеклисты по категориям
└── stages/                 # Описание этапов pipeline
```

---

## Context7 MCP

**Всегда использовать Context7 MCP** для:
- Документации библиотек/API
- Генерации кода
- Настройки и конфигурации

Без явного запроса пользователя.

---

## Git

**После любых изменений файлов — делать коммит.**

```bash
git add <files>
git commit -m "feat/fix/docs: краткое описание"
```

---

**Version:** 28.0
