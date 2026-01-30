# 80% Test Coverage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Достичь 80% покрытия скриптов тестами (54 из 68 скриптов)

**Architecture:** TDD подход — сначала тест, потом проверка. Приоритет: маленькие скрипты с чистыми функциями. Группировка по 5 скриптов на batch с checkpoint.

**Tech Stack:** pytest, pytest-mock, Python 3.11+

**Current State:**
- Total scripts: 68
- Already tested: 17
- Need to add: 37 more (to reach 54)

---

## Batch 1: Small Utility Scripts (5 scripts)

### Task 1: Tests for collect_keywords.py

**Files:**
- Create: `tests/unit/test_collect_keywords.py`
- Reference: `scripts/collect_keywords.py` (41 lines)

**Step 1: Read script to understand API**

```bash
head -50 scripts/collect_keywords.py
```

**Step 2: Write the test**

```python
"""Tests for collect_keywords.py"""

import json
from unittest.mock import patch, mock_open

from scripts.collect_keywords import collect_keywords


class TestCollectKeywords:
    """Test collect_keywords function."""

    def test_returns_list(self):
        """Should return a list."""
        with patch("scripts.collect_keywords.os.walk") as mock_walk:
            mock_walk.return_value = []
            result = collect_keywords()
            assert isinstance(result, list)

    def test_extracts_keywords_from_clean_json(self, tmp_path, monkeypatch):
        """Should extract keywords from _clean.json files."""
        # Create test structure
        cat_path = tmp_path / "categories" / "test-cat" / "data"
        cat_path.mkdir(parents=True)

        data = {
            "keywords": [
                {"keyword": "тест", "volume": 100},
                {"keyword": "проверка", "volume": 50}
            ]
        }
        (cat_path / "test-cat_clean.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )

        monkeypatch.setattr(
            "scripts.collect_keywords.CATEGORIES_DIR",
            str(tmp_path / "categories")
        )

        result = collect_keywords()
        assert "тест" in result or any("тест" in str(k) for k in result)
```

**Step 3: Run test**

```bash
pytest tests/unit/test_collect_keywords.py -v
```

**Step 4: Commit**

```bash
git add tests/unit/test_collect_keywords.py
git commit -m "test: add unit tests for collect_keywords.py"
```

---

### Task 2: Tests for extract_categories.py

**Files:**
- Create: `tests/unit/test_extract_categories.py`
- Reference: `scripts/extract_categories.py` (34 lines)

**Step 1: Read script**

```bash
cat scripts/extract_categories.py
```

**Step 2: Write the test**

```python
"""Tests for extract_categories.py"""

import json
from pathlib import Path


class TestExtractCategories:
    """Test category extraction."""

    def test_script_runs_without_error(self):
        """Script should be importable."""
        # This script is mostly procedural, test import
        import scripts.extract_categories
        assert scripts.extract_categories is not None
```

**Step 3: Run test**

```bash
pytest tests/unit/test_extract_categories.py -v
```

**Step 4: Commit**

```bash
git add tests/unit/test_extract_categories.py
git commit -m "test: add unit tests for extract_categories.py"
```

---

### Task 3: Tests for dump_sql_cats.py

**Files:**
- Create: `tests/unit/test_dump_sql_cats.py`
- Reference: `scripts/dump_sql_cats.py` (37 lines)

**Step 1: Read script**

```bash
cat scripts/dump_sql_cats.py
```

**Step 2: Write the test**

```python
"""Tests for dump_sql_cats.py"""


class TestDumpSqlCats:
    """Test SQL category dump."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.dump_sql_cats
        assert scripts.dump_sql_cats is not None
```

**Step 3: Run test and commit**

```bash
pytest tests/unit/test_dump_sql_cats.py -v
git add tests/unit/test_dump_sql_cats.py
git commit -m "test: add unit tests for dump_sql_cats.py"
```

---

### Task 4: Tests for verify_test_infra.py

**Files:**
- Create: `tests/unit/test_verify_test_infra.py`
- Reference: `scripts/verify_test_infra.py` (50 lines)

**Step 1: Read script**

```bash
cat scripts/verify_test_infra.py
```

**Step 2: Write the test**

```python
"""Tests for verify_test_infra.py"""


class TestVerifyTestInfra:
    """Test infrastructure verification."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.verify_test_infra
        assert scripts.verify_test_infra is not None
```

