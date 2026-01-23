# UK antidozhd Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать полный UK контент для категории antidozhd

**Architecture:** Последовательный вызов UK скиллов: init → meta → research → content → review → gate → deploy

**Tech Stack:** UK skills pipeline v2.1

---

## Task 1: Инициализация UK структуры

**Команда:**
```
/uk-content-init antidozhd
```

**Ожидаемый результат:**
- `uk/categories/antidozhd/data/antidozhd_clean.json`
- `uk/categories/antidozhd/meta/` (пустая)
- `uk/categories/antidozhd/content/` (пустая)
- `uk/categories/antidozhd/research/CONTEXT.md`

---

## Task 2: Генерация UK мета-тегов

**Команда:**
```
/uk-generate-meta antidozhd
```

**Ожидаемый результат:**
- `uk/categories/antidozhd/meta/antidozhd_meta.json`
- Title, Description, H1 на украинском
- keywords_in_content заполнен

---

## Task 3: SEO Research промпт

**Команда:**
```
/uk-seo-research antidozhd
```

**Ожидаемый результат:**
- `uk/categories/antidozhd/research/RESEARCH_PROMPT.md`

**Ручной шаг:** Запустить промпт в Perplexity, сохранить в `RESEARCH_DATA.md`
(или использовать RU research как fallback)

---

## Task 4: Генерация UK контента

**Команда:**
```
/uk-content-generator antidozhd
```

**Ожидаемый результат:**
- `uk/categories/antidozhd/content/antidozhd_uk.md`
- Buyer guide формат, 400-700 слов

---

## Task 5: Ревизия контента

**Команда (агент):**
```
uk-content-reviewer antidozhd
```

**Ожидаемый результат:**
- Исправленный `antidozhd_uk.md`
- Плотность ключей 1-3%
- H2 с ключами

---

## Task 6: Quality Gate

**Команда:**
```
/uk-quality-gate antidozhd
```

**Ожидаемый результат:**
- PASS со всеми проверками

---

## Task 7: Deploy

**Команда:**
```
/uk-deploy antidozhd
```

**Ожидаемый результат:**
- Мета и контент в OpenCart (language_id=1)

---

## Task 8: Отметить в TODO

**Действие:** В `tasks/TODO_UK_CONTENT.md` отметить `[x] antidozhd`

**Commit:**
```bash
git add uk/categories/antidozhd/ tasks/TODO_UK_CONTENT.md
git commit -m "feat(uk): add antidozhd category content"
```
