# RU Semantics Master Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать единый master CSV файл как источник истины для русской семантики с автоматической синхронизацией в `_clean.json` файлы категорий.

**Architecture:** Master CSV (`data/ru_semantics_master.csv`) содержит все ключи с частотностью и привязкой к категориям. Три скрипта: `merge_to_master.py` (создание/обновление CSV), `validate_master.py` (валидация), `sync_semantics.py` (синхронизация в `_clean.json`).

**Tech Stack:** Python 3.9+, pandas (для Excel), csv, json, pathlib, argparse

**Design Doc:** `docs/plans/2026-01-28-ru-semantics-master-design.md`

---

## Task 1: Create validate_master.py (validation script)

**Files:**
- Create: `scripts/validate_master.py`
- Test: `tests/unit/test_validate_master.py`

**Step 1: Write failing tests**

```python
# tests/unit/test_validate_master.py
"""Tests for validate_master.py"""

import pytest
from io import StringIO
from scripts.validate_master import (
    load_master_csv,
    validate_columns,
    validate_categories_exist,
    validate_no_duplicates,
    validate_types,
    validate_volumes,
    validate_has_keywords,
)


class TestLoadMasterCsv:
    """Test CSV loading."""

    def test_loads_valid_csv(self, tmp_path):
        """Should load CSV and return list of dicts."""
        csv_file = tmp_path / "master.csv"
        csv_file.write_text(
            "keyword,volume,category,type,use_in\n"
            "тест,100,aktivnaya-pena,keyword,\n",
            encoding="utf-8"
        )
        rows = load_master_csv(csv_file)
        assert len(rows) == 1
        assert rows[0]["keyword"] == "тест"
        assert rows[0]["volume"] == "100"

    def test_raises_on_missing_file(self, tmp_path):
        """Should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_master_csv(tmp_path / "nonexistent.csv")


class TestValidateColumns:
    """Test column validation."""

    def test_valid_columns(self):
        """Should pass with all required columns."""
        rows = [{"keyword": "a", "volume": "1", "category": "b", "type": "keyword", "use_in": ""}]
        errors = validate_columns(rows)
        assert errors == []

    def test_missing_column(self):
        """Should report missing column."""
        rows = [{"keyword": "a", "volume": "1", "category": "b"}]  # missing type, use_in
        errors = validate_columns(rows)
        assert len(errors) > 0
        assert "type" in errors[0].lower() or "use_in" in errors[0].lower()


class TestValidateCategoriesExist:
    """Test category existence validation."""

    def test_existing_category(self, tmp_path):
        """Should pass for existing category."""
        (tmp_path / "categories" / "aktivnaya-pena" / "data").mkdir(parents=True)
        rows = [{"category": "aktivnaya-pena"}]
        errors = validate_categories_exist(rows, tmp_path / "categories")
        assert errors == []

    def test_missing_category(self, tmp_path):
        """Should report missing category."""
        (tmp_path / "categories").mkdir()
        rows = [{"category": "nonexistent"}]
        errors = validate_categories_exist(rows, tmp_path / "categories")
        assert len(errors) == 1
        assert "nonexistent" in errors[0]

    def test_uncategorized_allowed(self, tmp_path):
        """Should allow 'uncategorized' without folder."""
        (tmp_path / "categories").mkdir()
        rows = [{"category": "uncategorized"}]
        errors = validate_categories_exist(rows, tmp_path / "categories")
        assert errors == []


class TestValidateNoDuplicates:
    """Test duplicate detection."""

    def test_no_duplicates(self):
        """Should pass with unique keywords."""
        rows = [{"keyword": "a"}, {"keyword": "b"}]
        errors = validate_no_duplicates(rows)
        assert errors == []

    def test_finds_duplicates(self):
        """Should report duplicate keywords."""
        rows = [{"keyword": "a"}, {"keyword": "a"}]
        errors = validate_no_duplicates(rows)
        assert len(errors) == 1
        assert "a" in errors[0]


class TestValidateTypes:
    """Test type field validation."""

    def test_valid_types(self):
        """Should pass for keyword and synonym."""
        rows = [{"keyword": "a", "type": "keyword"}, {"keyword": "b", "type": "synonym"}]
        errors = validate_types(rows)
        assert errors == []

    def test_invalid_type(self):
        """Should report invalid type."""
        rows = [{"keyword": "a", "type": "invalid"}]
        errors = validate_types(rows)
        assert len(errors) == 1


class TestValidateVolumes:
    """Test volume validation."""

    def test_valid_volumes(self):
        """Should pass for non-negative integers."""
        rows = [{"keyword": "a", "volume": "100"}, {"keyword": "b", "volume": "0"}]
        errors = validate_volumes(rows)
        assert errors == []

    def test_negative_volume(self):
        """Should report negative volume."""
        rows = [{"keyword": "a", "volume": "-1"}]
        errors = validate_volumes(rows)
        assert len(errors) == 1

    def test_non_integer_volume(self):
        """Should report non-integer volume."""
        rows = [{"keyword": "a", "volume": "abc"}]
        errors = validate_volumes(rows)
        assert len(errors) == 1


class TestValidateHasKeywords:
    """Test that each category has at least one keyword type."""

    def test_has_keyword(self):
        """Should pass when category has keyword type."""
        rows = [
            {"category": "cat1", "type": "keyword"},
            {"category": "cat1", "type": "synonym"},
        ]
        errors = validate_has_keywords(rows)
        assert errors == []

    def test_only_synonyms(self):
        """Should report category with only synonyms."""
        rows = [{"category": "cat1", "type": "synonym"}]
        errors = validate_has_keywords(rows)
        assert len(errors) == 1
        assert "cat1" in errors[0]
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/unit/test_validate_master.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'scripts.validate_master'"

**Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""Валидация master CSV файла семантики."""

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEFAULT_CSV = ROOT / "data" / "ru_semantics_master.csv"
CATEGORIES_DIR = ROOT / "categories"

REQUIRED_COLUMNS = {"keyword", "volume", "category", "type", "use_in"}
VALID_TYPES = {"keyword", "synonym"}
VALID_USE_IN = {"", "meta_only"}


def load_master_csv(csv_path: Path) -> list[dict]:
    """Загружает CSV и возвращает список словарей."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def validate_columns(rows: list[dict]) -> list[str]:
    """Проверяет наличие всех обязательных колонок."""
    if not rows:
        return ["CSV is empty"]

    actual = set(rows[0].keys())
    missing = REQUIRED_COLUMNS - actual
    if missing:
        return [f"Missing columns: {', '.join(sorted(missing))}"]
    return []


def validate_categories_exist(rows: list[dict], categories_dir: Path) -> list[str]:
    """Проверяет существование категорий."""
    errors = []
    categories = {row["category"] for row in rows}

    for cat in categories:
        if cat == "uncategorized":
            continue
        cat_path = categories_dir / cat
        if not cat_path.exists():
            # Check nested paths
            found = list(categories_dir.rglob(cat))
            if not found:
                errors.append(f"Category not found: {cat}")
    return errors


def validate_no_duplicates(rows: list[dict]) -> list[str]:
    """Проверяет отсутствие дубликатов ключей."""
    keywords = [row["keyword"].lower().strip() for row in rows]
    counts = Counter(keywords)
    duplicates = [kw for kw, count in counts.items() if count > 1]

    if duplicates:
        return [f"Duplicate keyword: {kw}" for kw in duplicates[:10]]  # Limit to 10
    return []


def validate_types(rows: list[dict]) -> list[str]:
    """Проверяет валидность поля type."""
    errors = []
    for i, row in enumerate(rows, 1):
        if row.get("type", "") not in VALID_TYPES:
            errors.append(f"Row {i}: Invalid type '{row.get('type')}' for '{row['keyword']}'")
    return errors[:10]


def validate_volumes(rows: list[dict]) -> list[str]:
    """Проверяет валидность поля volume."""
    errors = []
    for i, row in enumerate(rows, 1):
        vol = row.get("volume", "")
        try:
            v = int(vol)
            if v < 0:
                errors.append(f"Row {i}: Negative volume {v} for '{row['keyword']}'")
        except ValueError:
            errors.append(f"Row {i}: Invalid volume '{vol}' for '{row['keyword']}'")
    return errors[:10]


def validate_has_keywords(rows: list[dict]) -> list[str]:
    """Проверяет что каждая категория имеет минимум 1 keyword."""
    from collections import defaultdict

    by_category = defaultdict(set)
    for row in rows:
        by_category[row["category"]].add(row["type"])

    errors = []
    for cat, types in by_category.items():
        if cat == "uncategorized":
            continue
        if "keyword" not in types:
            errors.append(f"Category '{cat}' has no keywords, only synonyms")
    return errors


def validate_use_in(rows: list[dict]) -> list[str]:
    """Проверяет валидность поля use_in."""
    errors = []
    for i, row in enumerate(rows, 1):
        use_in = row.get("use_in", "")
        if use_in not in VALID_USE_IN:
            errors.append(f"Row {i}: Invalid use_in '{use_in}' for '{row['keyword']}'")
    return errors[:10]


def validate(csv_path: Path, categories_dir: Path) -> tuple[list[str], list[str]]:
    """Запускает все проверки. Возвращает (errors, warnings)."""
    errors = []
    warnings = []

    try:
        rows = load_master_csv(csv_path)
    except FileNotFoundError as e:
        return [str(e)], []

    errors.extend(validate_columns(rows))
    if errors:
        return errors, warnings  # Can't continue without columns

    errors.extend(validate_no_duplicates(rows))
    errors.extend(validate_types(rows))
    errors.extend(validate_volumes(rows))
    errors.extend(validate_use_in(rows))
    errors.extend(validate_categories_exist(rows, categories_dir))

    kw_errors = validate_has_keywords(rows)
    warnings.extend(kw_errors)  # Warnings, not errors

    return errors, warnings


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate master CSV")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to CSV")
    parser.add_argument("--categories", type=Path, default=CATEGORIES_DIR, help="Categories dir")
    args = parser.parse_args()

    print(f"Validating {args.csv}...")
    errors, warnings = validate(args.csv, args.categories)

    if warnings:
        print(f"\n⚠️  {len(warnings)} warnings:")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n❌ {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n✅ Validation passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_validate_master.py -v
```

