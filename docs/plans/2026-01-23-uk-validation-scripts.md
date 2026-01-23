# UK Validation Scripts Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `--lang uk` parameter to 3 validation scripts for Ukrainian content support.

**Architecture:** Add `--lang {ru,uk}` argument to existing scripts. UK mode uses `uk/categories/` paths and Ukrainian stopwords/stemmers. RU mode unchanged (backward compatible).

**Tech Stack:** Python 3.11+, argparse, snowballstemmer (Ukrainian), pytest

---

## Task 1: check_keyword_density.py — Add UK Support

**Files:**
- Modify: `scripts/check_keyword_density.py:36-43` (stemmer), `62-184` (stopwords), `645-651` (argparse)

**Step 1: Add Ukrainian stopwords constant after STOPWORDS_RU**

Find line ~184 (after STOPWORDS_RU closing brace), add:

```python
# Ukrainian stopwords
STOPWORDS_UK = {
    "і", "в", "на", "з", "по", "для", "із", "до", "у", "о", "від", "за",
    "при", "не", "але", "а", "ж", "то", "це", "як", "що", "так", "все",
    "він", "вона", "вони", "ми", "ви", "його", "її", "їх", "або", "якщо",
    "тільки", "вже", "ще", "би", "чи", "до", "без", "під", "над", "між",
    "через", "після", "перед", "біля", "більше", "менше", "також", "теж",
    "дуже", "може", "можна", "потрібно", "є", "був", "була", "були", "буде",
    "який", "яка", "яке", "які", "цей", "ця", "ці", "той", "та", "ті",
    "свій", "своя", "свої", "наш", "ваш", "сам", "самий", "весь", "вся",
    "все", "кожен", "будь", "інший", "такий", "який", "щоб", "тому",
    "коли", "де", "куди", "звідки", "чому", "навіщо", "скільки", "хто",
    "чого", "чому", "кого", "кому", "чим", "ким", "ним", "ній", "них",
    "йому", "їй", "їм", "вам", "нам", "себе", "собі", "собою", "мені",
    "мене", "мною", "тебе", "тобі", "тобою",
}
```

**Step 2: Add get_stopwords function**

After stopwords constants, add:

```python
def get_stopwords(lang: str = "ru") -> set[str]:
    """Return stopwords for specified language."""
    if lang == "uk":
        return STOPWORDS_UK
    return STOPWORDS_RU
```

**Step 3: Add Ukrainian stemmer initialization**

Modify lines 36-43:

```python
try:
    from snowballstemmer import stemmer as snowball_stemmer

    STEMMER_RU = snowball_stemmer("russian")
    STEMMER_UK = snowball_stemmer("ukrainian")
    HAS_STEMMER = True
except ImportError:
    HAS_STEMMER = False
    STEMMER_RU = None
    STEMMER_UK = None


def get_stemmer(lang: str = "ru"):
    """Return stemmer for specified language."""
    if lang == "uk":
        return STEMMER_UK
    return STEMMER_RU
```

**Step 4: Add --lang argument to argparse**

In `build_parser()` function (~line 651), add:

```python
parser.add_argument("--lang", choices=["ru", "uk"], default="ru", help="Language: ru (default) or uk")
```

**Step 5: Update functions to use lang parameter**

Functions that use STOPWORDS or STEMMER need `lang` parameter. Key functions to update:
- `tokenize()` — pass stopwords
- `get_stem()` — use correct stemmer
- `analyze_density()` — pass lang through

**Step 6: Verify syntax**

Run: `python3 -m py_compile scripts/check_keyword_density.py`
Expected: No output (success)

**Step 7: Test on UK file**

Run:
```bash
python3 scripts/check_keyword_density.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md --lang uk
```
Expected: Output with Ukrainian words analyzed, no Russian stopwords in results

**Step 8: Test RU backward compatibility**

Run:
```bash
python3 scripts/check_keyword_density.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
```
Expected: Same output as before (RU default)

**Step 9: Commit**

```bash
git add scripts/check_keyword_density.py
git commit -m "feat(validation): add --lang uk support to check_keyword_density.py"
```

---

## Task 2: check_h1_sync.py — Add UK Support

**Files:**
- Modify: `scripts/check_h1_sync.py`

**Step 1: Add --lang argument**

In argparse section (~line 128), add:

```python
parser.add_argument("--lang", choices=["ru", "uk"], default="ru", help="Language: ru (default) or uk")
```

**Step 2: Update check_sync function signature**

```python
def check_sync(fix: bool = False, lang: str = "ru"):
```

**Step 3: Select paths based on language**

At the start of `check_sync()`:

```python
if lang == "uk":
    categories_dir = Path("uk/categories")
    content_suffix = "_uk.md"
else:
    categories_dir = CATEGORIES_DIR
    content_suffix = "_ru.md"

print(f"🔍 Проверка синхронизации H1 в {categories_dir} ({lang.upper()})...\n")
```

**Step 4: Update file paths in loop**

Replace:
```python
md_file = category_dir / "content" / f"{slug}_ru.md"
```

With:
```python
md_file = category_dir / "content" / f"{slug}{content_suffix}"
```

**Step 5: Pass lang to function call**

In `__main__`:
```python
check_sync(args.fix, args.lang)
```

**Step 6: Verify syntax**

Run: `python3 -m py_compile scripts/check_h1_sync.py`
Expected: No output (success)

**Step 7: Test UK mode**

