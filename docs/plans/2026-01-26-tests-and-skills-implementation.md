# Tests & Skills Optimization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Покрыть 80% скриптов тестами (54/67) + оптимизировать RU/UK скиллы через shared references

**Architecture:** TDD подход (Red → Green → Refactor), параллельные задачи A (тесты) и B (скиллы)

**Tech Stack:** pytest, pytest-mock, Python 3.11+

---

## Task 1: Создать fixtures для тестов

**Files:**
- Create: `tests/fixtures/sample_clean.json`
- Create: `tests/fixtures/sample_meta.json`
- Create: `tests/fixtures/sample_content.md`

**Step 1: Создать sample_clean.json**

```json
{
  "id": "test-category",
  "name": "Тестовая категория",
  "parent_id": "parent-slug",
  "keywords": [
    {"keyword": "тестовый ключ", "volume": 1000},
    {"keyword": "второй ключ", "volume": 500}
  ],
  "synonyms": [
    {"keyword": "синоним", "volume": 100, "use_in": "content"}
  ],
  "micro_intents": ["как выбрать", "какой лучше"]
}
```

**Step 2: Создать sample_meta.json**

```json
{
  "slug": "test-category",
  "language": "ru",
  "meta": {
    "title": "Тестовый ключ — купить в интернет-магазине Ultimate",
    "description": "Тестовый ключ от производителя Ultimate. Типы и формы — подробности. Опт и розница."
  },
  "h1": "Тестовый ключ",
  "keywords_in_content": {
    "primary": ["тестовый ключ"],
    "secondary": ["второй ключ"],
    "supporting": ["синоним"]
  }
}
```

**Step 3: Создать sample_content.md**

```markdown
# Тестовый ключ

Тестовый ключ помогает решить задачу. Если вам нужен качественный результат — выбирайте проверенные варианты.

## Как выбрать тестовый ключ

| Тип | Особенности | Для кого |
|-----|-------------|----------|
| Тип А | Быстрый | Новички |
| Тип Б | Надёжный | Профи |

**Сценарии:**
- **Если нужна скорость** → выбирай Тип А
- **Если важна надёжность** → выбирай Тип Б

## FAQ

### Какой тип выбрать новичку?
Начните с Тип А — он проще в использовании.

### Сколько держится результат?
Зависит от условий, обычно достаточно для повседневного использования.
```

**Step 4: Commit**

```bash
git add tests/fixtures/
git commit -m "test: add sample fixtures for unit tests"
```

---

## Task 2: Тесты для md_to_html.py

**Files:**
- Create: `tests/unit/test_md_to_html.py`
- Reference: `scripts/md_to_html.py`

**Step 1: Write the failing test (basic)**

```python
"""Tests for md_to_html.py"""

import pytest

from scripts.md_to_html import md_to_html, convert_tables, convert_lists


class TestMdToHtml:
    """Test md_to_html main function."""

    def test_removes_h1_from_output(self):
        """H1 should be removed (goes to meta_h1)."""
        md = "# Заголовок H1\n\n## Заголовок H2\n\nТекст."
        html = md_to_html(md)
        assert "<h1>" not in html
        assert "Заголовок H1" not in html

    def test_converts_h2_to_html(self):
        """## should become <h2>."""
        md = "## Заголовок"
        html = md_to_html(md)
        assert "<h2>Заголовок</h2>" in html

    def test_converts_h3_to_html(self):
        """### should become <h3>."""
        md = "### Подзаголовок"
        html = md_to_html(md)
        assert "<h3>Подзаголовок</h3>" in html

    def test_converts_bold_to_strong(self):
        """**text** should become <strong>."""
        md = "**жирный текст**"
        html = md_to_html(md)
        assert "<strong>жирный текст</strong>" in html

    def test_handles_empty_input(self):
        """Empty input should return empty string."""
        assert md_to_html("") == ""

    def test_handles_cyrillic_text(self):
        """Cyrillic text should be preserved."""
        md = "## Кириллица\n\nТекст на русском."
        html = md_to_html(md)
        assert "Кириллица" in html
        assert "русском" in html
```

