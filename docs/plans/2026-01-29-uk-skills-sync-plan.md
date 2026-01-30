# UK Skills Sync Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Синхронизировать UK формулу Title со стандартом RU и исправить 5 WARNING в meta-валидации.

**Architecture:** Исправляем формулу в 4 скилл-файлах, затем регенерируем 3 meta-файла с короткими Title и убираем marketing fluff из 3 description.

**Tech Stack:** Markdown skills, JSON meta files, Python validate_meta.py

---

## Task 1: Исправить формулу Title в uk-generate-meta

**Files:**
- Modify: `.claude/skills/uk-generate-meta/skill.md:158-176`

**Step 1: Прочитать текущую формулу**

Найти секцию "Адаптивна формула:" (строки 158-176).

**Step 2: Заменить формулу**

Старое:
```
ЯКЩО primary_keyword ≤ 20 chars:
  Купити {primary_keyword} в Україні | Ultimate

ІНАКШЕ:
  {primary_keyword} — купити, ціни | Ultimate
```

Новое:
```
ЯКЩО primary_keyword ≤ 20 chars:
  {primary_keyword} — купити в інтернет-магазині Ultimate

ІНАКШЕ:
  {primary_keyword} — купити, ціни | Ultimate
```

**Step 3: Заменить таблицу примеров**

Старое:
```
| силант | 6 | Купити силант в Україні \| Ultimate |
| віск для авто | 13 | Купити віск для авто в Україні \| Ultimate |
| полірувальна машинка | 20 | Купити полірувальну машинку в Україні \| Ultimate |
```

Новое:
```
| силант | 6 | Силант — купити в інтернет-магазині Ultimate |
| віск для авто | 13 | Віск для авто — купити в інтернет-магазині Ultimate |
| полірувальна машинка | 20 | Полірувальна машинка — купити в інтернет-магазині Ultimate |
```

**Step 4: Заменить JSON Output Format**

Строка 282, старое:
```json
"title": "Купити {primary_keyword} в Україні | Ultimate",
```

Новое:
```json
"title": "{primary_keyword} — купити в інтернет-магазині Ultimate",
```

**Step 5: Обновить версию**

Добавить в Changelog:
```
**Changelog v16.1:**
- 🔧 Синхронізовано формулу Title з RU: "в інтернет-магазині" замість "в Україні"
- 📏 Виправлено Front-loading: ключ на початку, не "Купити"
```

---

## Task 2: Исправить формулу в uk-content-init

**Files:**
- Modify: `.claude/skills/uk-content-init/skill.md:122,131`

**Step 1: Найти строку 122**

Старое:
```
**Title formula:** `Купити {primary} в Україні | Ultimate`
```

Новое:
```
**Title formula:** `{primary} — купити в інтернет-магазині Ultimate`
```

**Step 2: Найти строку 131 (JSON пример)**

Старое:
```json
"title": "Купити {Primary} в Україні | Ultimate",
```

Новое:
```json
"title": "{Primary} — купити в інтернет-магазині Ultimate",
```

---

## Task 3: Исправить пример в quality-gate

**Files:**
- Modify: `.claude/skills/quality-gate/skill.md:283`

**Step 1: Найти строку 283**

Старое:
```
| Title | "Купити" ОБОВ'ЯЗКОВО | "Купити активну піну в Україні \| Ultimate" |
```

Новое:
```
| Title | primary_keyword на початку | "Активна піна — купити в інтернет-магазині Ultimate" |
```

---

## Task 4: Проверить uk-quality-gate

**Files:**
- Check: `.claude/skills/uk-quality-gate/skill.md`

**Step 1: Найти упоминания "в Україні"**

```bash
grep -n "в Україні" .claude/skills/uk-quality-gate/skill.md
```

**Step 2: Если найдено — исправить аналогично Task 3**

---

## Task 5: Регенерировать silanty meta

**Files:**
- Modify: `uk/categories/silanty/meta/silanty_meta.json`

**Step 1: Прочитать _clean.json для primary_keyword**

```bash
cat uk/categories/silanty/data/silanty_clean.json | jq '.keywords[0]'
```

**Step 2: Обновить title**

Старое:
```json
"title": "Купити силант в Україні | Ultimate"
```

Новое (primary_keyword = "силант", 6 chars ≤ 20):
```json
"title": "Силант — купити в інтернет-магазині Ultimate"
```

**Step 3: Валидация**

```bash
python3 scripts/validate_meta.py uk/categories/silanty/meta/silanty_meta.json
```

Expected: PASS

---

## Task 6: Регенерировать ochistiteli-shin meta

**Files:**
- Modify: `uk/categories/ochistiteli-shin/meta/ochistiteli-shin_meta.json`

