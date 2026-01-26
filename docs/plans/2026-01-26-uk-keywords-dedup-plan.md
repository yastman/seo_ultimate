# UK Keywords Deduplication — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `/semantic-cluster {slug}` for each category. Execute task-by-task without subagents.

**Goal:** Кластеризувати ключі 52 UK категорій — перенести варіанти словоформ в synonyms.

**Architecture:** Для кожної категорії: прочитати _clean.json → знайти дублі по стемах → перенести в synonyms → оновити _meta.json → коміт.

**Tech Stack:** Edit tool, `/semantic-cluster` skill, `validate_meta.py`

**Design:** [2026-01-26-uk-keywords-dedup-design.md](2026-01-26-uk-keywords-dedup-design.md)

---

## Pre-flight

**Step 1: Verify skill exists**

```bash
ls .claude/skills/semantic-cluster/SKILL.md
```

Expected: file exists

**Step 2: Verify UK categories count**

```bash
ls -d uk/categories/*/ | wc -l
```

Expected: 52

---

## Group 1: A-categories (8)

### Task 1: akkumulyatornaya

**Files:**
- Read: `uk/categories/akkumulyatornaya/data/akkumulyatornaya_clean.json`
- Read: `uk/categories/akkumulyatornaya/meta/akkumulyatornaya_meta.json`

**Step 1: Read _clean.json, identify duplicates by stem**

Look for:
- машина/машинка variants
- купити/ціна modifiers
- singular/plural duplicates

**Step 2: Move variants to synonyms**

Add `use_in: "lsi"` and `variant_of` to moved keywords.

**Step 3: Update _meta.json keywords_in_content if needed**

Remove variants from primary/secondary/supporting, keep only canonical.

**Step 4: Validate**

```bash
python3 scripts/validate_meta.py uk/categories/akkumulyatornaya/meta/akkumulyatornaya_meta.json
```

Expected: PASS

**Step 5: Commit**

```bash
git add uk/categories/akkumulyatornaya/
git commit -m "cluster(uk): akkumulyatornaya — move variants to synonyms"
```

---

### Task 2: aksessuary

**Files:**
- Read: `uk/categories/aksessuary/data/aksessuary_clean.json`
- Read: `uk/categories/aksessuary/meta/aksessuary_meta.json`

**Steps:** Same as Task 1

**Commit:**
```bash
git add uk/categories/aksessuary/
git commit -m "cluster(uk): aksessuary — move variants to synonyms"
```

---

### Task 3: aksessuary-dlya-naneseniya-sredstv

**Files:**
- Read: `uk/categories/aksessuary-dlya-naneseniya-sredstv/data/aksessuary-dlya-naneseniya-sredstv_clean.json`
- Read: `uk/categories/aksessuary-dlya-naneseniya-sredstv/meta/aksessuary-dlya-naneseniya-sredstv_meta.json`

**Steps:** Same as Task 1

**Commit:**
```bash
git add uk/categories/aksessuary-dlya-naneseniya-sredstv/
git commit -m "cluster(uk): aksessuary-dlya-naneseniya-sredstv — move variants to synonyms"
```

---

### Task 4: aktivnaya-pena

**Files:**
- Read: `uk/categories/aktivnaya-pena/data/aktivnaya-pena_clean.json`
- Read: `uk/categories/aktivnaya-pena/meta/aktivnaya-pena_meta.json`

**Steps:** Same as Task 1

**Commit:**
```bash
git add uk/categories/aktivnaya-pena/
git commit -m "cluster(uk): aktivnaya-pena — move variants to synonyms"
```

---

### Task 5: antibitum

**Files:**
- Read: `uk/categories/antibitum/data/antibitum_clean.json`
- Read: `uk/categories/antibitum/meta/antibitum_meta.json`

**Steps:** Same as Task 1

**Commit:**
```bash
git add uk/categories/antibitum/
git commit -m "cluster(uk): antibitum — move variants to synonyms"
```

---

### Task 6: antidozhd

**Files:**
- Read: `uk/categories/antidozhd/data/antidozhd_clean.json`
- Read: `uk/categories/antidozhd/meta/antidozhd_meta.json`

**Steps:** Same as Task 1

**Commit:**
```bash
git add uk/categories/antidozhd/
git commit -m "cluster(uk): antidozhd — move variants to synonyms"
```

---

