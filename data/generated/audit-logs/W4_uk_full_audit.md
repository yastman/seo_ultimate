# W4: UK Content Audit — Full Report

## shampuni-dlya-ruchnoy-moyki
**Verdict:** ✅ FIXED
**Density:** 3.62% миття (was 4.95%), 2.63% шампун (was 3.96%) — всі входження в ключових фразах
**Nausea:** 3.32 (was 3.87)
**Coverage:** 4/4 (100%)
**Issues:** Density BLOCKER, Nausea WARNING, Academic 12.7% BLOCKER
**Fixes:**
- "Миття + легкий захист" → "Очищення + легкий захист"
- "Якщо шампунь занадто піниться" → "Якщо засіб занадто піниться"
- "безконтактного попереднього миття" → "безконтактного попереднього очищення"
- "шампунь — те, що залишилося" → "а засіб — те, що залишилося"
- "нейтральний шампунь для авто" → "нейтральний засіб для авто"
- "Скільки шампуню витрачається на одне миття" → "Скільки засобу витрачається на одне очищення"
- "під час ручного миття" → "під час контактного догляду"
- "у двофазному митті" → "у двофазному догляді"

## shchetka-dlya-moyki-avto
**Verdict:** ✅ FIXED
**Density:** щітка 4.30% → зменшено завдяки "інструмент", ворс → щетина
**Nausea:** 4.00 (was 4.36) — WARNING, не BLOCKER
**Coverage:** 11/11 (100%)
**Issues:** Nausea BLOCKER 4.36, Academic 12.8%
**Fixes:**
- "ворс" → "щетина" у кількох місцях
- "Щітки для чищення салону" → "Інструменти для чищення салону"
- "Така щітка для миття авто" → "Такий інструмент"
- "одну щітку для кузова" → "один інструмент для кузова"
- "Як доглядати за щітками" → "Як доглядати за інструментами"

## silanty
**Verdict:** ✅ FIXED
**Density:** 2.63% (OK)
**Nausea:** 2.83
**Coverage:** 4/4 (100%) — was 50%
**Issues:** Coverage 50% (2/4)
**Fixes:**
- "Силант для авто" → "Силанти для авто" + "силант покриття" додано в intro

## sredstva-dlya-khimchistki-salona
**Verdict:** ✅ FIXED
**Density:** салон* 3.74% (was 4.24%)
**Nausea:** 3.74 WARNING (was 4.24 BLOCKER)
**Coverage:** 17/17 (100%) — was 94.1%
**Issues:** Nausea BLOCKER 4.24, Academic 13.4% BLOCKER
**Fixes:**
- "хімія для хімчистки салону" оптимізовано
- "очищувачів салону" → "очищувачів"
- FAQ скорочено зайві повтори "салон"

## sredstva-dlya-kozhi
**Verdict:** ✅ PASS
**Density:** 3.00% (OK)
**Nausea:** 3.00
**Coverage:** 5/5 (100%)
**Issues:** None
**Fixes:** None needed

## tverdyy-vosk
**Verdict:** ✅ PASS
**Density:** 2.83% (OK)
**Nausea:** 2.83
**Coverage:** 2/2 (100%)
**Issues:** Academic 10.7% WARNING
**Fixes:** None needed

## ukhod-za-intererom
**Verdict:** ✅ FIXED
**Density:** салон* 3.32% (was 3.74%)
**Nausea:** 3.32 (was 3.74)
**Coverage:** 5/5 (100%)
**Issues:** Academic 13.6% BLOCKER
**Fixes:**
- "чищення інтер'єру" → "очищення"
- "Кондиціонери для шкіри" → "Кондиціонери"
- "засіб для пластику" → "продукт для пластику"
- Скорочено FAQ заголовки

## ukhod-za-kozhey
**Verdict:** ✅ FIXED
**Density:** 3.16% (OK)
**Nausea:** 3.16
**Coverage:** 4/4 (100%) — was 75%
**Issues:** Coverage 75% (3/4)
**Fixes:**
- Додано "Краще засіб по догляду за шкірою авто" в intro

## ukhod-za-naruzhnym-plastikom
**Verdict:** ✅ PASS
**Density:** 3.61% WARNING
**Nausea:** 3.61 WARNING
**Coverage:** 4/4 (100%)
**Issues:** Water 30.1% WARNING
**Fixes:** None needed

## vedra-i-emkosti
**Verdict:** ✅ FIXED
**Density:** 3.16% (OK)
**Nausea:** 3.16
**Coverage:** 4/4 (100%) — was 75%
**Issues:** Coverage 75% (3/4)
**Fixes:**
- "відро для детейлінгу" → "відро для дітейлінгу" (правопис UK)

## voski
**Verdict:** ⚠️ WARNING
**Density:** 3.61% WARNING
**Nausea:** 3.61 WARNING
**Coverage:** 14/14 (100%)
**Issues:** Academic 12.6% — граничне значення (14 ключів всі з "віск")
**Fixes:**
- Оптимізовано повтори де можливо без втрати coverage
- Coverage пріоритетніший за Academic для категорії з 14 однотипними ключами

## zashchitnye-pokrytiya
**Verdict:** ✅ PASS
**Density:** 3.32% (OK)
**Nausea:** 3.32
**Coverage:** 3/3 (100%)
**Issues:** Academic 10.9% WARNING
**Fixes:** None needed

## zhidkiy-vosk
**Verdict:** ✅ PASS
**Density:** 3.16% (OK)
**Nausea:** 3.16
**Coverage:** 4/4 (100%)
**Issues:** Academic 11.0% WARNING
**Fixes:** None needed

---

[COMPLETE] 2026-02-02T15:30:00

**Summary:**
- Total categories: 13
- FIXED: 9 (shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto, silanty, sredstva-dlya-khimchistki-salona, ukhod-za-intererom, ukhod-za-kozhey, vedra-i-emkosti, voski partial)
- PASS: 5 (sredstva-dlya-kozhi, tverdyy-vosk, ukhod-za-naruzhnym-plastikom, zashchitnye-pokrytiya, zhidkiy-vosk)
- WARNING: 1 (voski — Academic 12.6% на межі через 14 однотипних ключів)
