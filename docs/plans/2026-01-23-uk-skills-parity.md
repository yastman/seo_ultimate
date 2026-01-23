# UK Skills Parity Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Обновить UK скиллы (uk-content-generator v1.0 → v2.0, uk-quality-gate v1.0 → v2.0) до паритета с RU версиями (content-generator v3.3, quality-gate v3.0)

**Architecture:** Вместо дублирования RU references → ссылки на RU + UK-специфичные оверрайды (UK-термінологія, UK-синоніми). Скрипты валидации общие.

**Tech Stack:** Markdown skills, Python validation scripts

---

## Gap Analysis

### uk-content-generator: v1.0 → v2.0

| Компонент | RU v3.3 | UK v1.0 | Действие |
|-----------|---------|---------|----------|
| references/buyer-guide.md | ✅ Scope Control, "Если X→Y" мін. 3, max 2-3 таблиці, 500-700 слів | ❌ Немає | Посилання на RU |
| references/templates.md | ✅ 5 типів (автохімія, захист, дресинги, інструменти, расходники) | ❌ Немає | Посилання на RU |
| references/validation.md | ✅ Academic ≥7%, H2 keyword мін. 2, stem ≤2.5% | ⚠️ Частково | Посилання на RU |
| references/lsi-synonyms.md | ✅ Таблиці синонімів | ❌ Немає | Створити uk-lsi-synonyms.md |
| references/research-mapping.md | ✅ Блок→Content маппінг | ❌ Немає | Посилання на RU |
| check_seo_structure.py в Workflow | ✅ | ❌ | Додати |
| Word count | 500-700 | Не вказано | Додати |
| "Если X→Y" мінімум | 3 | ⚠️ Згадано | Явно вимагати |
| H2 keyword check | мін. 2 | мін. 1 | Оновити до 2 |
| Academic ≥7% | ✅ | ❌ | Додати |

### uk-quality-gate: v1.0 → v2.0

| Компонент | RU v3.0 | UK v1.0 | Действие |
|-----------|---------|---------|----------|
| check_seo_structure.py | ✅ | ❌ | Додати |
| H2 keyword check | мін. 2 | ❌ | Додати |
| Academic ≥7% | ✅ | ❌ | Додати |
| Description length | 120-160 | 100-160 | Оновити до 120-160 |
| "Якщо X→Y" patterns | ≥3 | ❌ | Додати |
| Word count | 400-700 | 300-800 | Оновити |

---

## Task 1: Create uk-lsi-synonyms.md

**Files:**
- Create: `.claude/skills/uk-content-generator/references/uk-lsi-synonyms.md`

**Step 1: Write UK synonyms file**

```markdown
# LSI-синоніми для розбавлення переспаму (UK)

Коли stem-група перевищує 2.5%, замінити частину входжень на синоніми.

**Правило:** Цільові ключі з `_clean.json` НЕ замінювати. Замінювати лише тематичні слова.

---

## Семантичні дублі — НЕ додавати

Google склеює варіації одного смислу. Stuffing дублями = переспам без SEO-користі.

**❌ НЕ додавати:**

| Дубль 1 | ≈ Дубль 2 | ≈ Дубль 3 |
|---------|-----------|-----------|
| омивач для авто | омивач для машини | омивач для автомобіля |
| шампунь для авто | шампунь для машини | автомобільний шампунь |
| чорнитель шин | чорнитель для шин | чорнитель гуми |

---

## Інструменти/обладнання

| Слово | Синоніми |
|-------|----------|
| машинка/машина | інструмент, пристрій, варіант, модель |
| акумулятор | АКБ, елемент живлення, джерело живлення |
| батарея | АКБ, заряд, Li-Ion комірка |
| мережева | дротова, від розетки |
| бездротова | автономна, мобільна |

---

## Автохімія/детейлінг

| Слово | Синоніми |
|-------|----------|
| засіб | склад, продукт, препарат |
| нанесення | обробка, застосування |
| поверхня | покриття, основа, матеріал |
| захист | бар'єр, шар, покриття |
| блиск | глянець, сяяння, фініш |
| чищення | очищення, видалення, обробка |
| очищувач | склад, продукт, засіб |

---

## Автомобіль

| Слово | Синоніми |
|-------|----------|
| автомобіль | авто, машина, транспорт |
| кузов | поверхня, панелі, деталі |
| колесо | диск, шина (контекстно) |
| салон | інтер'єр, внутрішня частина |

---

## Процеси

| Слово | Синоніми |
|-------|----------|
| робота | процес, використання, експлуатація |
| полірування | обробка, корекція (контекстно) |
| миття | очищення, догляд |

---

## Приклад виправлення

**Проблема:** "очищувач" 13 разів, тошнота 3.61

**Рішення:**
1. Залишити 8-9 входжень "очищувач" (цільовий ключ)
2. Замінити 4-5 на: "склад", "засіб", "продукт"

**Результат:** тошнота 3.61 → 3.32 ✅

---

**Version:** 1.0 — January 2026
```

