# UK Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать полный UK pipeline, зеркалирующий RU pipeline — скиллы и субагенты для украинских категорий.

**Architecture:** Каждый UK скилл/агент = копия RU версии с заменой путей (`categories/` → `uk/categories/`), языка (`ru` → `uk`), терминологии (резина→гума). Используем `skill-creator` и `subagent-creator` для создания.

**Tech Stack:** Claude Code skills/agents, Bash, Python validators

---

## Task 1: Удаление uk-content-adapter

**Files:**
- Delete: `.claude/skills/uk-content-adapter/` (вся папка)
- Delete: `.claude/agents/uk-content-adapter.md`

**Step 1: Удалить скилл uk-content-adapter**

```bash
rm -rf .claude/skills/uk-content-adapter/
```

**Step 2: Удалить агент uk-content-adapter**

```bash
rm -f .claude/agents/uk-content-adapter.md
```

**Step 3: Проверить удаление**

```bash
ls .claude/skills/ | grep uk-content
ls .claude/agents/ | grep uk-content-adapter
```

Expected: Нет файлов `uk-content-adapter`

**Step 4: Commit**

```bash
git add -A && git commit -m "chore: remove uk-content-adapter (replaced by uk-content-generator)"
```

---

## Task 2: Создать скилл uk-seo-research

**Files:**
- Create: `.claude/skills/uk-seo-research/skill.md`
- Reference: `.claude/skills/seo-research/skill.md`

**Step 1: Создать папку**

```bash
mkdir -p .claude/skills/uk-seo-research
```

**Step 2: Создать скилл через skill-creator**

Вызвать `/skill-creator` с параметрами:

```
name: uk-seo-research
description: >-
  Генерує контекстний промпт для Perplexity Deep Research на основі семантики UK категорії
  та узагальнених характеристик товарів. Аналізує uk/.../data/{slug}_clean.json та PRODUCTS_LIST.md,
  витягує типи форм/баз/ефектів, створює RESEARCH_PROMPT.md.
  Use when /uk-seo-research, дослідження UK категорії, research для UK.

Базовый скилл: seo-research
Изменения:
- Пути: categories/{slug}/ → uk/categories/{slug}/
- Язык инструкций: украинский
- Output: uk/categories/{slug}/research/RESEARCH_PROMPT.md
```

**Step 3: Проверить создание**

```bash
cat .claude/skills/uk-seo-research/skill.md | head -20
```

Expected: Файл существует, начинается с `---` и содержит `name: uk-seo-research`

**Step 4: Commit**

```bash
git add .claude/skills/uk-seo-research/ && git commit -m "feat(skills): add uk-seo-research skill"
```

---

## Task 3: Создать скилл uk-content-generator

**Files:**
- Create: `.claude/skills/uk-content-generator/skill.md`
- Reference: `.claude/skills/content-generator/skill.md`

**Step 1: Создать папку**

```bash
mkdir -p .claude/skills/uk-content-generator
```

**Step 2: Создать скилл через skill-creator**

Вызвать `/skill-creator` с параметрами:

```
name: uk-content-generator
description: >-
  Генерує SEO-контент у форматі buyer guide для UK категорій Ultimate.net.ua.
  Без посилань/цитат у тексті. Спірні твердження пом'якшувати. Research — лише як довідка.
  Use when: /uk-content-generator, напиши UK текст, згенеруй UK контент, створи контент для UK категорії.
  ВАЖЛИВО: використовувати ПІСЛЯ завершення /uk-seo-research.

Базовый скилл: content-generator v3.2
Изменения:
- Пути: categories/{slug}/ → uk/categories/{slug}/
- Язык контента: украинский
- Output: uk/categories/{slug}/content/{slug}_uk.md
- Терминология: резина→гума, мойка→миття, стекло→скло
- H1: БЕЗ "Купити" (только в Title)
```

**Step 3: Проверить создание**

```bash
cat .claude/skills/uk-content-generator/skill.md | head -20
```

**Step 4: Commit**

```bash
git add .claude/skills/uk-content-generator/ && git commit -m "feat(skills): add uk-content-generator skill"
```

---

## Task 4: Создать скилл uk-quality-gate

**Files:**
- Create: `.claude/skills/uk-quality-gate/skill.md`
- Reference: `.claude/skills/quality-gate/skill.md`

**Step 1: Создать папку**

```bash
mkdir -p .claude/skills/uk-quality-gate
```

**Step 2: Создать скилл через skill-creator**

Вызвать `/skill-creator` с параметрами:

```
name: uk-quality-gate
description: >-
  Фінальна валідація UK категорії перед деплоєм. Перевіряє дані, мета, контент, термінологію.
  Use when /uk-quality-gate, перевір UK категорію, фінальна перевірка UK, валідація UK перед деплоєм.

Базовый скилл: quality-gate v2.0
Изменения:
- Пути: categories/{slug}/ → uk/categories/{slug}/
- Язык отчёта: украинский
- Проверки: резина→гума, Title содержит "Купити", H1 БЕЗ "Купити"
- Output: uk/categories/{slug}/QUALITY_REPORT.md
```

