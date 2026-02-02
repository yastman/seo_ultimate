# Design: Fix Validation Skills for 100% Coverage Loop

**Date:** 2026-02-02
**Status:** Draft
**Tool:** /skill-creator

---

## Problem Statement

Скіли валідації контенту (content-reviewer, verify-content, quality-gate) мають асиметрію між RU та UK версіями:

1. **RU скіли не мають explicit циклу ітерацій** — UK має "max 3 iterations", RU ні
2. **SYNONYM інтерпретація не вказана в RU** — UK явно каже "SYNONYM = NOT COVERED"
3. **keywords[] severity різна** — UK-content-reviewer v2.3 змінив WARNING → BLOCKER, RU ні
4. **Застарілі посилання** — quality-gate посилається на `check_semantic_coverage.py`

---

## Goals

1. Синхронізувати RU скіли з UK версіями (паритет функціональності)
2. Додати явний цикл "валідація → фікс → ревалідація → 100%"
3. Прибрати застарілі посилання на скрипти
4. Забезпечити однакову поведінку для обох мов

---

## Scope

### Скіли для оновлення:

| Скіл | Тип змін | Пріоритет |
|------|----------|-----------|
| content-reviewer (RU) | Major update | HIGH |
| verify-content (RU) | Minor update | MEDIUM |
| quality-gate (RU) | Cleanup | MEDIUM |
| uk-quality-gate (UK) | Cleanup | LOW |

### Поза scope:

- content-generator (не валідує, тільки генерує)
- uk-content-generator (не валідує)
- uk-content-reviewer (вже має правильну логіку — референс)
- uk-verify-content (вже має правильну логіку)

---

## Design

### Unified Validation Loop (SSOT)

Всі скіли валідації повинні використовувати однаковий цикл:

```
┌─────────────────────────────────────────┐
│ Step N: Keywords Coverage Check         │
│ audit_coverage.py --include-meta        │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│ Step N+1: Evaluate Results              │
│ - primary+secondary < 100% → BLOCKER    │
│ - supporting < 80% → WARNING            │
│ - keywords[] < threshold → BLOCKER      │
│ - SYNONYM = NOT COVERED                 │
└─────────────────────────────────────────┘
                   ↓
         ┌─────────────────┐
         │ All 100%?       │
         └────────┬────────┘
           YES ↓  │  NO ↓
           ┌──────┴──────┐
           │             │
      PASS ↓        ┌────┴────┐
                    │ iter<3? │
                    └────┬────┘
                  YES ↓  │ NO ↓
                    ┌────┴────┐
                FIX │         │ STOP+LOG
                    ↓         ↓
              Re-validate   Document
                    │     unresolved
                    └──→ Loop back
```

### Shared Reference File

Створити `shared/coverage-loop.md` з:
- Алгоритм циклу
- Статуси покриття (EXACT/NORM/LEMMA = COVERED, SYNONYM/PARTIAL/ABSENT = NOT COVERED)
- Куди вставляти непокриті ключі
- Max 3 ітерації

---

## Changes Per Skill

### 1. content-reviewer (RU) — MAJOR UPDATE

**File:** `.claude/skills/content-reviewer/SKILL.md`

**Додати:**

```markdown
### Step 3: Keywords Coverage (audit_coverage.py)

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang ru --json --include-meta
```

**Статуси покриття:**
- ✅ COVERED: `EXACT`, `NORM`, `LEMMA`
- ❌ NOT COVERED: `SYNONYM`, `PARTIAL`, `ABSENT`

> **SYNONYM = NOT COVERED:** Синонім знайдено в тексті, але сам ключ — відсутній. Для SEO потрібен саме ключ.

**Severity:**

| Джерело | Вимога | Severity |
|---------|--------|----------|
| primary+secondary | **100% COVERED** | BLOCKER |
| supporting | **≥80% COVERED** | WARNING |
| keywords[] | adaptive threshold | **BLOCKER** |

### Step 9: Re-validate Coverage (MANDATORY)

**Обов'язково після будь-яких виправлень!**

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang ru --json --include-meta
```

**Цикл виправлень (max 3 ітерації):**

```
Iteration 1: Fix → Re-validate → check NOT COVERED
Iteration 2: Fix remaining → Re-validate → check NOT COVERED
Iteration 3: Fix remaining → Re-validate → STOP
```

**Якщо після 3 ітерацій залишаються NOT COVERED:**
- Задокументувати в логу які ключі не вдалося вставити
- Перейти до фінального verdict

**Куди вставляти непокриті ключі:**

| Пріоритет | Куди | Приклад |
|-----------|------|---------|
| **primary** | Intro (перший абзац) | "...{keyword} поможет..." |
| **secondary** | H2 заголовки | "## Как выбрать {keyword}" |
| **supporting** | Сценарии, таблицы, FAQ | "**Для {keyword}** — ..." |
```

