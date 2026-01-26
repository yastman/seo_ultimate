# Design: Покрытие скриптов тестами + Оптимизация скиллов

**Дата:** 2026-01-26
**Статус:** Draft
**Автор:** Claude + User

---

## Обзор

Две параллельные задачи:
- **Задача A:** Покрытие скриптов тестами (цель 80%)
- **Задача B:** Оптимизация скиллов (устранение дублей RU/UK)

---

## Текущее состояние

### Скрипты
- **Всего:** 67 скриптов в `scripts/`
- **Покрыто тестами:** 14 (21%)
- **Цель:** 54 (80%)

### Скиллы
- **RU/UK пары:** 6 (quality-gate, content-generator, generate-meta, deploy, seo-research, content-init)
- **Дублирование:** 70-85%
- **Цель:** <30% дублирования

---

## Задача A: Покрытие скриптов тестами

### Структура тестов

```
tests/
├── conftest.py              # Общие фикстуры (уже есть)
├── helpers/
│   └── file_builders.py     # Билдеры тестовых данных (уже есть)
├── unit/                    # Изолированные тесты функций
│   ├── test_md_to_html.py   # NEW
│   ├── test_generate_sql.py # NEW
│   └── ...
├── integration/             # Тесты с файловой системой/DB
│   ├── test_upload_to_db.py # NEW (mock DB)
│   └── ...
└── fixtures/                # NEW: тестовые данные
    ├── sample_clean.json
    ├── sample_meta.json
    └── sample_content.md
```

### Принципы тестирования

| Принцип | Описание |
|---------|----------|
| **Unit first** | Тестировать чистые функции без side effects |
| **Mock I/O** | Файлы, DB, SSH — через mock/fixtures |
| **Parametrize** | Один тест, много кейсов (pytest.mark.parametrize) |
| **Fast** | Без реальных сетевых вызовов |

### TDD Workflow

```
1. RED:    Написать тест который падает
2. GREEN:  Убедиться что скрипт проходит тест
3. REFACTOR: Улучшить тест/скрипт если нужно
```

Для существующих скриптов:

```
1. Читаем скрипт → понимаем API (input/output)
2. Пишем тест на expected behavior
3. Запускаем тест → должен быть GREEN
4. Пишем тест на edge cases
5. Если RED → это баг в скрипте, фиксим
6. Пишем тест на error handling
7. Если RED → добавляем error handling в скрипт
```

### Приоритеты скриптов

#### P0 — Блокеры deploy (3 скрипта)

| Скрипт | Что тестировать | Сложность |
|--------|-----------------|-----------|
| `md_to_html.py` | Конвертация MD→HTML, таблицы, списки | Низкая |
| `generate_sql.py` | SQL генерация, escaping, language_id | Низкая |
| `upload_to_db.py` | SSH mock, error handling | Средняя |

#### P1 — Валидация (5 скриптов)

| Скрипт | Что тестировать | Сложность |
|--------|-----------------|-----------|
| `validate_uk.py` | UK-специфичные правила | Низкая |
| `audit_keyword_consistency.py` | meta vs clean sync | Низкая |
| `audit_meta.py` | Batch meta validation | Низкая |
| `audit_synonyms.py` | Synonyms validation | Низкая |
| `check_cannibalization.py` | Keyword overlap detection | Средняя |

#### P2 — Генерация (8 скриптов)

| Скрипт | Что тестировать | Сложность |
|--------|-----------------|-----------|
| `generate_all_meta.py` | Batch generation | Средняя |
| `generate_catalog_json.py` | Catalog structure | Низкая |
| `generate_checklists.py` | Checklist output | Низкая |
| `generate_uk_keywords_from_ru.py` | RU→UK translation | Средняя |
| `extract_categories.py` | Category extraction | Низкая |
| `extract_uk_keywords.py` | UK keyword extraction | Низкая |
| `build_product_map.py` | Product mapping | Низкая |
| `batch_generate.py` | Batch orchestration | Средняя |

#### P3 — Утилиты (24 скрипта, топ-10)

- `utils/text.py`, `utils/url.py`
- `fix_keywords_order.py`, `fix_missing_keywords.py`
- `migrate_keywords.py`, `restore_from_csv.py`
- `uk_seed_from_ru.py`, `update_uk_clean_json.py`
- `csv_to_readable_md.py`, `parse_semantics_to_json.py`

### Пример TDD теста

```python
# tests/unit/test_md_to_html.py

import pytest
from scripts.md_to_html import convert_md_to_html

class TestMdToHtml:
    """TDD tests for md_to_html.py"""

    # 1. Basic functionality (должен быть GREEN)
    def test_converts_h2_to_html(self):
        md = "## Заголовок"
        assert "<h2>Заголовок</h2>" in convert_md_to_html(md)

    def test_converts_bold_to_strong(self):
        md = "**жирный**"
        assert "<strong>жирный</strong>" in convert_md_to_html(md)

    # 2. Edge cases (может быть RED → фиксим скрипт)
    def test_handles_empty_input(self):
        assert convert_md_to_html("") == ""

    def test_handles_cyrillic_in_table(self):
        md = "| Колонка |\n|---|\n| Значение |"
        html = convert_md_to_html(md)
        assert "<table" in html

    # 3. H1 removal (специфика проекта)
    def test_removes_h1_for_meta(self):
        md = "# H1 Title\n\n## H2 Content"
        html = convert_md_to_html(md)
        assert "<h1>" not in html  # H1 идёт в meta_h1
        assert "<h2>H2 Content</h2>" in html
```

