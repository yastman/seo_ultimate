# Meta Tags Audit via Subagents — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Проверить мета-теги всех 49 категорий Ultimate.net.ua через субагентов (вручную, без скриптов) и сгенерировать исправления для проблемных категорий.

**Architecture:** Параллельный запуск субагентов батчами по родительским категориям. Каждый субагент читает _meta.json и _clean.json, проверяет по чеклисту, возвращает отчёт + fix.

**Tech Stack:** Claude Code субагенты (general-purpose), JSON файлы

---

## Правила аудита (из generate-meta skill)

### IRON RULE
`primary_keyword` из `_clean.json` используется в Title/H1/Description **ДОСЛОВНО** (без изменения слов/порядка).

### Извлечение primary_keyword
```
List-схема: keywords[0].keyword
Dict-схема: keywords.primary[0].keyword
```

### Title формула (30-60 chars уникальная часть)
```
ЕСЛИ primary_keyword ≤ 20 chars:
  {primary_keyword} — купить в интернет-магазине Ultimate

ИНАЧЕ:
  {primary_keyword} — купить, цены | Ultimate
```

### H1 формула
```
= {primary_keyword} (без "купить", без добавлений)
```

### Description формула (100-160 chars)
```
Producer (есть товары Ultimate):
  {primary_keyword} от производителя Ultimate. {Типы} — {подробности}. Опт и розница.

Shop (НЕТ товаров Ultimate):
  {primary_keyword} в интернет-магазине Ultimate. {Типы} — {подробности}.
```

### Shop-категории (без товаров Ultimate)
```
glina-i-avtoskraby, gubki-i-varezhki, cherniteli-shin, raspyliteli-i-penniki,
vedra-i-emkosti, kisti-dlya-deteylinga, shchetka-dlya-moyki-avto, shchetki-i-kisti,
malyarniy-skotch, polirovka, polirovalnye-krugi, polirovalnye-mashinki,
oborudovanie, apparaty-tornador, mekhovye, akkumulyatornaya
```

---

## Чеклист для субагента

### Title
- [ ] Содержит primary_keyword ДОСЛОВНО
- [ ] 30-60 chars (уникальная часть до `|`)
- [ ] primary_keyword В НАЧАЛЕ (front-loading)
- [ ] "купить" ПОСЛЕ primary_keyword
- [ ] Без двоеточия `:`
- [ ] Бренд "Ultimate" в конце

### H1
- [ ] = primary_keyword ДОСЛОВНО
- [ ] БЕЗ "Купить/Купити"
- [ ] БЕЗ добавлений ("для авто" и т.п.)

### Description
- [ ] 100-160 chars
- [ ] Начинается с primary_keyword
- [ ] Producer: содержит "от производителя Ultimate" + "Опт и розница"
- [ ] Shop: содержит "в интернет-магазине Ultimate", БЕЗ "опт"
- [ ] НЕТ названий товаров/брендов/fluff

---

## Формат отчёта субагента

```markdown
## Категория: {slug}
**Статус:** PASS / WARNING / FAIL
**Тип:** Producer / Shop

### Title
- Значение: `{title}`
- Длина: {X} chars (уникальная часть)
- Проверки:
  - primary_keyword в начале: ✓/✗
  - "купить" после ВЧ: ✓/✗
  - Без двоеточия: ✓/✗
  - Длина 30-60: ✓/✗

### H1
- Значение: `{h1}`
- Проверки:
  - = primary_keyword: ✓/✗
  - Без "купить": ✓/✗

### Description
- Значение: `{description}`
- Длина: {X} chars
- Проверки:
  - primary_keyword в начале: ✓/✗
  - Корректный паттерн (Producer/Shop): ✓/✗
  - Длина 100-160: ✓/✗

### Проблемы
{список проблем или "Нет"}

### Fix (если нужен)
```json
{исправленный _meta.json}
```
```

---

## Task 1: Батч — aksessuary (10 категорий)

**Запуск:** 10 субагентов параллельно через Task tool

**Категории:**

