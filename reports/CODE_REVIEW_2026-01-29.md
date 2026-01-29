# Code Review Report — Ultimate.net.ua SEO Content Pipeline

**Date:** 2026-01-29  
**Scope:** `scripts/`, `tests/`, project configs (pytest/ruff/mypy)  
**Environment used for checks:** Linux/WSL, Python 3.12.3

## Executive summary

Проект выглядит живым и хорошо покрыт тестами (сотни тест-кейсов), но сейчас есть несколько регрессий/несостыковок между кодом, тестами и документацией:

- `pytest` падает на 5 тестах (в основном из‑за несоответствий ожиданий к текстовым нормализаторам и стандартам контента, плюс несовпадение тестового билдера структуры с реальными данными).
- `ruff` на целевых папках (`scripts`, `tests`) находит 8 ошибок, включая реальную логическую ошибку (shadowing переменной) в `scripts/analyze_keyword_duplicates.py`.
- `mypy` включён в очень строгом режиме, но код/тесты ему не соответствуют (сотни ошибок) — сейчас это скорее “wishful config”, чем реально используемый контроль качества.
- Найдена потенциальная runtime-ошибка: `scripts/competitors.py` импортирует `is_blacklisted_domain` из `scripts.seo_utils`, но реализация находится в `scripts/utils/url.py` (и дублируется ещё в нескольких местах).

## What I ran (repro)

- `python3 -m pytest -q`
- `python3 -m pytest <точечные тесты> -vv` (по каждому из упавших)
- `ruff check scripts tests`
- `mypy --config-file pyproject.toml scripts`

## Test failures (5)

### 1) Markdown lists cleanup
- **Fail:** `tests/unit/test_seo_utils.py::TestCleanMarkdown::test_remove_lists`
- **Symptom:** `clean_markdown()` снимает маркеры списков только для `-/*/+`, но **не** для нумерованных списков (`1. `).
- **Where:** `scripts/seo_utils.py:346` (`clean_markdown`)
- **Suggested fix:** доп. правило для ordered lists, например `r"^\\s*\\d+[\\.)]\\s+"` с `re.MULTILINE`.

### 2) Punctuation removal in normalize_text
- **Fail:** `tests/unit/test_seo_utils.py::TestNormalizeText::test_remove_punctuation`
- **Symptom:** `normalize_text()` сейчас почти не трогает пунктуацию, хотя по смыслу/докстрингу “оставляет только слова”.
- **Where:** `scripts/seo_utils.py:402` (`normalize_text`)
- **Suggested fix:** после снятия markdown добавить шаг удаления пунктуации (аккуратно, чтобы не сломать апострофы в `It's` и дефисы в словах при необходимости).

### 3) Split coverage: expectation vs adaptive target
- **Fail:** `tests/unit/test_validate_content.py::TestCoverage::test_coverage_split_semantic`
- **Symptom:** `check_keyword_coverage_split()` использует `get_adaptive_coverage_target(core_total)` для core‑части. При `core_total=2` target, вероятно, 70%, а 1/2=50% => `passed=False`.
- **Where:** `scripts/validate_content.py:448` (`check_keyword_coverage_split`)
- **Suggested fix (one of):**
  - Если логика верная: **исправить тест**, патчив `get_adaptive_coverage_target` как в `test_keyword_coverage`.
  - Если ожидание верное: **пересмотреть target** для очень малого `core_total` или правила `passed` (например, разрешать 50% при `core_total <= 2`).

### 4) Content standards: “## Safety” not detected
- **Fail:** `tests/unit/test_validate_content.py::TestContentStandards::test_standards_patterns`
- **Symptom:** докстринг обещает `## Safety`, но в паттернах safety для RU/UK английского `## Safety` нет, поэтому `safety_block=False`.
- **Where:** `scripts/validate_content.py:714` (`check_content_standards`)
- **Suggested fix:** добавить language-independent паттерн для `##\\s*safety\\b` (или расширить `ru/uk`-паттерны).

