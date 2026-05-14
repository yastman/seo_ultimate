# Public Portfolio Cleanup Design

Date: 2026-05-14
Project: `llm-keywords-pipeline`
Goal: make the repository credible as a public portfolio project for employers.

## Context

`llm-keywords-pipeline` is a Python 3.12 toolkit for automating SEO content operations
around e-commerce keyword semantics, meta tags, content validation, audits, extraction,
repair utilities, and LLM prompt workflows.

The repository has already been partially sanitized for public release: private data and
large internal folders were removed, core package code lives under `src/`, tests are
present, and a GitHub Actions workflow exists in the working tree. The next step is not
to turn the project into a polished open-source product. The goal is to make it look
intentional, honest, and technically strong to a hiring manager or senior engineer
reviewing it quickly.

## Target Reader

The primary reader is an employer evaluating engineering ability. They should understand
within a few minutes:

- what real automation problem the project solves;
- how the package is structured;
- how quality is enforced with tests, linting, fixtures, and CI;
- what is included in the public version and what was intentionally removed;
- which parts are stable package code versus legacy/internal migration utilities.

## Design Principles

- Be honest about scope. Do not claim this is a plug-and-play SaaS or complete OSS
  product if the public version excludes production datasets and orchestration.
- Make the root directory calm. A public portfolio repo should not expose agent logs,
  transient signals, local artifacts, or stale internal notes.
- Prefer fewer, clearer docs. The repo needs a strong README and a few compact support
  docs, not a sprawling documentation tree.
- Align commands with reality. Every command in README/CI/docs should be executable or
  explicitly marked as illustrative.
- Separate portfolio polish from product rewrites. Fix the presentation and obvious
  public risks first; deeper CLI/API redesign can be a later milestone.

## Current Audit Summary

### Root and Configuration

Issues found:

- `README.md` has portfolio value, but its structure reads more like a generic package
  overview than an employer-facing project narrative.
- `README.md` includes a broken compose helper command: `uv run compose up`.
- `pyproject.toml` and `pytest.ini` both define pytest settings, creating config drift.
- Coverage settings are split between `.coveragerc` and `pyproject.toml`.
- `requirements.txt` and `requirements-dev.txt` appear stale relative to
  `pyproject.toml`.
- `pyproject.toml` lacks public package metadata such as `description`, `readme`,
  `license`, `authors`, `keywords`, classifiers, and URLs.
- `docker-compose.yml` is useful as a demo, but should be framed as local-only and avoid
  deceptive production signals.
- `.gitignore` does not yet explicitly ignore current local agent artifacts such as
  `.codex/`, `.signals/`, and `logs/`.

### Hidden, Generated, and CI Files

Issues found:

- `.github/workflows/ci.yml` is untracked; CI is therefore not part of the committed
  public repository yet.
- `.codex/`, `.signals/`, and `logs/` are untracked local orchestration artifacts and
  should not be published.
- `artifacts/` is already ignored and should remain ignored.

### Source Package

Issues found:

- Several modules still contain hardcoded local paths or assumptions about removed
  project folders.
- Some modules retain coupling to old `scripts/`, `tasks/`, or `.claude` locations.
- One-off migration and repair scripts are mixed into the public package surface,
  making the architecture look noisier than it needs to.
- CLI strategy is unclear: many modules have `if __name__ == "__main__"` entrypoints,
  but no stable `[project.scripts]` surface exists.
- Public exports are inconsistent across packages such as `validate`, `audit`, and
  `tools`.
- Some Russian/internal comments are acceptable for domain context, but public-facing
  docs should provide English framing.

### Tests

Issues found:

- `pytest.ini` excludes `tests/smoke` and root-level `tests/*.py` from default test
  discovery.
- Test documentation says `uv run pytest` runs all tests, but current config does not
  collect every visible test file.
- Some tests retain stale `scripts/` path assumptions.
- Some integration/smoke tests skip when private category data is absent. This is fine
  only if documented as a data-required suite.
- A few tests use fixed temp filenames in the repository root, which is not ideal for
  parallel runs.

