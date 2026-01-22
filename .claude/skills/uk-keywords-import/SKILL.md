---
name: uk-keywords-import
description: Import Ukrainian keywords with frequency from CSV file, group by category, create JSON for UK pipeline. Use when /uk-keywords-import, імпортуй ключі, завантаж частотність, загрузи украинские ключи, импорт UK keywords.
---

# UK Keywords Import

Import Ukrainian keywords with search volume from CSV and group by RU category slugs.

---

## Input Format

CSV with `keyword,volume` columns (auto-detects delimiter: `,`, `;`, `\t`):

```csv
keyword,volume
чорнитель шин,1200
активна піна для миття авто,800
засіб для скла,500
```

Alternative column names supported: `query`, `freq`, `frequency`, `ключ`, `частота`.

---

## Workflow

### Step 1: Validate Input

```bash
# Check CSV exists and has correct format
head -5 {csv_path}
```

Verify columns: keyword + volume (numeric).

### Step 2: Run Import Script

```bash
python .claude/skills/uk-keywords-import/scripts/import_uk_keywords.py \
    {csv_path} \
    --output uk/data \
    --verbose
```

Options:
- `--output`, `-o`: Output directory (default: `uk/data`)
- `--mapping`, `-m`: Custom category mapping JSON
- `--verbose`, `-v`: Show unmatched keywords

### Step 3: Review Output

Script creates `uk/data/uk_keywords.json`:

```json
{
  "source": "keywords.csv",
  "total_keywords": 150,
  "matched_keywords": 120,
  "unmatched_keywords": 30,
  "categories": {
    "cherniteli-shin": {
      "count": 15,
      "total_volume": 5600,
      "keywords": [
        {"keyword": "чорнитель шин", "volume": 1200},
        {"keyword": "чорніння шин", "volume": 800}
      ]
    }
  },
  "unmatched": [
    {"keyword": "щось невідоме", "volume": 100}
  ]
}
```

### Step 4: Handle Unmatched Keywords

If unmatched > 20%:
1. Review unmatched list in output JSON
2. Create custom mapping file
3. Re-run with `--mapping` option

Custom mapping format:

```json
{
  "new-category-slug": ["ключ1", "ключ2", "ключ3"]
}
```

---

## Category Matching

Script uses built-in UK keyword patterns for these categories:

| Category Slug | UK Patterns |
|--------------|-------------|
| aktivnaya-pena | активна піна, піна для миття |
| cherniteli-shin | чорнитель шин, чорніння шин |
| ochistiteli-diskov | очищувач дисків |
| ochistiteli-stekol | очищувач скла, засіб для скла |
| antidozhd | антидощ, гідрофобне покриття |
| antimoshka | антимошка, засіб від мошки |
| voski | віск, автовіск |
| sredstva-dlya-kozhi | засіб для шкіри |
| ... | (30+ categories) |

Full mapping in `scripts/import_uk_keywords.py` -> `CATEGORY_KEYWORDS`.

---

## Output

```
uk/data/uk_keywords.json
  - Grouped by category slug
  - Sorted by volume (descending)
  - Unmatched keywords preserved for review
```

---

## Next Steps

After import:
1. Review unmatched keywords
2. Run `/uk-content-init {slug}` for categories with keywords
3. Use imported data for UK meta generation

---

**Version:** 1.0