**Changelog додати:**
```markdown
**Changelog v2.1:**
- **SYNCED with UK v2.3** — повний паритет
- ADDED: max 3 ітерації для циклу виправлень
- ADDED: SYNONYM = NOT COVERED (explicit)
- CHANGED: keywords[] severity WARNING → BLOCKER
- ADDED: Таблиця куди вставляти непокриті ключі
```

---

### 2. verify-content (RU) — MINOR UPDATE

**File:** `.claude/skills/verify-content/SKILL.md`

**Додати в Phase 7 (або відповідний step):**

```markdown
**SYNONYM = NOT COVERED:** Синонім знайдено в тексті, але сам ключ — відсутній. Для SEO потрібен саме ключ.

**Цикл виправлень (max 3 ітерації):**
- Iteration 1-3: Fix → Re-validate → check
- Після 3 ітерацій: STOP і задокументувати
```

---

### 3. quality-gate (RU) — CLEANUP

**File:** `.claude/skills/quality-gate/SKILL.md` та `skill.md`

**Видалити:**
```markdown
# H1 sync check
python3 scripts/check_h1_sync.py

# Semantic coverage
python3 scripts/check_semantic_coverage.py
```

**Додати:**
```markdown
**SYNONYM = NOT COVERED** — синонім не замінює ключ для SEO.
```

---

### 4. uk-quality-gate — CLEANUP

**File:** `.claude/skills/uk-quality-gate/skill.md`

**Видалити:**
```markdown
# H1 sync check
python3 scripts/check_h1_sync.py --lang uk

# Semantic coverage check
python3 scripts/check_semantic_coverage.py --lang uk
```

---

### 5. shared/validation-checklist.md — UPDATE

**File:** `.claude/skills/shared/validation-checklist.md`

**Додати:**

```markdown
## Keywords Coverage (audit_coverage.py)

**Статуси:**
- ✅ COVERED: EXACT, NORM, LEMMA
- ❌ NOT COVERED: SYNONYM, PARTIAL, ABSENT

**SYNONYM = NOT COVERED** — синонім знайдено, але сам ключ відсутній.

**Цикл:** max 3 ітерації (Fix → Re-validate → Check)
```

---

## Implementation Plan

### Task 1: Update content-reviewer (RU)
- Read current SKILL.md
- Add coverage loop section (copy from uk-content-reviewer)
- Add SYNONYM = NOT COVERED
- Change keywords[] severity to BLOCKER
- Add changelog v2.1

### Task 2: Update verify-content (RU)
- Add SYNONYM clarification
- Add max 3 iterations

### Task 3: Cleanup quality-gate (RU)
- Remove check_semantic_coverage.py references
- Remove check_h1_sync.py references
- Add SYNONYM clarification

### Task 4: Cleanup uk-quality-gate
- Remove check_semantic_coverage.py references
- Remove check_h1_sync.py references

### Task 5: Update shared/validation-checklist.md
- Add coverage statuses
- Add SYNONYM clarification
- Add iteration loop

### Task 6: Validate changes
- Run /skill-creator quick_validate.py on each updated skill
- Test on real category (aktivnaya-pena UK)

---

## Validation Criteria

1. ✅ RU content-reviewer має max 3 ітерації
2. ✅ RU content-reviewer має SYNONYM = NOT COVERED
3. ✅ RU content-reviewer має keywords[] = BLOCKER
4. ✅ quality-gate (RU/UK) не посилається на check_semantic_coverage.py
5. ✅ Всі скіли проходять quick_validate.py
6. ✅ E2E тест: uk-content-reviewer знаходить і фіксить aktivnaya-pena

---

## Risks

| Ризик | Mitigation |
|-------|------------|
| Зламати існуючі скіли | Backup перед змінами, test після |
| Inconsistency між RU/UK | Копіювати секції дослівно з UK |
| Великі зміни в SKILL.md | Зберігати структуру, тільки додавати |

---

## Next Steps

1. Затвердити дизайн
2. Виконати Task 1-5 послідовно
3. Validate на реальній категорії
4. Commit з описом змін

---

**Version:** 1.0