**Step 3: Проверить создание**

```bash
cat .claude/skills/uk-quality-gate/skill.md | head -20
```

**Step 4: Commit**

```bash
git add .claude/skills/uk-quality-gate/ && git commit -m "feat(skills): add uk-quality-gate skill"
```

---

## Task 5: Создать скилл uk-deploy-to-opencart

**Files:**
- Create: `.claude/skills/uk-deploy-to-opencart/skill.md`
- Reference: `.claude/skills/deploy-to-opencart/skill.md`

**Step 1: Создать папку**

```bash
mkdir -p .claude/skills/uk-deploy-to-opencart
```

**Step 2: Создать скилл через skill-creator**

Вызвать `/skill-creator` с параметрами:

```
name: uk-deploy-to-opencart
description: >-
  Деплой UK мета-тегів та контенту в OpenCart. Оновлює language_id=1 (українська).
  Use when /uk-deploy, залий UK на сайт, деплой UK мета, оновити UK на сайті.

Базовый скилл: deploy-to-opencart v3.0
Изменения:
- Пути: uk/categories/{slug}/
- language_id: 1 (UK) вместо 3 (RU)
- SQL: UPDATE только для language_id=1
```

**Step 3: Проверить создание**

```bash
cat .claude/skills/uk-deploy-to-opencart/skill.md | head -20
```

**Step 4: Commit**

```bash
git add .claude/skills/uk-deploy-to-opencart/ && git commit -m "feat(skills): add uk-deploy-to-opencart skill"
```

---

## Task 6: Создать субагент uk-seo-research

**Files:**
- Create: `.claude/agents/uk-seo-research.md`
- Reference: `.claude/agents/seo-research.md`

**Step 1: Создать агент через subagent-creator**

Вызвать `/subagent-creator` с параметрами:

```
name: uk-seo-research
description: Генерує RESEARCH_PROMPT.md для Perplexity Deep Research (UK). Use when потрібно дослідити UK категорію, зібрати дані для UK, підготувати промпт для UK ресерчу.
tools: Read, Grep, Glob, Bash, Write
model: opus

Базовый агент: seo-research.md
Изменения:
- Пути: uk/categories/{slug}/
- Язык: украинский
```

**Step 2: Проверить создание**

```bash
cat .claude/agents/uk-seo-research.md | head -20
```

**Step 3: Commit**

```bash
git add .claude/agents/uk-seo-research.md && git commit -m "feat(agents): add uk-seo-research agent"
```

---

## Task 7: Создать субагент uk-content-generator

**Files:**
- Create: `.claude/agents/uk-content-generator.md`
- Reference: `.claude/agents/content-generator.md`

**Step 1: Создать агент через subagent-creator**

Вызвать `/subagent-creator` с параметрами:

```
name: uk-content-generator
description: Генерує SEO buyer guide контент для UK категорій Ultimate.net.ua. Без посилань/цитат. Use when /uk-content-generator, напиши UK текст, згенеруй UK контент.
tools: Read, Grep, Glob, Bash, Write
model: opus

Базовый агент: content-generator.md
Изменения:
- Пути: uk/categories/{slug}/
- Язык контента: украинский
- Терминология: резина→гума, мойка→миття
```

**Step 2: Проверить создание**

```bash
cat .claude/agents/uk-content-generator.md | head -20
```

**Step 3: Commit**

```bash
git add .claude/agents/uk-content-generator.md && git commit -m "feat(agents): add uk-content-generator agent"
```

---

## Task 8: Создать субагент uk-quality-gate

**Files:**
- Create: `.claude/agents/uk-quality-gate.md`
- Reference: `.claude/agents/quality-gate.md`

**Step 1: Создать агент через subagent-creator**

Вызвать `/subagent-creator` с параметрами:

```
name: uk-quality-gate
description: Фінальна валідація UK категорії перед деплоєм. Use when /uk-quality-gate, перевір UK категорію, фінальна перевірка UK.
tools: Read, Grep, Glob, Bash, Write
model: opus

Базовый агент: quality-gate.md
Изменения:
- Пути: uk/categories/{slug}/
- UK-specific проверки: резина→гума, Купити в Title
```

**Step 2: Проверить создание**

```bash
cat .claude/agents/uk-quality-gate.md | head -20
```

**Step 3: Commit**

```bash
git add .claude/agents/uk-quality-gate.md && git commit -m "feat(agents): add uk-quality-gate agent"
```

---

## Task 9: Создать субагент uk-deploy-to-opencart

**Files:**
- Create: `.claude/agents/uk-deploy-to-opencart.md`
- Reference: `.claude/agents/deploy-to-opencart.md`

**Step 1: Создать агент через subagent-creator**

