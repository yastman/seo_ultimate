# UK Full Cycle — Session Prompt

Скопіюй цей промпт у нову сесію Claude Code.

---

## Промпт

```
Виконай план з docs/plans/2026-01-26-uk-full-cycle-plan.md

Контекст:
- 52 UK категорії потребують мета + контент + валідацію
- 4 групи за пріоритетом: FAIL (19) → WARNING (3) → NO_KEYWORDS (13) → PASS (17)
- Ручний режим через скіли (не batch)

Порядок виконання:

1. **Pre-flight:** Виправ 13 NO_KEYWORDS категорій
   - Перенеси top keyword з supporting_keywords → keywords
   - Commit fix

2. **Для кожної категорії (по групах):**

   **Step 0: RU Comparison**
   - Перевір UK keywords vs RU keywords
   - Перевір RU content/meta існує

   **Step 1: /uk-generate-meta {slug}** (якщо потрібно)

   **Step 2: Validate Meta**
   - python3 scripts/validate_meta.py
   - Manual check: Title 50-60, "Купити", Desc 120-160, H1 без "Купити"

   **Step 3: /uk-content-generator {slug}** (якщо потрібно)

   **Step 4: uk-content-reviewer {slug}**
   - Автономний review + fix
   - Manual RU parity check після

   **Step 5: /uk-quality-gate {slug}**
   - Фінальна валідація
   - PASS required

   **Step 6: Commit**
   - git commit -m "feat(uk): {slug} — meta + content + quality-gate"

3. **Після кожної категорії:**
   - Оновити tasks/TODO_UK_CONTENT.md
   - Показати progress: X/52

Групи категорій:

**Group 1 (FAIL, 19):** akkumulyatornaya, aksessuary-dlya-naneseniya-sredstv, antimoshka, cherniteli-shin, gubki-i-varezhki, keramika-i-zhidkoe-steklo, kisti-dlya-deteylinga, kvik-deteylery, malyarniy-skotch, neytralizatory-zapakha, ochistiteli-stekol, omyvatel, poliroli-dlya-plastika, polirovalnye-pasty, raspyliteli-i-penniki, shampuni-dlya-ruchnoy-moyki, sredstva-dlya-khimchistki-salona, tverdyy-vosk, ukhod-za-intererom
→ Workflow: Step 0 → 4 → 5 → 6

**Group 2 (WARNING, 3):** aktivnaya-pena, mikrofibra-i-tryapki, voski
→ Workflow: Step 0 → 4 → 5 → 6

**Group 3 (NO_KEYWORDS, 13):** aksessuary, antibitum, keramika-dlya-diskov, mekhovye, oborudovanie, ochistiteli-diskov, ochistiteli-kozhi, ochistiteli-shin, opt-i-b2b, silanty, ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, zashchitnye-pokrytiya
→ Workflow: Step 0 → 1 → 2 → 3 → 4 → 5 → 6

**Group 4 (PASS, 17):** antidozhd, apparaty-tornador, avtoshampuni, glina-i-avtoskraby, moyka-i-eksterer, nabory, obezzhirivateli, ochistiteli-dvigatelya, ochistiteli-kuzova, polirol-dlya-stekla, polirovalnye-mashinki, polirovka, pyatnovyvoditeli, shchetka-dlya-moyki-avto, sredstva-dlya-kozhi, ukhod-za-kozhey, zhidkiy-vosk
→ Workflow: Step 0 → 5 → 6 (if changes)

Почни з Pre-flight (fix NO_KEYWORDS), потім Group 1.
```

---

## Швидкий старт

1. Відкрий нову сесію Claude Code
2. Скопіюй промпт вище
3. Claude почне з Pre-flight і піде по групах

---

## Validation Commands (reference)

```bash
# Meta
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json

# SEO structure
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{keyword}"

# Academic nausea
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md

# Keyword density
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

# UK terms (should be 0)
grep -c "резина\|мойка\|стекло" uk/categories/{slug}/content/{slug}_uk.md

# Word count
wc -w uk/categories/{slug}/content/{slug}_uk.md
```
