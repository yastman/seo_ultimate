# UK Full Pipeline: Meta + Content (Sequential)

> **For Claude:** Выполнять последовательно по одной категории. БЕЗ суб-агентов. После каждой категории — коммит и отметка в чеклисте.

**Goal:** Сгенерировать мета-теги и контент для 47 UK категорий с валидацией

**Architecture:** Sequential pipeline: meta → validate → content → review → quality-gate → commit → mark done

**Tech Stack:** UK skills (/uk-generate-meta, /uk-content-generator, uk-content-reviewer, /uk-quality-gate)

---

## Скиллы (Skills)

| Step | Skill | Тип | Описание |
|------|-------|-----|----------|
| 1 | `/uk-generate-meta` | slash command | Генерирует UK мета-теги (Title, Description, H1) |
| 2 | — | manual | Валидация мета (проверка длины, "Купити" в Title) |
| 3 | `/uk-content-generator` | slash command | Генерирует UK контент (buyer guide, 400-700 слов) |
| 4 | `uk-content-reviewer` | subagent | Проверяет и исправляет контент (SEO, тошнота) |
| 5 | `/uk-quality-gate` | slash command | Финальная валидация всех файлов |
| 6 | — | git | Коммит изменений |
| 7 | — | manual | Отметка в TODO_UK_CONTENT.md |

**Важно:**
- Скиллы со слэшем (`/`) — вызываются как команды
- Скилл без слэша (`uk-content-reviewer`) — это subagent, вызывается как Task
- Выполнять строго последовательно, без параллельных агентов

---

## Pipeline для каждой категории

```
Step 1: /uk-generate-meta {slug}
Step 2: Validate meta (Title 50-60, Description 120-160, H1 без "Купити")
Step 3: /uk-content-generator {slug}
Step 4: uk-content-reviewer {slug}
Step 5: /uk-quality-gate {slug}
Step 6: git commit
Step 7: Mark [x] in checklist below
```

---

## Category 1: antidozhd

**Files:**
- Meta: `uk/categories/antidozhd/meta/antidozhd_meta.json`
- Content: `uk/categories/antidozhd/content/antidozhd_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta antidozhd`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator antidozhd`
- [ ] **Step 4:** `uk-content-reviewer antidozhd`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate antidozhd`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/antidozhd/ && git commit -m "feat(uk): antidozhd - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 2: akkumulyatornaya

**Files:**
- Meta: `uk/categories/akkumulyatornaya/meta/akkumulyatornaya_meta.json`
- Content: `uk/categories/akkumulyatornaya/content/akkumulyatornaya_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta akkumulyatornaya`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator akkumulyatornaya`
- [ ] **Step 4:** `uk-content-reviewer akkumulyatornaya`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate akkumulyatornaya`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/akkumulyatornaya/ && git commit -m "feat(uk): akkumulyatornaya - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 3: cherniteli-shin

**Files:**
- Meta: `uk/categories/cherniteli-shin/meta/cherniteli-shin_meta.json`
- Content: `uk/categories/cherniteli-shin/content/cherniteli-shin_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta cherniteli-shin`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator cherniteli-shin`
- [ ] **Step 4:** `uk-content-reviewer cherniteli-shin`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate cherniteli-shin`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/cherniteli-shin/ && git commit -m "feat(uk): cherniteli-shin - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 4: glina-i-avtoskraby

**Files:**
- Meta: `uk/categories/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json`
- Content: `uk/categories/glina-i-avtoskraby/content/glina-i-avtoskraby_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta glina-i-avtoskraby`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator glina-i-avtoskraby`
- [ ] **Step 4:** `uk-content-reviewer glina-i-avtoskraby`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate glina-i-avtoskraby`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/glina-i-avtoskraby/ && git commit -m "feat(uk): glina-i-avtoskraby - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 5: gubki-i-varezhki

