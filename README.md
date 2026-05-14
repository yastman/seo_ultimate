<div align="center">

# LLM Keywords Pipeline

**English · [Русский](README.ru.md) · [Українська](README.uk.md)**

**Keyword clustering and SEO content QA pipeline for Russian and Ukrainian e-commerce pages.**

**Turns a raw keyword list into clustered SEO groups, LLM-ready briefs, and measurable content checks: coverage, density, spam, wateriness, and nausea.**

<p>
  <a href="https://github.com/yastman/llm-keywords-pipeline/actions/workflows/ci.yml">
    <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/yastman/llm-keywords-pipeline/ci.yml?branch=main&label=tests&style=for-the-badge">
  </a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="uv" src="https://img.shields.io/badge/package%20manager-uv-6E56CF?style=for-the-badge">
  <img alt="Ruff" src="https://img.shields.io/badge/lint-ruff-46A758?style=for-the-badge">
  <img alt="Pytest" src="https://img.shields.io/badge/tests-pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white">
  <img alt="NLP" src="https://img.shields.io/badge/NLP-RU%20%2F%20UK-0E9F6E?style=for-the-badge">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-111111?style=for-the-badge">
</p>

</div>

```bash
uv sync --frozen
uv run ruff check src tests
uv run mypy
uv run pytest
uv build
```

---

## What Problem It Solves

SEO specialists often start with a messy keyword export: duplicates, synonyms, mixed
commercial and informational intent, raw search volumes, competitor notes, and a text
that may or may not cover the required semantics.

Doing that by hand does not scale. The hard part is not writing one category text. The
hard part is turning keyword research into a repeatable workflow:

- group raw keywords into usable clusters;
- separate primary, secondary, supporting, and commercial keywords;
- use TOP-10 SERP overlap and competitor research artifacts when they exist;
- write or generate content from the clustered brief;
- check the finished text against the expected keyword set;
- catch over-optimization before the page is shipped.

This repository is that workflow packaged as a Python project.

---

## Core Workflow

### 1. Adapt keyword exports into JSON

The workflow starts from a keyword export, usually CSV or a structured keyword list.
That raw input is adapted into category JSON files so the rest of the pipeline can work
with one contract instead of spreadsheets.

The project keeps several paths for that handoff:

- raw category JSON, such as `categories/{slug}/data/{slug}.json`;
- clustered clean JSON, such as `categories/{slug}/data/{slug}_clean.json`;
- master CSV sync into `_clean.json`;
- CSV restore/compare utilities for drift, missing keywords, and changed volumes.

The D+E fallback pattern prefers `_clean.json` first, then raw parsed JSON, then CSV
fallback. In practice, `_clean.json` is the main working artifact for the next stages.

### 2. Cluster semantics

Keywords are grouped into practical SEO roles:

| Group | Purpose |
| --- | --- |
| `primary` | Main target terms for H1, intro, and core page intent. |
| `secondary` | Related terms that expand the page without changing intent. |
| `supporting` | Long-tail and contextual phrases for semantic depth. |
| `commercial` | Buy/price/order modifiers, often used for meta or commercial signals. |

Duplicate and synonym cleanup tools normalize close variants, choose stronger winners by
volume and phrase quality, and remove weaker duplicates.

### 3. Generate category research

The original workflow also supports a separate SERP TOP-10 file: keywords can be checked
by URL intersection in Google results. If two queries share enough TOP-10 URLs, they can
belong to the same cluster or synonym group; if their TOP-10 results differ, the keyword
is treated as a separate search intent.

In the original orchestrated workflow, after clustering, the primary keyword, semantic
groups, entities, micro-intents, and product insights were used to generate a
`categories/{slug}/research/RESEARCH_PROMPT.md` file for an external web-research tool,
for example Perplexity Deep Research or an LLM agent with web search. The research
result was then saved into `categories/{slug}/research/RESEARCH_DATA.md`.

That research file is not just an attachment. It becomes the category brief for the
next stage: product facts, competitor structure, user intent, content gaps, required
blocks, FAQ ideas, and risks that should shape the final SEO text.

The public package does not ship the old Perplexity runner or private research outputs.
It keeps the research stage as prompt/checklist/reference material and as a pipeline
artifact checked by task generation.

### 4. Produce SEO briefs and content

The `prompts/` directory documents a prepare/produce/deliver flow for LLM-assisted
writing. It reads clustered keywords, primary terms, entity dictionaries, content rules,
and optional research context before drafting or reviewing category content.

