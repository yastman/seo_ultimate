# Scripts Modernization Plan

**Дизайн:** [2026-02-04-scripts-modernization-design.md](./2026-02-04-scripts-modernization-design.md)

---

## Worker 1: Инфраструктура + Core

### Task 1.1: uv + pyproject.toml
```bash
# Файлы для создания/изменения:
- pyproject.toml (новый)
- .python-version (новый)
# Удалить после миграции:
- requirements.txt
```

**Шаги:**
1. `uv init --no-readme`
2. Перенести зависимости из requirements.txt в pyproject.toml
3. Добавить dependency-groups: nlp, dev, test
4. Настроить [tool.ruff], [tool.pytest], [tool.mypy]
5. `uv sync --all-groups`
6. Проверить: `uv run python -c "import pymorphy3"`

### Task 1.2: Структура src/
```bash
mkdir -p src/seo_ultimate/{core,validate,audit,analyze,extract,generate,fix,sync,compare,batch,tools}
touch src/seo_ultimate/__init__.py
touch src/seo_ultimate/core/__init__.py
```

### Task 1.3: Миграция core/
```bash
# Переместить:
scripts/config.py         → src/seo_ultimate/core/config.py
scripts/keyword_utils.py  → src/seo_ultimate/core/keyword_utils.py
scripts/text_utils.py     → src/seo_ultimate/core/text_utils.py
scripts/seo_utils.py      → src/seo_ultimate/core/seo_utils.py
scripts/coverage_matcher.py → src/seo_ultimate/core/coverage_matcher.py
scripts/synonym_tools.py  → src/seo_ultimate/core/synonym_tools.py
```

**После миграции:**
- Обновить импорты внутри core/
- Создать `src/seo_ultimate/core/__init__.py` с публичным API

### Task 1.4: Unit-тесты core/
```bash
tests/unit/core/
├── test_config.py
├── test_keyword_utils.py
├── test_text_utils.py
├── test_seo_utils.py
├── test_coverage_matcher.py
└── test_synonym_tools.py
```

**Target:** 90% coverage на core/

---

## Worker 2: Validate модуль

### Task 2.1: Миграция validate/
```bash
# Переместить (8 файлов):
scripts/validate_content.py  → src/seo_ultimate/validate/content.py
scripts/validate_density.py  → src/seo_ultimate/validate/density.py
scripts/validate_master.py   → src/seo_ultimate/validate/master.py
scripts/validate_meta.py     → src/seo_ultimate/validate/meta.py
scripts/validate_seo.py      → src/seo_ultimate/validate/seo.py
scripts/validate_uk.py       → src/seo_ultimate/validate/uk.py
scripts/verify_structural_integrity.py → src/seo_ultimate/validate/structural.py
scripts/verify_test_infra.py → src/seo_ultimate/validate/test_infra.py
```

### Task 2.2: Обновить импорты
- Заменить `from scripts.keyword_utils` → `from seo_ultimate.core.keyword_utils`
- Заменить `from scripts.config` → `from seo_ultimate.core.config`

### Task 2.3: CLI entry points
```python
# src/seo_ultimate/validate/__init__.py
from .meta import validate_meta
from .content import validate_content
# etc.
```

### Task 2.4: Integration-тесты
```bash
tests/integration/validate/
├── test_validate_meta.py      # fixtures: valid/invalid _meta.json
├── test_validate_content.py   # fixtures: sample .md files
├── test_validate_density.py
└── test_validate_seo.py
```

**Target:** 80% coverage на validate/

---

## Worker 3: Audit модуль

### Task 3.1: Миграция audit/ (11 файлов)
```bash
scripts/audit_coverage.py          → src/seo_ultimate/audit/coverage.py
scripts/audit_h1_primary.py        → src/seo_ultimate/audit/h1_primary.py
scripts/audit_keyword_consistency.py → src/seo_ultimate/audit/keyword_consistency.py
scripts/audit_meta.py              → src/seo_ultimate/audit/meta.py
scripts/audit_synonyms.py          → src/seo_ultimate/audit/synonyms.py
scripts/audit_unused_keywords.py   → src/seo_ultimate/audit/unused_keywords.py
scripts/check_cannibalization.py   → src/seo_ultimate/audit/cannibalization.py
scripts/check_h1_sync.py           → src/seo_ultimate/audit/h1_sync.py
scripts/check_ner_brands.py        → src/seo_ultimate/audit/ner_brands.py
scripts/check_semantic_coverage.py → src/seo_ultimate/audit/semantic_coverage.py
scripts/check_water_natasha.py     → src/seo_ultimate/audit/water_natasha.py
```

### Task 3.2: Обновить импорты
- Аналогично Worker 2

### Task 3.3: Integration-тесты
```bash
tests/integration/audit/
├── test_audit_coverage.py
├── test_audit_h1_primary.py
├── test_check_water_natasha.py
└── ...
```

**Target:** 80% coverage на audit/

---

## Worker 4: Остальные модули

