# Content Audit: All Categories Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Провести полный аудит контента всех 50 категорий по стандартам content-generator v3.1: валидация скриптами, ручная проверка по чеклисту, автофикс проблем.

**Architecture:** Batch-подход по группам категорий. Для каждой категории: активация скилла → автоматическая валидация → ручная проверка по v3.1 чеклисту → автофикс → ре-валидация.

**Tech Stack:** Python scripts (validate_content.py, validate_meta.py), content-generator v3.1 skill, _meta.json (keywords_in_content), _clean.json (entities, name), RESEARCH_DATA.md (FAQ источник).

---

## Prerequisites

**Перед началом работы:**

1. **Активировать скилл content-generator:**

   ```
   /content-generator
   ```

   Изучить стандарты v3.1:
   - micro_intents УБРАНЫ — FAQ из RESEARCH_DATA.md или шаблонов
   - H1 = `name` из `_clean.json` (без "Купить")
   - Минимум 1 H2 содержит secondary keyword
   - Нет how-to секций (5+ пошаговых инструкций)
   - RU-first: русский термин первым, англ. в скобках

2. **Проверить скрипты валидации:**

   ```bash
   python3 scripts/validate_meta.py --all
   python3 scripts/validate_content.py --help
   ```

3. **Понимать источники данных:**

   | Данные | Источник | Поле |
   |--------|----------|------|
   | H1 | `_clean.json` | `name` |
   | Primary keywords | `_meta.json` | `keywords_in_content.primary` |
   | Secondary keywords | `_meta.json` | `keywords_in_content.secondary` |
   | Supporting keywords | `_meta.json` | `keywords_in_content.supporting` |
   | Entities (E-E-A-T) | `_clean.json` | `entities[]` |
   | FAQ вопросы | `research/RESEARCH_DATA.md` | Раздел FAQ или шаблоны |

---

## Checklist v3.1 для каждой категории

### 1. Meta Validation (validate_meta.py)

- [ ] Title: 30-60 chars, primary keyword в начале
- [ ] Title: без двоеточия, с "купить/купити" после ВЧ
- [ ] Description: 100-160 chars, содержит "виробника/производителя Ultimate"
- [ ] Description: содержит "опт і роздріб" или "опт и розница"
- [ ] H1: чистый (без "купить"), = `name` из `_clean.json`

### 2. Content Validation (validate_content.py --mode seo)

- [ ] Structure: H1 есть, intro 30-60 слов, минимум 1 H2
- [ ] Primary keyword: в H1 И в intro
- [ ] Blacklist: нет strict phrases

### 3. Ручная проверка v3.1

#### Структура
- [ ] H1 без "Купить" (= `name` из `_clean.json`)
- [ ] Intro 30-60 слов (не общие фразы)
- [ ] Таблица сравнения типов есть
- [ ] FAQ 3-5 вопросов про ВЫБОР (не how-to)
- [ ] **НЕТ how-to секций** (пошаговых инструкций 5+ шагов)

#### SEO/LSI (из _meta.json)
- [ ] Primary keywords из `keywords_in_content.primary` — в H1 и intro
- [ ] **Минимум 1 H2 содержит secondary keyword** из `keywords_in_content.secondary`
- [ ] Secondary keywords — 1x каждый, естественно в тексте
- [ ] Нет коммерческих ключей в body (купить, цена, заказать)

#### E-E-A-T (из _clean.json)
- [ ] 3-4 профтермина из `entities[]` присутствуют в тексте
- [ ] Объяснено преимущество над бытовым продуктом

#### RU-first локализация
- [ ] Англицизмы: русский первым, англ. в скобках
  - ✅ "разбрызгивание (sling)", "время выдержки (dwell time)"
  - ❌ "sling", "dwell time", "wet look"

#### Цифры и факты
- [ ] Нет точных диапазонов без SSOT (5-10 минут → "дайте впитаться")
- [ ] Нет спорных утверждений (смягчить или убрать)

### 4. RESEARCH_DATA.md проверка

