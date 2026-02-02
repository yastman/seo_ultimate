# Fix Nausea After Coverage Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Добавить в скиллы content-reviewer и uk-content-reviewer автоматическую проверку и исправление тошноты (nausea) после добавления ключевых слов.

**Architecture:**
1. После каждого добавления ключей — re-check nausea
2. Если nausea >3.5 — применить synonym replacement из таблицы
3. Итеративный цикл: add keyword → check nausea → fix if needed → re-check

**Tech Stack:** Markdown skills, Python validators

---

## Проблема

При добавлении ключевых слов для улучшения coverage, тошнота растёт:
- UK aktivnaya-pena: coverage 27% → 72.7% ✅, но nausea 3.46 → 3.74 ❌
- RU aktivnaya-pena: nausea 3.46 → 3.74 ❌

Скиллы имеют инструкцию "Replace with synonyms", но:
1. Нет явного шага re-check после каждого fix
2. Нет конкретного алгоритма замены
3. Порог 3.5 — WARNING, а скиллы фиксят только BLOCKER (>4.0)

---

## Task 1: Добавить Nausea Auto-Fix секцию в content-reviewer.md

**Files:**
- Modify: `.claude/archive/agents/content-reviewer.md:225-240`

**Step 1: Прочитать текущую секцию BLOCKER Fixes**

```bash
sed -n '213,240p' .claude/archive/agents/content-reviewer.md
```

**Step 2: Добавить новую секцию после BLOCKER Fixes**

Вставить после строки 240 (после WARNING Fixes):

```markdown
---

## Nausea Auto-Fix Algorithm (v3.1)

**Когда применять:** После ЛЮБОГО добавления ключевых слов в текст.

### Workflow

```
1. Добавить ключ →
2. Запустить check_water_natasha.py →
3. Если nausea >3.5:
   a. Найти самое частое слово (из отчёта)
   b. Заменить 1-2 вхождения на синоним (таблица ниже)
   c. Re-check nausea
   d. Повторить до nausea ≤3.5
4. Максимум 3 итерации
```

### Таблица синонимов для разбавления

| Частое слово | Синонимы для замены |
|--------------|---------------------|
| средство | состав, продукт, препарат, формула |
| очиститель | состав, продукт, химия, препарат |
| пена | состав, средство, продукт, формула |
| мойка | очистка, уход, обработка |
| авто | машина, автомобиль, транспорт |
| поверхность | покрытие, основа, материал, слой |
| защита | барьер, слой, покрытие |
| воск | покрытие, защита, слой |

### Пример

```
❌ ДО (nausea 3.74, слово "пена" 14 раз):
"Активная пена для мойки... Пена размягчает... пена работает..."

✅ ПОСЛЕ (nausea 3.2):
"Активная пена для мойки... Состав размягчает... средство работает..."
```

### Правило замены

1. Заменять только **повторы**, не первое вхождение ключа
2. Primary keyword — НЕ ТРОГАТЬ (нужен для SEO)
3. Заменять generic слова, не ключевые фразы
```

**Step 3: Обновить Step 8 (Re-validate) — добавить nausea check**

Найти секцию "Step 8: Re-validate after fix" и добавить:

```markdown
### Step 8: Re-validate after fix

После исправлений запустить:

```bash
# 1. Density check
python3 scripts/check_keyword_density.py {content_path}

# 2. Nausea check (ОБЯЗАТЕЛЬНО после добавления ключей!)
python3 scripts/check_water_natasha.py {content_path}
# Если nausea >3.5 → применить Nausea Auto-Fix Algorithm

# 3. Coverage check
python3 scripts/audit_coverage.py --slug {slug} --lang ru --verbose

# 4. Content validation
python3 scripts/validate_content.py {content_path} "{primary}" --mode seo
```
```

**Step 4: Commit**

```bash
git add .claude/archive/agents/content-reviewer.md
git commit -m "feat(skill): add nausea auto-fix algorithm to content-reviewer"
```

---

## Task 2: Добавить Nausea Auto-Fix секцию в uk-content-reviewer.md

**Files:**
- Modify: `.claude/archive/agents/uk-content-reviewer.md`

**Step 1: Прочитать структуру файла**

```bash
grep -n "^## " .claude/archive/agents/uk-content-reviewer.md | head -20
```

**Step 2: Добавить секцию Nausea Auto-Fix (украинская версия)**

Вставить после секции "Synonyms for spam reduction":

