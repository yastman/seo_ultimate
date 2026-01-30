# Validation Skills Fix Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix validation skills and coverage logic so workers correctly detect and fix keyword coverage issues.

**Architecture:** Fix pymorphy Surn filter → change SYNONYM to not-covered → update audit output → update 7 skill files via /skill-creator.

**Tech Stack:** Python, pymorphy3, pytest, Claude skills

---

## Task 1: Fix morphology Surn filter

**Files:**
- Modify: `scripts/keyword_utils.py` (MorphAnalyzer.get_lemma method)
- Test: `tests/unit/test_keyword_utils.py`

**Step 1: Write the failing test**

Add to `tests/unit/test_keyword_utils.py`:

```python
class TestMorphAnalyzerSurnFilter:
    """Test that Surn (surname) parses are filtered out."""

    def test_uk_gubka_not_surname(self):
        """губка should lemmatize to губка, not губко (surname)."""
        morph = MorphAnalyzer(lang='uk')
        assert morph.get_lemma("губка") == "губка"

    def test_uk_gubky_to_gubka(self):
        """губки should lemmatize to губка."""
        morph = MorphAnalyzer(lang='uk')
        assert morph.get_lemma("губки") == "губка"

    def test_ru_no_surname_interference(self):
        """RU morphology should also filter surnames."""
        morph = MorphAnalyzer(lang='ru')
        # Иванов as noun (not surname Ivanov)
        result = morph.get_lemma("шампунь")
        assert result == "шампунь"
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_keyword_utils.py::TestMorphAnalyzerSurnFilter -v`
Expected: FAIL on `test_uk_gubka_not_surname` (returns "губко")

**Step 3: Find and read the get_lemma method**

Run: `grep -n "def get_lemma" scripts/keyword_utils.py`

Read the method to understand current implementation.

**Step 4: Implement Surn filter**

In `scripts/keyword_utils.py`, modify `get_lemma()` method:

```python
def get_lemma(self, word: str) -> str:
    """Get lemma (normal form) of a word, filtering out surname parses."""
    if not word:
        return word

    word_lower = word.lower()
    parses = self._morph.parse(word_lower)

    if not parses:
        return word_lower

    # Filter out surname (Surn) parses - they give false lemmas
    # e.g., "губка" parsed as surname "Губко" instead of noun "губка"
    non_surname = [p for p in parses if 'Surn' not in p.tag]

    if non_surname:
        return non_surname[0].normal_form

    # Fallback if all parses are surnames
    return parses[0].normal_form
```

**Step 5: Run test to verify it passes**

Run: `pytest tests/unit/test_keyword_utils.py::TestMorphAnalyzerSurnFilter -v`
Expected: PASS

**Step 6: Run all keyword_utils tests**

Run: `pytest tests/unit/test_keyword_utils.py -v`
Expected: All PASS (no regressions)

**Step 7: Commit**

```bash
git add scripts/keyword_utils.py tests/unit/test_keyword_utils.py
git commit -m "fix(morphology): filter Surn parses in get_lemma

pymorphy3 returns surname parses (e.g., губка→губко) with same score
as noun parses. Filter out Surn-tagged parses to get correct lemmas.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Change SYNONYM to not-covered

**Files:**
- Modify: `scripts/coverage_matcher.py`
- Test: `tests/unit/test_coverage_matcher.py`

**Step 1: Write the failing test**

Add to `tests/unit/test_coverage_matcher.py`:

```python
class TestSynonymNotCovered:
    """Test that SYNONYM status means covered=False."""

    def test_synonym_match_returns_not_covered(self):
        """When keyword matches only via synonym, covered should be False."""
        # This test verifies the contract: SYNONYM → covered=False
        from scripts.coverage_matcher import MatchResult

        # Create a SYNONYM result
        result = MatchResult(
            status="SYNONYM",
            covered=False,  # This is what we're enforcing
            covered_by="синонім ключа",
            syn_match_method="NORM",
            reason="Synonym match only"
        )

        assert result.status == "SYNONYM"
        assert result.covered is False
        assert result.reason == "Synonym match only"
