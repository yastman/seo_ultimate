# Scripts — Утилиты проекта

**[← Назад в корень](../README.md)**

Большинство скриптов запускаются из корневой директории: `python3 scripts/script_name.py`.


---

## Работа с семантикой (CSV → JSON)

| Скрипт | Назначение | Использование |
|--------|------------|---------------|
| `csv_to_readable_md.py` | **Генератор STRUCTURE.md** (с валидацией 100%) | `python3 scripts/csv_to_readable_md.py` |
| `fix_csv_structure.py` | **Чистка CSV** от ложных заголовков | `python3 scripts/fix_csv_structure.py` |
| `parse_semantics_to_json.py` | Парсинг CSV в raw JSON (Legacy) | `python3 scripts/parse_semantics_to_json.py` |
| `compare_raw_clean.py` | Сравнение CSV с _clean.json (Legacy) | `python3 scripts/compare_raw_clean.py` |
| `restore_from_csv.py` | Восстановление _clean.json из CSV | `python3 scripts/restore_from_csv.py` |
| `find_orphan_keywords.py` | Поиск и распределение "сирот" | `python3 scripts/find_orphan_keywords.py` |
| `batch_synonym_cleanup.py` | Массовая чистка синонимов | `python3 scripts/batch_synonym_cleanup.py` |
| `cleanup_misplaced.py` | Очистка неправильно размещенных ключей | `python3 scripts/cleanup_misplaced.py` |

---

## Валидация и Проверка качества (Quality Gate)

| Скрипт | Назначение |
|--------|------------|
| `validate_meta.py` | Проверка мета-тегов (Title, Desc length, H1) |
| `validate_content.py` | Проверка контента (HTML structure, keywords presence) |
| `validate_uk.py` | Проверка UK версии (наличие, соответствие RU) |
| `quality_runner.py` | **Главный раннер**. Запускает все проверки для категории |
| `check_seo_structure.py` | Глобальная проверка структуры SEO проекта |
| `check_simple_v2_md.py` | Проверка Markdown файлов на соответствие v2 |
| `check_water_natasha.py` | Анализ "воды" и стоп-слов (Natasha NLP) |
| `check_ner_brands.py` | Проверка брендов (NER) |
| `deep_check_files.py` | Глубокая проверка целостности файлов |

---

## Анализ и Аудит

| Скрипт | Назначение |
|--------|------------|
| `analyze_category.py` | Полный анализ одной категории |
| `find_duplicates.py` | Поиск дублей ключей между категориями |
| `check_cannibalization.py` | Поиск каннибализации (пересечения интентов) |
| `check_h1_sync.py` | Синхронизация H1 между RU/UK |
| `summarize_clean_keywords.py` | Сводка по чистым ключам |
| `show_keyword_distribution.py` | Статистика распределения ключей |
| `audit_content.py` | Аудит существующего контента |
| `audit_keywords_relevance.py` | Аудит релевантности ключей |

---

## Генерация и Конвертация

| Скрипт | Назначение |
|--------|------------|
| `generate_sql.py` | **Сборка SQL** для деплоя OpenCart |
| `md_to_html.py` | Конвертация Markdown → HTML |
| `batch_generate.py` | Массовая генерация контента (через LLM) |
| `generate_checklists.py` | Генерация чеклистов задач в `tasks/` |

---

## Извлечение данных (Parsers)

| Скрипт | Назначение |
|--------|------------|
| `extract_products.py` | Извлечение товаров с сайта |
| `extract_products_with_desc.py` | Товары с описаниями |
| `find_category_id.py` | Поиск ID категории в БД |
| `extract_competitor_urls_v2.py` | Парсинг URL конкурентов |
| `filter_mega_competitors.py` | Фильтрация конкурентов |
| `mega_url_extract.py` | Извлечение URL из больших списков |

---

## UK версия (Локализация)

| Скрипт | Назначение |
|--------|------------|
| `uk_seed_from_ru.py` | Создание скелета UK версии на основе RU |
| `export_uk_category_texts.py` | Экспорт UK текстов в один файл |

---

## Системные и Утилиты

| Скрипт | Назначение |
|--------|------------|
| `config.py` | **Конфигурация всего проекта** (пути, константы) |
| `seo_utils.py` | Библиотека общих функций SEO |
| `url_filters.py` | Фильтрация URL |
| `setup_all.py` | Инициализация окружения |
| `verify_structural_integrity.py` | Проверка структуры папок |
| `upload_to_db.py` | Прямая загрузка SQL в БД |

---

## Exit Codes

*   `0`: **PASS** — Всё отлично.
*   `1`: **WARNING** — Есть замечания, но не критично.
*   `2`: **FAIL** — Критическая ошибка, деплой запрещен.
