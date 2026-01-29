# Glavnaya + Audit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать категорию glavnaya (54 HOME ключа) и провести аудит всех 52 категорий.

**Architecture:** Фаза 1 — создание glavnaya через category-init + добавление ключей. Фаза 2 — 6 параллельных воркеров проверяют релевантность ключей в своих группах категорий.

**Tech Stack:** JSON, Edit tool, spawn-claude

---

## Task 1: Создать категорию glavnaya

**Files:**
- Create: `categories/glavnaya/data/glavnaya_clean.json`
- Create: `categories/glavnaya/meta/` (пустая папка)
- Create: `categories/glavnaya/content/` (пустая папка)
- Create: `categories/glavnaya/research/` (пустая папка)

**Step 1: Создать структуру папок**

```bash
mkdir -p categories/glavnaya/{data,meta,content,research}
```

**Step 2: Создать glavnaya_clean.json**

```json
{
  "id": "glavnaya",
  "name": "Главная",
  "type": "category",
  "parent_id": null,
  "keywords": [
    {"keyword": "автохимия", "volume": 2400},
    {"keyword": "авто химия", "volume": 2400},
    {"keyword": "автокосметика", "volume": 480},
    {"keyword": "магазин автохимии", "volume": 390},
    {"keyword": "автохимия для авто", "volume": 140},
    {"keyword": "автохимия для автомобиля", "volume": 140},
    {"keyword": "химия для автомобиля", "volume": 140},
    {"keyword": "косметика для авто", "volume": 90},
    {"keyword": "косметика для автомобиля", "volume": 90},
    {"keyword": "автодетейлинг", "volume": 90},
    {"keyword": "автокосметика для авто", "volume": 70},
    {"keyword": "автокосметика для автомобиля", "volume": 70},
    {"keyword": "химия для машины", "volume": 50}
  ],
  "synonyms": [
    {"keyword": "химия для детейлинга", "volume": 40},
    {"keyword": "магазин автокосметики", "volume": 40},
    {"keyword": "косметика для машин", "volume": 40},
    {"keyword": "детейлинг магазин киев", "volume": 30},
    {"keyword": "химия автомобильная", "volume": 30},
    {"keyword": "автохимия купить", "volume": 70, "use_in": "meta_only"},
    {"keyword": "купить химию для автомобиля", "volume": 20, "use_in": "meta_only"},
    {"keyword": "купить химию для авто", "volume": 20, "use_in": "meta_only"},
    {"keyword": "автокосметика купить", "volume": 10, "use_in": "meta_only"},
    {"keyword": "автокосметика для детейлинга", "volume": 10},
    {"keyword": "автохимия для детейлинга", "volume": 10},
    {"keyword": "автокосметика купить киев", "volume": 10, "use_in": "meta_only"},
    {"keyword": "автохимия для автомобиля интернет магазин", "volume": 10},
    {"keyword": "автохимия и автокосметика интернет магазин", "volume": 10},
    {"keyword": "автохимия интернет магазин", "volume": 10},
    {"keyword": "детейлинг шоп", "volume": 10},
    {"keyword": "автохимия каталог", "volume": 10},
    {"keyword": "автокосметика для автомобиля интернет магазин", "volume": 10},
    {"keyword": "автокосметика киев", "volume": 10},
    {"keyword": "автокосметика профессиональная", "volume": 10},
    {"keyword": "автохимия киев интернет магазин", "volume": 10},
    {"keyword": "автохимия купить киев", "volume": 10, "use_in": "meta_only"},
    {"keyword": "магазин автохимии киев", "volume": 10},
    {"keyword": "автокосметика цены", "volume": 10, "use_in": "meta_only"},
    {"keyword": "автохимия цена", "volume": 10, "use_in": "meta_only"},
    {"keyword": "автокосметика для машины", "volume": 10},
    {"keyword": "автохимия и косметика", "volume": 10},
    {"keyword": "автокосметика автохимия", "volume": 10},
    {"keyword": "автокосметика купить в украине", "volume": 10, "use_in": "meta_only"},
    {"keyword": "интернет магазин автокосметики", "volume": 10},
    {"keyword": "профессиональная автохимия и автокосметика", "volume": 10},
    {"keyword": "химия для автомоек киев", "volume": 10},
    {"keyword": "косметика для автомобиля купить", "volume": 10, "use_in": "meta_only"},
    {"keyword": "где купить автохимию", "volume": 10, "use_in": "meta_only"},
    {"keyword": "продажа автохимии", "volume": 10},
    {"keyword": "автомобильная косметика", "volume": 10},
    {"keyword": "детейлинг химия", "volume": 10},
    {"keyword": "профессиональная химия для автомоек", "volume": 10},
    {"keyword": "купить химию для автомойки", "volume": 10, "use_in": "meta_only"},
    {"keyword": "каталог автокосметики", "volume": 10},
    {"keyword": "элитная автокосметика", "volume": 10}
  ],
  "variations": [],
  "entities": ["автохимия", "автокосметика", "детейлинг", "уход за авто"],
  "micro_intents": [],
  "source": "manual-import-home"
}
```

