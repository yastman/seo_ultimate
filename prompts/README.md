# Prompts — Workflow Templates

Prompt templates for the 3-stage LLM-driven content workflow. Most templates are in
Russian because the primary target content is in Russian.

**Note:** These prompts depend on external infrastructure (an LLM orchestrator, seed
data sources, and a `categories/` data directory). They are preserved as public
reference templates and are not directly runnable from a fresh clone.

These files are included to show the staged content workflow behind the pipeline. They
are not required for running the public test suite.

## Structure

| File                          | Stage     | Description                         |
| ----------------------------- | --------- | ----------------------------------- |
| **[prepare.md](prepare.md)**   | PREPARE   | Category init: folders, keywords     |
| **[produce.md](produce.md)**   | PRODUCE   | Content generation (RU) + meta       |
| **[deliver.md](deliver.md)**   | DELIVER   | Validation + packaging               |

## Workflow

```
Orchestrator
    ├──→ PREPARE  → Folders + JSON
    ├──→ PRODUCE  → Content + Meta
    └──→ DELIVER  → Validation + Deliverables
```

## Parameters

Each template accepts slug, category name, and tier as input placeholders, for example
`{slug}` and `{tier}`. Replace them with actual values before using the template in an
LLM-assisted workflow.

## Limitations

- The templates reference pipeline modules (e.g. `validate.content`) that live in
  `src/llm_keywords_pipeline/`. In the current package layout, these are importable
  Python modules, not standalone command files.
- Some template references to `CONTENT_GUIDE.md` and spec versions are historical
  and have no corresponding files in this repository. Adapt as needed.