- [ ] Найти файл: `research/RESEARCH_DATA.md` или `research_data_*.md`
- [ ] FAQ вопросы соответствуют теме исследования
- [ ] Спорные факты из research НЕ копировать напрямую

---

## Алгоритм на каждую категорию

```
1. Определить тип страницы:
   - Read _clean.json → parent_id
   - null = Hub Page (L1) → короткий текст 2000-2500 знаков
   - не null = Product Page (L2/L3) → buyer guide

2. Run meta validation:
   python3 scripts/validate_meta.py categories/{path}/meta/{slug}_meta.json

3. Run content validation:
   python3 scripts/validate_content.py categories/{path}/content/{slug}_ru.md "{primary}" --mode seo

4. Read data files:
   - _meta.json → keywords_in_content (primary, secondary, supporting)
   - _clean.json → name (для H1), entities (для E-E-A-T)
   - research/RESEARCH_DATA.md → FAQ источник

5. Ручная проверка по v3.1 чеклисту выше

6. Автофикс найденных проблем

7. Ре-валидация
```

---

## Частые проблемы и автофиксы

### H1 проблемы

| Проблема | Пример | Фикс |
|----------|--------|------|
| H1 ≠ name из JSON | "Автошампуни" vs name="Автошампунь" | Заменить на `name` |
| H1 содержит "Купить" | "Купить автошампунь" | Убрать "Купить" |

### H2 без secondary keyword

| Проблема | Пример | Фикс |
|----------|--------|------|
| H2 не содержит ключ | "## Как это работает" | Добавить secondary: "## Как работает шампунь для мойки авто" |
| Ни один H2 не содержит | Все H2 общие | Переписать минимум 1 H2 |

### Англицизмы (RU-first)

| Было | Стало |
|------|-------|
| dwell time | время выдержки (dwell time) |
| sling | разбрызгивание (sling) |
| wet look | мокрый блеск (wet look) |
| per wash | на одну мойку |
| clearcoat | лак / защитный слой |

### Точные цифры → смягчить

| Было | Стало |
|------|-------|
| 5-10 минут | дайте впитаться |
| 20-30°C | при комнатной температуре |
| 7-14 дней | обычно требует обновления после нескольких моек |
| 80-90% грязи | большую часть загрязнений |

### How-to → упоминание

| Было (how-to = инфо-интент) | Стало (экспертное упоминание) |
|-----------------------------|-------------------------------|
| 1. Подготовьте ведро<br>2. Налейте воду<br>3. Добавьте шампунь<br>4. Вспеньте<br>5. Мойте | **Метод двух вёдер** — профессиональный подход: одно ведро с раствором, второе для ополаскивания. |

### FAQ — источник

| Старый подход (v3.0) | Новый подход (v3.1) |
|----------------------|---------------------|
| micro_intents из _clean.json | RESEARCH_DATA.md или шаблоны по типу категории |

---

## Batch 1: Мойка и экстерьер (18 categories)

### Task 1: moyka-i-eksterer (Hub Page)

**Files:**
- Content: `categories/moyka-i-eksterer/content/moyka-i-eksterer_ru.md`
- Data: `categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json`
- Meta: `categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json`

**Тип:** Hub Page (parent_id = null) → 2000-2500 знаков, H2 по процессам

**Steps:**
1. Run meta validation
2. Run content validation
3. Check: H1 = name, H2 содержит secondary, entities присутствуют
4. Fix issues
5. Re-validate

---

### Task 2: avtoshampuni (Hub Page)

**Files:**
- Content: `categories/moyka-i-eksterer/avtoshampuni/content/avtoshampuni_ru.md`
- Data: `categories/moyka-i-eksterer/avtoshampuni/data/avtoshampuni_clean.json`
- Meta: `categories/moyka-i-eksterer/avtoshampuni/meta/avtoshampuni_meta.json`

**Steps:** Same pattern

---

### Task 3: aktivnaya-pena (Product Page)

