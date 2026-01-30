# UK Skills Sync — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Привести все UK скиллы к полному паритету с RU скиллами (эталон).

**Architecture:** Читаем RU скилл → адаптируем для UK (пути, термины, примеры) → записываем → коммитим. RU = source of truth, UK = адаптированная копия.

**Tech Stack:** Markdown skills, Write tool, Git

---

## Таблица адаптации (справочник)

| RU | UK |
|----|-----|
| `categories/{slug}/` | `uk/categories/{slug}/` |
| `{slug}_ru.md` | `{slug}_uk.md` |
| `/content-generator` | `/uk-content-generator` |
| `/generate-meta` | `/uk-generate-meta` |
| `/quality-gate` | `/uk-quality-gate` |
| `/seo-research` | `/uk-seo-research` |
| `/deploy-to-opencart` | `/uk-deploy` |
| `language: "ru"` | `language: "uk"` |
| `language_id=3` | `language_id=1` |
| резина | гума |
| мойка | миття |
| стекло | скло |
| чернитель | чорнитель |
| очиститель | очищувач |
| покрытие | покриття |
| поверхность | поверхня |
| защита | захист |
| нанесение | нанесення |
| блеск | блиск |
| сушка | сушіння |

---

## Task 1: uk-content-generator/skill.md

**Files:**
- Read: `.claude/skills/content-generator/skill.md` (v3.3, 568 lines)
- Write: `.claude/skills/uk-content-generator/skill.md`

**Step 1: Read RU source**

Read `.claude/skills/content-generator/skill.md` полностью.

**Step 2: Adapt to UK**

Адаптировать:
- YAML header: name → `uk-content-generator`, description на українській
- Quick Start: `/content-generator` → `/uk-content-generator`
- Paths: `categories/{slug}/` → `uk/categories/{slug}/`
- Output: `{slug}_ru.md` → `{slug}_uk.md`
- Язык инструкций: русский → українська
- Примеры: русские → украинские
- Термины: резина→гума, мойка→миття, стекло→скло
- Version: v3.3 (синхронизировано с RU)
- References paths: `references/` → локальные (будут созданы)

**Step 3: Write UK file**

Write to `.claude/skills/uk-content-generator/skill.md`

**Step 4: Verify structure**

Проверить что все секции RU присутствуют в UK:
- [ ] Quick Start
- [ ] ПЕРВЫЙ КРОК: Визначити тип сторінки
- [ ] Комерційний vs Інфо інтент
- [ ] СТОП-ЛИСТ
- [ ] Режим "Без пруфів"
- [ ] Політика цифр
- [ ] Workflow
- [ ] LSI/Семантика
- [ ] Локалізація термінів
- [ ] Валідація
- [ ] Структура контенту
- [ ] SEO Rules
- [ ] Контроль тошноти
- [ ] Validation Checklist
- [ ] Self-Check
- [ ] Output

**Step 5: Commit**

```bash
git add .claude/skills/uk-content-generator/skill.md
git commit -m "feat(uk-skills): sync uk-content-generator with RU v3.3"
```

---

## Task 2: uk-generate-meta/skill.md

**Files:**
- Read: `.claude/skills/generate-meta/skill.md` (v15.0, 398 lines)
- Write: `.claude/skills/uk-generate-meta/skill.md`

**Step 1: Read RU source**

Read `.claude/skills/generate-meta/skill.md` полностью.

**Step 2: Adapt to UK**

Адаптировать:
- YAML header: name → `uk-generate-meta`
- Paths: `categories/{slug}/` → `uk/categories/{slug}/`
- Title formula: "купить" → "Купити"
- Description: "от производителя" → "від виробника"
- H1: без "Купити"
- Примеры: украинские
- Version: v15.0

**Step 3: Write UK file**

Write to `.claude/skills/uk-generate-meta/skill.md`

**Step 4: Verify structure**

Проверить секции:
- [ ] January 2026 SEO Rules
- [ ] Терміни та джерела істини
- [ ] Producer vs Shop pattern
- [ ] IRON RULE
- [ ] Title (50-60 chars)
- [ ] Description (100-160 chars)
- [ ] H1
- [ ] JSON Output Format
- [ ] Workflow
- [ ] Validation Checklist
- [ ] Red Flags

**Step 5: Commit**

```bash
git add .claude/skills/uk-generate-meta/skill.md
git commit -m "feat(uk-skills): sync uk-generate-meta with RU v15.0"
```

---

## Task 3: uk-quality-gate/skill.md

**Files:**
- Read: `.claude/skills/quality-gate/skill.md` (v3.0, 328 lines)
- Write: `.claude/skills/uk-quality-gate/skill.md`

**Step 1: Read RU source**

Read `.claude/skills/quality-gate/skill.md` полностью.

**Step 2: Adapt to UK**