**Step 1: Прочитать primary_keyword**

```bash
cat uk/categories/ochistiteli-shin/data/ochistiteli-shin_clean.json | jq '.keywords | max_by(.volume)'
```

**Step 2: Обновить title**

Старое:
```json
"title": "Купити очищувач шин в Україні | Ultimate"
```

Новое (primary_keyword = "очищувач шин", 12 chars ≤ 20):
```json
"title": "Очищувач шин — купити в інтернет-магазині Ultimate"
```

**Step 3: Валидация**

```bash
python3 scripts/validate_meta.py uk/categories/ochistiteli-shin/meta/ochistiteli-shin_meta.json
```

Expected: PASS

---

## Task 7: Регенерировать omyvatel meta + убрать fluff

**Files:**
- Modify: `uk/categories/omyvatel/meta/omyvatel_meta.json`

**Step 1: Обновить title**

Старое:
```json
"title": "Купити омивач скла в Україні | Ultimate"
```

Новое (primary_keyword = "омивач скла", 11 chars ≤ 20):
```json
"title": "Омивач скла — купити в інтернет-магазині Ultimate"
```

**Step 2: Убрать fluff из description**

Старое:
```json
"description": "Омивач скла від виробника Ultimate. Зимовий та літній склоомивач — концентрати й готові до -30°C, без розводів. Опт і роздріб."
```

Новое (убрать "без розводів"):
```json
"description": "Омивач скла від виробника Ultimate. Зимовий та літній склоомивач — концентрати й готові до -30°C. Опт і роздріб."
```

**Step 3: Валидация**

```bash
python3 scripts/validate_meta.py uk/categories/omyvatel/meta/omyvatel_meta.json
```

Expected: PASS

---

## Task 8: Убрать fluff из kvik-deteylery

**Files:**
- Modify: `uk/categories/kvik-deteylery/meta/kvik-deteylery_meta.json`

**Step 1: Убрать "швидкого" из description**

Старое:
```json
"description": "Сухий туман для авто від виробника Ultimate. Квік-детейлери для миттєвого блиску — спреї для швидкого догляду. Опт і роздріб."
```

Новое:
```json
"description": "Сухий туман для авто від виробника Ultimate. Квік-детейлери для миттєвого блиску — спреї для догляду між мийками. Опт і роздріб."
```

**Step 2: Валидация**

```bash
python3 scripts/validate_meta.py uk/categories/kvik-deteylery/meta/kvik-deteylery_meta.json
```

Expected: PASS

---

## Task 9: Убрать fluff из ochistiteli-stekol

**Files:**
- Modify: `uk/categories/ochistiteli-stekol/meta/ochistiteli-stekol_meta.json`

**Step 1: Убрать "Без розводів" из description**

Старое:
```json
"description": "Очищувач скла від виробника Ultimate. Видалення жиру, пилу, відбитків — спреї 500мл, 1л та 5л. Без розводів. Опт і роздріб."
```

Новое:
```json
"description": "Очищувач скла від виробника Ultimate. Видалення жиру, пилу, відбитків — спреї 500мл, 1л та 5л. Опт і роздріб."
```

**Step 2: Валидация**

```bash
python3 scripts/validate_meta.py uk/categories/ochistiteli-stekol/meta/ochistiteli-stekol_meta.json
```

Expected: PASS

---

## Task 10: Финальная валидация всех meta

**Step 1: Запустить полную валидацию**

```bash
python3 scripts/validate_meta.py --all
```

**Expected output:**
```
Total files: 60
✅ PASS: 60
⚠️  WARNING: 0
❌ FAIL: 0
```

**Step 2: Если всё PASS — коммит**

```bash
git add .claude/skills/ uk/categories/*/meta/*_meta.json
git commit -m "fix(uk): sync Title formula with RU, fix 5 meta warnings

- uk-generate-meta: use 'в інтернет-магазині' instead of 'в Україні'
- Fix Front-loading: keyword first, not 'Купити'
- Remove marketing fluff from 3 descriptions
- Regenerate 3 short Title metas

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Summary

| Task | Файл | Действие |
|------|------|----------|
| 1 | uk-generate-meta/skill.md | Формула + примеры |
| 2 | uk-content-init/skill.md | Формула |
| 3 | quality-gate/skill.md | Пример |
| 4 | uk-quality-gate/skill.md | Проверить |
| 5 | silanty_meta.json | Title |
| 6 | ochistiteli-shin_meta.json | Title |
| 7 | omyvatel_meta.json | Title + fluff |
| 8 | kvik-deteylery_meta.json | fluff |
| 9 | ochistiteli-stekol_meta.json | fluff |
| 10 | Финальная валидация | Коммит |

---

**Version:** 1.0
**Date:** 2026-01-29