### Prompts

Issues found:

- `prompts/` can be valuable portfolio evidence because it shows the LLM workflow around
  prepare/produce/deliver stages.
- The prompt files are mostly Russian and read like operational playbooks. Public readers
  need short English summaries at the top.
- Prompt files should be clearly marked as reference templates that require external
  orchestration and project data.

## Proposed Repository Shape

Keep the public root focused:

```text
.
├── .github/workflows/ci.yml
├── docs/
│   ├── architecture.md
│   ├── public-version.md
│   └── testing.md
├── prompts/
│   ├── README.md
│   ├── prepare.md
│   ├── produce.md
│   └── deliver.md
├── src/llm_keywords_pipeline/
├── tests/
├── README.md
├── LICENSE
├── pyproject.toml
├── pytest.ini
├── .coveragerc
├── .env.example
├── .gitignore
├── docker-compose.yml
└── uv.lock
```

Do not publish:

- `.codex/`
- `.signals/`
- `logs/`
- `artifacts/`
- runtime caches and local virtual environments

## README Design

The README should become the main employer-facing document.

Recommended sections:

1. Title and one-line positioning.
2. Problem: manual SEO content operations do not scale.
3. Solution: tested Python pipeline for generation, validation, audits, extraction, and
   repair workflows.
4. What this demonstrates: package architecture, data-pipeline thinking, NLP tooling,
   validation quality gates, CI, and public cleanup discipline.
5. Core capabilities grouped by domain.
6. Architecture overview with a table of package areas.
7. Quality and verification: pytest, coverage, ruff, fixtures, CI.
8. Quick start with only working commands.
9. Public version notes and limitations.
10. License.

The README should avoid exact module/test counts unless generated during the same pass.
Exact counts become stale quickly and weaken trust when wrong.

## Supporting Docs Design

Add compact docs only where they reduce README length:

- `docs/architecture.md`: package map, stable versus legacy/internal boundaries, data
  flow from inputs to validation/audit outputs.
- `docs/testing.md`: test tiers, how to run them, why some data-required tests may skip,
  and what CI runs.
- `docs/public-version.md`: what was removed from the public repo, why prompts remain,
  and what external data/orchestration is not included.

Do not add contribution, governance, or large OSS process docs unless the repository is
later positioned as a community package.

## Source Cleanup Design

This pass should not rewrite the full package architecture. It should remove the most
visible public-readiness problems:

- Replace README/docstring examples that still point to `scripts/` with
  `python -m llm_keywords_pipeline...` examples where the module is runnable.
- Remove or quarantine `.claude` and removed-folder imports from runtime code.
- Make hardcoded project roots configurable where the module is still documented as part
  of the public package.
- Mark legacy migration utilities as legacy/internal in docs if they are not cleaned up
  immediately.
- Avoid presenting legacy utilities as stable public API.

If deeper code movement is needed, defer it to a separate refactor plan so this portfolio
cleanup remains reviewable.

## Test and Verification Design

The public quality story should be true:

- Keep `pytest.ini` as the only pytest configuration source.
- Keep `.coveragerc` as the only coverage configuration source.
- Remove pytest and coverage configuration blocks from `pyproject.toml` during cleanup
  so `pyproject.toml` remains focused on package metadata, dependencies, build settings,
  ruff, and mypy.
- Align `uv run pytest`, README, and CI so they run the same intended default suite.
- Include smoke tests or explicitly document them as optional.
- Mark data-required tests clearly and document expected skips when private datasets are
  absent.
- Use `tmp_path` for tests that write temporary files.
- Run:
  - `uv run ruff check src tests`
  - `uv run pytest`
  - optionally `uv run pytest --collect-only -q` to verify collection matches docs.

## Dependency and Metadata Design

Use `pyproject.toml` and `uv.lock` as the source of truth.

Recommended changes:

- Add PEP 621 metadata: description, README, license, authors, keywords, classifiers,
  and project URLs.
- Keep `requirements*.txt` only if they are regenerated and clearly documented as
  compatibility snapshots.
