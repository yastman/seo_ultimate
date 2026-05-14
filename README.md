# LLM Keywords Pipeline

**Automated SEO content generation pipeline for e-commerce, powered by Claude LLM.**

Generates production-ready meta tags, buyer guides, and OpenCart SQL for 100+ product categories (RU + UK) using a skills-based pipeline architecture.

---

## Problem

Manual SEO content creation for 50+ product categories requires days of repetitive work per cycle. Keyword research, competitor analysis, meta tag generation, content writing, and deployment — each step is labor-intensive and error-prone when done manually. This pipeline automates the entire workflow, ensuring consistent quality and SEO best practices across all categories.

---

## Key Features

- **Skills-based pipeline** — 15+ Claude slash commands orchestrate the full SEO workflow
- **Bilingual (RU + UK)** — Parallel pipelines: 30 RU + 54 UK product categories
- **Production quality** — 348 tests, linting, coverage metrics, and quality gates at every stage
- **Automated deployment** — Generates SQL dumps ready for OpenCart import
- **Validation suite** — Meta tag validation, keyword density checks, academic nausea analysis, water/stem detection

---

## Architecture

```
CSV → Init → Meta → Research → Content → Review → QA → Deploy
              ↓ (parallel)
        UK content pipeline
```

**Pipeline stages:** Category initialization → meta tag generation → SEO competitor research → content generation (buyer guides) → content review/auto-fix → quality gate validation → OpenCart SQL deployment.

---

## Tech Stack

**LLM Orchestration:** Claude (Anthropic), Skills-based commands
**Backend:** Python 3.12+, uv package manager
**NLP:** pymorphy3, natasha, spacy, razdel
**Validation:** Custom SEO analyzers (keyword density, nausea, water, H1 sync, coverage)
**Testing:** pytest (578 tests), pytest-cov, pytest-xdist
**Linting:** ruff, mypy
**Infrastructure:** Docker, docker-compose

---

## Quick Start

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Validate meta tags for a category
uv run python -m llm_keywords_pipeline.validate.meta categories/avtoshampuni/meta/avtoshampuni_meta.json

# Validate content quality
uv run python -m llm_keywords_pipeline.validate.content categories/avtoshampuni/content/avtoshampuni_ru.md "active foam"

# Run linting
uv run ruff check src/
```

---

## Project Structure

```
├── src/llm_keywords_pipeline/   # Python package
│   ├── core/                    # Config, keywords, text, SEO utilities
│   ├── validate/                # Meta, content, density validators
│   ├── audit/                   # Coverage, H1, keyword consistency
│   ├── generate/                # SQL, meta, checklist generators
│   ├── analyze/                 # Category analysis, duplicates
│   ├── extract/                 # Keyword extraction tools
│   ├── fix/                     # Data repair utilities
│   └── sync/                    # Migration and sync tools
├── categories/                  # Category data (RU)
├── uk/                          # Category data (UK)
├── tests/                       # pytest test suite
├── docs/                        # Documentation
├── data/                        # Raw and generated data
├── pyproject.toml               # Project config and dependencies
└── docker-compose.yml           # Docker deployment
```

---

## Metrics

- **Categories:** 30 RU + 54 UK (84 L3 category slugs)
- **Modules:** 65 Python modules
- **Tests:** 348 passing
- **Quality thresholds:** stem density ≤2.5%, classic nausea ≤3.5, water 40-65%

---

## License

MIT — see [LICENSE](LICENSE)
