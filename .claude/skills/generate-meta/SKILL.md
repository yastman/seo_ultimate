---
name: generate-meta
description: Use when you see /generate-meta, генерируй мета, создай мета теги, оновити мета, обнови мета. (project)
---

# Meta Tag Generator for Ultimate.net.ua

---

## January 2026 SEO Rules

| Параметр | Значение | Источник |
|----------|----------|----------|
| Title | **30-60 chars (уникальная часть; до `|` если `|` используется)** | validate_meta.py |
| Title formula | **{primary_keyword} — купить** (Front-loading) | Ahrefs 2025 |
| Description | **100-160 chars** | validate_meta.py |
| H1 | **= {primary_keyword} БЕЗ "Купить/Купити"** | John Mueller 2025 |
| Commercial modifiers | **После ВЧ в Title** | Ahrefs, BigCommerce |
| Запрещено | Названия товаров/SKU, бренды конкурентов, marketing fluff, разведение | правила проекта + проверки |

---

## Термины и источники правды

### Что такое `{primary_keyword}`

Это ключ с **максимальным volume** в категории. Его нужно использовать в Title/H1/Description как основу.

**🚨 ВАЖНО: primary_keyword = MAX(volume), НЕ первый в списке!**

**Алгоритм определения из `categories/{slug}/data/{slug}_clean.json`:**

1) **List-схема:**
```json
"keywords": [
  {"keyword": "пена для мойки авто", "volume": 1300},
  {"keyword": "активная пена", "volume": 720}
]
```
→ `{primary_keyword}` = ключ с MAX(volume) = `"пена для мойки авто"` (1300)

2) **Dict-схема:**
```json
"keywords": {"primary": [{"keyword": "очиститель дисков", "volume": 70}]}
```
→ `{primary_keyword}` = ключ с MAX(volume) из `keywords.primary[]`

**Как найти:**
```python
# List-схема
keywords = data.get("keywords", [])
if isinstance(keywords, list) and keywords:
    primary = max(keywords, key=lambda x: x.get("volume", 0))
    primary_keyword = primary["keyword"]

# Dict-схема
if isinstance(keywords, dict):
    primary_list = keywords.get("primary", [])
    primary = max(primary_list, key=lambda x: x.get("volume", 0))
    primary_keyword = primary["keyword"]
```

Если keywords пуст или не найден — это проблема данных, мета генерировать нельзя.

### Acceptance criteria (что значит “готово”)

Файл `categories/{slug}/meta/{slug}_meta.json` должен проходить:
`python3 scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json --keywords categories/{slug}/data/{slug}_clean.json`

---

## 🏭 Два типа категорий: Producer vs Shop

**ВАЖНО:** Description зависит от наличия товаров бренда Ultimate в категории.

### Категории С товарами Ultimate (Producer pattern)
```
{primary_keyword} от производителя Ultimate. {Типы} — {подробности}. Опт и розница.
```
- ✅ "от производителя Ultimate"
- ✅ "Опт и розница" в конце

