# UK Meta & Content Update Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Update meta tags and content for all 53 UK categories after keyword refresh.

**Architecture:** Two-phase approach — first fix skills with outdated script references, then parallel workers process categories using `/uk-generate-meta` and `uk-content-reviewer`.

**Tech Stack:** Python validators, Claude Code skills, parallel workers (tmux)

---

## Phase 0: Fix Skills

### Task 1: Update uk-content-reviewer skill

**Files:**
- Modify: `.claude/skills/uk-content-reviewer/SKILL.md:97-101`

**Step 1: Read current file**

Read `.claude/skills/uk-content-reviewer/SKILL.md` to confirm line numbers.

**Step 2: Replace script references**

```
OLD: python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
NEW: python3 scripts/validate_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

OLD: python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary}"
NEW: python3 scripts/validate_seo.py uk/categories/{slug}/content/{slug}_uk.md "{primary}"
```

**Step 3: Verify scripts exist**

Run: `ls scripts/validate_density.py scripts/validate_seo.py`
Expected: Both files listed

---

### Task 2: Update uk-content-generator skill

**Files:**
- Modify: `.claude/skills/uk-content-generator/skill.md:414`

**Step 1: Read current file**

Read `.claude/skills/uk-content-generator/skill.md` lines 410-420.

**Step 2: Replace script reference**

```
OLD: python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
NEW: python3 scripts/validate_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
```

---

### Task 3: Update content-reviewer skill (RU)

**Files:**
- Modify: `.claude/skills/content-reviewer/SKILL.md:98-99`

**Step 1: Read current file**

Read `.claude/skills/content-reviewer/SKILL.md` lines 95-105.

**Step 2: Replace script references**

```
OLD: python3 scripts/check_keyword_density.py categories/{path}/content/{slug}_ru.md
NEW: python3 scripts/validate_density.py categories/{path}/content/{slug}_ru.md

OLD: python3 scripts/check_seo_structure.py ...
NEW: python3 scripts/validate_seo.py ...
```

---

### Task 4: Update content-generator skill (RU)

**Files:**
- Modify: `.claude/skills/content-generator/skill.md:395`

**Step 1: Read current file**

Read `.claude/skills/content-generator/skill.md` lines 390-400.

**Step 2: Replace script reference**

```
OLD: python3 scripts/check_keyword_density.py categories/{slug}/content/{slug}_ru.md
NEW: python3 scripts/validate_density.py categories/{slug}/content/{slug}_ru.md
```

---

### Task 5: Update shared validation-checklist

**Files:**
- Modify: `.claude/skills/shared/validation-checklist.md:84,90`

**Step 1: Read current file**

Read `.claude/skills/shared/validation-checklist.md` lines 75-95.

**Step 2: Replace script references**

```
OLD: python3 scripts/check_keyword_density.py {content_path}
NEW: python3 scripts/validate_density.py {content_path}

OLD: python3 scripts/check_seo_structure.py {content_path} "{primary}"
NEW: python3 scripts/validate_seo.py {content_path} "{primary}"
```

---

### Task 6: Commit skill fixes

**Step 1: Check changes**

Run: `git diff --stat .claude/skills/`

**Step 2: Commit**

```bash
git add .claude/skills/
git commit -m "fix(skills): update script references after rename

- check_keyword_density.py → validate_density.py
- check_seo_structure.py → validate_seo.py

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 1: Parallel Workers

### Task 7: Create worker log directory

**Step 1: Create directory**

Run: `mkdir -p data/generated/audit-logs`

---

### Task 8: Launch Worker 1 (13 categories)

**Categories:**
```
akkumulyatornaya, aksessuary, aksessuary-dlya-naneseniya-sredstv, aktivnaya-pena, antibitum, antidozhd, antimoshka, apparaty-tornador, avtoshampuni, cherniteli-shin, glavnaya, glina-i-avtoskraby, gubki-i-varezhki
```

**Step 1: Launch worker**

```bash
spawn-claude "W1: UK Meta + Content Update.

/superpowers:executing-plans docs/plans/2026-01-30-uk-meta-content-update-plan.md

Выполни Task 8 (W1 categories).

Категории (13):
akkumulyatornaya, aksessuary, aksessuary-dlya-naneseniya-sredstv, aktivnaya-pena, antibitum, antidozhd, antimoshka, apparaty-tornador, avtoshampuni, cherniteli-shin, glavnaya, glina-i-avtoskraby, gubki-i-varezhki

Для КАЖДОЙ категории:
1. /uk-generate-meta {slug}
2. uk-content-reviewer {slug}

