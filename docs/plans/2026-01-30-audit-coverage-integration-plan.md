# audit_coverage.py Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add `--include-meta` flag to audit_coverage.py and integrate it into 6 validation skills.

**Architecture:** Extend audit_coverage.py to load `keywords_in_content` from _meta.json, audit both sources, return combined JSON. Update skills to call the script and format output.

**Tech Stack:** Python 3, pytest, existing MorphAnalyzer

---

## Task 1: Add --include-meta Flag Tests

**Files:**
- Modify: `tests/unit/test_coverage_matcher.py`

**Step 1: Write failing tests for load_meta_keywords**

```python
class TestLoadMetaKeywords:
    """Tests for loading keywords_in_content from _meta.json."""

    def test_load_meta_keywords_returns_grouped_dict(self, tmp_path):
        """load_meta_keywords should return {primary: [], secondary: [], supporting: []}."""
        slug = "test-cat"
        meta_dir = tmp_path / "uk" / "categories" / slug / "meta"
        meta_dir.mkdir(parents=True)
        meta_file = meta_dir / f"{slug}_meta.json"
        meta_file.write_text(json.dumps({
            "keywords_in_content": {
                "primary": ["активна піна"],
                "secondary": ["піна для мийки", "безконтактна піна"],
                "supporting": ["автошампунь"]
            }
        }))

        import scripts.audit_coverage as module
        original_root = module.PROJECT_ROOT
        module.PROJECT_ROOT = tmp_path
        try:
            from scripts.audit_coverage import load_meta_keywords
            result = load_meta_keywords(slug, "uk")
            assert result is not None
            assert "primary" in result
            assert "secondary" in result
            assert "supporting" in result
            assert result["primary"] == ["активна піна"]
        finally:
            module.PROJECT_ROOT = original_root

    def test_load_meta_keywords_missing_file_returns_none(self, tmp_path):
        """Missing _meta.json should return None."""
        import scripts.audit_coverage as module
        original_root = module.PROJECT_ROOT
        module.PROJECT_ROOT = tmp_path
        try:
            from scripts.audit_coverage import load_meta_keywords
            result = load_meta_keywords("nonexistent", "uk")
            assert result is None
        finally:
            module.PROJECT_ROOT = original_root

    def test_load_meta_keywords_no_keywords_in_content_returns_empty(self, tmp_path):
        """_meta.json without keywords_in_content returns empty groups."""
        slug = "test-cat"
        meta_dir = tmp_path / "uk" / "categories" / slug / "meta"
        meta_dir.mkdir(parents=True)
        (meta_dir / f"{slug}_meta.json").write_text('{"h1": "Test"}')

        import scripts.audit_coverage as module
        original_root = module.PROJECT_ROOT
        module.PROJECT_ROOT = tmp_path
        try:
            from scripts.audit_coverage import load_meta_keywords
            result = load_meta_keywords(slug, "uk")
            assert result == {"primary": [], "secondary": [], "supporting": []}
        finally:
            module.PROJECT_ROOT = original_root
```

Add import at top of test file:
```python
import json
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_coverage_matcher.py::TestLoadMetaKeywords -v`
Expected: FAIL with "cannot import name 'load_meta_keywords'"

**Step 3: Commit test**

```bash
git add tests/unit/test_coverage_matcher.py
git commit -m "test: add tests for load_meta_keywords function"
```

---

## Task 2: Implement load_meta_keywords

**Files:**
- Modify: `scripts/audit_coverage.py`

**Step 1: Add load_meta_keywords function**

After `load_category_data` function (line ~77), add:

