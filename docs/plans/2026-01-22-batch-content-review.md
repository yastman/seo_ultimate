# Batch Content Review — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Пройти все 50 русских категорий, выполняя полную ревизию контента по скиллу `/content-reviewer`.

**Architecture:** Последовательный проход. Для каждой категории: вызвать скилл `/content-reviewer {path}` → скилл читает файлы, прогоняет валидаторы, проверяет keywords/research/commercial intent, фиксит BLOCKERs → выдаёт отчёт → ожидание одобрения → следующая.

**Tech Stack:** `/content-reviewer` skill, Python validators, Edit tool

---

## Execution Mode

**Важно:** НЕ использовать субагента `Task(subagent_type="content-reviewer")`.
Вместо этого вызывать скилл напрямую:

```
Skill(skill="content-reviewer", args="{path}")
```

Скилл выполняет полный 10-шаговый workflow в текущей сессии.

---

## Категории (50 шт)

| # | Path | Slug |
|---|------|------|
| 1 | aksessuary | aksessuary |
| 2 | aksessuary/aksessuary-dlya-naneseniya-sredstv | aksessuary-dlya-naneseniya-sredstv |
| 3 | aksessuary/gubki-i-varezhki | gubki-i-varezhki |
| 4 | aksessuary/malyarniy-skotch | malyarniy-skotch |
| 5 | aksessuary/mikrofibra-i-tryapki | mikrofibra-i-tryapki |
| 6 | aksessuary/nabory | nabory |
| 7 | aksessuary/raspyliteli-i-penniki | raspyliteli-i-penniki |
| 8 | aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga | kisti-dlya-deteylinga |
| 9 | aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto | shchetka-dlya-moyki-avto |
| 10 | aksessuary/vedra-i-emkosti | vedra-i-emkosti |
| 11 | moyka-i-eksterer | moyka-i-eksterer |
| 12 | moyka-i-eksterer/avtoshampuni | avtoshampuni |
| 13 | moyka-i-eksterer/avtoshampuni/aktivnaya-pena | aktivnaya-pena |
| 14 | moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki | shampuni-dlya-ruchnoy-moyki |
| 15 | moyka-i-eksterer/ochistiteli-dvigatelya | ochistiteli-dvigatelya |
| 16 | moyka-i-eksterer/ochistiteli-kuzova/antibitum | antibitum |
| 17 | moyka-i-eksterer/ochistiteli-kuzova/antimoshka | antimoshka |
| 18 | moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby | glina-i-avtoskraby |
| 19 | moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli | obezzhirivateli |
| 20 | moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom | ukhod-za-naruzhnym-plastikom |
| 21 | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin | cherniteli-shin |
| 22 | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov | keramika-dlya-diskov |
| 23 | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov | ochistiteli-diskov |
| 24 | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin | ochistiteli-shin |
| 25 | moyka-i-eksterer/sredstva-dlya-stekol/antidozhd | antidozhd |
| 26 | moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol | ochistiteli-stekol |
| 27 | moyka-i-eksterer/sredstva-dlya-stekol/omyvatel | omyvatel |
| 28 | moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla | polirol-dlya-stekla |
| 29 | oborudovanie | oborudovanie |
| 30 | oborudovanie/apparaty-tornador | apparaty-tornador |
| 31 | opt-i-b2b | opt-i-b2b |
| 32 | polirovka | polirovka |
| 33 | polirovka/polirovalnye-krugi/mekhovye | mekhovye |
| 34 | polirovka/polirovalnye-mashinki/akkumulyatornaya | akkumulyatornaya |
| 35 | polirovka/polirovalnye-pasty | polirovalnye-pasty |
| 36 | ukhod-za-intererom | ukhod-za-intererom |
| 37 | ukhod-za-intererom/neytralizatory-zapakha | neytralizatory-zapakha |
| 38 | ukhod-za-intererom/poliroli-dlya-plastika | poliroli-dlya-plastika |
| 39 | ukhod-za-intererom/pyatnovyvoditeli | pyatnovyvoditeli |
| 40 | ukhod-za-intererom/sredstva-dlya-khimchistki-salona | sredstva-dlya-khimchistki-salona |
| 41 | ukhod-za-intererom/sredstva-dlya-kozhi | sredstva-dlya-kozhi |
| 42 | ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi | ochistiteli-kozhi |
| 43 | ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey | ukhod-za-kozhey |
| 44 | zashchitnye-pokrytiya | zashchitnye-pokrytiya |
| 45 | zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo | keramika-i-zhidkoe-steklo |
| 46 | zashchitnye-pokrytiya/kvik-deteylery | kvik-deteylery |
| 47 | zashchitnye-pokrytiya/silanty | silanty |
| 48 | zashchitnye-pokrytiya/voski | voski |
| 49 | zashchitnye-pokrytiya/voski/tverdyy-vosk | tverdyy-vosk |
| 50 | zashchitnye-pokrytiya/voski/zhidkiy-vosk | zhidkiy-vosk |

---

## Task Template

### Task N: Review {slug}

**Step 1: Invoke skill**

```
Skill(skill="content-reviewer", args="{path}")
```

**Step 2: Skill executes full workflow**

Скилл `/content-reviewer` выполняет:

