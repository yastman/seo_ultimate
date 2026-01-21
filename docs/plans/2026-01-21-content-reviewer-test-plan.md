# Content Reviewer Agent: Test & Integration Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Протестировать субагента content-reviewer на одной категории и интегрировать в workflow.

**Architecture:** Smoke test → Validator check → Edit capability → Integration → Batch test.

**Tech Stack:** Python validators (validate_meta.py, validate_content.py, check_keyword_density.py, check_water_natasha.py), Task tool для вызова субагента.

---

## Prerequisites

**Step 1: Verify agent file exists**

```bash
cat .claude/agents/content-reviewer.md | head -20
```

Expected: YAML frontmatter с `name: content-reviewer`, `model: opus`, `tools: Read, Grep, Glob, Bash, Edit`

**Step 2: Verify validation scripts**

```bash
python3 scripts/validate_meta.py --help
python3 scripts/validate_content.py --help
python3 scripts/check_keyword_density.py --help 2>/dev/null || echo "OK (no --help)"
python3 scripts/check_water_natasha.py --help 2>/dev/null || echo "OK (no --help)"
```

Expected: No import errors, scripts executable.

**Step 3: Choose test category**

```
Test category: moyka-i-eksterer/avtoshampuni/aktivnaya-pena
Slug: aktivnaya-pena
Type: Product Page (parent_id ≠ null)
```

---

## Task 1: Verify Data Files Exist

**Files:**
- Check: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json`
- Check: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/meta/aktivnaya-pena_meta.json`
- Check: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md`
- Check: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/research/RESEARCH_DATA.md`

**Step 1: Check all 4 files exist**

```bash
ls -la categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json
ls -la categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/meta/aktivnaya-pena_meta.json
ls -la categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
ls -la categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/research/RESEARCH_DATA.md
```

Expected: All 4 files exist, non-empty.

**Step 2: Verify JSON valid**

```bash
python3 -c "import json; json.load(open('categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json'))"
python3 -c "import json; json.load(open('categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/meta/aktivnaya-pena_meta.json'))"
```

Expected: No errors.

---

## Task 2: Run Validators Manually

**Files:**
- Test: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md`

**Step 1: Run validate_meta.py**

```bash
python3 scripts/validate_meta.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/meta/aktivnaya-pena_meta.json
```

Expected: PASS or list of issues.

**Step 2: Run validate_content.py**

```bash
python3 scripts/validate_content.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md "активная пена" --mode seo
```

Expected: PASS or list of issues.

**Step 3: Run check_keyword_density.py**

```bash
python3 scripts/check_keyword_density.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
```

Expected: Stem density report, max <3.0%.

**Step 4: Run check_water_natasha.py**

```bash
python3 scripts/check_water_natasha.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
```

Expected: Water %, classic nausea, academic nausea.

**Step 5: Document baseline**

Record current validator output as baseline for comparison after agent run.

---

## Task 3: Invoke Content-Reviewer Agent

**Step 1: Call agent via Task tool**

Use Task tool with:
- `subagent_type`: `content-reviewer`
- `prompt`: `moyka-i-eksterer/avtoshampuni/aktivnaya-pena`

**Step 2: Observe agent behavior**

Checklist:
- [ ] Agent reads 4 data files
- [ ] Agent runs 4 validators
- [ ] Agent performs keywords coverage check
- [ ] Agent performs facts vs research check
- [ ] Agent performs buyer guide quality check
- [ ] Agent fills verdict table
- [ ] Agent makes Edit calls if issues found
- [ ] Agent re-validates after fixes
- [ ] Agent outputs structured report

**Step 3: Verify agent did NOT commit**

```bash
git status
```

Expected: Modified files shown but NOT committed.

---

## Task 4: Review Agent Output

**Step 1: Check output format**

Agent output should contain:
- `## Review: aktivnaya-pena`
- `**Path:** categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena`
- `**Type:** Product Page`
- `**Verdict:** ✅/⚠️/❌`
- Verdict table with all 13 criteria
- List of fixes (if any)
- Re-validation results

**Step 2: Verify fixes are correct**

```bash
git diff categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
```

Review each change:
- [ ] H1 matches `name` from `_clean.json`
- [ ] No how-to sections added
- [ ] Keywords added organically (not stuffed)
- [ ] Facts match RESEARCH_DATA.md

**Step 3: Re-run validators**

```bash
python3 scripts/check_keyword_density.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
python3 scripts/check_water_natasha.py categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md
```

Expected: Same or better than baseline.

---

## Task 5: Commit Test Results

**Step 1: Stage and commit agent file**

```bash
git add .claude/agents/content-reviewer.md
git add docs/plans/2026-01-21-content-reviewer-agent-design.md
git add docs/plans/2026-01-21-content-reviewer-test-plan.md
git commit -m "feat(agents): add content-reviewer for revision workflow v3.0"
```

**Step 2: Commit test category changes (if fixes were good)**

```bash
git add categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/
git commit -m "review(content): aktivnaya-pena - validated via content-reviewer"
```

---

## Task 6: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Add content-reviewer to pipeline**

Add to Skills table:

```markdown
| Нужна ревизия контента | `content-reviewer {path}` | Проверяет и исправляет контент категории |
```

**Step 2: Update pipeline description**

```markdown
## Pipeline

```
/category-init → /generate-meta → /seo-research → /content-generator → content-reviewer → /uk-content-init → /quality-gate → /deploy
```
```

**Step 3: Commit CLAUDE.md**

```bash
git add CLAUDE.md
git commit -m "docs: add content-reviewer to pipeline"
```

---

## Task 7: Batch Test (3 categories)

**Step 1: Run content-reviewer on 3 categories sequentially**

Categories:
1. `moyka-i-eksterer` (Hub Page)
2. `moyka-i-eksterer/avtoshampuni` (Hub Page)
3. `moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki` (Product Page)

For each: Task tool → content-reviewer → review output → approve fixes

**Step 2: Verify diverse page types work**

- [ ] Hub Page works correctly
- [ ] Product Page works correctly
- [ ] Validators run correctly for all
- [ ] Fixes are appropriate

**Step 3: Document issues**

If any issues found during batch test, document in `docs/plans/2026-01-21-content-reviewer-issues.md`

**Step 4: Commit batch results**

```bash
git add categories/moyka-i-eksterer/
git commit -m "review(content): batch test moyka-i-eksterer - 3 categories validated"
```

---

## Execution Checklist

| Task | Description | Status |
|------|-------------|--------|
| 1 | Verify data files exist | ⬜ |
| 2 | Run validators manually | ⬜ |
| 3 | Invoke content-reviewer agent | ⬜ |
| 4 | Review agent output | ⬜ |
| 5 | Commit test results | ⬜ |
| 6 | Update CLAUDE.md | ⬜ |
| 7 | Batch test 3 categories | ⬜ |

---

## Success Criteria

- [ ] Agent reads all 4 data files correctly
- [ ] Agent runs all 4 validators
- [ ] Agent performs manual checks (keywords, facts, buyer guide)
- [ ] Agent makes appropriate fixes via Edit tool
- [ ] Agent does NOT commit (user controls git)
- [ ] Agent outputs structured verdict report
- [ ] Fixes improve or maintain validator scores
- [ ] Works for both Hub and Product pages

---

## Next Steps After Success

1. **Full batch execution:** Use `superpowers:dispatching-parallel-agents` to run content-reviewer on all 50 categories
2. **Or sequential:** Use `superpowers:executing-plans` with `2026-01-21-content-revision-plan.md`, calling content-reviewer for each category

---

**Plan Version:** 1.0 | **Created:** 2026-01-21
