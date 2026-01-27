# UK Keywords Apply All Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Автоматично застосувати всі 356 UK ключів з чек-листа до `_clean.json` файлів у 45 категоріях без ручної перевірки.

**Architecture:** Парсимо `tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md`, витягуємо ключі по категоріях, оновлюємо `uk/categories/{slug}/data/{slug}_clean.json`. Один коміт на категорію.

**Tech Stack:** Markdown parsing, JSON editing, batch processing

---

## Task 1: aktivnaya-pena

**Files:**
- Read: `tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md` (секція aktivnaya-pena)
- Modify: `uk/categories/aktivnaya-pena/data/aktivnaya-pena_clean.json`

**Step 1: Прочитати поточний _clean.json**

**Step 2: Оновити keywords масив**

Замінити/додати keywords з чек-листа:
```json
{
  "keywords": [
    {"keyword": "активна піна для авто", "volume": 1600},
    {"keyword": "піна для миття авто", "volume": 1300},
    {"keyword": "піна для миття автомобіля", "volume": 1300},
    {"keyword": "активна піна", "volume": 1000},
    {"keyword": "хімія для миття авто", "volume": 1000},
    {"keyword": "активна піна для миття авто", "volume": 390},
    {"keyword": "активна піна для безконтактної мийки", "volume": 320},
    {"keyword": "автохімія для автомийки", "volume": 260},
    {"keyword": "хімія для миття автомобіля", "volume": 260},
    {"keyword": "активна піна для автомийки", "volume": 210},
    {"keyword": "хімія для безконтактної мийки", "volume": 140},
    {"keyword": "активна піна для мийки", "volume": 110},
    {"keyword": "піна для безконтактної мийки", "volume": 110},
    {"keyword": "хімія для мийки самообслуговування", "volume": 110},
    {"keyword": "засоби для мийки самообслуговування", "volume": 90},
    {"keyword": "активна піна купити", "volume": 70},
    {"keyword": "піна активна", "volume": 70},
    {"keyword": "активна піна ціна", "volume": 50},
    {"keyword": "хімія для мийки", "volume": 50},
    {"keyword": "активна піна для авто відгуки", "volume": 40},
    {"keyword": "хімія для автомийки", "volume": 40},
    {"keyword": "активна піна для миття", "volume": 30},
    {"keyword": "піна", "volume": 20}
  ]
}
```

**Step 3: Зберегти JSON**

**Step 4: Оновити чек-лист — поставити [x]**

**Step 5: Commit**

```bash
git add uk/categories/aktivnaya-pena/data/aktivnaya-pena_clean.json tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md
git commit -m "keywords(uk): apply 23 keywords to aktivnaya-pena"
```

---

## Task 2: antidozhd

**Files:**
- Modify: `uk/categories/antidozhd/data/antidozhd_clean.json`

**Step 1-5:** Аналогічно Task 1

Keywords:
- `антидощ` (1900)
- `антидощ для авто` (480)
- `антидощ для скла авто` (390)
- `антидощ для автомобіля` (320)
- `антидощ на лобове скло` (170)
- `засіб антидощ` (140)
- `антидощ купити` (50)
- `антидощ для скла` (70)
- `антидощ відгуки` (30)

**Commit:** `keywords(uk): apply 10 keywords to antidozhd`

---

## Task 3: antibitum

**Files:**
- Modify: `uk/categories/antibitum/data/antibitum_clean.json`

Keywords:
- `антибітум` (720)
- `очищувач бітуму` (390)
- `очисник бітуму` (170)
- `засоби для видалення бітуму` (70)
- `засіб від бітуму` (70)
- `засіб для видалення бітуму` (140)
- `засіб для очищення кузова від бітуму` (70)
- `очищувач кузова від бітуму` (50)

**Commit:** `keywords(uk): apply 8 keywords to antibitum`

---

## Task 4-45: Решта категорій

**Патерн однаковий для всіх:**

1. Прочитати `_clean.json`
2. Замінити `keywords` масив ключами з чек-листа
3. Зберегти JSON
4. Оновити чек-лист `[x]`
5. Commit: `keywords(uk): apply N keywords to {slug}`