**Files:**
- Content: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md`
- Data: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json`
- Meta: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/meta/aktivnaya-pena_meta.json`
- Research: `categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/research/RESEARCH_DATA.md`

**Steps:** Same pattern + проверка RESEARCH_DATA.md для FAQ

---

### Task 4: shampuni-dlya-ruchnoy-moyki

**Files:**
- Content: `categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/content/shampuni-dlya-ruchnoy-moyki_ru.md`
- Data: `categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/data/shampuni-dlya-ruchnoy-moyki_clean.json`
- Meta: `categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/meta/shampuni-dlya-ruchnoy-moyki_meta.json`

**Steps:** Same pattern

---

### Task 5: ochistiteli-dvigatelya

**Files:**
- Content: `categories/moyka-i-eksterer/ochistiteli-dvigatelya/content/ochistiteli-dvigatelya_ru.md`
- Data: `categories/moyka-i-eksterer/ochistiteli-dvigatelya/data/ochistiteli-dvigatelya_clean.json`
- Meta: `categories/moyka-i-eksterer/ochistiteli-dvigatelya/meta/ochistiteli-dvigatelya_meta.json`

**Steps:** Same pattern

---

### Task 6: glina-i-avtoskraby

**Files:**
- Content: `categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/content/glina-i-avtoskraby_ru.md`
- Data: `categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json`
- Meta: `categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json`

**Steps:** Same pattern

---

### Task 7: antibitum

**Files:**
- Content: `categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/content/antibitum_ru.md`
- Data: `categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/data/antibitum_clean.json`
- Meta: `categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/meta/antibitum_meta.json`

**Steps:** Same pattern

---

### Task 8: antimoshka

**Files:**
- Content: `categories/moyka-i-eksterer/ochistiteli-kuzova/antimoshka/content/antimoshka_ru.md`
- Data: `categories/moyka-i-eksterer/ochistiteli-kuzova/antimoshka/data/antimoshka_clean.json`
- Meta: `categories/moyka-i-eksterer/ochistiteli-kuzova/antimoshka/meta/antimoshka_meta.json`

**Steps:** Same pattern

---

### Task 9: obezzhirivateli

**Files:**
- Content: `categories/moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli/content/obezzhirivateli_ru.md`
- Data: `categories/moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli/data/obezzhirivateli_clean.json`
- Meta: `categories/moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli/meta/obezzhirivateli_meta.json`

**Steps:** Same pattern

---

### Task 10: ukhod-za-naruzhnym-plastikom

**Files:**
- Content: `categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/content/ukhod-za-naruzhnym-plastikom_ru.md`
- Data: `categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/data/ukhod-za-naruzhnym-plastikom_clean.json`
- Meta: `categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/meta/ukhod-za-naruzhnym-plastikom_meta.json`

**Steps:** Same pattern

---

### Task 11: cherniteli-shin

**Files:**
- Content: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/content/cherniteli-shin_ru.md`
- Data: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/data/cherniteli-shin_clean.json`
- Meta: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/meta/cherniteli-shin_meta.json`

**Steps:** Same pattern

---

### Task 12: ochistiteli-diskov

**Files:**
- Content: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov/content/ochistiteli-diskov_ru.md`
- Data: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov/data/ochistiteli-diskov_clean.json`
- Meta: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov/meta/ochistiteli-diskov_meta.json`

**Steps:** Same pattern

---

### Task 13: ochistiteli-shin

**Files:**
- Content: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin/content/ochistiteli-shin_ru.md`
- Data: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin/data/ochistiteli-shin_clean.json`
- Meta: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin/meta/ochistiteli-shin_meta.json`

**Steps:** Same pattern

---

### Task 14: keramika-dlya-diskov

**Files:**
- Content: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/content/keramika-dlya-diskov_ru.md`
- Data: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/data/keramika-dlya-diskov_clean.json`
- Meta: `categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/meta/keramika-dlya-diskov_meta.json`

**Steps:** Same pattern

---

### Task 15: ochistiteli-stekol

