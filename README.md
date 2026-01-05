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
├── GEMINI.md               # Инструкции для Gemini [UPDATED]
├── README.md               # Этот файл
│
├── docs/                   # Документация проекта
├── tasks/                  # Управление задачами (Active, Completed, Refs)
├── categories/             # Данные категорий (RU)
├── uk/                     # Локализация (UK)
├── scripts/                # Утилиты автоматизации [REFACTORED]
├── data/                   # Данные (Raw, Dumps, Generated)
├── reports/                # Логи и отчеты
├── tests/                  # Pytest тесты
├── archive/                # Устаревшие файлы
└── deploy/                 # SQL скрипты для деплоя
```

---

## 🚀 Быстрый старт

### Основные команды

```bash
# Инициализация категории
python scripts/setup_all.py --slug avtoshampuni

# Генерация мета-тегов
python scripts/validate_meta.py categories/avtoshampuni/meta/avtoshampuni_meta.json

# Валидация контента
python scripts/validate_content.py categories/avtoshampuni/content/avtoshampuni_ru.md

# Генерация HTML
python scripts/md_to_html.py categories/avtoshampuni/content/avtoshampuni_ru.md
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

-   **Всего категорий:** 280+
-   **Готово к деплою:** См. статус
-   **Скриптов:** ~30 (оптимизировано)

---

## 🛠 Инструменты `scripts/`

Полный список в [`scripts/README.md`](scripts/README.md).

| Группа         | Скрипты                                                     |
| -------------- | ----------------------------------------------------------- |
| **Core**       | `seo_utils.py`, `config.py`                                 |
| **Validators** | `validate_meta.py`, `validate_content.py`, `validate_uk.py` |
| **Parsers**    | `csv_to_readable_md.py`, `parse_semantics_to_json.py`       |
| **Tools**      | `synonym_tools.py`, `competitors.py`, `products.py`         |
| **Generators** | `generate_sql.py`, `md_to_html.py`                          |

---

## 📝 Основные правила (2025/2026)

1. **Title:** 50-60 знаков, "Купить" + Бренд в конце.
2. **Desc:** 130-150 знаков, без эмодзи.
3. **Content:** Полезный, без воды, с таблицами и списками.
4. **Git:** Commit often, Atomic commits.

---

**Updated:** 2026-01-05
**Version:** 9.0