### Task 7: antimoshka

**Files:**
- Read: `uk/categories/antimoshka/data/antimoshka_clean.json`
- Read: `uk/categories/antimoshka/meta/antimoshka_meta.json`

**Steps:** Same as Task 1

**Commit:**
```bash
git add uk/categories/antimoshka/
git commit -m "cluster(uk): antimoshka — move variants to synonyms"
```

---

### Task 8: apparaty-tornador

**Files:**
- Read: `uk/categories/apparaty-tornador/data/apparaty-tornador_clean.json`
- Read: `uk/categories/apparaty-tornador/meta/apparaty-tornador_meta.json`

**Steps:** Same as Task 1

**Commit:**
```bash
git add uk/categories/apparaty-tornador/
git commit -m "cluster(uk): apparaty-tornador — move variants to synonyms"
```

---

## Group 2: A-K categories (6)

### Task 9: avtoshampuni

**Files:**
- Read: `uk/categories/avtoshampuni/data/avtoshampuni_clean.json`
- Read: `uk/categories/avtoshampuni/meta/avtoshampuni_meta.json`

**Commit:**
```bash
git add uk/categories/avtoshampuni/
git commit -m "cluster(uk): avtoshampuni — move variants to synonyms"
```

---

### Task 10: cherniteli-shin

**Files:**
- Read: `uk/categories/cherniteli-shin/data/cherniteli-shin_clean.json`
- Read: `uk/categories/cherniteli-shin/meta/cherniteli-shin_meta.json`

**Commit:**
```bash
git add uk/categories/cherniteli-shin/
git commit -m "cluster(uk): cherniteli-shin — move variants to synonyms"
```

---

### Task 11: glina-i-avtoskraby

**Files:**
- Read: `uk/categories/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json`
- Read: `uk/categories/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json`

**Commit:**
```bash
git add uk/categories/glina-i-avtoskraby/
git commit -m "cluster(uk): glina-i-avtoskraby — move variants to synonyms"
```

---

### Task 12: gubki-i-varezhki

**Files:**
- Read: `uk/categories/gubki-i-varezhki/data/gubki-i-varezhki_clean.json`
- Read: `uk/categories/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json`

**Commit:**
```bash
git add uk/categories/gubki-i-varezhki/
git commit -m "cluster(uk): gubki-i-varezhki — move variants to synonyms"
```

---

### Task 13: keramika-dlya-diskov

**Files:**
- Read: `uk/categories/keramika-dlya-diskov/data/keramika-dlya-diskov_clean.json`
- Read: `uk/categories/keramika-dlya-diskov/meta/keramika-dlya-diskov_meta.json`

**Commit:**
```bash
git add uk/categories/keramika-dlya-diskov/
git commit -m "cluster(uk): keramika-dlya-diskov — move variants to synonyms"
```

---

### Task 14: keramika-i-zhidkoe-steklo

**Files:**
- Read: `uk/categories/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json`
- Read: `uk/categories/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json`

**Commit:**
```bash
git add uk/categories/keramika-i-zhidkoe-steklo/
git commit -m "cluster(uk): keramika-i-zhidkoe-steklo — move variants to synonyms"
```

---

## Group 3: K-N categories (7)

### Task 15: kisti-dlya-deteylinga

**Commit:**
```bash
git add uk/categories/kisti-dlya-deteylinga/
git commit -m "cluster(uk): kisti-dlya-deteylinga — move variants to synonyms"
```

---

### Task 16: kvik-deteylery

**Commit:**
```bash
git add uk/categories/kvik-deteylery/
git commit -m "cluster(uk): kvik-deteylery — move variants to synonyms"
```

---

### Task 17: malyarniy-skotch

**Commit:**
```bash
git add uk/categories/malyarniy-skotch/
git commit -m "cluster(uk): malyarniy-skotch — move variants to synonyms"
```

---

### Task 18: mekhovye

**Commit:**
```bash
git add uk/categories/mekhovye/
git commit -m "cluster(uk): mekhovye — move variants to synonyms"
```

---

### Task 19: mikrofibra-i-tryapki

**Commit:**
```bash
git add uk/categories/mikrofibra-i-tryapki/
git commit -m "cluster(uk): mikrofibra-i-tryapki — move variants to synonyms"
```

---

### Task 20: moyka-i-eksterer

