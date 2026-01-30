# UK Full Audit — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Повний аудит 52 UK категорій з перевіркою ключів, мета, контенту, щільності, тошноти через інтерактивний скілл `/uk-verify-content`.

**Architecture:**
- Кожна категорія проходить через `/uk-verify-content {slug}` з ручною перевіркою
- Людина контролює кожен крок і вирішує що виправляти
- Після фіксів — QUALITY_REPORT.md в категорії

**Tech Stack:** Python validators, Edit tool, uk-verify-content skill

**Design:** [2026-01-26-uk-full-audit-design.md](2026-01-26-uk-full-audit-design.md)

---

## Pre-flight: Commit Pending Changes

**Files:**
- Commit: `.claude/skills/uk-verify-content/SKILL.md`

**Step 1: Check status**

```bash
git status --short .claude/skills/uk-verify-content/
```

Expected: New skill files

**Step 2: Commit skill**

```bash
git add .claude/skills/uk-verify-content/
git commit -m "feat: add uk-verify-content skill for interactive UK audit"
```

---

## Task Template (repeat for each category)

### Task N: {slug}

**Invoke skill:**

```
/uk-verify-content {slug}
```

**The skill will:**
1. Load files (parallel)
2. Run validators
3. Check UK terminology
4. Verify facts against research
5. Check keywords coverage
6. Present quality checklist
7. Show verdict & actions
8. Fix mode if needed

**After skill completes:**

```bash
git add uk/categories/{slug}/
git commit -m "audit(uk): {slug} — verified and fixed"
```

---

## Categories (52)

### Group 1: A-categories (8)

| # | Slug | Task |
|---|------|------|
| 1 | akkumulyatornaya | `/uk-verify-content akkumulyatornaya` |
| 2 | aksessuary | `/uk-verify-content aksessuary` |
| 3 | aksessuary-dlya-naneseniya-sredstv | `/uk-verify-content aksessuary-dlya-naneseniya-sredstv` |
| 4 | aktivnaya-pena | `/uk-verify-content aktivnaya-pena` |
| 5 | antibitum | `/uk-verify-content antibitum` |
| 6 | antidozhd | `/uk-verify-content antidozhd` |
| 7 | antimoshka | `/uk-verify-content antimoshka` |
| 8 | apparaty-tornador | `/uk-verify-content apparaty-tornador` |

### Group 2: A-G categories (6)

| # | Slug | Task |
|---|------|------|
| 9 | avtoshampuni | `/uk-verify-content avtoshampuni` |
| 10 | cherniteli-shin | `/uk-verify-content cherniteli-shin` |
| 11 | glina-i-avtoskraby | `/uk-verify-content glina-i-avtoskraby` |
| 12 | gubki-i-varezhki | `/uk-verify-content gubki-i-varezhki` |
| 13 | keramika-dlya-diskov | `/uk-verify-content keramika-dlya-diskov` |
| 14 | keramika-i-zhidkoe-steklo | `/uk-verify-content keramika-i-zhidkoe-steklo` |

### Group 3: K-M categories (7)

| # | Slug | Task |
|---|------|------|
| 15 | kisti-dlya-deteylinga | `/uk-verify-content kisti-dlya-deteylinga` |
| 16 | kvik-deteylery | `/uk-verify-content kvik-deteylery` |
| 17 | malyarniy-skotch | `/uk-verify-content malyarniy-skotch` |
| 18 | mekhovye | `/uk-verify-content mekhovye` |
| 19 | mikrofibra-i-tryapki | `/uk-verify-content mikrofibra-i-tryapki` |
| 20 | moyka-i-eksterer | `/uk-verify-content moyka-i-eksterer` |
| 21 | nabory | `/uk-verify-content nabory` |

### Group 4: N-O categories (10)

| # | Slug | Task |
|---|------|------|
| 22 | neytralizatory-zapakha | `/uk-verify-content neytralizatory-zapakha` |
| 23 | obezzhirivateli | `/uk-verify-content obezzhirivateli` |
| 24 | oborudovanie | `/uk-verify-content oborudovanie` |
| 25 | ochistiteli-diskov | `/uk-verify-content ochistiteli-diskov` |
| 26 | ochistiteli-dvigatelya | `/uk-verify-content ochistiteli-dvigatelya` |
| 27 | ochistiteli-kozhi | `/uk-verify-content ochistiteli-kozhi` |
| 28 | ochistiteli-kuzova | `/uk-verify-content ochistiteli-kuzova` |
| 29 | ochistiteli-shin | `/uk-verify-content ochistiteli-shin` |
| 30 | ochistiteli-stekol | `/uk-verify-content ochistiteli-stekol` |
| 31 | omyvatel | `/uk-verify-content omyvatel` |