### 5) Test helper produces non-matching clean.json schema
- **Fail:** `tests/integration/test_file_ops.py::test_category_builder_creates_structure`
- **Symptom:** `CategoryBuilder.with_keywords([...])` сохраняет keywords как `{"primary": [...]}`, а тест ожидает `clean_data["keywords"][0]`.
- **Where:** `tests/helpers/file_builders.py:45` (`CategoryBuilder.with_keywords`) + `build()`
- **Important context:** в реальных данных большинство `*_clean.json` имеют `keywords: list[...]`, но встречаются и `keywords: dict[...]` (по кластерам).
- **Suggested fix:** определиться со schema (1 SSOT) и:
  - либо сделать `CategoryBuilder` по умолчанию совместимым с основным форматом данных,
  - либо обновить тест и/или добавить режим/флаг в билдер (list-vs-clustered) и использовать нужный в тестах.

## Lint (ruff) findings (8 on `scripts` + `tests`)

### High impact (logic bug)
- `scripts/analyze_keyword_duplicates.py:134` — `B020` shadowing переменной `dup` (и использование `dup` из предыдущего цикла).
  - Это легко приводит к неверной логике/непредсказуемому поведению в секции “Рекомендация”.

### Low/medium impact
- `scripts/audit_unused_keywords.py` — несортированные импорты (`I001`).
- `scripts/compare_with_master.py` — неиспользуемая переменная цикла (`B007`), `f`-строка без плейсхолдеров (`F541`).
- `tests/unit/test_audit_keyword_consistency.py`, `tests/unit/test_validate_uk.py` — неиспользуемые импорты (`F401`).

### Tooling note (ruff scope)
Если запускать `ruff check .`, он лезет также в `.github_repos/` и `.claude/` и генерирует много шума. Имеет смысл добавить `extend-exclude` в `pyproject.toml` для этих папок (если они не являются частью поддерживаемого кода проекта).

## Typing (mypy) status

`pyproject.toml` включает **очень строгий** режим `mypy`, но текущий код в `scripts/` и особенно `tests/` ему не соответствует (сотни ошибок).

Ключевой практический вывод: либо:
- ослабить mypy‑настройки (или отключить для `tests/`), либо
- идти итеративно: начать с типизации “ядра” (например `scripts/seo_utils.py`, `scripts/validate_content.py`), затем постепенно расширять покрытие.

Отдельный важный сигнал от mypy:
- `scripts/competitors.py` импортирует `is_blacklisted_domain` из `scripts.seo_utils`, но реализация находится в `scripts/utils/url.py` (плюс дублируется в `scripts/utils/text.py` и `scripts/url_filters.py`). Это риск runtime‑ошибки/рассинхронизации.

## Config consistency issues

- `pytest`: присутствуют настройки и в `pyproject.toml`, и в `pytest.ini`, но реально используется `pytest.ini` (pytest прямо пишет, что игнорирует конфиг в `pyproject.toml`). Лучше оставить один источник правды.
- `keywords` schema: одновременно встречаются `keywords: list[...]` и `keywords: dict[cluster -> list[...]]` в `*_clean.json`. Это повышает стоимость поддержки и тестирования.

## Suggested next actions (prioritized)

1. Починить 5 упавших тестов (или код, или тест-ожидания) — это вернёт “green” базу.
2. Устранить `B020` в `scripts/analyze_keyword_duplicates.py` (реальная логическая ошибка).
3. Привести `is_blacklisted_domain` к одному месту (например `scripts/utils/url.py`) и поправить импорты/реэкспорт.
4. Убрать дублирование конфигов (`pytest.ini` vs `pyproject.toml`) и зафиксировать SSOT.
5. По `mypy`: либо отключить strict для тестов, либо вести поэтапную типизацию с постепенным ужесточением.

