# UK Keywords Redistribution Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Перерозподілити UK ключі з uk/data/uk_keywords.json на основі RU категорій (categories/**/data/*_clean.json) як референсу.

**Architecture:**
1. Витягти RU keywords з усіх 50 категорій — це ground truth для mapping'у
2. Створити скрипт який матчить UK keywords до RU категорій за семантичною подібністю
3. Оновити uk/data/uk_keywords.json з правильним розподілом
4. Перегенерувати uk/categories/*/data/*_clean.json

**Tech Stack:** Python, fuzzy matching (rapidfuzz), existing RU _clean.json files

---

## Problem Analysis

Поточна проблема: import_uk_keywords.py має hardcoded CATEGORY_KEYWORDS mapping, який не відповідає реальним RU keywords. Наприклад:
- `aksessuary` отримав "автокосметика" (має бути в moyka-i-eksterer)
- `kvik-deteylery` отримав "полимер для авто" (не той продукт)
- `ukhod-za-kozhey` отримав "очищувач кондиціонера" (це про кліматику, не шкіру)

**Рішення:** Використати RU _clean.json keywords як базу для matching.

---

## Task 1: Extract RU Keywords Mapping

**Files:**
- Create: `scripts/extract_ru_keywords_mapping.py`
- Read: `categories/**/data/*_clean.json` (50 files)
- Output: `data/generated/ru_keywords_mapping.json`

**Step 1: Write the script**

```python
#!/usr/bin/env python3
"""
Extracts all keywords from RU _clean.json files.
Creates mapping: slug -> [keywords with volumes]
"""
import json
from pathlib import Path

def extract_ru_keywords():
    categories_dir = Path("categories")
    mapping = {}

    for clean_file in categories_dir.rglob("*_clean.json"):
        with open(clean_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        slug = data.get("id") or data.get("slug")
        if not slug:
            continue

        keywords = []

        # V2 format: keywords is list
        if isinstance(data.get("keywords"), list):
            keywords.extend(data["keywords"])
        # Legacy format: keywords is dict with groups
        elif isinstance(data.get("keywords"), dict):
            for group in data["keywords"].values():
                keywords.extend(group)

        # Add synonyms if present
        if isinstance(data.get("synonyms"), list):
            for syn in data["synonyms"]:
                if isinstance(syn, dict) and "keyword" in syn:
                    keywords.append(syn)

        if keywords:
            mapping[slug] = {
                "keywords": keywords,
                "path": str(clean_file.relative_to(categories_dir))
            }

    return mapping

def main():
    mapping = extract_ru_keywords()

    output_path = Path("data/generated/ru_keywords_mapping.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(mapping)} categories")
    total_kws = sum(len(v["keywords"]) for v in mapping.values())
    print(f"Total keywords: {total_kws}")

if __name__ == "__main__":
    main()
```

**Step 2: Run script**

Run: `python3 scripts/extract_ru_keywords_mapping.py`
Expected: ~50 categories, ~300+ keywords

**Step 3: Verify output**

Run: `cat data/generated/ru_keywords_mapping.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(list(d.keys())[:10])"`
Expected: List of category slugs

**Step 4: Commit**

```bash
git add scripts/extract_ru_keywords_mapping.py data/generated/ru_keywords_mapping.json
git commit -m "feat: extract RU keywords mapping from _clean.json files"
```

---

## Task 2: Create UK-to-RU Matcher Script

**Files:**
- Create: `scripts/match_uk_keywords_to_categories.py`
- Read: `data/generated/ru_keywords_mapping.json`
- Read: `uk/data/uk_keywords.json` (current broken mapping)
- Output: `uk/data/uk_keywords_fixed.json`

**Step 1: Install rapidfuzz if needed**

Run: `pip install rapidfuzz`

**Step 2: Write the matcher script**

```python
#!/usr/bin/env python3
"""
Matches UK keywords to RU categories using fuzzy matching.
Uses RU keywords as ground truth for category assignment.
"""
import json
import re
from pathlib import Path
from collections import defaultdict

try:
    from rapidfuzz import fuzz, process
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False
    print("WARNING: rapidfuzz not installed, using basic matching")

# Manual translation patterns UK -> RU for matching
UK_TO_RU = {
    "піна": "пена",
    "миття": "мойк",
    "авто": "авто",
    "засіб": "средств",
    "очищувач": "очистител",
    "шин": "шин",
    "гум": "резин",
    "віск": "воск",
    "шкір": "кож",
    "поліроль": "полирол",
    "полірув": "полиров",
    "скло": "стекл",
    "диск": "диск",
    "знежир": "обезжир",
    "двигун": "двигател",
    "салон": "салон",
    "пластик": "пластик",
    "машинк": "машинк",
    "кераміка": "керамик",
    "антидощ": "антидожд",
    "антибітум": "антибитум",
    "мікрофібр": "микрофибр",
    "губк": "губк",
    "рукавиц": "варежк",
    "щітк": "щетк",
    "набір": "набор",
    "глин": "глин",
    "скраб": "скраб",
    "омивач": "омывател",
    "торнадор": "торнадор",
    "шампунь": "шампун",
    "хімчистк": "химчистк",
    "нейтралізатор": "нейтрализатор",
    "запах": "запах",
    "відро": "ведр",
    "ємност": "емкост",
    "скотч": "скотч",
    "малярн": "малярн",
    "розпилювач": "распылител",
    "пінник": "пенник",
}

def translate_uk_to_ru_pattern(uk_keyword: str) -> str:
    """Translate UK keyword to RU pattern for matching."""
    result = uk_keyword.lower()
    for uk, ru in UK_TO_RU.items():
        result = result.replace(uk.lower(), ru)
    return result

def load_ru_mapping() -> dict:
    with open("data/generated/ru_keywords_mapping.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_current_uk_keywords() -> dict:
    with open("uk/data/uk_keywords.json", "r", encoding="utf-8") as f:
        return json.load(f)

def build_ru_keyword_index(ru_mapping: dict) -> dict:
    """Build index: ru_keyword_lower -> slug"""
    index = {}
    for slug, data in ru_mapping.items():
        for kw_data in data["keywords"]:
            kw = kw_data["keyword"].lower()
            index[kw] = slug
            # Also index without "для авто", "автомобиля" etc
            simplified = re.sub(r"\s*(для\s+)?(авто|автомобил[яь]|машин[ыу])\s*", " ", kw).strip()
            if simplified != kw:
                index[simplified] = slug
    return index

def match_uk_keyword(uk_kw: str, ru_index: dict, ru_mapping: dict) -> str:
    """Find best matching RU category for UK keyword."""
    uk_lower = uk_kw.lower()
    ru_pattern = translate_uk_to_ru_pattern(uk_lower)

    # Direct match in index
    if ru_pattern in ru_index:
        return ru_index[ru_pattern]

    # Fuzzy match against all RU keywords
    if HAS_RAPIDFUZZ:
        all_ru_kws = list(ru_index.keys())
        matches = process.extract(ru_pattern, all_ru_kws, scorer=fuzz.token_set_ratio, limit=3)
        if matches and matches[0][1] >= 70:  # 70% similarity threshold
            return ru_index[matches[0][0]]

    # Fallback: check if any RU keyword contains similar root
    for ru_kw, slug in ru_index.items():
        # Check if translated pattern has significant overlap
        if len(ru_pattern) > 5 and ru_pattern[:5] in ru_kw:
            return slug

    return None

def main():
    ru_mapping = load_ru_mapping()
    current_uk = load_current_uk_keywords()
    ru_index = build_ru_keyword_index(ru_mapping)

    # Collect all UK keywords
    all_uk_keywords = []
    for slug, cat_data in current_uk.get("categories", {}).items():
        for kw_data in cat_data.get("keywords", []):
            all_uk_keywords.append(kw_data)

    print(f"Total UK keywords to redistribute: {len(all_uk_keywords)}")

    # Match and redistribute
    new_categories = defaultdict(lambda: {"keywords": [], "total_volume": 0})
    unmatched = []

    for kw_data in all_uk_keywords:
        uk_kw = kw_data["keyword"]
        volume = kw_data.get("volume", 0)

        matched_slug = match_uk_keyword(uk_kw, ru_index, ru_mapping)

        if matched_slug:
            new_categories[matched_slug]["keywords"].append(kw_data)
            new_categories[matched_slug]["total_volume"] += volume
        else:
            unmatched.append(kw_data)

    # Build output
    output = {
        "generated": "2026-01-26",
        "method": "fuzzy_match_to_ru_categories",
        "total_keywords": len(all_uk_keywords),
        "matched": len(all_uk_keywords) - len(unmatched),
        "unmatched_count": len(unmatched),
        "categories": dict(new_categories)
    }

    # Add unmatched to special key
    if unmatched:
        output["unmatched"] = unmatched

    # Write output
    output_path = Path("uk/data/uk_keywords_fixed.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Matched: {len(all_uk_keywords) - len(unmatched)}")
    print(f"Unmatched: {len(unmatched)}")
    print(f"Categories with keywords: {len(new_categories)}")
    print(f"Output: {output_path}")

    if unmatched:
        print("\nUnmatched keywords (first 10):")
        for kw in unmatched[:10]:
            print(f"  - {kw['keyword']}")

if __name__ == "__main__":
    main()
```

**Step 3: Run matcher**

Run: `python3 scripts/match_uk_keywords_to_categories.py`
Expected: ~90%+ matched, <10% unmatched

**Step 4: Review unmatched**

Run: `cat uk/data/uk_keywords_fixed.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('Unmatched:', d.get('unmatched_count', 0)); print([k['keyword'] for k in d.get('unmatched', [])[:10]])"`
Expected: List of unmatched keywords to manually assign

**Step 5: Commit**

```bash
git add scripts/match_uk_keywords_to_categories.py uk/data/uk_keywords_fixed.json
git commit -m "feat: match UK keywords to RU categories using fuzzy matching"
```

---

## Task 3: Manual Review and Fix Unmatched

**Files:**
- Modify: `uk/data/uk_keywords_fixed.json`

**Step 1: Review unmatched keywords**

Run: `cat uk/data/uk_keywords_fixed.json | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f\"{k['keyword']} ({k['volume']})\") for k in d.get('unmatched', [])]"`

**Step 2: Manually assign unmatched to categories**

For each unmatched keyword:
1. Determine correct category based on product type
2. Add to appropriate category in `uk/data/uk_keywords_fixed.json`
3. Remove from `unmatched` array

**Step 3: Verify no unmatched remain**

Run: `cat uk/data/uk_keywords_fixed.json | python3 -c "import json,sys; d=json.load(sys.stdin); print('Unmatched:', len(d.get('unmatched', [])))"`
Expected: 0

**Step 4: Commit**

```bash
git add uk/data/uk_keywords_fixed.json
git commit -m "fix: manually assign remaining unmatched UK keywords"
```

---

## Task 4: Replace uk_keywords.json and Regenerate _clean.json

**Files:**
- Replace: `uk/data/uk_keywords.json` with `uk/data/uk_keywords_fixed.json`
- Regenerate: `uk/categories/*/data/*_clean.json` (42 files)

**Step 1: Backup and replace**

```bash
mv uk/data/uk_keywords.json uk/data/uk_keywords_backup.json
mv uk/data/uk_keywords_fixed.json uk/data/uk_keywords.json
```

**Step 2: Run update_uk_clean_json.py**

Run: `python3 scripts/update_uk_clean_json.py`
Expected: 42 categories updated

**Step 3: Verify semantic coverage**

Run: `python3 scripts/check_semantic_coverage.py --lang uk`
Expected: 100% coverage, 0 missing

**Step 4: Commit**

```bash
git add uk/data/uk_keywords.json uk/categories/*/data/*_clean.json
git commit -m "feat(uk): redistribute keywords based on RU category matching"
```

---

## Task 5: Validate UK Content Against New Keywords

**Files:**
- Validate: `uk/categories/*/content/*_uk.md`

**Step 1: Run SEO validation for all UK content**

```bash
for f in uk/categories/*/content/*_uk.md; do
  slug=$(basename "$f" _uk.md)
  clean_file="uk/categories/$slug/data/${slug}_clean.json"
  if [ -f "$clean_file" ]; then
    kw=$(python3 -c "import json; d=json.load(open('$clean_file')); kws=d.get('keywords',[])+d.get('secondary_keywords',[]); print(kws[0]['keyword'] if kws else '')" 2>/dev/null)
    if [ -n "$kw" ]; then
      result=$(python3 scripts/check_seo_structure.py "$f" "$kw" 2>&1 | grep "SEO STRUCTURE")
      echo "$slug: $result"
    fi
  fi
done
```

**Step 2: Count PASS/WARN/FAIL**

Expected: Higher PASS rate than before (was 18/42)

**Step 3: Document remaining issues**

Create list of categories that still need content updates in `tasks/UK_CONTENT_UPDATES_NEEDED.md`

**Step 4: Commit validation report**

```bash
git add tasks/UK_CONTENT_UPDATES_NEEDED.md
git commit -m "docs: document UK categories needing content updates after keyword redistribution"
```

---

## Summary

| Task | Action | Output |
|------|--------|--------|
| 1 | Extract RU keywords | `data/generated/ru_keywords_mapping.json` |
| 2 | Match UK to RU | `uk/data/uk_keywords_fixed.json` |
| 3 | Manual fix unmatched | Clean `uk_keywords_fixed.json` |
| 4 | Replace and regenerate | Updated `uk_keywords.json` + `_clean.json` |
| 5 | Validate content | Report of needed updates |

**Expected outcome:** UK keywords correctly distributed to match RU category structure, higher SEO validation pass rate.
