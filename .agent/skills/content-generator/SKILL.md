---
name: content-generator
description: >-
    Generate SEO content in buyer guide format for Ultimate.net.ua categories.
    No links/citations in text. Soften controversial claims. Research as reference only.
    Use when: /content-generator {slug}, напиши текст, сгенерируй контент,
    создай контент для категории. IMPORTANT: use AFTER completing /seo-research.
---

# Content Generator

Generate SEO buyer guide content for categories.

## Quick Start

```
/content-generator {slug}
```

**Input:** `_clean.json` + `_meta.json` + research/\*.md (reference)
**Output:** `categories/{slug}/content/{slug}_ru.md`

---

## ⚠️ COMMERCIAL INTENT — TOP PRIORITY

Category content = **buying help**, NOT educational article.

| ✅ Commercial                  | ❌ Informational          |
| ------------------------------ | ------------------------- |
| "If need X → choose Y"         | "How X works"             |
| Comparison table               | Step-by-step instructions |
| "What to look for on label"    | "History of creation"     |
| Scenarios: beginner/pro/budget | Theory and principles     |

---

## Buyer Guide Structure (Required)

1. **First H2** = "Як вибрати" / "Сценарії використання"
2. **Table** = Task → Product type → Why
3. **Pattern** = "If X → recommendation Y" (minimum 3 times)
4. **Summary** = Clear recommendations by scenarios

---

## First Step: Determine Page Type

Check `parent_id` in `_clean.json`:

| Type             | Condition          | Template                    |
| ---------------- | ------------------ | --------------------------- |
| **Hub Page**     | `parent_id = null` | See references/hub-pages.md |
| **Product Page** | `parent_id ≠ null` | Buyer Guide (below)         |

---

## "No Proof" Mode (Default)

### What NOT to include:

| Forbidden                           | Why                                 |
| ----------------------------------- | ----------------------------------- |
| Links, citations, [1][2]            | Buyer guide, not scientific article |
| Percentages ("56% of detailers...") | Unverifiable                        |
| Exact research                      | "According to study X..." — no      |
| Brands in examples                  | Neutrality                          |

### Controversial Topics → Soften or Remove

| Topic          | ❌ Was                  | ✅ Became                                       |
| -------------- | ----------------------- | ----------------------------------------------- |
| "Dries rubber" | "Silicone dries rubber" | "Some formulas may affect elasticity over time" |
| Safety claims  | Categorical statements  | "may", "higher risk when...", "depends on..."   |

---

## Numbers Policy

| ❌ Don't write | ✅ Alternative                              |
| -------------- | ------------------------------------------- |
| "5-10 minutes" | "let absorb"                                |
| "20-30°C"      | "at room temperature"                       |
| "7-14 days"    | "usually needs update after several washes" |

---

## Workflow

```
1. Read data        → _clean.json (keywords, entities, micro_intents)
2. Check parent_id  → null = Hub Page, otherwise = Product Page
3. Read meta        → _meta.json (H1 + keywords_in_content)
4. Find research    → research/*.md (as reference, don't copy!)
5. Write content    → Hub: by processes | Product: buyer guide
6. Check density    → check_keyword_density.py (stem ≤2.5%)
7. Check nausea     → check_water_natasha.py (nausea ≤3.5)
8. Validate         → validate_content.py --mode seo
```

---

## Content Structure Template

```markdown
# {H1 from category name — NO "Купить"}

{Intro: what + why + key choice. 30-50 words. No "we offer".}

## Як вибрати: сценарії використання

| Task         | Product Type | Why         |
| ------------ | ------------ | ----------- |
| {Scenario 1} | {Type A}     | {Advantage} |
| {Scenario 2} | {Type B}     | {Advantage} |

**If need quick result** → {recommendation}

**If durability matters** → {recommendation}

## Types: differences by {key characteristic}

| Type | Characteristic 1 | Characteristic 2 | Who it suits |
| ---- | ---------------- | ---------------- | ------------ |

## What to look for on label

| Marker | Meaning | Who it suits |
| ------ | ------- | ------------ |

## FAQ

### {Question about CHOICE between types}?

{Answer 2-3 sentences with recommendation}

---

**Summary:**

-   **{Scenario 1}** → {product type}
-   **{Scenario 2}** → {product type}
-   **Main rule:** {key choice factor}
```

---

## Spam Control

### Thresholds

| Metric         | Target | Blocker      |
| -------------- | ------ | ------------ |
| Stem-group key | ≤2.5%  | >3.0% = SPAM |
| Classic nausea | ≤3.5   | >4.0         |
| Water          | 40-65% | >75%         |

### Validation Commands

```bash
# Keyword density
python scripts/check_keyword_density.py categories/{slug}/content/{slug}_ru.md

# Nausea and water
python scripts/check_water_natasha.py categories/{slug}/content/{slug}_ru.md

# Full validation
python scripts/validate_content.py categories/{slug}/content/{slug}_ru.md "{keyword}" --mode seo
```

---

## Validation Checklist

### Commercial Intent (MAIN)

-   [ ] First H2 = "Як вибрати" / "Scenarios"
-   [ ] Pattern "If X → Y" minimum 3 times
-   [ ] Table Task → Type → Why
-   [ ] Summary with scenario recommendations
-   [ ] NO "How to apply" section with 5+ steps

### Structure

-   [ ] H1 without "Купить"
-   [ ] Intro 30-50 words
-   [ ] Comparison table
-   [ ] FAQ 3-5 questions about CHOICE

### SEO/LSI

-   [ ] Primary keyword in H1 and intro
-   [ ] 3-4 entity-terms from \_clean.json
-   [ ] No "commercial" keywords in body (купить, цена)

---

## Output

```
✅ Content: categories/{slug}/content/{slug}_ru.md
✅ Validated: python scripts/validate_content.py {path} "{keyword}" --mode seo

Next step: /uk-content-init {slug}
```

---

**Version:** 2.7 — January 2026
