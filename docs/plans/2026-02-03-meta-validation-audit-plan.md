# Meta Validation & Audit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Виправити пошук файлів в `validate_meta.py`, покрити тестами, провести аудит скіллів, пофіксити мета-дані для 53 RU + 54 UK категорій.

**Architecture:** Замінити glob на rglob для вкладених категорій, додати unit та E2E тести з pytest markers, синхронізувати скілли generate-meta.

**Tech Stack:** Python 3, pytest, pytest markers (@pytest.mark.e2e), subprocess.

---

## Milestone 1: Фікс пошуку файлів

### Task 1: Написати failing тест для find_all_meta_files

**Files:**
- Modify: `tests/unit/test_validate_meta.py`

**Step 1: Написати тест**

Додати в кінець файлу:

```python
class TestFindAllMetaFiles:
    """Test find_all_meta_files function."""

    def test_finds_nested_ru_categories(self, tmp_path):
        """Should find meta files in nested RU category structure."""
        from scripts.validate_meta import find_all_meta_files

        # Create nested structure: categories/parent/child/meta/child_meta.json
        parent = tmp_path / "categories" / "moyka-i-eksterer"
        parent.mkdir(parents=True)

        child = parent / "ochistiteli-diskov" / "meta"
        child.mkdir(parents=True)
        (child / "ochistiteli-diskov_meta.json").write_text('{"h1": "test"}')

        # Also create L1 category
        l1 = tmp_path / "categories" / "aktivnaya-pena" / "meta"
        l1.mkdir(parents=True)
        (l1 / "aktivnaya-pena_meta.json").write_text('{"h1": "test"}')

        files = find_all_meta_files(str(tmp_path))
        paths = [f[0] for f in files]

        assert len(paths) >= 2, f"Expected at least 2 files, got {len(paths)}"
        assert any("ochistiteli-diskov" in p for p in paths), "Nested category not found"
        assert any("aktivnaya-pena" in p for p in paths), "L1 category not found"

    def test_finds_uk_categories(self, tmp_path):
        """Should find meta files in uk/categories/."""
        from scripts.validate_meta import find_all_meta_files

        # Create UK structure
        uk = tmp_path / "uk" / "categories" / "antibitum" / "meta"
        uk.mkdir(parents=True)
        (uk / "antibitum_meta.json").write_text('{"h1": "test", "language": "uk"}')

        files = find_all_meta_files(str(tmp_path))
        paths = [f[0] for f in files]

        assert len(paths) == 1
        assert "antibitum" in paths[0]
```

**Step 2: Запустити тест, переконатись що FAIL**

```bash
pytest tests/unit/test_validate_meta.py::TestFindAllMetaFiles -v
```

Expected: FAIL — nested category not found.

---

### Task 2: Виправити find_all_meta_files

**Files:**
- Modify: `scripts/validate_meta.py:595-621`

**Step 1: Замінити glob на rglob**

Замінити функцію `find_all_meta_files`:

```python
def find_all_meta_files(base_path: str = ".") -> list[tuple[str, str | None]]:
    """
    Find all meta files and their corresponding keywords files.

    Uses rglob to find nested categories (L2, L3).

    Returns:
        List of (meta_path, keywords_path) tuples
    """
    base = Path(base_path)
    results = []

    # Search in categories/ (RU) - including nested
    categories_path = base / "categories"
    if categories_path.exists():
        for meta_file in categories_path.rglob("*_meta.json"):
            # Skip if not in meta/ folder
            if meta_file.parent.name != "meta":
                continue
            slug = meta_file.stem.replace("_meta", "")
            data_dir = meta_file.parent.parent / "data"
            keywords_file = data_dir / f"{slug}_clean.json"
            if not keywords_file.exists():
                keywords_file = data_dir / f"{slug}.json"
            results.append((str(meta_file), str(keywords_file) if keywords_file.exists() else None))

    # Search in uk/categories/ (UK) - including nested
    uk_categories_path = base / "uk" / "categories"
    if uk_categories_path.exists():
        for meta_file in uk_categories_path.rglob("*_meta.json"):
            # Skip if not in meta/ folder
            if meta_file.parent.name != "meta":
                continue
            slug = meta_file.stem.replace("_meta", "")
            data_dir = meta_file.parent.parent / "data"
            keywords_file = data_dir / f"{slug}_clean.json"
            if not keywords_file.exists():
                keywords_file = data_dir / f"{slug}.json"
            results.append((str(meta_file), str(keywords_file) if keywords_file.exists() else None))

    return results
```

**Step 2: Запустити тест, переконатись що PASS**

```bash
pytest tests/unit/test_validate_meta.py::TestFindAllMetaFiles -v
```

Expected: PASS

**Step 3: Коміт**