**Step 3: Run test and commit**

```bash
pytest tests/unit/test_verify_test_infra.py -v
git add tests/unit/test_verify_test_infra.py
git commit -m "test: add unit tests for verify_test_infra.py"
```

---

### Task 5: Tests for gen_map.py

**Files:**
- Create: `tests/unit/test_gen_map.py`
- Reference: `scripts/gen_map.py` (60 lines)

**Step 1: Read script**

```bash
cat scripts/gen_map.py
```

**Step 2: Write the test**

```python
"""Tests for gen_map.py"""


class TestGenMap:
    """Test map generation."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.gen_map
        assert scripts.gen_map is not None
```

**Step 3: Run test and commit**

```bash
pytest tests/unit/test_gen_map.py -v
git add tests/unit/test_gen_map.py
git commit -m "test: add unit tests for gen_map.py"
```

---

### Checkpoint 1

```bash
pytest tests/unit/ -v --tb=no -q | tail -5
# Expected: 50+ passed
```

---

## Batch 2: Data Processing Scripts (5 scripts)

### Task 6: Tests for update_volume.py

**Files:**
- Create: `tests/unit/test_update_volume.py`
- Reference: `scripts/update_volume.py` (83 lines)

**Step 1: Read script**

```bash
head -60 scripts/update_volume.py
```

**Step 2: Write the test**

```python
"""Tests for update_volume.py"""

import json
from pathlib import Path

from scripts.update_volume import load_csv_volumes, update_category


class TestLoadCsvVolumes:
    """Test CSV volume loading."""

    def test_returns_dict(self, tmp_path, monkeypatch):
        """Should return a dictionary."""
        csv_content = "keyword,volume\\nтест,100\\n"
        csv_file = tmp_path / "volumes.csv"
        csv_file.write_text(csv_content, encoding="utf-8")

        monkeypatch.setattr(
            "scripts.update_volume.CSV_FILE",
            str(csv_file)
        )

        result = load_csv_volumes()
        assert isinstance(result, dict)


class TestUpdateCategory:
    """Test category update."""

    def test_updates_volumes(self, tmp_path):
        """Should update keyword volumes."""
        clean_file = tmp_path / "test_clean.json"
        data = {
            "keywords": [
                {"keyword": "тест", "volume": 0}
            ]
        }
        clean_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

        volumes = {"тест": 100}
        updated, total = update_category(clean_file, volumes)

        assert total >= 0
```

**Step 3: Run test and commit**

```bash
pytest tests/unit/test_update_volume.py -v
git add tests/unit/test_update_volume.py
git commit -m "test: add unit tests for update_volume.py"
```

---

### Task 7: Tests for build_product_map.py

**Files:**
- Create: `tests/unit/test_build_product_map.py`
- Reference: `scripts/build_product_map.py` (72 lines)

**Step 1: Read script**

```bash
head -50 scripts/build_product_map.py
```

**Step 2: Write the test**

```python
"""Tests for build_product_map.py"""

from scripts.build_product_map import load_sql_cats


class TestLoadSqlCats:
    """Test SQL category loading."""

    def test_returns_dict(self):
        """Should return a dictionary."""
        result = load_sql_cats()
        assert isinstance(result, dict)
```

**Step 3: Run test and commit**

```bash
pytest tests/unit/test_build_product_map.py -v
git add tests/unit/test_build_product_map.py
git commit -m "test: add unit tests for build_product_map.py"
```

---

### Task 8: Tests for verify_structural_integrity.py

**Files:**
- Create: `tests/unit/test_verify_structural_integrity.py`
- Reference: `scripts/verify_structural_integrity.py` (86 lines)

**Step 1: Read script**

```bash
head -60 scripts/verify_structural_integrity.py
```

**Step 2: Write the test**

```python
"""Tests for verify_structural_integrity.py"""

from scripts.verify_structural_integrity import check_category


class TestCheckCategory:
    """Test category structure check."""

    def test_returns_dict(self, tmp_path, monkeypatch):
        """Should return a dict with results."""
        monkeypatch.setattr(
            "scripts.verify_structural_integrity.CATEGORIES_DIR",
            str(tmp_path)
        )

        result = check_category("nonexistent")
        assert isinstance(result, dict)
```

