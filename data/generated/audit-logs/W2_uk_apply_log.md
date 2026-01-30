# W2: UK Keywords Apply Log

**Source:** `data/generated/uk_apply_W2.json`
**Worker:** W2 (Полірування)
**Date:** 2026-01-30

---

## polirovka

- Added: "полірувальні круги" (320)
- Added: "круг для полірування авто" (170)
- Added: "полірувальні круги для авто" (140)
- Added: "круги для полірування" (110)
- Skipped (exists): "полірування авто своїми руками" (90)
- Skipped (exists): "полірування кузова" (70)
- Skipped (exists): "полірування автомобіля" (50)
- Added: "купити полірувальні круги" (40)
- Added: "диск для полірування авто" (10)

**Result:** 6 added, 3 skipped

---

## polirovalnye-pasty

- Added: "пасти для полірування авто" (880)
- Added: "полірувальна паста для авто" (480)
- Added: "паста авто" (110)
- Added: "паста для полірування" (110)
- Added: "купити полірувальну пасту для авто" (70)
- Added: "купити полірувальну пасту" (40)
- Added: "набір паст для полірування авто" (30)
- Added: "купити пасту для полірування авто" (20)

**Result:** 8 added, 0 skipped

---

## polirovalnye-mashinki

- Added: "полірувальна машина для авто" (590)
- Added: "машинка для полірування авто" (390)
- Added: "полірувальна машинка для автомобіля" (320)
- Added: "купити полірувальну машинку" (320)
- Added: "купити полірувальну машинку для авто" (260)
- Added: "полірувальні машини" (110)
- Added: "машинка для полірування" (110)
- Added: "купити полірувальну машину" (70)
- Added: "купити машинку для полірування авто" (50)
- Added: "купити полірувальну машинку для автомобіля" (40)
- Added: "машина для полірування авто" (20)
- Added: "полірувальні машинки для авто" (10)
- Added: "машина для полірування" (10)

**Result:** 13 added, 0 skipped

---

## akkumulyatornaya

- Updated: "акумуляторна полірувальна машина" (260→320)
- Moved to keywords: "акумуляторна полірувальна машина для авто" (90)
- Added: "полірувальна машина для авто на акумуляторі" (70)

**Result:** 1 added, 2 restructured (moved from secondary/supporting to keywords)

---

## mekhovye

- Added: "диск полірувальний" (20)
- Added: "диски для полірування" (20)
- Skipped (exists): "wool pad" (10)
- Added: "диск для полірування авто" (10)
- Skipped (duplicate in list): 2 duplicates removed

**Result:** 3 added, 1 skipped

---

## glina-i-avtoskraby

- Added: "глина для кузова" (50)
- Added: "автомобільна глина" (40)
- Added: "глина для полірування" (10)

**Result:** 3 added, 0 skipped

---

## keramika-i-zhidkoe-steklo

- Added: "рідке скло" (5400) - HIGH VOLUME!
- Skipped (exists): "рідке скло для авто" (1000)
- Updated: "керамічне покриття авто" (140→210)
- Added: "купити рідке скло для авто" (210)
- Added: "купити рідке скло для автомобіля" (210)
- Added: "рідке скло ціна" (90)
- Added: "рідке скло для кузова авто" (10)
- Added: "рідке скло на машину" (10)
- Added: "нанокераміка ціна" (10)

**Result:** 8 added, 1 skipped, 1 updated

---

## kvik-deteylery

- Skipped (exists): "швидкий віск для авто" (20→40 already had higher volume)
- Added: "гарячий віск для автомобіля" (10)
- Restructured: moved secondary/supporting keywords to keywords array

**Result:** 1 added, 1 skipped

---

## Summary

| Category | Added | Skipped | Updated |
|----------|-------|---------|---------|
| polirovka | 6 | 3 | 0 |
| polirovalnye-pasty | 8 | 0 | 0 |
| polirovalnye-mashinki | 13 | 0 | 0 |
| akkumulyatornaya | 1 | 0 | 2 |
| mekhovye | 3 | 1 | 0 |
| glina-i-avtoskraby | 3 | 0 | 0 |
| keramika-i-zhidkoe-steklo | 8 | 1 | 1 |
| kvik-deteylery | 1 | 1 | 0 |
| **Total** | **43** | **6** | **3** |

---

**Validation:** All 8 JSON files passed `python3 -c "import json; json.load(open('file.json'))"`

**Note:** Categories `silanty` and `zashchitnye-pokrytiya` had no keywords in `uk_apply_W2.json`.
