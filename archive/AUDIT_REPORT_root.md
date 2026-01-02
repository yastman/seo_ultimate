# Аудит скриптов + TDD (pytest) — отчет

## Статус тестов

- Команда: `venv/bin/python -m pytest -q`
- Результат: `367 passed, 0 failed` (есть warnings — см. вывод pytest)

## Покрытие (pytest-cov / coverage)

- Команда: `venv/bin/python -m coverage report -m`
- Итог: `81%` (2827 statements)

| Скрипт | Coverage |
| --- | --- |
| `scripts/check_ner_brands.py` | 89% |
| `scripts/check_seo_structure.py` | 88% |
| `scripts/check_simple_v2_md.py` | 90% |
| `scripts/check_water_natasha.py` | 72% |
| `scripts/extract_competitor_urls_v2.py` | 87% |
| `scripts/filter_mega_competitors.py` | 77% |
| `scripts/mega_url_extract.py` | 84% |
| `scripts/parse_hubs_logic.py` | 76% |
| `scripts/parse_semantics_to_json.py` | 70% |
| `scripts/quality_runner.py` | 71% |
| `scripts/seo_utils.py` | 76% |
| `scripts/setup_all.py` | 95% |
| `scripts/show_keyword_distribution.py` | 90% |
| `scripts/url_filters.py` | 100% |
| `scripts/url_preparation_filter_and_validate.py` | 80% |

## Оценка качества (кратко)

- `scripts/check_simple_v2_md.py`: много логики в одном файле (валидация+репортинг+CLI), но покрытие высокое; следующий шаг — выделять “ядро” проверок в отдельный модуль, CLI оставить тонким.
- `scripts/quality_runner.py`: по сути оркестратор; сейчас тестируемый и стабильно импортируемый, но стоит продолжать разделение I/O и чистой логики.
- `scripts/parse_semantics_to_json.py`: парсер/трансформации/CLI смешаны; логически напрашивается декомпозиция на read/transform/write.
- `scripts/check_water_natasha.py`: тяжёлая зависимость (NLP), важно сохранять мягкие fallback’и/опциональность и держать API функций стабильным.
- Остальные (`extract_competitor_urls_v2.py`, `filter_mega_competitors.py`, `mega_url_extract.py`, `show_keyword_distribution.py`, `setup_all.py`): читабельные, покрыты тестами, CLI не мешает импорту.

## Ключевые проблемы качества (по аудиту)

### 1) Тестируемость vs “скриптовость”

Ранее часть тестов:

- запускала скрипты только через `subprocess` (это **не попадало** в `pytest-cov` по умолчанию);
- местами “переписывала” логику внутри тестов вместо импорта функций (ложное ощущение покрытия).

Это давало ситуацию “тесты есть, а coverage 0% по файлу”.

### 2) Импорты, завязанные на `PYTHONPATH=.` (DX-проблема)

Несколько скриптов импортировали `from scripts.*` и при запуске как:
`python3 scripts/<file>.py` падали с `ModuleNotFoundError: No module named 'scripts'`
без явного `PYTHONPATH=.`.

### 3) Side effects на import

Часть скриптов парсила CLI-аргументы на уровне модуля (в момент `import`), из-за чего:

- импорт в тестах ломался;
- приходилось уходить в `subprocess` вместо unit-тестов.

## Что сделано (исправления + TDD тесты)

- Добавлен `scripts/__init__.py` для стабильных импортов `scripts.*`.
- Исправлен запуск без `PYTHONPATH=.` для:
  - `scripts/filter_mega_competitors.py`
  - `scripts/quality_runner.py`
  - `scripts/parse_semantics_to_json.py`
  - `scripts/check_water_natasha.py`
  - `scripts/url_preparation_filter_and_validate.py`
- Убраны side effects на import и сделаны `main(argv=...)` там, где это было blocker’ом для TDD:
  - `scripts/mega_url_extract.py`
  - `scripts/show_keyword_distribution.py`
  - `scripts/extract_competitor_urls_v2.py` (переписан в более модульный вид)
- Переписаны тесты так, чтобы:
  - вызывать функции/`main(argv=...)` **в одном процессе** (coverage учитывается);
  - использовать `tmp_path` фикстуры для файлов и изоляции от реальных данных;
  - monkeypatch-ить сетевые/медленные части (например HTTP-check) вместо реальных запросов.

Файлы тестов, которые были существенно переработаны под TDD/coverage:

- `tests/test_extract_competitor_urls.py`
- `tests/test_filter_mega_competitors.py`
- `tests/test_mega_url_extract.py`
- `tests/test_show_keyword_distribution.py`
- `tests/test_url_preparation.py`
- `tests/test_keyword_density.py` (убран `subprocess` → in-process запуск для стабильности/coverage)

## Риски и рекомендации (следующий шаг)

- Точки роста по качеству кода: `scripts/parse_semantics_to_json.py` и `scripts/quality_runner.py` (объём/ветвления) — держать “ядро” в pure-функциях, CLI тонким.
- По тестам: сейчас покрытие высокое; при добавлении новых стадий пайплайна сохранять стиль “in-process” тестов (без `subprocess`) для честного coverage.
- Dev-tools: в репо есть конфиги `ruff`/`mypy`, но в текущем venv они не установлены (имеет смысл ставить через `requirements-dev.txt` и включить в CI/pre-commit).