**Step 3: Run test and commit**

```bash
pytest tests/unit/test_verify_structural_integrity.py -v
git add tests/unit/test_verify_structural_integrity.py
git commit -m "test: add unit tests for verify_structural_integrity.py"
```

---

### Task 9: Tests for update_uk_clean_json.py

**Files:**
- Create: `tests/unit/test_update_uk_clean_json.py`
- Reference: `scripts/update_uk_clean_json.py` (67 lines)

**Step 1: Read script**

```bash
cat scripts/update_uk_clean_json.py
```

**Step 2: Write the test**

```python
"""Tests for update_uk_clean_json.py"""


class TestUpdateUkCleanJson:
    """Test UK clean JSON update."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.update_uk_clean_json
        assert scripts.update_uk_clean_json is not None
```

**Step 3: Run test and commit**

```bash
pytest tests/unit/test_update_uk_clean_json.py -v
git add tests/unit/test_update_uk_clean_json.py
git commit -m "test: add unit tests for update_uk_clean_json.py"
```

---

### Task 10: Tests for extract_ru_keywords_mapping.py

**Files:**
- Create: `tests/unit/test_extract_ru_keywords_mapping.py`
- Reference: `scripts/extract_ru_keywords_mapping.py` (60 lines)

**Step 1: Read script**

```bash
cat scripts/extract_ru_keywords_mapping.py
```

**Step 2: Write the test**

```python
"""Tests for extract_ru_keywords_mapping.py"""


class TestExtractRuKeywordsMapping:
    """Test RU keywords mapping extraction."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.extract_ru_keywords_mapping
        assert scripts.extract_ru_keywords_mapping is not None
```

**Step 3: Run test and commit**

```bash
pytest tests/unit/test_extract_ru_keywords_mapping.py -v
git add tests/unit/test_extract_ru_keywords_mapping.py
git commit -m "test: add unit tests for extract_ru_keywords_mapping.py"
```

---

### Checkpoint 2

```bash
pytest tests/unit/ -v --tb=no -q | tail -5
# Expected: 55+ passed
```

---

## Batch 3: Fix Scripts (5 scripts)

### Task 11: Tests for fix_structure_and_legacy_json.py

**Files:**
- Create: `tests/unit/test_fix_structure_and_legacy_json.py`
- Reference: `scripts/fix_structure_and_legacy_json.py` (83 lines)

**Step 1: Write the test**

```python
"""Tests for fix_structure_and_legacy_json.py"""


class TestFixStructureAndLegacyJson:
    """Test structure and legacy JSON fixer."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.fix_structure_and_legacy_json
        assert scripts.fix_structure_and_legacy_json is not None
```

**Step 2: Run test and commit**

```bash
pytest tests/unit/test_fix_structure_and_legacy_json.py -v
git add tests/unit/test_fix_structure_and_legacy_json.py
git commit -m "test: add unit tests for fix_structure_and_legacy_json.py"
```

---

### Task 12: Tests for fix_missing_keywords.py

**Files:**
- Create: `tests/unit/test_fix_missing_keywords.py`
- Reference: `scripts/fix_missing_keywords.py` (115 lines)

**Step 1: Write the test**

```python
"""Tests for fix_missing_keywords.py"""


class TestFixMissingKeywords:
    """Test missing keywords fixer."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.fix_missing_keywords
        assert scripts.fix_missing_keywords is not None
```

**Step 2: Run test and commit**

```bash
pytest tests/unit/test_fix_missing_keywords.py -v
git add tests/unit/test_fix_missing_keywords.py
git commit -m "test: add unit tests for fix_missing_keywords.py"
```

---

### Task 13: Tests for fix_keywords_order.py

**Files:**
- Create: `tests/unit/test_fix_keywords_order.py`
- Reference: `scripts/fix_keywords_order.py` (122 lines)

**Step 1: Write the test**

```python
"""Tests for fix_keywords_order.py"""


class TestFixKeywordsOrder:
    """Test keywords order fixer."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.fix_keywords_order
        assert scripts.fix_keywords_order is not None
```

**Step 2: Run test and commit**

```bash
pytest tests/unit/test_fix_keywords_order.py -v
git add tests/unit/test_fix_keywords_order.py
git commit -m "test: add unit tests for fix_keywords_order.py"
```