**Files:**
- Content: `categories/moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol/content/ochistiteli-stekol_ru.md`
- Data: `categories/moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol/data/ochistiteli-stekol_clean.json`
- Meta: `categories/moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol/meta/ochistiteli-stekol_meta.json`

**Steps:** Same pattern

---

### Task 16: antidozhd

**Files:**
- Content: `categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/content/antidozhd_ru.md`
- Data: `categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/data/antidozhd_clean.json`
- Meta: `categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/meta/antidozhd_meta.json`

**Steps:** Same pattern

---

### Task 17: omyvatel

**Files:**
- Content: `categories/moyka-i-eksterer/sredstva-dlya-stekol/omyvatel/content/omyvatel_ru.md`
- Data: `categories/moyka-i-eksterer/sredstva-dlya-stekol/omyvatel/data/omyvatel_clean.json`
- Meta: `categories/moyka-i-eksterer/sredstva-dlya-stekol/omyvatel/meta/omyvatel_meta.json`

**Steps:** Same pattern

---

### Task 18: polirol-dlya-stekla

**Files:**
- Content: `categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/content/polirol-dlya-stekla_ru.md`
- Data: `categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/data/polirol-dlya-stekla_clean.json`
- Meta: `categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/meta/polirol-dlya-stekla_meta.json`

**Steps:** Same pattern

---

## Batch 2: Аксессуары (10 categories)

### Task 19: aksessuary (Hub Page)

**Files:**
- Content: `categories/aksessuary/content/aksessuary_ru.md`
- Data: `categories/aksessuary/data/aksessuary_clean.json`
- Meta: `categories/aksessuary/meta/aksessuary_meta.json`

**Steps:** Same pattern as Batch 1

---

### Task 20: mikrofibra-i-tryapki

**Files:**
- Content: `categories/aksessuary/mikrofibra-i-tryapki/content/mikrofibra-i-tryapki_ru.md`
- Data: `categories/aksessuary/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json`
- Meta: `categories/aksessuary/mikrofibra-i-tryapki/meta/mikrofibra-i-tryapki_meta.json`

**Steps:** Same pattern

---

### Task 21: gubki-i-varezhki

**Files:**
- Content: `categories/aksessuary/gubki-i-varezhki/content/gubki-i-varezhki_ru.md`
- Data: `categories/aksessuary/gubki-i-varezhki/data/gubki-i-varezhki_clean.json`
- Meta: `categories/aksessuary/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json`

**Steps:** Same pattern

---

### Task 22: raspyliteli-i-penniki

**Files:**
- Content: `categories/aksessuary/raspyliteli-i-penniki/content/raspyliteli-i-penniki_ru.md`
- Data: `categories/aksessuary/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json`
- Meta: `categories/aksessuary/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json`

**Steps:** Same pattern

---

### Task 23: aksessuary-dlya-naneseniya-sredstv

**Files:**
- Content: `categories/aksessuary/aksessuary-dlya-naneseniya-sredstv/content/aksessuary-dlya-naneseniya-sredstv_ru.md`
- Data: `categories/aksessuary/aksessuary-dlya-naneseniya-sredstv/data/aksessuary-dlya-naneseniya-sredstv_clean.json`
- Meta: `categories/aksessuary/aksessuary-dlya-naneseniya-sredstv/meta/aksessuary-dlya-naneseniya-sredstv_meta.json`

**Steps:** Same pattern

---

### Task 24: nabory

**Files:**
- Content: `categories/aksessuary/nabory/content/nabory_ru.md`
- Data: `categories/aksessuary/nabory/data/nabory_clean.json`
- Meta: `categories/aksessuary/nabory/meta/nabory_meta.json`

**Steps:** Same pattern

---

### Task 25: vedra-i-emkosti

**Files:**
- Content: `categories/aksessuary/vedra-i-emkosti/content/vedra-i-emkosti_ru.md`
- Data: `categories/aksessuary/vedra-i-emkosti/data/vedra-i-emkosti_clean.json`
- Meta: `categories/aksessuary/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json`

**Steps:** Same pattern

---

### Task 26: shchetka-dlya-moyki-avto