1. **Read files** (parallel): `_clean.json`, `_meta.json`, `RESEARCH_DATA.md`, `{slug}_ru.md`
2. **Run 4 validators** (parallel):
   - `validate_meta.py`
   - `validate_content.py --mode seo`
   - `check_keyword_density.py`
   - `check_water_natasha.py`
3. **Keywords Coverage**: primary 100%, secondary 100%, supporting ≥80%
4. **Research Completeness**: все типы из Блок 2, нет противоречий
5. **Commercial Intent Check**: каждая секция → "помогает выбрать или учит использовать?"
6. **Dryness Diagnosis**: intro, обращения, паттерны "Если X → Y", таблицы
7. **Build Verdict Table**: сводка всех критериев
8. **Fix BLOCKERs** (Edit tool): H1≠name, stem>3%, nausea>4, how-to sections, missing keywords
9. **Re-validate**: повторный прогон валидаторов
10. **Output Report**: verdict + исправления

**Step 3: Review report**

После получения отчёта — ожидание одобрения пользователя.

**Step 4: Next category**

После "ок" → следующая категория.

---

## BLOCKER Criteria (must fix)

| Issue | Detection | Fix |
|-------|-----------|-----|
| H1 ≠ name | H1 должен = `_clean.json`.name (мн.ч.) | Replace H1 |
| Stem >3.0% | check_keyword_density.py | Replace with synonyms |
| Nausea >4.0 | check_water_natasha.py | Add variety |
| Intro = definition | "X — это Y, которое..." | Rewrite: benefit + scenario |
| How-to sections | H2: "Как наносить", "Техника" | Delete or convert |
| >2 primary missing | Keywords coverage | Add organically |
| Research contradiction | Fact ≠ RESEARCH_DATA | Fix to match |
| FAQ duplicates table | Same Q in table | Replace with unique Q |

---

## WARNING Criteria (should note)

| Issue | Detection | Note |
|-------|-----------|------|
| Water >75% | check_water_natasha.py | Report, minor issue |
| Academic <7% | check_water_natasha.py | INFO only, no fix needed |
| <3 "Если X → Y" patterns | Count | Report |
| 1-2 primary missing | Coverage | Add if easy |
| No H2 with secondary | Manual check | Report |

---

## Execution Notes

1. **НЕ коммитить автоматически** — только Edit файлы. Коммит вручную после батча.
2. **RESEARCH_DATA.md — источник истины** для фактов и профтерминов.
3. **entities в _clean.json НЕ использовать** — автогенерированные.
4. **Buyer guide, не how-to** — секции про применение удалять.
5. **Скилл, не субагент** — вызывать через `Skill()`, не `Task()`.

---

## Progress Tracker

```
[ ] 1. aksessuary
[ ] 2. aksessuary-dlya-naneseniya-sredstv
[ ] 3. gubki-i-varezhki
[ ] 4. malyarniy-skotch
[ ] 5. mikrofibra-i-tryapki
[ ] 6. nabory
[ ] 7. raspyliteli-i-penniki
[ ] 8. kisti-dlya-deteylinga
[ ] 9. shchetka-dlya-moyki-avto
[ ] 10. vedra-i-emkosti
[ ] 11. moyka-i-eksterer
[ ] 12. avtoshampuni
[ ] 13. aktivnaya-pena
[ ] 14. shampuni-dlya-ruchnoy-moyki
[ ] 15. ochistiteli-dvigatelya
[ ] 16. antibitum
[ ] 17. antimoshka
[ ] 18. glina-i-avtoskraby
[ ] 19. obezzhirivateli
[ ] 20. ukhod-za-naruzhnym-plastikom
[ ] 21. cherniteli-shin
[ ] 22. keramika-dlya-diskov
[ ] 23. ochistiteli-diskov
[ ] 24. ochistiteli-shin
[ ] 25. antidozhd
[ ] 26. ochistiteli-stekol
[ ] 27. omyvatel
[ ] 28. polirol-dlya-stekla
[ ] 29. oborudovanie
[ ] 30. apparaty-tornador
[ ] 31. opt-i-b2b
[ ] 32. polirovka
[ ] 33. mekhovye
[ ] 34. akkumulyatornaya
[ ] 35. polirovalnye-pasty
[ ] 36. ukhod-za-intererom
[ ] 37. neytralizatory-zapakha
[ ] 38. poliroli-dlya-plastika
[ ] 39. pyatnovyvoditeli
[ ] 40. sredstva-dlya-khimchistki-salona
[ ] 41. sredstva-dlya-kozhi
[ ] 42. ochistiteli-kozhi
[ ] 43. ukhod-za-kozhey
[ ] 44. zashchitnye-pokrytiya
[ ] 45. keramika-i-zhidkoe-steklo
[ ] 46. kvik-deteylery
[ ] 47. silanty
[ ] 48. voski
[ ] 49. tverdyy-vosk
[ ] 50. zhidkiy-vosk
```

---

## Commit Strategy

После завершения батча (10-15 категорий или все 50):

```bash
git add categories/
git commit -m "refactor(content): batch review and fixes for RU categories

- Fixed H1 mismatches
- Added missing keywords
- Improved commercial intent
- Removed how-to sections

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```
