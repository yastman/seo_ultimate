---
name: verify-content
description: Интерактивная верификация контента категории перед продакшеном. Use when /verify-content {slug}, проверь контент, верифицируй текст, pre-production QA. Отличается от content-reviewer субагента интерактивностью — человек контролирует каждый шаг и решает что исправлять.
---

# Verify Content

Интерактивная проверка контента категории с контролем человека на каждом шаге.

## Input

```
/verify-content {path}
/verify-content moyka-i-eksterer/avtoshampuni/aktivnaya-pena
```

## Data Files

```
categories/{path}/
├── content/{slug}_ru.md        # Контент для проверки
├── research/RESEARCH_DATA.md   # Источник истины для фактов
├── meta/{slug}_meta.json       # Keywords для проверки
└── data/{slug}_clean.json      # name (для H1)
```

---

## Workflow

### Phase 1: Load & Overview

1. Read all 4 files in parallel
2. Show summary:

```
## Overview: {slug}

**Type:** Hub Page / Product Page (parent_id = null → Hub)
**Content:** X words, Y sections (H2)
**Primary keywords:** keyword1, keyword2, keyword3
**Research date:** YYYY-MM-DD (from git or file date)
```

---

### Phase 2: Facts Verification

**Extract ALL concrete claims:**
- Numbers: %, time, sizes, pH, temperatures
- Comparisons: "X better than Y"
- Technical facts

**Check each in RESEARCH_DATA.md:**
- ✅ VERIFIED — found in research
- ⚠️ UNVERIFIED — not in research (where from?)
- ❌ CONTRADICTION — conflicts with research

**Output format:**

```
## Facts Verification

| # | Факт | Строка | Research | Статус |
|---|------|--------|----------|--------|
| 1 | "pH 12-13" | 34 | line 45 | ✅ |
| 2 | "95% эффективность" | 56 | NOT FOUND | ⚠️ |
| 3 | "безопасен для резины" | 78 | line 89 противоречит | ❌ |

⚠️ Found 2 issues. Fix now? [Y/n]
```

**Wait for user response before proceeding.**

---

### Phase 3: AI Patterns Detection

1. Прочитать `references/ai-patterns.md` для списка паттернов
2. Искать каждый паттерн в контенте
3. Показать находки

**Output format:**

```
## AI Patterns

| Строка | Тип | Текст |
|--------|-----|-------|
| 15 | Linguistic | "Важно отметить, что..." |
| 42 | Empty | "Качество играет важную роль..." |

Found 2 AI patterns. Show context? [Y/n]
```

---

### Phase 4: Keywords Coverage

1. Get keywords from `_meta.json` → `keywords_in_content`
2. Search each in content (any declension OK)
3. Show coverage

**Output format:**

```
## Keywords Coverage

Primary (need 100%):
- ✅ "активная пена" — found 5×
- ❌ "пена для бесконтактной мойки" — NOT FOUND

Secondary (need ≥80%): ✅ 4/5 (80%)
Supporting (need ≥80%): ✅ 6/7 (86%)

⚠️ 1 primary keyword missing. Add? [Y/n]
```

---

### Phase 5: Quality Checklist

**Present to user:**

```
## Quality Checklist

Answer each:

Intro:
- [ ] Clear what's being sold in 5 sec?
- [ ] Buyer focus (not dictionary definition)?
- [ ] H1 = name from _clean.json?

Structure:
- [ ] Logical section order?
- [ ] H2 help navigation?

Tables:
- [ ] Answer "what to choose"?
- [ ] No duplication between tables?

FAQ:
- [ ] Questions are real (buyer would ask)?
- [ ] Don't duplicate main text?

Overall:
- [ ] Reads smoothly out loud?
- [ ] Know what to buy after reading?
```

---

### Phase 6: Verdict & Actions

```
## Verdict

| Aspect | Status |
|--------|--------|
| Facts | ⚠️ 1 contradiction |
| AI Patterns | ⚠️ 2 found |
| Keywords | ⚠️ 1 missing |
| Quality | ✅ Good |

**VERDICT: ⚠️ NEEDS FIXES**

Actions:
1. [F] Fix facts
2. [A] Remove AI patterns
3. [K] Add keywords
4. [S] Skip (keep as-is)
5. [N] Next category
```

**Wait for user choice.**

---

### Phase 7: Fix Mode

If user chooses to fix:

1. Show exact location
2. Propose fix
3. User confirms or edits
4. Apply Edit tool
5. Return to verdict

**Example:**

```
## Fix: Contradiction at line 78

Current:
> "Безопасен для любой резины"

Research (line 89):
> "Избегать контакта с резиновыми уплотнителями"

Proposed fix:
> "Безопасен для большинства материалов. На резиновых
> уплотнителях рекомендуется предварительный тест."

Apply this fix? [Y/n/edit]
```

---

## Key Principles

1. **Interactive** — wait for user at each decision point
2. **Transparent** — show where data comes from
3. **User controls** — skill proposes, user decides
4. **Research = truth** — facts verified only against research
5. **No silent fixes** — always ask before Edit

---

## vs content-reviewer (subagent)

| Aspect | content-reviewer | verify-content |
|--------|------------------|----------------|
| Mode | Autonomous | Interactive |
| Control | Minimal | Full |
| Fixes | Automatic | On request |
| Speed | Fast (batch) | Thorough |
| Use case | Mass revision | Pre-prod QA |