**Files:**
- Content: `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/content/shchetka-dlya-moyki-avto_ru.md`
- Data: `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/data/shchetka-dlya-moyki-avto_clean.json`
- Meta: `categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/meta/shchetka-dlya-moyki-avto_meta.json`

**Steps:** Same pattern

---

### Task 27: kisti-dlya-deteylinga

**Files:**
- Content: `categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/content/kisti-dlya-deteylinga_ru.md`
- Data: `categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json`
- Meta: `categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/meta/kisti-dlya-deteylinga_meta.json`

**Steps:** Same pattern

---

### Task 28: malyarniy-skotch

**Files:**
- Content: `categories/aksessuary/malyarniy-skotch/content/malyarniy-skotch_ru.md`
- Data: `categories/aksessuary/malyarniy-skotch/data/malyarniy-skotch_clean.json`
- Meta: `categories/aksessuary/malyarniy-skotch/meta/malyarniy-skotch_meta.json`

**Steps:** Same pattern

---

## Batch 3: Уход за интерьером (8 categories)

### Task 29: ukhod-za-intererom (Hub Page)

**Files:**
- Content: `categories/ukhod-za-intererom/content/ukhod-za-intererom_ru.md`
- Data: `categories/ukhod-za-intererom/data/ukhod-za-intererom_clean.json`
- Meta: `categories/ukhod-za-intererom/meta/ukhod-za-intererom_meta.json`

**Steps:** Same pattern

---

### Task 30: sredstva-dlya-khimchistki-salona

**Files:**
- Content: `categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/content/sredstva-dlya-khimchistki-salona_ru.md`
- Data: `categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/data/sredstva-dlya-khimchistki-salona_clean.json`
- Meta: `categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/meta/sredstva-dlya-khimchistki-salona_meta.json`

**Steps:** Same pattern

---

### Task 31: sredstva-dlya-kozhi (Hub Page)

**Files:**
- Content: `categories/ukhod-za-intererom/sredstva-dlya-kozhi/content/sredstva-dlya-kozhi_ru.md`
- Data: `categories/ukhod-za-intererom/sredstva-dlya-kozhi/data/sredstva-dlya-kozhi_clean.json`
- Meta: `categories/ukhod-za-intererom/sredstva-dlya-kozhi/meta/sredstva-dlya-kozhi_meta.json`

**Steps:** Same pattern

---

### Task 32: ochistiteli-kozhi

**Files:**
- Content: `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi/content/ochistiteli-kozhi_ru.md`
- Data: `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi/data/ochistiteli-kozhi_clean.json`
- Meta: `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi/meta/ochistiteli-kozhi_meta.json`

**Steps:** Same pattern

---

### Task 33: ukhod-za-kozhey

**Files:**
- Content: `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/content/ukhod-za-kozhey_ru.md`
- Data: `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/data/ukhod-za-kozhey_clean.json`
- Meta: `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/meta/ukhod-za-kozhey_meta.json`

**Steps:** Same pattern

---

### Task 34: poliroli-dlya-plastika

**Files:**
- Content: `categories/ukhod-za-intererom/poliroli-dlya-plastika/content/poliroli-dlya-plastika_ru.md`
- Data: `categories/ukhod-za-intererom/poliroli-dlya-plastika/data/poliroli-dlya-plastika_clean.json`
- Meta: `categories/ukhod-za-intererom/poliroli-dlya-plastika/meta/poliroli-dlya-plastika_meta.json`

**Steps:** Same pattern

---

### Task 35: pyatnovyvoditeli

**Files:**
- Content: `categories/ukhod-za-intererom/pyatnovyvoditeli/content/pyatnovyvoditeli_ru.md`
- Data: `categories/ukhod-za-intererom/pyatnovyvoditeli/data/pyatnovyvoditeli_clean.json`
- Meta: `categories/ukhod-za-intererom/pyatnovyvoditeli/meta/pyatnovyvoditeli_meta.json`

**Steps:** Same pattern

---

### Task 36: neytralizatory-zapakha