**Files:**
- Meta: `uk/categories/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json`
- Content: `uk/categories/gubki-i-varezhki/content/gubki-i-varezhki_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta gubki-i-varezhki`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator gubki-i-varezhki`
- [ ] **Step 4:** `uk-content-reviewer gubki-i-varezhki`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate gubki-i-varezhki`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/gubki-i-varezhki/ && git commit -m "feat(uk): gubki-i-varezhki - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 6: keramika-dlya-diskov

**Files:**
- Meta: `uk/categories/keramika-dlya-diskov/meta/keramika-dlya-diskov_meta.json`
- Content: `uk/categories/keramika-dlya-diskov/content/keramika-dlya-diskov_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta keramika-dlya-diskov`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator keramika-dlya-diskov`
- [ ] **Step 4:** `uk-content-reviewer keramika-dlya-diskov`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate keramika-dlya-diskov`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/keramika-dlya-diskov/ && git commit -m "feat(uk): keramika-dlya-diskov - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 7: kisti-dlya-deteylinga

**Files:**
- Meta: `uk/categories/kisti-dlya-deteylinga/meta/kisti-dlya-deteylinga_meta.json`
- Content: `uk/categories/kisti-dlya-deteylinga/content/kisti-dlya-deteylinga_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta kisti-dlya-deteylinga`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator kisti-dlya-deteylinga`
- [ ] **Step 4:** `uk-content-reviewer kisti-dlya-deteylinga`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate kisti-dlya-deteylinga`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/kisti-dlya-deteylinga/ && git commit -m "feat(uk): kisti-dlya-deteylinga - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 8: malyarniy-skotch

**Files:**
- Meta: `uk/categories/malyarniy-skotch/meta/malyarniy-skotch_meta.json`
- Content: `uk/categories/malyarniy-skotch/content/malyarniy-skotch_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta malyarniy-skotch`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator malyarniy-skotch`
- [ ] **Step 4:** `uk-content-reviewer malyarniy-skotch`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate malyarniy-skotch`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/malyarniy-skotch/ && git commit -m "feat(uk): malyarniy-skotch - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 9: mekhovye

**Files:**
- Meta: `uk/categories/mekhovye/meta/mekhovye_meta.json`
- Content: `uk/categories/mekhovye/content/mekhovye_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta mekhovye`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator mekhovye`
- [ ] **Step 4:** `uk-content-reviewer mekhovye`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate mekhovye`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/mekhovye/ && git commit -m "feat(uk): mekhovye - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 10: nabory

**Files:**
- Meta: `uk/categories/nabory/meta/nabory_meta.json`
- Content: `uk/categories/nabory/content/nabory_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta nabory`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator nabory`
- [ ] **Step 4:** `uk-content-reviewer nabory`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate nabory`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/nabory/ && git commit -m "feat(uk): nabory - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 11: neytralizatory-zapakha

**Files:**
- Meta: `uk/categories/neytralizatory-zapakha/meta/neytralizatory-zapakha_meta.json`
- Content: `uk/categories/neytralizatory-zapakha/content/neytralizatory-zapakha_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta neytralizatory-zapakha`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator neytralizatory-zapakha`
- [ ] **Step 4:** `uk-content-reviewer neytralizatory-zapakha`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate neytralizatory-zapakha`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/neytralizatory-zapakha/ && git commit -m "feat(uk): neytralizatory-zapakha - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 12: obezzhirivateli

**Files:**
- Meta: `uk/categories/obezzhirivateli/meta/obezzhirivateli_meta.json`
- Content: `uk/categories/obezzhirivateli/content/obezzhirivateli_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta obezzhirivateli`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator obezzhirivateli`
- [ ] **Step 4:** `uk-content-reviewer obezzhirivateli`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate obezzhirivateli`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/obezzhirivateli/ && git commit -m "feat(uk): obezzhirivateli - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 13: ochistiteli-diskov