```python
def load_meta_keywords(slug: str, lang: str) -> dict[str, list[str]] | None:
    """
    Load keywords_in_content from _meta.json.

    Returns:
        {"primary": [...], "secondary": [...], "supporting": [...]}
        or None if file not found.
    """
    base = find_category_path(slug, lang)
    if base is None:
        return None

    meta_file = base / "meta" / f"{slug}_meta.json"
    if not meta_file.exists():
        return None

    with open(meta_file, encoding="utf-8") as f:
        data = json.load(f)

    kic = data.get("keywords_in_content", {})
    return {
        "primary": kic.get("primary", []),
        "secondary": kic.get("secondary", []),
        "supporting": kic.get("supporting", []),
    }
```

**Step 2: Run tests to verify they pass**

Run: `pytest tests/unit/test_coverage_matcher.py::TestLoadMetaKeywords -v`
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/audit_coverage.py
git commit -m "feat: add load_meta_keywords function"
```

---

## Task 3: Add Tests for audit_with_meta

**Files:**
- Modify: `tests/unit/test_coverage_matcher.py`

**Step 1: Write failing tests**

```python
class TestAuditWithMeta:
    """Tests for --include-meta functionality."""

    def test_audit_with_meta_returns_both_sections(self, tmp_path):
        """audit_with_meta should return keywords_in_content and keywords sections."""
        from scripts.audit_coverage import audit_with_meta
        from scripts.coverage_matcher import PreparedText

        keywords = [{"keyword": "активна піна", "volume": 100}]
        synonyms = []
        meta_keywords = {
            "primary": ["активна піна"],
            "secondary": [],
            "supporting": [],
        }
        text = "Купуйте активна піна"

        result = audit_with_meta(keywords, synonyms, meta_keywords, text, "uk")

        assert "keywords_in_content" in result
        assert "keywords" in result
        assert "primary" in result["keywords_in_content"]
        assert result["keywords_in_content"]["primary"]["total"] == 1
        assert result["keywords_in_content"]["primary"]["covered"] == 1

    def test_audit_with_meta_groups_coverage_correctly(self, tmp_path):
        """Each group (primary/secondary/supporting) should have own coverage stats."""
        from scripts.audit_coverage import audit_with_meta

        keywords = [
            {"keyword": "ключ1", "volume": 100},
            {"keyword": "ключ2", "volume": 90},
            {"keyword": "ключ3", "volume": 80},
        ]
        meta_keywords = {
            "primary": ["ключ1"],
            "secondary": ["ключ2"],
            "supporting": ["ключ3", "ключ4"],  # ключ4 not in text
        }
        text = "Текст з ключ1 та ключ2 та ключ3"

        result = audit_with_meta(keywords, [], meta_keywords, text, "uk")

        assert result["keywords_in_content"]["primary"]["coverage_percent"] == 100.0
        assert result["keywords_in_content"]["secondary"]["coverage_percent"] == 100.0
        assert result["keywords_in_content"]["supporting"]["coverage_percent"] == 50.0

    def test_audit_with_meta_handles_empty_meta(self):
        """Empty meta_keywords should return empty groups."""
        from scripts.audit_coverage import audit_with_meta

        result = audit_with_meta(
            [{"keyword": "test", "volume": 10}],
            [],
            {"primary": [], "secondary": [], "supporting": []},
            "test text",
            "uk",
        )

        assert result["keywords_in_content"]["primary"]["total"] == 0
        assert result["keywords_in_content"]["secondary"]["total"] == 0
        assert result["keywords_in_content"]["supporting"]["total"] == 0
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/unit/test_coverage_matcher.py::TestAuditWithMeta -v`
Expected: FAIL with "cannot import name 'audit_with_meta'"

**Step 3: Commit**

```bash
git add tests/unit/test_coverage_matcher.py
git commit -m "test: add tests for audit_with_meta function"
```

---

## Task 4: Implement audit_with_meta

**Files:**
- Modify: `scripts/audit_coverage.py`

**Step 1: Add audit_with_meta function**

After `load_meta_keywords` function, add:

```python
def audit_with_meta(
    keywords: list[dict],
    synonyms: list[dict],
    meta_keywords: dict[str, list[str]],
    text: str,
    lang: str,
) -> dict:
    """
    Audit both keywords[] and keywords_in_content.

    Args:
        keywords: List from _clean.json
        synonyms: List from _clean.json
        meta_keywords: Dict with primary/secondary/supporting lists
        text: Content text
        lang: Language code

    Returns:
        {
            "keywords_in_content": {
                "primary": {"total": N, "covered": M, "coverage_percent": X, "results": [...]},
                "secondary": {...},
                "supporting": {...}
            },
            "keywords": {"total": N, "covered": M, "coverage_percent": X, "results": [...]}
        }
    """
    from coverage_matcher import PreparedText, check_keyword

    prepared = PreparedText(text, lang)

    # Build volume lookup from keywords[]
    volume_map = {kw["keyword"]: kw.get("volume", 0) for kw in keywords}

    # Audit keywords_in_content groups
    kic_results = {}
    for group in ["primary", "secondary", "supporting"]:
        group_keywords = meta_keywords.get(group, [])
        results = []
        for kw in group_keywords:
            match = check_keyword(kw, prepared, synonyms)
            results.append({
                "keyword": kw,
                "volume": volume_map.get(kw, 0),
                "status": match.status,
                "covered": match.covered,
                "covered_by": match.covered_by,
                "syn_match_method": match.syn_match_method,
                "lemma_coverage": match.lemma_coverage,
                "reason": match.reason,
            })

        total = len(group_keywords)
        covered = sum(1 for r in results if r["covered"])
        kic_results[group] = {
            "total": total,
            "covered": covered,
            "coverage_percent": round(covered / total * 100, 1) if total > 0 else 100.0,
            "results": results,
        }

    # Audit full keywords[]
    keywords_result = audit_category(keywords, synonyms, text, lang)

    return {
        "keywords_in_content": kic_results,
        "keywords": keywords_result,
    }