### Task 4.1: analyze/ (5 файлов)
```bash
scripts/analyze_category.py           → src/seo_ultimate/analyze/category.py
scripts/analyze_keyword_duplicates.py → src/seo_ultimate/analyze/keyword_duplicates.py
scripts/analyze_keywords_order.py     → src/seo_ultimate/analyze/keywords_order.py
scripts/analyze_keywords_synonyms.py  → src/seo_ultimate/analyze/keywords_synonyms.py
scripts/analyze_meta_keywords.py      → src/seo_ultimate/analyze/meta_keywords.py
```

### Task 4.2: extract/ (9 файлов)
```bash
scripts/extract_all_keywords.py      → src/seo_ultimate/extract/all_keywords.py
scripts/extract_categories.py        → src/seo_ultimate/extract/categories.py
scripts/extract_ru_keywords_list.py  → src/seo_ultimate/extract/ru_keywords_list.py
scripts/extract_ru_keywords_mapping.py → src/seo_ultimate/extract/ru_keywords_mapping.py
scripts/extract_uk_keywords.py       → src/seo_ultimate/extract/uk_keywords.py
scripts/extract_uk_keywords_list.py  → src/seo_ultimate/extract/uk_keywords_list.py
scripts/export_uk_category_texts.py  → src/seo_ultimate/extract/uk_category_texts.py
scripts/collect_keywords.py          → src/seo_ultimate/extract/collect.py
```

### Task 4.3: generate/ (8 файлов)
```bash
scripts/generate_all_meta.py         → src/seo_ultimate/generate/all_meta.py
scripts/generate_catalog_json.py     → src/seo_ultimate/generate/catalog_json.py
scripts/generate_checklists.py       → src/seo_ultimate/generate/checklists.py
scripts/generate_plural_sql.py       → src/seo_ultimate/generate/plural_sql.py
scripts/generate_semantic_review.py  → src/seo_ultimate/generate/semantic_review.py
scripts/generate_sql.py              → src/seo_ultimate/generate/sql.py
scripts/generate_uk_keywords_from_ru.py → src/seo_ultimate/generate/uk_keywords.py
scripts/regenerate_all_meta.py       → src/seo_ultimate/generate/regenerate_meta.py
```

### Task 4.4: fix/, sync/, compare/, batch/
```bash
# fix/ (6 файлов)
scripts/fix_*.py → src/seo_ultimate/fix/
scripts/cleanup_misplaced.py → src/seo_ultimate/fix/cleanup.py

# sync/ (6 файлов)
scripts/sync_*.py → src/seo_ultimate/sync/
scripts/merge_to_master.py → src/seo_ultimate/sync/merge_master.py
scripts/migrate_keywords.py → src/seo_ultimate/sync/migrate.py
scripts/upload_to_db.py → src/seo_ultimate/sync/upload_db.py

# compare/ (3 файла)
scripts/compare_*.py → src/seo_ultimate/compare/

# batch/ (2 файла)
scripts/batch_*.py → src/seo_ultimate/batch/
```

### Task 4.5: Smoke-тесты
- Проверить что каждый модуль импортируется
- Базовые тесты на основные функции

---

## Финальная фаза (после всех воркеров)

### Task 5.1: Аудит tools/
- Проанализировать оставшиеся ~26 скриптов
- Удалить неиспользуемые
- Распределить полезные по модулям

### Task 5.2: Legacy cleanup
```bash
# После полной миграции:
rm -rf scripts/*.py
# Оставить только __init__.py с deprecation warning
```

### Task 5.3: Обновить документацию
- CLAUDE.md: новые пути импортов
- README: инструкции по uv

### Task 5.4: Coverage отчёт
```bash
uv run pytest --cov=src/seo_ultimate --cov-report=html
# Проверить ≥80%
```

---

## Порядок выполнения

```
W1 (Core) ────────┐
                  ├──→ W2, W3, W4 параллельно ──→ Финальная фаза
                  │
[блокирует остальных - нужен core для импортов]
```

**W1 должен завершиться первым**, потом W2/W3/W4 могут работать параллельно.

---

## Команды запуска воркеров

```bash
# После завершения W1:
spawn-claude "W2: Validate модуль.
Читай docs/plans/2026-02-04-scripts-modernization-plan.md — Worker 2.
Лог: data/generated/audit-logs/W2_modernization.md
НЕ ДЕЛАЙ git commit" "$(pwd)"

spawn-claude "W3: Audit модуль.
Читай docs/plans/2026-02-04-scripts-modernization-plan.md — Worker 3.
Лог: data/generated/audit-logs/W3_modernization.md
НЕ ДЕЛАЙ git commit" "$(pwd)"

spawn-claude "W4: Остальные модули.
Читай docs/plans/2026-02-04-scripts-modernization-plan.md — Worker 4.
Лог: data/generated/audit-logs/W4_modernization.md
НЕ ДЕЛАЙ git commit" "$(pwd)"
```