**Files:**
- Meta: `uk/categories/ochistiteli-diskov/meta/ochistiteli-diskov_meta.json`
- Content: `uk/categories/ochistiteli-diskov/content/ochistiteli-diskov_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta ochistiteli-diskov`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator ochistiteli-diskov`
- [ ] **Step 4:** `uk-content-reviewer ochistiteli-diskov`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate ochistiteli-diskov`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/ochistiteli-diskov/ && git commit -m "feat(uk): ochistiteli-diskov - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 14: ochistiteli-dvigatelya

**Files:**
- Meta: `uk/categories/ochistiteli-dvigatelya/meta/ochistiteli-dvigatelya_meta.json`
- Content: `uk/categories/ochistiteli-dvigatelya/content/ochistiteli-dvigatelya_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta ochistiteli-dvigatelya`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator ochistiteli-dvigatelya`
- [ ] **Step 4:** `uk-content-reviewer ochistiteli-dvigatelya`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate ochistiteli-dvigatelya`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/ochistiteli-dvigatelya/ && git commit -m "feat(uk): ochistiteli-dvigatelya - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 15: ochistiteli-kozhi

**Files:**
- Meta: `uk/categories/ochistiteli-kozhi/meta/ochistiteli-kozhi_meta.json`
- Content: `uk/categories/ochistiteli-kozhi/content/ochistiteli-kozhi_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta ochistiteli-kozhi`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator ochistiteli-kozhi`
- [ ] **Step 4:** `uk-content-reviewer ochistiteli-kozhi`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate ochistiteli-kozhi`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/ochistiteli-kozhi/ && git commit -m "feat(uk): ochistiteli-kozhi - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 16: ochistiteli-shin

**Files:**
- Meta: `uk/categories/ochistiteli-shin/meta/ochistiteli-shin_meta.json`
- Content: `uk/categories/ochistiteli-shin/content/ochistiteli-shin_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta ochistiteli-shin`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator ochistiteli-shin`
- [ ] **Step 4:** `uk-content-reviewer ochistiteli-shin`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate ochistiteli-shin`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/ochistiteli-shin/ && git commit -m "feat(uk): ochistiteli-shin - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 17: ochistiteli-stekol

**Files:**
- Meta: `uk/categories/ochistiteli-stekol/meta/ochistiteli-stekol_meta.json`
- Content: `uk/categories/ochistiteli-stekol/content/ochistiteli-stekol_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta ochistiteli-stekol`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator ochistiteli-stekol`
- [ ] **Step 4:** `uk-content-reviewer ochistiteli-stekol`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate ochistiteli-stekol`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/ochistiteli-stekol/ && git commit -m "feat(uk): ochistiteli-stekol - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 18: omyvatel

**Files:**
- Meta: `uk/categories/omyvatel/meta/omyvatel_meta.json`
- Content: `uk/categories/omyvatel/content/omyvatel_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta omyvatel`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator omyvatel`
- [ ] **Step 4:** `uk-content-reviewer omyvatel`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate omyvatel`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/omyvatel/ && git commit -m "feat(uk): omyvatel - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 19: polirol-dlya-stekla

**Files:**
- Meta: `uk/categories/polirol-dlya-stekla/meta/polirol-dlya-stekla_meta.json`
- Content: `uk/categories/polirol-dlya-stekla/content/polirol-dlya-stekla_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta polirol-dlya-stekla`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator polirol-dlya-stekla`
- [ ] **Step 4:** `uk-content-reviewer polirol-dlya-stekla`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate polirol-dlya-stekla`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/polirol-dlya-stekla/ && git commit -m "feat(uk): polirol-dlya-stekla - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 20: poliroli-dlya-plastika