**Commit:**
```bash
git add uk/categories/moyka-i-eksterer/
git commit -m "cluster(uk): moyka-i-eksterer — move variants to synonyms"
```

---

### Task 21: nabory

**Commit:**
```bash
git add uk/categories/nabory/
git commit -m "cluster(uk): nabory — move variants to synonyms"
```

---

## Group 4: N-O categories (10)

### Task 22: neytralizatory-zapakha

**Commit:**
```bash
git add uk/categories/neytralizatory-zapakha/
git commit -m "cluster(uk): neytralizatory-zapakha — move variants to synonyms"
```

---

### Task 23: obezzhirivateli

**Commit:**
```bash
git add uk/categories/obezzhirivateli/
git commit -m "cluster(uk): obezzhirivateli — move variants to synonyms"
```

---

### Task 24: oborudovanie

**Commit:**
```bash
git add uk/categories/oborudovanie/
git commit -m "cluster(uk): oborudovanie — move variants to synonyms"
```

---

### Task 25: ochistiteli-diskov

**Commit:**
```bash
git add uk/categories/ochistiteli-diskov/
git commit -m "cluster(uk): ochistiteli-diskov — move variants to synonyms"
```

---

### Task 26: ochistiteli-dvigatelya

**Commit:**
```bash
git add uk/categories/ochistiteli-dvigatelya/
git commit -m "cluster(uk): ochistiteli-dvigatelya — move variants to synonyms"
```

---

### Task 27: ochistiteli-kozhi

**Commit:**
```bash
git add uk/categories/ochistiteli-kozhi/
git commit -m "cluster(uk): ochistiteli-kozhi — move variants to synonyms"
```

---

### Task 28: ochistiteli-kuzova

**Commit:**
```bash
git add uk/categories/ochistiteli-kuzova/
git commit -m "cluster(uk): ochistiteli-kuzova — move variants to synonyms"
```

---

### Task 29: ochistiteli-shin

**Commit:**
```bash
git add uk/categories/ochistiteli-shin/
git commit -m "cluster(uk): ochistiteli-shin — move variants to synonyms"
```

---

### Task 30: ochistiteli-stekol

**Commit:**
```bash
git add uk/categories/ochistiteli-stekol/
git commit -m "cluster(uk): ochistiteli-stekol — move variants to synonyms"
```

---

### Task 31: omyvatel

**Commit:**
```bash
git add uk/categories/omyvatel/
git commit -m "cluster(uk): omyvatel — move variants to synonyms"
```

---

## Group 5: O-R categories (8)

### Task 32: opt-i-b2b

**Commit:**
```bash
git add uk/categories/opt-i-b2b/
git commit -m "cluster(uk): opt-i-b2b — move variants to synonyms"
```

---

### Task 33: polirol-dlya-stekla

**Commit:**
```bash
git add uk/categories/polirol-dlya-stekla/
git commit -m "cluster(uk): polirol-dlya-stekla — move variants to synonyms"
```

---

### Task 34: poliroli-dlya-plastika

**Commit:**
```bash
git add uk/categories/poliroli-dlya-plastika/
git commit -m "cluster(uk): poliroli-dlya-plastika — move variants to synonyms"
```

---

### Task 35: polirovalnye-mashinki

**Commit:**
```bash
git add uk/categories/polirovalnye-mashinki/
git commit -m "cluster(uk): polirovalnye-mashinki — move variants to synonyms"
```

---

### Task 36: polirovalnye-pasty

**Commit:**
```bash
git add uk/categories/polirovalnye-pasty/
git commit -m "cluster(uk): polirovalnye-pasty — move variants to synonyms"
```

---

### Task 37: polirovka

**Commit:**
```bash
git add uk/categories/polirovka/
git commit -m "cluster(uk): polirovka — move variants to synonyms"
```

---

### Task 38: pyatnovyvoditeli

**Commit:**
```bash
git add uk/categories/pyatnovyvoditeli/
git commit -m "cluster(uk): pyatnovyvoditeli — move variants to synonyms"
```

---

### Task 39: raspyliteli-i-penniki

**Commit:**
```bash
git add uk/categories/raspyliteli-i-penniki/
git commit -m "cluster(uk): raspyliteli-i-penniki — move variants to synonyms"
```

---

## Group 6: S-U categories (8)

### Task 40: shampuni-dlya-ruchnoy-moyki

