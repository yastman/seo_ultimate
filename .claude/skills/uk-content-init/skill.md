---
name: uk-content-init
description: Use when preparing Ukrainian version for categories like antimoshka, cherniteli-shin, aktivnaya-pena, or when you see підготуй UK, створи українську версію, переклади ключі на українську. (project)
---

# Ukrainian Content Initializer

Initialize UK category structure with translated keywords from RU source.

**Documentation:**

- [docs/CONTENT_GUIDE.md](../../../docs/CONTENT_GUIDE.md) — SEO Guide v20.0 (December 2025 rules)
- [TRANSLATION_RULES.md](TRANSLATION_RULES.md) — Dictionary RU→UK, intent mapping

---

## Input Validation

Before initializing UK version, verify:

```text
Prerequisites:
- [ ] categories/{slug}/data/{slug}_clean.json EXISTS
- [ ] categories/{slug}/meta/{slug}_meta.json EXISTS
- [ ] categories/{slug}/content/{slug}_ru.md EXISTS (recommended)
- [ ] uk/categories/{slug}/ does NOT exist (or force overwrite)

If RU version missing, run /content-generator {slug} first.
```

---

## December 2025 Rules

| Parameter   | Value                                      |
| ----------- | ------------------------------------------ |
| Title       | **50-60 chars**, "Купити" REQUIRED         |
| Description | **120-160 chars**                          |
| H1          | **NO "Купити"** — commercial only in Title |
| Intro       | **30-60 words**                            |

---

## Workflow

### Step 1: Read RU Source

```bash
# Read RU data
categories/{slug}/data/{slug}_clean.json
categories/{slug}/meta/{slug}_meta.json
```

Extract:

- Keywords (primary, secondary, supporting, commercial)
- Meta (types, forms, volumes)
- Category name

### Step 2: Translate Keywords

Apply rules from [TRANSLATION_RULES.md](TRANSLATION_RULES.md):

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

**Keep unchanged:**

- pH, PPF, APC, HF, SiO2
- антимошка, антибітум

### Step 3: Create Folder Structure

```bash
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
    "secondary": [...],
    "supporting": [...],
    "commercial": [
      {"keyword": "{UK}", "keyword_ru": "{RU}", "volume": N, "use_in": "meta_only"}
    ]
  },
  "translation_notes": {
    "adapted_terms": ["резина→гума"],
    "kept_original": ["pH", "PPF"],
    "intent_preserved": true
  }
}
```

### Step 5: Write UK Meta JSON

**Title formula:** `Купити {primary} в Україні | Ultimate`
**Description formula:** `{Категорія} від виробника Ultimate. {Типи}. {Призначення}. Опт і роздріб.`

```json
{
    "language": "uk",
    "slug": "{slug}",
    "h1": "{Primary keyword} для авто",
    "meta": {
        "title": "Купити {Primary} в Україні | Ultimate",
        "description": "{Категорія} від виробника Ultimate. {Типи}. Опт і роздріб."
    },
    "types": ["тип1", "тип2"],
    "volumes": ["0.5л", "1л", "5л"]
}
```

### Step 6: Write CONTEXT.md

```markdown
# Research Context: {category_name_uk}

## Primary Keyword

**UK:** {keyword}
**RU:** {original}

## Keywords

| Type      | UK  | RU  | Volume |
| --------- | --- | --- | ------ |
| primary   | ... | ... | ...    |
| secondary | ... | ... | ...    |

## Content Requirements

-   300-700 words
-   H1 = primary keyword (NO "Купити")
-   Intro: 30-60 words
-   1+ table, 1+ warning

## Next Steps

1. Web search: "{primary_uk} як обрати"
2. Write uk/categories/{slug}/content/{slug}\_uk.md
```

### Step 7: Validate Output

```bash
python scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
```

**Validation checks:**

- [ ] UK folder structure created
- [ ] Keywords translated correctly (резина→гума)
- [ ] Commercial keywords marked as meta_only
- [ ] Title: 50-60 chars, contains "Купити"
- [ ] Description: 120-160 chars
- [ ] H1: NO "Купити"
- [ ] CONTEXT.md created

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

## Common Mistakes

| Wrong                | Right                      |
| -------------------- | -------------------------- |
| резина → резина      | резина → гума              |
| Copy RU numbers      | "діапазон + див. етикетку" |
| Latin in H1          | Only in body text          |
| Skip commercial flag | Add `use_in: meta_only`    |
| H1 с "Купити"        | H1 БЕЗ "Купити"            |
| Title без "Купити"   | Title С "Купити"           |

---

## Next Step

After uk-content-init, write content to `uk/categories/{slug}/content/{slug}_uk.md`.

Then run `/quality-gate {slug}` to validate both RU and UK versions.

---

**Version:** 4.0 — December 2025 (with validation)
**Docs:** [TRANSLATION_RULES.md](TRANSLATION_RULES.md)
