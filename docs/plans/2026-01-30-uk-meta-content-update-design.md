# UK Meta & Content Update — Design Document

**Date:** 2026-01-30
**Task:** Update meta tags and content for all 53 UK categories after keyword refresh

---

## Problem

New keywords were distributed to UK categories (commit `97fbced`). Meta tags and content now need updating to reflect the new semantic data.

**Affected files:**
- 50 `uk/categories/{slug}/data/{slug}_clean.json` — already updated
- 53 `uk/categories/{slug}/meta/{slug}_meta.json` — need regeneration
- 53 `uk/categories/{slug}/content/{slug}_uk.md` — need review/fixes

---

## Blockers

Skills reference renamed scripts:

| Skill | Old Script | New Script |
|-------|------------|------------|
| `uk-content-reviewer` | `check_keyword_density.py` | `validate_density.py` |
| `uk-content-reviewer` | `check_seo_structure.py` | `validate_seo.py` |
| `uk-content-generator` | `check_keyword_density.py` | `validate_density.py` |
| `content-reviewer` | `check_keyword_density.py` | `validate_density.py` |
| `content-reviewer` | `check_seo_structure.py` | `validate_seo.py` |
| `content-generator` | `check_keyword_density.py` | `validate_density.py` |
| `shared/validation-checklist.md` | `check_keyword_density.py` | `validate_density.py` |
| `shared/validation-checklist.md` | `check_seo_structure.py` | `validate_seo.py` |

---

## Solution

### Phase 0: Fix Skills (prerequisite)

Update all skills with correct script names using `/skill-creator`.

**Files to update:**
1. `.claude/skills/uk-content-reviewer/SKILL.md`
2. `.claude/skills/uk-content-generator/skill.md`
3. `.claude/skills/content-reviewer/SKILL.md`
4. `.claude/skills/content-generator/skill.md`
5. `.claude/skills/shared/validation-checklist.md`

**Changes:**
- `check_keyword_density.py` → `validate_density.py`
- `check_seo_structure.py` → `validate_seo.py`

### Phase 1: Parallel Processing (4 workers)

Split 53 categories among 4 workers (~13 each).

**Worker assignment:**

| Worker | Categories (13-14 each) |
|--------|-------------------------|
| W1 | akkumulyatornaya, aksessuary, aksessuary-dlya-naneseniya-sredstv, aktivnaya-pena, antibitum, antidozhd, antimoshka, apparaty-tornador, avtoshampuni, cherniteli-shin, glavnaya, glina-i-avtoskraby, gubki-i-varezhki |
| W2 | keramika-dlya-diskov, keramika-i-zhidkoe-steklo, kisti-dlya-deteylinga, kvik-deteylery, malyarniy-skotch, mekhovye, mikrofibra-i-tryapki, moyka-i-eksterer, nabory, neytralizatory-zapakha, obezzhirivateli, oborudovanie, ochistiteli-diskov |
| W3 | ochistiteli-dvigatelya, ochistiteli-kozhi, ochistiteli-kuzova, ochistiteli-shin, ochistiteli-stekol, omyvatel, opt-i-b2b, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-mashinki, polirovalnye-pasty, polirovka, pyatnovyvoditeli |
| W4 | raspyliteli-i-penniki, shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto, silanty, sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi, tverdyy-vosk, ukhod-za-intererom, ukhod-za-kozhey, ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, voski, zashchitnye-pokrytiya, zhidkiy-vosk |

**Per-category workflow:**
1. `/uk-generate-meta {slug}` — regenerate meta based on new keywords
2. `uk-content-reviewer {slug}` — review and fix content

**Worker output:**
- Log file: `data/generated/audit-logs/W{N}_uk_update_log.md`
- No git commits (orchestrator commits)

---

## Category List (53 total)

```
akkumulyatornaya
aksessuary
aksessuary-dlya-naneseniya-sredstv
aktivnaya-pena
antibitum
antidozhd
antimoshka
apparaty-tornador
avtoshampuni
cherniteli-shin
glavnaya
glina-i-avtoskraby
gubki-i-varezhki
keramika-dlya-diskov
keramika-i-zhidkoe-steklo
kisti-dlya-deteylinga
kvik-deteylery
malyarniy-skotch
mekhovye
mikrofibra-i-tryapki
moyka-i-eksterer
nabory
neytralizatory-zapakha
obezzhirivateli
oborudovanie
ochistiteli-diskov
ochistiteli-dvigatelya
ochistiteli-kozhi
ochistiteli-kuzova
ochistiteli-shin
ochistiteli-stekol
omyvatel
opt-i-b2b
polirol-dlya-stekla
poliroli-dlya-plastika
polirovalnye-mashinki
polirovalnye-pasty
polirovka
pyatnovyvoditeli
raspyliteli-i-penniki
shampuni-dlya-ruchnoy-moyki
shchetka-dlya-moyki-avto
silanty
sredstva-dlya-khimchistki-salona
sredstva-dlya-kozhi
tverdyy-vosk
ukhod-za-intererom
ukhod-za-kozhey
ukhod-za-naruzhnym-plastikom
vedra-i-emkosti
voski
zashchitnye-pokrytiya
zhidkiy-vosk
```

---

## Execution Order

1. **Phase 0:** Fix skills (orchestrator, sequential)
2. **Phase 1:** Launch 4 workers in parallel
3. **Phase 2:** Orchestrator reviews logs, commits changes

---

## Success Criteria

- [ ] All skills updated with correct script names
- [ ] All 53 `_meta.json` files pass `validate_meta.py`
- [ ] All 53 `_uk.md` files pass validators
- [ ] Worker logs show no BLOCKERs remaining
- [ ] Single commit with all changes

---

## Risks

| Risk | Mitigation |
|------|------------|
| Worker file conflicts | Each worker has exclusive category set |
| Skill not reloaded | Skills load dynamically on each call |
| Content needs REWRITE | Worker handles per `uk-content-reviewer` logic |

---

**Version:** 1.0
