# Public Version Notes

This repository is a sanitized portfolio version of an internal SEO automation pipeline.
It is intended to show engineering approach and project structure without exposing
private operational data.

## Included

- Python package code under `src/llm_keywords_pipeline/`.
- Public pytest fixtures and tests.
- LLM prompt templates under `prompts/` as reference material.
- Local-only Docker Compose demo for MariaDB/Adminer.
- GitHub Actions CI for linting and tests.

## Omitted

- Production category datasets.
- Private SEO content and generated reports.
- External LLM orchestration and worker logs.
- Local agent prompts, signal files, and session logs.
- Deployment scripts and environment-specific infrastructure.

## Prompt Templates

The files in `prompts/` describe the prepare/produce/deliver workflow used around LLM
content generation. They are public because they show how the pipeline was designed, but
they are not standalone commands.

To run an equivalent workflow, a user would need compatible project data, an LLM
orchestrator, and the surrounding automation that is intentionally excluded here.

## Docker Demo

`docker-compose.yml` is a local development helper. It starts MariaDB and Adminer with
demo credentials from `.env.example`.

It is not a production deployment guide.
