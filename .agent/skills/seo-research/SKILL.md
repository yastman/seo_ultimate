---
name: seo-research
description: >-
    Generate contextual prompt for Perplexity Deep Research based on category semantics
    and product characteristics. Analyzes _clean.json and PRODUCTS_LIST.md,
    extracts types/forms/effects, creates RESEARCH_PROMPT.md.
    Use when: /seo-research {slug}, исследуй категорию, собери данные, ресёрч,
    подготовь промпт для ресёрча.
---

# SEO Research

Generate research prompt for Perplexity Deep Research.

## Quick Start

```
/seo-research {slug}
```

**Output:**

-   `categories/{slug}/research/RESEARCH_PROMPT.md` — load into Perplexity
-   `categories/{slug}/research/RESEARCH_DATA.md` — skeleton for results

---

## Workflow

```
/seo-research {slug}
├─► 1. Read _clean.json → keywords, entities, micro_intents, parent_id
├─► 2. Resolve section ID via data/category_ids.json
├─► 3. Find section in PRODUCTS_LIST.md by "## ... (ID: {id})"
├─► 4. Extract product insights (forms/volumes/effects from descriptions)
├─► 5. Generate RESEARCH_PROMPT.md
└─► 6. Create RESEARCH_DATA.md skeleton
```

---

## Data Sources

| File                                       | What to extract                   |
| ------------------------------------------ | --------------------------------- |
| `categories/{slug}/data/{slug}_clean.json` | keywords, entities, micro_intents |
| `data/category_ids.json`                   | slug → section ID                 |
| `data/generated/PRODUCTS_LIST.md`          | Products in section               |

---

## RESEARCH_PROMPT.md Structure

### Header

-   `# {Name} ({slug}) — SEO Research (Buyer Guide)`
-   **Context:** page type, category, parent_id, language

### Semantics (from \_clean.json)

-   Table `| Keyword | Volume |` — all keywords
-   **Entities:** list
-   **User questions:** micro_intents

### Product Insights (from PRODUCTS_LIST.md)

| Characteristic | From descriptions |
| -------------- | ----------------- |
| Forms          | gel, spray...     |
| Volumes        | 250ml, 500ml...   |
| Base           | water, solvent    |
| Effects        | matte, gloss      |

### Prompt for Perplexity (11 blocks)

1. **What and why** — definition, problem, main rule
2. **Types** — classification by INDEPENDENT axes
3. **How to choose** — scenarios "if X → take Y"
4. **How to apply** — prep → application → drying → finish
5. **Critical errors** — error | consequence | correct way
6. **Safety** — PPE, restrictions, risks
   6a. **Controversial claims** — request for PROOF
7. **Beginner FAQ** — 8-12 short Q→A
8. **Troubleshooting** — symptom | cause | solution
9. **Compatibility** — surface | ok? | conditions
10. **Practical numbers** — consumption, time, durability (with sources only)

---

## Block 2: Classification Rules

> ⚠️ **Critical:** Don't mix axes! Silicone is an active component, not carrier type.

**Typical axes for auto chemistry:**

**Axis 1 — Carrier (what evaporates):**

-   Water-based
-   Solvent-based

**Axis 2 — Active component (what remains):**

-   Silicone-based
-   Polymer-based
-   Natural oils

**Axis 3 — Finish/effect:**

-   Matte
-   Satin
-   Gloss / Wet look

---

## Block 6a: Controversial Claims

For each category, identify typical "myths" requiring verification.

```markdown
| Claim                     | Status | Source/Proof |
| ------------------------- | ------ | ------------ |
| "{controversial claim 1}" | ?      | Need source  |
| "{controversial claim 2}" | ?      | Need source  |
```

---

## Response Requirements (in prompt)

```markdown
1. **Every fact = source.** Format: claim → URL → quote.
2. **No source — don't write.** No data → "data not found".
3. **Source priority:**
    - Official manufacturer sites
    - Scientific articles / tests with measurements
    - Detailing forums — only for practical tips
4. **Language:** English and Russian.
5. **Relevance:** preferably 2020-2025.
```

---

## Done Criteria

-   [ ] Product Insights contains only explicitly stated info (no assumptions)
-   [ ] Block 2 uses independent classification axes
-   [ ] Block 6a contains controversial claims for this category
-   [ ] Output template added to end of prompt
-   [ ] RESEARCH_PROMPT.md ready for Perplexity

---

## Output

```
✅ Done:
- RESEARCH_PROMPT.md: categories/{slug}/research/RESEARCH_PROMPT.md
- RESEARCH_DATA.md: categories/{slug}/research/RESEARCH_DATA.md

Next step:
1. Open RESEARCH_PROMPT.md
2. Load ENTIRE file into Perplexity → Deep Research
3. Transfer results with sources to RESEARCH_DATA.md
```

---

**Version:** 13.0 — January 2026