### Категории БЕЗ товаров Ultimate (Shop pattern)
```
{primary_keyword} в интернет-магазине Ultimate. {Типы} — {подробности}.
```
- ✅ "в интернет-магазине Ultimate"
- ❌ НЕТ "Опт и розница"
- ❌ НЕТ названий брендов (Meguiar's, Gtechniq, Koch и т.д.)

### Как определить тип категории?
Проверить в SQL базе `data/dumps/ultimate_net_ua_backup.sql`:
- manufacturer_id=13 → Ultimate
- Если в категории есть товары с manufacturer_id=13 → Producer pattern
- Если нет → Shop pattern

### Категории БЕЗ товаров Ultimate (Shop pattern):
*(Снимок на January 2026; список может устаревать. При конфликте доверяй факту из SQL.)*
- glina-i-avtoskraby
- gubki-i-varezhki
- cherniteli-shin
- raspyliteli-i-penniki
- vedra-i-emkosti
- kisti-dlya-deteylinga
- shchetka-dlya-moyki-avto
- shchetki-i-kisti
- malyarniy-skotch
- polirovka
- polirovalnye-krugi
- polirovalnye-mashinki
- oborudovanie
- apparaty-tornador

---

## 🚨 IRON RULE: primary_keyword — ДОСЛОВНО

**`{primary_keyword}` из `_clean.json` используется в Title/H1/Description без изменения слов и порядка.**

Допускается только:
- капитализация первой буквы (по стилю), без изменения слов/падежей/синонимов.

```
_clean.json: "keywords": [{"keyword": "воск для авто", "volume": 1000}]

✅ Title: Воск для авто — купить, цены | Ultimate
✅ H1: Воск для авто

❌ Title: Автовоск — купить | Ultimate           ← ИЗМЕНИЛ КЛЮЧ!
❌ Title: Воск для авто для авто — купить        ← ДОБАВИЛ "для авто"!
❌ H1: Автомобильный воск                        ← ИЗМЕНИЛ КЛЮЧ!
```

**Нельзя:**
- Менять порядок слов
- Добавлять слова ("авто" → "автомобильный", добавлять "для авто")
- Склеивать слова ("воск для авто" → "автовоск")
- "Улучшать" или "оптимизировать" ключ
- Использовать синонимы вместо primary_keyword

**Почему:** `{primary_keyword}` — это ТОП ВЧ ключ по volume. Любая “оптимизация” ключа руками = риск потери точного совпадения и позиций.

---

## Title (30-60 chars, уникальная часть)

**Как считать длину (как в `validate_meta.py`):**
- если в Title есть `|` → длина считается только для части слева от `|`
- если `|` нет → длина считается по всей строке

### Адаптивная формула:

```
ЕСЛИ primary_keyword ≤ 20 chars:
  {primary_keyword} — купить в интернет-магазине Ultimate

ИНАЧЕ:
  {primary_keyword} — купить, цены | Ultimate
```

**Примеры:**

| primary_keyword | Длина | Title |
|-------------|-------|-------|
| силант | 6 | Силант — купить в интернет-магазине Ultimate |
| воск для авто | 13 | Воск для авто — купить в интернет-магазине Ultimate |
| полировочная машинка | 20 | Полировочная машинка — купить в интернет-магазине Ultimate |
| уход за салоном авто | 20 | Уход за салоном авто — купить в интернет-магазине Ultimate |
| наборы для детейлинга | 21 | Наборы для детейлинга — купить, цены \| Ultimate |
| аккумуляторная полировальная машина | 35 | Аккумуляторная полировальная машина — купить, цены \| Ultimate |

**Правила:**
- **primary_keyword В НАЧАЛО** (Front-loading!)
- Commercial modifiers **ПОСЛЕ** primary_keyword
- Бренд **В КОНЕЦ** `| Ultimate` или `Ultimate`
- **БЕЗ двоеточий** (Google заменяет на дефис)
- **Минимум 30 chars** в уникальной части — иначе WARNING

---

## Description (100-160 chars)

### Формула (Producer pattern — есть товары Ultimate):

```
{primary_keyword} от производителя Ultimate. {Назначение/типы} — {подробности}. Опт и розница.
```

### Формула (Shop pattern — НЕТ товаров Ultimate):

```
{primary_keyword} в интернет-магазине Ultimate. {Назначение/типы} — {подробности}.
```

### Примеры Producer pattern (С товарами Ultimate):

```
✅ Силант от производителя Ultimate. Полимерная защита кузова — гидрофобный эффект, защита 3–6 месяцев. Опт и розница.

✅ Активная пена от производителя Ultimate. Бесконтактная мойка — щелочные и нейтральные, концентраты и готовые. Опт и розница.

✅ Антибитум от производителя Ultimate. Удаление битума и смолы — сольвентные и щелочные составы. Опт и розница.
```

### Примеры Shop pattern (БЕЗ товаров Ultimate):

```
✅ Полировочная машинка в интернет-магазине Ultimate. Роторные, эксцентриковые, аккумуляторные — диаметр 75–180мм.

✅ Щетки для детейлинга в интернет-магазине Ultimate. Для кузова, салона, дисков — мягкие и жёсткие, все размеры.

✅ Глина для авто в интернет-магазине Ultimate. Глубокая очистка кузова — глина синяя, жёлтая, автоскрабы.
```

### 🚨 ОБЯЗАТЕЛЬНЫЕ ЭЛЕМЕНТЫ:

**Producer pattern:**
1. **primary_keyword** — в начале Description
2. **"от производителя Ultimate"** — сразу после keyword
3. **"Опт и розница"** — в конце

**Shop pattern:**
1. **primary_keyword** — в начале Description
2. **"в интернет-магазине Ultimate"** — сразу после keyword
3. ❌ НЕТ "Опт и розница"
4. ❌ НЕТ названий брендов

### ❌ ЗАПРЕЩЕНО в Description:

| Запрещено | Почему | Правильно |
|-----------|--------|-----------|
| Названия товаров (Bitumen Buster) | Пользователь не знает SKU | Типы: "сольвентные", "щелочные" |
| Названия брендов (Meguiar's, Gtechniq) | Динамические данные, могут меняться | Только "Ultimate" как магазин |
| Marketing fluff (быстро, качественно) | Валидатор отклонит | Факты: "удаляет смолу" |
| Разведение (1:5, 1:10) | Это для контента | Только объёмы: 0.5л, 1л, 5л |
| Длинные описания >160 chars | Обрежется в SERP | Краткие типы + объёмы |

### ✅ Что использовать:

| Поле | Источник | Пример |
|------|----------|--------|
| **Типы** | PRODUCTS_LIST.md | щелочные, кислотные, сольвентные |
| **Формы** | PRODUCTS_LIST.md | концентраты, готовые, спреи |
| **Объёмы** | PRODUCTS_LIST.md | 0.5л, 1л, 5л, 20л |
| **Эффект** | entities | матовый, гидрофобный, UV-защита |

---

## H1 (= primary_keyword → PLURAL)

**🚨 КРИТИЧНО: H1 должен быть во МНОЖЕСТВЕННОМ числе, т.к. категория содержит много товаров.**

**Формула:** `{primary_keyword}` → **конвертировать в множественное**

### Таблица конвертации (RU)

| Единственное | Множественное |
|--------------|---------------|
| Очиститель | **Очистители** |
| Полироль | **Полироли** |
| Силант | **Силанты** |
| Обезжириватель | **Обезжириватели** |
| Пятновыводитель | **Пятновыводители** |
| Нейтрализатор | **Нейтрализаторы** |
| Губка | **Губки** |
| Ведро | **Вёдра** |
| Набор | **Наборы** |
| Воск | **Воски** |
| Шампунь | **Шампуни** |
| Щётка | **Щётки** |
| Машинка | **Машинки** |
| Круг | **Круги** |
| Средство | **Средства** |
| Торнадор | **Торнадоры** |
| Восстановитель | **Восстановители** |

### Алгоритм

1. Взять `{primary_keyword}` из `_clean.json` (MAX volume)
2. Конвертировать **первое слово** в множественное по таблице
3. Остальную фразу оставить без изменений

```
primary_keyword: "очиститель дисков" (ед.ч.)
H1: "Очистители дисков" (мн.ч.) ✅

primary_keyword: "силант для авто" (ед.ч.)
H1: "Силанты для авто" (мн.ч.) ✅

primary_keyword: "губка для авто" (ед.ч.)
H1: "Губки для авто" (мн.ч.) ✅
```

### Исключения (уже множественное или собирательное)

НЕ конвертировать:
- glavnaya (Автохимия — собирательное)
- aksessuary (Аксессуары — уже множественное)
- oborudovanie (Оборудование — собирательное)
- zashchitnye-pokrytiya (Защитные покрытия — уже множественное)
- polirovka (Полировка — процесс)

**Другие правила:**
- **БЕЗ "Купить"**
- НЕ добавлять "для авто" если его нет в keyword

---

## JSON Output Format

```json
{
  "slug": "{slug}",
  "language": "ru",
  "meta": {
    "title": "{H1_PLURAL} — купить, цены | Ultimate",
    "description": "{H1_PLURAL} от производителя Ultimate. {Типы/назначение} — {подробности}. Опт и розница."
  },
  "h1": "{H1_PLURAL}",  // ← МНОЖЕСТВЕННОЕ!
  "h1": "{primary_keyword}",
  "keywords_in_content": {
    "primary": ["keyword1", "keyword2"],
    "secondary": ["keyword3", "keyword4"],
    "supporting": ["keyword5", "keyword6"]
  },
  "types": ["тип1", "тип2"],
  "forms": ["концентрат", "готовый"],
  "volumes": ["0.5л", "1л", "5л"],
  "updated_at": "2026-01-07"
}
```

---

## Workflow

1. **Прочитать** `categories/{slug}/data/{slug}_clean.json`
   - Определить `{primary_keyword}` (см. “Термины и источники правды” выше)
   - Проверить длину `{primary_keyword}` для выбора формулы Title

2. **Найти товары** в `data/generated/PRODUCTS_LIST.md`
   - Извлечь **типы**: щелочные, кислотные, сольвентные
   - Извлечь **формы**: концентраты, готовые, спреи
   - Извлечь **объёмы**: 0.5л, 1л, 5л, 20л

3. **Применить формулы:**
   - Title: адаптивная формула (см. выше)
   - H1: `{primary_keyword}` (без "купить", без добавлений)
   - Description: Producer/Shop формула (см. выше)

4. **Проверить:**
   - ✅ Title содержит primary_keyword ДОСЛОВНО (по словам и порядку)
   - ✅ Title 30-60 chars (уникальная часть)
   - ✅ H1 = primary_keyword ДОСЛОВНО (по словам и порядку)
   - ✅ Description 100-160 chars
   - ✅ Description содержит primary_keyword и корректный паттерн (Producer или Shop)
   - ❌ НЕТ названий товаров, fluff, разведения

5. **Сохранить** в `categories/{slug}/meta/{slug}_meta.json`

6. **Валидация:** `python3 scripts/validate_meta.py {path}` → должен быть PASS

---

## Validation Checklist

### Title:
- [ ] **primary_keyword ДОСЛОВНО** (по словам и порядку) ← IRON RULE!
- [ ] **30-60 chars (уникальная часть, см. правило `|`)**
- [ ] **primary_keyword в начале** (НЕ "Купить" первым!)
- [ ] Содержит "купить" ПОСЛЕ primary_keyword
- [ ] Без двоеточия

### Description (Producer pattern — есть товары Ultimate):
- [ ] **100-160 chars**
- [ ] **Начинается с primary_keyword**
- [ ] **Содержит "от производителя Ultimate"**
- [ ] **Содержит "Опт и розница"**
- [ ] **НЕТ** названий товаров, брендов, fluff, разведения

### Description (Shop pattern — НЕТ товаров Ultimate):
- [ ] **100-160 chars**
- [ ] **Начинается с primary_keyword**
- [ ] **Содержит "в интернет-магазине Ultimate"**
- [ ] **НЕТ "Опт и розница"**
- [ ] **НЕТ** названий товаров, брендов, fluff, разведения

### H1:
- [ ] **= primary_keyword ДОСЛОВНО** ← IRON RULE!
- [ ] **БЕЗ "Купить/Купити"**
- [ ] **БЕЗ добавлений** ("для авто" и т.п.)

---

## Quick Translation RU → UK

| RU | UK |
|----|-----|
| Купить | Купити |
| цены | ціни |
| в интернет-магазине | в інтернет-магазині |
| производителя | виробника |
| опт и розница | опт і роздріб |
| доставка | доставка |
| щелочная | лужна |
| кислотная | кислотна |

---

## 🚩 Red Flags — СТОП и исправь

Если ты думаешь что-то из этого — ты рационализируешь:

| Мысль | Реальность |
|-------|------------|
| "Автовоск звучит лучше" | primary_keyword = данные семантики. Твоё мнение ≠ данные. |
| "Добавлю для авто для ясности" | Если в primary_keyword нет "для авто" — НЕ добавляй! |
| "Это же синоним" | Синоним ≠ точное совпадение. Google различает. |
| "Так короче/длиннее" | Длина регулируется хвостом Title, НЕ ключом. |
| "Я оптимизирую" | Оптимизация = использовать primary_keyword по словам и порядку. |

**Все эти мысли = вернись к `_clean.json` и возьми primary_keyword ДОСЛОВНО (по словам и порядку).**

---

## Output

```
categories/{slug}/meta/{slug}_meta.json (validated)

Status: ready for /seo-research
```

---

**Version:** 16.1 — February 2026

**Changelog v16.1:**
- **SYNCED with UK v16.1** — повний паритет

**Changelog v16.0:**
- 🎯 **КРИТИЧНО: primary_keyword = MAX(volume)**, НЕ первый в списке
- 🔧 Добавлен Python-код для определения primary_keyword
- 📋 После semantic-cluster порядок ключей может измениться — всегда искать MAX

**Changelog v15.0:**
- 🔧 Введён термин `{primary_keyword}` и описаны 2 схемы `_clean.json` (list/dict)
- 📏 Уточнено правило подсчёта длины Title (уникальная часть, логика `|` как в валидаторе)
- 🧱 IRON RULE уточнено: слова/порядок неизменны, допускается капитализация первой буквы
- 🚚 “Доставка” переведена в optional (не является обязательной проверкой `validate_meta.py`)

**Changelog v14.0:**
- 🏭 **Producer vs Shop pattern:** два типа Description в зависимости от наличия товаров Ultimate
- ✅ **Producer:** "от производителя Ultimate" + "Опт и розница"
- ✅ **Shop:** "в интернет-магазине Ultimate" (без опта, без брендов)
- ❌ **Запрещено:** названия брендов (Meguiar's, Gtechniq) — динамические данные
- 📋 **Список Shop-категорий:** 14 категорий без товаров Ultimate

**Changelog v13.0:**
- 🎯 **Адаптивная формула Title:** если primary_keyword ≤ 20 chars → "купить в интернет-магазине Ultimate"
- ❌ **Запрещено:** разведение (1:5) — это для контента, не для мета
- 🔧 **H1:** строго = primary_keyword (по словам и порядку), без добавлений "для авто"
- ✅ **Validation:** Description 100-160 chars (не 120-160)

**Changelog v12.0:**
- IRON RULE: primary_keyword используется ДОСЛОВНО (по словам и порядку)
- Red Flags: таблица рационализаций
