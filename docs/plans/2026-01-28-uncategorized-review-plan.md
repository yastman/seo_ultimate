# Uncategorized Keywords Review Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Распределить 451 uncategorized ключ по RU категориям через ручной ревью и импорт в _clean.json.

**Architecture:** 9 файлов для ревью разбиты по тематикам. Пользователь заполняет decision, Claude импортирует в _clean.json категорий. Master CSV не изменяется.

**Tech Stack:** Markdown файлы для ревью, Python для импорта, JSON для _clean.json.

**Design:** `docs/plans/2026-01-28-uncategorized-review-design.md`

---

## Параллельные задачи (ручной ревью)

Задачи 1-8 можно выполнять параллельно. Каждая задача — заполнить decision в файле.

---

### Task 1: Ревью — Полировочные машинки (44 ключа)

**Files:**
- Review: `data/generated/review/01_polirovochnye_mashinki.md`
- Target: `categories/polirovka/data/polirovka_clean.json`

**Step 1: Открыть файл**

Открой `data/generated/review/01_polirovochnye_mashinki.md` в редакторе.

**Step 2: Заполнить decision**

Для каждого ключа укажи категорию:
- `polirovka` — корневая категория полировки
- `HOME` — главная страница
- `NEW:polirovalnye-mashinki` — если нужна новая L2 категория
- (пусто) — пропустить

**Step 3: Сохранить файл**

---

### Task 2: Ревью — Круги для полировки (27 ключей)

**Files:**
- Review: `data/generated/review/02_krugi_dlya_polirovki.md`
- Target: `categories/polirovka/polirovalnye-krugi/data/polirovalnye-krugi_clean.json` или `mekhovye_clean.json`

**Step 1: Открыть файл**

Открой `data/generated/review/02_krugi_dlya_polirovki.md` в редакторе.

**Step 2: Заполнить decision**

Категории:
- `polirovalnye-krugi` — L2 категория (общая)
- `mekhovye` — L3 категория (меховые круги)
- `NEW:porolonvye` — если нужны поролоновые круги

**Step 3: Сохранить файл**

---

### Task 3: Ревью — Пасты (13 ключей)

**Files:**
- Review: `data/generated/review/03_pasty.md`
- Target: `categories/polirovka/polirovalnye-pasty/data/polirovalnye-pasty_clean.json`

**Step 1: Открыть файл**

Открой `data/generated/review/03_pasty.md` в редакторе.

**Step 2: Заполнить decision**

Категория: `polirovalnye-pasty`

**Step 3: Сохранить файл**

---

### Task 4: Ревью — Воск (15 ключей)

**Files:**
- Review: `data/generated/review/04_vosk.md`
- Target: `categories/zashchitnye-pokrytiya/voski/data/voski_clean.json`

**Step 1: Открыть файл**

Открой `data/generated/review/04_vosk.md` в редакторе.

**Step 2: Заполнить decision**

Категории:
- `voski` — L2 общая
- `tverdyy-vosk` — L3 твердый воск
- `zhidkiy-vosk` — L3 жидкий воск

**Step 3: Сохранить файл**

---

### Task 5: Ревью — Тряпки/микрофибра (0 ключей)

**Files:**
- Review: `data/generated/review/05_tryapki_mikrofibra.md`

**Status:** SKIP — файл пустой (все ключи уже в категории mikrofibra-i-tryapki)

---

### Task 6: Ревью — Химчистка (38 ключей)

**Files:**
- Review: `data/generated/review/06_khimchistka.md`
- Target: `categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/data/sredstva-dlya-khimchistki-salona_clean.json`

**Step 1: Открыть файл**

Открой `data/generated/review/06_khimchistka.md` в редакторе.

**Step 2: Заполнить decision**

Категории:
- `sredstva-dlya-khimchistki-salona` — химчистка салона
- `pyatnovyvoditeli` — пятновыводители
- `ukhod-za-intererom` — уход за интерьером (общая)

**Step 3: Сохранить файл**

---

### Task 7: Ревью — Автохимия/автокосметика (47 ключей)

**Files:**
- Review: `data/generated/review/07_avtokhimiya.md`
- Target: Главная страница или `opt-i-b2b`

**Step 1: Открыть файл**

Открой `data/generated/review/07_avtokhimiya.md` в редакторе.

**Step 2: Заполнить decision**

Категории:
- `HOME` — главная страница (автохимия, автокосметика, магазин)
- `opt-i-b2b` — оптовые запросы
- (пусто) — пропустить общие запросы

**Step 3: Сохранить файл**

---

### Task 8: Ревью — Губки/щётки (31 ключ)

**Files:**
- Review: `data/generated/review/08_gubki_shchetki.md`
- Target: `categories/aksessuary/*/data/*_clean.json`

**Step 1: Открыть файл**

Открой `data/generated/review/08_gubki_shchetki.md` в редакторе.

**Step 2: Заполнить decision**

Категории:
- `gubki-i-varezhki` — губки и варежки
- `shchetka-dlya-moyki-avto` — щётки для мойки
- `kisti-dlya-deteylinga` — кисти для детейлинга
- `aksessuary` — аксессуары (общая)

**Step 3: Сохранить файл**

---

### Task 9: Ревью — Прочее (236 ключей)

**Files:**
- Review: `data/generated/review/09_prochee.md`
- Target: Различные категории

**Step 1: Открыть файл**

Открой `data/generated/review/09_prochee.md` в редакторе.

**Step 2: Заполнить decision**

Просмотри каждый ключ и определи категорию по содержанию. Используй список категорий в файле.

**Step 3: Сохранить файл**

---

## Последовательные задачи (после ревью)

### Task 10: Импорт в _clean.json

**Prerequisite:** Tasks 1-9 завершены (decision заполнены)

**Step 1: Запустить импорт**

Claude читает все файлы `data/generated/review/*.md`, парсит decision и добавляет ключи в соответствующие _clean.json.

**Step 2: Проверить результат**

```bash
python3 scripts/extract_all_keywords.py
python3 scripts/compare_with_master.py
```

**Step 3: Отчёт**

Показать сколько ключей добавлено в каждую категорию.

---

### Task 11: Создание новых категорий (если есть NEW:)

**Prerequisite:** Task 10 завершён, выявлены NEW:{slug}

**Step 1: Создать структуру**

Для каждого `NEW:{slug}` создать папку и _clean.json.

**Step 2: Добавить ключи**

Добавить ключи с decision=NEW:{slug} в новую категорию.

---

### Task 12: Создание HOME категории (главная страница RU)

**Prerequisite:** Task 10 завершён, есть ключи с decision=HOME

**Step 1: Создать структуру**

```
categories/home/
└── data/
    └── home_clean.json
```

**Step 2: Добавить ключи**

Добавить ключи с decision=HOME.

---

## Checklist

**Параллельные (ручной ревью):**
- [ ] Task 1: Полировочные машинки (44)
- [ ] Task 2: Круги для полировки (27)
- [ ] Task 3: Пасты (13)
- [ ] Task 4: Воск (15)
- [ ] Task 5: Тряпки (SKIP - 0)
- [ ] Task 6: Химчистка (38)
- [ ] Task 7: Автохимия (47)
- [ ] Task 8: Губки/щётки (31)
- [ ] Task 9: Прочее (236)

**Последовательные:**
- [ ] Task 10: Импорт в _clean.json
- [ ] Task 11: Создание новых категорий
- [ ] Task 12: Создание HOME категории
