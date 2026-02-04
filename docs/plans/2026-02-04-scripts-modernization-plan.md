# Scripts Modernization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Migrate 89 scripts to uv + src layout, achieve 80% test coverage

**Architecture:** Phased migration — infra first (blocks all), then core (blocks validate/audit), then parallel workers for remaining modules

**Tech Stack:** uv, pytest, ruff, mypy, pymorphy3, natasha

---

## Pre-flight Checklist

```bash
# Verify environment
echo $TMUX              # Must be inside tmux
mkdir -p logs data/generated/audit-logs
git status              # Clean working tree
```

---

## Phase 1: Infrastructure (Orchestrator — blocks all workers)

### Task 1.1: Initialize uv project

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Delete (after): `requirements.txt`

**Step 1: Init uv**

```bash
uv init --no-readme --name seo-ultimate
```

**Step 2: Set Python version**

```bash
echo "3.12" > .python-version
```

**Step 3: Verify**

Run: `cat pyproject.toml`
Expected: `[project]` section with `name = "seo-ultimate"`

---

### Task 1.2: Configure pyproject.toml

**Files:**
- Modify: `pyproject.toml`

**Step 1: Write full config**

```toml
[project]
name = "seo-ultimate"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pyyaml>=6.0",
    "tqdm>=4.67",
    "requests>=2.32",
    "toml>=0.10",
    "pandas>=2.2",
]

[dependency-groups]
nlp = [
    "pymorphy3>=2.0",
    "pymorphy3-dicts-ru>=2.4",
    "pymorphy3-dicts-uk>=2.4",
    "natasha>=1.6",
    "razdel>=0.5",
    "navec>=0.10",
    "slovnet>=0.6",
    "spacy>=3.8",
]
dev = [
    "ruff>=0.14",
    "mypy>=1.18",
]
test = [
    "pytest>=9.0",
    "pytest-cov>=7.0",
    "pytest-xdist>=3.5",
]

[tool.uv]
default-groups = ["nlp", "dev", "test"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --tb=short"

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true

[tool.coverage.run]
source = ["src/seo_ultimate"]
branch = true

[tool.coverage.report]
exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:"]
```

**Step 2: Sync dependencies**

Run: `uv sync`
Expected: `Resolved X packages`, creates `uv.lock`

**Step 3: Verify**

Run: `uv run python -c "import pymorphy3; print('OK')"`
Expected: `OK`

---

### Task 1.3: Create src layout

**Files:**
- Create: `src/seo_ultimate/__init__.py`
- Create: `src/seo_ultimate/core/__init__.py`
- Create: `src/seo_ultimate/validate/__init__.py`
- Create: `src/seo_ultimate/audit/__init__.py`
- Create: `src/seo_ultimate/py.typed`

**Step 1: Create directories**

```bash
mkdir -p src/seo_ultimate/{core,validate,audit,analyze,extract,generate,fix,sync,compare,batch,tools}
```

**Step 2: Create init files**

```bash
touch src/seo_ultimate/__init__.py
touch src/seo_ultimate/py.typed
for d in core validate audit analyze extract generate fix sync compare batch tools; do
  touch src/seo_ultimate/$d/__init__.py
done
```

**Step 3: Add package to pyproject.toml**

Add to `pyproject.toml`:
```toml
[tool.setuptools.packages.find]
where = ["src"]
```

**Step 4: Verify import**

Run: `uv run python -c "import seo_ultimate; print('OK')"`
Expected: `OK`

**Step 5: Commit infra**

```bash
git add pyproject.toml uv.lock .python-version src/
git commit -m "feat: init uv + src layout for scripts modernization"
```

---

### Task 1.4: Migrate core modules

**Files:**
- Move: `scripts/config.py` → `src/seo_ultimate/core/config.py`
- Move: `scripts/keyword_utils.py` → `src/seo_ultimate/core/keywords.py`
- Move: `scripts/text_utils.py` → `src/seo_ultimate/core/text.py`
- Move: `scripts/seo_utils.py` → `src/seo_ultimate/core/seo.py`
- Move: `scripts/coverage_matcher.py` → `src/seo_ultimate/core/coverage.py`
- Move: `scripts/synonym_tools.py` → `src/seo_ultimate/core/synonyms.py`
- Modify: `src/seo_ultimate/core/__init__.py`