### Чеклист TDD для каждого скрипта

- [ ] Тест на happy path (основной сценарий)
- [ ] Тест на edge cases (пустой input, Unicode, большие данные)
- [ ] Тест на error handling (невалидный input)
- [ ] Тест на project-specific logic (UK терминология, etc.)

---

## Задача B: Оптимизация скиллов

### Подход: Наследование + Shared References

UK скиллы ссылаются на общие reference файлы, содержат только UK-специфику.

### Целевая структура

```
.claude/skills/
├── shared/                          # NEW: общие references
│   ├── validation-checklist.md      # Общие правила валидации
│   ├── meta-rules.md                # IRON RULE, формулы Title/H1
│   ├── buyer-guide-structure.md     # Структура контента
│   └── deploy-workflow.md           # SQL patterns, safety rules
│
├── quality-gate/
│   └── skill.md                     # RU-specific + ссылка на shared/
│
├── uk-quality-gate/
│   └── skill.md                     # UK-specific + ссылка на shared/
│
├── generate-meta/
│   ├── skill.md                     # RU формулы
│   └── REFERENCE.md
│
├── uk-generate-meta/
│   └── skill.md                     # UK формулы + ссылка на shared/
│
└── ... (остальные по аналогии)
```

### Что выносится в shared/

| Файл | Содержимое | Используется в |
|------|------------|----------------|
| `validation-checklist.md` | Структура, SEO rules, pass criteria | quality-gate, uk-quality-gate |
| `meta-rules.md` | IRON RULE, Producer/Shop pattern, Red Flags | generate-meta, uk-generate-meta |
| `buyer-guide-structure.md` | Intro, Tables, FAQ, Stop-list | content-generator, uk-content-generator |
| `deploy-workflow.md` | SQL template, Safety rules, Verify steps | deploy, uk-deploy |

### Что остаётся в UK скиллах

| Скилл | UK-specific контент |
|-------|---------------------|
| uk-quality-gate | Терминология (резина→гума), language_id=1 |
| uk-generate-meta | "Купити" формула, UK Description pattern |
| uk-content-generator | uk-lsi-synonyms.md (уже есть) |
| uk-deploy | language_id=1, UK paths |

### План миграции

1. Создать `.claude/skills/shared/` директорию
2. Вынести общие части из RU скиллов в shared/
3. Обновить UK скиллы на ссылки
4. Smoke test — проверить что скиллы работают

---

## Timeline

```
Week 1-2: Задача A (Тесты) + Задача B (Скиллы) параллельно
         ├── A: P0 скрипты (3) + P1 скрипты (5)
         └── B: shared/ структура + миграция quality-gate

Week 3-4: Продолжение
         ├── A: P2 скрипты (8) + P3 топ-10
         └── B: миграция остальных скиллов
```

---

## Deliverables

### Задача A — Тесты

| Этап | Файлы | Покрытие |
|------|-------|----------|
| A1-A3 | P0 скрипты (3) | 25% |
| A4-A6 | P1 скрипты (5) | 33% |
| A7-A10 | P2 скрипты (8) | 45% |
| A11-A40 | P3 скрипты (30) | 80% |

### Задача B — Скиллы

| Этап | Файлы |
|------|-------|
| B1 | `.claude/skills/shared/` директория |
| B2 | `shared/validation-checklist.md` |
| B3 | `shared/meta-rules.md` |
| B4 | `shared/buyer-guide-structure.md` |
| B5 | `shared/deploy-workflow.md` |
| B6-B9 | Миграция UK скиллов |

---

## Критерии успеха

### Задача A

| Метрика | Текущее | Цель |
|---------|---------|------|
| Покрытие скриптов | 21% | 80% |
| Все тесты проходят | — | 100% |
| P0 скрипты покрыты | 0/3 | 3/3 |
| P1 скрипты покрыты | 0/5 | 5/5 |

### Задача B

| Метрика | Текущее | Цель |
|---------|---------|------|
| Дублирование кода | 70-85% | <30% |
| shared/ файлов | 0 | 4 |
| UK скиллы с ссылками | 2/6 | 6/6 |

### Definition of Done

**Задача A:**
- [ ] `pytest` проходит без ошибок
- [ ] Покрытие ≥80% (54+ скриптов)
- [ ] Все P0 и P1 скрипты покрыты

**Задача B:**
- [ ] `shared/` содержит 4 файла
- [ ] Все UK скиллы ссылаются на shared/
- [ ] Скиллы работают (smoke test)

---

## Риски и Mitigation

| Риск | Вероятность | Влияние | Mitigation |
|------|-------------|---------|------------|
| Скрипты без чистого API | Средняя | Высокое | Рефакторинг: вынести логику в функции |
| Тесты ломаются при изменении | Высокая | Среднее | Тесты на контракт, не на реализацию |
| Shared references рассинхронизируются | Низкая | Среднее | CI check: grep references в UK skills |
| SSH/DB тесты требуют credentials | Высокая | Низкое | Mock всех внешних вызовов |

---

## Команды

```bash
# Запуск всех тестов
pytest

# Запуск конкретного теста
pytest tests/unit/test_md_to_html.py -v

# Покрытие
pytest --cov=scripts --cov-report=term-missing

# Проверка скиллов
ls .claude/skills/shared/
grep -r "shared/" .claude/skills/uk-*/
```

---

**Version:** 1.0
**Next step:** Утверждение плана → Реализация