**Files:**
- Meta: `uk/categories/poliroli-dlya-plastika/meta/poliroli-dlya-plastika_meta.json`
- Content: `uk/categories/poliroli-dlya-plastika/content/poliroli-dlya-plastika_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta poliroli-dlya-plastika`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator poliroli-dlya-plastika`
- [ ] **Step 4:** `uk-content-reviewer poliroli-dlya-plastika`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate poliroli-dlya-plastika`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/poliroli-dlya-plastika/ && git commit -m "feat(uk): poliroli-dlya-plastika - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 21: polirovalnye-pasty

**Files:**
- Meta: `uk/categories/polirovalnye-pasty/meta/polirovalnye-pasty_meta.json`
- Content: `uk/categories/polirovalnye-pasty/content/polirovalnye-pasty_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta polirovalnye-pasty`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator polirovalnye-pasty`
- [ ] **Step 4:** `uk-content-reviewer polirovalnye-pasty`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate polirovalnye-pasty`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/polirovalnye-pasty/ && git commit -m "feat(uk): polirovalnye-pasty - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 22: pyatnovyvoditeli

**Files:**
- Meta: `uk/categories/pyatnovyvoditeli/meta/pyatnovyvoditeli_meta.json`
- Content: `uk/categories/pyatnovyvoditeli/content/pyatnovyvoditeli_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta pyatnovyvoditeli`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator pyatnovyvoditeli`
- [ ] **Step 4:** `uk-content-reviewer pyatnovyvoditeli`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate pyatnovyvoditeli`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/pyatnovyvoditeli/ && git commit -m "feat(uk): pyatnovyvoditeli - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 23: raspyliteli-i-penniki

**Files:**
- Meta: `uk/categories/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json`
- Content: `uk/categories/raspyliteli-i-penniki/content/raspyliteli-i-penniki_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta raspyliteli-i-penniki`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator raspyliteli-i-penniki`
- [ ] **Step 4:** `uk-content-reviewer raspyliteli-i-penniki`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate raspyliteli-i-penniki`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/raspyliteli-i-penniki/ && git commit -m "feat(uk): raspyliteli-i-penniki - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 24: shampuni-dlya-ruchnoy-moyki

**Files:**
- Meta: `uk/categories/shampuni-dlya-ruchnoy-moyki/meta/shampuni-dlya-ruchnoy-moyki_meta.json`
- Content: `uk/categories/shampuni-dlya-ruchnoy-moyki/content/shampuni-dlya-ruchnoy-moyki_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta shampuni-dlya-ruchnoy-moyki`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator shampuni-dlya-ruchnoy-moyki`
- [ ] **Step 4:** `uk-content-reviewer shampuni-dlya-ruchnoy-moyki`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate shampuni-dlya-ruchnoy-moyki`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/shampuni-dlya-ruchnoy-moyki/ && git commit -m "feat(uk): shampuni-dlya-ruchnoy-moyki - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 25: shchetka-dlya-moyki-avto

**Files:**
- Meta: `uk/categories/shchetka-dlya-moyki-avto/meta/shchetka-dlya-moyki-avto_meta.json`
- Content: `uk/categories/shchetka-dlya-moyki-avto/content/shchetka-dlya-moyki-avto_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta shchetka-dlya-moyki-avto`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator shchetka-dlya-moyki-avto`
- [ ] **Step 4:** `uk-content-reviewer shchetka-dlya-moyki-avto`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate shchetka-dlya-moyki-avto`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/shchetka-dlya-moyki-avto/ && git commit -m "feat(uk): shchetka-dlya-moyki-avto - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 26: silanty

**Files:**
- Meta: `uk/categories/silanty/meta/silanty_meta.json`
- Content: `uk/categories/silanty/content/silanty_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta silanty`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator silanty`
- [ ] **Step 4:** `uk-content-reviewer silanty`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate silanty`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/silanty/ && git commit -m "feat(uk): silanty - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 27: sredstva-dlya-khimchistki-salona

