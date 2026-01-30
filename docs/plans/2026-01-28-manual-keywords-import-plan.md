# Manual Keywords Import Plan (No Scripts)

> **For Claude:** Ручной импорт ключей через Edit tool. Каждый воркер работает со своей группой категорий.

**Goal:** Добавить ~390 ключей из review файлов в _clean.json категорий (без скриптов).

**Architecture:** Воркеры читают review MD файлы, извлекают ключи для своих категорий, проверяют дубликаты вручную, добавляют через Edit tool.

**Источники:** `data/generated/review/*.md` (10 файлов, 451 ключ, ~58 HOME пропускаем)

---

## Правила импорта

### Формат записи в _clean.json
```json
{"keyword": "ключевое слово", "volume": 1000}
{"keyword": "купить что-то", "volume": 200, "use_in": "meta_only"}
```

### Классификация ключей
| Условие | Куда добавлять |
|---------|----------------|
| Volume ≥ 50, основное значение | `keywords[]` |
| Volume < 50 или вариация | `synonyms[]` |
| Содержит: купить, цена, заказать, стоимость | `synonyms[]` с `"use_in": "meta_only"` |

### Проверка дубликатов
Перед добавлением проверить что ключ НЕ существует в:
- `keywords[]`
- `synonyms[]`
- `variations[]`

### Сортировка
После добавления — сортировать по убыванию `volume`.

---

## Task 1: Worker 1 — Полировка (polirovka/*)

**Категории:**
- `categories/polirovka/polirovalnye-pasty/data/polirovalnye-pasty_clean.json`
- `categories/polirovka/polirovalnye-mashinki/data/polirovalnye-mashinki_clean.json`
- `categories/polirovka/polirovalnye-mashinki/akkumulyatornaya/data/akkumulyatornaya_clean.json`
- `categories/polirovka/polirovalnye-krugi/data/polirovalnye-krugi_clean.json`
- `categories/polirovka/polirovalnye-krugi/mekhovye/data/mekhovye_clean.json`
- `categories/polirovka/data/polirovka_clean.json`

**Review файлы для поиска:**
- `data/generated/review/01_polirovochnye_mashinki.md`
- `data/generated/review/02_krugi_dlya_polirovki.md`
- `data/generated/review/03_pasty.md`

**Шаги:**
1. Открыть review файл
2. Найти строки с decision = `polirovalnye-pasty`, `polirovalnye-mashinki`, `polirovalnye-krugi`, `polirovka`, `akkumulyatornaya`, `mekhovye`
3. Для каждой категории:
   - Прочитать _clean.json
   - Проверить какие ключи уже есть
   - Добавить новые через Edit (сортировка по volume)
4. Проверить JSON валидность

---

## Task 2: Worker 2 — Мойка экстерьер (moyka-i-eksterer/*)

**Категории:**
- `aktivnaya-pena` (~38 ключей)
- `avtoshampuni` (~9)
- `shampuni-dlya-ruchnoy-moyki`
- `ochistiteli-dvigatelya` (~21)
- `ochistiteli-diskov` (~12)
- `ochistiteli-stekol`
- `glina-i-avtoskraby` (~11)
- `antibitum`, `antimoshka`
- `obezzhirivateli`
- `cherniteli-shin` (~6)
- `ochistiteli-shin`
- `omyvatel` (~7)
- `antidozhd`
- `moyka-i-eksterer` (~27)

**Review файлы:**
- `data/generated/review/09_prochee_part1.md`
- `data/generated/review/09_prochee_part2.md`
- `data/generated/review/09_prochee_part3.md`

**Шаги:** Аналогично Task 1

---

## Task 3: Worker 3 — Уход за интерьером (ukhod-za-intererom/*)

**Категории:**
- `sredstva-dlya-khimchistki-salona` (~46 ключей)
- `sredstva-dlya-kozhi` (~9)
- `ochistiteli-kozhi`
- `ukhod-za-kozhey` (~11)
- `poliroli-dlya-plastika`
- `neytralizatory-zapakha` (~12)
- `pyatnovyvoditeli`
- `ukhod-za-intererom`

**Review файлы:**
- `data/generated/review/06_khimchistka.md`
- `data/generated/review/07_avtokhimiya.md`
- `data/generated/review/09_prochee_part1.md`
- `data/generated/review/09_prochee_part2.md`
- `data/generated/review/09_prochee_part3.md`

---

## Task 4: Worker 4 — Защитные покрытия (zashchitnye-pokrytiya/*)

**Категории:**
- `tverdyy-vosk` (~11 ключей)
- `zhidkiy-vosk`
- `voski`
- `keramika-i-zhidkoe-steklo` (~8)
- `silanty`
- `kvik-deteylery`
- `zashchitnye-pokrytiya`

**Review файлы:**
- `data/generated/review/04_vosk.md`
- `data/generated/review/09_prochee_part1.md`
- `data/generated/review/09_prochee_part3.md`

---

## Task 5: Worker 5 — Аксессуары (aksessuary/*)

**Категории:**
- `gubki-i-varezhki` (~17 ключей)
- `shchetka-dlya-moyki-avto` (~10)
- `kisti-dlya-deteylinga`
- `mikrofibra-i-tryapki`
- `nabory` (~23)
- `raspyliteli-i-penniki` (~6)
- `vedra-i-emkosti`
- `malyarniy-skotch` (~5)
- `aksessuary-dlya-naneseniya-sredstv`
- `aksessuary`

**Review файлы:**
- `data/generated/review/08_gubki_shchetki.md`
- `data/generated/review/09_prochee_part1.md`
- `data/generated/review/09_prochee_part2.md`
- `data/generated/review/09_prochee_part3.md`

---

## Task 6: Worker 6 — Оборудование и опт

**Категории:**
- `apparaty-tornador` (~4 ключей)
- `oborudovanie`
- `opt-i-b2b` (~10)

**Review файлы:**
- `data/generated/review/06_khimchistka.md`
- `data/generated/review/07_avtokhimiya.md`
- `data/generated/review/09_prochee_part3.md`

**Примечание:** HOME ключи (~58) пропускаем — это общие ключи для главной страницы.

---

## Инструкция для воркера

```markdown
## Алгоритм работы

1. **Открыть review файл** — найти таблицу с ключами
2. **Фильтровать по decision** — выбрать только свои категории
3. **Для каждой категории:**
   a. Прочитать _clean.json
   b. Выписать существующие keywords и synonyms
   c. Из review выбрать НОВЫЕ (которых нет)
   d. Классифицировать: keywords vs synonyms vs meta_only
   e. Добавить через Edit tool
   f. Проверить JSON валидность: `python3 -c "import json; json.load(open('file.json'))"`

4. **Отчёт в конце:**
   ```
   ✅ polirovalnye-pasty: +4 kw, +8 syn
   ✅ polirovalnye-mashinki: +12 kw, +25 syn
   ```
```

---

## Финальная проверка (оркестратор)

После всех воркеров:
1. `find categories -name "*_clean.json" -exec python3 -c "import json; json.load(open('{}'))" \;`
2. Подсчитать добавленные ключи
3. Commit:
```bash
git add categories/*/data/*_clean.json categories/*/*/data/*_clean.json categories/*/*/*/data/*_clean.json
git commit -m "feat: import ~390 uncategorized keywords into 52 category _clean.json files

- Manual import via parallel workers (no scripts)
- Restored 4 categories from git: polirovalnye-mashinki, polirovalnye-krugi, mekhovye, akkumulyatornaya
- Skipped ~58 HOME keywords
- Master CSV unchanged

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```