**Step 2: Run test to verify it passes**

```bash
pytest tests/unit/test_md_to_html.py -v
```

Expected: All PASS (скрипт уже существует)

**Step 3: Add edge case tests**

```python
class TestConvertTables:
    """Test table conversion."""

    def test_converts_simple_table(self):
        """Simple markdown table should become HTML table."""
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = convert_tables(md)
        assert "<table" in html
        assert "<th>" in html or "<td>" in html

    def test_preserves_cyrillic_in_table(self):
        """Cyrillic in table cells should be preserved."""
        md = "| Колонка |\n|---|\n| Значение |"
        html = convert_tables(md)
        assert "Колонка" in html
        assert "Значение" in html

    def test_handles_empty_table(self):
        """Empty or malformed table should not crash."""
        md = "| |\n|---|"
        html = convert_tables(md)
        assert html is not None


class TestConvertLists:
    """Test list conversion."""

    def test_converts_unordered_list(self):
        """- items should become <ul><li>."""
        md = "- item 1\n- item 2"
        html = convert_lists(md)
        assert "<ul>" in html
        assert "<li>item 1</li>" in html
        assert "</ul>" in html

    def test_handles_nested_content(self):
        """List followed by text should close properly."""
        md = "- item\n\nПараграф"
        html = convert_lists(md)
        assert "</ul>" in html
```

**Step 4: Run all tests**

```bash
pytest tests/unit/test_md_to_html.py -v
```

Expected: All PASS

**Step 5: Commit**

```bash
git add tests/unit/test_md_to_html.py
git commit -m "test: add unit tests for md_to_html.py"
```

---

## Task 3: Тесты для generate_sql.py

**Files:**
- Create: `tests/unit/test_generate_sql.py`
- Reference: `scripts/generate_sql.py`

**Step 1: Write the failing test**

```python
"""Tests for generate_sql.py"""

import pytest

from scripts.generate_sql import (
    escape_sql,
    md_to_html,
    build_html_table,
    convert_tables,
    convert_lists,
)


class TestEscapeSql:
    """Test SQL escaping."""

    def test_escapes_single_quotes(self):
        """Single quotes should be escaped."""
        assert escape_sql("it's") == "it\\'s"

    def test_escapes_double_quotes(self):
        """Double quotes should be escaped."""
        assert escape_sql('say "hello"') == 'say \\"hello\\"'

    def test_escapes_backslashes(self):
        """Backslashes should be escaped."""
        assert escape_sql("path\\to") == "path\\\\to"

    def test_handles_empty_string(self):
        """Empty string should return empty."""
        assert escape_sql("") == ""

    def test_handles_cyrillic(self):
        """Cyrillic should be preserved."""
        assert escape_sql("Привет") == "Привет"

    def test_complex_escaping(self):
        """Multiple special chars in one string."""
        result = escape_sql("It's a \"test\" with \\ backslash")
        assert "\\'" in result
        assert '\\"' in result
        assert "\\\\" in result


class TestMdToHtmlGenerateSql:
    """Test md_to_html from generate_sql module."""

    def test_extracts_h1(self):
        """H1 should be extracted separately."""
        md = "# Заголовок\n\nТекст"
        h1, html = md_to_html(md)
        assert h1 == "Заголовок"
        assert "Заголовок" not in html or "<h1>" not in html

    def test_returns_empty_h1_if_missing(self):
        """No H1 should return empty string."""
        md = "## H2 Only\n\nТекст"
        h1, html = md_to_html(md)
        assert h1 == ""

    def test_converts_body_to_html(self):
        """Body should be converted to HTML."""
        md = "# H1\n\n## H2\n\nПараграф"
        h1, html = md_to_html(md)
        assert "<h2>" in html or "H2" in html


class TestBuildHtmlTable:
    """Test HTML table building."""

    def test_builds_simple_table(self):
        """Should build valid HTML table."""
        lines = ["| A | B |", "|---|---|", "| 1 | 2 |"]
        html = build_html_table(lines)
        assert "<table>" in html
        assert "<th>" in html
        assert "<td>" in html
        assert "</table>" in html

    def test_returns_original_if_invalid(self):
        """Invalid table should return original lines."""
        lines = ["not a table"]
        result = build_html_table(lines)
        assert "not a table" in result
```

