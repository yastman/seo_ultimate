---
name: category-init
description: >-
    Initialize new category folder structure for SEO content pipeline.
    Creates data/, meta/, content/, research/ folders and minimal JSON stubs.
    Use when: /category-init {slug}, создай категорию, инициализируй категорию,
    новая категория, подготовь папку для категории.
---

# Category Init

Initialize new category folder + minimal data for SEO content pipeline.

**Goal:** Category ready for `/generate-meta {slug}` → `/seo-research` → `/content-generator`.

---

## Source of Truth (SSOT)

Единственный источник правды: `Структура _Ultimate.csv`.

```bash
# After CSV changes:
python scripts/fix_csv_structure.py
python scripts/csv_to_readable_md.py
```

---

## Workflow

### Step 1: Validate Input

```
Input: slug (e.g., "aktivnaya-pena", "cherniteli-shin")
Validate:
- slug is kebab-case (lowercase, hyphens)
- slug exists in Структура _Ultimate.csv
- folder categories/{slug}/ exists or can be created
```

### Step 2: Ensure Checklist Exists

```bash
# Generate checklists if missing:
python scripts/generate_checklists.py

# Check: tasks/categories/{slug}.md
```

### Step 3: Create Category Folders

```text
categories/{slug}/
  data/
  meta/
  content/
  research/
```

### Step 4: Create `data/{slug}_clean.json`

**Option A (recommended):** From checklists:

```bash
python scripts/init_categories_from_checklists.py
```

**Option B (manual):**

```json
{
    "id": "{slug}",
    "name": "{Category Name}",
    "type": "category",
    "parent_id": "{parent_slug}",
    "keywords": [{ "keyword": "primary keyword", "volume": 1000 }],
    "synonyms": [
        { "keyword": "variant", "volume": 120, "use_in": "meta_only" }
    ],
    "entities": ["тип", "форма", "объём"],
    "micro_intents": ["как выбрать", "как использовать"],
    "source": "manual"
}
```

### Step 5: Create Template Stubs

**meta/{slug}\_meta.json:**

```json
{
    "slug": "{slug}",
    "language": "ru",
    "meta": { "title": "", "description": "" },
    "h1": "",
    "status": "template"
}
```

**content/{slug}\_ru.md:**

```markdown
# {H1}

<!-- Status: DRAFT -->
```

**research/RESEARCH_DATA.md:**

```markdown
# Research: {slug}

## Status: PENDING
```

### Step 6: Validate Output

-   [ ] JSON is valid
-   [ ] `keywords[0].keyword` exists (primary keyword)
-   [ ] Folders `meta/ content/ research/` exist
-   [ ] Stub files created

---

## Output

```
categories/{slug}/
  - data/{slug}_clean.json
  - meta/{slug}_meta.json (stub)
  - content/{slug}_ru.md (stub)
  - research/RESEARCH_DATA.md (stub)

Status: ready for /generate-meta
```

---

**Version:** 3.0 — January 2026
