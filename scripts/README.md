# Scripts — Утилиты проекта

**[← Назад в корень](../README.md)**

Большинство скриптов запускаются из корневой директории: `python3 scripts/script_name.py`.

---

## Работа с семантикой (CSV → JSON)

| Скрипт                       | Назначение                                      | Использование                                                                             |
| ---------------------------- | ----------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `csv_to_readable_md.py`      | **Генератор STRUCTURE.md** (с валидацией 100%)  | `python3 scripts/csv_to_readable_md.py`                                                   |
| `fix_csv_structure.py`       | **Чистка CSV** от ложных заголовков             | `python3 scripts/fix_csv_structure.py`                                                    |
| `parse_semantics_to_json.py` | Парсинг CSV в raw JSON (Legacy)                 | `python3 scripts/parse_semantics_to_json.py`                                              |
| `compare_raw_clean.py`       | Сравнение CSV с \_clean.json (Legacy)           | `python3 scripts/compare_raw_clean.py`                                                    |
| `restore_from_csv.py`        | Восстановление \_clean.json из CSV              | `python3 scripts/restore_from_csv.py`                                                     |
| `find_orphan_keywords.py`    | Поиск и распределение "сирот"                   | `python3 scripts/find_orphan_keywords.py`                                                 |
| `synonym_tools.py`           | **Работа с синонимами** (анализ, отчёт, чистка) | `python3 scripts/synonym_tools.py report` <br> `python3 scripts/synonym_tools.py cleanup` |
| `cleanup_misplaced.py`       | Очистка неправильно размещенных ключей          | `python3 scripts/cleanup_misplaced.py`                                                    |

---

## Валидация и Проверка качества (Quality Gate)

| Скрипт                           | Назначение                                                       |
| -------------------------------- | ---------------------------------------------------------------- |
| `validate_meta.py`               | Проверка мета-тегов (Title, Desc length, H1)                     |
| `validate_content.py`            | **Главный валидатор контента** (HTML structure, keywords, rules) |
| `validate_uk.py`                 | Проверка UK версии (наличие, соответствие RU)                    |
| `check_seo_structure.py`         | Глобальная проверка структуры SEO проекта                        |
| `check_water_natasha.py`         | Анализ "воды" и стоп-слов (Natasha NLP)                          |
| `check_ner_brands.py`            | Проверка брендов (NER)                                           |
| `verify_structural_integrity.py` | Проверка целостности структуры папок проектов                    |

---

## Анализ и Аудит

| Скрипт                         | Назначение                                  |
| ------------------------------ | ------------------------------------------- |
| `analyze_category.py`          | Полный анализ одной категории               |
| `find_duplicates.py`           | Поиск дублей ключей между категориями       |
| `check_cannibalization.py`     | Поиск каннибализации (пересечения интентов) |
| `check_h1_sync.py`             | Синхронизация H1 между RU/UK                |
| `show_keyword_distribution.py` | Статистика распределения ключей             |

---

## Генерация и Конвертация

| Скрипт                   | Назначение                              |
| ------------------------ | --------------------------------------- |
| `generate_sql.py`        | **Сборка SQL** для деплоя OpenCart      |
| `md_to_html.py`          | Конвертация Markdown → HTML             |
| `batch_generate.py`      | Массовая генерация контента (через LLM) |
| `generate_checklists.py` | Генерация чеклистов задач в `tasks/`    |

---

## Извлечение данных (Parsers)

| Скрипт           | Назначение                                        | Использование                                                                                  |
| ---------------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `products.py`    | **Работа с товарами** (список, поиск ID в SQL)    | `python3 scripts/products.py list` <br> `python3 scripts/products.py find "Query"`             |
| `competitors.py` | **Работа с конкурентами** (SERP, Mega, агрегация) | `python3 scripts/competitors.py filter {slug}` <br> `python3 scripts/competitors.py aggregate` |

---

## UK версия (Локализация)

| Скрипт                        | Назначение                              |
| ----------------------------- | --------------------------------------- |
| `uk_seed_from_ru.py`          | Создание скелета UK версии на основе RU |
| `export_uk_category_texts.py` | Экспорт UK текстов в один файл          |

---

## Системные и Утилиты

| Скрипт            | Назначение                                       |
| ----------------- | ------------------------------------------------ |
| `config.py`       | **Конфигурация всего проекта** (пути, константы) |
| `seo_utils.py`    | Библиотека общих функций SEO                     |
| `url_filters.py`  | Фильтрация URL                                   |
| `setup_all.py`    | Инициализация окружения                          |
| `upload_to_db.py` | Прямая загрузка SQL в БД                         |

---

## Exit Codes

-   `0`: **PASS** — Всё отлично.
-   `1`: **WARNING** — Есть замечания, но не критично.
-   `2`: **FAIL** — Критическая ошибка, деплой запрещен.