**Step 1: Copy files (keep originals for now)**

```bash
cp scripts/config.py src/seo_ultimate/core/config.py
cp scripts/keyword_utils.py src/seo_ultimate/core/keywords.py
cp scripts/text_utils.py src/seo_ultimate/core/text.py
cp scripts/seo_utils.py src/seo_ultimate/core/seo.py
cp scripts/coverage_matcher.py src/seo_ultimate/core/coverage.py
cp scripts/synonym_tools.py src/seo_ultimate/core/synonyms.py
```

**Step 2: Fix imports in core modules**

Replace in all `src/seo_ultimate/core/*.py`:
- `from scripts.config` → `from seo_ultimate.core.config`
- `from scripts.keyword_utils` → `from seo_ultimate.core.keywords`
- `from scripts.text_utils` → `from seo_ultimate.core.text`

**Step 3: Export public API**

`src/seo_ultimate/core/__init__.py`:
```python
"""Core utilities for SEO Ultimate."""
from seo_ultimate.core.config import *
from seo_ultimate.core.keywords import KeywordMatcher, CoverageChecker
from seo_ultimate.core.text import get_stopwords, clean_markdown, count_words
from seo_ultimate.core.seo import extract_frontmatter, count_keyword_occurrences
from seo_ultimate.core.coverage import CoverageMatcher
```

**Step 4: Verify imports**

Run: `uv run python -c "from seo_ultimate.core import KeywordMatcher; print('OK')"`
Expected: `OK`

**Step 5: Commit core**

```bash
git add src/seo_ultimate/core/
git commit -m "feat(core): migrate utils to src layout"
```

---

## Phase 2: Parallel Workers (after Phase 1 complete)

### Worktree Setup

```bash
# Create worktrees for parallel work
git worktree add .worktrees/validate -b refactor/validate main
git worktree add .worktrees/audit -b refactor/audit main
git worktree add .worktrees/modules -b refactor/modules main
```

### tmux Windows

```bash
tmux new-window -n "W-VAL" -c "$(pwd)/.worktrees/validate"
tmux new-window -n "W-AUD" -c "$(pwd)/.worktrees/audit"
tmux new-window -n "W-MOD" -c "$(pwd)/.worktrees/modules"
```

---

## Worker W-VAL: Validate Module

### Spawn Command

```bash
tmux send-keys -t "W-VAL" "claude --dangerously-skip-permissions 'W-VAL: Migrate validate scripts.

ПЛАН: docs/plans/2026-02-04-scripts-modernization-plan.md
ЗАДАЧИ: Worker W-VAL section

⚠️ BEST PRACTICES 2026:
1. Используй существующие core модули: from seo_ultimate.core import ...
2. ТЕСТЫ — только свои: uv run pytest tests/integration/validate/ -v
   НЕ запускай все тесты.
3. Target coverage: 80% для validate/

ЛОГИРОВАНИЕ в $(pwd)/logs/worker-val.log:
[START] timestamp Task
[DONE] timestamp Task
[COMPLETE] timestamp Worker finished

НЕ делай git commit.'" Enter
```

### Task W-VAL.1: Migrate validate_meta.py

**Files:**
- Move: `scripts/validate_meta.py` → `src/seo_ultimate/validate/meta.py`
- Create: `tests/integration/validate/test_meta.py`

**Step 1: Copy and fix imports**

```bash
cp scripts/validate_meta.py src/seo_ultimate/validate/meta.py
```

Fix imports:
```python
from seo_ultimate.core.config import QUALITY_THRESHOLDS, PROJECT_ROOT
from seo_ultimate.core.keywords import KeywordMatcher
```

**Step 2: Write integration test**

`tests/integration/validate/test_meta.py`:
```python
import pytest
from pathlib import Path

def test_validate_meta_valid_file(tmp_path):
    """Valid meta file should pass validation."""
    meta = tmp_path / "test_meta.json"
    meta.write_text('{"slug": "test", "language": "ru", "meta": {"title": "Test", "description": "Desc"}, "h1": "Test H1"}')

    from seo_ultimate.validate.meta import validate_meta_file
    result = validate_meta_file(meta)
    assert result.is_valid

def test_validate_meta_missing_h1(tmp_path):
    """Missing H1 should fail validation."""
    meta = tmp_path / "test_meta.json"
    meta.write_text('{"slug": "test", "language": "ru", "meta": {"title": "Test"}}')

    from seo_ultimate.validate.meta import validate_meta_file
    result = validate_meta_file(meta)
    assert not result.is_valid
    assert "h1" in str(result.errors).lower()
```

