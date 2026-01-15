---
name: generate-meta
description: >-
    Generate SEO meta tags (Title, Description, H1) for Ultimate.net.ua categories.
    Uses primary_keyword from _clean.json, determines Producer/Shop pattern,
    validates via validate_meta.py. Use when: /generate-meta {slug}, генерируй мета,
    создай мета теги, обнови мета.
---

# Meta Tag Generator

Generate SEO meta tags for Ultimate.net.ua categories.

---

## January 2026 Rules

| Parameter     | Value                                        |
| ------------- | -------------------------------------------- | --- |
| Title         | **30-60 chars** (unique part before `        | `)  |
| Title formula | `{primary_keyword} — купить` (Front-loading) |
| Description   | **100-160 chars**                            |
| H1            | **= {primary_keyword} БЕЗ "Купить"**         |

---

## Primary Keyword Source

From `categories/{slug}/data/{slug}_clean.json`:

**List-schema:**

```json
"keywords": [{"keyword": "воск для авто", "volume": 1000}]
```

→ `primary_keyword = keywords[0].keyword`

**Dict-schema:**

```json
"keywords": {"primary": [{"keyword": "очиститель дисков", "volume": 70}]}
```

→ `primary_keyword = keywords.primary[0].keyword`

---

## 🏭 Producer vs Shop Pattern

**Producer (has Ultimate products):**

```
{primary_keyword} от производителя Ultimate. {Types}. Опт и розница.
```

**Shop (no Ultimate products):**

```
{primary_keyword} в интернет-магазине Ultimate. {Types}.
```

**Shop categories (no Ultimate products):**
glina-i-avtoskraby, gubki-i-varezhki, cherniteli-shin, raspyliteli-i-penniki,
vedra-i-emkosti, kisti-dlya-deteylinga, shchetka-dlya-moyki-avto, shchetki-i-kisti,
malyarniy-skotch, polirovka, polirovalnye-krugi, polirovalnye-mashinki, oborudovanie

---

## 🚨 IRON RULE

**`{primary_keyword}` used VERBATIM in Title/H1/Description.**

Allowed: capitalize first letter only.

```
✅ Title: Воск для авто — купить, цены | Ultimate
✅ H1: Воск для авто

❌ Title: Автовоск — купить | Ultimate  ← CHANGED KEY!
❌ H1: Автомобильный воск              ← CHANGED KEY!
```

---

## Adaptive Title Formula

```
IF primary_keyword ≤ 20 chars:
  {primary_keyword} — купить в интернет-магазине Ultimate

ELSE:
  {primary_keyword} — купить, цены | Ultimate
```

---

## Workflow

1. **Read** `categories/{slug}/data/{slug}_clean.json` → extract primary_keyword
2. **Find products** in `data/generated/PRODUCTS_LIST.md` → types, forms, volumes
3. **Apply formulas** → Title, H1, Description
4. **Save** to `categories/{slug}/meta/{slug}_meta.json`
5. **Validate:** `python scripts/validate_meta.py {path}` → must PASS

---

## JSON Output Format

```json
{
    "slug": "{slug}",
    "language": "ru",
    "meta": {
        "title": "{primary_keyword} — купить в интернет-магазине Ultimate",
        "description": "{primary_keyword} от производителя Ultimate. {Types}. Опт и розница."
    },
    "h1": "{primary_keyword}",
    "keywords_in_content": {
        "primary": ["keyword1"],
        "secondary": ["keyword2", "keyword3"],
        "supporting": ["keyword4"]
    },
    "updated_at": "2026-01-15"
}
```

---

## Validation Checklist

### Title:

-   [ ] primary_keyword VERBATIM
-   [ ] 30-60 chars (unique part)
-   [ ] primary_keyword first (NOT "Купить" first!)

### Description:

-   [ ] 100-160 chars
-   [ ] Starts with primary_keyword
-   [ ] Correct pattern (Producer/Shop)
-   [ ] NO product names, brands, fluff

### H1:

-   [ ] = primary_keyword VERBATIM
-   [ ] NO "Купить/Купити"

---

## Output

```
categories/{slug}/meta/{slug}_meta.json (validated)

Status: ready for /seo-research
```

---

**Version:** 15.0 — January 2026