### 5. Validate the written text

The validators check whether the final markdown actually satisfies the brief:

- primary keyword in H1 and intro;
- morphology-aware keyword coverage for Russian and Ukrainian;
- split coverage for core and commercial keywords;
- keyword density and stem-based over-spam detection;
- water percentage, classic nausea, academic nausea, and lemma repetition;
- H1/H2 structure, intro quality, blacklist terms, brand/city mentions, and meta sync.

---

## Why It Is Useful

### For an SEO specialist

It converts keyword research into a controlled checklist: what to target, what to keep
out of the body, what to include in meta, and what to fix after the text is written.

### For LLM-assisted content

It treats LLM output as a draft that must pass deterministic checks. The model can write,
but the pipeline verifies coverage, structure, and over-optimization.

### For multilingual catalogs

The code handles Russian and Ukrainian text with language-aware tokenization,
stopwords, stemming, lemmatization, and morphology-aware keyword matching.

---

## Capabilities

| Area | What it does |
| --- | --- |
| Keyword JSON adaptation | Converts CSV/master/raw keyword data into category JSON and `_clean.json` artifacts used by the pipeline. |
| Keyword clustering | Builds clean keyword groups from raw/CSV/category data and separates intent roles. |
| SERP TOP-10 overlap | Uses search-result URL intersections to decide whether keywords belong in one cluster or represent different intents. |
| Synonym cleanup | Detects near-duplicates and normalizes competing keyword variants. |
| Research prompt workflow | Turns clustered keywords/entities/product insights into a research prompt contract; public docs preserve `RESEARCH_PROMPT.md` → `RESEARCH_DATA.md` as the brief workflow. |
| Content validation | Checks H1, intro, headings, keyword coverage, meta sync, and language-specific rules. |
| Density and spam | Finds exact, partial, stem, and substring overuse with warning/spam thresholds. |
| Water and nausea | Calculates Advego-like water, classic nausea, academic nausea, and lemma repetition. |
| Generation | Produces meta artifacts, SQL exports, semantic review files, catalog JSON, and checklists. |
| Repair and sync | Updates volumes, restores clean JSON from CSV, merges master keyword data, and fixes ordering or misplaced terms. |

---

## Project Structure

```text
src/llm_keywords_pipeline/
  analyze/      category and metadata analysis for LLM briefs
  audit/        water, nausea, coverage, blacklist, H1, and quality audits
  core/         keyword matching, morphology, SEO rules, text utilities
  generate/     meta, checklist, semantic review, catalog, and export tools
  validate/     content, meta, heading, density, language, and data validators
  sync/         CSV/master-data synchronization and _clean.json repair
  fix/          focused cleanup utilities
  compare/      keyword distribution and dataset comparison helpers
tests/          pytest suite and public fixtures
prompts/        prepare/produce/deliver LLM workflow templates
docs/           architecture, testing, and public-version notes
```

---

## Getting Started

Prerequisites: Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/yastman/llm-keywords-pipeline.git
cd llm-keywords-pipeline

uv sync --frozen
uv run ruff check src tests
uv run mypy
uv run pytest
```

Run a public fixture through one of the packaged CLI tools:

```bash
uv run llm-keywords-audit-brands tests/fixtures/valid_content.md --json
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

## Documentation

| Doc | What's in it |
| --- | --- |
| [Architecture](docs/architecture.md) | Package map, workflow boundaries, stable vs legacy surface. |
| [Testing](docs/testing.md) | Test tiers, default commands, CI parity, data-required skips. |
| [Research Workflow](docs/research-workflow.md) | How clustered keywords became `RESEARCH_PROMPT.md`, `RESEARCH_DATA.md`, and a content brief. |
| [Public Version](docs/public-version.md) | What is included, what is omitted, and why prompts remain public. |
| [Prompt Templates](prompts/README.md) | Prepare/produce/deliver LLM workflow templates. |

---

## Public Boundary

This public repository keeps the engineering structure, tests, fixtures, and prompt
workflow, but excludes private production datasets, generated reports, old SERP TOP-10
exports, and external LLM orchestration. Some utilities and docs reference the original
private data layout and are preserved to show the real project architecture.

---

## License

MIT. See [LICENSE](LICENSE).

---

Raw keywords are easy to export. This project turns them into clustered SEO work that
can be written, checked, and improved.
