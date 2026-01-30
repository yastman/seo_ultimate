# Shared Validation Checklist

Common validation rules for RU and UK categories.

---

## Data Validation (_clean.json)

- [ ] Valid JSON
- [ ] Has primary keywords with volumes
- [ ] Keywords clustered (primary, secondary, supporting)
- [ ] Total keywords: 10-15

---

## Meta Validation (_meta.json)

| Field | Rule | Blocker |
|-------|------|---------|
| Title | 50-60 chars | YES |
| Title | Contains commercial keyword | YES |
| Title | Primary keyword at start | YES |
| Description | 120-160 chars | YES |
| Description | No emojis | YES |
| H1 | No commercial keyword | YES |
| H1 | ≠ Title | YES |

---

## Content Validation

### Structure
- [ ] Has H1 (first line starts with #)
- [ ] H1 = `name` from _clean.json (plural form)
- [ ] Intro: 30-60 words (buyer guide, NOT definition)
- [ ] Has comparison table (3 columns)
- [ ] Has "If X → Y" patterns (≥3)
- [ ] Has FAQ (3-5 questions, no duplicates with tables)
- [ ] **NO how-to sections** (BLOCKER!)
- [ ] Word count: 400-700

### SEO
- [ ] Primary keyword in first 100 words
- [ ] Secondary keywords used naturally
- [ ] No brand names/prices
- [ ] Stem group ≤2.5% (BLOCKER >3.0%)
- [ ] Classic nausea ≤3.5 (BLOCKER >4.0)
- [ ] Academic ≥7% (WARNING <7%)
- [ ] Water 40-65% (WARNING >75%)

---

## Pass Criteria

**PASS** requires ALL of:

| Criterion | Required |
|-----------|----------|
| Data valid | YES |
| Title 50-60 chars | YES |
| Title has commercial | YES |
| Description 120-160 | YES |
| H1 no commercial | YES |
| Content structured | YES |
| No brands/prices | YES |

**FAIL** if ANY check fails.

---

## Commands

```bash
# JSON validity
python3 -c "import json; json.load(open('{path}'))"

# Meta validation
python3 scripts/validate_meta.py {meta_path}

# Content validation
python3 scripts/validate_content.py {content_path} "{primary}" --mode seo

# Keyword density
python3 scripts/validate_density.py {content_path}

# Water/nausea
python3 scripts/check_water_natasha.py {content_path}

# SEO structure
python3 scripts/validate_seo.py {content_path} "{primary}"
```
