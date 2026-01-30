# Session Prompt: UK Full Cycle v2

Скопіюй в нову сесію:

---

Виконай план з `docs/plans/2026-01-26-uk-full-cycle-plan-v2.md`

**Контекст:**
- 52 UK категорії потребують мета + контент + валідацію
- 4 групи за пріоритетом: FAIL (19) → WARNING (3) → NO_KEYWORDS (13) → PASS (17)
- Ручний режим через скіли (не batch, не субагенти)
- Review через валідатори + Edit (замість uk-content-reviewer субагента)

**Послідовність:**
1. Task 0: Pre-flight — fix NO_KEYWORDS (promote supporting → keywords)
2. Group 1: FAIL категорії (Step 0 → 3 → 4 → 5)
3. Group 2: WARNING категорії
4. Group 3: NO_KEYWORDS full cycle (всі кроки)
5. Group 4: PASS verify only

**Скіли для використання:**
- `/uk-generate-meta {slug}` — генерація мета-тегів
- `/uk-content-generator {slug}` — генерація контенту
- `/uk-quality-gate {slug}` — фінальна валідація

**Валідатори:**
```bash
python3 scripts/check_seo_structure.py uk/categories/{slug}/content/{slug}_uk.md "{primary}"
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md
```

**Почни з Task 0 (Pre-flight).**
