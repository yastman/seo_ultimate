# Research Workflow

This document describes the public contract for the SEO research stage. Production
category data, generated research outputs, and local automation files are intentionally
not included in this repository.

## Purpose

The research stage turns clustered keyword data into a factual brief for category
content. It exists so an SEO text is based on product facts, user intent, competitor
patterns, and source-backed research instead of generic LLM filler.

## Inputs

The full workflow used these inputs:

| Input | Purpose |
| --- | --- |
| `categories/{slug}/data/{slug}_clean.json` | Clustered keywords, primary terms, entities, micro-intents, and category metadata. |
| Product/catalog export | Product characteristics such as form, volume, base, effect, pH/type, dilution, and use cases. |
| SERP TOP-10 export | Search-result URL overlap and competitor URL signals for intent and cluster decisions. |
| Category mapping data | Connects a category slug to the relevant product/catalog section. |

In the public package, the runnable code keeps the keyword JSON, checklist, validation,
and prompt-template pieces. Production exports and local orchestration files are omitted.

## Stage Output

The full workflow produced two files under the category folder:

```text
categories/{slug}/research/
  RESEARCH_PROMPT.md   prompt for an external web-research tool
  RESEARCH_DATA.md     source-backed research result used as the content brief
```

`RESEARCH_PROMPT.md` was generated from the clustered keyword JSON plus product/catalog
insights. It was designed to be pasted into Perplexity Deep Research or another
web-enabled LLM workflow.

`RESEARCH_DATA.md` stored the research result: sources, extracted facts, product
classification, how-to notes, common mistakes, safety limits, FAQ ideas,
troubleshooting, compatibility, and practical numbers.

## How It Fits The Pipeline

```text
keyword export / CSV
        |
        v
raw category JSON
        |
        v
_clean.json with clustered keywords
        |
        v
RESEARCH_PROMPT.md for external web research
        |
        v
RESEARCH_DATA.md as category brief
        |
        v
content draft and meta generation
        |
        v
coverage, density, water, nausea, structure, and meta validation
```

The public code confirms this stage in the checklist generator:
`src/llm_keywords_pipeline/generate/checklists.py` tracks `research/RESEARCH_DATA.md`,
creates the Stage 03 Research checklist, and includes the research stage in pipeline
status reporting.

The content prompt in `prompts/produce.md` treats research as context for drafting:
keywords are read first, web research is performed by the external workflow, and any
category research folder is used for competitor and content-structure context.

## Public Boundary

This repository does not currently ship a runnable external research runner or production
`RESEARCH_PROMPT.md` / `RESEARCH_DATA.md` category outputs. It keeps the public contract,
reference prompts, checklist stage, and validation code so the architecture remains
inspectable without exposing operational data.
