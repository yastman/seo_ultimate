# W4: Semantic Cluster Report

**Worker:** W4
**Date:** 2026-01-29
**Categories:** 34-44 (11 categories)

---

## Summary

| # | Category | Status | Keywords | Synonyms | Changes |
|---|----------|--------|----------|----------|---------|
| 1 | poliroli-dlya-plastika | OK | 4 | 18 | - |
| 2 | polirovalnye-krugi | OK | 7 | 25 | - |
| 3 | polirovalnye-mashinki | OK | 6 | 31 | - |
| 4 | polirovalnye-pasty | OK | 6 | 27 | - |
| 5 | polirovka | OK | 5 | 3 | - |
| 6 | pyatnovyvoditeli | OK | 3 | 5 | - |
| 7 | raspyliteli-i-penniki | OK | 6 | 18 | - |
| 8 | shampuni-dlya-ruchnoy-moyki | FIXED | 3 | 4 | +variant_of |
| 9 | shchetka-dlya-moyki-avto | FIXED | 6 | 16 | +1 keyword, +variant_of |
| 10 | silanty | FIXED | 3 | 5 | +1 keyword, +variant_of |
| 11 | sredstva-dlya-khimchistki-salona | FIXED | 13 | 67 | restructured |

---

## Detailed Analysis

### 1. poliroli-dlya-plastika
**Path:** `categories/ukhod-za-intererom/poliroli-dlya-plastika/`
**Status:** Already well-structured

**Keywords (4):**
- полироль для салона автомобиля (390)
- полироль для пластика автомобиля (320)
- полироль для торпеды (260)
- полироль для панели авто (170)

**Synonyms:** All have proper `variant_of` references

---

### 2. polirovalnye-krugi
**Path:** `categories/polirovka/polirovalnye-krugi/`
**Status:** Already well-structured
**Note:** meta file missing, needs /generate-meta

**Keywords (7):**
- круг для полировки авто (720)
- круги для полировки (480)
- полировальные круги (390)
- диск для полировки авто (90) — ІНШИЙ СЦЕНАРІЙ (диск vs круг)
- круги для полировальной машины (90) — ІНШИЙ СЦЕНАРІЙ
- круг полировальный на липучке (40) — ІНШИЙ СЦЕНАРІЙ
- набор кругов для полировки авто (30) — ІНШИЙ СЦЕНАРІЙ

---

### 3. polirovalnye-mashinki
**Path:** `categories/polirovka/polirovalnye-mashinki/`
**Status:** Already well-structured
**Note:** meta file missing, needs /generate-meta

**Keywords (6):**
- полировочная машинка (8100)
- машинка для полировки авто (1000)
- машинка для полировки (210)
- полировальная машина на аккумуляторе (260) — УНІКАЛЬНИЙ СЦЕНАРІЙ
- машинка для полировки кузова (30)
- полировочная машинка для детейлинга (10) — УНІКАЛЬНИЙ СЦЕНАРІЙ

---

### 4. polirovalnye-pasty
**Path:** `categories/polirovka/polirovalnye-pasty/`
**Status:** Already well-structured

**Keywords (6):**
- полировочная паста (1600)
- паста для полировки (320)
- полировочная паста для авто от царапин (260) — УНІКАЛЬНИЙ СЦЕНАРІЙ
- паста для полировки кузова (40)
- набор паст для полировки авто (20) — УНІКАЛЬНИЙ СЦЕНАРІЙ
- паста для полировки авто машинкой (10) — УНІКАЛЬНИЙ СЦЕНАРІЙ

---

### 5. polirovka
**Path:** `categories/polirovka/`
**Status:** Already well-structured

**Keywords (5):**
- полировка авто (2400)
- полировка кузова (480) — УНІКАЛЬНИЙ СЦЕНАРІЙ
- набор для полировки авто (480) — УНІКАЛЬНИЙ СЦЕНАРІЙ
- средства для полировки авто (50)
- полировка авто своими руками (40) — УНІКАЛЬНИЙ СЦЕНАРІЙ

---

### 6. pyatnovyvoditeli
**Path:** `categories/ukhod-za-intererom/pyatnovyvoditeli/`
**Status:** Already well-structured

**Keywords (3):**
- пятновыводитель (2400)
- пятновыводитель для салона авто (10) — УНІКАЛЬНИЙ СЦЕНАРІЙ
- пятновыводитель для сидений авто (10) — УНІКАЛЬНИЙ СЦЕНАРІЙ

---

### 7. raspyliteli-i-penniki
**Path:** `categories/aksessuary/raspyliteli-i-penniki/`
**Status:** Already well-structured

