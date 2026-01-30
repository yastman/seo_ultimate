# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Ultimate.net.ua — интернет-магазин автохимии и детейлинга.
**Язык ответов:** русский

---

## Архитектура данных

### Иерархия категорий (53 RU + 53 UK)

```
categories/{slug}/data/{slug}_clean.json     # Семантика RU
categories/{slug}/meta/{slug}_meta.json      # Мета-теги RU
categories/{slug}/content/{slug}_ru.md       # Контент RU

uk/categories/{slug}/data/{slug}_clean.json  # Семантика UK
uk/categories/{slug}/meta/{slug}_meta.json   # Мета-теги UK
uk/categories/{slug}/content/{slug}_uk.md    # Контент UK
```

Вложенность: L1 (корневые) → L2 → L3 (листовые с товарами).

### Формат JSON

**_clean.json (семантика):**
```json
{
  "id": "aktivnaya-pena",
  "keywords": [{"keyword": "...", "volume": 1000}],
  "synonyms": [{"keyword": "...", "volume": 100, "use_in": "meta_only", "variant_of": "..."}],
  "micro_intents": ["как разводить", "расход"]
}
```

**primary_keyword = MAX(volume)** — используется в Title/H1.

**_meta.json:**
```json
{
  "slug": "aktivnaya-pena",
  "language": "ru",
  "meta": {"title": "...", "description": "..."},
  "h1": "...",
  "keywords_in_content": {"primary": [], "secondary": [], "supporting": []}
}
```

---

## Pipeline

```
RU: /category-init → /generate-meta → /seo-research → /content-generator → content-reviewer → /quality-gate → /deploy

UK: /uk-content-init → /uk-generate-meta → /uk-seo-research → /uk-content-generator → uk-content-reviewer → /uk-quality-gate → /uk-deploy
```

### Скиллы

| RU | UK | Описание |
|----|-----|----------|
| `/category-init {slug}` | `/uk-content-init {slug}` | Структура папок |
| `/semantic-cluster {slug}` | — | keywords vs synonyms |
| `/generate-meta {slug}` | `/uk-generate-meta {slug}` | Мета-теги |
| `/seo-research {slug}` | `/uk-seo-research {slug}` | RESEARCH_PROMPT.md |
| `/content-generator {slug}` | `/uk-content-generator {slug}` | Buyer guide контент |
| `content-reviewer {path}` | `uk-content-reviewer {slug}` | Автофикс проблем |
| `/verify-content {slug}` | `/uk-verify-content {slug}` | Ручная проверка |
| `/quality-gate {slug}` | `/uk-quality-gate {slug}` | Финальная валидация |
| `/deploy-to-opencart {slug}` | `/uk-deploy {slug}` | SQL в OpenCart |

---

## Команды

```bash
# Тесты
pytest                        # Все
pytest -k "test_meta"         # По имени

# Линтинг
ruff check scripts/
ruff format scripts/

# Валидация
python3 scripts/validate_meta.py <path> [--lang ru|uk]
python3 scripts/validate_meta.py --all [--lang ru|uk]
python3 scripts/validate_content.py <path> "<keyword>" [--lang ru|uk]

# Аудит
python3 scripts/audit_keyword_consistency.py   # Ключи meta vs clean
python3 scripts/check_h1_sync.py               # H1 синхронизация

# Coverage audit (покрытие ключей в контенте)
python3 scripts/audit_coverage.py --slug {slug} --lang uk --verbose   # Одна категория
python3 scripts/audit_coverage.py --lang uk                            # Batch все UK
python3 scripts/audit_coverage.py --slug {slug} --lang uk --json       # JSON output
# CSV отчёты: reports/coverage_summary_*.csv, coverage_details_*.csv
```

---

## Семантика RU (Master CSV)

**Источник истины:** `data/ru_semantics_master.csv`

```bash
python3 scripts/merge_to_master.py --excel reports/new.xlsx  # Импорт
python3 scripts/validate_master.py                            # Валидация
python3 scripts/sync_semantics.py --apply                     # Синхронизация
```

---

## Ключевые модули

| Модуль | Назначение |
|--------|------------|
| `config.py` | SSOT: пути, thresholds, L3→slug маппинг |
| `keyword_utils.py` | Морфология RU/UK, KeywordMatcher, CoverageChecker |
| `text_utils.py` | Стопслова, clean_markdown, count_words |
| `seo_utils.py` | Front-matter, keyword counting, protected sections |
| `coverage_matcher.py` | Coverage audit: EXACT/NORM/LEMMA/SYNONYM matching |

```python
from scripts.keyword_utils import KeywordMatcher, CoverageChecker
from scripts.text_utils import get_stopwords, clean_markdown
from scripts.config import QUALITY_THRESHOLDS
```

**Coverage thresholds:** ≤5 ключей → 70%, 6-15 → 60%, >15 → 50%

---

## Parallel Workers

```bash
spawn-claude "W1: Описание.

Прочитай docs/plans/YYYY-MM-DD-plan.md — Task 1.

Для каждого slug: /semantic-cluster {slug}

Пиши лог в data/generated/audit-logs/W1_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

**Правила:**
- 1 воркер = 1 набор файлов (без пересечений)
- Воркеры пишут логи в `data/generated/audit-logs/`
- Коммиты делает только оркестратор
- tmux: `Ctrl+A, w` — список окон

Полная документация: **[docs/PARALLEL_WORKERS.md](docs/PARALLEL_WORKERS.md)**

---

## Навигация

| Что | Где |
|-----|-----|
| SEO-гайд | `docs/CONTENT_GUIDE.md` |
| Планы | `docs/plans/` |
| UK синоніми | `.claude/skills/uk-content-generator/references/uk-lsi-synonyms.md` |
| Логи воркеров | `data/generated/audit-logs/` |

---

## Правила

- **python3** — использовать вместо python
- **Context7 MCP** — для документации библиотек без запроса

---

**Version:** 56.0
