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

### Title формула (2026)

```
[ТОП ВЧ КЛЮЧ] — купити/купить, ціни/цены | Ultimate
```

ВЧ первым (Front-Loading) → "купити" включает Transactional Intent.

---

## Команды

```bash
# Тесты
uv run pytest                              # Все тесты
uv run pytest -k "test_meta"               # По имени
uv run pytest -n auto --dist loadfile      # Параллельно

# Линтинг
uv run ruff check src/
uv run ruff format src/

# Валидация
uv run python -m llm_keywords_pipeline.validate.meta <path> [--lang ru|uk]
uv run python -m llm_keywords_pipeline.validate.content <path> "<keyword>" [--lang ru|uk]
uv run python -m llm_keywords_pipeline.validate.density <path> [--lang ru|uk]
uv run python -m llm_keywords_pipeline.audit.water <path>

# Аудит
uv run python -m llm_keywords_pipeline.audit.keyword_consistency
uv run python -m llm_keywords_pipeline.audit.h1_sync
uv run python -m llm_keywords_pipeline.audit.coverage --slug {slug} --lang uk --verbose
```

---

## Ключевые модули (src/llm_keywords_pipeline/)

| Модуль | Назначение |
|--------|------------|
| `core/config.py` | SSOT: пути, thresholds, L3→slug маппинг |
| `core/keywords.py` | Морфология RU/UK, KeywordMatcher, CoverageChecker |
| `core/text.py` | Стопслова, clean_markdown, count_words |
| `core/seo.py` | Front-matter, keyword counting |
| `core/coverage.py` | Coverage audit: EXACT/NORM/LEMMA/SYNONYM |

```python
from llm_keywords_pipeline.core import KeywordMatcher, CoverageChecker
from llm_keywords_pipeline.core import get_stopwords, clean_markdown
from llm_keywords_pipeline.core import QUALITY_THRESHOLDS
```

**Coverage thresholds:** ≤5 ключей → 70%, 6-15 → 60%, >15 → 50%

**Nausea thresholds:** Classic ≤3.5 (target), >4.0 (BLOCKER).

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

- **uv run** — для всех Python команд (управляет зависимостями)
- **Context7 MCP** — для документации библиотек без запроса

---

## Quality Thresholds

| Метрика | Target | BLOCKER |
|---------|--------|---------|
| Stem density | ≤2.5% | >3.0% |
| Classic nausea | ≤3.5 | >4.0 |
| Academic nausea | ≥7% | <6% |
| Water | 40-65% | >70% |
| Word count | 400-700 | — |
