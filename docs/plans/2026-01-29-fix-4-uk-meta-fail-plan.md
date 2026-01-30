# Plan: Fix 4 UK Meta FAIL

**Design:** [2026-01-29-fix-4-uk-meta-fail-design.md](2026-01-29-fix-4-uk-meta-fail-design.md)

---

## Task 1: Fix ochistiteli-shin meta

**Files:**
- `uk/categories/ochistiteli-shin/meta/ochistiteli-shin_meta.json`

**Changes:**
- Description: "Очищувач шин" → "Очищувач гуми"

**Validation:**
```bash
python3 scripts/validate_meta.py uk/categories/ochistiteli-shin/meta/ochistiteli-shin_meta.json --keywords uk/categories/ochistiteli-shin/data/ochistiteli-shin_clean.json
```

**Expected:** PASS

---

## Task 2: Fix poliroli-dlya-plastika meta

**Files:**
- `uk/categories/poliroli-dlya-plastika/meta/poliroli-dlya-plastika_meta.json`

**Changes:**
- Title: "Поліроль для пластику авто" → "Поліроль для пластику"
- H1: "Поліроль для пластику авто" → "Поліроль для пластику"
- Description: already correct (no "авто")

**Validation:**
```bash
python3 scripts/validate_meta.py uk/categories/poliroli-dlya-plastika/meta/poliroli-dlya-plastika_meta.json --keywords uk/categories/poliroli-dlya-plastika/data/poliroli-dlya-plastika_clean.json
```

**Expected:** PASS

---

## Task 3: Fix raspyliteli-i-penniki meta

**Files:**
- `uk/categories/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json`

**Changes:**
- Title: "Піноутворювачі для миття авто" → "Розпилювач для води"
- H1: "Піноутворювач для миття" → "Розпилювач для води"
- Description: "Піноутворювачі для миття авто" → "Розпилювач для води"

**Validation:**
```bash
python3 scripts/validate_meta.py uk/categories/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json --keywords uk/categories/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json
```

**Expected:** PASS

---

## Task 4: Fix shchetka-dlya-moyki-avto meta

**Files:**
- `uk/categories/shchetka-dlya-moyki-avto/meta/shchetka-dlya-moyki-avto_meta.json`

**Changes:**
- Title: "Купити щітку для миття авто в Україні | Ultimate" → "Щітка для миття авто — купити в інтернет-магазині Ultimate"

**Validation:**
```bash
python3 scripts/validate_meta.py uk/categories/shchetka-dlya-moyki-avto/meta/shchetka-dlya-moyki-avto_meta.json --keywords uk/categories/shchetka-dlya-moyki-avto/data/shchetka-dlya-moyki-avto_clean.json
```

**Expected:** PASS

---

## Task 5: Final validation and commit

**Validation:**
```bash
python3 scripts/validate_meta.py --all
```

**Expected:** 0 FAIL (was 4)

**Commit:**
```bash
git add uk/categories/ochistiteli-shin/meta/ochistiteli-shin_meta.json \
        uk/categories/poliroli-dlya-plastika/meta/poliroli-dlya-plastika_meta.json \
        uk/categories/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json \
        uk/categories/shchetka-dlya-moyki-avto/meta/shchetka-dlya-moyki-avto_meta.json

git commit -m "fix(uk): align 4 UK meta files with primary_keyword from _clean.json

- ochistiteli-shin: Description очищувач шин → очищувач гуми
- poliroli-dlya-plastika: remove 'авто' from Title/H1
- raspyliteli-i-penniki: піноутворювач → розпилювач для води
- shchetka-dlya-moyki-avto: update Title to new formula

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

**Version:** 1.0
**Date:** 2026-01-29
