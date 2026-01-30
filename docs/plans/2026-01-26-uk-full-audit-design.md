# Design: UK Full Audit — Комплексний аудит всіх UK категорій

**Дата:** 2026-01-26
**Статус:** Draft
**Автор:** Claude + User

---

## Мета

Повний аудит **52 UK категорій** з:
- Перевіркою ключів, мета, контенту
- Валідацією щільності, тошноти, води
- Ручною перевіркою тексту
- Виправленням через UK скілли

---

## Створені артефакти

### Новий скілл: uk-verify-content

**Шлях:** `.claude/skills/uk-verify-content/SKILL.md`

**Призначення:** Інтерактивна верифікація UK контенту перед продакшеном

**Тригери:**
- `/uk-verify-content {slug}`
- "перевір UK контент"
- "верифікуй UK текст"
- "UK pre-production QA"

**Відмінність від uk-content-reviewer:**

| Aspect | uk-content-reviewer | uk-verify-content |
|--------|---------------------|-------------------|
| Mode | Autonomous | Interactive |
| Control | Minimal | Full |
| Fixes | Automatic | On request |
| Use case | Mass revision | Pre-prod QA |

---

## Скрипти валідації

### Інтегровані в UK скілли (9)

| Скрипт | Що перевіряє | Пороги |
|--------|--------------|--------|
| `validate_meta.py` | Title/Desc довжина | 50-60 / 120-160 |
| `validate_content.py` | Структура контенту | — |
| `check_keyword_density.py --lang uk` | Stem density | ≤2.5%, BLOCKER >3.0% |
| `check_water_natasha.py` | Тошнота, вода, academic | ≤3.5, 40-65%, ≥7% |
| `check_seo_structure.py` | H2 keywords, intro | ≥2 H2, keyword в intro |
| `check_h1_sync.py --lang uk` | H1 sync | — |
| `check_semantic_coverage.py --lang uk` | Покриття ключів | — |

### НЕ інтегровані (потенційно корисні)

| Скрипт | Що перевіряє | Потрібен? |
|--------|--------------|-----------|
| `validate_uk.py` | UK-специфічні правила | Перевірити |
| `check_cannibalization.py` | Канібалізація ключів | Для batch |
| `audit_keyword_consistency.py` | meta vs clean sync | Для batch |
| `audit_meta.py` | Batch meta validation | Для batch |
| `audit_synonyms.py` | Synonyms validation | Опційно |

---

## Workflow на категорію

```
┌─────────────────────────────────────────────────────────┐
│  /uk-verify-content {slug}                              │
│  (інтерактивний режим — людина контролює)               │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 1: Load & Overview                               │
│  - Read _clean.json, _meta.json, _uk.md, RESEARCH       │
│  - Show summary                                          │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 2: Run Validators                                │
│  - validate_meta.py                                      │
│  - check_seo_structure.py                               │
│  - check_keyword_density.py --lang uk                   │
│  - check_water_natasha.py                               │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 3: UK Terminology Check (BLOCKER)                │
│  - резина → гума                                         │
│  - мойка → миття                                         │
│  - стекло → скло                                         │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 4: Facts Verification                            │
│  - Extract claims from content                          │
│  - Verify against RESEARCH_DATA.md                      │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 5: Keywords Coverage                             │
│  - Primary: 100%, 3-7×                                   │
│  - Secondary: ≥80%                                       │
│  - Supporting: ≥80%                                      │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 6: Content Quality Checklist                     │
│  - Intro (buyer focus, not definition)                  │
│  - Structure (H2, "Якщо X → Y" patterns)                │
│  - Tables, FAQ                                           │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 7: Verdict & Actions                             │
│  [T] Fix terminology                                     │
│  [F] Fix facts                                           │
│  [K] Add keywords                                        │
│  [D] Fix density/nausea                                  │
│  [S] Skip                                                │
│  [N] Next category                                       │
└───────────────────────────┬─────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Phase 8: Fix Mode (if needed)                          │
│  - Show exact location                                   │
│  - Propose fix                                           │
│  - User confirms → Edit tool                            │
└─────────────────────────────────────────────────────────┘
```

---

## UK Terminology Reference

| RU термін | UK термін | Severity |
|-----------|-----------|----------|
| резина | гума | BLOCKER |
| мойка | миття | BLOCKER |
| стекло | скло | BLOCKER |
| чернитель | чорнитель | WARNING |
| очиститель | очищувач | WARNING |
| покрытие | покриття | WARNING |
| поверхность | поверхня | WARNING |
| защита | захист | WARNING |
| блеск | блиск | WARNING |
| нанесение | нанесення | WARNING |
| чистка | чищення | WARNING |

---

## Пороги валідації

| Metric | Target | WARNING | BLOCKER |
|--------|--------|---------|---------|
| Title length | 50-60 chars | — | <50 or >60 |
| Description | 120-160 chars | — | <120 or >160 |
| H1 | ≠ Title, без "Купити" | — | = Title or has "Купити" |
| Stem density | ≤2.5% | 2.5-3.0% | >3.0% |
| Classic nausea | ≤3.5 | 3.5-4.0 | >4.0 |
| Academic | ≥7% | 6-7% | <6% |
| Water | 40-65% | 65-75% | >75% |
| Primary keyword | 3-7× | 2× or 8-10× | 0 or >10 |
| H2 with keyword | ≥2 | 1 | 0 |
| Word count | 400-700 | 300-400 or 700-800 | <300 or >800 |
| "Якщо X → Y" | ≥3 | 2 | <2 |

---

## Категорії (52)

```
uk/categories/
├── aksessuary/
├── aktivnaya-pena/
├── antibitum/
├── antidozhd/
├── ... (ще 48)
```

---

## Наступні кроки

1. **Затвердити дизайн** — цей документ
2. **Почати аудит** — `/uk-verify-content {slug}` по черзі
3. **Фіксити проблеми** — інтерактивно через скілл
4. **Документувати результати** — QUALITY_REPORT.md в кожній категорії

---

**Version:** 1.0