**Keywords (6):**
- пенообразователи для мойки (260)
- помповый распылитель для мойки авто (260) — ІНШЕ СЛОВО
- пенообразователь для мойки высокого давления (70) — УНІКАЛЬНИЙ СЦЕНАРІЙ
- распылитель для мойки авто (50)
- пенник для минимойки (10) — УНІКАЛЬНИЙ СЦЕНАРІЙ
- авто триггер (10) — ІНШЕ СЛОВО

---

### 8. shampuni-dlya-ruchnoy-moyki
**Path:** `categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/`
**Status:** FIXED

**Changes:**
- Added `variant_of` to synonyms without it

**Before:**
```json
{"keyword": "шампунь для ручной мойки", "volume": 10},
{"keyword": "шампунь для мытья авто вручную", "volume": 10},
```

**After:**
```json
{"keyword": "шампунь для ручной мойки", "volume": 10, "use_in": "lsi", "variant_of": "автошампунь для ручной мойки"},
{"keyword": "шампунь для мытья авто вручную", "volume": 10, "use_in": "lsi", "variant_of": "шампунь для ручной мойки авто"},
```

---

### 9. shchetka-dlya-moyki-avto
**Path:** `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/`
**Status:** FIXED

**Changes:**
- Added "щетка для мытья дисков авто" to keywords (unique intent - specific surface)
- Added `variant_of` to synonyms without it
- Updated `_meta.json` keywords_in_content

**Keywords (6):**
- щетка для мойки авто (480)
- щетка для мытья машины (390)
- щетка для автомобиля (320)
- мягкие щетки для мытья машины (110) — УНІКАЛЬНИЙ СЦЕНАРІЙ
- щетка скребок для авто (70) — ІНШЕ СЛОВО
- щетка для мытья дисков авто (10) — УНІКАЛЬНИЙ СЦЕНАРІЙ (moved from synonyms)

---

### 10. silanty
**Path:** `categories/zashchitnye-pokrytiya/silanty/`
**Status:** FIXED

**Changes:**
- Moved "силант для кузова" to keywords (unique intent - specific surface)
- Added `variant_of` to "силант покрытие"
- Updated `_meta.json` keywords_in_content

**Keywords (3):**
- силант (50)
- силанты для авто (40)
- силант для кузова (10) — УНІКАЛЬНИЙ СЦЕНАРІЙ (moved from synonyms)

---

### 11. sredstva-dlya-khimchistki-salona
**Path:** `categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/`
**Status:** FIXED (major restructure)

**Changes:**
- Identified 13 unique intents (was 7)
- Added proper `variant_of` to all 53 LSI synonyms
- Updated `_meta.json` keywords_in_content

**Keywords (13) — unique intents:**
1. химия для чистки салона (590) — базовий
2. химия для химчистки авто (390) — +модифікатор "химчистка"
3. средство для чистки салона авто (390) — ІНШЕ СЛОВО "средство"
4. химия для салона авто (320) — коротша форма
5. средство для химчистки салона авто (260) — +модифікатор
6. автохимия для салона (210) — ІНШЕ СЛОВО "автохимия"
7. профессиональная химия для чистки салона авто (210) — +модифікатор "профессиональная"
8. очиститель салона автомобиля (170) — ІНШЕ СЛОВО "очиститель"
9. средство для чистки сидений авто (90) — УНІКАЛЬНИЙ СЦЕНАРІЙ (сидіння)
10. средство для чистки тканевого салона автомобиля (20) — УНІКАЛЬНИЙ СЦЕНАРІЙ (тканина)
11. средство для чистки обивки салона автомобиля (10) — УНІКАЛЬНИЙ СЦЕНАРІЙ (обивка)
12. средства для чистки потолка автомобиля (10) — УНІКАЛЬНИЙ СЦЕНАРІЙ (потолок)
13. химия для текстиля авто (10) — ІНШЕ СЛОВО "текстиль"

---

## Files Modified

1. `categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/data/shampuni-dlya-ruchnoy-moyki_clean.json`
2. `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/data/shchetka-dlya-moyki-avto_clean.json`
3. `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/meta/shchetka-dlya-moyki-avto_meta.json`
4. `categories/zashchitnye-pokrytiya/silanty/data/silanty_clean.json`
5. `categories/zashchitnye-pokrytiya/silanty/meta/silanty_meta.json`
6. `categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/data/sredstva-dlya-khimchistki-salona_clean.json`
7. `categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/meta/sredstva-dlya-khimchistki-salona_meta.json`

---

## Notes

- **polirovalnye-krugi** and **polirovalnye-mashinki** need `/generate-meta` — meta files not found
- All 11 categories now follow semantic clustering principles
- Total unique intents identified: 57
- Total synonyms with variant_of: 194
