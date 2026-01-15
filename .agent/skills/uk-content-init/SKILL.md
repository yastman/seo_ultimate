---
name: uk-content-init
description: >-
    Initialize Ukrainian version for categories with translated keywords from RU source.
    Use when: /uk-content-init {slug}, підготуй UK, створи українську версію,
    переклади ключі на українську.
---

# Ukrainian Content Initializer

Initialize UK category structure with translated keywords from RU source.

---

## January 2026 Rules

| Parameter   | Value                                      |
| ----------- | ------------------------------------------ |
| Title       | **50-60 chars**, "Купити" REQUIRED         |
| Description | **120-160 chars**                          |
| H1          | **NO "Купити"** — commercial only in Title |
| Intro       | **30-60 words**                            |

---

## Input Validation

```text
Prerequisites:
- [ ] categories/{slug}/data/{slug}_clean.json EXISTS
- [ ] categories/{slug}/meta/{slug}_meta.json EXISTS
- [ ] categories/{slug}/content/{slug}_ru.md EXISTS (recommended)
- [ ] uk/categories/{slug}/ does NOT exist (or force overwrite)

If RU version missing, run /content-generator {slug} first.
```

---

## Workflow

### Step 1: Read RU Source

```bash
categories/{slug}/data/{slug}_clean.json
categories/{slug}/meta/{slug}_meta.json
```

Extract: Keywords (primary, secondary), Meta (types, forms), Category name

### Step 2: Translate Keywords

**Quick reference:**

```
резина     → гума       (IMPORTANT!)
средство   → засіб
мойка      → миття/мийка
стекло     → скло
чернитель  → чорнитель
очиститель → очищувач
купить     → купити     (meta_only!)
```

**Keep unchanged:** pH, PPF, APC, HF, SiO2, антимошка, антибітум

### Step 3: Create Folder Structure

```text
uk/categories/{slug}/
├── data/
│   └── {slug}_clean.json    # Translated keywords
├── meta/
│   └── {slug}_meta.json     # UK meta tags
├── content/
│   └── {slug}_uk.md         # (empty for now)
└── research/
    └── CONTEXT.md           # Research context
```

### Step 4: Write UK Data JSON

```json
{
  "slug": "{slug}",
  "language": "uk",
  "category_name_uk": "{Назва категорії}",
  "keywords": {
    "primary": [
      {"keyword": "{UK}", "keyword_ru": "{RU}", "volume": N}
    ],
    "commercial": [
      {"keyword": "{UK}", "keyword_ru": "{RU}", "volume": N, "use_in": "meta_only"}
    ]
  },
  "translation_notes": {
    "adapted_terms": ["резина→гума"],
    "kept_original": ["pH", "PPF"]
  }
}
```

### Step 5: Write UK Meta JSON

**Title formula:** `Купити {primary} в Україні | Ultimate`
**Description formula:** `{Category} від виробника Ultimate. {Types}. Опт і роздріб.`

```json
{
    "language": "uk",
    "slug": "{slug}",
    "h1": "{Primary keyword}",
    "meta": {
        "title": "Купити {Primary} в Україні | Ultimate",
        "description": "{Category} від виробника Ultimate. {Types}. Опт і роздріб."
    }
}
```

### Step 6: Write CONTEXT.md

```markdown
# Research Context: {category_name_uk}

## Primary Keyword

**UK:** {keyword}
**RU:** {original}

## Keywords

| Type    | UK  | RU  | Volume |
| ------- | --- | --- | ------ |
| primary | ... | ... | ...    |

## Content Requirements

-   300-700 words
-   H1 = primary keyword (NO "Купити")
-   Intro: 30-60 words

## Next Steps

1. Web search: "{primary_uk} як обрати"
2. Write uk/categories/{slug}/content/{slug}\_uk.md
```

### Step 7: Validate

```bash
python scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
```

---

## Common Mistakes

| Wrong                | Right                   |
| -------------------- | ----------------------- |
| резина → резина      | резина → гума           |
| H1 с "Купити"        | H1 БЕЗ "Купити"         |
| Title без "Купити"   | Title С "Купити"        |
| Skip commercial flag | Add `use_in: meta_only` |

---

## Output

```
uk/categories/{slug}/
  - data/{slug}_clean.json (translated)
  - meta/{slug}_meta.json (UK meta)
  - content/{slug}_uk.md (empty)
  - research/CONTEXT.md (context)

Status: ready for UK content writing
```

---

**Version:** 4.0 — January 2026
