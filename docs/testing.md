# Testing

The project uses `pytest` with `pytest.ini` as the source of truth for test discovery and
default options. Coverage settings live in `.coveragerc`.

## Default Checks

These are the commands used by the README and CI:

```bash
uv sync --frozen
uv run ruff check src tests
uv run mypy
uv run pytest
uv build
```

To inspect collection:

```bash
uv run pytest --collect-only -q
```

Coverage:

```bash
uv run pytest --cov=src/llm_keywords_pipeline --cov-report=term-missing
```

## Test Tiers

| Tier | Location | Purpose |
| --- | --- | --- |
| Unit | `tests/unit/` | Fast checks for isolated functions and deterministic behavior. |
| Integration | `tests/integration/` | File and pipeline interactions using fixtures or temporary paths. |
| Smoke | `tests/smoke/` | Broad sanity checks for important modules. |
| E2E | `tests/e2e/` | End-to-end scenarios when available. |
| Fixtures | `tests/fixtures/` | Synthetic public data used by tests. |

## Data-Required Tests

Some tests were originally designed to run against private category/content datasets.
The public repository does not include those datasets. Such tests should either use
public fixtures or skip with an explicit reason when private data is absent.

Skips caused by missing private data are acceptable only when they are intentional and
documented. They should not hide failures in the default fixture-backed suite.

## CI Parity

GitHub Actions runs the same default quality path documented above:

```bash
uv sync --frozen
uv run ruff check src tests
uv run mypy
uv run pytest --cov-fail-under=24
uv build
```

If local commands change, update README, this file, `tests/README.md`, and
`.github/workflows/ci.yml` together.
