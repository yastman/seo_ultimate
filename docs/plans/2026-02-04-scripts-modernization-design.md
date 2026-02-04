# Scripts Modernization Design

**Дата:** 2026-02-04
**Цель:** Навести порядок в 89 скриптах, перейти на uv, покрыть 80% тестами

---

## Итоговая структура

```
seo-ultimate/
├── pyproject.toml
├── uv.lock
├── src/seo_ultimate/
│   ├── core/           # config, keyword_utils, text_utils, seo_utils, coverage_matcher
│   ├── validate/       # validate_*, verify_*
│   ├── audit/          # audit_*, check_*
│   ├── analyze/        # analyze_*
│   ├── extract/        # extract_*, export_*, collect_*
│   ├── generate/       # generate_*, regenerate_*
│   ├── fix/            # fix_*, cleanup_*
│   ├── sync/           # sync_*, merge_*, migrate_*, upload_*
│   ├── compare/        # compare_*
│   ├── batch/          # batch_*
│   └── tools/          # остальное (разберём в конце)
├── tests/
│   ├── unit/           # core/
│   ├── integration/    # validate/, audit/
│   └── e2e/            # smoke tests
└── scripts/            # legacy symlinks (deprecate постепенно)
```

---

## Фазы работы

### Фаза 1: Инфраструктура
- [ ] Создать pyproject.toml с uv
- [ ] Настроить dependency-groups: dev, test, nlp
- [ ] Создать src/seo_ultimate/ структуру
- [ ] Настроить ruff, pytest, mypy в pyproject.toml

### Фаза 2: Core модуль
- [ ] Мигрировать: config, keyword_utils, text_utils, seo_utils, coverage_matcher
- [ ] Unit-тесты на core (target: 90%+ coverage для core)
- [ ] Исправить импорты в зависимых скриптах

### Фаза 3: Validate + Audit
- [ ] Мигрировать validate_* (8 файлов)
- [ ] Мигрировать audit_*, check_* (11 файлов)
- [ ] Integration-тесты с fixtures

### Фаза 4: Остальные модули
- [ ] analyze/, extract/, generate/, fix/, sync/, compare/, batch/
- [ ] Аудит tools/ — удалить мёртвое, распределить живое

### Фаза 5: Cleanup
- [ ] Удалить legacy scripts/
- [ ] Обновить CLAUDE.md
- [ ] Финальный coverage отчёт

---

## Распределение по воркерам

| Worker | Задача | Файлы |
|--------|--------|-------|
| W1 | Инфраструктура + Core | pyproject.toml, src/seo_ultimate/core/ |
| W2 | Validate модуль + тесты | src/seo_ultimate/validate/, tests/unit/validate/ |
| W3 | Audit модуль + тесты | src/seo_ultimate/audit/, tests/integration/audit/ |
| W4 | Остальные модули | analyze/, extract/, generate/, fix/, sync/ |

**Правило:** каждый воркер работает с изолированным набором файлов, без пересечений.

---

## Тестирование

| Модуль | Подход | Target |
|--------|--------|--------|
| core/ | Unit | 90% |
| validate/ | Integration | 80% |
| audit/ | Integration | 80% |
| остальное | Smoke | 60% |
| **Общий** | — | **80%** |

---

## Зависимости (pyproject.toml)

```toml
[project]
name = "seo-ultimate"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pyyaml>=6.0",
    "tqdm>=4.67",
    "requests>=2.32",
]

[dependency-groups]
nlp = ["pymorphy3>=2.0", "natasha>=1.6", "spacy>=3.8"]
dev = ["ruff>=0.14", "mypy>=1.18"]
test = ["pytest>=9.0", "pytest-cov>=7.0", "pytest-xdist>=3.5"]

[tool.uv]
dev-dependencies = ["ruff", "mypy", "pytest", "pytest-cov"]
```

---

## Критерии готовности

- [ ] `uv sync` работает
- [ ] `uv run pytest` проходит
- [ ] Coverage ≥80%
- [ ] Все скрипты импортируются из src/seo_ultimate/
- [ ] ruff check проходит без ошибок
- [ ] mypy --strict на core/ проходит