Вызвать `/subagent-creator` с параметрами:

```
name: uk-deploy-to-opencart
description: Деплой UK мета-тегів та контенту в OpenCart. Use when /uk-deploy, залий UK на сайт, деплой UK мета.
tools: Read, Grep, Glob, Bash, Write
model: opus

Базовый агент: deploy-to-opencart.md
Изменения:
- Пути: uk/categories/{slug}/
- language_id: 1 (UK)
```

**Step 2: Проверить создание**

```bash
cat .claude/agents/uk-deploy-to-opencart.md | head -20
```

**Step 3: Commit**

```bash
git add .claude/agents/uk-deploy-to-opencart.md && git commit -m "feat(agents): add uk-deploy-to-opencart agent"
```

---

## Task 10: Синхронизировать uk-generate-meta

**Files:**
- Modify: `.claude/skills/uk-generate-meta/skill.md`
- Modify: `.claude/agents/uk-generate-meta.md`
- Reference: `.claude/skills/generate-meta/skill.md` (v15.0)

**Step 1: Сравнить версии**

```bash
wc -l .claude/skills/generate-meta/skill.md
wc -l .claude/skills/uk-generate-meta/skill.md
```

**Step 2: Обновить uk-generate-meta скилл**

Добавить недостающие элементы из generate-meta v15.0:
- IRON RULE секция
- Producer vs Shop pattern
- Red Flags таблица
- Validation Checklist

**Step 3: Обновить uk-generate-meta агент**

Синхронизировать с агентом generate-meta.md

**Step 4: Проверить**

```bash
grep -c "IRON RULE" .claude/skills/uk-generate-meta/skill.md
grep -c "Producer" .claude/skills/uk-generate-meta/skill.md
```

Expected: Оба > 0

**Step 5: Commit**

```bash
git add .claude/skills/uk-generate-meta/ .claude/agents/uk-generate-meta.md && git commit -m "feat(uk): sync uk-generate-meta with v15.0"
```

---

## Task 11: Обновить CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Добавить UK Pipeline секцию**

Добавить после RU Pipeline:

```markdown
## UK Pipeline

| Когда использовать | Команда | Описание |
| ------------------ | ------- | -------- |
| UK категория нужна | `/uk-category-init {slug}` | Создаёт UK структуру папок |
| UK мета-теги | `/uk-generate-meta {slug}` | Генерирует UK мета |
| UK research | `/uk-seo-research {slug}` | Промпт для Perplexity UK |
| UK контент | `/uk-content-generator {slug}` | Генерирует UK buyer guide |
| UK ревизия | `uk-content-reviewer {slug}` | Проверяет UK контент |
| UK валидация | `/uk-quality-gate {slug}` | Финальная проверка UK |
| UK деплой | `/uk-deploy {slug}` | Деплой UK на сайт |
```

**Step 2: Обновить версию**

Увеличить версию CLAUDE.md до 37.0

**Step 3: Проверить**

```bash
grep "UK Pipeline" CLAUDE.md
grep "Version:" CLAUDE.md
```

**Step 4: Commit**

```bash
git add CLAUDE.md && git commit -m "docs: add UK Pipeline to CLAUDE.md v37.0"
```

---

## Task 12: Финальная проверка

**Step 1: Проверить все UK скиллы**

```bash
ls -la .claude/skills/ | grep uk-
```

Expected:
- uk-content-generator/
- uk-content-init/
- uk-generate-meta/
- uk-keywords-export/
- uk-keywords-import/
- uk-quality-gate/
- uk-seo-research/
- uk-deploy-to-opencart/

**Step 2: Проверить все UK агенты**

```bash
ls -la .claude/agents/ | grep uk-
```

Expected:
- uk-category-init.md
- uk-content-generator.md
- uk-content-reviewer.md
- uk-generate-meta.md
- uk-keywords-export.md
- uk-keywords-import.md
- uk-quality-gate.md
- uk-seo-research.md
- uk-deploy-to-opencart.md

**Step 3: Проверить отсутствие uk-content-adapter**

```bash
ls .claude/skills/ | grep uk-content-adapter
ls .claude/agents/ | grep uk-content-adapter
```

Expected: Нет результатов

**Step 4: Финальный коммит**

```bash
git add -A && git commit -m "feat: complete UK pipeline sync v2.0"
```

---

## Acceptance Criteria

- [ ] `uk-content-adapter` удалён (скилл + агент)
- [ ] 4 новых скилла созданы: uk-seo-research, uk-content-generator, uk-quality-gate, uk-deploy-to-opencart
- [ ] 4 новых агента созданы: uk-seo-research, uk-content-generator, uk-quality-gate, uk-deploy-to-opencart
- [ ] uk-generate-meta синхронизирован с v15.0
- [ ] CLAUDE.md содержит UK Pipeline секцию
- [ ] Все коммиты созданы

---

**Version:** 1.0 — 2026-01-22
