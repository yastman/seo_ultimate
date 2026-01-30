# Sync Volume from Master Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Обновить частотность (volume) ключей в _clean.json файлах из data/ru_semantics_master.csv. Только обновление volume — без добавления/удаления ключей.

**Architecture:** Для каждой категории: прочитать master CSV, найти ключи которые есть в JSON, обновить volume если отличается.

**Tech Stack:** Read tool для CSV/JSON, Edit tool для обновления volume

---

## Алгоритм для каждой категории

**Step 1:** Прочитать `data/ru_semantics_master.csv`, построить словарь `{keyword: volume}` для category={slug}

**Step 2:** Прочитать `categories/.../data/{slug}_clean.json`

**Step 3:** Для каждого ключа в `keywords[]` и `synonyms[]`:
- Найти в словаре master
- Если volume отличается → обновить через Edit tool
- Записать в лог: `"keyword": old_volume → new_volume`

**Step 4:** Валидировать JSON: `python3 -c "import json; json.load(open('file.json'))"`

**Step 5:** Записать итог в лог

---

## ВАЖНО

- **НЕ добавлять** новые ключи — только обновлять volume существующих
- **НЕ удалять** ключи которых нет в master
- **НЕ менять** порядок ключей, use_in, другие поля
- Если ключ есть в JSON но нет в master — оставить как есть, записать в лог "не найден в master"
- После каждой категории — валидировать JSON

---

## Task 1: W1 — aksessuary cluster (10 категорий)

**Категории:**
- aksessuary
- aksessuary-dlya-naneseniya-sredstv
- gubki-i-varezhki
- malyarniy-skotch
- mikrofibra-i-tryapki
- nabory
- raspyliteli-i-penniki
- kisti-dlya-deteylinga
- shchetka-dlya-moyki-avto
- vedra-i-emkosti

**Лог:** `data/generated/audit-logs/W1_volume_sync.md`

---

## Task 2: W2 — moyka-i-eksterer/avtoshampuni + ochistiteli (9 категорий)

**Категории:**
- moyka-i-eksterer
- avtoshampuni
- aktivnaya-pena
- shampuni-dlya-ruchnoy-moyki
- ochistiteli-dvigatelya
- antibitum
- antimoshka
- glina-i-avtoskraby
- obezzhirivateli

**Лог:** `data/generated/audit-logs/W2_volume_sync.md`

---

## Task 3: W3 — moyka-i-eksterer остальные (9 категорий)

**Категории:**
- ukhod-za-naruzhnym-plastikom
- cherniteli-shin
- keramika-dlya-diskov
- ochistiteli-diskov
- ochistiteli-shin
- antidozhd
- ochistiteli-stekol
- omyvatel
- polirol-dlya-stekla

**Лог:** `data/generated/audit-logs/W3_volume_sync.md`

---

## Task 4: W4 — ukhod-za-intererom (8 категорий)

**Категории:**
- ukhod-za-intererom
- neytralizatory-zapakha
- poliroli-dlya-plastika
- pyatnovyvoditeli
- sredstva-dlya-khimchistki-salona
- sredstva-dlya-kozhi
- ochistiteli-kozhi
- ukhod-za-kozhey

**Лог:** `data/generated/audit-logs/W4_volume_sync.md`

---

## Task 5: W5 — polirovka (6 категорий)

**Категории:**
- polirovka
- polirovalnye-pasty
- akkumulyatornaya
- mekhovye

**Лог:** `data/generated/audit-logs/W5_volume_sync.md`

---

## Task 6: W6 — zashchitnye-pokrytiya + остальные (9 категорий)

**Категории:**
- zashchitnye-pokrytiya
- keramika-i-zhidkoe-steklo
- kvik-deteylery
- silanty
- voski
- tverdyy-vosk
- zhidkiy-vosk
- oborudovanie
- apparaty-tornador
- opt-i-b2b

**Лог:** `data/generated/audit-logs/W6_volume_sync.md`

---

## Формат лога

```markdown
# W{N} Volume Sync Log

## {category-slug}
- Обновлено N ключей:
  - "keyword1": 100 → 150
  - "keyword2": 50 → 70
- Без изменений: M ключей

**Итого:** X ключей обновлено
```

---

## Важно

- НЕ добавлять новые ключи — только обновлять volume существующих
- НЕ удалять ключи
- Если ключ есть в master но нет в JSON — записать в лог как "не найден"
- Валидировать JSON после изменений