```

**Step 2: Run tests to verify they pass**

Run: `pytest tests/unit/test_coverage_matcher.py::TestAuditWithMeta -v`
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/audit_coverage.py
git commit -m "feat: add audit_with_meta function"
```

---

## Task 5: Add --include-meta CLI Flag

**Files:**
- Modify: `scripts/audit_coverage.py`

**Step 1: Add argparse flag**

In `main()` function, after line `parser.add_argument("--json", ...)` add:

```python
    parser.add_argument("--include-meta", action="store_true",
                        help="Include keywords_in_content from _meta.json")
```

**Step 2: Update single-category mode to use --include-meta**

Replace the single category JSON output block (lines ~248-254) with:

```python
            if args.json:
                if args.include_meta:
                    meta_kw = load_meta_keywords(args.slug, lang)
                    if meta_kw is None:
                        meta_kw = {"primary": [], "secondary": [], "supporting": []}
                    result = audit_with_meta(keywords, synonyms, meta_kw, content, lang)
                    result["slug"] = args.slug
                    result["lang"] = lang
                print(json.dumps(result, ensure_ascii=False, indent=2))
```

**Step 3: Test manually**

Run: `python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --json --include-meta`
Expected: JSON with both `keywords_in_content` and `keywords` sections

**Step 4: Commit**

```bash
git add scripts/audit_coverage.py
git commit -m "feat: add --include-meta CLI flag"
```

---

## Task 6: Update content-reviewer Skill

**Files:**
- Modify: `.claude/skills/content-reviewer/SKILL.md`

**Step 1: Replace Step 3 content**

Find the section "### Step 3: Keywords Coverage (100% required)" and replace it with:

```markdown
### Step 3: Keywords Coverage (audit_coverage.py)

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang ru --json --include-meta
```

**Verdict Rules:**

| Source | Group | Requirement | On Fail |
|--------|-------|-------------|---------|
| keywords_in_content | primary | 100% COVERED | BLOCKER |
| keywords_in_content | secondary | 100% COVERED | BLOCKER |
| keywords_in_content | supporting | ≥80% COVERED | WARNING |
| keywords[] | all | adaptive threshold | WARNING |