Run:
```bash
python3 scripts/check_h1_sync.py --lang uk
```
Expected: Scans `uk/categories/`, checks `*_uk.md` files

**Step 8: Test RU backward compatibility**

Run:
```bash
python3 scripts/check_h1_sync.py
```
Expected: Same behavior as before

**Step 9: Commit**

```bash
git add scripts/check_h1_sync.py
git commit -m "feat(validation): add --lang uk support to check_h1_sync.py"
```

---

## Task 3: check_semantic_coverage.py — Add UK Support

**Files:**
- Modify: `scripts/check_semantic_coverage.py`

**Step 1: Add imports and argparse**

At top, add argparse:

```python
import argparse
```

**Step 2: Add load_uk_keywords function**

```python
def load_uk_keywords() -> dict[str, str]:
    """Load keywords from uk_keywords.json. Returns kw -> slug mapping."""
    uk_keywords_path = os.path.join(PROJECT_ROOT, "uk", "data", "uk_keywords.json")
    if not os.path.exists(uk_keywords_path):
        print(f"ERROR: UK keywords file not found: {uk_keywords_path}")
        return {}

    with open(uk_keywords_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    kw_map = {}
    for slug, cat_data in data.get("categories", {}).items():
        for kw_item in cat_data.get("keywords", []):
            kw_map[kw_item["keyword"].strip().lower()] = slug
    return kw_map
```

**Step 3: Add scan_uk_json_keywords function**

```python
def scan_uk_json_keywords() -> dict[str, str]:
    """Scan uk/categories/ for keywords in _clean.json files."""
    uk_categories_dir = os.path.join(PROJECT_ROOT, "uk", "categories")
    kw_map = {}

    for root, _dirs, files in os.walk(uk_categories_dir):
        for file in files:
            if file.endswith("_clean.json"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    slug = data.get("id") or data.get("slug")

                    keywords = []
                    if isinstance(data.get("keywords"), list):
                        keywords = [k["keyword"] for k in data["keywords"]]

                    for kw in keywords:
                        kw_map[kw.strip().lower()] = slug
                except Exception:
                    pass
    return kw_map
```

**Step 4: Add analyze_uk_coverage function**

```python
def analyze_uk_coverage():
    """Analyze UK keyword coverage: uk_keywords.json vs uk/categories/_clean.json"""
    source_kws = load_uk_keywords()  # kw -> slug from uk_keywords.json
    json_kws = scan_uk_json_keywords()  # kw -> slug from _clean.json files

    report = []
    report.append("# UK Semantic Coverage: uk_keywords.json vs _clean.json")
    report.append("")

    missing_in_json = []
    for kw, slug in source_kws.items():
        if kw not in json_kws:
            missing_in_json.append((kw, slug))

    if missing_in_json:
        report.append("## ❌ Keywords in uk_keywords.json but NOT in _clean.json files:")
        for kw, slug in sorted(missing_in_json, key=lambda x: x[1]):
            report.append(f"- `{kw}` (should be in {slug})")
        report.append("")

    report.append("## Итог")
    report.append(f"- Всего в uk_keywords.json: **{len(source_kws)}**")
    report.append(f"- Найдено в _clean.json: **{len(json_kws)}**")
    report.append(f"- Потеряно: **{len(missing_in_json)}**")

    if len(missing_in_json) == 0:
        report.append("\n✅ **ALL CLEAR:** Все UK ключи распределены.")
    else:
        report.append("\n⚠️ **ATTENTION:** Есть нераспределённые UK ключи.")

    output_path = os.path.join(PROJECT_ROOT, "tasks", "reports", "SEMANTIC_COVERAGE_CHECK_UK.md")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"UK coverage report: {output_path}")
```

**Step 5: Update main block with argparse**

Replace `if __name__ == "__main__":` block:

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check semantic coverage")
    parser.add_argument("--lang", choices=["ru", "uk"], default="ru", help="Language: ru (default) or uk")
    args = parser.parse_args()

    if args.lang == "uk":
        analyze_uk_coverage()
    else:
        analyze_coverage()
```

**Step 6: Verify syntax**

Run: `python3 -m py_compile scripts/check_semantic_coverage.py`
Expected: No output (success)

**Step 7: Test UK mode**

Run:
```bash
python3 scripts/check_semantic_coverage.py --lang uk
```
Expected: Creates `tasks/reports/SEMANTIC_COVERAGE_CHECK_UK.md`

**Step 8: Test RU backward compatibility**

Run:
```bash
python3 scripts/check_semantic_coverage.py
```
Expected: Same behavior as before (RU mode)

**Step 9: Commit**

```bash
git add scripts/check_semantic_coverage.py
git commit -m "feat(validation): add --lang uk support to check_semantic_coverage.py"
```

---

## Task 4: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Add UK examples to validation section**

Find the validation commands section, add UK examples:

```bash
# Валидация (UK)
python scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
python scripts/check_h1_sync.py --lang uk
python scripts/check_semantic_coverage.py --lang uk
```

**Step 2: Update version**

Change version number.

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add UK validation commands to CLAUDE.md"
```

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| check_keyword_density.py accepts --lang uk | ✓ |
| check_h1_sync.py accepts --lang uk | ✓ |
| check_semantic_coverage.py accepts --lang uk | ✓ |
| All scripts work without --lang (RU default) | ✓ |
| UK files validated correctly | ✓ |

---

**Version:** 1.0
**Created:** 2026-01-23