**Step 2: Run test to verify**

```bash
pytest tests/unit/test_generate_sql.py -v
```

Expected: All PASS

**Step 3: Commit**

```bash
git add tests/unit/test_generate_sql.py
git commit -m "test: add unit tests for generate_sql.py"
```

---

## Task 4: Тесты для upload_to_db.py (с mock)

**Files:**
- Create: `tests/unit/test_upload_to_db.py`
- Reference: `scripts/upload_to_db.py`

**Step 1: Write the failing test with mocks**

```python
"""Tests for upload_to_db.py"""

import pytest
from unittest.mock import patch, MagicMock

from scripts.upload_to_db import (
    md_to_html,
    convert_tables,
    convert_lists,
    wrap_paragraphs,
    load_category_data,
    update_database,
    CATEGORY_IDS,
)


class TestMdToHtmlUpload:
    """Test md_to_html from upload_to_db module."""

    def test_removes_h1(self):
        """H1 should be removed from output."""
        md = "# Заголовок\n\nТекст"
        html = md_to_html(md)
        assert "# Заголовок" not in html

    def test_converts_h2(self):
        """H2 should be converted."""
        md = "## Секция"
        html = md_to_html(md)
        assert "<h2>Секция</h2>" in html

    def test_converts_bold(self):
        """Bold should be converted."""
        md = "**жирный**"
        html = md_to_html(md)
        assert "<strong>жирный</strong>" in html


class TestConvertTablesUpload:
    """Test table conversion."""

    def test_simple_table(self):
        """Simple table should convert."""
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        html = convert_tables(md)
        assert "<table" in html
        assert "border=" in html


class TestConvertListsUpload:
    """Test list conversion."""

    def test_unordered_list(self):
        """Unordered list should convert."""
        md = "- item 1\n- item 2"
        html = convert_lists(md)
        assert "<ul>" in html
        assert "<li>item 1</li>" in html


class TestWrapParagraphs:
    """Test paragraph wrapping."""

    def test_wraps_text_in_p(self):
        """Plain text should be wrapped in <p>."""
        text = "Простой текст"
        html = wrap_paragraphs(text)
        assert "<p>" in html
        assert "Простой текст" in html

    def test_skips_headings(self):
        """Headings should not be wrapped."""
        text = "<h2>Заголовок</h2>"
        html = wrap_paragraphs(text)
        assert "<p><h2>" not in html


class TestLoadCategoryData:
    """Test category data loading with mocks."""

    @patch("builtins.open")
    def test_loads_ru_content(self, mock_open):
        """Should load RU content files."""
        mock_md = MagicMock()
        mock_md.read.return_value = "# Test\n\nContent"
        mock_md.__enter__ = MagicMock(return_value=mock_md)
        mock_md.__exit__ = MagicMock(return_value=False)

        mock_json = MagicMock()
        mock_json.read.return_value = '{"meta": {"title": "T", "description": "D"}, "h1": "H"}'
        mock_json.__enter__ = MagicMock(return_value=mock_json)
        mock_json.__exit__ = MagicMock(return_value=False)

        mock_open.side_effect = [mock_md, mock_json]

        # Need to patch CATEGORY_IDS to include test slug
        with patch.dict("scripts.upload_to_db.CATEGORY_IDS", {"test-slug": 999}):
            data = load_category_data("test-slug", "ru")

        assert data["slug"] == "test-slug"
        assert data["language_id"] == 3  # LANG_RU


class TestUpdateDatabase:
    """Test database update with mocks."""

    def test_dry_run_does_not_connect(self, capsys):
        """Dry run should print but not connect."""
        data = {
            "slug": "test",
            "category_id": 1,
            "language_id": 3,
            "description": "<p>Test</p>",
            "meta_title": "Title",
            "meta_description": "Desc",
            "meta_h1": "H1",
        }
        update_database(data, dry_run=True)
        captured = capsys.readouterr()
        assert "[DRY RUN]" in captured.out

    @patch("scripts.upload_to_db.mysql.connector.connect")
    def test_connects_to_database(self, mock_connect):
        """Should connect and execute query."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        data = {
            "slug": "test",
            "category_id": 1,
            "language_id": 3,
            "description": "<p>Test</p>",
            "meta_title": "Title",
            "meta_description": "Desc",
            "meta_h1": "H1",
        }
        update_database(data, dry_run=False)

        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()
```

