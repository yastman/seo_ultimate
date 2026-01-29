# Sync Volume from Master — Workers Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Обновить volume в _clean.json файлах из data/ru_semantics_master.csv. Только обновление существующих ключей — без добавления/удаления.

**Architecture:** Читаем master CSV, строим словарь {keyword: volume} для каждой категории. Затем для каждого JSON файла: находим ключи в keywords[] и synonyms[], сравниваем volume, обновляем если отличается.

**Tech Stack:** Read tool для CSV/JSON, Edit tool для обновления volume

---

## ПРАВИЛА (КРИТИЧЕСКИ ВАЖНО)

1. **ТОЛЬКО обновлять volume** — не добавлять/удалять ключи
2. **НЕ менять порядок ключей** — только значение `"volume": X`
3. **НЕ менять другие поля** — use_in, keyword остаются как есть
4. **Валидировать JSON** после каждой категории: `python3 -c "import json; json.load(open('file.json'))"`
5. **Писать лог** — каждое изменение записывать
6. **НЕ коммитить** — коммит делает оркестратор

---

## Task 1: W1 — aksessuary (10 файлов)

**Файлы:**
- `categories/aksessuary/data/aksessuary_clean.json`
- `categories/aksessuary/aksessuary-dlya-naneseniya-sredstv/data/aksessuary-dlya-naneseniya-sredstv_clean.json`
- `categories/aksessuary/gubki-i-varezhki/data/gubki-i-varezhki_clean.json`
- `categories/aksessuary/malyarniy-skotch/data/malyarniy-skotch_clean.json`
- `categories/aksessuary/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json`
- `categories/aksessuary/nabory/data/nabory_clean.json`
- `categories/aksessuary/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json`
- `categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json`
- `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/data/shchetka-dlya-moyki-avto_clean.json`
- `categories/aksessuary/vedra-i-emkosti/data/vedra-i-emkosti_clean.json`

**Лог:** `data/generated/audit-logs/W1_volume_sync.md`

**Step 1: Прочитать master CSV**

Read: `data/ru_semantics_master.csv`

Построить словарь для каждой категории из списка:
```
{slug} -> {keyword: volume, keyword2: volume2, ...}
```

**Step 2: Для каждого файла из списка**

a) Извлечь slug из имени файла (например `aksessuary_clean.json` → `aksessuary`)

b) Read JSON файл

c) Для каждого объекта в `keywords[]`:
   - Найти keyword в словаре master
   - Если найден И volume отличается:
     - Edit: заменить `"volume": OLD` на `"volume": NEW`
     - Записать в лог: `"keyword": OLD → NEW`

d) Для каждого объекта в `synonyms[]`:
   - То же самое

e) Валидировать JSON:
```bash
python3 -c "import json; json.load(open('categories/.../data/..._clean.json'))"
```

**Step 3: Записать лог**

Write: `data/generated/audit-logs/W1_volume_sync.md`

Формат:
```markdown
# W1 Volume Sync Log

## aksessuary
- Обновлено: 3 ключей
  - "аксессуары для мойки авто": 40 → 50
  - "аксессуары для детейлинга": 15 → 20
- Без изменений: 5 ключей

## aksessuary-dlya-naneseniya-sredstv
...

---
**Итого:** 10 файлов, X ключей обновлено
```

---

## Task 2: W2 — moyka-i-eksterer часть 1 (9 файлов)

**Файлы:**
- `categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json`
- `categories/moyka-i-eksterer/avtoshampuni/data/avtoshampuni_clean.json`
- `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json`
- `categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/data/shampuni-dlya-ruchnoy-moyki_clean.json`
- `categories/moyka-i-eksterer/ochistiteli-dvigatelya/data/ochistiteli-dvigatelya_clean.json`
- `categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/data/antibitum_clean.json`
- `categories/moyka-i-eksterer/ochistiteli-kuzova/antimoshka/data/antimoshka_clean.json`
- `categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json`
- `categories/moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli/data/obezzhirivateli_clean.json`

**Лог:** `data/generated/audit-logs/W2_volume_sync.md`

**Шаги:** Аналогично Task 1

---

## Task 3: W3 — moyka-i-eksterer часть 2 (9 файлов)