**Files:**
- Meta: `uk/categories/sredstva-dlya-khimchistki-salona/meta/sredstva-dlya-khimchistki-salona_meta.json`
- Content: `uk/categories/sredstva-dlya-khimchistki-salona/content/sredstva-dlya-khimchistki-salona_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta sredstva-dlya-khimchistki-salona`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator sredstva-dlya-khimchistki-salona`
- [ ] **Step 4:** `uk-content-reviewer sredstva-dlya-khimchistki-salona`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate sredstva-dlya-khimchistki-salona`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/sredstva-dlya-khimchistki-salona/ && git commit -m "feat(uk): sredstva-dlya-khimchistki-salona - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 28: tverdyy-vosk

**Files:**
- Meta: `uk/categories/tverdyy-vosk/meta/tverdyy-vosk_meta.json`
- Content: `uk/categories/tverdyy-vosk/content/tverdyy-vosk_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta tverdyy-vosk`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator tverdyy-vosk`
- [ ] **Step 4:** `uk-content-reviewer tverdyy-vosk`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate tverdyy-vosk`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/tverdyy-vosk/ && git commit -m "feat(uk): tverdyy-vosk - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 29: ukhod-za-kozhey

**Files:**
- Meta: `uk/categories/ukhod-za-kozhey/meta/ukhod-za-kozhey_meta.json`
- Content: `uk/categories/ukhod-za-kozhey/content/ukhod-za-kozhey_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta ukhod-za-kozhey`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator ukhod-za-kozhey`
- [ ] **Step 4:** `uk-content-reviewer ukhod-za-kozhey`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate ukhod-za-kozhey`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/ukhod-za-kozhey/ && git commit -m "feat(uk): ukhod-za-kozhey - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 30: ukhod-za-naruzhnym-plastikom

**Files:**
- Meta: `uk/categories/ukhod-za-naruzhnym-plastikom/meta/ukhod-za-naruzhnym-plastikom_meta.json`
- Content: `uk/categories/ukhod-za-naruzhnym-plastikom/content/ukhod-za-naruzhnym-plastikom_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta ukhod-za-naruzhnym-plastikom`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator ukhod-za-naruzhnym-plastikom`
- [ ] **Step 4:** `uk-content-reviewer ukhod-za-naruzhnym-plastikom`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate ukhod-za-naruzhnym-plastikom`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/ukhod-za-naruzhnym-plastikom/ && git commit -m "feat(uk): ukhod-za-naruzhnym-plastikom - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 31: vedra-i-emkosti

**Files:**
- Meta: `uk/categories/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json`
- Content: `uk/categories/vedra-i-emkosti/content/vedra-i-emkosti_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta vedra-i-emkosti`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator vedra-i-emkosti`
- [ ] **Step 4:** `uk-content-reviewer vedra-i-emkosti`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate vedra-i-emkosti`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/vedra-i-emkosti/ && git commit -m "feat(uk): vedra-i-emkosti - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 32: zhidkiy-vosk

**Files:**
- Meta: `uk/categories/zhidkiy-vosk/meta/zhidkiy-vosk_meta.json`
- Content: `uk/categories/zhidkiy-vosk/content/zhidkiy-vosk_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta zhidkiy-vosk`
- [ ] **Step 2:** Validate meta
  - [ ] Title: 50-60 chars, містить "Купити"
  - [ ] Description: 120-160 chars
  - [ ] H1: БЕЗ "Купити"
- [ ] **Step 3:** `/uk-content-generator zhidkiy-vosk`
- [ ] **Step 4:** `uk-content-reviewer zhidkiy-vosk`
  - [ ] Word count: 400-700
  - [ ] H2 з ключовим словом: ≥2
  - [ ] Stem-група: ≤2.5%
- [ ] **Step 5:** `/uk-quality-gate zhidkiy-vosk`
- [ ] **Step 6:** Commit
  ```bash
  git add uk/categories/zhidkiy-vosk/ && git commit -m "feat(uk): zhidkiy-vosk - meta + content"
  ```
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## L2 Categories (8)

---