**Step 2: Run test**

```bash
pytest tests/unit/test_upload_to_db.py -v
```

Expected: All PASS

**Step 3: Commit**

```bash
git add tests/unit/test_upload_to_db.py
git commit -m "test: add unit tests for upload_to_db.py with mocks"
```

---

## Task 5: Тесты для validate_uk.py

**Files:**
- Create: `tests/unit/test_validate_uk.py`
- Reference: `scripts/validate_uk.py`

**Step 1: Write the test**

```python
"""Tests for validate_uk.py"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from scripts.validate_uk import validate_uk_category


class TestValidateUkCategory:
    """Test UK category validation."""

    def test_fails_if_folder_missing(self, tmp_path):
        """Should fail if UK folder doesn't exist."""
        with patch("scripts.validate_uk.Path") as mock_path:
            mock_path.return_value.exists.return_value = False
            result = validate_uk_category("nonexistent")
        assert result == 2  # FAIL

    def test_fails_if_required_files_missing(self, tmp_path):
        """Should fail if required files are missing."""
        uk_path = tmp_path / "uk/categories/test-slug"
        uk_path.mkdir(parents=True)

        with patch("scripts.validate_uk.Path") as mock_path:
            mock_instance = MagicMock()
            mock_instance.exists.return_value = True
            mock_instance.__truediv__ = lambda self, x: MagicMock(exists=MagicMock(return_value=False))
            mock_path.return_value = mock_instance

            result = validate_uk_category("test-slug")
        assert result == 2  # FAIL

    def test_warns_on_russian_words_in_meta(self, tmp_path):
        """Should warn if Russian words found in UK meta."""
        # Setup test directory
        uk_path = tmp_path / "uk" / "categories" / "test-slug"
        (uk_path / "data").mkdir(parents=True)
        (uk_path / "meta").mkdir(parents=True)
        (uk_path / "content").mkdir(parents=True)

        # Create required files
        (uk_path / "data" / "test-slug_clean.json").write_text("{}", encoding="utf-8")

        meta = {
            "h1": "Тестовий заголовок",
            "meta": {
                "title": "Купить тест",  # Russian word!
                "description": "Опис"
            }
        }
        (uk_path / "meta" / "test-slug_meta.json").write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8"
        )
        (uk_path / "content" / "test-slug_uk.md").write_text(
            "# Заголовок\n\n" + "Текст " * 100, encoding="utf-8"
        )

        # Patch Path to use tmp_path
        original_path = Path

        def patched_path(p):
            if p.startswith("uk/categories"):
                return tmp_path / p
            return original_path(p)

        with patch("scripts.validate_uk.Path", side_effect=patched_path):
            result = validate_uk_category("test-slug")

        assert result == 1  # WARNING

    def test_passes_valid_category(self, tmp_path):
        """Should pass if all checks are OK."""
        uk_path = tmp_path / "uk" / "categories" / "test-slug"
        (uk_path / "data").mkdir(parents=True)
        (uk_path / "meta").mkdir(parents=True)
        (uk_path / "content").mkdir(parents=True)

        (uk_path / "data" / "test-slug_clean.json").write_text("{}", encoding="utf-8")

        meta = {
            "h1": "Тестовий заголовок",
            "meta": {
                "title": "Купити тест в Україні",
                "description": "Опис категорії українською"
            }
        }
        (uk_path / "meta" / "test-slug_meta.json").write_text(
            json.dumps(meta, ensure_ascii=False), encoding="utf-8"
        )
        (uk_path / "content" / "test-slug_uk.md").write_text(
            "# Заголовок\n\n" + "Текст українською мовою " * 50, encoding="utf-8"
        )

        original_path = Path

        def patched_path(p):
            if p.startswith("uk/categories"):
                return tmp_path / p
            return original_path(p)

        with patch("scripts.validate_uk.Path", side_effect=patched_path):
            result = validate_uk_category("test-slug")

        assert result == 0  # PASS
```