### Group 5: O-P categories (8)

| # | Slug | Task |
|---|------|------|
| 32 | opt-i-b2b | `/uk-verify-content opt-i-b2b` |
| 33 | polirol-dlya-stekla | `/uk-verify-content polirol-dlya-stekla` |
| 34 | poliroli-dlya-plastika | `/uk-verify-content poliroli-dlya-plastika` |
| 35 | polirovalnye-mashinki | `/uk-verify-content polirovalnye-mashinki` |
| 36 | polirovalnye-pasty | `/uk-verify-content polirovalnye-pasty` |
| 37 | polirovka | `/uk-verify-content polirovka` |
| 38 | pyatnovyvoditeli | `/uk-verify-content pyatnovyvoditeli` |
| 39 | raspyliteli-i-penniki | `/uk-verify-content raspyliteli-i-penniki` |

### Group 6: S-U categories (8)

| # | Slug | Task |
|---|------|------|
| 40 | shampuni-dlya-ruchnoy-moyki | `/uk-verify-content shampuni-dlya-ruchnoy-moyki` |
| 41 | shchetka-dlya-moyki-avto | `/uk-verify-content shchetka-dlya-moyki-avto` |
| 42 | silanty | `/uk-verify-content silanty` |
| 43 | sredstva-dlya-khimchistki-salona | `/uk-verify-content sredstva-dlya-khimchistki-salona` |
| 44 | sredstva-dlya-kozhi | `/uk-verify-content sredstva-dlya-kozhi` |
| 45 | tverdyy-vosk | `/uk-verify-content tverdyy-vosk` |
| 46 | ukhod-za-intererom | `/uk-verify-content ukhod-za-intererom` |
| 47 | ukhod-za-kozhey | `/uk-verify-content ukhod-za-kozhey` |

### Group 7: U-Z categories (5)

| # | Slug | Task |
|---|------|------|
| 48 | ukhod-za-naruzhnym-plastikom | `/uk-verify-content ukhod-za-naruzhnym-plastikom` |
| 49 | vedra-i-emkosti | `/uk-verify-content vedra-i-emkosti` |
| 50 | voski | `/uk-verify-content voski` |
| 51 | zashchitnye-pokrytiya | `/uk-verify-content zashchitnye-pokrytiya` |
| 52 | zhidkiy-vosk | `/uk-verify-content zhidkiy-vosk` |

---

## Progress Tracking

```
Total: 52 categories

[ ] Pre-flight: Commit uk-verify-content skill
[ ] Group 1 (8): akkumulyatornaya → apparaty-tornador
[ ] Group 2 (6): avtoshampuni → keramika-i-zhidkoe-steklo
[ ] Group 3 (7): kisti-dlya-deteylinga → nabory
[ ] Group 4 (10): neytralizatory-zapakha → omyvatel
[ ] Group 5 (8): opt-i-b2b → raspyliteli-i-penniki
[ ] Group 6 (8): shampuni-dlya-ruchnoy-moyki → ukhod-za-kozhey
[ ] Group 7 (5): ukhod-za-naruzhnym-plastikom → zhidkiy-vosk

Progress: 0/52
```

---

## Validation Thresholds (Quick Reference)

| Metric | Target | BLOCKER |
|--------|--------|---------|
| Title | 50-60 chars | <50 or >60 |
| Description | 120-160 chars | <120 or >160 |
| Stem density | ≤2.5% | >3.0% |
| Classic nausea | ≤3.5 | >4.0 |
| Academic | ≥7% | <6% |
| Water | 40-65% | >75% |
| Primary keyword | 3-7× | 0 or >10 |
| H2 with keyword | ≥2 | 0 |
| UK terminology | No RU terms | резина/мойка/стекло |

---

## Post-Audit

After all 52 categories verified:

**Step 1: Generate summary report**

```bash
echo "# UK Audit Summary $(date +%Y-%m-%d)" > uk/AUDIT_SUMMARY.md
echo "" >> uk/AUDIT_SUMMARY.md
for slug in uk/categories/*/; do
  name=$(basename "$slug")
  if [ -f "$slug/QUALITY_REPORT.md" ]; then
    status=$(grep -m1 "Status:" "$slug/QUALITY_REPORT.md" | cut -d: -f2)
    echo "- $name:$status" >> uk/AUDIT_SUMMARY.md
  else
    echo "- $name: NO REPORT" >> uk/AUDIT_SUMMARY.md
  fi
done
```

**Step 2: Final commit**

```bash
git add uk/
git commit -m "audit(uk): complete audit of 52 categories"
```

---

**Version:** 1.0
**Created:** 2026-01-26
