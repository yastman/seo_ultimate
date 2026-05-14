# Public Portfolio Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `llm-keywords-pipeline` credible as a public portfolio repository for employers.

**Architecture:** Keep package code under `src/`, keep public docs small and direct, and make `README.md` the employer-facing entry point. Treat production data, orchestration, logs, and generated artifacts as excluded from the public version.

**Tech Stack:** Python 3.12, uv, pytest, pytest-cov, ruff, mypy config, GitHub Actions, Docker Compose demo.

---

## File Map

- Modify `.gitignore`: ignore local orchestration artifacts and avoid hiding useful `.txt` files globally.
- Modify `README.md`: rewrite project positioning, problem, solution, architecture, quality, quick start, limitations.
- Create `docs/architecture.md`: package map and stable-vs-legacy boundary.
- Create `docs/testing.md`: test tiers, commands, CI parity, data-required skips.
- Create `docs/public-version.md`: what is intentionally omitted and why.
- Modify `tests/README.md`: point to `docs/testing.md` and keep commands aligned.
- Modify `pyproject.toml`: add PEP 621 metadata and remove duplicate pytest/coverage config.
- Modify `pytest.ini`: make test discovery match documented default suite.
- Modify `.coveragerc`: keep as coverage source of truth.
- Modify `.github/workflows/ci.yml`: keep CI aligned with README commands.
- Modify `.env.example` and `docker-compose.yml`: local-only demo clarity.
- Modify `prompts/README.md`, `prompts/prepare.md`, `prompts/produce.md`, `prompts/deliver.md`: frame prompts as reference templates.
- Modify selected tests and low-risk source comments/imports only where required to remove obvious public-readiness issues.

## Task 1: Public Hygiene

**Files:**
- Modify: `.gitignore`
- Keep untracked for now: `.codex/`, `.signals/`, `logs/`
- Commit later with all cleanup changes.

- [ ] Add `.codex/`, `.signals/`, and `logs/` to `.gitignore`.
- [ ] Replace broad `*.txt` ignore with narrower local-output patterns, preserving `requirements*.txt`.
- [ ] Verify `git status --short --ignored` shows `.codex/`, `.signals/`, `logs/`, and `artifacts/` ignored or intentionally untracked.

## Task 2: Documentation Rewrite

**Files:**
- Modify: `README.md`
- Create: `docs/architecture.md`
- Create: `docs/testing.md`
- Create: `docs/public-version.md`
- Modify: `tests/README.md`

- [ ] Rewrite README with sections: problem, solution, core capabilities, architecture, quality and verification, quick start, public-version notes, license.
- [ ] Remove stale exact module/test counts and non-working commands.
- [ ] Add `docs/architecture.md` with package boundaries and data flow.
- [ ] Add `docs/testing.md` with exact default commands, optional/data-required test notes, and CI parity.
- [ ] Add `docs/public-version.md` with omitted private datasets, omitted orchestration, and prompt-template status.
- [ ] Update `tests/README.md` to point to `docs/testing.md` and avoid contradictory commands.

## Task 3: Config and Metadata Alignment

**Files:**
- Modify: `pyproject.toml`
- Modify: `pytest.ini`
- Modify: `.coveragerc`
- Modify: `.github/workflows/ci.yml`
- Modify: `requirements.txt`
- Modify: `requirements-dev.txt`

- [ ] Add package metadata to `pyproject.toml`: description, readme, license, authors, keywords, classifiers, URLs.
- [ ] Remove `[tool.pytest.ini_options]` from `pyproject.toml`.
- [ ] Remove `[tool.coverage.*]` blocks from `pyproject.toml`.
- [ ] Keep pytest configuration in `pytest.ini`.
- [ ] Keep coverage configuration in `.coveragerc`, including branch coverage.
- [ ] Make `pytest.ini` collect the documented default suite.
- [ ] Align CI commands with README: `uv sync`, `uv run ruff check src tests`, `uv run pytest`.
- [ ] Either align `requirements*.txt` with `pyproject.toml` or clearly document them as compatibility snapshots.

## Task 4: Docker Demo Clarity

**Files:**
- Modify: `docker-compose.yml`
- Modify: `.env.example`
- Modify: `README.md`
- Modify: `docs/public-version.md`

- [ ] Replace the broken README compose command with `docker compose up`.
- [ ] Bind MariaDB and Adminer to localhost by default.
- [ ] Avoid `adminer:latest`; use a pinned public tag.
- [ ] Make seed SQL optional or document it as optional.
- [ ] Remove unused env variables or explain them.

## Task 5: Prompt Template Framing

**Files:**
- Modify: `prompts/README.md`
- Modify: `prompts/prepare.md`
- Modify: `prompts/produce.md`
- Modify: `prompts/deliver.md`

- [ ] Add a short English summary block to each prompt template.
- [ ] Mark each prompt as a non-executable reference template requiring external orchestration and project data.
- [ ] Keep Russian operational content where useful, but remove confusing model/version claims if they read as mandatory.

## Task 6: Low-Risk Source/Test Triage

**Files:**
- Modify: `tests/unit/test_check_ner_brands.py`
- Modify: `src/llm_keywords_pipeline/validate/test_infra.py` if needed.
- Modify targeted public-facing docstrings/comments that reference removed `scripts/`, `tasks/`, or `.claude` paths.

- [ ] Remove stale `scripts` sys.path hack from `tests/unit/test_check_ner_brands.py`.
- [ ] Convert fixed temp files in `tests/unit/test_check_ner_brands.py` to `tmp_path`.
- [ ] Make `validate/test_infra.py` messaging resilient to missing optional public docs, or document it as legacy if tests already pass.
- [ ] Replace obvious public-facing examples that call removed `scripts/...` with package/module examples where low-risk.
- [ ] Do not perform a broad architectural refactor in this pass.

## Task 7: Verification

**Files:**
- No planned source changes unless verification reveals a blocker.

- [ ] Run `uv run ruff check src tests`.
- [ ] Run `uv run pytest --collect-only -q`.
- [ ] Run `uv run pytest`.
- [ ] Scan tracked public files for `.codex`, `.signals`, `logs/`, `.claude`, `scripts/`, `tasks/`, `reports/`, `/home/`, `password`, `token`, and `api_key`.
- [ ] Verify documented shell commands are either runnable or clearly marked optional/illustrative.
- [ ] Review `git status --short` and stage only intentional public files.

