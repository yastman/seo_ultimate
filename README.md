# LLM Keywords Pipeline

[![CI](https://github.com/yastman/llm-keywords-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/yastman/llm-keywords-pipeline/actions/workflows/ci.yml)

Python toolkit for automating SEO content operations in e-commerce: keyword semantics,
meta tags, content validation, audits, extraction, and repair workflows.

This repository is a sanitized public portfolio version of a production-style internal
pipeline. It is structured to show the engineering approach, test strategy, and quality
gates without publishing private datasets or external orchestration.

## Problem

SEO content operations for large catalogs do not scale well when handled manually.
Teams need to prepare keyword semantics, generate meta tags, validate H1/H2 usage,
control keyword density, detect low-quality LLM phrasing, and keep multilingual content
consistent across many categories.

Without automation, these checks become slow, repetitive, and easy to miss. The main
risk is not just bad copy; it is silent regression across hundreds of generated or
edited pages.

## Solution

`llm-keywords-pipeline` collects the repeatable parts of this workflow into a tested
Python package:

- validate meta tags, page content, keyword density, structure, and language-specific
  SEO rules;
- audit generated content for coverage, H1 consistency, wateriness, brand mentions,
  semantic gaps, and cannibalization risks;
- extract, compare, and synchronize keyword data across source files;
- generate supporting artifacts such as SQL dumps, meta files, checklists, and semantic
  review outputs;
- keep LLM prompt templates for prepare/produce/deliver stages as public reference
  material.

The public repo does not include private category datasets or production orchestration.
Tests use fixtures and synthetic examples.

## What This Demonstrates

This project is useful as an engineering portfolio because it shows:

- package organization with a `src/` layout and typed package marker;
- data-pipeline thinking around ingestion, validation, audit, repair, and sync stages;
- practical NLP usage for Russian and Ukrainian SEO content checks;
- defensive validation of LLM-generated content;
- pytest coverage across unit, integration, smoke, and fixture-driven scenarios;
- modern Python tooling with `uv`, `ruff`, `mypy` configuration, coverage, and CI;
- public-repo cleanup discipline: private data is omitted and limitations are explicit.

## Core Capabilities

| Area | What it does |
| --- | --- |
| Validation | Checks meta JSON, content structure, keyword density, SEO headings, language rules, and master keyword data. |
| Audits | Reviews coverage, H1 sync, brand/city mentions, wateriness, semantic quality, unused terms, and cannibalization risks. |
| Generation | Produces meta artifacts, SQL exports, semantic review files, catalog JSON, and checklists. |
| Extraction | Extracts category and keyword data from project files for downstream validation and comparison. |
| Repair and sync | Provides utilities for cleanup, migration, keyword ordering, volume updates, and master-data merges. |
| Prompt workflow | Documents reference LLM templates for preparing briefs, producing drafts, and delivery checks. |

## Architecture

The package is organized by workflow responsibility:

| Package | Responsibility |
| --- | --- |
| `core` | Shared config, text processing, keyword utilities, coverage helpers, and SEO primitives. |
| `validate` | Quality gates for content, meta files, density, master data, SEO structure, and Ukrainian content. |
| `audit` | Higher-level audits for content quality, coverage, H1 sync, NER brand checks, semantic gaps, and wateriness. |
| `generate` | Artifact generators for meta files, SQL, checklists, semantic review, and catalog JSON. |
| `extract` | Keyword/category extraction helpers. |
| `fix` | Repair utilities for duplicates, misplaced files, missing keywords, and legacy structures. |
| `sync` | Sync and migration helpers for keyword and semantic data. |
| `analyze` | Category, duplicate, synonym, order, and meta analysis tools. |
| `compare` | Comparison helpers for raw/clean keyword data and master data. |
| `batch` | Batch-oriented orchestration helpers. |

See [docs/architecture.md](docs/architecture.md) for the public architecture boundary and
legacy/internal notes.

## Quality and Verification

The repository uses a small but explicit quality stack:

- `pytest` for unit, integration, smoke, and fixture-based checks;
- `pytest-cov` with coverage settings in `.coveragerc`;
- `ruff` for linting and import hygiene;
- `mypy` configuration for stricter typing policy;
- GitHub Actions CI for repeatable lint/test validation.

Default local and CI checks:

```bash
uv sync
uv run ruff check src tests
uv run pytest
```

More detail is in [docs/testing.md](docs/testing.md).

## Quick Start

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

The Compose stack is local-only demo infrastructure for MariaDB/Adminer. It is not a
production deployment recipe.

## Public Version Notes

This repository intentionally excludes:

- production category datasets and private SEO content;
- external LLM orchestration used around the prompt templates;
- generated reports, local logs, agent signals, and runtime artifacts;
- private deployment automation.

The `prompts/` directory is kept as reference material because it shows the intended
LLM-assisted workflow. The templates are not standalone commands.

See [docs/public-version.md](docs/public-version.md) for details.

## Repository Map

```text
src/llm_keywords_pipeline/   Python package
tests/                       pytest suite and fixtures
prompts/                     LLM workflow templates
docs/                        architecture, testing, and public-version notes
.github/workflows/ci.yml     CI lint/test workflow
pyproject.toml               package metadata and tool configuration
pytest.ini                   pytest configuration
.coveragerc                  coverage configuration
docker-compose.yml           optional local database demo
```

## License

MIT. See [LICENSE](LICENSE).
