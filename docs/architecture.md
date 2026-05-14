# Architecture

`llm-keywords-pipeline` is organized as a workflow toolkit for SEO content operations.
The public package keeps related responsibilities in separate subpackages so validation,
auditing, generation, extraction, repair, and synchronization can evolve independently.

## Workflow

```text
source keyword/category data
        |
        v
extract / compare / sync
        |
        v
generate content artifacts and review files
        |
        v
validate meta, content, headings, density, and language rules
        |
        v
audit coverage, semantic quality, brands, H1 sync, wateriness
        |
        v
repair or regenerate affected artifacts
```

## Package Boundaries

| Package | Role | Public-readiness note |
| --- | --- | --- |
| `core` | Shared config, text, keyword, coverage, and SEO helpers. | Stable foundation for other modules. |
| `validate` | Deterministic checks for SEO/content quality. | Main quality-gate layer. |
| `audit` | Higher-level quality and consistency audits. | Useful for demonstrating pipeline quality controls. |
| `generate` | Artifact generation for meta, SQL, catalogs, semantic review, and checklists. | Some commands need project-specific input data. |
| `extract` | Extracts category and keyword data from project files. | Input paths are project-dependent. |
| `fix` | Repair utilities for duplicate, missing, misplaced, and older data formats. | Data-layout dependent support tools. |
| `sync` | Synchronizes keyword and semantic data across files. | Public use requires compatible data layout. |
| `analyze` | Category, synonym, duplicate, order, and meta analysis. | Mostly diagnostic tooling. |
| `compare` | Compares raw/clean/master keyword representations. | Data-layout dependent. |
| `batch` | Batch helpers for multi-category workflows. | Orchestration layer, not a stable public CLI. |

## Supported Public Surface

The strongest public surface is the validation/audit/core code and its tests. Some
generation, repair, sync, and migration modules are data-layout dependent and remain in
the public version to show the broader pipeline shape.

When reading this repository as a portfolio project, treat those modules as evidence of
real operational tooling rather than a fully supported public API. The README and test
suite focus on the parts that can be run without production datasets.

## Data and Orchestration

Production category data, content files, and external LLM orchestration are intentionally
not part of this repository. The public version uses fixtures and compact examples so the
package can be linted and tested without access to production inputs.