| # | Slug | Тип | Путь к meta | Путь к clean |
|---|------|-----|-------------|--------------|
| 1 | aksessuary | Producer | categories/aksessuary/meta/aksessuary_meta.json | categories/aksessuary/data/aksessuary_clean.json |
| 2 | aksessuary-dlya-naneseniya-sredstv | Producer | categories/aksessuary/aksessuary-dlya-naneseniya-sredstv/meta/aksessuary-dlya-naneseniya-sredstv_meta.json | categories/aksessuary/aksessuary-dlya-naneseniya-sredstv/data/aksessuary-dlya-naneseniya-sredstv_clean.json |
| 3 | gubki-i-varezhki | **Shop** | categories/aksessuary/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json | categories/aksessuary/gubki-i-varezhki/data/gubki-i-varezhki_clean.json |
| 4 | malyarniy-skotch | **Shop** | categories/aksessuary/malyarniy-skotch/meta/malyarniy-skotch_meta.json | categories/aksessuary/malyarniy-skotch/data/malyarniy-skotch_clean.json |
| 5 | mikrofibra-i-tryapki | Producer | categories/aksessuary/mikrofibra-i-tryapki/meta/mikrofibra-i-tryapki_meta.json | categories/aksessuary/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json |
| 6 | nabory | Producer | categories/aksessuary/nabory/meta/nabory_meta.json | categories/aksessuary/nabory/data/nabory_clean.json |
| 7 | raspyliteli-i-penniki | **Shop** | categories/aksessuary/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json | categories/aksessuary/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json |
| 8 | kisti-dlya-deteylinga | **Shop** | categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/meta/kisti-dlya-deteylinga_meta.json | categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json |
| 9 | shchetka-dlya-moyki-avto | **Shop** | categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/meta/shchetka-dlya-moyki-avto_meta.json | categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/data/shchetka-dlya-moyki-avto_clean.json |
| 10 | vedra-i-emkosti | **Shop** | categories/aksessuary/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json | categories/aksessuary/vedra-i-emkosti/data/vedra-i-emkosti_clean.json |

---

## Task 2: Батч — moyka-i-eksterer/avtoshampuni (4 категории)

**Запуск:** 4 субагента параллельно

| # | Slug | Тип | Путь к meta |
|---|------|-----|-------------|
| 1 | moyka-i-eksterer | Producer | categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json |
| 2 | avtoshampuni | Producer | categories/moyka-i-eksterer/avtoshampuni/meta/avtoshampuni_meta.json |
| 3 | aktivnaya-pena | Producer | categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/meta/aktivnaya-pena_meta.json |
| 4 | shampuni-dlya-ruchnoy-moyki | Producer | categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/meta/shampuni-dlya-ruchnoy-moyki_meta.json |

---

## Task 3: Батч — moyka-i-eksterer/ochistiteli-kuzova (5 категорий)

**Запуск:** 5 субагентов параллельно

| # | Slug | Тип | Путь к meta |
|---|------|-----|-------------|
| 1 | antibitum | Producer | categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/meta/antibitum_meta.json |
| 2 | antimoshka | Producer | categories/moyka-i-eksterer/ochistiteli-kuzova/antimoshka/meta/antimoshka_meta.json |
| 3 | glina-i-avtoskraby | **Shop** | categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json |
| 4 | obezzhirivateli | Producer | categories/moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli/meta/obezzhirivateli_meta.json |
| 5 | ukhod-za-naruzhnym-plastikom | Producer | categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/meta/ukhod-za-naruzhnym-plastikom_meta.json |

---

## Task 4: Батч — moyka-i-eksterer/sredstva-dlya-diskov-i-shin (5 категорий)

**Запуск:** 5 субагентов параллельно

| # | Slug | Тип | Путь к meta |
|---|------|-----|-------------|
| 1 | ochistiteli-diskov | Producer | categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov/meta/ochistiteli-diskov_meta.json |
| 2 | ochistiteli-shin | Producer | categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin/meta/ochistiteli-shin_meta.json |
| 3 | cherniteli-shin | **Shop** | categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/meta/cherniteli-shin_meta.json |
| 4 | keramika-dlya-diskov | Producer | categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/meta/keramika-dlya-diskov_meta.json |
| 5 | ochistiteli-dvigatelya | Producer | categories/moyka-i-eksterer/ochistiteli-dvigatelya/meta/ochistiteli-dvigatelya_meta.json |

