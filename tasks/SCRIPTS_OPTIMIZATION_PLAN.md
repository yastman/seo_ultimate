# План оптимизации скриптов (Scripts Optimization Plan)

**Дата:** 2026-01-14
**Цель:** Привести в порядок папку `scripts/`, уменьшить количество файлов с **58** до **~20**, объединить дублирующую логику.

---

## 1. 🗑️ Legacy (Архив)

Папка `scripts/legacy/`. Сюда уходят скрипты, выполнившие свою историческую миссию.

| Скрипт                             | Статус                                                                          |
| ---------------------------------- | ------------------------------------------------------------------------------- |
| `parse_semantics_to_json.py`       | Legacy (Old CSV parser)                                                         |
| `compare_raw_clean.py`             | Legacy (Diff tool)                                                              |
| `restore_from_csv.py`              | Legacy (Restore tool)                                                           |
| `fix_structure_and_legacy_json.py` | Legacy (Old fix)                                                                |
| `transform_structure_alignment.py` | Legacy (Old One-off migration)                                                  |
| `migrate_keywords.py`              | Legacy (Old migration)                                                          |
| `check_ner_brands.py`              | Low value (Можно перенести в валидатор, но пока в архив как редко используемый) |

---

## 2. 🧩 Аналитика: `analyze.py`

Единый CLI для всех проверок, не блокирующих CI/CD (информационные проверки).
**Команда:** `python scripts/analyze.py <subcommand>`

| Исходные файлы (будут удалены)  | Новая подкоманда                         |
| ------------------------------- | ---------------------------------------- |
| `analyze_category.py`           | `category {slug}`                        |
| `analyze_keyword_duplicates.py` | `duplicates-internal` (внутри категории) |
| `find_duplicates.py`            | `duplicates-cross` (между категориями)   |
| `analyze_keywords_order.py`     | `order`                                  |
| `analyze_keywords_synonyms.py`  | `synonyms`                               |
| `audit_synonyms.py`             | `synonyms --audit`                       |
| `audit_keyword_consistency.py`  | `consistency`                            |
| `analyze_meta_keywords.py`      | `meta-coverage`                          |
| `show_keyword_distribution.py`  | `distribution`                           |
| `check_cannibalization.py`      | `cannibalization`                        |
| `check_semantic_coverage.py`    | `coverage`                               |
| `check_keyword_density.py`      | `density`                                |

---

## 3. ✅ Валидация: `validate.py` (Wrapper)

Обертка над критическими проверками (CI/CD Gates). Сами проверки можно оставить в `modules/validators/` или импортировать.

| Исходные файлы (остаются/переносятся) | Команда обертки                             |
| ------------------------------------- | ------------------------------------------- |
| `validate_meta.py`                    | `python scripts/validate.py meta`           |
| `validate_content.py`                 | `python scripts/validate.py content`        |
| `validate_uk.py`                      | `python scripts/validate.py uk`             |
| `check_h1_sync.py`                    | `python scripts/validate.py h1`             |
| `check_seo_structure.py`              | `python scripts/validate.py structure`      |
| `verify_structural_integrity.py`      | `python scripts/validate.py integrity`      |
| `check_water_natasha.py`              | `python scripts/validate.py content --deep` |
| `verify_test_infra.py`                | `python scripts/validate.py tests`          |

---

## 4. 🔧 Фиксеры: `fix.py`

Инструменты исправления данных.
**Команда:** `python scripts/fix.py <subcommand>`

| Исходные файлы (будут удалены) | Новая подкоманда |
| ------------------------------ | ---------------- |
| `fix_csv_structure.py`         | `csv`            |
| `fix_keywords_order.py`        | `order`          |
| `fix_missing_keywords.py`      | `missing`        |
| `fix_structure_orphans.py`     | `orphans`        |
| `cleanup_misplaced.py`         | `cleanup`        |
| `find_orphan_keywords.py`      | `orphans --find` |
| `update_volume.py`             | `volumes`        |

---

## 5. 🚀 Генераторы и Утилиты (Standalone)

Эти скрипты остаются самостоятельными или объединяются.

| Скрипт                                               | Действие                                  |
| ---------------------------------------------------- | ----------------------------------------- |
| `generate_all_meta.py` + `regenerate_all_meta.py`    | **Объединить** в `generate_meta.py`       |
| `batch_generate.py`                                  | Переименовать в `generate_content.py`     |
| `uk_seed_from_ru.py` + `export_uk_category_texts.py` | Объединить в `manage_uk.py` (seed/export) |
| `synonym_tools.py`                                   | Оставить (или в `fix.py`)                 |
| `csv_to_readable_md.py`                              | Оставить (Core)                           |
| `init_categories_from_checklists.py`                 | Оставить (Core)                           |
| `generate_checklists.py`                             | Оставить                                  |
| `generate_catalog_json.py`                           | Оставить                                  |
| `generate_semantic_review.py`                        | Оставить                                  |
| `generate_sql.py`                                    | Оставить                                  |
| `upload_to_db.py`                                    | Оставить                                  |
| `products.py`                                        | Оставить                                  |
| `competitors.py`                                     | Оставить                                  |
| `md_to_html.py`                                      | Оставить                                  |
| `setup_all.py`                                       | Оставить                                  |
| `extract_categories.py`                              | Оставить                                  |

---

## 6. 🛠️ Shared Modules

Файлы без изменений (библиотеки).

-   `config.py`
-   `seo_utils.py`
-   `url_filters.py`

---

## 7. Структура (Proposed)

```text
scripts/
├── legacy/                  # [NEW]
│   ├── parse_semantics_to_json.py
│   └── ... (см. пункт 1)
├── modules/                 # [NEW]
│   ├── validators/          # Валидаторы
│   ├── config.py
│   ├── seo_utils.py
│   └── url_filters.py
├── analyze.py               # [NEW]
├── fix.py                   # [NEW]
├── validate.py              # [NEW CLI]
├── generate_meta.py         # [MERGED]
├── generate_content.py      # [RENAMED]
├── manage_uk.py             # [NEW]
└── (остальные Standalone из пункта 5)
```

## 4. План действий (Action Plan)

1.  **Phase 1: Cleanup**

    -   Создать `scripts/legacy`.
    -   Переместить туда 4-5 старых скриптов.
    -   Обновить `README.md`.

2.  **Phase 2: Analyze Tool**

    -   Создать `scripts/analyze.py` с `argparse`.
    -   Поочередно перенести логику из `analyze_*.py`, превращая файлы в функции внутри нового скрипта или импортируя их (для начала импортируя).
    -   Удалить старые файлы.

3.  **Phase 3: Fix Tool**

    -   Создать `scripts/fix.py`.
    -   Перенести логику фиксеров.
    -   Удалить старые файлы.

4.  **Phase 4: Meta Merge**
    -   Рефакторинг `generate_all_meta.py` чтобы он включал логику `regenerate`.

---

## Ожидаемый результат

-   Сокращение количества файлов в корне `scripts/` с **~57** до **~15-20**.
-   Понятный CLI интерфейс: `analyze`, `fix`, `generate`, `validate`.
-   Отсутствие дублирования кода.