**Files:**
- Content: `categories/ukhod-za-intererom/neytralizatory-zapakha/content/neytralizatory-zapakha_ru.md`
- Data: `categories/ukhod-za-intererom/neytralizatory-zapakha/data/neytralizatory-zapakha_clean.json`
- Meta: `categories/ukhod-za-intererom/neytralizatory-zapakha/meta/neytralizatory-zapakha_meta.json`

**Steps:** Same pattern

---

## Batch 4: Защитные покрытия (7 categories)

### Task 37: zashchitnye-pokrytiya (Hub Page)

**Files:**
- Content: `categories/zashchitnye-pokrytiya/content/zashchitnye-pokrytiya_ru.md`
- Data: `categories/zashchitnye-pokrytiya/data/zashchitnye-pokrytiya_clean.json`
- Meta: `categories/zashchitnye-pokrytiya/meta/zashchitnye-pokrytiya_meta.json`

**Steps:** Same pattern

---

### Task 38: keramika-i-zhidkoe-steklo

**Files:**
- Content: `categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/content/keramika-i-zhidkoe-steklo_ru.md`
- Data: `categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json`
- Meta: `categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json`

**Steps:** Same pattern

---

### Task 39: voski (Hub Page)

**Files:**
- Content: `categories/zashchitnye-pokrytiya/voski/content/voski_ru.md`
- Data: `categories/zashchitnye-pokrytiya/voski/data/voski_clean.json`
- Meta: `categories/zashchitnye-pokrytiya/voski/meta/voski_meta.json`

**Steps:** Same pattern

---

### Task 40: tverdyy-vosk

**Files:**
- Content: `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/content/tverdyy-vosk_ru.md`
- Data: `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/data/tverdyy-vosk_clean.json`
- Meta: `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/meta/tverdyy-vosk_meta.json`

**Steps:** Same pattern

---

### Task 41: zhidkiy-vosk

**Files:**
- Content: `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/content/zhidkiy-vosk_ru.md`
- Data: `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/data/zhidkiy-vosk_clean.json`
- Meta: `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/meta/zhidkiy-vosk_meta.json`

**Steps:** Same pattern

---

### Task 42: silanty

**Files:**
- Content: `categories/zashchitnye-pokrytiya/silanty/content/silanty_ru.md`
- Data: `categories/zashchitnye-pokrytiya/silanty/data/silanty_clean.json`
- Meta: `categories/zashchitnye-pokrytiya/silanty/meta/silanty_meta.json`

**Steps:** Same pattern

---

### Task 43: kvik-deteylery

**Files:**
- Content: `categories/zashchitnye-pokrytiya/kvik-deteylery/content/kvik-deteylery_ru.md`
- Data: `categories/zashchitnye-pokrytiya/kvik-deteylery/data/kvik-deteylery_clean.json`
- Meta: `categories/zashchitnye-pokrytiya/kvik-deteylery/meta/kvik-deteylery_meta.json`

**Steps:** Same pattern

---

## Batch 5: Полировка (4 categories)

### Task 44: polirovka (Hub Page)

**Files:**
- Content: `categories/polirovka/content/polirovka_ru.md`
- Data: `categories/polirovka/data/polirovka_clean.json`
- Meta: `categories/polirovka/meta/polirovka_meta.json`

**Steps:** Same pattern

---

### Task 45: polirovalnye-pasty

**Files:**
- Content: `categories/polirovka/polirovalnye-pasty/content/polirovalnye-pasty_ru.md`
- Data: `categories/polirovka/polirovalnye-pasty/data/polirovalnye-pasty_clean.json`
- Meta: `categories/polirovka/polirovalnye-pasty/meta/polirovalnye-pasty_meta.json`

**Steps:** Same pattern

---

### Task 46: mekhovye

**Files:**
- Content: `categories/polirovka/polirovalnye-krugi/mekhovye/content/mekhovye_ru.md`
- Data: `categories/polirovka/polirovalnye-krugi/mekhovye/data/mekhovye_clean.json`
- Meta: `categories/polirovka/polirovalnye-krugi/mekhovye/meta/mekhovye_meta.json`

