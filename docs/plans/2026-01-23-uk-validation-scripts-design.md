# UK Support for Validation Scripts — Design Document

**Status:** Approved
**Goal:** Add `--lang uk` parameter to validation scripts for Ukrainian content support.

**Approach:** Add `--lang {ru,uk}` argument to existing scripts (one file, two modes).

---

## Scripts to Adapt

| Script | Current UK Support | Changes Needed |
|--------|-------------------|----------------|
| `check_keyword_density.py` | ❌ None | Add `--lang`, UK stopwords |
| `check_h1_sync.py` | ❌ None | Add `--lang`, UK paths |
| `check_semantic_coverage.py` | ❌ None | Add `--lang`, read uk_keywords.json |

---

## Task 1: check_keyword_density.py

**Files:** `scripts/check_keyword_density.py`

**Step 1:** Add argparse `--lang` parameter
```python
parser.add_argument("--lang", choices=["ru", "uk"], default="ru", help="Language: ru or uk")
```

**Step 2:** Pass `lang` to functions that need stopwords/stemming

**Step 3:** Verify with UK file:
```bash
python scripts/check_keyword_density.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md --lang uk
```

**Step 4:** Commit

---

## Task 2: check_h1_sync.py

**Files:** `scripts/check_h1_sync.py`

**Step 1:** Add argparse `--lang` parameter

**Step 2:** Select paths based on language:
```python
if args.lang == "uk":
    CATEGORIES_DIR = Path("uk/categories")
else:
    CATEGORIES_DIR = Path("categories")
```

**Step 3:** Verify:
```bash
python scripts/check_h1_sync.py --lang uk
```

**Step 4:** Commit

---

## Task 3: check_semantic_coverage.py

**Files:** `scripts/check_semantic_coverage.py`

**Step 1:** Add argparse `--lang` parameter

**Step 2:** For UK mode:
- Source keywords: `uk/data/uk_keywords.json` (instead of STRUCTURE.md)
- Scan: `uk/categories/*/data/*_clean.json`
- Output: `tasks/reports/SEMANTIC_COVERAGE_CHECK_UK.md`

**Step 3:** Add function `load_uk_keywords()`:
```python
def load_uk_keywords() -> dict[str, str]:
    """Load keywords from uk_keywords.json. Returns kw -> slug mapping."""
    with open("uk/data/uk_keywords.json") as f:
        data = json.load(f)
    kw_map = {}
    for slug, cat_data in data["categories"].items():
        for kw_item in cat_data.get("keywords", []):
            kw_map[kw_item["keyword"].lower()] = slug
    return kw_map
```

**Step 4:** Verify:
```bash
python scripts/check_semantic_coverage.py --lang uk
```

**Step 5:** Commit

---

## Task 4: Update CLAUDE.md

Add UK examples to validation commands section.

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| All 3 scripts accept `--lang uk` | ✓ |
| UK files validated correctly | ✓ |
| RU mode unchanged (backward compatible) | ✓ |
| No new dependencies | ✓ |

---

**Version:** 1.0
**Created:** 2026-01-23