Пиши лог в data/generated/audit-logs/W1_uk_update_log.md

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"
```

---

### Task 9: Launch Worker 2 (13 categories)

**Categories:**
```
keramika-dlya-diskov, keramika-i-zhidkoe-steklo, kisti-dlya-deteylinga, kvik-deteylery, malyarniy-skotch, mekhovye, mikrofibra-i-tryapki, moyka-i-eksterer, nabory, neytralizatory-zapakha, obezzhirivateli, oborudovanie, ochistiteli-diskov
```

**Step 1: Launch worker**

```bash
spawn-claude "W2: UK Meta + Content Update.

/superpowers:executing-plans docs/plans/2026-01-30-uk-meta-content-update-plan.md

Выполни Task 9 (W2 categories).

Категории (13):
keramika-dlya-diskov, keramika-i-zhidkoe-steklo, kisti-dlya-deteylinga, kvik-deteylery, malyarniy-skotch, mekhovye, mikrofibra-i-tryapki, moyka-i-eksterer, nabory, neytralizatory-zapakha, obezzhirivateli, oborudovanie, ochistiteli-diskov

Для КАЖДОЙ категории:
1. /uk-generate-meta {slug}
2. uk-content-reviewer {slug}

Пиши лог в data/generated/audit-logs/W2_uk_update_log.md

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"
```

---

### Task 10: Launch Worker 3 (13 categories)

**Categories:**
```
ochistiteli-dvigatelya, ochistiteli-kozhi, ochistiteli-kuzova, ochistiteli-shin, ochistiteli-stekol, omyvatel, opt-i-b2b, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-mashinki, polirovalnye-pasty, polirovka, pyatnovyvoditeli
```

**Step 1: Launch worker**

```bash
spawn-claude "W3: UK Meta + Content Update.

/superpowers:executing-plans docs/plans/2026-01-30-uk-meta-content-update-plan.md

Выполни Task 10 (W3 categories).

Категории (13):
ochistiteli-dvigatelya, ochistiteli-kozhi, ochistiteli-kuzova, ochistiteli-shin, ochistiteli-stekol, omyvatel, opt-i-b2b, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-mashinki, polirovalnye-pasty, polirovka, pyatnovyvoditeli

Для КАЖДОЙ категории:
1. /uk-generate-meta {slug}
2. uk-content-reviewer {slug}

Пиши лог в data/generated/audit-logs/W3_uk_update_log.md

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"
```

---

### Task 11: Launch Worker 4 (14 categories)

**Categories:**
```
raspyliteli-i-penniki, shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto, silanty, sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi, tverdyy-vosk, ukhod-za-intererom, ukhod-za-kozhey, ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, voski, zashchitnye-pokrytiya, zhidkiy-vosk
```

**Step 1: Launch worker**

```bash
spawn-claude "W4: UK Meta + Content Update.

/superpowers:executing-plans docs/plans/2026-01-30-uk-meta-content-update-plan.md

Выполни Task 11 (W4 categories).

Категории (14):
raspyliteli-i-penniki, shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto, silanty, sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi, tverdyy-vosk, ukhod-za-intererom, ukhod-za-kozhey, ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, voski, zashchitnye-pokrytiya, zhidkiy-vosk

Для КАЖДОЙ категории:
1. /uk-generate-meta {slug}
2. uk-content-reviewer {slug}

Пиши лог в data/generated/audit-logs/W4_uk_update_log.md

НЕ ДЕЛАЙ git commit - коммиты делает оркестратор" "$(pwd)"
```

---

## Phase 2: Review & Commit

### Task 12: Monitor workers

**Step 1: Check tmux windows**

Run: `tmux list-windows` (Ctrl+A, w)

**Step 2: Wait for completion**

Monitor logs:
```bash
tail -f data/generated/audit-logs/W*_uk_update_log.md
```

---

### Task 13: Validate all meta files

**Step 1: Run batch validation**

```bash
python3 scripts/validate_meta.py --all --lang uk
```

Expected: All 53 categories PASS

---

### Task 14: Review worker logs

**Step 1: Check for BLOCKERs**

```bash
grep -l "BLOCKER\|❌" data/generated/audit-logs/W*_uk_update_log.md
```

Expected: No BLOCKERs remaining

---

### Task 15: Final commit

**Step 1: Check changes**

```bash
git status
git diff --stat uk/categories/
```

**Step 2: Commit all changes**

```bash
git add uk/categories/
git commit -m "feat(uk): update meta and content for 53 categories

- Regenerated meta tags with new keywords
- Reviewed and fixed content per uk-content-reviewer
- All validators pass

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Success Criteria

- [ ] All 5 skills updated with correct script names
- [ ] Skills commit pushed
- [ ] All 4 workers completed
- [ ] All 53 `_meta.json` pass `validate_meta.py --all --lang uk`
- [ ] No BLOCKERs in worker logs
- [ ] Final commit with all UK changes

---

**Total Tasks:** 15
**Estimated parallel execution:** Phase 0 sequential (Tasks 1-6), Phase 1 parallel (Tasks 7-11), Phase 2 sequential (Tasks 12-15)