Адаптировать:
- YAML header: name → `uk-quality-gate`
- Paths: `uk/categories/{slug}/`
- Commands: `/quality-gate` → `/uk-quality-gate`
- Валидация: украинские скрипты с `--lang uk`
- Термины: украинские
- Version: v3.0

**Step 3: Write UK file**

Write to `.claude/skills/uk-quality-gate/skill.md`

**Step 4: Verify structure**

Проверить секции:
- [ ] Input Requirements
- [ ] Validation Checklist (Data, Meta, Content, SEO, Terminology)
- [ ] Workflow
- [ ] Pass Criteria
- [ ] Common Issues
- [ ] Output

**Step 5: Commit**

```bash
git add .claude/skills/uk-quality-gate/skill.md
git commit -m "feat(uk-skills): sync uk-quality-gate with RU v3.0"
```

---

## Task 4: uk-seo-research/skill.md

**Files:**
- Read: `.claude/skills/seo-research/SKILL.md` (v13.0, 338 lines)
- Write: `.claude/skills/uk-seo-research/skill.md`

**Step 1: Read RU source**

Read `.claude/skills/seo-research/SKILL.md` полностью.

**Step 2: Adapt to UK**

Адаптировать:
- YAML header: name → `uk-seo-research`
- Paths: `uk/categories/{slug}/research/`
- Язык промпта для Perplexity: українська
- Примеры: украинские
- References: локальные пути
- Version: v13.0

**Step 3: Write UK file**

Write to `.claude/skills/uk-seo-research/skill.md`

**Step 4: Verify structure**

Проверить секции:
- [ ] Quick Start
- [ ] Workflow
- [ ] Джерела даних
- [ ] Структура RESEARCH_PROMPT.md
- [ ] Блок 2: Правила класифікації
- [ ] Блок 6а: Спірні твердження
- [ ] Вимоги до відповіді
- [ ] Шаблон виводу
- [ ] Структура RESEARCH_DATA.md
- [ ] Критерій готовності
- [ ] References

**Step 5: Commit**

```bash
git add .claude/skills/uk-seo-research/skill.md
git commit -m "feat(uk-skills): sync uk-seo-research with RU v13.0"
```

---

## Task 5: uk-deploy-to-opencart/skill.md

**Files:**
- Read: `.claude/skills/deploy-to-opencart/SKILL.md` (v3.0, 192 lines)
- Write: `.claude/skills/uk-deploy-to-opencart/skill.md`

**Step 1: Read RU source**

Read `.claude/skills/deploy-to-opencart/SKILL.md` полностью.

**Step 2: Adapt to UK**

Адаптировать:
- YAML header: name → `uk-deploy-to-opencart`
- Paths: `uk/categories/{slug}/`
- SQL: `language_id=1` only
- Deploy folder: `deploy/uk/`
- Version: v3.0

**Step 3: Write UK file**

Write to `.claude/skills/uk-deploy-to-opencart/skill.md`

**Step 4: Verify structure**

Проверить секции:
- [ ] Input Validation
- [ ] Quick Start
- [ ] Workflow
- [ ] Category Mapping (UK names)
- [ ] Safety Rules
- [ ] Output
- [ ] Troubleshooting

**Step 5: Commit**

```bash
git add .claude/skills/uk-deploy-to-opencart/skill.md
git commit -m "feat(uk-skills): sync uk-deploy-to-opencart with RU v3.0"
```

---

## Task 6: uk-content-reviewer/SKILL.md (NEW)

**Files:**
- Read: `.claude/skills/content-reviewer/SKILL.md` (223 lines)
- Create: `.claude/skills/uk-content-reviewer/SKILL.md`

**Step 1: Read RU source**

Read `.claude/skills/content-reviewer/SKILL.md` полностью.

**Step 2: Adapt to UK**

Адаптировать:
- YAML header: name → `uk-content-reviewer`
- Paths: `uk/categories/{slug}/content/{slug}_uk.md`
- Термины: украинские
- Чеклисты: украинские
- Version: v1.0 (based on RU)

**Step 3: Create UK folder and file**

```bash
mkdir -p .claude/skills/uk-content-reviewer
```

Write to `.claude/skills/uk-content-reviewer/SKILL.md`

**Step 4: Verify structure**

Проверить секции (аналогично RU content-reviewer)

**Step 5: Commit**

```bash
git add .claude/skills/uk-content-reviewer/
git commit -m "feat(uk-skills): create uk-content-reviewer skill"
```

---

## Task 7-12: References для uk-content-generator

### Task 7: references/buyer-guide.md

**Files:**
- Read: `.claude/skills/content-generator/references/buyer-guide.md`
- Create: `.claude/skills/uk-content-generator/references/buyer-guide.md`

**Steps:**
1. Read RU source
2. Adapt: язык → українська, термины → UK, примеры → украинские
3. Write UK file
4. Commit