Expected: All tests PASS

**Step 5: Commit**

```bash
git add scripts/validate_master.py tests/unit/test_validate_master.py
git commit -m "feat(semantics): add validate_master.py for CSV validation"
```

---

## Task 2: Create merge_to_master.py (CSV creation/update)

**Files:**
- Create: `scripts/merge_to_master.py`
- Test: `tests/unit/test_merge_to_master.py`

**Step 1: Write failing tests**

```python
# tests/unit/test_merge_to_master.py
"""Tests for merge_to_master.py"""

import json
import pytest
from pathlib import Path
from scripts.merge_to_master import (
    collect_from_clean_json,
    load_excel_keywords,
    merge_keywords,
    save_master_csv,
    find_clean_json_files,
)


class TestFindCleanJsonFiles:
    """Test finding _clean.json files."""

    def test_finds_nested_files(self, tmp_path):
        """Should find _clean.json in nested structure."""
        # Create nested structure
        cat1 = tmp_path / "cat1" / "data"
        cat1.mkdir(parents=True)
        (cat1 / "cat1_clean.json").write_text("{}", encoding="utf-8")

        cat2 = tmp_path / "cat1" / "sub" / "data"
        cat2.mkdir(parents=True)
        (cat2 / "sub_clean.json").write_text("{}", encoding="utf-8")

        files = find_clean_json_files(tmp_path)
        assert len(files) == 2


class TestCollectFromCleanJson:
    """Test collecting keywords from _clean.json."""

    def test_collects_keywords_list_format(self, tmp_path):
        """Should collect keywords from list format."""
        data = {
            "id": "test-cat",
            "keywords": [
                {"keyword": "ключ1", "volume": 100},
                {"keyword": "ключ2", "volume": 50},
            ],
            "synonyms": [
                {"keyword": "синоним", "volume": 30},
                {"keyword": "meta", "volume": 20, "use_in": "meta_only"},
            ]
        }
        clean_file = tmp_path / "test-cat" / "data" / "test-cat_clean.json"
        clean_file.parent.mkdir(parents=True)
        clean_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        rows = collect_from_clean_json(clean_file)

        assert len(rows) == 4
        assert rows[0] == {"keyword": "ключ1", "volume": 100, "category": "test-cat", "type": "keyword", "use_in": ""}
        assert rows[3] == {"keyword": "meta", "volume": 20, "category": "test-cat", "type": "synonym", "use_in": "meta_only"}

    def test_collects_keywords_dict_format(self, tmp_path):
        """Should collect keywords from dict format (legacy)."""
        data = {
            "id": "test-cat",
            "keywords": {
                "primary": [{"keyword": "primary", "volume": 100}],
                "secondary": [{"keyword": "secondary", "volume": 50}],
            }
        }
        clean_file = tmp_path / "test-cat" / "data" / "test-cat_clean.json"
        clean_file.parent.mkdir(parents=True)
        clean_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        rows = collect_from_clean_json(clean_file)

        assert len(rows) == 2


class TestLoadExcelKeywords:
    """Test loading keywords from Excel."""

    def test_loads_excel_with_standard_columns(self, tmp_path):
        """Should load Excel with 'Ключевое слово' and 'Точное вхождение'."""
        # Create test Excel using pandas
        import pandas as pd

        df = pd.DataFrame({
            "Ключевое слово": ["тест1", "тест2"],
            "Точное вхождение": [100, 200],
        })
        excel_path = tmp_path / "test.xlsx"
        df.to_excel(excel_path, index=False)

        keywords = load_excel_keywords(excel_path)

        assert keywords == {"тест1": 100, "тест2": 200}


class TestMergeKeywords:
    """Test merging keywords."""

    def test_updates_volume_from_excel(self):
        """Should update volume from Excel data."""
        existing = [
            {"keyword": "ключ", "volume": 50, "category": "cat1", "type": "keyword", "use_in": ""},
        ]
        excel = {"ключ": 100}

        result = merge_keywords(existing, excel)

        assert result[0]["volume"] == 100

    def test_adds_new_keywords_as_uncategorized(self):
        """Should add new keywords from Excel as uncategorized."""
        existing = []
        excel = {"новый": 200}

        result = merge_keywords(existing, excel)

        assert len(result) == 1
        assert result[0]["category"] == "uncategorized"
        assert result[0]["type"] == "keyword"

    def test_deduplicates_by_keyword(self):
        """Should keep keyword with higher volume on duplicate."""
        existing = [
            {"keyword": "ключ", "volume": 50, "category": "cat1", "type": "keyword", "use_in": ""},
            {"keyword": "ключ", "volume": 100, "category": "cat2", "type": "keyword", "use_in": ""},
        ]

        result = merge_keywords(existing, {})

        assert len(result) == 1
        assert result[0]["volume"] == 100


class TestSaveMasterCsv:
    """Test saving master CSV."""

    def test_saves_sorted_csv(self, tmp_path):
        """Should save CSV sorted by category, then volume DESC."""
        rows = [
            {"keyword": "b", "volume": 50, "category": "cat2", "type": "keyword", "use_in": ""},
            {"keyword": "a", "volume": 100, "category": "cat1", "type": "keyword", "use_in": ""},
            {"keyword": "c", "volume": 200, "category": "cat1", "type": "keyword", "use_in": ""},
        ]
        csv_path = tmp_path / "master.csv"

        save_master_csv(rows, csv_path)

        content = csv_path.read_text(encoding="utf-8")
        lines = content.strip().split("\n")
        assert len(lines) == 4  # header + 3 rows
        assert "cat1" in lines[1]  # cat1 first (alphabetically)
        assert "200" in lines[1]  # highest volume first
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/unit/test_merge_to_master.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""Создание/обновление master CSV из существующих источников."""

import csv
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent
CATEGORIES_DIR = ROOT / "categories"
DEFAULT_OUTPUT = ROOT / "data" / "ru_semantics_master.csv"

CSV_COLUMNS = ["keyword", "volume", "category", "type", "use_in"]


def find_clean_json_files(categories_dir: Path) -> list[Path]:
    """Находит все _clean.json файлы."""
    return list(categories_dir.rglob("*_clean.json"))


def extract_category_slug(clean_file: Path) -> str:
    """Извлекает slug категории из пути или содержимого файла."""
    # Try from file content first
    try:
        data = json.loads(clean_file.read_text(encoding="utf-8"))
        if "id" in data:
            return data["id"]
    except:
        pass

    # Fallback to filename
    return clean_file.stem.replace("_clean", "")


def collect_from_clean_json(clean_file: Path) -> list[dict]:
    """Собирает ключи из одного _clean.json файла."""
    data = json.loads(clean_file.read_text(encoding="utf-8"))
    category = extract_category_slug(clean_file)
    rows = []

    # Keywords
    keywords = data.get("keywords", [])
    if isinstance(keywords, list):
        for kw in keywords:
            rows.append({
                "keyword": kw["keyword"],
                "volume": kw.get("volume", 0),
                "category": category,
                "type": "keyword",
                "use_in": kw.get("use_in", ""),
            })
    elif isinstance(keywords, dict):
        # Legacy dict format
        for group in keywords.values():
            for kw in group:
                rows.append({
                    "keyword": kw["keyword"],
                    "volume": kw.get("volume", 0),
                    "category": category,
                    "type": "keyword",
                    "use_in": kw.get("use_in", ""),
                })

    # Synonyms
    for syn in data.get("synonyms", []):
        rows.append({
            "keyword": syn["keyword"],
            "volume": syn.get("volume", 0),
            "category": category,
            "type": "synonym",
            "use_in": syn.get("use_in", ""),
        })

    return rows


def load_excel_keywords(excel_path: Path) -> dict[str, int]:
    """Загружает ключи из Excel файла. Возвращает {keyword: volume}."""
    import pandas as pd

    df = pd.read_excel(excel_path)

    # Find keyword column
    kw_col = None
    for col in df.columns:
        if "ключ" in col.lower() or "keyword" in col.lower():
            kw_col = col
            break

    # Find volume column
    vol_col = None
    for col in df.columns:
        if "вхожд" in col.lower() or "volume" in col.lower() or "частот" in col.lower():
            vol_col = col
            break

    if not kw_col or not vol_col:
        raise ValueError(f"Cannot find keyword/volume columns in {excel_path}")

    result = {}
    for _, row in df.iterrows():
        kw = str(row[kw_col]).strip().lower()
        try:
            vol = int(row[vol_col])
        except (ValueError, TypeError):
            vol = 0
        if kw and kw != "nan":
            result[kw] = vol

    return result


def merge_keywords(existing: list[dict], excel_volumes: dict[str, int]) -> list[dict]:
    """Объединяет ключи: обновляет volume, добавляет новые, дедуплицирует."""
    # Index existing by keyword
    by_keyword = {}
    for row in existing:
        kw = row["keyword"].lower().strip()
        if kw not in by_keyword or row["volume"] > by_keyword[kw]["volume"]:
            by_keyword[kw] = row.copy()

    # Update volumes from Excel
    for kw, vol in excel_volumes.items():
        kw_lower = kw.lower().strip()
        if kw_lower in by_keyword:
            by_keyword[kw_lower]["volume"] = vol
        else:
            # New keyword from Excel
            by_keyword[kw_lower] = {
                "keyword": kw,
                "volume": vol,
                "category": "uncategorized",
                "type": "keyword",
                "use_in": "",
            }

    return list(by_keyword.values())


def save_master_csv(rows: list[dict], output_path: Path):
    """Сохраняет CSV, сортируя по category, затем по volume DESC."""
    # Sort
    sorted_rows = sorted(rows, key=lambda r: (r["category"], -r["volume"]))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(sorted_rows)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Create/update master CSV")
    parser.add_argument("--excel", nargs="*", type=Path, help="Excel files with frequency")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output CSV path")
    parser.add_argument("--categories", type=Path, default=CATEGORIES_DIR, help="Categories dir")
    args = parser.parse_args()

    print("📊 Collecting keywords from _clean.json files...")
    clean_files = find_clean_json_files(args.categories)
    print(f"   Found {len(clean_files)} _clean.json files")

    all_rows = []
    for f in clean_files:
        try:
            rows = collect_from_clean_json(f)
            all_rows.extend(rows)
        except Exception as e:
            print(f"   ⚠️  Error in {f.name}: {e}")

    print(f"   Collected {len(all_rows)} keywords")

    # Load Excel if provided
    excel_volumes = {}
    if args.excel:
        for excel_file in args.excel:
            print(f"\n📥 Loading {excel_file.name}...")
            try:
                vols = load_excel_keywords(excel_file)
                excel_volumes.update(vols)
                print(f"   Loaded {len(vols)} keywords")
            except Exception as e:
                print(f"   ⚠️  Error: {e}")

    # Merge
    print("\n🔄 Merging...")
    merged = merge_keywords(all_rows, excel_volumes)
    print(f"   Result: {len(merged)} unique keywords")

    # Count uncategorized
    uncategorized = sum(1 for r in merged if r["category"] == "uncategorized")
    if uncategorized:
        print(f"   ⚠️  {uncategorized} uncategorized keywords")

    # Save
    save_master_csv(merged, args.output)
    print(f"\n✅ Saved to {args.output}")


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_merge_to_master.py -v
```