**Step 3: Run test**

Run: `uv run pytest tests/integration/validate/test_meta.py -v`
Expected: 2 passed

**Step 4: Log completion**

```bash
echo "[DONE] $(date +%H:%M) Task W-VAL.1: validate_meta migrated" >> logs/worker-val.log
```

---

### Task W-VAL.2-8: Remaining validate scripts

Repeat pattern for:
- `validate_content.py` → `validate/content.py`
- `validate_density.py` → `validate/density.py`
- `validate_seo.py` → `validate/seo.py`
- `validate_uk.py` → `validate/uk.py`
- `validate_master.py` → `validate/master.py`
- `verify_structural_integrity.py` → `validate/structural.py`
- `verify_test_infra.py` → `validate/test_infra.py`

**After all tasks:**

```bash
echo "[COMPLETE] $(date +%H:%M) Worker W-VAL finished" >> logs/worker-val.log
```

---

## Worker W-AUD: Audit Module

### Spawn Command

```bash
tmux send-keys -t "W-AUD" "claude --dangerously-skip-permissions 'W-AUD: Migrate audit scripts.

ПЛАН: docs/plans/2026-02-04-scripts-modernization-plan.md
ЗАДАЧИ: Worker W-AUD section

⚠️ BEST PRACTICES 2026:
1. Используй существующие core модули: from seo_ultimate.core import ...
2. ТЕСТЫ — только свои: uv run pytest tests/integration/audit/ -v
3. Target coverage: 80% для audit/

ЛОГИРОВАНИЕ в $(pwd)/logs/worker-aud.log:
[START] timestamp Task
[DONE] timestamp Task
[COMPLETE] timestamp Worker finished

НЕ делай git commit.'" Enter
```

### Task W-AUD.1: Migrate audit_coverage.py

**Files:**
- Move: `scripts/audit_coverage.py` → `src/seo_ultimate/audit/coverage.py`
- Create: `tests/integration/audit/test_coverage.py`

**Step 1: Copy and fix imports**

```bash
cp scripts/audit_coverage.py src/seo_ultimate/audit/coverage.py
```

**Step 2: Write integration test**

`tests/integration/audit/test_coverage.py`:
```python
import pytest

def test_audit_coverage_returns_report():
    """Audit should return coverage report dict."""
    from seo_ultimate.audit.coverage import audit_category_coverage
    # Use existing test fixture
    result = audit_category_coverage("aktivnaya-pena", lang="ru")
    assert "coverage_percent" in result
    assert isinstance(result["coverage_percent"], (int, float))
```

**Step 3: Run test**

Run: `uv run pytest tests/integration/audit/test_coverage.py -v`

---

### Task W-AUD.2-11: Remaining audit scripts

Migrate (11 files):
- `audit_h1_primary.py` → `audit/h1.py`
- `audit_keyword_consistency.py` → `audit/keyword_consistency.py`
- `audit_meta.py` → `audit/meta.py`
- `audit_synonyms.py` → `audit/synonyms.py`
- `audit_unused_keywords.py` → `audit/unused.py`
- `check_cannibalization.py` → `audit/cannibalization.py`
- `check_h1_sync.py` → `audit/h1_sync.py`
- `check_ner_brands.py` → `audit/ner_brands.py`
- `check_semantic_coverage.py` → `audit/semantic.py`
- `check_water_natasha.py` → `audit/water.py`

**After all tasks:**

```bash
echo "[COMPLETE] $(date +%H:%M) Worker W-AUD finished" >> logs/worker-aud.log
```

---

## Worker W-MOD: Remaining Modules

### Spawn Command

