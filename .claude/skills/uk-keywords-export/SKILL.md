---
name: uk-keywords-export
description: Export all RU keywords from categories, translate to Ukrainian, deduplicate, and create MD file for frequency collection. Use when /uk-keywords-export, export UK keywords, export keywords for frequency, prepare UK keywords, підготуй ключі для частотності, експортуй ключі для UK.
---

# UK Keywords Export

Export RU keywords from all categories, translate to Ukrainian using TRANSLATION_RULES, deduplicate, and write to `data/generated/UK_KEYWORDS_FOR_FREQUENCY.md`.

## Workflow

### Step 1: Run Export Script

```bash
python3 .claude/skills/uk-keywords-export/scripts/export_uk_keywords.py
```

Script actions:
1. Glob `categories/**/data/*_clean.json`
2. Extract `keywords`, `synonyms`, `variations` arrays
3. Filter structural artifacts (synonyms_*, primary, etc.)
4. Translate RU → UK using built-in dictionary
5. Deduplicate
6. Write to `data/generated/UK_KEYWORDS_FOR_FREQUENCY.md`

### Step 2: Review Output

```bash
head -50 data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
wc -l data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
```

Expected output format:
```markdown
# UK Keywords for Frequency Check

Generated from N categories.
Total: M unique keywords.

---

активна піна
активна піна для авто
антибітум
...
```

### Step 3: Use for Frequency Collection

Copy keywords from `data/generated/UK_KEYWORDS_FOR_FREQUENCY.md` to frequency check tool (e.g., Serpstat, Ahrefs).

## Translation Rules

Script uses built-in dictionary based on [uk-content-init/TRANSLATION_RULES.md](../uk-content-init/TRANSLATION_RULES.md):

**Key translations:**
```
резина     → гума
средство   → засіб
мойка      → миття/мийка
стекло     → скло
чернитель  → чорнитель
очиститель → очищувач
купить     → купити
автохимия  → автохімія
```

**Preserved (no translation):**
- pH, PPF, APC, SiO2
- Brand names
- Tornador

## Output

- **File:** `data/generated/UK_KEYWORDS_FOR_FREQUENCY.md`
- **Format:** One keyword per line, alphabetically sorted
- **Source:** All `*_clean.json` files from categories

---

**Version:** 1.0
