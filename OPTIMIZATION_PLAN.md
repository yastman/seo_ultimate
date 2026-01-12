# План оптимизации проекта Ultimate.net.ua

**Цель:** повысить воспроизводимость, качество и скорость пайплайна SEO‑контента.
**Область:** скрипты, пайплайн, QA, деплой, управление данными.
**Горизонт:** 4–6 недель (по 1–2 итерации в неделю).

---

## Принципы оптимизации (чтобы не “сломать прод”)

- **SSOT:** конфиги/пути/правила качества живут в `scripts/config.py`, в коде не дублируются.
- **Совместимость схем:** `_clean.json` читается через адаптер (поддержка `keywords` как dict и list) до полной миграции.
- **Один конвертер MD→HTML:** одна реализация (и один набор тестов) вместо 3 разных.
- **Безопасность по умолчанию:** любые действия с БД/SQL — dry‑run по умолчанию, секреты только через env.
- **Депрекация вместо удаления:** устаревшие скрипты помечаем как deprecated и выводим предупреждение, но не ломаем поток работы.

---

## Срез проекта (крупные части и “вес”)

- Контент/данные: `categories/` (~0.8 MB), `uk/` (~0.4 MB), `data/` (~64 MB).
- Инструменты: `scripts/` (~1.8 MB), `docs/` (~60 KB), `deploy/` (~0.4 MB), `.claude/` (~9 MB).
- Тесты: `tests/` (~3.1 MB) + набор “плоских” папок вида `testsunit/`, `testsintegration/` и т.п. (важно проверить, что это не дубликаты/артефакты экспорта).
- Тяжёлые каталоги, которые мешают переносимости/скорости: `.venv/` (~592 MB), `.github_repos/` (~69 MB), `archive/` (~7.4 MB).

**Рекомендация:** если репозиторий планируется шарить/деплоить/гонять в CI — вынести `.venv/` и любые “зеркала репозиториев” (`.github_repos/`) из VCS, оставить только `requirements*.txt`/`pyproject.toml`.

---

## Карта `scripts/` (не архив, укрупнённо)

- Инициализация/структура: `setup_all.py`, `init_categories_from_checklists.py`, `restore_from_csv.py`, `parse_semantics_to_json.py`, `csv_to_readable_md.py`, `transform_structure_alignment.py`, `fix_structure_*.py`.
- Генерация/пакетная обработка: `batch_generate.py`, `generate_all_meta.py`, `regenerate_all_meta.py`, `products.py`, `generate_sql.py`, `md_to_html.py`, `upload_to_db.py`.
- QA/валидация: `validate_meta.py`, `validate_content.py`, `validate_uk.py`, `check_h1_sync.py`, `check_seo_structure.py`, `verify_structural_integrity.py`, `check_*` (water/natasha/NER/coverage/cannibalization).
- Аналитика/аудит: `audit_*`, `analyze_*`, `find_*`, `compare_raw_clean.py`, `show_keyword_distribution.py`.
- Базовые утилиты: `config.py`, `seo_utils.py`, `synonym_tools.py`, `url_filters.py`, `scripts/utils/*`.

---

## Что уже выявлено при инвентаризации `scripts/` (не архив)

- Абсолютные Windows‑пути ломают переносимость и запуск в Linux/CI: `scripts/audit_keyword_consistency.py`, `scripts/check_cannibalization.py`, `scripts/check_semantic_coverage.py`, `scripts/fix_missing_keywords.py`, `scripts/generate_semantic_review.py`, `scripts/migrate_keywords.py`.
- Несогласованный SSOT CSV: часть скриптов читает `Структура _Ultimate.csv`, часть — `data/Структура  Ultimate финал - Лист2.csv` (риск “работать не с тем источником”).
- Дрифт схемы `_clean.json` (критично для пайплайна):
  - `categories/*/*_clean.json`: **61** файлов с `keywords: [ ... ]` (list), **1** файл с `keywords: {primary/...}` (dict).
  - `uk/categories/*/*_clean.json`: **34** файлов с `keywords: {primary/...}` (dict).
  - Следствие: часть скриптов/тестов ожидают dict‑схему (напр. `scripts/analyze_category.py`), но данные в RU в основном list‑схемы.