## Category 33: aksessuary-dlya-naneseniya-sredstv

**Files:**
- Meta: `uk/categories/aksessuary-dlya-naneseniya-sredstv/meta/aksessuary-dlya-naneseniya-sredstv_meta.json`
- Content: `uk/categories/aksessuary-dlya-naneseniya-sredstv/content/aksessuary-dlya-naneseniya-sredstv_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta aksessuary-dlya-naneseniya-sredstv`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator aksessuary-dlya-naneseniya-sredstv`
- [ ] **Step 4:** `uk-content-reviewer aksessuary-dlya-naneseniya-sredstv`
- [ ] **Step 5:** `/uk-quality-gate aksessuary-dlya-naneseniya-sredstv`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 34: apparaty-tornador

**Files:**
- Meta: `uk/categories/apparaty-tornador/meta/apparaty-tornador_meta.json`
- Content: `uk/categories/apparaty-tornador/content/apparaty-tornador_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta apparaty-tornador`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator apparaty-tornador`
- [ ] **Step 4:** `uk-content-reviewer apparaty-tornador`
- [ ] **Step 5:** `/uk-quality-gate apparaty-tornador`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 35: avtoshampuni

**Files:**
- Meta: `uk/categories/avtoshampuni/meta/avtoshampuni_meta.json`
- Content: `uk/categories/avtoshampuni/content/avtoshampuni_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta avtoshampuni`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator avtoshampuni`
- [ ] **Step 4:** `uk-content-reviewer avtoshampuni`
- [ ] **Step 5:** `/uk-quality-gate avtoshampuni`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 36: keramika-i-zhidkoe-steklo

**Files:**
- Meta: `uk/categories/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json`
- Content: `uk/categories/keramika-i-zhidkoe-steklo/content/keramika-i-zhidkoe-steklo_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta keramika-i-zhidkoe-steklo`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator keramika-i-zhidkoe-steklo`
- [ ] **Step 4:** `uk-content-reviewer keramika-i-zhidkoe-steklo`
- [ ] **Step 5:** `/uk-quality-gate keramika-i-zhidkoe-steklo`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 37: kvik-deteylery

**Files:**
- Meta: `uk/categories/kvik-deteylery/meta/kvik-deteylery_meta.json`
- Content: `uk/categories/kvik-deteylery/content/kvik-deteylery_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta kvik-deteylery`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator kvik-deteylery`
- [ ] **Step 4:** `uk-content-reviewer kvik-deteylery`
- [ ] **Step 5:** `/uk-quality-gate kvik-deteylery`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 38: mikrofibra-i-tryapki

**Files:**
- Meta: `uk/categories/mikrofibra-i-tryapki/meta/mikrofibra-i-tryapki_meta.json`
- Content: `uk/categories/mikrofibra-i-tryapki/content/mikrofibra-i-tryapki_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta mikrofibra-i-tryapki`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator mikrofibra-i-tryapki`
- [ ] **Step 4:** `uk-content-reviewer mikrofibra-i-tryapki`
- [ ] **Step 5:** `/uk-quality-gate mikrofibra-i-tryapki`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 39: sredstva-dlya-kozhi

**Files:**
- Meta: `uk/categories/sredstva-dlya-kozhi/meta/sredstva-dlya-kozhi_meta.json`
- Content: `uk/categories/sredstva-dlya-kozhi/content/sredstva-dlya-kozhi_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta sredstva-dlya-kozhi`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator sredstva-dlya-kozhi`
- [ ] **Step 4:** `uk-content-reviewer sredstva-dlya-kozhi`
- [ ] **Step 5:** `/uk-quality-gate sredstva-dlya-kozhi`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 40: voski

**Files:**
- Meta: `uk/categories/voski/meta/voski_meta.json`
- Content: `uk/categories/voski/content/voski_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta voski`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator voski`
- [ ] **Step 4:** `uk-content-reviewer voski`
- [ ] **Step 5:** `/uk-quality-gate voski`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## L1 Categories (7)