- If the snapshots are stale or hard to maintain, remove them in a separate explicit
  cleanup commit or label them as legacy compatibility files.
- Align README dependency instructions with `uv sync`.

## Docker Design

Treat Docker Compose as a local demo helper, not production infrastructure.

Recommended changes:

- Replace broken README compose command with `docker compose up`.
- Bind Adminer and database ports to localhost by default.
- Avoid `latest` for public-facing images where practical.
- Make optional seed/backup mounting clear; do not require a missing `backup.sql` for a
  successful demo startup.
- Document that credentials in `.env.example` are safe local demo defaults only.

## Implementation Plan

### Phase 1: Public Hygiene

- Update `.gitignore` for `.codex/`, `.signals/`, and `logs/`.
- Keep `.github/workflows/ci.yml` and prepare it for commit.
- Ensure generated artifacts remain ignored.
- Search for obvious secrets, local paths, stale internal folder references, and broken
  public commands.

### Phase 2: README Rewrite

- Rewrite README around problem, solution, capabilities, architecture, and verification.
- Remove stale exact counts and non-working commands.
- Explain the public version honestly.
- Link to supporting docs and prompt templates.

### Phase 3: Supporting Docs

- Add `docs/architecture.md`.
- Add `docs/testing.md`.
- Add `docs/public-version.md`.
- Update `tests/README.md` only if it remains in the repository; it should point to
  `docs/testing.md` or contain the same command set without contradiction.
- Keep each file concise and employer-readable.

### Phase 4: Config Alignment

- Keep `pytest.ini` for pytest settings and remove duplicate pytest config from
  `pyproject.toml`.
- Keep `.coveragerc` for coverage settings and remove duplicate coverage config from
  `pyproject.toml`.
- Align README, CI, and local test commands.
- Add missing package metadata to `pyproject.toml`.
- Decide whether `requirements*.txt` are maintained compatibility snapshots or removed
  later.

### Phase 5: Source and Test Triage

- Remove public-facing references to removed `scripts/`, `tasks/`, and `.claude` paths
  where they are easy and low-risk.
- Document or quarantine legacy utilities that are not stable public API.
- Fix test discovery/documentation mismatch.
- Convert fixed temp-file tests to `tmp_path`.

### Phase 6: Verification

- Run lint.
- Run tests.
- Run collection check.
- Re-run internal/path/secrets search with an explicit scan for `.codex`, `.signals`,
  `logs/`, `.claude`, `scripts/`, `tasks/`, `reports/`, `/home/`, `password`, `token`,
  and `api_key` in tracked public files.
- Inventory documented shell commands in README and docs, then verify each command is
  runnable or explicitly marked as optional/illustrative.
- Review `git status --short` to make sure only intentional public files are staged.

## Acceptance Criteria

The cleanup is complete when:

- README contains these sections: problem, solution, core capabilities, architecture,
  quality and verification, quick start, public-version notes, and license.
- Every shell command shown in README and docs is either verified during the cleanup or
  explicitly labeled optional/illustrative.
- README, CI, `docs/testing.md`, and retained `tests/README.md` document the same default
  lint/test commands.
- The root directory contains no local orchestration artifacts.
- CI is committed and matches documented commands.
- Test and coverage configuration do not contradict each other.
- `docs/public-version.md` explicitly lists omitted private datasets, omitted external
  orchestration, and the status of `prompts/` as reference templates.
- Prompts are framed as reference templates.
- A tracked-file scan for `.codex`, `.signals`, `logs/`, `.claude`, `scripts/`,
  `tasks/`, `reports/`, and `/home/` has no unexplained public-facing hits.
- Data-required tests are either included with fixtures or explicitly marked/documented
  as optional/skipped when private datasets are absent.
- `ruff` and the intended pytest suite pass, or any remaining skips are documented and
  intentional.

## Out of Scope

- Rewriting the entire CLI strategy.
- Publishing to PyPI.
- Building a full sample dataset if a minimal fixture story is enough.
- Replacing the existing NLP stack.
- Turning the project into a community open-source package with contribution governance.