Expected: All tests PASS

**Step 5: Commit**

```bash
git add scripts/merge_to_master.py tests/unit/test_merge_to_master.py
git commit -m "feat(semantics): add merge_to_master.py for CSV creation"
```

---

## Task 3: Create sync_semantics.py (sync CSV → _clean.json)

**Files:**
- Create: `scripts/sync_semantics.py`
- Test: `tests/unit/test_sync_semantics.py`

**Step 1: Write failing tests**

```python
# tests/unit/test_sync_semantics.py
"""Tests for sync_semantics.py"""

import json
import pytest
from pathlib import Path
from scripts.sync_semantics import (
    load_master_csv,
    group_by_category,
    find_clean_json_path,
    sync_category,
    build_keywords_list,
    build_synonyms_list,
)


class TestGroupByCategory:
    """Test grouping rows by category."""

    def test_groups_correctly(self):
        """Should group rows by category."""
        rows = [
            {"category": "cat1", "keyword": "a"},
            {"category": "cat2", "keyword": "b"},
            {"category": "cat1", "keyword": "c"},
        ]
        grouped = group_by_category(rows)

        assert len(grouped) == 2
        assert len(grouped["cat1"]) == 2
        assert len(grouped["cat2"]) == 1


class TestFindCleanJsonPath:
    """Test finding _clean.json path for category."""

    def test_finds_direct_path(self, tmp_path):
        """Should find _clean.json in direct category folder."""
        cat_dir = tmp_path / "categories" / "test-cat" / "data"
        cat_dir.mkdir(parents=True)
        clean_file = cat_dir / "test-cat_clean.json"
        clean_file.write_text("{}", encoding="utf-8")

        result = find_clean_json_path("test-cat", tmp_path / "categories")
        assert result == clean_file

    def test_finds_nested_path(self, tmp_path):
        """Should find _clean.json in nested category folder."""
        cat_dir = tmp_path / "categories" / "parent" / "child" / "data"
        cat_dir.mkdir(parents=True)
        clean_file = cat_dir / "child_clean.json"
        clean_file.write_text("{}", encoding="utf-8")

        result = find_clean_json_path("child", tmp_path / "categories")
        assert result == clean_file


class TestBuildKeywordsList:
    """Test building keywords list from rows."""

    def test_builds_sorted_list(self):
        """Should build list sorted by volume DESC."""
        rows = [
            {"keyword": "low", "volume": 10, "type": "keyword", "use_in": ""},
            {"keyword": "high", "volume": 100, "type": "keyword", "use_in": ""},
        ]
        result = build_keywords_list(rows)

        assert len(result) == 2
        assert result[0]["keyword"] == "high"
        assert result[0]["volume"] == 100

    def test_excludes_synonyms(self):
        """Should exclude synonym type."""
        rows = [
            {"keyword": "kw", "volume": 100, "type": "keyword", "use_in": ""},
            {"keyword": "syn", "volume": 50, "type": "synonym", "use_in": ""},
        ]
        result = build_keywords_list(rows)

        assert len(result) == 1
        assert result[0]["keyword"] == "kw"


class TestBuildSynonymsList:
    """Test building synonyms list from rows."""

    def test_builds_sorted_list(self):
        """Should build list sorted by volume DESC."""
        rows = [
            {"keyword": "syn1", "volume": 10, "type": "synonym", "use_in": ""},
            {"keyword": "syn2", "volume": 50, "type": "synonym", "use_in": "meta_only"},
        ]
        result = build_synonyms_list(rows)

        assert len(result) == 2
        assert result[0]["keyword"] == "syn2"
        assert result[0]["use_in"] == "meta_only"


class TestSyncCategory:
    """Test syncing single category."""

    def test_preserves_existing_fields(self, tmp_path):
        """Should preserve id, name, parent_id, entities, micro_intents."""
        cat_dir = tmp_path / "categories" / "test-cat" / "data"
        cat_dir.mkdir(parents=True)

        existing = {
            "id": "test-cat",
            "name": "Test Category",
            "parent_id": "parent",
            "entities": ["entity1"],
            "micro_intents": ["intent1"],
            "keywords": [{"keyword": "old", "volume": 1}],
            "synonyms": [],
        }
        clean_file = cat_dir / "test-cat_clean.json"
        clean_file.write_text(json.dumps(existing, ensure_ascii=False), encoding="utf-8")

        rows = [
            {"keyword": "new", "volume": 100, "type": "keyword", "use_in": ""},
        ]

        sync_category("test-cat", rows, tmp_path / "categories", dry_run=False)

        result = json.loads(clean_file.read_text(encoding="utf-8"))
        assert result["name"] == "Test Category"
        assert result["parent_id"] == "parent"
        assert result["entities"] == ["entity1"]
        assert result["micro_intents"] == ["intent1"]
        assert result["keywords"][0]["keyword"] == "new"

    def test_dry_run_no_changes(self, tmp_path):
        """Should not modify file in dry-run mode."""
        cat_dir = tmp_path / "categories" / "test-cat" / "data"
        cat_dir.mkdir(parents=True)

        existing = {"id": "test-cat", "keywords": [{"keyword": "old", "volume": 1}]}
        clean_file = cat_dir / "test-cat_clean.json"
        clean_file.write_text(json.dumps(existing), encoding="utf-8")
        original_content = clean_file.read_text()

        rows = [{"keyword": "new", "volume": 100, "type": "keyword", "use_in": ""}]

        sync_category("test-cat", rows, tmp_path / "categories", dry_run=True)

        assert clean_file.read_text() == original_content
```