```

**Step 2: Run test to verify current behavior**

Run: `pytest tests/unit/test_coverage_matcher.py::TestSynonymNotCovered -v`
Note: May pass (just testing the contract) - we need to find where SYNONYM is created.

**Step 3: Find SYNONYM creation in coverage_matcher.py**

Run: `grep -n "SYNONYM" scripts/coverage_matcher.py`

Read the code to find where `status="SYNONYM"` is set.

**Step 4: Modify SYNONYM to set covered=False**

Find the location where SYNONYM MatchResult is created and change:

```python
# Was:
return MatchResult(
    status="SYNONYM",
    covered=True,  # OLD
    ...
)

# Change to:
return MatchResult(
    status="SYNONYM",
    covered=False,  # NEW - synonym found but keyword itself absent
    covered_by=synonym_keyword,
    syn_match_method=method,
    reason="Synonym match only"
)
```

**Step 5: Run coverage_matcher tests**

Run: `pytest tests/unit/test_coverage_matcher.py -v`
Expected: All PASS

**Step 6: Commit**

```bash
git add scripts/coverage_matcher.py tests/unit/test_coverage_matcher.py
git commit -m "fix(coverage): SYNONYM status now means covered=False

SYNONYM indicates the keyword is covered by a synonym, but the
actual keyword is absent from the text. For SEO purposes, the
keyword itself must appear, so SYNONYM → not covered.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Update audit_coverage.py verbose output

**Files:**
- Modify: `scripts/audit_coverage.py`

**Step 1: Find verbose output code**

Run: `grep -n "COVERED\|SYNONYM" scripts/audit_coverage.py`

Read the verbose output section.

**Step 2: Move SYNONYM to NOT COVERED section**

Find the verbose output logic and ensure SYNONYM appears in "✗ NOT COVERED" block:

```python
# In the verbose output section, SYNONYM should be grouped with NOT COVERED
# since covered=False for SYNONYM results

# Example output format:
# ✗ NOT COVERED (3):
#   - [SYNONYM] активна піна для авто (1600) ← via "активна піна для миття авто"
#   - [PARTIAL] хімія для миття авто (1000) — 100% lemmas
#   - [ABSENT] гель для миття авто (90)
```

**Step 3: Test verbose output**

Run: `python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --verbose`

Verify SYNONYM appears in NOT COVERED section.

**Step 4: Commit**

```bash
git add scripts/audit_coverage.py
git commit -m "fix(audit): show SYNONYM in NOT COVERED section

SYNONYM now has covered=False, so verbose output should display
it in the NOT COVERED block for clarity.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Update shared/validation-checklist.md

**Files:**
- Modify: `.claude/skills/shared/validation-checklist.md`

**Step 1: Read current file**

Read `.claude/skills/shared/validation-checklist.md`

**Step 2: Replace script names**

```
OLD: python3 scripts/check_keyword_density.py {content_path}
NEW: python3 scripts/validate_density.py {content_path}

OLD: python3 scripts/check_seo_structure.py {content_path} "{primary}"
NEW: python3 scripts/validate_seo.py {content_path} "{primary}"
```

**Step 3: Commit**

```bash
git add .claude/skills/shared/validation-checklist.md
git commit -m "fix(skills): update script names in validation-checklist

- check_keyword_density.py → validate_density.py
- check_seo_structure.py → validate_seo.py

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Update content-reviewer skill

**Files:**
- Modify: `.claude/skills/content-reviewer/SKILL.md`

**Step 1: Use /skill-creator**

Invoke: `/skill-creator`

Request changes:
1. Replace `check_keyword_density.py` → `validate_density.py`
2. Replace `check_seo_structure.py` → `validate_seo.py`
3. Update severity table: keywords[] = BLOCKER
4. Add "COVERED = EXACT/NORM/LEMMA, NOT COVERED = SYNONYM/PARTIAL/ABSENT"
5. Add Step 10: Re-validate Coverage (mandatory, max 3 iterations)
6. Add concrete instructions for where to add keywords

**Step 2: Verify changes**

Read the updated file and verify all changes applied.

**Step 3: Commit**