**Категорії:**
- Task 4: antimoshka (3 ключі)
- Task 5: apparaty-tornador (1 ключ)
- Task 6: avtoshampuni (15 ключів)
- Task 7: cherniteli-shin (5 ключів)
- Task 8: glina-i-avtoskraby (7 ключів)
- Task 9: gubki-i-varezhki (8 ключів)
- Task 10: keramika-i-zhidkoe-steklo (7 ключів)
- Task 11: kisti-dlya-deteylinga (3 ключі)
- Task 12: malyarniy-skotch (3 ключі)
- Task 13: mikrofibra-i-tryapki (14 ключів)
- Task 14: neytralizatory-zapakha (6 ключів)
- Task 15: obezzhirivateli (13 ключів)
- Task 16: ochistiteli-diskov (15 ключів)
- Task 17: ochistiteli-dvigatelya (13 ключів)
- Task 18: ochistiteli-kozhi (10 ключів)
- Task 19: ochistiteli-kuzova (6 ключів)
- Task 20: ochistiteli-shin (6 ключів)
- Task 21: ochistiteli-stekol (7 ключів)
- Task 22: omyvatel (3 ключі)
- Task 23: polirol-dlya-stekla (2 ключі)
- Task 24: poliroli-dlya-plastika (14 ключів)
- Task 25: polirovalnye-mashinki (3 ключі)
- Task 26: polirovalnye-pasty (9 ключів)
- Task 27: polirovka (7 ключів)
- Task 28: pyatnovyvoditeli (2 ключі)
- Task 29: raspyliteli-i-penniki (4 ключі)
- Task 30: shampuni-dlya-ruchnoy-moyki (4 ключі)
- Task 31: shchetka-dlya-moyki-avto (11 ключів)
- Task 32: sredstva-dlya-khimchistki-salona (24 ключі)
- Task 33: sredstva-dlya-kozhi (7 ключів)
- Task 34: tverdyy-vosk (2 ключі)
- Task 35: ukhod-za-intererom (3 ключі)
- Task 36: ukhod-za-naruzhnym-plastikom (3 ключі)
- Task 37: vedra-i-emkosti (2 ключі)
- Task 38: voski (12 ключів)
- Task 39: zashchitnye-pokrytiya (1 ключ)
- Task 40: zhidkiy-vosk (1 ключ)
- Task 41: nabory (11 ключів)
- Task 42: aksessuary (5 ключів)

---

## Task 43: uncategorized — ручний розподіл

**20 ключів без категорії потребують ручного рішення:**

```
- автокосметика (590)
- автохімія (20)
- віск (20)
- губка (20)
- засіб для чищення шкіри (20)
- засіб для чорніння гуми (20)
- набір (20)
- очищувач (20)
- полірування (20)
- шампунь (20)
- щітка (20)
- автокосметика для авто (140)
- автокосметика для салону (40)
- автохімія інтернет магазин (170)
- автохімія київ (40)
- преміум автохімія (90)
- професійна автохімія (90)
- хімія для авто (90)
- преміум мийка (50)
- силікон для авто (70)
```

**Рішення:** Додати до найближчої за смислом категорії або залишити.

---

## Parallel Execution Strategy

**Оскільки 45 категорій незалежні, можна розбити на воркерів:**

```bash
PROJECT="/mnt/c/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт"

# Worker 1: Tasks 1-10 (категорії a-g)
spawn-claude "W1: Apply UK keywords Tasks 1-10. План: docs/plans/2026-01-27-uk-keywords-apply-all-plan.md. Категорії: aktivnaya-pena, antidozhd, antibitum, antimoshka, apparaty-tornador, avtoshampuni, cherniteli-shin, glina-i-avtoskraby, gubki-i-varezhki, keramika-i-zhidkoe-steklo" $PROJECT

# Worker 2: Tasks 11-20 (категорії k-o)
spawn-claude "W2: Apply UK keywords Tasks 11-20. План: docs/plans/2026-01-27-uk-keywords-apply-all-plan.md. Категорії: kisti-dlya-deteylinga, malyarniy-skotch, mikrofibra-i-tryapki, neytralizatory-zapakha, obezzhirivateli, ochistiteli-diskov, ochistiteli-dvigatelya, ochistiteli-kozhi, ochistiteli-kuzova, ochistiteli-shin" $PROJECT

# Worker 3: Tasks 21-30 (категорії o-s)
spawn-claude "W3: Apply UK keywords Tasks 21-30. План: docs/plans/2026-01-27-uk-keywords-apply-all-plan.md. Категорії: ochistiteli-stekol, omyvatel, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-mashinki, polirovalnye-pasty, polirovka, pyatnovyvoditeli, raspyliteli-i-penniki, shampuni-dlya-ruchnoy-moyki" $PROJECT

# Worker 4: Tasks 31-42 (категорії s-z + nabory, aksessuary)
spawn-claude "W4: Apply UK keywords Tasks 31-42. План: docs/plans/2026-01-27-uk-keywords-apply-all-plan.md. Категорії: shchetka-dlya-moyki-avto, sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi, tverdyy-vosk, ukhod-za-intererom, ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, voski, zashchitnye-pokrytiya, zhidkiy-vosk, nabory, aksessuary" $PROJECT
```

---

## Verification

Після всіх Tasks:

```bash
# Перевірити що всі категорії оновлені
find uk/categories -name "*_clean.json" -exec grep -l "keywords" {} \; | wc -l

# Перевірити git log
git log --oneline -50 | grep "keywords(uk)"

# Перевірити чек-лист — всі [x]
grep -c "\[x\]" tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md
```