```bash
git add scripts/validate_meta.py tests/unit/test_validate_meta.py
git commit -m "fix(validate_meta): use rglob for nested categories

- find_all_meta_files now finds L2/L3 nested categories
- Added unit tests for nested RU and UK structure

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 3: Перевірити кількість знайдених категорій

**Step 1: Запустити підрахунок**

```bash
python3 -c "
from scripts.validate_meta import find_all_meta_files
files = find_all_meta_files()
ru = [f for f in files if '/uk/' not in f[0]]
uk = [f for f in files if '/uk/' in f[0]]
print(f'RU: {len(ru)} categories')
print(f'UK: {len(uk)} categories')
print(f'Total: {len(files)}')
"
```

Expected:
- RU: ~53 categories
- UK: ~54 categories

---

## Milestone 2: E2E тести

### Task 4: Створити E2E тест файл

**Files:**
- Create: `tests/e2e/__init__.py`
- Create: `tests/e2e/test_meta_validation.py`

**Step 1: Створити __init__.py**

```bash
mkdir -p tests/e2e
touch tests/e2e/__init__.py
```

**Step 2: Створити test_meta_validation.py**

```python
"""
E2E tests for meta validation on real data.

Run with: pytest -m e2e -v
Skip with: pytest -m "not e2e"
"""

import subprocess

import pytest


@pytest.mark.e2e
class TestMetaValidationE2E:
    """E2E tests that run on actual category data."""

    def test_validate_all_ru_finds_categories(self):
        """validate_meta.py --all --lang ru should find 50+ RU categories."""
        result = subprocess.run(
            ["python3", "scripts/validate_meta.py", "--all", "--lang", "ru"],
            capture_output=True,
            text=True,
        )
        # Check output contains summary
        assert "Total files:" in result.stdout
        # Extract count from "Total files: N"
        for line in result.stdout.split("\n"):
            if "Total files:" in line:
                count = int(line.split(":")[1].strip())
                assert count >= 50, f"Expected 50+ RU files, got {count}"
                break

    def test_validate_all_uk_finds_categories(self):
        """validate_meta.py --all --lang uk should find 50+ UK categories."""
        result = subprocess.run(
            ["python3", "scripts/validate_meta.py", "--all", "--lang", "uk"],
            capture_output=True,
            text=True,
        )
        assert "Total files:" in result.stdout
        for line in result.stdout.split("\n"):
            if "Total files:" in line:
                count = int(line.split(":")[1].strip())
                assert count >= 50, f"Expected 50+ UK files, got {count}"
                break

    def test_audit_h1_ru_runs(self):
        """audit_h1_primary.py --lang ru should run without errors."""
        result = subprocess.run(
            ["python3", "scripts/audit_h1_primary.py", "--lang", "ru"],
            capture_output=True,
            text=True,
        )
        # Should have summary output
        assert "Audit Results:" in result.stdout or "OK:" in result.stdout

    def test_audit_h1_uk_runs(self):
        """audit_h1_primary.py --lang uk should run without errors."""
        result = subprocess.run(
            ["python3", "scripts/audit_h1_primary.py", "--lang", "uk"],
            capture_output=True,
            text=True,
        )
        assert "Audit Results:" in result.stdout or "OK:" in result.stdout
```

**Step 3: Додати e2e marker в pytest.ini**

Перевірити чи існує `pytest.ini`, додати marker якщо потрібно:

```ini
[pytest]
markers =
    e2e: end-to-end tests on real data (deselect with '-m "not e2e"')
```

**Step 4: Запустити E2E тести**

```bash
pytest -m e2e -v
```

Expected: всі 4 тести PASS

**Step 5: Коміт**

```bash
git add tests/e2e/ pytest.ini
git commit -m "test(e2e): add meta validation E2E tests

- test_validate_all_ru_finds_categories
- test_validate_all_uk_finds_categories
- test_audit_h1_ru_runs
- test_audit_h1_uk_runs

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Milestone 3: Аудит скіллів generate-meta

### Task 5: Порівняти RU та UK скілли

**Files:**
- Read: `.claude/skills/generate-meta/SKILL.md`
- Read: `.claude/skills/uk-generate-meta/SKILL.md`

**Step 1: Перевірити checklist**

| Перевірка | RU | UK | Коментар |
|-----------|----|----|----------|
| Title формула | `{primary_keyword} — купить` | `{title_phrase} — купити` | UK використовує title_phrase! |
| H1 формула | `= {primary_keyword}` | `= {title_phrase}` | UK використовує title_phrase |
| category_title логіка | ✅ описано | ✅ описано | Обидва мають |
| title_phrase = category_title ?? primary_keyword | ❌ немає терміну | ✅ є | RU потребує оновлення |
| Версія | v16.1 | v16.1 | Синхронізовані |

**Step 2: Визначити потрібні зміни**

RU скілл потребує:
1. Додати термін `{title_phrase}` як в UK
2. Оновити формули Title/H1/Description на `{title_phrase}`
3. Оновити версію до v17.2