```markdown
---

## Nausea Auto-Fix Algorithm (v2.2)

**Коли застосовувати:** Після БУДЬ-ЯКОГО додавання ключових слів у текст.

### Workflow

```
1. Додати ключ →
2. Запустити check_water_natasha.py →
3. Якщо nausea >3.5:
   a. Знайти найчастіше слово (з звіту)
   b. Замінити 1-2 входження на синонім (таблиця нижче)
   c. Re-check nausea
   d. Повторити до nausea ≤3.5
4. Максимум 3 ітерації
```

### Таблиця синонімів для розбавлення (UK)

| Часте слово | Синоніми для заміни |
|-------------|---------------------|
| засіб | склад, продукт, препарат, формула |
| очисник | склад, продукт, хімія, препарат |
| піна | склад, засіб, продукт, формула |
| мийка | очищення, догляд, обробка |
| авто | машина, автомобіль, транспорт |
| поверхня | покриття, основа, матеріал, шар |
| захист | бар'єр, шар, покриття |
| віск | покриття, захист, шар |

### Приклад

```
❌ ДО (nausea 3.74, слово "піна" 14 разів):
"Активна піна для миття... Піна розм'якшує... піна працює..."

✅ ПІСЛЯ (nausea 3.2):
"Активна піна для миття... Склад розм'якшує... засіб працює..."
```

### Правило заміни

1. Замінювати лише **повтори**, не перше входження ключа
2. Primary keyword — НЕ ЧІПАТИ (потрібен для SEO)
3. Замінювати generic слова, не ключові фрази
```

**Step 3: Обновить Step 10 (Re-validate) — добавить nausea check**

```markdown
### Step 10: Re-validate after fix

Після виправлень запустити:

```bash
# 1. Density check
python3 scripts/check_keyword_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk

# 2. Nausea check (ОБОВ'ЯЗКОВО після додавання ключів!)
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md
# Якщо nausea >3.5 → застосувати Nausea Auto-Fix Algorithm

# 3. Coverage check
python3 scripts/audit_coverage.py --slug {slug} --lang uk --verbose

# 4. Content validation
python3 scripts/validate_content.py uk/categories/{slug}/content/{slug}_uk.md "{primary_uk}" --mode seo
```
```

**Step 4: Commit**

```bash
git add .claude/archive/agents/uk-content-reviewer.md
git commit -m "feat(skill): add nausea auto-fix algorithm to uk-content-reviewer"
```

---

## Task 3: Добавить Nausea threshold в validation-checklist.md

**Files:**
- Modify: `.claude/skills/shared/validation-checklist.md`

**Step 1: Прочитать текущие SEO thresholds**

```bash
grep -A5 "SEO" .claude/skills/shared/validation-checklist.md
```

**Step 2: Обновить thresholds — сделать 3.5 явным WARNING**

Заменить:

```markdown
- [ ] Classic nausea ≤3.5 (BLOCKER >4.0)
```

На:

```markdown
- [ ] Classic nausea ≤3.5 (WARNING >3.5, BLOCKER >4.0)
- [ ] **After adding keywords:** Re-check nausea, apply synonym replacement if >3.5
```

**Step 3: Commit**

```bash
git add .claude/skills/shared/validation-checklist.md
git commit -m "feat(validation): add nausea re-check requirement after keyword insertion"
```

---

## Task 4: Тестирование на aktivnaya-pena

**Files:**
- Test: `uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md`

**Step 1: Проверить текущую nausea**

```bash
python3 scripts/check_water_natasha.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md 2>/dev/null | grep -E "ТОШНОТА|самое частое"
```

Expected: nausea ~3.74, частое слово — "піна" или "авто"

**Step 2: Применить synonym replacement вручную**

Найти повторы слова и заменить 2-3 на синонимы.

**Step 3: Re-check nausea**

```bash
python3 scripts/check_water_natasha.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md 2>/dev/null | grep -E "ТОШНОТА"
```

Expected: nausea ≤3.5

**Step 4: Verify coverage preserved**

```bash
python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --verbose
```

Expected: Coverage ≥72%

**Step 5: Commit test fix**

```bash
git add uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md
git commit -m "fix(uk): reduce nausea in aktivnaya-pena via synonym replacement"
```

---

## Task 5: Тестирование на RU aktivnaya-pena

**Files:**
- Test: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md`

**Step 1-5:** Аналогично Task 4, но для RU версии.

---

## Summary

После выполнения плана:
1. Скиллы будут автоматически проверять nausea после добавления ключей
2. Порог 3.5 станет явным WARNING с обязательным fix
3. Алгоритм synonym replacement будет документирован
4. Тексты aktivnaya-pena будут исправлены как proof-of-concept