---

## Task 5: Батч — moyka-i-eksterer/sredstva-dlya-stekol (4 категории)

**Запуск:** 4 субагента параллельно

| # | Slug | Тип | Путь к meta |
|---|------|-----|-------------|
| 1 | antidozhd | Producer | categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/meta/antidozhd_meta.json |
| 2 | ochistiteli-stekol | Producer | categories/moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol/meta/ochistiteli-stekol_meta.json |
| 3 | omyvatel | Producer | categories/moyka-i-eksterer/sredstva-dlya-stekol/omyvatel/meta/omyvatel_meta.json |
| 4 | polirol-dlya-stekla | Producer | categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/meta/polirol-dlya-stekla_meta.json |

---

## Task 6: Батч — zashchitnye-pokrytiya (7 категорий)

**Запуск:** 7 субагентов параллельно

| # | Slug | Тип | Путь к meta |
|---|------|-----|-------------|
| 1 | zashchitnye-pokrytiya | Producer | categories/zashchitnye-pokrytiya/meta/zashchitnye-pokrytiya_meta.json |
| 2 | keramika-i-zhidkoe-steklo | Producer | categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json |
| 3 | kvik-deteylery | Producer | categories/zashchitnye-pokrytiya/kvik-deteylery/meta/kvik-deteylery_meta.json |
| 4 | silanty | Producer | categories/zashchitnye-pokrytiya/silanty/meta/silanty_meta.json |
| 5 | voski | Producer | categories/zashchitnye-pokrytiya/voski/meta/voski_meta.json |
| 6 | tverdyy-vosk | Producer | categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/meta/tverdyy-vosk_meta.json |
| 7 | zhidkiy-vosk | Producer | categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/meta/zhidkiy-vosk_meta.json |

---

## Task 7: Батч — ukhod-za-intererom (7 категорий)

**Запуск:** 7 субагентов параллельно

| # | Slug | Тип | Путь к meta |
|---|------|-----|-------------|
| 1 | ukhod-za-intererom | Producer | categories/ukhod-za-intererom/meta/ukhod-za-intererom_meta.json |
| 2 | sredstva-dlya-khimchistki-salona | Producer | categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/meta/sredstva-dlya-khimchistki-salona_meta.json |
| 3 | poliroli-dlya-plastika | Producer | categories/ukhod-za-intererom/poliroli-dlya-plastika/meta/poliroli-dlya-plastika_meta.json |
| 4 | neytralizatory-zapakha | Producer | categories/ukhod-za-intererom/neytralizatory-zapakha/meta/neytralizatory-zapakha_meta.json |
| 5 | pyatnovyvoditeli | Producer | categories/ukhod-za-intererom/pyatnovyvoditeli/meta/pyatnovyvoditeli_meta.json |
| 6 | ochistiteli-kozhi | Producer | categories/ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi/meta/ochistiteli-kozhi_meta.json |
| 7 | ukhod-za-kozhey | Producer | categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/meta/ukhod-za-kozhey_meta.json |

---

## Task 8: Батч — polirovka + oborudovanie + opt (7 категорий)

**Запуск:** 7 субагентов параллельно

| # | Slug | Тип | Путь к meta |
|---|------|-----|-------------|
| 1 | polirovka | **Shop** | categories/polirovka/meta/polirovka_meta.json |
| 2 | polirovalnye-pasty | Producer | categories/polirovka/polirovalnye-pasty/meta/polirovalnye-pasty_meta.json |
| 3 | mekhovye | **Shop** | categories/polirovka/polirovalnye-krugi/mekhovye/meta/mekhovye_meta.json |
| 4 | akkumulyatornaya | **Shop** | categories/polirovka/polirovalnye-mashinki/akkumulyatornaya/meta/akkumulyatornaya_meta.json |
| 5 | oborudovanie | **Shop** | categories/oborudovanie/meta/oborudovanie_meta.json |
| 6 | apparaty-tornador | **Shop** | categories/oborudovanie/apparaty-tornador/meta/apparaty-tornador_meta.json |
| 7 | opt-i-b2b | Producer | categories/opt-i-b2b/meta/opt-i-b2b_meta.json |

