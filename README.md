# Ultimate.net.ua — SEO Content Pipeline

Автоматизированная система генерации SEO-контента для категорий интернет-магазина автохимии.

**Архитектура:** Skills-based Pipeline
**SSOT (контент):** `docs/CONTENT_GUIDE.md`
**Оркестратор:** `CLAUDE.md`
**Задачи:** `tasks/PIPELINE_STATUS.md`
**Язык:** RU + UK
**Version:** 9.0 (Refactored)

---

## Pipeline

```
CSV → /category-init → /generate-meta → /seo-research → /content-generator → /quality-gate → /deploy-to-opencart
                                                                ↓
                                                    /uk-content-init (parallel)
```

---

## 📂 Структура проекта

```
/
├── CLAUDE.md               # Инструкции для Claude
├── pyproject.toml          # uv project config
├── src/seo_ultimate/       # Python пакет (core, validate, audit, etc.)
│
├── categories/             # Данные категорий (RU)
├── uk/                     # Локализация (UK)
├── scripts/                # Legacy утилиты (миграция в src/)
├── tests/                  # Pytest тесты
├── docs/                   # Документация
└── data/                   # Данные (Raw, Generated)
```

---

## 🚀 Быстрый старт

### Основные команды

```bash
# Установка зависимостей
uv sync

# Тесты
uv run pytest

# Валидация мета-тегов
uv run python -m seo_ultimate.validate.meta categories/avtoshampuni/meta/avtoshampuni_meta.json

# Валидация контента
uv run python -m seo_ultimate.validate.content categories/avtoshampuni/content/avtoshampuni_ru.md
```

### Skills (Slash Commands)

```
/category-init {slug}      → Создать структуру папок
/generate-meta {slug}      → Сгенерировать JSON мета-тегов
/seo-research {slug}       → Провести анализ конкурентов
/content-generator {slug}  → Написать контент (RU)
/uk-content-init {slug}    → Создать UK версию
/quality-gate {slug}       → Полная проверка
/deploy-to-opencart {slug} → SQL дамп
```

---

## 📋 Статус проекта

Актуальный статус всех работ находится в **[`tasks/PIPELINE_STATUS.md`](tasks/PIPELINE_STATUS.md)**.

**Метрики:**

-   **Всего категорий:** 53 RU + 53 UK
-   **Модулей:** 65 (src/seo_ultimate/)
-   **Тестов:** 569

---

## 🛠 Модули `src/seo_ultimate/`

| Пакет | Назначение |
|-------|------------|
| **core/** | Config, keywords, text, SEO utilities |
| **validate/** | Meta, content, density, SEO validators |
| **audit/** | Coverage, H1, keywords consistency |
| **generate/** | SQL, meta, checklists |
| **analyze/** | Category analysis, duplicates |

---

## 📝 Основные правила (2025/2026)

1. **Title:** 50-60 знаков, "Купить" + Бренд в конце.
2. **Desc:** 130-150 знаков, без эмодзи.
3. **Content:** Полезный, без воды, с таблицами и списками.
4. **Git:** Commit often, Atomic commits.

---

**Updated:** 2026-02-04
**Version:** 10.0 (uv + src layout)