---

### Task 6: Оновити RU скілл generate-meta

**Files:**
- Modify: `.claude/skills/generate-meta/SKILL.md`

**Step 1: Додати секцію title_phrase**

Після секції "Що таке `{category_title}`" додати:

```markdown
### Що таке `{title_phrase}` (головний термін!)

**🚨 КРИТИЧНО:** `{title_phrase}` — це фраза для Title/H1/Description.

```
{title_phrase} = category_title ?? primary_keyword
```

**Логіка:**
1. Якщо в `_clean.json` є поле `category_title` → використовувати його
2. Інакше → використовувати `primary_keyword` (MAX volume)
```

**Step 2: Оновити формули**

Замінити `{primary_keyword}` на `{title_phrase}` в:
- Title формулі
- H1 формулі
- Description формулі
- Validation Checklist

**Step 3: Оновити версію**

```markdown
**Version:** 17.2 — February 2026

**Changelog v17.2:**
- 🔧 Введено `{title_phrase}` = category_title ?? primary_keyword
- 📋 Оновлено формули Title/H1/Description на {title_phrase}
- ✅ Синхронізовано з UK v17.2
```

**Step 4: Коміт**

```bash
git add .claude/skills/generate-meta/SKILL.md
git commit -m "docs(skills): update generate-meta with title_phrase v17.2

- Added {title_phrase} = category_title ?? primary_keyword
- Updated Title/H1/Description formulas
- Synced with uk-generate-meta v17.2

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

### Task 7: Оновити UK скілл uk-generate-meta

**Files:**
- Modify: `.claude/skills/uk-generate-meta/SKILL.md`

**Step 1: Оновити версію**

```markdown
**Version:** 17.2 — February 2026

**Changelog v17.2:**
- ✅ Синхронізовано з RU v17.2
```

**Step 2: Коміт**

```bash
git add .claude/skills/uk-generate-meta/SKILL.md
git commit -m "docs(skills): update uk-generate-meta v17.2

- Version bump to match RU skill

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Milestone 4: Запуск повного аудиту

### Task 8: Запустити валідацію та зберегти результати

**Step 1: Валідація RU**

```bash
python3 scripts/validate_meta.py --all --lang ru 2>&1 | tee /tmp/validate_ru.txt
```

**Step 2: Валідація UK**

```bash
python3 scripts/validate_meta.py --all --lang uk 2>&1 | tee /tmp/validate_uk.txt
```

**Step 3: H1 аудит RU**

```bash
python3 scripts/audit_h1_primary.py --lang ru 2>&1 | tee /tmp/audit_h1_ru.txt
```

**Step 4: H1 аудит UK**

```bash
python3 scripts/audit_h1_primary.py --lang uk 2>&1 | tee /tmp/audit_h1_uk.txt
```

**Step 5: Підсумок**

Перевірити:
- Скільки FAIL в кожному аудиті
- Які категорії потребують фіксу

---

### Task 9: Пофіксити мета-дані (якщо є FAIL)

**Для кожної категорії з FAIL:**

**Step 1: Прочитати _clean.json**

```bash
cat categories/{slug}/data/{slug}_clean.json | head -20
```

Визначити `title_phrase` = category_title ?? MAX(volume) keyword.

**Step 2: Прочитати поточну мета**

```bash
cat categories/{slug}/meta/{slug}_meta.json
```

**Step 3: Виправити мета по формулах скілла**

- Title: `{title_phrase} — купить, цены | Ultimate`
- H1: `{title_phrase}` (без "Купить")
- Description: `{title_phrase} от производителя Ultimate. ...`

**Step 4: Валідувати**

```bash
python3 scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json --keywords categories/{slug}/data/{slug}_clean.json
```

Expected: PASS

---

### Task 10: Фінальна перевірка та коміт

**Step 1: Запустити всі E2E тести**

```bash
pytest -m e2e -v
```

Expected: всі PASS

**Step 2: Запустити unit тести**

```bash
pytest tests/unit/test_validate_meta.py tests/unit/test_audit_h1_primary.py -v
```

Expected: всі PASS

**Step 3: Коміт виправлених мета**

```bash
git add categories/ uk/categories/
git commit -m "fix(meta): validate and fix meta tags for RU/UK categories

- Fixed H1/Title/Description alignment with title_phrase
- All categories pass validate_meta.py

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Verification Commands

```bash
# Unit tests
pytest tests/unit/test_validate_meta.py -v

# E2E tests
pytest -m e2e -v

# Full validation
python3 scripts/validate_meta.py --all --lang ru
python3 scripts/validate_meta.py --all --lang uk

# H1 audit
python3 scripts/audit_h1_primary.py --lang ru
python3 scripts/audit_h1_primary.py --lang uk
```

---

**Version:** 1.0 — February 2026
