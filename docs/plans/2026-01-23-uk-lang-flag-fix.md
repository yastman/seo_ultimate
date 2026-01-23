# UK --lang uk Flag Fix Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add missing `--lang uk` flags to all UK validation commands in skills and agents.

**Architecture:** Fix 3 files by adding `--lang uk` to validation script calls. Create automated test to prevent regression.

**Tech Stack:** Python (pytest), Markdown files, Bash commands

---

## Task 1: Create Automated Test

**Files:**
- Create: `tests/test_uk_lang_flag.py`

**Step 1: Write the test file**

```python
"""
Test that all UK skills/agents use --lang uk flag for validation scripts.

This test prevents regression - ensures UK files always use proper language flag.
"""
import pytest
from pathlib import Path
import re

# Scripts that MUST have --lang uk when used in UK context
SCRIPTS_REQUIRING_LANG_UK = [
    "check_keyword_density.py",
    "check_h1_sync.py",
    "check_semantic_coverage.py",
]

# Files that should use --lang uk
UK_FILES = [
    ".claude/agents/uk-content-generator.md",
    ".claude/agents/uk-content-reviewer.md",
    ".claude/agents/uk-quality-gate.md",
    ".claude/skills/uk-content-generator/skill.md",
    ".claude/skills/uk-quality-gate/skill.md",
    ".claude/skills/quality-gate/skill.md",  # Has UK section
]


@pytest.mark.parametrize("filepath", UK_FILES)
def test_uk_files_have_lang_flag(filepath):
    """Each UK file must use --lang uk for relevant scripts."""
    path = Path(filepath)
    if not path.exists():
        pytest.skip(f"File not found: {filepath}")

    content = path.read_text(encoding="utf-8")

    for script in SCRIPTS_REQUIRING_LANG_UK:
        # Find all usages of the script in bash code blocks or commands
        # Pattern matches: script_name followed by anything on same line
        pattern = rf"python3?\s+scripts/{script}\s+[^\n]+"
        matches = re.findall(pattern, content)

        for match in matches:
            # Check if --lang uk is present in the command
            assert "--lang uk" in match, (
                f"{filepath}: {script} missing --lang uk\n"
                f"Found: {match}"
            )


def test_no_orphan_uk_validation_without_lang():
    """Grep-style check: no UK path validation without --lang uk."""
    for filepath in UK_FILES:
        path = Path(filepath)
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8")

        # Find lines with uk/categories AND check_keyword_density but NO --lang uk
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if "uk/categories" in line and "check_keyword_density" in line:
                assert "--lang uk" in line, (
                    f"{filepath}:{i} has UK path but missing --lang uk:\n{line}"
                )
```

**Step 2: Run test to verify failures (baseline)**

Run: `pytest tests/test_uk_lang_flag.py -v`

Expected output (failures):
```
FAILED tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/agents/uk-content-generator.md]
FAILED tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/skills/quality-gate/skill.md]
```

**Step 3: Commit test**

```bash
git add tests/test_uk_lang_flag.py
git commit -m "test: add UK --lang uk flag regression test"
```

---

## Task 2: Fix uk-content-generator Agent

**Files:**
- Modify: `.claude/agents/uk-content-generator.md`

**Step 1: Read current file to find exact location**

The agent file is short (67 lines) and lacks validation commands entirely.

**Step 2: Add validation section before Output**

Find this section (~line 59-66):
```markdown
## Output

```
uk/categories/{slug}/content/{slug}_uk.md

Наступний крок: /uk-quality-gate {slug}
```
```

Insert BEFORE `## Output`:
```markdown
## Validation

```bash
# Keyword density with UK morphology
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

# SEO structure check
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary_uk}"

# Academic nausea check
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md
```

**Пороги:**
- Stem-група ≤2.5% (BLOCKER >3.0%)
- Класична тошнота ≤3.5 (BLOCKER >4.0)
- Академічна ≥7% (WARNING <7%)

```

**Step 3: Run test to verify this file passes**

Run: `pytest tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/agents/uk-content-generator.md] -v`

Expected: PASS

**Step 4: Commit**

```bash
git add .claude/agents/uk-content-generator.md
git commit -m "fix(agents): add --lang uk to uk-content-generator validation"
```