**Step 2: Run test**

```bash
pytest tests/unit/test_validate_uk.py -v
```

Expected: All PASS

**Step 3: Commit**

```bash
git add tests/unit/test_validate_uk.py
git commit -m "test: add unit tests for validate_uk.py"
```

---

## Task 6: Создать shared/ для скиллов

**Files:**
- Create: `.claude/skills/shared/validation-checklist.md`

**Step 1: Create shared directory and validation-checklist.md**

```markdown
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
python3 scripts/check_keyword_density.py {content_path}

# Water/nausea
python3 scripts/check_water_natasha.py {content_path}

# SEO structure
python3 scripts/check_seo_structure.py {content_path} "{primary}"
```
```

**Step 2: Commit**

```bash
git add .claude/skills/shared/
git commit -m "feat: add shared validation-checklist.md for skills"
```

---

## Task 7: Создать shared/meta-rules.md

**Files:**
- Create: `.claude/skills/shared/meta-rules.md`

**Step 1: Create meta-rules.md**

```markdown
# Shared Meta Rules

Common meta tag rules for RU and UK categories.

---

## IRON RULE: primary_keyword — VERBATIM

`{primary_keyword}` from `_clean.json` is used in Title/H1/Description **without changing words or order**.

Only allowed: capitalize first letter.

```
_clean.json: "keywords": [{"keyword": "воск для авто", "volume": 1000}]

✅ Title: Воск для авто — купить...
✅ H1: Воск для авто

❌ Title: Автовоск — купить...     ← CHANGED KEYWORD!
❌ H1: Автомобильный воск          ← CHANGED KEYWORD!
```

**NOT allowed:**
- Change word order
- Add words ("авто" → "автомобильный")
- Merge words ("воск для авто" → "автовоск")
- "Improve" or "optimize" the keyword
- Use synonyms instead of primary_keyword

---

## Title Rules

| Rule | Value |
|------|-------|
| Length | 50-60 chars (unique part) |
| Structure | {primary_keyword} + commercial + brand |
| Commercial | "купить/купити" AFTER keyword |
| Brand | "Ultimate" at end |
| Forbidden | Colons (Google replaces with dash) |

---

## Description Rules

### Producer Pattern (has Ultimate products)

```
{primary_keyword} от производителя Ultimate. {Types} — {details}. Опт и розница.
```

### Shop Pattern (NO Ultimate products)

```
{primary_keyword} в интернет-магазине Ultimate. {Types} — {details}.
```

**Shop categories (no Ultimate products):**
- glina-i-avtoskraby
- gubki-i-varezhki
- cherniteli-shin
- raspyliteli-i-penniki
- vedra-i-emkosti
- kisti-dlya-deteylinga
- shchetka-dlya-moyki-avto
- polirovalnye-krugi
- polirovalnye-mashinki

---

## H1 Rules

**Formula:** `{primary_keyword}`

**Rules:**
- = primary_keyword VERBATIM
- NO "Купить/Купити"
- NO additions ("для авто" if not in keyword)

---

## Red Flags — STOP and fix

| Thought | Reality |
|---------|---------|
| "Sounds better this way" | primary_keyword = semantic data. Your opinion ≠ data. |
| "I'll add 'для авто' for clarity" | If not in primary_keyword — DON'T add! |
| "It's a synonym" | Synonym ≠ exact match. Google distinguishes. |
| "This way it's shorter/longer" | Length is adjusted by Title tail, NOT keyword. |