```bash
git add .claude/skills/uk-content-generator/references/buyer-guide.md
git commit -m "feat(uk-skills): add uk-content-generator/references/buyer-guide.md"
```

### Task 8: references/hub-pages.md

**Files:**
- Read: `.claude/skills/content-generator/references/hub-pages.md`
- Create: `.claude/skills/uk-content-generator/references/hub-pages.md`

**Steps:** Аналогично Task 7

```bash
git commit -m "feat(uk-skills): add uk-content-generator/references/hub-pages.md"
```

### Task 9: references/templates.md

**Files:**
- Read: `.claude/skills/content-generator/references/templates.md`
- Create: `.claude/skills/uk-content-generator/references/templates.md`

**Steps:** Аналогично Task 7

```bash
git commit -m "feat(uk-skills): add uk-content-generator/references/templates.md"
```

### Task 10: references/validation.md

**Files:**
- Read: `.claude/skills/content-generator/references/validation.md`
- Create: `.claude/skills/uk-content-generator/references/validation.md`

**Steps:** Аналогично Task 7

```bash
git commit -m "feat(uk-skills): add uk-content-generator/references/validation.md"
```

### Task 11: references/research-mapping.md

**Files:**
- Read: `.claude/skills/content-generator/references/research-mapping.md`
- Create: `.claude/skills/uk-content-generator/references/research-mapping.md`

**Steps:** Аналогично Task 7

```bash
git commit -m "feat(uk-skills): add uk-content-generator/references/research-mapping.md"
```

### Task 12: references/lsi-synonyms.md

**Files:**
- Read: `.claude/skills/content-generator/references/lsi-synonyms.md`
- Read: `.claude/skills/uk-content-generator/references/uk-lsi-synonyms.md` (существующий)
- Create: `.claude/skills/uk-content-generator/references/lsi-synonyms.md`

**Steps:**
1. Read RU source
2. Read existing UK uk-lsi-synonyms.md
3. Объединить: RU структура + UK синонимы
4. Write merged file
5. Delete old uk-lsi-synonyms.md (или оставить для совместимости)
6. Commit

```bash
git add .claude/skills/uk-content-generator/references/lsi-synonyms.md
git commit -m "feat(uk-skills): add uk-content-generator/references/lsi-synonyms.md (merged)"
```

---

## Task 13-15: References для uk-seo-research

### Task 13: references/category-matrix.md

**Files:**
- Read: `.claude/skills/seo-research/references/category-matrix.md`
- Create: `.claude/skills/uk-seo-research/references/category-matrix.md`

**Steps:**
1. Create folder: `mkdir -p .claude/skills/uk-seo-research/references`
2. Read RU source
3. Adapt: язык → українська
4. Write UK file
5. Commit

```bash
git add .claude/skills/uk-seo-research/references/category-matrix.md
git commit -m "feat(uk-skills): add uk-seo-research/references/category-matrix.md"
```

### Task 14: references/example-output.md

**Files:**
- Read: `.claude/skills/seo-research/references/example-output.md`
- Create: `.claude/skills/uk-seo-research/references/example-output.md`

**Steps:** Аналогично Task 13

```bash
git commit -m "feat(uk-skills): add uk-seo-research/references/example-output.md"
```

### Task 15: references/perplexity-space-instructions.md

**Files:**
- Read: `.claude/skills/seo-research/references/perplexity-space-instructions.md`
- Create: `.claude/skills/uk-seo-research/references/perplexity-space-instructions.md`

**Steps:** Аналогично Task 13

```bash
git commit -m "feat(uk-skills): add uk-seo-research/references/perplexity-space-instructions.md"
```

---

## Task 16: uk-generate-meta/REFERENCE.md

**Files:**
- Read: `.claude/skills/generate-meta/REFERENCE.md`
- Create: `.claude/skills/uk-generate-meta/REFERENCE.md`

**Steps:**
1. Read RU source
2. Adapt: язык → українська, примеры → украинские
3. Write UK file
4. Commit

```bash
git add .claude/skills/uk-generate-meta/REFERENCE.md
git commit -m "feat(uk-skills): add uk-generate-meta/REFERENCE.md"
```

---

## Final Task: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Steps:**
1. Обновить версии UK скиллов в таблице
2. Добавить uk-content-reviewer в список
3. Commit

```bash
git add CLAUDE.md
git commit -m "docs: update UK skills versions in CLAUDE.md"
```

---

## Summary

| Batch | Tasks | Files |
|-------|-------|-------|
| 1: Main skills | 1-6 | 6 |
| 2: uk-content-generator refs | 7-12 | 6 |
| 3: uk-seo-research refs | 13-15 | 3 |
| 4: Additional | 16 | 1 |
| Final | CLAUDE.md | 1 |
| **Total** | **17** | **17** |

---

**Готово к выполнению.**