---

## Task 3: Fix uk-quality-gate Agent

**Files:**
- Modify: `.claude/agents/uk-quality-gate.md`

**Step 1: Find location for validation commands**

Current file has Workflow section but lacks validation script commands.
Insert after step 3 (Валідуй Meta) and before step 4 (Перевір UK термінологію).

**Step 2: Add validation commands**

Find (~line 31-32):
```markdown
   - H1: БЕЗ "Купити"

4. **Перевір UK термінологію (BLOCKER):**
```

Insert between them:
```markdown
   - H1: БЕЗ "Купити"

4. **Валідуй Content:**
   ```bash
   python3 scripts/validate_content.py uk/categories/{slug}/content/{slug}_uk.md "{primary_uk}" --mode seo
   python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
   python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary_uk}"
   python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md
   python3 scripts/check_h1_sync.py --lang uk
   python3 scripts/check_semantic_coverage.py --lang uk
   ```

5. **Перевір UK термінологію (BLOCKER):**
```

Also update step numbers (4→5, 5→6).

**Step 3: Run test**

Run: `pytest tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/agents/uk-quality-gate.md] -v`

Expected: PASS

**Step 4: Commit**

```bash
git add .claude/agents/uk-quality-gate.md
git commit -m "fix(agents): add --lang uk to uk-quality-gate validation"
```

---

## Task 4: Fix quality-gate Skill (UK Section)

**Files:**
- Modify: `.claude/skills/quality-gate/skill.md`

**Step 1: Find UK Validation Commands section**

Location: ~line 249

Current:
```bash
# Keyword density
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md
```

**Step 2: Add --lang uk flag**

Replace with:
```bash
# Keyword density
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

# H1 sync check
python3 scripts/check_h1_sync.py --lang uk

# Semantic coverage
python3 scripts/check_semantic_coverage.py --lang uk
```

**Step 3: Run test**

Run: `pytest tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/skills/quality-gate/skill.md] -v`

Expected: PASS

**Step 4: Commit**

```bash
git add .claude/skills/quality-gate/skill.md
git commit -m "fix(skills): add --lang uk to quality-gate UK section"
```

---

## Task 5: Run Full Test Suite

**Step 1: Run all UK lang flag tests**

Run: `pytest tests/test_uk_lang_flag.py -v`

Expected:
```
tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/agents/uk-content-generator.md] PASSED
tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/agents/uk-content-reviewer.md] PASSED
tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/agents/uk-quality-gate.md] PASSED
tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/skills/uk-content-generator/skill.md] PASSED
tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/skills/uk-quality-gate/skill.md] PASSED
tests/test_uk_lang_flag.py::test_uk_files_have_lang_flag[.claude/skills/quality-gate/skill.md] PASSED
tests/test_uk_lang_flag.py::test_no_orphan_uk_validation_without_lang PASSED

7 passed
```

**Step 2: Grep verification**

Run:
```bash
grep -r "check_keyword_density.py" .claude/ | grep "uk" | grep -v "\-\-lang uk"
```

Expected: No output (empty)

**Step 3: Integration test**

Run: `/uk-quality-gate aktivnaya-pena`

Expected: Executes without errors, validation scripts use UK morphology.

---

## Task 6: Final Commit

**Step 1: Verify all changes**

Run: `git status`

Expected: Only the 4 files modified/created.

**Step 2: Final commit (if not already committed per-task)**

```bash
git add -A
git commit -m "fix: ensure all UK skills/agents use --lang uk for validation

- Add validation section to uk-content-generator agent
- Add validation commands to uk-quality-gate agent
- Add --lang uk to quality-gate skill UK section
- Add regression test to prevent future issues

Closes: UK validation consistency"
```

---

## Success Criteria

| Check | Expected |
|-------|----------|
| `pytest tests/test_uk_lang_flag.py` | 7 passed |
| Grep for missing `--lang uk` | 0 results |
| `/uk-quality-gate aktivnaya-pena` | PASS |

---

## Rollback

If issues found:
```bash
git revert HEAD~3  # Revert last 3 commits (or adjust as needed)
```

Test file remains for future reference.

---

**Version:** 1.0
**Created:** 2026-01-23