**Step 3: Проверить JSON валидность**

```bash
python3 -c "import json; json.load(open('categories/glavnaya/data/glavnaya_clean.json'))" && echo "✅ Valid"
```

---

## Task 2: Обновить CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Обновить количество категорий**

Заменить "52 RU категории" на "53 RU категории".

---

## Task 3: Аудит aksessuary/* (10 категорий)

**Worker:** W1

**Категории:**
1. `categories/aksessuary/data/aksessuary_clean.json`
2. `categories/aksessuary/aksessuary-dlya-naneseniya-sredstv/data/aksessuary-dlya-naneseniya-sredstv_clean.json`
3. `categories/aksessuary/gubki-i-varezhki/data/gubki-i-varezhki_clean.json`
4. `categories/aksessuary/malyarniy-skotch/data/malyarniy-skotch_clean.json`
5. `categories/aksessuary/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json`
6. `categories/aksessuary/nabory/data/nabory_clean.json`
7. `categories/aksessuary/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json`
8. `categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json`
9. `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/data/shchetka-dlya-moyki-avto_clean.json`
10. `categories/aksessuary/vedra-i-emkosti/data/vedra-i-emkosti_clean.json`

**Инструкция:**
1. Прочитать каждый _clean.json
2. Проверить что каждый ключ релевантен категории
3. Проверить классификацию (keyword vs synonym vs meta_only)
4. Исправить ошибки через Edit
5. Отчёт: `✅ {slug}: OK` или `⚠️ {slug}: исправлено X ключей`

---

## Task 4: Аудит moyka-i-eksterer/* (17 категорий)

**Worker:** W2

**Категории:**
1. `categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json`
2. `categories/moyka-i-eksterer/avtoshampuni/data/avtoshampuni_clean.json`
3. `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json`
4. `categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/data/shampuni-dlya-ruchnoy-moyki_clean.json`
5. `categories/moyka-i-eksterer/ochistiteli-dvigatelya/data/ochistiteli-dvigatelya_clean.json`
6. `categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/data/antibitum_clean.json`
7. `categories/moyka-i-eksterer/ochistiteli-kuzova/antimoshka/data/antimoshka_clean.json`
8. `categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json`
9. `categories/moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli/data/obezzhirivateli_clean.json`
10. `categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/data/ukhod-za-naruzhnym-plastikom_clean.json`
11. `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/data/cherniteli-shin_clean.json`
12. `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/data/keramika-dlya-diskov_clean.json`
13. `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov/data/ochistiteli-diskov_clean.json`
14. `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin/data/ochistiteli-shin_clean.json`
15. `categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/data/antidozhd_clean.json`
16. `categories/moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol/data/ochistiteli-stekol_clean.json`
17. `categories/moyka-i-eksterer/sredstva-dlya-stekol/omyvatel/data/omyvatel_clean.json`