- Дубли логики:
  - `scripts/seo_utils.py` и `scripts/utils/text.py` (почти одно и то же).
  - `scripts/url_filters.py` и `scripts/utils/url.py` (перекрывающиеся функции).
  - 3 реализации MD→HTML: `scripts/md_to_html.py`, `scripts/upload_to_db.py`, `scripts/generate_sql.py`.
- Частичная незавершенность: `scripts/competitors.py extract_from_serp()` — заглушка.
- Небольшие баги/мёртвый код: недостижимые `return` в `scripts/url_filters.py`, лишний `return` в `scripts/fix_csv_structure.py`.
- Несогласованность фактических статусов и файлов: часть `categories/*/content/*_ru.md` — placeholders (например, `categories/avtoshampuni/content/avtoshampuni_ru.md`), при этом мета/SQL могут быть “готовыми”.

---

## 1) Быстрые улучшения (1 неделя)

- Безопасность: вынести креды БД и параметры окружения в `.env` + пример `.env.example`.
- Безопасность репозитория: добавить `.gitignore` для `.env`, включить минимальный “secret scan” (хотя бы `rg`-проверка в CI).
- Явные зависимости QA: документировать и проверять наличие NLP/MD/grammar библиотек до запуска валидаторов.
- Унифицировать запуск: добавить `make`/`task` с типовыми командами (setup, validate, test, deploy-dry-run).
- Устранить “тихие” пропуски проверок: валидатор должен явно предупреждать при отключенных модулях.
- Унифицировать пути и SSOT: убрать абсолютные Windows-пути, привести все скрипты к `scripts/config.py` и одному CSV.
- Убрать дубли утилит: свести `scripts/seo_utils.py` и `scripts/utils/text.py` к одному модулю, так же `scripts/url_filters.py` и `scripts/utils/url.py`.
- Починить “мелкие” баги в утилитах (недостижимый код/лишние `return`) и прогнать unit-тесты.
- Привести в порядок “готовность” контента: различать **placeholder** и реальный контент (автоматическая проверка перед сменой статуса в `tasks/PIPELINE_STATUS.md`).

**Критерии:**
- Нет паролей в репозитории.
- Валидация сообщает о неполной проверке.
- Все скрипты работают с относительными путями и единым SSOT CSV.
- “Готово” в статусах соответствует реальным файлам (не placeholder).

---

## 2) Качество и воспроизводимость (1–2 недели)

- CI‑профиль: `pytest`, `ruff`, `mypy` (минимум для `scripts/`).
- Минимальный smoke‑pipeline: запуск `validate_meta.py`, `validate_content.py` на fixtures.
- Зафиксировать SSOT пути и формат CSV (именование без пробелов/кириллицы) + документация миграции.
- Нормализовать схему `_clean.json`:
  - определить целевую схему (предпочтительно dict: `primary/secondary/supporting/commercial`),
  - добавить слой совместимости для скриптов, которые ожидают list,
  - запретить “частичные” записи (валидация схемы до дальнейших шагов).
- Логирование: перевести ключевые CLI на `logging` + опция `--json` для машинного вывода (для батч‑потока).
- Синхронизировать тестовые фикстуры с реальными данными (сейчас tests могут проверять устаревшую схему и не ловить регрессии в прод‑данных).

**Критерии:**
- Тесты и линт проходят локально и в CI.
- SSOT файл имеет стабильное имя.
- Любой `_clean.json` проходит проверку схемы.

---

## 3) Оптимизация пайплайна контента (1–2 недели)

- Добавить “жесткий” режим quality‑gate: без NLP зависимостей — статус WARNING/FAIL.
- Протоколировать все метрики в `reports/` (water, nausea, coverage, blacklist).
- Автоматизировать batch‑генерацию с контрольными точками и отчетом прогресса.
- Унифицировать MD→HTML (выбрать 1 реализацию, покрыть тестами, остальные пометить deprecated).
- Уточнить границы ответственности:
  - `validate_content.py` — качество текста и структура,
  - `generate_sql.py`/деплой — только преобразование и упаковка.