---

## Category 41: aksessuary

**Files:**
- Meta: `uk/categories/aksessuary/meta/aksessuary_meta.json`
- Content: `uk/categories/aksessuary/content/aksessuary_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta aksessuary`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator aksessuary`
- [ ] **Step 4:** `uk-content-reviewer aksessuary`
- [ ] **Step 5:** `/uk-quality-gate aksessuary`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 42: moyka-i-eksterer

**Files:**
- Meta: `uk/categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json`
- Content: `uk/categories/moyka-i-eksterer/content/moyka-i-eksterer_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta moyka-i-eksterer`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator moyka-i-eksterer`
- [ ] **Step 4:** `uk-content-reviewer moyka-i-eksterer`
- [ ] **Step 5:** `/uk-quality-gate moyka-i-eksterer`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 43: oborudovanie

**Files:**
- Meta: `uk/categories/oborudovanie/meta/oborudovanie_meta.json`
- Content: `uk/categories/oborudovanie/content/oborudovanie_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta oborudovanie`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator oborudovanie`
- [ ] **Step 4:** `uk-content-reviewer oborudovanie`
- [ ] **Step 5:** `/uk-quality-gate oborudovanie`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 44: opt-i-b2b

**Files:**
- Meta: `uk/categories/opt-i-b2b/meta/opt-i-b2b_meta.json`
- Content: `uk/categories/opt-i-b2b/content/opt-i-b2b_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta opt-i-b2b`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator opt-i-b2b`
- [ ] **Step 4:** `uk-content-reviewer opt-i-b2b`
- [ ] **Step 5:** `/uk-quality-gate opt-i-b2b`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 45: polirovka

**Files:**
- Meta: `uk/categories/polirovka/meta/polirovka_meta.json`
- Content: `uk/categories/polirovka/content/polirovka_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta polirovka`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator polirovka`
- [ ] **Step 4:** `uk-content-reviewer polirovka`
- [ ] **Step 5:** `/uk-quality-gate polirovka`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 46: ukhod-za-intererom

**Files:**
- Meta: `uk/categories/ukhod-za-intererom/meta/ukhod-za-intererom_meta.json`
- Content: `uk/categories/ukhod-za-intererom/content/ukhod-za-intererom_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta ukhod-za-intererom`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator ukhod-za-intererom`
- [ ] **Step 4:** `uk-content-reviewer ukhod-za-intererom`
- [ ] **Step 5:** `/uk-quality-gate ukhod-za-intererom`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Category 47: zashchitnye-pokrytiya

**Files:**
- Meta: `uk/categories/zashchitnye-pokrytiya/meta/zashchitnye-pokrytiya_meta.json`
- Content: `uk/categories/zashchitnye-pokrytiya/content/zashchitnye-pokrytiya_uk.md`

### Checklist:

- [ ] **Step 1:** `/uk-generate-meta zashchitnye-pokrytiya`
- [ ] **Step 2:** Validate meta
- [ ] **Step 3:** `/uk-content-generator zashchitnye-pokrytiya`
- [ ] **Step 4:** `uk-content-reviewer zashchitnye-pokrytiya`
- [ ] **Step 5:** `/uk-quality-gate zashchitnye-pokrytiya`
- [ ] **Step 6:** Commit
- [ ] **Step 7:** Mark `[x]` in TODO_UK_CONTENT.md

---

## Final Acceptance Criteria

- [ ] 47/47 категорій оброблено
- [ ] 47/47 чеклістів виконано повністю
- [ ] TODO_UK_CONTENT.md: всі `[~]` → `[x]`
- [ ] Progress: 50/50

---

## Progress Summary

| Group | Total | Done |
|-------|-------|------|
| L3 Categories | 32 | 0 |
| L2 Categories | 8 | 0 |
| L1 Categories | 7 | 0 |
| **TOTAL** | **47** | **0** |