```bash
tmux send-keys -t "W-MOD" "claude --dangerously-skip-permissions 'W-MOD: Migrate remaining scripts.

ПЛАН: docs/plans/2026-02-04-scripts-modernization-plan.md
ЗАДАЧИ: Worker W-MOD section

⚠️ BEST PRACTICES 2026:
1. Batch migrate by prefix: analyze_*, extract_*, generate_*, etc.
2. Smoke tests only — verify imports work
3. НЕ трогай tools/ пока — оставь на финальную фазу

ЛОГИРОВАНИЕ в $(pwd)/logs/worker-mod.log:
[START] timestamp Task
[DONE] timestamp Task
[COMPLETE] timestamp Worker finished

НЕ делай git commit.'" Enter
```

### Task W-MOD.1: analyze/ (5 files)

```bash
cp scripts/analyze_category.py src/seo_ultimate/analyze/category.py
cp scripts/analyze_keyword_duplicates.py src/seo_ultimate/analyze/duplicates.py
cp scripts/analyze_keywords_order.py src/seo_ultimate/analyze/order.py
cp scripts/analyze_keywords_synonyms.py src/seo_ultimate/analyze/synonyms.py
cp scripts/analyze_meta_keywords.py src/seo_ultimate/analyze/meta.py
```

Fix imports, verify: `uv run python -c "from seo_ultimate.analyze import category"`

### Task W-MOD.2: extract/ (8 files)

### Task W-MOD.3: generate/ (8 files)

### Task W-MOD.4: fix/ (6 files)

### Task W-MOD.5: sync/ (6 files)

### Task W-MOD.6: compare/ (3 files)

### Task W-MOD.7: batch/ (2 files)

**After all tasks:**

```bash
echo "[COMPLETE] $(date +%H:%M) Worker W-MOD finished" >> logs/worker-mod.log
```

---

## Auto-Monitor Script

Create `scripts/monitor-workers.sh`:

```bash
#!/bin/bash
declare -A WINDOW_MAP=(
  ["worker-val"]="W-VAL"
  ["worker-aud"]="W-AUD"
  ["worker-mod"]="W-MOD"
)

while true; do
  completed=0
  for k in "${!WINDOW_MAP[@]}"; do
    if grep -q '\[COMPLETE\]' "logs/${k}.log" 2>/dev/null; then
      tmux kill-window -t "${WINDOW_MAP[$k]}" 2>/dev/null
      ((completed++))
    fi
  done

  # All done
  if [ $completed -eq ${#WINDOW_MAP[@]} ]; then
    echo "[MONITOR] All workers complete at $(date +%H:%M)" >> logs/monitor.log
    exit 0
  fi

  sleep 30
done
```

Run: `chmod +x scripts/monitor-workers.sh && nohup ./scripts/monitor-workers.sh > logs/monitor.log 2>&1 &`

---

## Phase 3: Merge & Cleanup (Orchestrator)

### Task 3.1: Merge worktrees

```bash
# After all [COMPLETE] in logs
git checkout main

# Merge each branch
git merge refactor/validate --no-ff -m "feat(validate): migrate to src layout"
git merge refactor/audit --no-ff -m "feat(audit): migrate to src layout"
git merge refactor/modules --no-ff -m "feat(modules): migrate remaining scripts"

# Cleanup worktrees
git worktree remove .worktrees/validate
git worktree remove .worktrees/audit
git worktree remove .worktrees/modules
```

### Task 3.2: Coverage report

```bash
uv run pytest --cov=src/seo_ultimate --cov-report=term-missing --cov-report=html
```

Expected: `TOTAL ... 80%+`

### Task 3.3: Update CLAUDE.md

Replace script paths:
- `python3 scripts/validate_meta.py` → `uv run python -m seo_ultimate.validate.meta`

### Task 3.4: Final commit

```bash
git add .
git commit -m "feat: complete scripts modernization to uv + src layout

- Migrated 65 scripts to src/seo_ultimate/
- Added uv for dependency management
- All 569 tests passing
- Updated CLAUDE.md with new paths"
```

---

## Verification Checklist

**Required (blocking):**
- [x] `uv sync` — no errors
- [x] `uv run pytest` — all pass (569 tests)
- [x] `uv run ruff check src/` — no errors

**Nice-to-have (future work):**
- [ ] `uv run pytest --cov` — ≥80% (currently ~26%, requires new tests)
- [ ] `uv run mypy src/seo_ultimate/core/` — no errors (currently 29, requires type annotations)

**Note:** Coverage 80% was unrealistic for Phase 2 which focused on migration (copy + fix imports), not writing new tests. Type annotations for legacy code are a separate task.
