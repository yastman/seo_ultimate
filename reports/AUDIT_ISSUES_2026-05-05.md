# Полный аудит проекта — 2026-05-05

> Ветка: `main` (up to date with `origin/main`)
> Коммит: последний
> Окружение: Python 3.12.3, uv

---

## 📊 Общая статистика

| Метрика | RU | UK |
|---------|----|-----|
| Категорий | 53 | 54 |
| Контент-файлов | 53 | 54 |
| Пустых контент-файлов | 0 | 0 |
| Мета-файлов | 53 | 54 |
| `_clean.json` | 53 | 54 |
| Keywords flat | 53 | 53 |
| Keywords nested (v2) | 0 | 1 (polirovalnye-krugi) |
| Тестов: passed | 555 | |
| Тестов: failed | 14 (все из-за BUG-002) | |
| Тестов: error | 1 (BUG-007) | |

---

## 🔴 CRITICAL

### BUG-001: TypeError в coverage audit при обработке UK категорий
- **Issue:** [#1](https://github.com/yastman/llm-keywords-pipeline/issues/1)
- **Компонент:** `src/llm_keywords_pipeline/core/coverage.py:275`
- **Тип:** Runtime Error (TypeError)
- **Причина:** 1 UK категория (`polirovalnye-krugi`) использует nested keywords (primary/secondary/supporting/commercial), а код ожидает плоский список. Остальные 53 UK — flat, работают корректно.

### BUG-002: ModuleNotFoundError — pkg_resources (блокирует audit.water + 14 тестов)
- **Issue:** [#2](https://github.com/yastman/llm-keywords-pipeline/issues/2)
- **Компонент:** `src/llm_keywords_pipeline/audit/water.py`
- **Тип:** Runtime Error (ModuleNotFoundError)
- **Влияние:** `audit.water` не работает. 14/570 тестов падают (все `test_water` + `test_check_water_natasha`).
- **Причина:** `pymorphy2` (зависимость `natasha`) требует `pkg_resources` из `setuptools`, а его нет в venv.

---

## 🟡 HIGH

### ISSUE-003: H1 Sync — рассинхронизация (3 категории)
- **Issue:** [#3](https://github.com/yastman/llm-keywords-pipeline/issues/3)
- **Тип:** Data Inconsistency

| Slug | MD H1 | JSON H1 |
|------|-------|---------|
| `moyka-i-eksterer` | Химия для мойки авто | Мойка и экстерьер |
| `opt-i-b2b` | Автохимия опт | Автохимия оптом |
| `zashchitnye-pokrytiya` | Защитные покрытия для авто | Полимер для авто |

- Всего синхронизировано: 5, рассинхрон: 3.

---

## 🟠 MEDIUM

### ISSUE-004: Низкое покрытие ключей в контенте (RU)
- **Issue:** [#4](https://github.com/yastman/llm-keywords-pipeline/issues/4)

| Slug | Покрытие | Пропущено |
|------|----------|-----------|
| `neytralizatory-zapakha` | 70.0% | 3/10 |
| `ochistiteli-kozhi` | 75.0% | 2/8 |
| `glavnaya` | 91.7% | 1/12 |
| `omyvatel` | 90.0% | 1/10 |
| `sredstva-dlya-kozhi` | 85.7% | 1/7 |
| `ukhod-za-kozhey` | 87.5% | 1/8 (synonym-only) |

### ISSUE-005: Низкое покрытие ключей в контенте (UK)
- **Issue:** [#5](https://github.com/yastman/llm-keywords-pipeline/issues/5)

| Slug | Покрытие |
|------|----------|
| `glavnaya` | 47.1% |
| `nabory` | 62.5% |
| `apparaty-tornador` | 60.0% |
| `moyka-i-eksterer` | 80.0% |
| `poliroli-dlya-plastika` | 80.0% |

### BUG-007: test_upload_to_db ImportError — missing mysql.connector
- **Issue:** [#7](https://github.com/yastman/llm-keywords-pipeline/issues/7)
- **Тип:** ImportError
- **Влияние:** 1 тест не собирается (`tests/unit/test_upload_to_db.py`).
- **Причина:** `scripts/upload_to_db.py` импортирует `mysql.connector`, не установленный в venv.

---

## 🟢 LOW

### ISSUE-006: RuntimeWarning при импорте audit-модулей
- **Issue:** [#6](https://github.com/yastman/llm-keywords-pipeline/issues/6)
- **Тип:** Warning (все audit-модули)
- **Причина:** Циклический импорт `audit.__init__` ↔ `audit.<module>`.

### ISSUE-008: Ruff linting — 11 замечаний
- **Issue:** [#8](https://github.com/yastman/llm-keywords-pipeline/issues/8)
- **Тип:** Code Style
- 3× unsorted imports, 5× deprecated typing, 3× unnecessary mode arg.
- 10/11 фиксятся автофиксом.

---

## ✅ PASSED (без ошибок)

- **Keyword consistency:** 53 категории RU, 0 пустых, 295 ключей — OK
- **RU мета-теги:** 53 файла — все поля на месте, длина в норме
- **UK мета-теги:** 54 файла — все поля на месте, длина в норме
- **Контент-файлы:** Все 107 (53 RU + 54 UK) — не пустые
- **RU Coverage (основная масса):** 47/53 категорий — 100%
- **UK Coverage (основная масса):** 44/54 категорий — 100%

---

## 📎 Артефакты

| Файл | Описание |
|------|----------|
| `reports/KEYWORD_CONSISTENCY.md` | Статистика ключей по категориям |
| `reports/coverage_summary_ru_2026-05-05.csv` | Сводка покрытия RU |
| `reports/coverage_details_ru_2026-05-05.csv` | Детали покрытия RU (поключевой) |
| `reports/AUDIT_ISSUES_2026-05-05.md` | Этот отчёт |

---

## 🎯 Сводка: что чинить в первую очередь

1. **BUG-002** — добавить `setuptools` в зависимости (разблокирует water audit + 14 тестов)
2. **BUG-001** — фикс coverage.py для nested keywords (разблокирует UK audit до конца)
3. **ISSUE-003** — H1 синхронизация (`--fix` + реген мета)
4. **ISSUE-004/005** — дописать контент для coverage <90% RU и <80% UK
5. **BUG-007** — добавить `mysql-connector-python` или замокать тест
6. **ISSUE-008** — `ruff check --fix` (10 секунд)
7. **ISSUE-006** — починить циклический импорт audit