**Steps:** Same pattern

---

### Task 47: akkumulyatornaya

**Files:**
- Content: `categories/polirovka/polirovalnye-mashinki/akkumulyatornaya/content/akkumulyatornaya_ru.md`
- Data: `categories/polirovka/polirovalnye-mashinki/akkumulyatornaya/data/akkumulyatornaya_clean.json`
- Meta: `categories/polirovka/polirovalnye-mashinki/akkumulyatornaya/meta/akkumulyatornaya_meta.json`

**Steps:** Same pattern

---

## Batch 6: Оборудование и Опт (3 categories)

### Task 48: oborudovanie (Hub Page)

**Files:**
- Content: `categories/oborudovanie/content/oborudovanie_ru.md`
- Data: `categories/oborudovanie/data/oborudovanie_clean.json`
- Meta: `categories/oborudovanie/meta/oborudovanie_meta.json`

**Steps:** Same pattern

---

### Task 49: apparaty-tornador

**Files:**
- Content: `categories/oborudovanie/apparaty-tornador/content/apparaty-tornador_ru.md`
- Data: `categories/oborudovanie/apparaty-tornador/data/apparaty-tornador_clean.json`
- Meta: `categories/oborudovanie/apparaty-tornador/meta/apparaty-tornador_meta.json`

**Steps:** Same pattern

---

### Task 50: opt-i-b2b

**Files:**
- Content: `categories/opt-i-b2b/content/opt-i-b2b_ru.md`
- Data: `categories/opt-i-b2b/data/opt-i-b2b_clean.json`
- Meta: `categories/opt-i-b2b/meta/opt-i-b2b_meta.json`

**Steps:** Same pattern

---

## Appendix A: Validation Commands

**Meta validation (all):**
```bash
python3 scripts/validate_meta.py --all
```

**Meta validation (single):**
```bash
python3 scripts/validate_meta.py categories/{path}/meta/{slug}_meta.json
```

**Content validation:**
```bash
python3 scripts/validate_content.py categories/{path}/content/{slug}_ru.md "{primary}" --mode seo
```

**Keyword density check:**
```bash
python3 scripts/check_keyword_density.py categories/{path}/content/{slug}_ru.md
```

**Water/nausea check:**
```bash
python3 scripts/check_water_natasha.py categories/{path}/content/{slug}_ru.md
```

---

## Appendix B: Data Extraction Commands

**Get name (для H1):**
```bash
cat categories/{path}/data/{slug}_clean.json | python3 -c "import json,sys; print(json.load(sys.stdin)['name'])"
```

**Get primary keywords:**
```bash
cat categories/{path}/meta/{slug}_meta.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('keywords_in_content',{}).get('primary',[]))"
```

**Get secondary keywords:**
```bash
cat categories/{path}/meta/{slug}_meta.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('keywords_in_content',{}).get('secondary',[]))"
```

**Get entities:**
```bash
cat categories/{path}/data/{slug}_clean.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('entities',[]))"
```

---

## Execution Checklist

- [ ] **Prerequisite:** Активирован `/content-generator` skill
- [ ] Batch 1: Мойка и экстерьер (18 tasks)
- [ ] Batch 2: Аксессуары (10 tasks)
- [ ] Batch 3: Уход за интерьером (8 tasks)
- [ ] Batch 4: Защитные покрытия (7 tasks)
- [ ] Batch 5: Полировка (4 tasks)
- [ ] Batch 6: Оборудование и Опт (3 tasks)

**Total: 50 categories**

---

**Plan Version:** 2.0 | **Updated:** 2026-01-20

**Changelog v2.0:**
- Добавлен prerequisite: активация `/content-generator` skill
- Обновлён чеклист под v3.1 (micro_intents убраны)
- Добавлена таблица источников данных (_meta.json vs _clean.json)
- Добавлены примеры частых фиксов (H2 keywords, RU-first, цифры)
- Добавлены команды извлечения данных из JSON
- Убраны ссылки на micro_intents