**Step 2: Verify file created**

Run: `cat .claude/skills/uk-content-generator/references/uk-lsi-synonyms.md | head -20`
Expected: File header visible

**Step 3: Commit**

```bash
git add .claude/skills/uk-content-generator/references/uk-lsi-synonyms.md
git commit -m "$(cat <<'EOF'
feat(skills): add uk-lsi-synonyms.md for UK content generation

UK-specific synonyms table for reducing keyword density spam.
Based on RU lsi-synonyms.md with Ukrainian translations.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Create references directory structure

**Files:**
- Create: `.claude/skills/uk-content-generator/references/` (directory)

**Step 1: Create directory**

Run: `mkdir -p .claude/skills/uk-content-generator/references`
Expected: Directory created

**Step 2: Verify**

Run: `ls -la .claude/skills/uk-content-generator/`
Expected: `references/` directory exists

---

## Task 3: Update uk-content-generator skill.md to v2.0

**Files:**
- Modify: `.claude/skills/uk-content-generator/skill.md`

**Step 1: Read current file**

Run: `cat .claude/skills/uk-content-generator/skill.md`

**Step 2: Update skill.md with new sections**

Key changes:
1. Version: v1.0 → v2.0
2. Add references section pointing to RU + UK overrides
3. Add Workflow step: check_seo_structure.py
4. Add word count: 500-700
5. Update H2 keyword requirement: мін. 1 → мін. 2
6. Add Academic ≥7% requirement
7. Add "Якщо X→Y" мін. 3 requirement
8. Add Scope Control section
9. Add Self-Check section

**Step 3: Write updated skill.md**

The updated file should include:

```markdown
---
name: uk-content-generator
description: >-
  Генерує SEO-контент у форматі buyer guide для UK категорій Ultimate.net.ua.
  Без посилань/цитат у тексті. Спірні твердження пом'якшувати. Research — лише як довідка.
  Use when: /uk-content-generator, напиши UK текст, згенеруй UK контент, створи контент для UK категорії,
  напиши опис UK категорії. ВАЖЛИВО: використовувати ПІСЛЯ завершення /uk-seo-research.
---

# UK Content Generator v2.0

## Quick Start

\`\`\`
/uk-content-generator {slug}
\`\`\`

**Input:** `uk/categories/{slug}/data/{slug}_clean.json` + `uk/categories/{slug}/meta/{slug}_meta.json` + research/*.md
**Output:** `uk/categories/{slug}/content/{slug}_uk.md`

---

## References

**RU references (основа):**
- [buyer-guide.md](../content-generator/references/buyer-guide.md) — Scope Control, патерни, ліміти
- [templates.md](../content-generator/references/templates.md) — Шаблони за типами категорій
- [validation.md](../content-generator/references/validation.md) — Метрики, чеклісти
- [research-mapping.md](../content-generator/references/research-mapping.md) — Research → Content

**UK-specific:**
- [uk-lsi-synonyms.md](references/uk-lsi-synonyms.md) — UK синоніми для розбавлення

---

## ⚠️ ПЕРШИЙ КРОК: Визначити тип сторінки
... [rest of the updated content]
```

**Step 4: Validate file**

Run: `head -50 .claude/skills/uk-content-generator/skill.md`
Expected: Version 2.0, References section visible

**Step 5: Commit**

