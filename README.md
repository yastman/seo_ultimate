# LLM Keywords Pipeline

[![CI](https://github.com/yastman/llm-keywords-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/yastman/llm-keywords-pipeline/actions/workflows/ci.yml)

A Python pipeline for turning messy SEO keyword operations into repeatable validation,
audit, and generation workflows.

Solves the quality-control problem that appears when SEO content and LLM drafts scale
beyond manual review.

```bash
uv sync
uv run ruff check src tests
uv run pytest
```

Works with Python 3.12+ and `uv`.

---

## Why I Built This

SEO content for e-commerce catalogs is repetitive until it suddenly is not.

One category is easy to review by hand. Hundreds of categories are different: keyword
semantics drift, generated meta tags miss primary terms, H1/H2 structure regresses,
LLM drafts repeat generic phrases, and multilingual variants stop matching the source
intent.

The hard part is not generating text. The hard part is making generated or edited
content reviewable.

This project packages that review layer: deterministic checks, NLP-aware keyword
matching, audit utilities, repair helpers, and prompt templates around a practical
content pipeline.

---

## How It Works

The pipeline follows a simple loop.

### 1. Extract

Read category and keyword data from structured files, normalize it, and prepare it for
validation or generation.

### 2. Generate

Create supporting artifacts: meta JSON, SQL exports, semantic review files, catalogs,
checklists, and LLM workflow outputs.

### 3. Validate

Run deterministic quality gates for meta tags, content structure, keyword density,
headings, language-specific rules, and master keyword data.

### 4. Audit

Inspect higher-level content quality: semantic coverage, H1 synchronization, wateriness,
brand/city mentions, unused terms, and cannibalization risks.

### 5. Repair and Sync

Use focused utilities to clean up duplicates, missing keywords, ordering issues,
migration artifacts, and master-data drift.

---

## Core Capabilities

| Area | What it does |
| --- | --- |
| Validation | Checks meta JSON, content structure, keyword density, SEO headings, language rules, and master keyword data. |
| Audits | Reviews coverage, H1 sync, brand/city mentions, wateriness, semantic quality, unused terms, and cannibalization risks. |
| Generation | Produces meta artifacts, SQL exports, semantic review files, catalog JSON, and checklists. |
| Extraction | Extracts category and keyword data from project files for downstream validation and comparison. |
| Repair and sync | Provides cleanup, migration, keyword ordering, volume update, and master-data merge utilities. |
| Prompt workflow | Documents prepare/produce/deliver templates for an LLM-assisted content workflow. |

---

## Why It Works

### Deterministic checks around probabilistic output

LLMs can draft content quickly, but their output still needs stable quality gates. This
project treats generated text as input to validate, not as something to trust blindly.

### NLP-aware SEO validation

Keyword checks need to handle Russian and Ukrainian morphology, not only exact string
matches. The package includes language-aware text utilities, stemming/lemmatization
helpers, stopword handling, and semantic coverage checks.

### Testable pipeline pieces

The code is split into package modules for `core`, `validate`, `audit`, `generate`,
`extract`, `fix`, `sync`, `analyze`, `compare`, and `batch`. Tests cover isolated
utilities, fixture-backed validation, integration flows, and smoke checks.

### Honest public boundary

The public repository keeps the engineering structure and fixtures, but excludes private
category datasets, generated reports, deployment automation, and external orchestration.
That makes the project inspectable without pretending to be a plug-and-play SaaS.

---

## Getting Started

Prerequisites: Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/yastman/llm-keywords-pipeline.git
cd llm-keywords-pipeline

uv sync
uv run ruff check src tests
uv run pytest
```

Coverage:

```bash
uv run pytest --cov=src/llm_keywords_pipeline --cov-report=term-missing
```

Optional local database demo:

```bash
cp .env.example .env
docker compose up
```

The Compose stack starts MariaDB and Adminer on localhost. It is a local demo, not a
production deployment recipe.

---

## Commands

Main verification path:

| Command | Purpose |
| --- | --- |
| `uv sync` | Install the locked Python environment. |
| `uv run ruff check src tests` | Run lint and import checks. |
| `uv run pytest` | Run the default test suite. |
| `uv run pytest --collect-only -q` | Inspect collected tests. |

Most pipeline modules can also be explored with `uv run python -m
llm_keywords_pipeline.<package>.<module>`, but some generation and migration utilities
expect the private data layout that is intentionally omitted from this public version.

---

## Project Structure

```text
src/llm_keywords_pipeline/   Python package
tests/                       pytest suite and public fixtures
prompts/                     LLM workflow reference templates
docs/                        architecture, testing, and public-version notes
.github/workflows/ci.yml     CI lint/test workflow
pyproject.toml               package metadata and tool configuration
pytest.ini                   pytest configuration
.coveragerc                  coverage configuration
docker-compose.yml           optional local database demo
```

---

## Documentation

| Doc | What's in it |
| --- | --- |
| [Architecture](docs/architecture.md) | Package map, workflow boundaries, stable vs legacy surface. |
| [Testing](docs/testing.md) | Test tiers, default commands, CI parity, data-required skips. |
| [Public Version](docs/public-version.md) | What is included, what is omitted, and why prompts remain public. |
| [Prompt Templates](prompts/README.md) | Prepare/produce/deliver LLM workflow templates. |

---

## Public Version

This repository intentionally excludes production datasets and external LLM
orchestration. The included tests use fixtures and synthetic examples.

The `prompts/` directory is preserved as reference material: it shows how the surrounding
LLM-assisted workflow was structured, but the templates are not standalone commands.

---

## License

MIT. See [LICENSE](LICENSE).

---

LLM output is easy to generate. This project makes it reviewable.
