# Session Prompt: UK Full Audit

Скопіюй цей промпт в нову сесію Claude Code.

---

## Промпт

```
Виконай план docs/plans/2026-01-26-uk-full-audit-plan.md

Режим: без субагентів, виконуй самостійно.

Workflow на кожну категорію:
1. Прочитай файли категорії (parallel): _clean.json, _meta.json, _uk.md
2. Запусти валідатори (parallel):
   - python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
   - python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary}"
   - python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
   - python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md
3. Перевір UK термінологію (grep резина|мойка|стекло)
4. Перевір покриття ключів (primary 3-7×, secondary/supporting ≥80%)
5. Покажи verdict таблицю
6. Запитай мене що фіксити: [T]erminology, [K]eywords, [D]ensity, [S]kip, [N]ext
7. Виконай фікси через Edit tool
8. Закоміть після кожної категорії

Пороги:
- Stem density: ≤2.5% (BLOCKER >3.0%)
- Classic nausea: ≤3.5 (BLOCKER >4.0)
- Academic: ≥7%
- Water: 40-65%
- Primary keyword: 3-7× (BLOCKER 0 or >10)
- H2 with keyword: ≥2

UK термінологія (BLOCKER):
- резина → гума
- мойка → миття
- стекло → скло

Почни з Pre-flight (коміт uk-verify-content skill), потім Group 1: akkumulyatornaya.
```

---

## Файли плану

- **Design:** `docs/plans/2026-01-26-uk-full-audit-design.md`
- **Plan:** `docs/plans/2026-01-26-uk-full-audit-plan.md`
- **Skill:** `.claude/skills/uk-verify-content/SKILL.md`

---

## Категорії (52)

Group 1 (8): akkumulyatornaya, aksessuary, aksessuary-dlya-naneseniya-sredstv, aktivnaya-pena, antibitum, antidozhd, antimoshka, apparaty-tornador

Group 2 (6): avtoshampuni, cherniteli-shin, glina-i-avtoskraby, gubki-i-varezhki, keramika-dlya-diskov, keramika-i-zhidkoe-steklo

Group 3 (7): kisti-dlya-deteylinga, kvik-deteylery, malyarniy-skotch, mekhovye, mikrofibra-i-tryapki, moyka-i-eksterer, nabory

Group 4 (10): neytralizatory-zapakha, obezzhirivateli, oborudovanie, ochistiteli-diskov, ochistiteli-dvigatelya, ochistiteli-kozhi, ochistiteli-kuzova, ochistiteli-shin, ochistiteli-stekol, omyvatel

Group 5 (8): opt-i-b2b, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-mashinki, polirovalnye-pasty, polirovka, pyatnovyvoditeli, raspyliteli-i-penniki

Group 6 (8): shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto, silanty, sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi, tverdyy-vosk, ukhod-za-intererom, ukhod-za-kozhey

Group 7 (5): ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, voski, zashchitnye-pokrytiya, zhidkiy-vosk