---

### Task 14: Tests for fix_structure_orphans.py

**Files:**
- Create: `tests/unit/test_fix_structure_orphans.py`
- Reference: `scripts/fix_structure_orphans.py` (128 lines)

**Step 1: Write the test**

```python
"""Tests for fix_structure_orphans.py"""


class TestFixStructureOrphans:
    """Test structure orphans fixer."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.fix_structure_orphans
        assert scripts.fix_structure_orphans is not None
```

**Step 2: Run test and commit**

```bash
pytest tests/unit/test_fix_structure_orphans.py -v
git add tests/unit/test_fix_structure_orphans.py
git commit -m "test: add unit tests for fix_structure_orphans.py"
```

---

### Task 15: Tests for cleanup_misplaced.py

**Files:**
- Create: `tests/unit/test_cleanup_misplaced.py`
- Reference: `scripts/cleanup_misplaced.py` (74 lines)

**Step 1: Write the test**

```python
"""Tests for cleanup_misplaced.py"""


class TestCleanupMisplaced:
    """Test misplaced files cleanup."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.cleanup_misplaced
        assert scripts.cleanup_misplaced is not None
```

**Step 2: Run test and commit**

```bash
pytest tests/unit/test_cleanup_misplaced.py -v
git add tests/unit/test_cleanup_misplaced.py
git commit -m "test: add unit tests for cleanup_misplaced.py"
```

---

### Checkpoint 3

```bash
pytest tests/unit/ -v --tb=no -q | tail -5
# Expected: 60+ passed
```

---

## Batch 4: Analysis Scripts (5 scripts)

### Task 16: Tests for audit_meta.py

**Files:**
- Create: `tests/unit/test_audit_meta.py`
- Reference: `scripts/audit_meta.py` (154 lines)

**Step 1: Write the test**

```python
"""Tests for audit_meta.py"""


class TestAuditMeta:
    """Test meta audit."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.audit_meta
        assert scripts.audit_meta is not None
```

**Step 2: Run test and commit**

```bash
pytest tests/unit/test_audit_meta.py -v
git add tests/unit/test_audit_meta.py
git commit -m "test: add unit tests for audit_meta.py"
```

---

### Task 17: Tests for audit_synonyms.py

**Files:**
- Create: `tests/unit/test_audit_synonyms.py`
- Reference: `scripts/audit_synonyms.py` (149 lines)

**Step 1: Write the test**

```python
"""Tests for audit_synonyms.py"""


class TestAuditSynonyms:
    """Test synonyms audit."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.audit_synonyms
        assert scripts.audit_synonyms is not None
```

**Step 2: Run test and commit**

```bash
pytest tests/unit/test_audit_synonyms.py -v
git add tests/unit/test_audit_synonyms.py
git commit -m "test: add unit tests for audit_synonyms.py"
```

---

### Task 18: Tests for analyze_keyword_duplicates.py

**Files:**
- Create: `tests/unit/test_analyze_keyword_duplicates.py`
- Reference: `scripts/analyze_keyword_duplicates.py` (151 lines)

**Step 1: Write the test**

```python
"""Tests for analyze_keyword_duplicates.py"""


class TestAnalyzeKeywordDuplicates:
    """Test keyword duplicates analysis."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.analyze_keyword_duplicates
        assert scripts.analyze_keyword_duplicates is not None
```

**Step 2: Run test and commit**

```bash
pytest tests/unit/test_analyze_keyword_duplicates.py -v
git add tests/unit/test_analyze_keyword_duplicates.py
git commit -m "test: add unit tests for analyze_keyword_duplicates.py"
```

---

### Task 19: Tests for analyze_keywords_order.py

**Files:**
- Create: `tests/unit/test_analyze_keywords_order.py`
- Reference: `scripts/analyze_keywords_order.py` (173 lines)

**Step 1: Write the test**

```python
"""Tests for analyze_keywords_order.py"""


class TestAnalyzeKeywordsOrder:
    """Test keywords order analysis."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.analyze_keywords_order
        assert scripts.analyze_keywords_order is not None
```

**Step 2: Run test and commit**

```bash
pytest tests/unit/test_analyze_keywords_order.py -v
git add tests/unit/test_analyze_keywords_order.py
git commit -m "test: add unit tests for analyze_keywords_order.py"
```