**Файлы:**
- `categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/data/ukhod-za-naruzhnym-plastikom_clean.json`
- `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/data/cherniteli-shin_clean.json`
- `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/data/keramika-dlya-diskov_clean.json`
- `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov/data/ochistiteli-diskov_clean.json`
- `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin/data/ochistiteli-shin_clean.json`
- `categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/data/antidozhd_clean.json`
- `categories/moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol/data/ochistiteli-stekol_clean.json`
- `categories/moyka-i-eksterer/sredstva-dlya-stekol/omyvatel/data/omyvatel_clean.json`
- `categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/data/polirol-dlya-stekla_clean.json`

**Лог:** `data/generated/audit-logs/W3_volume_sync.md`

**Шаги:** Аналогично Task 1

---

## Task 4: W4 — ukhod-za-intererom (8 файлов)

**Файлы:**
- `categories/ukhod-za-intererom/data/ukhod-za-intererom_clean.json`
- `categories/ukhod-za-intererom/neytralizatory-zapakha/data/neytralizatory-zapakha_clean.json`
- `categories/ukhod-za-intererom/poliroli-dlya-plastika/data/poliroli-dlya-plastika_clean.json`
- `categories/ukhod-za-intererom/pyatnovyvoditeli/data/pyatnovyvoditeli_clean.json`
- `categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/data/sredstva-dlya-khimchistki-salona_clean.json`
- `categories/ukhod-za-intererom/sredstva-dlya-kozhi/data/sredstva-dlya-kozhi_clean.json`
- `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi/data/ochistiteli-kozhi_clean.json`
- `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/data/ukhod-za-kozhey_clean.json`

**Лог:** `data/generated/audit-logs/W4_volume_sync.md`

**Шаги:** Аналогично Task 1

---

## Task 5: W5 — polirovka (6 файлов)

**Файлы:**
- `categories/polirovka/data/polirovka_clean.json`
- `categories/polirovka/polirovalnye-krugi/data/polirovalnye-krugi_clean.json`
- `categories/polirovka/polirovalnye-krugi/mekhovye/data/mekhovye_clean.json`
- `categories/polirovka/polirovalnye-mashinki/data/polirovalnye-mashinki_clean.json`
- `categories/polirovka/polirovalnye-mashinki/akkumulyatornaya/data/akkumulyatornaya_clean.json`
- `categories/polirovka/polirovalnye-pasty/data/polirovalnye-pasty_clean.json`

**Лог:** `data/generated/audit-logs/W5_volume_sync.md`

**Шаги:** Аналогично Task 1

---

## Task 6: W6 — zashchitnye-pokrytiya + остальные (11 файлов)

**Файлы:**
- `categories/zashchitnye-pokrytiya/data/zashchitnye-pokrytiya_clean.json`
- `categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json`
- `categories/zashchitnye-pokrytiya/kvik-deteylery/data/kvik-deteylery_clean.json`
- `categories/zashchitnye-pokrytiya/silanty/data/silanty_clean.json`
- `categories/zashchitnye-pokrytiya/voski/data/voski_clean.json`
- `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/data/tverdyy-vosk_clean.json`
- `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/data/zhidkiy-vosk_clean.json`
- `categories/oborudovanie/data/oborudovanie_clean.json`
- `categories/oborudovanie/apparaty-tornador/data/apparaty-tornador_clean.json`
- `categories/opt-i-b2b/data/opt-i-b2b_clean.json`
- `categories/glavnaya/data/glavnaya_clean.json`

**Лог:** `data/generated/audit-logs/W6_volume_sync.md`

**Шаги:** Аналогично Task 1

---

## Пример Edit для обновления volume

Если в JSON:
```json
{
  "keyword": "пена для мойки авто",
  "volume": 1000
}
```

И в master CSV volume = 1300, то:

```
Edit file: categories/.../aktivnaya-pena_clean.json
old_string: "volume": 1000
new_string: "volume": 1300
```

**ВАЖНО:** Убедиться что old_string уникален в контексте (включить keyword в old_string если нужно):
```
old_string: "keyword": "пена для мойки авто",
      "volume": 1000
new_string: "keyword": "пена для мойки авто",
      "volume": 1300
```
