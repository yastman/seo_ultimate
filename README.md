# LLM Keywords Pipeline

**Python toolkit for automated SEO content generation and validation for e-commerce.**

A modular Python pipeline that validates, generates, and audits SEO content — meta tags, buyer guides, keyword semantics — with NLP-based quality gates.

---

## Key Features

- **SEO validation suite** — Meta tag validation, keyword density checks, academic nausea analysis, water/stem detection, H1 sync verification
- **Content generation** — Meta tag generation, SQL dump generation, semantic review, checklist generation
- **Audit tools** — Keyword consistency, NER brand detection, semantic coverage, cannibalization, H1 audit
- **Analysis & extraction** — Category analysis, keyword extraction, duplicate detection, synonym analysis
- **Data repair utilities** — CSV structure fixes, missing keyword detection, orphan cleanup, migration tools
- **Production quality** — 348 tests, linting, coverage metrics

---

## Tech Stack

| Category | Tools |
|----------|-------|
| Language | Python 3.12+ |
| Package manager | uv |
| NLP | pymorphy3, natasha, spacy, razdel |
| Validation | Custom SEO analyzers |
| Testing | pytest (348 tests), pytest-cov, pytest-xdist |
| Linting | ruff, mypy |
| Infrastructure | Docker, docker-compose |

---

## Quick Start

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Run linting
uv run ruff check src/
```

---

## Project Structure

```
├── src/llm_keywords_pipeline/   # Python package (65 modules)
│   ├── core/                    # Config, keywords, text, SEO utilities
│   ├── validate/                # Meta, content, density validators
│   ├── audit/                   # Coverage, H1, keyword consistency, water
│   ├── generate/                # SQL, meta, checklist generators
│   ├── analyze/                 # Category analysis, duplicates, synonyms
│   ├── extract/                 # Keyword extraction tools
│   ├── fix/                     # Data repair and migration utilities
│   ├── sync/                    # Sync helpers
│   ├── compare/                 # Diff and comparison tools
│   ├── batch/                   # Batch processing
│   └── tools/                   # Misc utilities
├── tests/                       # pytest test suite (37 test files)
├── pyproject.toml               # Project config and dependencies
└── docker-compose.yml           # Docker deployment
```

---

## License

MIT — see [LICENSE](LICENSE)