**Step 2: Run tests to verify they fail**

```bash
pytest tests/unit/test_sync_semantics.py -v
```

Expected: FAIL with "ModuleNotFoundError"

**Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""Синхронизация master CSV → _clean.json файлы."""

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEFAULT_CSV = ROOT / "data" / "ru_semantics_master.csv"
CATEGORIES_DIR = ROOT / "categories"

PRESERVED_FIELDS = ["id", "name", "type", "parent_id", "entities", "micro_intents", "variations", "source"]


def load_master_csv(csv_path: Path) -> list[dict]:
    """Загружает master CSV."""
    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["volume"] = int(row["volume"])
            rows.append(row)
    return rows


def group_by_category(rows: list[dict]) -> dict[str, list[dict]]:
    """Группирует строки по категориям."""
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)
    return dict(grouped)


def find_clean_json_path(category: str, categories_dir: Path) -> Path | None:
    """Находит путь к _clean.json для категории."""
    # Direct path
    direct = categories_dir / category / "data" / f"{category}_clean.json"
    if direct.exists():
        return direct

    # Search nested
    for path in categories_dir.rglob(f"{category}_clean.json"):
        return path

    return None


def build_keywords_list(rows: list[dict]) -> list[dict]:
    """Строит список keywords из строк CSV."""
    keywords = []
    for row in rows:
        if row["type"] == "keyword":
            kw = {"keyword": row["keyword"], "volume": row["volume"]}
            if row.get("use_in"):
                kw["use_in"] = row["use_in"]
            keywords.append(kw)

    return sorted(keywords, key=lambda x: x["volume"], reverse=True)


def build_synonyms_list(rows: list[dict]) -> list[dict]:
    """Строит список synonyms из строк CSV."""
    synonyms = []
    for row in rows:
        if row["type"] == "synonym":
            syn = {"keyword": row["keyword"], "volume": row["volume"]}
            if row.get("use_in"):
                syn["use_in"] = row["use_in"]
            synonyms.append(syn)

    return sorted(synonyms, key=lambda x: x["volume"], reverse=True)


def sync_category(category: str, rows: list[dict], categories_dir: Path, dry_run: bool = True) -> dict:
    """Синхронизирует одну категорию. Возвращает статистику."""
    clean_path = find_clean_json_path(category, categories_dir)

    if not clean_path:
        # Create new file
        clean_path = categories_dir / category / "data" / f"{category}_clean.json"
        existing = {"id": category, "name": category}
    else:
        existing = json.loads(clean_path.read_text(encoding="utf-8"))

    # Build new keywords/synonyms
    new_keywords = build_keywords_list(rows)
    new_synonyms = build_synonyms_list(rows)

    # Stats
    old_kw_count = len(existing.get("keywords", []))
    old_syn_count = len(existing.get("synonyms", []))

    # Update
    updated = {}
    for field in PRESERVED_FIELDS:
        if field in existing:
            updated[field] = existing[field]

    updated["keywords"] = new_keywords
    updated["synonyms"] = new_synonyms

    stats = {
        "category": category,
        "keywords_before": old_kw_count,
        "keywords_after": len(new_keywords),
        "synonyms_before": old_syn_count,
        "synonyms_after": len(new_synonyms),
    }

    if not dry_run:
        clean_path.parent.mkdir(parents=True, exist_ok=True)
        clean_path.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")

    return stats


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sync master CSV to _clean.json files")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Master CSV path")
    parser.add_argument("--categories-dir", type=Path, default=CATEGORIES_DIR, help="Categories dir")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default: dry-run)")
    parser.add_argument("--categories", type=str, help="Comma-separated list of categories to sync")
    args = parser.parse_args()

    dry_run = not args.apply

    if dry_run:
        print("🔍 DRY-RUN mode (use --apply to make changes)\n")
    else:
        print("📝 APPLYING changes\n")

    print(f"Loading {args.csv}...")
    rows = load_master_csv(args.csv)
    print(f"Loaded {len(rows)} rows")

    grouped = group_by_category(rows)
    print(f"Found {len(grouped)} categories\n")

    # Filter categories if specified
    if args.categories:
        filter_cats = set(args.categories.split(","))
        grouped = {k: v for k, v in grouped.items() if k in filter_cats}
        print(f"Filtering to {len(grouped)} categories\n")

    # Skip uncategorized
    if "uncategorized" in grouped:
        print(f"⚠️  Skipping {len(grouped['uncategorized'])} uncategorized keywords\n")
        del grouped["uncategorized"]

    # Sync each category
    total_stats = {"updated": 0, "kw_added": 0, "kw_removed": 0, "syn_added": 0, "syn_removed": 0}

    for category, cat_rows in sorted(grouped.items()):
        stats = sync_category(category, cat_rows, args.categories_dir, dry_run=dry_run)

        kw_diff = stats["keywords_after"] - stats["keywords_before"]
        syn_diff = stats["synonyms_after"] - stats["synonyms_before"]

        if kw_diff != 0 or syn_diff != 0:
            total_stats["updated"] += 1
            if kw_diff > 0:
                total_stats["kw_added"] += kw_diff
            else:
                total_stats["kw_removed"] += abs(kw_diff)
            if syn_diff > 0:
                total_stats["syn_added"] += syn_diff
            else:
                total_stats["syn_removed"] += abs(syn_diff)

            print(f"  {category}: kw {stats['keywords_before']}→{stats['keywords_after']}, "
                  f"syn {stats['synonyms_before']}→{stats['synonyms_after']}")

    print(f"\n{'Would update' if dry_run else 'Updated'}: {total_stats['updated']} categories")
    print(f"Keywords: +{total_stats['kw_added']} / -{total_stats['kw_removed']}")
    print(f"Synonyms: +{total_stats['syn_added']} / -{total_stats['syn_removed']}")

    if dry_run:
        print("\n💡 Run with --apply to make changes")


if __name__ == "__main__":
    main()
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/unit/test_sync_semantics.py -v
```

Expected: All tests PASS

**Step 5: Commit**

```bash
git add scripts/sync_semantics.py tests/unit/test_sync_semantics.py
git commit -m "feat(semantics): add sync_semantics.py for CSV to _clean.json sync"
```

---

## Task 4: Initial migration — create master CSV

**Files:**
- Output: `data/ru_semantics_master.csv`

**Step 1: Run merge_to_master.py**

```bash
python scripts/merge_to_master.py --excel "reports/проверка_частотности_ключей_которых_нету_в_категориях_Adwords_1769608537.xlsx" "reports/проверка_частотности_ключей_которых_нету_в_категориях_2_Adwords_1769608444.xlsx"
```

**Step 2: Validate result**

```bash
python scripts/validate_master.py
```

Expected: Either PASS or list of warnings/errors to fix

**Step 3: Review CSV manually**

```bash
# Check uncategorized count
grep ",uncategorized," data/ru_semantics_master.csv | wc -l

# Check total count
wc -l data/ru_semantics_master.csv
```

**Step 4: Commit initial CSV**

```bash
git add data/ru_semantics_master.csv
git commit -m "data(semantics): create initial ru_semantics_master.csv"
```

---

## Task 5: Test sync dry-run

**Step 1: Run sync in dry-run mode**

```bash
python scripts/sync_semantics.py --dry-run
```

Expected: List of changes that would be made, no files modified

**Step 2: Verify no changes**

```bash
git status
```

Expected: No modified files in categories/

**Step 3: Pick one category for manual test**

```bash
# Show diff for one category
python scripts/sync_semantics.py --dry-run --categories aktivnaya-pena
```

---

## Task 6: Apply sync and verify pipeline

**Step 1: Apply sync**

```bash
python scripts/sync_semantics.py --apply
```

**Step 2: Verify _clean.json files updated**

```bash
git diff --stat categories/
```

**Step 3: Run existing pipeline validation**

```bash
# Test generate-meta still works
python scripts/validate_meta.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/meta/aktivnaya-pena_meta.json --keywords categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json

# Test content validation still works
python scripts/validate_content.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md "пена для мойки авто" --mode seo
```

Expected: Both validations PASS

**Step 4: Commit**

```bash
git add categories/ data/ru_semantics_master.csv
git commit -m "semantics(ru): migrate to master CSV as single source of truth

- Created ru_semantics_master.csv with all RU keywords
- Synced to _clean.json files
- Pipeline validation passed"
```

---

## Task 7: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Add new workflow section**

Add after "## Команды" section:

```markdown
## Семантика RU (Master CSV)

**Источник истины:** `data/ru_semantics_master.csv`

### Обновление частотности

```bash
# 1. Загрузить свежий Excel в reports/
# 2. Обновить master CSV
python scripts/merge_to_master.py --excel reports/new.xlsx

# 3. Валидация
python scripts/validate_master.py

# 4. Синхронизация в _clean.json
python scripts/sync_semantics.py --apply
```

### Добавление ключей

1. Открыть `data/ru_semantics_master.csv`
2. Добавить строки: `keyword,volume,category,type,use_in`
3. `python scripts/validate_master.py`
4. `python scripts/sync_semantics.py --apply`
```

**Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: add RU semantics master workflow to CLAUDE.md"
```

---

## Summary

| Task | Description | Time Est. |
|------|-------------|-----------|
| 1 | validate_master.py + tests | 15 min |
| 2 | merge_to_master.py + tests | 20 min |
| 3 | sync_semantics.py + tests | 20 min |
| 4 | Initial migration | 5 min |
| 5 | Test sync dry-run | 5 min |
| 6 | Apply sync and verify | 10 min |
| 7 | Update CLAUDE.md | 5 min |

**Total: ~80 min**

---

## Acceptance Criteria

- [ ] `validate_master.py` finds all validation errors
- [ ] `merge_to_master.py` creates CSV from existing data + Excel
- [ ] `sync_semantics.py --dry-run` shows changes without modifying
- [ ] `sync_semantics.py --apply` correctly updates `_clean.json`
- [ ] Existing pipeline (`/generate-meta`, `/content-generator`) works
- [ ] All tests pass: `pytest tests/unit/test_validate_master.py tests/unit/test_merge_to_master.py tests/unit/test_sync_semantics.py -v`