```bash
git add .claude/skills/uk-content-generator/skill.md
git commit -m "$(cat <<'EOF'
feat(skills): update uk-content-generator to v2.0

- Add references to RU buyer-guide, templates, validation, research-mapping
- Add uk-lsi-synonyms.md reference
- Add check_seo_structure.py to Workflow
- Word count: 500-700 (was unspecified)
- H2 keyword requirement: min 2 (was 1)
- Add Academic ≥7% requirement
- Add "Якщо X→Y" min 3 requirement
- Add Scope Control section
- Add Self-Check section

Now at parity with content-generator v3.3.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Update uk-quality-gate skill.md to v2.0

**Files:**
- Modify: `.claude/skills/uk-quality-gate/skill.md`

**Step 1: Read current file**

Run: `cat .claude/skills/uk-quality-gate/skill.md`

**Step 2: Update skill.md with new checks**

Key changes:
1. Version: v1.0 → v2.0
2. Add check_seo_structure.py validation
3. Add H2 keyword check (мін. 2)
4. Add Academic ≥7% requirement
5. Update Description length: 100-160 → 120-160
6. Add "Якщо X→Y" patterns check (≥3)
7. Update Word count: 300-800 → 400-700

**Step 3: Write updated skill.md**

See full content in implementation.

**Step 4: Validate file**

Run: `head -50 .claude/skills/uk-quality-gate/skill.md`
Expected: Version 2.0, new checks visible

**Step 5: Commit**

```bash
git add .claude/skills/uk-quality-gate/skill.md
git commit -m "$(cat <<'EOF'
feat(skills): update uk-quality-gate to v2.0

- Add check_seo_structure.py validation
- Add H2 keyword check (min 2)
- Add Academic ≥7% requirement
- Description length: 120-160 (was 100-160)
- Add "Якщо X→Y" patterns check (≥3)
- Word count: 400-700 (was 300-800)

Now at parity with quality-gate v3.0.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Update uk-content-reviewer agent config

**Files:**
- Modify: `.claude/agents/uk-content-reviewer.md`

**Step 1: Read current agent config**

Run: `cat .claude/agents/uk-content-reviewer.md`

**Step 2: Update agent with new validation requirements**

Add:
- check_seo_structure.py to validation commands
- Academic ≥7% check
- H2 keyword check (мін. 2)
- Word count 500-700

**Step 3: Write updated agent config**

**Step 4: Commit**

```bash
git add .claude/agents/uk-content-reviewer.md
git commit -m "$(cat <<'EOF'
feat(agents): update uk-content-reviewer with v2.0 validation

- Add check_seo_structure.py to validation
- Add Academic ≥7% check
- H2 keyword requirement: min 2
- Word count: 500-700

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Update CLAUDE.md documentation

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Read current CLAUDE.md**

**Step 2: Update version and add notes about UK parity**

Add to UK Pipeline section:
- Note that UK skills are now at v2.0
- Reference to uk-lsi-synonyms.md

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "$(cat <<'EOF'
docs: update CLAUDE.md with UK skills v2.0 parity (v40.0)

- Note UK skills updated to v2.0
- Reference to uk-lsi-synonyms.md
- UK now at parity with RU pipeline

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: Final verification

**Step 1: Run validation on existing UK content**

```bash
python3 scripts/check_seo_structure.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md "активна піна"
```

Expected: PASS or WARN (identifies any gaps in existing content)

**Step 2: Verify all files created/modified**

```bash
ls -la .claude/skills/uk-content-generator/
ls -la .claude/skills/uk-content-generator/references/
cat .claude/skills/uk-content-generator/skill.md | grep "Version:"
cat .claude/skills/uk-quality-gate/skill.md | grep "Version:"
```

Expected:
- `references/` directory exists
- `uk-lsi-synonyms.md` exists
- Both skills show "Version: 2.0"

**Step 3: Git status check**

```bash
git log --oneline -5
```

Expected: 5-6 new commits with UK skills updates

---

## Summary of Changes

| File | Change |
|------|--------|
| `.claude/skills/uk-content-generator/skill.md` | v1.0 → v2.0 |
| `.claude/skills/uk-content-generator/references/uk-lsi-synonyms.md` | NEW |
| `.claude/skills/uk-quality-gate/skill.md` | v1.0 → v2.0 |
| `.claude/agents/uk-content-reviewer.md` | Updated validation |
| `CLAUDE.md` | v39.0 → v40.0 |

---

## Rollback Plan

If issues found:
```bash
git revert HEAD~5..HEAD  # Revert all 5 commits
# Or selectively:
git revert <commit-hash>  # Revert specific commit
```

---

**Plan Version:** 1.0 — 2026-01-23