**Критерии:**
- Любой запуск quality‑gate дает полный отчет и воспроизводимую метрику.
- Один конвертер MD→HTML используется в пайплайне и покрыт тестами.

---

## 4) UK‑локализация (1 неделя)

- Сформировать единый пайплайн RU→UK (seed → meta → content → QA).
- Валидация согласованности H1/Title/ключей между RU и UK.
- Правила терминологии: закрепить “запрещенные RU‑маркеры” и допустимые англ. термины (один раз в body, не в заголовках).

**Критерии:**
- Минимум 10 UK категорий проходят полный quality‑gate без ручных фиксов.

---

## 5) Деплой и безопасность (1 неделя)

- Перевести `upload_to_db.py` на конфиг/ENV, добавить dry‑run по умолчанию.
- Добавить проверку целостности SQL до выгрузки (lint/preview).
- Развести “генерацию SQL” и “применение SQL”: отдельные команды/скрипты, чтобы случайно не применить.
- Для Docker: вынести пароли из `docker-compose.yml` в `.env` (через `env_file:`) и дать пример.
- Привести `docker-compose.yml` к реальным путям дампа (сейчас дамп лежит в `data/dumps/ultimate_net_ua_backup.sql`, а compose ожидает файл в корне).
- Выправить документацию деплоя: `deploy/README.md` содержит потенциально неверное соответствие `language_id` (в проекте RU=3, UK=1; это уже отражено в SQL и `scripts/upload_to_db.py`).

**Критерии:**
- Деплой без ручных правок SQL.
- Ошибки БД ловятся до применения.
- Любая команда “apply” требует явного подтверждения флагом (например, `--apply`).

---

## Метрики прогресса

- % категорий с валидным контентом (RU/UK).
- Количество ошибок quality‑gate на 1 категорию.
- Время полного пайплайна на 1 категорию (мин).
- Доля автогенерации без ручного редактирования.
- Доля скриптов, работающих через `scripts/config.py` (цель: 100%).

---

## Риски

- Неполные NLP зависимости → ложные PASS.
- Дубли логики в `archive/` → работа с устаревшей версией.
- Несогласованность SSOT (CSV/JSON) → смещения в ключах и мета.
- Расхождение схем `_clean.json` (list vs dict) → “тихие” пропуски в обновлении volume/keywords.
- Несколько MD→HTML конвертеров → различия в разметке между preview/SQL/DB.

---

## Следующие шаги (предложение)

1. Зафиксировать `.env` и удалить креды из кода.
2. Добавить цель `make qa` и smoke‑тесты.
3. Привести SSOT CSV к нейтральному имени и обновить ссылки.

---

## Приложение: приоритетные рефакторинги по скриптам

| Скрипт | Проблема | Действие |
|---|---|---|
| `scripts/migrate_keywords.py` | абсолютные пути, привязка к Windows | перевести на `Path` от `PROJECT_ROOT`, брать CSV из `scripts/config.py` |
| `scripts/check_cannibalization.py` | абсолютные пути в `__main__` | перейти на относительные пути + argparse |
| `scripts/check_semantic_coverage.py` | абсолютные пути | перейти на `PROJECT_ROOT` + `scripts/config.py` |
| `scripts/generate_semantic_review.py` | абсолютные пути | перейти на `PROJECT_ROOT` + `scripts/config.py` |
| `scripts/fix_missing_keywords.py` | абсолютные пути + ручная карта cluster→slug | сделать режим “по slug” + чтение из `STRUCTURE.md` без хардкода заголовков |
| `scripts/url_filters.py` | недостижимый код, дубли с `scripts/utils/url.py` | оставить один модуль, второй deprecated |
| `scripts/utils/text.py` | дубли с `scripts/seo_utils.py` | оставить один модуль, второй deprecated |
| `scripts/md_to_html.py` и `scripts/upload_to_db.py` | ручной конвертер MD→HTML, риск несовпадений | перейти на единую реализацию (см. этап 3) |