Adaptive thresholds: ≤5 keywords → 70%, 6-15 → 60%, >15 → 50%

**Output Format (compact):**

```markdown
### Keywords Coverage

| Source | Covered | Total | % | Status |
|--------|---------|-------|---|--------|
| primary+secondary | 8/8 | 100% | ✅ PASS |
| supporting | 4/5 | 80% | ✅ PASS |
| keywords[] | 8/15 | 53% | ⚠️ WARNING (threshold 50%) |

**NOT COVERED (primary/secondary):** none
**NOT COVERED (keywords[]):** ключ1 (1200), ключ2 (800)
```

**Details (only if BLOCKER or WARNING):**

| Keyword | Volume | Status | Note |
|---------|--------|--------|------|
| pH-нейтральный | 800 | TOKENIZATION | special tokens |
| пена для бесконтактной | 600 | PARTIAL | 67% lemmas |
| купить активную пену | 400 | SYNONYM | ← "активная пена" [LEMMA] |
```

**Step 2: Commit**

```bash
git add .claude/skills/content-reviewer/SKILL.md
git commit -m "feat(skill): integrate audit_coverage.py into content-reviewer"
```

---

## Task 7: Update uk-content-reviewer Skill

**Files:**
- Modify: `.claude/skills/uk-content-reviewer/SKILL.md`

**Step 1: Replace Step 3 content**

Find "### Step 3: Keywords Coverage (100% required)" and replace with:

```markdown
### Step 3: Keywords Coverage (audit_coverage.py)

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang uk --json --include-meta
```

**Verdict Rules:**

| Source | Group | Requirement | On Fail |
|--------|-------|-------------|---------|
| keywords_in_content | primary | 100% COVERED | BLOCKER |
| keywords_in_content | secondary | 100% COVERED | BLOCKER |
| keywords_in_content | supporting | ≥80% COVERED | WARNING |
| keywords[] | all | adaptive threshold | WARNING |

Adaptive thresholds: ≤5 keywords → 70%, 6-15 → 60%, >15 → 50%

**Output Format (compact):**

```markdown
### Keywords Coverage

| Source | Covered | Total | % | Status |
|--------|---------|-------|---|--------|
| primary+secondary | 8/8 | 100% | ✅ PASS |
| supporting | 4/5 | 80% | ✅ PASS |
| keywords[] | 8/15 | 53% | ⚠️ WARNING (threshold 50%) |

**NOT COVERED (primary/secondary):** немає
**NOT COVERED (keywords[]):** ключ1 (1200), ключ2 (800)
```

**Details (only if BLOCKER or WARNING):**

| Keyword | Volume | Status | Note |
|---------|--------|--------|------|
| pH-нейтральний | 800 | TOKENIZATION | special tokens |
| піна для безконтактної | 600 | PARTIAL | 67% lemmas |
| купити активну піну | 400 | SYNONYM | ← "активна піна" [LEMMA] |
```

**Step 2: Commit**

```bash
git add .claude/skills/uk-content-reviewer/SKILL.md
git commit -m "feat(skill): integrate audit_coverage.py into uk-content-reviewer"
```

---

## Task 8: Update quality-gate Skill

**Files:**
- Modify: `.claude/skills/quality-gate/skill.md`

**Step 1: Add Keywords Coverage section**

After "### 3. Content Validation" section, before "### 4. SEO Structure Check", add:

```markdown
### 3b. Keywords Coverage (audit_coverage.py)

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang ru --json --include-meta
```

**Checks:**

- [ ] primary+secondary: 100% COVERED (BLOCKER)
- [ ] supporting: ≥80% COVERED (WARNING)
- [ ] keywords[]: above adaptive threshold (WARNING)

**Include in report:**