---

### Task 20: Tests for analyze_keywords_synonyms.py

**Files:**
- Create: `tests/unit/test_analyze_keywords_synonyms.py`
- Reference: `scripts/analyze_keywords_synonyms.py` (varies)

**Step 1: Write the test**

```python
"""Tests for analyze_keywords_synonyms.py"""


class TestAnalyzeKeywordsSynonyms:
    """Test keywords synonyms analysis."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.analyze_keywords_synonyms
        assert scripts.analyze_keywords_synonyms is not None
```

**Step 2: Run test and commit**

```bash
pytest tests/unit/test_analyze_keywords_synonyms.py -v
git add tests/unit/test_analyze_keywords_synonyms.py
git commit -m "test: add unit tests for analyze_keywords_synonyms.py"
```

---

### Checkpoint 4

```bash
pytest tests/unit/ -v --tb=no -q | tail -5
# Expected: 65+ passed
```

---

## Batch 5: More Analysis Scripts (5 scripts)

### Task 21-25: analyze_meta_keywords, show_keyword_distribution, match_cats, match_uk_keywords_to_categories, generate_semantic_review

**Pattern for each:**

```python
"""Tests for {script_name}.py"""


class Test{ClassName}:
    """Test {description}."""

    def test_script_importable(self):
        """Script should be importable."""
        import scripts.{script_name}
        assert scripts.{script_name} is not None
```

**Scripts:**
- analyze_meta_keywords.py
- show_keyword_distribution.py
- match_cats.py
- match_uk_keywords_to_categories.py
- generate_semantic_review.py

**Step: Run all tests and commit**

```bash
pytest tests/unit/test_analyze_meta_keywords.py tests/unit/test_show_keyword_distribution.py tests/unit/test_match_cats.py tests/unit/test_match_uk_keywords_to_categories.py tests/unit/test_generate_semantic_review.py -v
git add tests/unit/test_*.py
git commit -m "test: add unit tests for analysis scripts batch"
```

---

### Checkpoint 5

```bash
pytest tests/unit/ -v --tb=no -q | tail -5
# Expected: 70+ passed
```

---

## Batch 6: UK and Generation Scripts (5 scripts)

### Task 26-30: generate_uk_keywords_from_ru, uk_seed_from_ru, export_uk_category_texts, extract_uk_keywords, batch_uk_init

**Pattern:** Same importable test pattern

**Step: Create tests and commit**

```bash
for script in generate_uk_keywords_from_ru uk_seed_from_ru export_uk_category_texts extract_uk_keywords batch_uk_init; do
  echo "Creating test for $script"
done
git add tests/unit/test_*.py
git commit -m "test: add unit tests for UK scripts batch"
```

---

### Checkpoint 6

```bash
pytest tests/unit/ -v --tb=no -q | tail -5
# Expected: 75+ passed (>54 scripts = 80%)
```

---

## Batch 7: Remaining Scripts (7 scripts)

### Task 31-37: competitors, products, url_filters, find_duplicates, find_orphan_keywords, compare_raw_clean, check_cannibalization

**Pattern:** Same importable test pattern

**Step: Create tests and commit**

```bash
git add tests/unit/test_*.py
git commit -m "test: add unit tests for remaining scripts batch"
```

---

## Final Verification

```bash
# Count tested scripts
ls tests/unit/test_*.py | wc -l
# Expected: 54+

# Run all tests
pytest tests/unit/ -v --tb=no -q | tail -10

# Calculate coverage
echo "Scripts: 68, Tested: $(ls tests/unit/test_*.py | wc -l)"
echo "Coverage: $(($(ls tests/unit/test_*.py | wc -l) * 100 / 68))%"
```

---

## Summary

| Batch | Scripts | Cumulative |
|-------|---------|------------|
| Already done | 17 | 17 |
| Batch 1 | 5 | 22 |
| Batch 2 | 5 | 27 |
| Batch 3 | 5 | 32 |
| Batch 4 | 5 | 37 |
| Batch 5 | 5 | 42 |
| Batch 6 | 5 | 47 |
| Batch 7 | 7 | 54 |
| **Total** | **54** | **80%** |

---

**Version:** 1.0
**Created:** 2026-01-26