```bash
git add .claude/skills/content-reviewer/SKILL.md
git commit -m "fix(skills): update content-reviewer with new coverage rules

- Fix script names
- keywords[] = BLOCKER (was WARNING)
- SYNONYM = not covered
- Add mandatory re-validate step (max 3 iterations)
- Add concrete keyword placement instructions

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Update uk-content-reviewer skill

**Files:**
- Modify: `.claude/skills/uk-content-reviewer/SKILL.md`

**Step 1: Use /skill-creator**

Invoke: `/skill-creator`

Request changes:
1. Update severity table: keywords[] = BLOCKER
2. Add "COVERED = EXACT/NORM/LEMMA, NOT COVERED = SYNONYM/PARTIAL/ABSENT"
3. Add Step 10: Re-validate Coverage (mandatory, max 3 iterations)
4. Add concrete instructions for where to add keywords

**Step 2: Commit**

```bash
git add .claude/skills/uk-content-reviewer/SKILL.md
git commit -m "fix(skills): update uk-content-reviewer with new coverage rules

- keywords[] = BLOCKER (was WARNING)
- SYNONYM = not covered
- Add mandatory re-validate step
- Add keyword placement instructions

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Update quality-gate skill

**Files:**
- Modify: `.claude/skills/quality-gate/SKILL.md`

**Step 1: Use /skill-creator**

Invoke: `/skill-creator`

Request changes:
1. Replace `check_keyword_density.py` → `validate_density.py`
2. Replace `check_seo_structure.py` → `validate_seo.py`
3. Update coverage rules documentation

**Step 2: Commit**

```bash
git add .claude/skills/quality-gate/SKILL.md
git commit -m "fix(skills): update quality-gate script names

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Update uk-quality-gate skill

**Files:**
- Modify: `.claude/skills/uk-quality-gate/skill.md`

**Step 1: Use /skill-creator**

Invoke: `/skill-creator`

Request changes:
1. Replace `check_keyword_density.py` → `validate_density.py`
2. Replace `check_seo_structure.py` → `validate_seo.py`

**Step 2: Commit**

```bash
git add .claude/skills/uk-quality-gate/skill.md
git commit -m "fix(skills): update uk-quality-gate script names

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Update verify-content skill

**Files:**
- Modify: `.claude/skills/verify-content/SKILL.md`

**Step 1: Use /skill-creator**

Invoke: `/skill-creator`

Request changes:
1. Replace `check_keyword_density.py` → `validate_density.py`
2. Replace `check_seo_structure.py` → `validate_seo.py`

**Step 2: Commit**

```bash
git add .claude/skills/verify-content/SKILL.md
git commit -m "fix(skills): update verify-content script names

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Update uk-verify-content skill

**Files:**
- Modify: `.claude/skills/uk-verify-content/SKILL.md`

**Step 1: Use /skill-creator**

Invoke: `/skill-creator`

Request changes:
1. Add re-validate step after fixes

**Step 2: Commit**

```bash
git add .claude/skills/uk-verify-content/SKILL.md
git commit -m "fix(skills): add re-validate to uk-verify-content

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Final verification

**Step 1: Run all tests**

Run: `pytest tests/unit/test_keyword_utils.py tests/unit/test_coverage_matcher.py -v`
Expected: All PASS

**Step 2: Test morphology fix**

Run:
```bash
python3 -c "from scripts.keyword_utils import MorphAnalyzer; m=MorphAnalyzer('uk'); print('губка →', m.get_lemma('губка'))"
```
Expected: `губка → губка` (not губко)

**Step 3: Test coverage output**

Run: `python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --verbose`
Expected: SYNONYM in NOT COVERED section

**Step 4: Verify skill files have no old script names**

Run:
```bash
grep -r "check_keyword_density\|check_seo_structure" .claude/skills/
```
Expected: No matches

---

## Success Criteria

- [ ] `get_lemma("губка")` returns "губка" (not "губко")
- [ ] SYNONYM status has `covered=False`
- [ ] audit_coverage verbose shows SYNONYM in NOT COVERED
- [ ] All 7 skill files use correct script names
- [ ] content-reviewer has re-validate step with max 3 iterations
- [ ] uk-content-reviewer has re-validate step
- [ ] All tests pass

---

**Total Tasks:** 11
**Estimated execution:** Sequential (Tasks 1-4 can be done without /skill-creator, Tasks 5-10 require /skill-creator)