| Keywords (primary+secondary) | ✅/❌ | 8/8 (100%) |
| Keywords (supporting) | ✅/⚠️ | 4/5 (80%) |
| Keywords (semantic) | ✅/⚠️ | 12/15 (80%) |
```

**Step 2: Commit**

```bash
git add .claude/skills/quality-gate/skill.md
git commit -m "feat(skill): integrate audit_coverage.py into quality-gate"
```

---

## Task 9: Update uk-quality-gate Skill

**Files:**
- Modify: `.claude/skills/uk-quality-gate/skill.md`

**Step 1: Read current file and add Keywords Coverage section**

After content validation section, add:

```markdown
### 3b. Keywords Coverage (audit_coverage.py)

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang uk --json --include-meta
```

**Checks:**

- [ ] primary+secondary: 100% COVERED (BLOCKER)
- [ ] supporting: ≥80% COVERED (WARNING)
- [ ] keywords[]: above adaptive threshold (WARNING)

**Include in report:**

| Keywords (primary+secondary) | ✅/❌ | 8/8 (100%) |
| Keywords (supporting) | ✅/⚠️ | 4/5 (80%) |
| Keywords (semantic) | ✅/⚠️ | 12/15 (80%) |
```

**Step 2: Commit**

```bash
git add .claude/skills/uk-quality-gate/skill.md
git commit -m "feat(skill): integrate audit_coverage.py into uk-quality-gate"
```

---

## Task 10: Update verify-content Skill

**Files:**
- Modify: `.claude/skills/verify-content/SKILL.md`

**Step 1: Add Keywords Coverage step**

Add new step after existing validation steps:

```markdown
### Step N: Keywords Coverage Check

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang ru --json --include-meta
```

Show results to user. Decision is manual.

**Display format:**

| Source | Covered | Total | % | Status |
|--------|---------|-------|---|--------|
| primary+secondary | X/Y | Z% | ✅/❌ |
| supporting | X/Y | Z% | ✅/⚠️ |
| keywords[] | X/Y | Z% | ✅/⚠️ |

If NOT COVERED in primary/secondary — highlight for user decision.
```

**Step 2: Commit**

```bash
git add .claude/skills/verify-content/SKILL.md
git commit -m "feat(skill): integrate audit_coverage.py into verify-content"
```

---

## Task 11: Update uk-verify-content Skill

**Files:**
- Modify: `.claude/skills/uk-verify-content/SKILL.md`

**Step 1: Add Keywords Coverage step**

```markdown
### Step N: Keywords Coverage Check

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang uk --json --include-meta
```

Show results to user. Decision is manual.

**Display format:**

| Source | Covered | Total | % | Status |
|--------|---------|-------|---|--------|
| primary+secondary | X/Y | Z% | ✅/❌ |
| supporting | X/Y | Z% | ✅/⚠️ |
| keywords[] | X/Y | Z% | ✅/⚠️ |

If NOT COVERED in primary/secondary — highlight for user decision.
```

**Step 2: Commit**

```bash
git add .claude/skills/uk-verify-content/SKILL.md
git commit -m "feat(skill): integrate audit_coverage.py into uk-verify-content"
```

---

## Task 12: Final Verification

**Step 1: Run all tests**

Run: `pytest tests/unit/test_coverage_matcher.py -v`
Expected: All PASS

**Step 2: Test --include-meta manually**

```bash
python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --json --include-meta | head -50
python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang ru --json --include-meta | head -50
```

Expected: JSON with both sections, correct coverage stats

**Step 3: Update design document status**

Change status in `docs/plans/2026-01-30-audit-coverage-integration-design.md`:
```markdown
**Статус:** Implemented
```

**Step 4: Final commit**

```bash
git add docs/plans/2026-01-30-audit-coverage-integration-design.md
git commit -m "docs: mark audit_coverage integration as implemented"
```

---

**Version:** 1.0
