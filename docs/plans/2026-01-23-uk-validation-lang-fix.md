# UK Skills `--lang uk` Validation Fix

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Оновити UK скіли та агенти, щоб вони передавали `--lang uk` у скрипти валідації, які підтримують цей прапорець.

**Architecture:** Редагування існуючих skill.md та agent.md файлів. Додавання `--lang uk` до викликів `check_keyword_density.py`, `check_h1_sync.py`, `check_semantic_coverage.py`. Без створення нових файлів.

**Tech Stack:** Markdown skills, Python validation scripts

---

## Task 1: Update uk-quality-gate/skill.md — keyword density

**Files:**
- Modify: `.claude/skills/uk-quality-gate/skill.md:107,171`

**Step 1: Read current file**

Run: `head -180 .claude/skills/uk-quality-gate/skill.md | tail -80`
Expected: Lines 100-180 visible with check_keyword_density calls

**Step 2: Edit line 107 — add --lang uk**

```
Old: python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md
New: python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
```

**Step 3: Edit line 171 — add --lang uk**

```
Old: python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md
New: python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
```

**Step 4: Verify changes**

Run: `grep "check_keyword_density" .claude/skills/uk-quality-gate/skill.md`
Expected: Both lines contain `--lang uk`

---

## Task 2: Update uk-quality-gate/skill.md — add h1_sync and semantic_coverage

**Files:**
- Modify: `.claude/skills/uk-quality-gate/skill.md`

**Step 1: Find validation section (around line 150-175)**

Run: `grep -n "Step 1: Run All Validations" .claude/skills/uk-quality-gate/skill.md`
Expected: Line number where validation commands block starts

**Step 2: Add check_h1_sync.py after keyword density check**

Add after the `check_keyword_density.py` line in the validation block:

```bash
# H1 sync check
python3 scripts/check_h1_sync.py --lang uk
```

**Step 3: Add check_semantic_coverage.py**

Add after check_h1_sync:

```bash
# Semantic coverage check
python3 scripts/check_semantic_coverage.py --lang uk
```

**Step 4: Verify all UK validation commands present**

Run: `grep -E "check_(keyword_density|h1_sync|semantic_coverage)" .claude/skills/uk-quality-gate/skill.md`
Expected: 3+ lines, all with `--lang uk`

---

## Task 3: Update uk-quality-gate/skill.md — version bump

**Files:**
- Modify: `.claude/skills/uk-quality-gate/skill.md`

**Step 1: Find version line**

Run: `grep -n "Version:" .claude/skills/uk-quality-gate/skill.md`
Expected: Line with "Version: 2.0"

**Step 2: Update version to 2.1**

```
Old: **Version:** 2.0 — January 2026 (parity with quality-gate v3.0)
New: **Version:** 2.1 — January 2026 (added --lang uk to validation scripts)
```

**Step 3: Add changelog entry**

Add after existing changelog:

```markdown
**Changelog v2.1:**
- Added `--lang uk` to check_keyword_density.py calls
- Added check_h1_sync.py --lang uk validation
- Added check_semantic_coverage.py --lang uk validation
```

**Step 4: Commit**

```bash
git add .claude/skills/uk-quality-gate/skill.md
git commit -m "$(cat <<'EOF'
feat(skills): add --lang uk to uk-quality-gate validation scripts

- check_keyword_density.py now uses UK stemmer
- Added check_h1_sync.py --lang uk
- Added check_semantic_coverage.py --lang uk
- Version 2.0 → 2.1

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Update uk-content-generator/skill.md

**Files:**
- Modify: `.claude/skills/uk-content-generator/skill.md:158`

**Step 1: Find keyword density line**

Run: `grep -n "check_keyword_density" .claude/skills/uk-content-generator/skill.md`
Expected: Line 158 with workflow step

**Step 2: Update workflow step with full command**

```
Old: 9. Check density    → check_keyword_density.py (stem ≤2.5%)
New: 9. Check density    → python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk (stem ≤2.5%)
```

**Step 3: Update version**

```
Old: **Version:** 2.0 — January 2026 (parity with content-generator v3.3)
New: **Version:** 2.1 — January 2026 (added --lang uk to validation)
```

**Step 4: Commit**

```bash
git add .claude/skills/uk-content-generator/skill.md
git commit -m "$(cat <<'EOF'
feat(skills): add --lang uk to uk-content-generator validation

- Explicit check_keyword_density.py command with --lang uk
- Version 2.0 → 2.1

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Update uk-content-reviewer.md agent

**Files:**
- Modify: `.claude/agents/uk-content-reviewer.md:137`

**Step 1: Find keyword density line**

Run: `grep -n "check_keyword_density" .claude/agents/uk-content-reviewer.md`
Expected: Line 137 with validation command

**Step 2: Add --lang uk**

```
Old: python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md
New: python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
```

**Step 3: Update version**

```
Old: **Version:** 2.0 — January 2026
New: **Version:** 2.1 — January 2026 (added --lang uk)
```

**Step 4: Commit**

```bash
git add .claude/agents/uk-content-reviewer.md
git commit -m "$(cat <<'EOF'
feat(agents): add --lang uk to uk-content-reviewer validation

- check_keyword_density.py now uses UK stemmer
- Version 2.0 → 2.1

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Final verification

**Step 1: Check all UK files for missing --lang uk**

Run: `grep -r "check_keyword_density" .claude/skills/uk-* .claude/agents/uk-* | grep -v "\-\-lang uk"`
Expected: No output (all calls have --lang uk)

**Step 2: Check h1_sync and semantic_coverage**

Run: `grep -r "check_h1_sync\|check_semantic_coverage" .claude/skills/uk-* .claude/agents/uk-*`
Expected: uk-quality-gate has both with --lang uk

**Step 3: Verify git log**

Run: `git log --oneline -5`
Expected: 3 new commits for uk-quality-gate, uk-content-generator, uk-content-reviewer

---

## Summary

| File | Changes |
|------|---------|
| `.claude/skills/uk-quality-gate/skill.md` | +`--lang uk` x2, +h1_sync, +semantic_coverage, v2.1 |
| `.claude/skills/uk-content-generator/skill.md` | +`--lang uk` x1, v2.1 |
| `.claude/agents/uk-content-reviewer.md` | +`--lang uk` x1, v2.1 |

---

**Plan Version:** 1.0 — 2026-01-23