---

## Task 9: Агрегация результатов

**Шаг 1:** Собрать все отчёты субагентов из батчей 1-8

**Шаг 2:** Создать сводную таблицу

```markdown
| # | Категория | Статус | Проблемы | Fix нужен |
|---|-----------|--------|----------|-----------|
| 1 | aktivnaya-pena | PASS | - | Нет |
| 2 | antibitum | WARNING | Title < 30 chars | Да |
...
```

**Шаг 3:** Сгруппировать по статусу

- **FAIL:** критичные проблемы (primary_keyword изменён, нет паттерна Producer/Shop, "Купить" первым)
- **WARNING:** некритичные (длина Title/Description вне нормы)
- **PASS:** всё в порядке

**Шаг 4:** Сохранить итоговый отчёт в `docs/reports/2026-01-20-meta-audit-report.md`

---

## Промпт для субагента (полный)

```
Ты — SEO-аудитор мета-тегов для Ultimate.net.ua.

## Задача
Проверь мета-теги категории `{slug}`.

## Файлы для чтения
1. Meta: `{meta_path}`
2. Keywords: `{clean_path}`

## Тип категории
{Producer / Shop}

## Правила проверки

### 1. Извлеки primary_keyword
Из _clean.json:
- List-схема: `keywords[0].keyword`
- Dict-схема: `keywords.primary[0].keyword`

### 2. Проверь Title
- [ ] Содержит primary_keyword ДОСЛОВНО (без изменений слов/порядка)
- [ ] 30-60 chars (уникальная часть до `|`)
- [ ] primary_keyword В НАЧАЛЕ
- [ ] "купить" ПОСЛЕ primary_keyword
- [ ] Без двоеточия `:`

Формула:
- ≤ 20 chars: `{primary_keyword} — купить в интернет-магазине Ultimate`
- > 20 chars: `{primary_keyword} — купить, цены | Ultimate`

### 3. Проверь H1
- [ ] = primary_keyword ДОСЛОВНО
- [ ] БЕЗ "Купить/Купити"
- [ ] БЕЗ добавлений

### 4. Проверь Description
- [ ] 100-160 chars
- [ ] Начинается с primary_keyword

Producer паттерн:
- [ ] Содержит "от производителя Ultimate"
- [ ] Содержит "Опт и розница"

Shop паттерн:
- [ ] Содержит "в интернет-магазине Ultimate"
- [ ] НЕТ "Опт и розница"

### 5. Вывод
Верни отчёт строго в формате:

## Категория: {slug}
**Статус:** PASS / WARNING / FAIL
**Тип:** Producer / Shop

### Title
- Значение: `{title}`
- Длина: {X} chars
- Проверки: primary_keyword в начале ✓/✗ | "купить" после ВЧ ✓/✗ | Без двоеточия ✓/✗ | Длина 30-60 ✓/✗

### H1
- Значение: `{h1}`
- Проверки: = primary_keyword ✓/✗ | Без "купить" ✓/✗

### Description
- Значение: `{description}`
- Длина: {X} chars
- Проверки: primary_keyword в начале ✓/✗ | Корректный паттерн ✓/✗ | Длина 100-160 ✓/✗

### Проблемы
{список проблем или "Нет"}

### Fix
{исправленный JSON или "Не требуется"}
```

---

## Итого

| Батч | Группа | Категорий | Субагентов |
|------|--------|-----------|------------|
| 1 | aksessuary | 10 | 10 |
| 2 | avtoshampuni | 4 | 4 |
| 3 | ochistiteli-kuzova | 5 | 5 |
| 4 | sredstva-dlya-diskov-i-shin | 5 | 5 |
| 5 | sredstva-dlya-stekol | 4 | 4 |
| 6 | zashchitnye-pokrytiya | 7 | 7 |
| 7 | ukhod-za-intererom | 7 | 7 |
| 8 | polirovka + oborudovanie + opt | 7 | 7 |
| **9** | **Агрегация** | - | - |
| **Всего** | **49 категорий** | **49** | **8 батчей** |

---

**Version:** 1.0 | **Created:** 2026-01-20
