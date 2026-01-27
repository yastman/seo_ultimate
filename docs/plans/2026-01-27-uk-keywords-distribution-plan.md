# UK Keywords Distribution Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Розподілити 356 UK ключів з CSV по 52 категоріях з ручною перевіркою кожної.

**Architecture:** Генеруємо чек-лист `tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md` з автоматичним маппінгом ключів по категоріях. Користувач перевіряє кожну категорію вручну, потім ключі застосовуються до `_clean.json`.

**Tech Stack:** Markdown checklist, manual review workflow

---

## Task 1: Згенерувати чек-лист

**Files:**
- Create: `tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md`
- Read: `uk/data/uk_keywords_source.csv`
- Read: `docs/plans/2026-01-27-uk-keywords-distribution-design.md` (маппінг)

**Step 1: Прочитати CSV та згрупувати ключі по категоріях**

Використати маппінг з дизайну:
- `піна` → aktivnaya-pena
- `антидощ` → antidozhd
- і т.д.

Пріоритет: специфічне > загальне (напр. "твердий віск" > "віск")

**Step 2: Створити чек-лист з секціями по категоріях**

Формат секції:
```markdown
## {slug}

**Запропоновані ключі:**
- [ ] `ключ` (volume)
- [ ] `ключ2` (volume)

**Статус:** ⏳ Очікує перевірки
```

**Step 3: Додати прогрес-трекер зверху**

```markdown
## Прогрес
- [ ] aktivnaya-pena (N ключів)
- [ ] antidozhd (N ключів)
...
```

**Step 4: Commit**

```bash
git add tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md
git commit -m "task(uk): generate keywords distribution checklist"
```

---

## Task 2: Ручна перевірка (USER ACTION)

**Це робить користувач, не Claude:**

1. Відкрити `tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md`
2. По кожній категорії:
   - Перевірити чи ключі відповідають категорії
   - Поставити `[x]` для правильних
   - Видалити або перенести неправильні
3. Оновити статус категорії на ✅

**Виконується поетапно — категорія за категорією.**

---

## Task 3: Застосувати ключі до _clean.json (per category)

**Виконується ПІСЛЯ ручної перевірки категорії.**

**Files:**
- Read: `tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md` (підтверджені ключі)
- Modify: `uk/categories/{slug}/data/{slug}_clean.json`

**Step 1: Витягти підтверджені ключі**

Парсити чек-лист, знайти `- [x]` записи для категорії.

**Step 2: Оновити keywords в _clean.json**

```json
{
  "keywords": [
    {"keyword": "ключ з чек-листа", "volume": 1600},
    ...
  ]
}
```

**Step 3: Commit**

```bash
git add uk/categories/{slug}/data/{slug}_clean.json
git commit -m "keywords(uk): apply verified keywords to {slug}"
```

**Повторити для кожної підтвердженої категорії.**

---

## Execution Notes

- **Task 1** — виконує Claude (генерація чек-листа)
- **Task 2** — виконує USER (ручна перевірка)
- **Task 3** — виконує Claude по команді `/apply-uk-keywords {slug}`

**Порядок категорій:** По пріоритету (volume), починаючи з найбільших:
1. aktivnaya-pena (піна — багато ключів)
2. sredstva-dlya-khimchistki-salona (салон — багато ключів)
3. voski (віск)
4. polirovka (полірування)
5. ... решта за алфавітом