**Инструкция:** Аналогично Task 3

---

## Task 5: Аудит ukhod-za-intererom/* (8 категорий)

**Worker:** W3

**Категории:**
1. `categories/ukhod-za-intererom/data/ukhod-za-intererom_clean.json`
2. `categories/ukhod-za-intererom/neytralizatory-zapakha/data/neytralizatory-zapakha_clean.json`
3. `categories/ukhod-za-intererom/poliroli-dlya-plastika/data/poliroli-dlya-plastika_clean.json`
4. `categories/ukhod-za-intererom/pyatnovyvoditeli/data/pyatnovyvoditeli_clean.json`
5. `categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/data/sredstva-dlya-khimchistki-salona_clean.json`
6. `categories/ukhod-za-intererom/sredstva-dlya-kozhi/data/sredstva-dlya-kozhi_clean.json`
7. `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi/data/ochistiteli-kozhi_clean.json`
8. `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/data/ukhod-za-kozhey_clean.json`

**Инструкция:** Аналогично Task 3

---

## Task 6: Аудит zashchitnye-pokrytiya/* (7 категорий)

**Worker:** W4

**Категории:**
1. `categories/zashchitnye-pokrytiya/data/zashchitnye-pokrytiya_clean.json`
2. `categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json`
3. `categories/zashchitnye-pokrytiya/kvik-deteylery/data/kvik-deteylery_clean.json`
4. `categories/zashchitnye-pokrytiya/silanty/data/silanty_clean.json`
5. `categories/zashchitnye-pokrytiya/voski/data/voski_clean.json`
6. `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/data/tverdyy-vosk_clean.json`
7. `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/data/zhidkiy-vosk_clean.json`

**Инструкция:** Аналогично Task 3

---

## Task 7: Аудит polirovka/* (6 категорий)

**Worker:** W5

**Категории:**
1. `categories/polirovka/data/polirovka_clean.json`
2. `categories/polirovka/polirovalnye-krugi/data/polirovalnye-krugi_clean.json`
3. `categories/polirovka/polirovalnye-krugi/mekhovye/data/mekhovye_clean.json`
4. `categories/polirovka/polirovalnye-mashinki/data/polirovalnye-mashinki_clean.json`
5. `categories/polirovka/polirovalnye-mashinki/akkumulyatornaya/data/akkumulyatornaya_clean.json`
6. `categories/polirovka/polirovalnye-pasty/data/polirovalnye-pasty_clean.json`

**Инструкция:** Аналогично Task 3

---

## Task 8: Аудит oborudovanie/*, opt-i-b2b, glavnaya (4 категории)

**Worker:** W6

**Категории:**
1. `categories/oborudovanie/data/oborudovanie_clean.json`
2. `categories/oborudovanie/apparaty-tornador/data/apparaty-tornador_clean.json`
3. `categories/opt-i-b2b/data/opt-i-b2b_clean.json`
4. `categories/glavnaya/data/glavnaya_clean.json`

**Инструкция:** Аналогично Task 3

---

## Task 9: Финальная проверка и коммит

**Step 1: Валидация всех JSON**

```bash
find categories -name "*_clean.json" -exec python3 -c "import json; json.load(open('{}'))" \; && echo "✅ All JSON valid"
```

**Step 2: Commit**

```bash
git add categories/
git add CLAUDE.md
git commit -m "feat: add glavnaya category + audit 53 categories

- Created glavnaya with 54 HOME keywords
- Audited all categories for keyword relevance
- Fixed misplaced keywords where found

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

**Step 3: Push**

```bash
git push
```

---

## Parallel Execution

```
/parallel docs/plans/2026-01-29-glavnaya-and-audit-plan.md
W1: 3
W2: 4
W3: 5
W4: 6
W5: 7
W6: 8
```

Оркестратор выполняет Task 1, 2, 9.
