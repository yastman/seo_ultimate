# W2: UK Content Full Audit

## keramika-i-zhidkoe-steklo
**Verdict:** FIXED
**Density:** 2.27% → 1.82% (OK)
**Nausea:** 2.45 → 2.65 (PASS)
**Academic:** 6.6% → 6.9% (INFO)
**Coverage:** 7/8 → 8/8 (100%)
**Issues:**
- Intro було визначення "X — це Y..."
- FAQ "Чи можна нанести" та "Як доглядати" — про процес
- Ключ "керамічний лак для авто" відсутній
**Fixes:**
1. Intro переписано на buyer-focused з "вам", "хочете"
2. FAQ переписано на вибір: "Яку кераміку обрати", "Що купити для догляду"
3. Додано "керамічний лак для авто" в FAQ

## kisti-dlya-deteylinga
**Verdict:** FIXED
**Density:** OK (без змін)
**Nausea:** 3.74 → 3.46 (PASS)
**Academic:** 10.9% → 9.2% (PASS)
**Water:** 33.3% → 35.0% (WARNING, not BLOCKER)
**Coverage:** 8/8 (100%)
**Issues:**
- "щітка" 14 разів — спричиняло nausea/academic overflow
**Fixes:**
1. Замінено частину "щітка/щітки" на "пензлик", "інструмент", "варіант"
2. Додано зв'язувальні слова ("вам", "буде", "за автомобілем")

## kvik-deteylery
**Verdict:** FIXED
**Density:** OK
**Nausea:** 4.00 → 3.32 (PASS)
**Academic:** 14.4% → 10.2% (WARNING, was BLOCKER)
**Coverage:** 8/8 (100%)
**Issues:**
- "авто" 16 разів — критичний переспам (BLOCKER)
**Fixes:**
1. Замінено 5× "авто" на "машина", "кузов"
2. Academic знижено з BLOCKER до WARNING

## malyarniy-skotch
**Verdict:** WARNING
**Density:** OK
**Nausea:** 3.16 (PASS)
**Academic:** 7.6% (PASS)
**Water:** 20.7% (WARNING <40%, not BLOCKER)
**Coverage:** 5/5 (100%)
**Issues:**
- Water низька — технічний текст з малою кількістю зв'язувальних слів
**Fixes:** None needed (not BLOCKER)

## mekhovye
**Verdict:** WARNING
**Density:** OK
**Nausea:** 3.32 (PASS)
**Academic:** 8.1% (PASS)
**Water:** 29.5% (WARNING <40%, not BLOCKER)
**Coverage:** 5/5 (100%)
**Issues:**
- Water низька — технічний текст
**Fixes:** None needed (not BLOCKER)

## mikrofibra-i-tryapki
**Verdict:** FIXED
**Density:** OK
**Nausea:** 3.87 → 3.46 (PASS)
**Academic:** 14.9% → 11.9% (WARNING, was BLOCKER)
**Coverage:** 11/19 (57.9%) → 17/19 (89.5%)
**Issues:**
- "авто" 15 разів — BLOCKER academic
- 8 ключів NOT COVERED
**Fixes:**
1. Додано непокриті ключі: влаговбирна ганчірка, ганчірка для сушки/миття/скла, набір мікрофібри, мікрофібра для полірування/скла, серветки для скла
2. Замінено 3× "авто" на "кузов", "машина"

## moyka-i-eksterer
**Verdict:** WARNING
**Density:** OK
**Nausea:** 3.32 (PASS)
**Academic:** 10.9% (WARNING)
**Water:** 32.6% (WARNING)
**Coverage:** 4/5 (80%, threshold 70%)
**Issues:**
- 1 ключ SYNONYM (автохімія для миття авто)
- Water та Academic — WARNING, не BLOCKER
**Fixes:** None needed (coverage above threshold)

## nabory
**Verdict:** WARNING
**Density:** OK
**Nausea:** 3.46 (PASS)
**Academic:** 9.0% (PASS)
**Water:** 36.6% (WARNING)
**Coverage:** 10/16 (62.5%, threshold 50%)
**Issues:**
- Water низька — не BLOCKER
**Fixes:** None needed

## neytralizatory-zapakha
**Verdict:** PASS
**Density:** OK
**Nausea:** 3.46 (PASS)
**Academic:** 9.3% (PASS)
**Water:** 28.4% (WARNING)
**Coverage:** 5/5 (100%)
**Issues:** None
**Fixes:** None needed

## obezzhirivateli
**Verdict:** FIXED
**Density:** OK
**Nausea:** 3.61 → 3.32 (PASS)
**Academic:** 11.2% → 9.3% (PASS)
**Water:** 36.2% (WARNING)
**Coverage:** 8/8 (100%)
**Issues:**
- "знежирювач" 13 разів — WARNING nausea/academic
**Fixes:**
1. Замінено 3× "знежирювач" на "засіб", "продукт"

## oborudovanie
**Verdict:** PASS
**Density:** OK
**Nausea:** 3.00 (PASS)
**Academic:** 9.2% (PASS)
**Water:** 40.7% (PASS)
**Coverage:** 3/3 (100%)
**Issues:** None
**Fixes:** None needed

## ochistiteli-diskov
**Verdict:** FIXED
**Density:** OK
**Nausea:** 3.61 → 3.74 (WARNING, not BLOCKER)
**Academic:** 9.4% → 9.4% (PASS)
**Coverage:** 3/10 (30%) → 10/10 (100%)
**Issues:**
- Coverage BLOCKER: 7 ключів NOT COVERED
**Fixes:**
1. Intro: додано "засіб для чищення дисків автомобіля", "хімія для чищення дисків", "щітка для дисків"
2. Таблиця: "засіб для очищення дисків від іржі", "очищувач гальмівних дисків"
3. FAQ: "щітка для миття дисків", "щітка для миття коліс"
4. Замінено 2× "очищувач" на "засіб", "формула"

## ochistiteli-dvigatelya
**Verdict:** FIXED
**Density:** OK
**Nausea:** 3.32 (PASS)
**Academic:** 10.0% → 9.8% (WARNING)
**Coverage:** 3/8 (37.5%) → 8/8 (100%)
**Issues:**
- Coverage BLOCKER: 5 ключів NOT COVERED
**Fixes:**
1. Intro: "автохімія для двигуна", "рідина для миття двигуна", "очищувач двигуна зовнішній"
2. Body: "очищувач двигуна від мастила"
3. FAQ: "консервант двигуна"

---

[COMPLETE] 2026-02-02T12:45:00