**Commit:**
```bash
git add uk/categories/shampuni-dlya-ruchnoy-moyki/
git commit -m "cluster(uk): shampuni-dlya-ruchnoy-moyki — move variants to synonyms"
```

---

### Task 41: shchetka-dlya-moyki-avto

**Commit:**
```bash
git add uk/categories/shchetka-dlya-moyki-avto/
git commit -m "cluster(uk): shchetka-dlya-moyki-avto — move variants to synonyms"
```

---

### Task 42: silanty

**Commit:**
```bash
git add uk/categories/silanty/
git commit -m "cluster(uk): silanty — move variants to synonyms"
```

---

### Task 43: sredstva-dlya-khimchistki-salona

**Commit:**
```bash
git add uk/categories/sredstva-dlya-khimchistki-salona/
git commit -m "cluster(uk): sredstva-dlya-khimchistki-salona — move variants to synonyms"
```

---

### Task 44: sredstva-dlya-kozhi

**Commit:**
```bash
git add uk/categories/sredstva-dlya-kozhi/
git commit -m "cluster(uk): sredstva-dlya-kozhi — move variants to synonyms"
```

---

### Task 45: tverdyy-vosk

**Commit:**
```bash
git add uk/categories/tverdyy-vosk/
git commit -m "cluster(uk): tverdyy-vosk — move variants to synonyms"
```

---

### Task 46: ukhod-za-intererom

**Commit:**
```bash
git add uk/categories/ukhod-za-intererom/
git commit -m "cluster(uk): ukhod-za-intererom — move variants to synonyms"
```

---

### Task 47: ukhod-za-kozhey

**Commit:**
```bash
git add uk/categories/ukhod-za-kozhey/
git commit -m "cluster(uk): ukhod-za-kozhey — move variants to synonyms"
```

---

## Group 7: U-Z categories (5)

### Task 48: ukhod-za-naruzhnym-plastikom

**Commit:**
```bash
git add uk/categories/ukhod-za-naruzhnym-plastikom/
git commit -m "cluster(uk): ukhod-za-naruzhnym-plastikom — move variants to synonyms"
```

---

### Task 49: vedra-i-emkosti

**Commit:**
```bash
git add uk/categories/vedra-i-emkosti/
git commit -m "cluster(uk): vedra-i-emkosti — move variants to synonyms"
```

---

### Task 50: voski

**Commit:**
```bash
git add uk/categories/voski/
git commit -m "cluster(uk): voski — move variants to synonyms"
```

---

### Task 51: zashchitnye-pokrytiya

**Commit:**
```bash
git add uk/categories/zashchitnye-pokrytiya/
git commit -m "cluster(uk): zashchitnye-pokrytiya — move variants to synonyms"
```

---

### Task 52: zhidkiy-vosk

**Commit:**
```bash
git add uk/categories/zhidkiy-vosk/
git commit -m "cluster(uk): zhidkiy-vosk — move variants to synonyms"
```

---

## Post-Execution

### Validation

```bash
# Verify all categories processed
for slug in uk/categories/*/; do
  name=$(basename "$slug")
  if [ -f "$slug/data/${name}_clean.json" ]; then
    synonyms=$(python3 -c "import json; d=json.load(open('$slug/data/${name}_clean.json')); print(len(d.get('synonyms',[])))")
    echo "$name: $synonyms synonyms"
  fi
done
```

### Summary commit

```bash
git log --oneline -60 | grep "cluster(uk)" | wc -l
# Expected: 52 commits
```

---

## Progress Tracking

```
[ ] Pre-flight verified
[ ] Group 1: 0/8 (akkumulyatornaya → apparaty-tornador)
[ ] Group 2: 0/6 (avtoshampuni → keramika-i-zhidkoe-steklo)
[ ] Group 3: 0/7 (kisti-dlya-deteylinga → nabory)
[ ] Group 4: 0/10 (neytralizatory-zapakha → omyvatel)
[ ] Group 5: 0/8 (opt-i-b2b → raspyliteli-i-penniki)
[ ] Group 6: 0/8 (shampuni-dlya-ruchnoy-moyki → ukhod-za-kozhey)
[ ] Group 7: 0/5 (ukhod-za-naruzhnym-plastikom → zhidkiy-vosk)

Total: 0/52
```

---

**Version:** 1.0
**Created:** 2026-01-26