**All these thoughts = go back to `_clean.json` and take primary_keyword VERBATIM.**
```

**Step 2: Commit**

```bash
git add .claude/skills/shared/meta-rules.md
git commit -m "feat: add shared meta-rules.md for skills"
```

---

## Task 8: Обновить uk-quality-gate на ссылку shared/

**Files:**
- Modify: `.claude/skills/uk-quality-gate/skill.md`

**Step 1: Add reference to shared**

В начало файла после frontmatter добавить:

```markdown
## Common Rules

See [../shared/validation-checklist.md](../shared/validation-checklist.md) for common validation rules.

This document contains **UK-specific** additions only.
```

**Step 2: Remove duplicated content**

Удалить секции которые теперь в shared/:
- Data Validation (общая часть)
- Meta Validation (общая таблица)
- Content Validation (общие правила)
- Pass Criteria (общая таблица)

Оставить только UK-specific:
- UK Terminology Check (резина→гума)
- UK Meta Rules (Купити)
- UK-specific validation commands

**Step 3: Commit**

```bash
git add .claude/skills/uk-quality-gate/skill.md
git commit -m "refactor: uk-quality-gate references shared validation-checklist"
```

---

## Task 9: Обновить uk-generate-meta на ссылку shared/

**Files:**
- Modify: `.claude/skills/uk-generate-meta/skill.md`

**Step 1: Add reference to shared**

В начало файла после frontmatter добавить:

```markdown
## Common Rules

See [../shared/meta-rules.md](../shared/meta-rules.md) for IRON RULE and common meta patterns.

This document contains **UK-specific** formulas only.
```

**Step 2: Remove duplicated content**

Удалить секции которые теперь в shared/:
- IRON RULE (уже в shared)
- Red Flags (уже в shared)
- Producer/Shop pattern descriptions (оставить только UK формулы)

**Step 3: Commit**

```bash
git add .claude/skills/uk-generate-meta/skill.md
git commit -m "refactor: uk-generate-meta references shared meta-rules"
```

---

## Task 10: Тесты для audit_keyword_consistency.py

**Files:**
- Create: `tests/unit/test_audit_keyword_consistency.py`
- Reference: `scripts/audit_keyword_consistency.py`

**Step 1: Read the script first**

```bash
head -100 scripts/audit_keyword_consistency.py
```

**Step 2: Write tests based on API**

```python
"""Tests for audit_keyword_consistency.py"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Import after reading the actual module API
# from scripts.audit_keyword_consistency import check_consistency, ...


class TestAuditKeywordConsistency:
    """Test keyword consistency audit."""

    def test_placeholder(self):
        """Placeholder - implement after reading script API."""
        # TODO: Implement based on actual script functions
        pass
```

**Step 3: Run and iterate**

```bash
pytest tests/unit/test_audit_keyword_consistency.py -v
```

**Step 4: Commit**

```bash
git add tests/unit/test_audit_keyword_consistency.py
git commit -m "test: add unit tests for audit_keyword_consistency.py"
```

---

## Summary Checklist

### Task A: Tests (P0-P1)

- [ ] Task 1: Create fixtures
- [ ] Task 2: test_md_to_html.py
- [ ] Task 3: test_generate_sql.py
- [ ] Task 4: test_upload_to_db.py
- [ ] Task 5: test_validate_uk.py
- [ ] Task 10: test_audit_keyword_consistency.py

### Task B: Skills

- [ ] Task 6: shared/validation-checklist.md
- [ ] Task 7: shared/meta-rules.md
- [ ] Task 8: uk-quality-gate → reference shared
- [ ] Task 9: uk-generate-meta → reference shared

---

## Verification

After completing all tasks:

```bash
# Run all tests
pytest -v

# Check test count
pytest --collect-only | grep "test session starts" -A 5

# Verify shared files exist
ls -la .claude/skills/shared/

# Verify UK skills reference shared
grep -r "shared/" .claude/skills/uk-*/
```

---

**Version:** 1.0
**Created:** 2026-01-26
