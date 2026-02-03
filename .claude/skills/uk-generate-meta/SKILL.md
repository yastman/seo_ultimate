---
name: uk-generate-meta
description: Генерація українських мета-тегів (Title, Description, H1) для категорій Ultimate.net.ua. Use when /uk-generate-meta, генеруй UK мета, створи мета-теги українською, оновити українські мета, uk meta tags.
---

# UK Meta Tag Generator for Ultimate.net.ua

## Common Rules

See [../shared/meta-rules.md](../shared/meta-rules.md) for IRON RULE and common meta patterns.

This document contains **UK-specific** formulas only.


---

## January 2026 SEO Rules (UK)

| Параметр | Значення | Джерело |
|----------|----------|---------|
| Title | **30-60 chars (унікальна частина; до `\|` якщо `\|` використовується)** | validate_meta.py |
| Title formula | **{primary_keyword} — купити** (Front-loading) | Ahrefs 2025 |
| Description | **100-160 chars** | validate_meta.py |
| H1 | **= {primary_keyword} БЕЗ "Купити"** | John Mueller 2025 |
| Commercial modifiers | **Після ВЧ у Title** | Ahrefs, BigCommerce |
| Заборонено | Назви товарів/SKU, бренди конкурентів, marketing fluff, розведення | правила проекту + перевірки |

---

## Терміни та джерела істини

### Що таке `{primary_keyword}`

Це ключ з **максимальним volume** у категорії. Його потрібно використовувати в Title/H1/Description як основу.

**🚨 ВАЖЛИВО: primary_keyword = MAX(volume), НЕ перший у списку!**

**Алгоритм визначення з `uk/categories/{slug}/data/{slug}_clean.json`:**

1) **List-схема:**
```json
"keywords": [
  {"keyword": "піна для миття авто", "volume": 1300},
  {"keyword": "активна піна", "volume": 720}
]
```
→ `{primary_keyword}` = ключ з MAX(volume) = `"піна для миття авто"` (1300)

2) **Dict-схема:**
```json
"keywords": {"primary": [{"keyword": "очищувач дисків", "volume": 70}]}
```
→ `{primary_keyword}` = ключ з MAX(volume) з `keywords.primary[]`

**Як знайти:**
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

Якщо keywords порожній або не знайдено — це проблема даних, мета генерувати не можна.

### Acceptance criteria (що значить "готово")

Файл `uk/categories/{slug}/meta/{slug}_meta.json` повинен проходити:
`python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json --keywords uk/categories/{slug}/data/{slug}_clean.json`

---

## 🏭 Два типи категорій: Producer vs Shop

**ВАЖЛИВО:** Description залежить від наявності товарів бренду Ultimate в категорії.

### Категорії З товарами Ultimate (Producer pattern)
```
{primary_keyword} від виробника Ultimate. {Типи} — {деталі}. Опт і роздріб.
```
- ✅ "від виробника Ultimate"
- ✅ "Опт і роздріб" в кінці

### Категорії БЕЗ товарів Ultimate (Shop pattern)
```
{primary_keyword} в інтернет-магазині Ultimate. {Типи} — {деталі}.
```
- ✅ "в інтернет-магазині Ultimate"
- ❌ НЕМАє "Опт і роздріб"
- ❌ НЕМАє назв брендів (Meguiar's, Gtechniq, Koch тощо)

### Як визначити тип категорії?
Перевірити в SQL базі `data/dumps/ultimate_net_ua_backup.sql`:
- manufacturer_id=13 → Ultimate
- Якщо в категорії є товари з manufacturer_id=13 → Producer pattern
- Якщо немає → Shop pattern

### Категорії БЕЗ товарів Ultimate (Shop pattern):
*(Знімок на January 2026; список може застарівати. При конфлікті довіряй факту з SQL.)*
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

## 🚨 IRON RULE: primary_keyword — ДОСЛІВНО

**`{primary_keyword}` з `_clean.json` використовується в Title/H1/Description без зміни слів і порядку.**

Допускається лише:
- капіталізація першої літери (за стилем), без зміни слів/відмінків/синонімів.

```
_clean.json: "keywords": [{"keyword": "віск для авто", "volume": 1000}]

✅ Title: Віск для авто — купити, ціни | Ultimate
✅ H1: Віск для авто

❌ Title: Автовіск — купити | Ultimate           ← ЗМІНИВ КЛЮЧ!
❌ Title: Віск для авто для авто — купити        ← ДОДАВ "для авто"!
❌ H1: Автомобільний віск                        ← ЗМІНИВ КЛЮЧ!
```

**Не можна:**
- Міняти порядок слів
- Додавати слова ("авто" → "автомобільний", додавати "для авто")
- Склеювати слова ("віск для авто" → "автовіск")
- "Покращувати" або "оптимізувати" ключ
- Використовувати синоніми замість primary_keyword

**Чому:** `{primary_keyword}` — це ТОП ВЧ ключ за volume. Будь-яка "оптимізація" ключа руками = ризик втрати точного збігу та позицій.

---

## Title (30-60 chars, унікальна частина)

**Як рахувати довжину (як у `validate_meta.py`):**
- якщо в Title є `|` → довжина рахується тільки для частини зліва від `|`
- якщо `|` немає → довжина рахується по всьому рядку

### Адаптивна формула:

```
ЯКЩО primary_keyword ≤ 20 chars:
  {primary_keyword} — купити в інтернет-магазині Ultimate

ІНАКШЕ:
  {primary_keyword} — купити, ціни | Ultimate
```

**Приклади:**

| primary_keyword | Довжина | Title |
|-----------------|---------|-------|
| силант | 6 | Силант — купити в інтернет-магазині Ultimate |
| віск для авто | 13 | Віск для авто — купити в інтернет-магазині Ultimate |
| полірувальна машинка | 20 | Полірувальна машинка — купити в інтернет-магазині Ultimate |
| догляд за салоном авто | 22 | Догляд за салоном авто — купити, ціни \| Ultimate |
| акумуляторна полірувальна машина | 33 | Акумуляторна полірувальна машина — купити, ціни \| Ultimate |

**Правила:**
- **primary_keyword В НАЧАЛО** (Front-loading!) — або "Купити {keyword}", або "{keyword} — купити"
- Commercial modifiers **ПІСЛЯ** primary_keyword
- Бренд **В КІНЕЦЬ** `| Ultimate`
- **БЕЗ двокрапки** (Google замінює на дефіс)
- **Мінімум 30 chars** в унікальній частині — інакше WARNING

---

## Description (100-160 chars)

### Формула (Producer pattern — є товари Ultimate):

```
{primary_keyword} від виробника Ultimate. {Призначення/типи} — {деталі}. Опт і роздріб.
```

### Формула (Shop pattern — НЕМАє товарів Ultimate):

```
{primary_keyword} в інтернет-магазині Ultimate. {Призначення/типи} — {деталі}.
```

### Приклади Producer pattern (З товарами Ultimate):

```
✅ Силант від виробника Ultimate. Полімерний захист кузова — гідрофобний ефект, захист 3–6 місяців. Опт і роздріб.

✅ Активна піна від виробника Ultimate. Безконтактна мийка — лужні та нейтральні, концентрати й готові. Опт і роздріб.

✅ Антибітум від виробника Ultimate. Видалення бітуму та смоли — сольвентні та лужні склади. Опт і роздріб.
```

### Приклади Shop pattern (БЕЗ товарів Ultimate):

```
✅ Полірувальна машинка в інтернет-магазині Ultimate. Роторні, ексцентрикові, акумуляторні — діаметр 75–180мм.

✅ Щітки для детейлінгу в інтернет-магазині Ultimate. Для кузова, салону, дисків — м'які та жорсткі, всі розміри.

✅ Глина для авто в інтернет-магазині Ultimate. Глибоке очищення кузова — глина синя, жовта, автоскраби.
```

### 🚨 ОБОВ'ЯЗКОВІ ЕЛЕМЕНТИ:

**Producer pattern:**
1. **primary_keyword** — на початку Description
2. **"від виробника Ultimate"** — одразу після keyword
3. **"Опт і роздріб"** — в кінці

**Shop pattern:**
1. **primary_keyword** — на початку Description
2. **"в інтернет-магазині Ultimate"** — одразу після keyword
3. ❌ НЕМАє "Опт і роздріб"
4. ❌ НЕМАє назв брендів

### ❌ ЗАБОРОНЕНО в Description:

| Заборонено | Чому | Правильно |
|------------|------|-----------|
| Назви товарів (Bitumen Buster) | Користувач не знає SKU | Типи: "сольвентні", "лужні" |
| Назви брендів (Meguiar's, Gtechniq) | Динамічні дані, можуть змінюватися | Тільки "Ultimate" як магазин |
| Marketing fluff (швидко, якісно) | Валідатор відхилить | Факти: "видаляє смолу" |
| Розведення (1:5, 1:10) | Це для контенту | Тільки об'єми: 0.5л, 1л, 5л |
| Довгі описи >160 chars | Обріжеться в SERP | Короткі типи + об'єми |

### ✅ Що використовувати:

| Поле | Джерело | Приклад |
|------|---------|---------|
| **Типи** | PRODUCTS_LIST.md | лужні, кислотні, сольвентні |
| **Форми** | PRODUCTS_LIST.md | концентрати, готові, спреї |
| **Об'єми** | PRODUCTS_LIST.md | 0.5л, 1л, 5л, 20л |
| **Ефект** | entities | матовий, гідрофобний, UV-захист |

---

## H1 (= primary_keyword → PLURAL)

**🚨 КРИТИЧНО: H1 має бути у МНОЖИНІ, бо категорія містить багато товарів.**

**Формула:** `{primary_keyword}` → **конвертувати в множину**

### Таблиця конвертації (UK)

| Однина | Множина |
|--------|---------|
| Очищувач | **Очищувачі** |
| Поліроль | **Поліролі** |
| Силант | **Силанти** |
| Знежирювач | **Знежирювачі** |
| Плямовивідник | **Плямовивідники** |
| Поглинач | **Нейтралізатори** |
| Губка | **Губки** |
| Відро | **Відра** |
| Набір | **Набори** |
| Віск | **Воски** |
| Шампунь | **Шампуні** |
| Щітка | **Щітки** |
| Машинка | **Машинки** |
| Круг | **Круги** |
| Засіб | **Засоби** |
| Торнадор | **Торнадори** |
| Відновлювач | **Відновлювачі** |

### Алгоритм

1. Взяти `{primary_keyword}` з `_clean.json` (MAX volume)
2. Конвертувати **перше слово** в множину за таблицею
3. Решту фрази залишити без змін

```
primary_keyword: "очищувач дисків" (однина)
H1: "Очищувачі дисків" (множина) ✅

primary_keyword: "силант для авто" (однина)
H1: "Силанти для авто" (множина) ✅

primary_keyword: "губка для авто" (однина)
H1: "Губки для авто" (множина) ✅
```

### Виключення (вже множина або збірне)

НЕ конвертувати:
- glavnaya (Автохімія — збірне)
- aksessuary (Аксесуари — вже множина)
- oborudovanie (Обладнання — збірне)
- zashchitnye-pokrytiya (Захисні покриття — вже множина)
- polirovka (Полірування — процес)

**Інші правила:**
- **БЕЗ "Купити"**
- НЕ додавати "для авто" якщо його немає в keyword

---

## JSON Output Format

```json
{
  "slug": "{slug}",
  "language": "uk",
  "meta": {
    "title": "{H1_PLURAL} — купити, ціни | Ultimate",
    "description": "{H1_PLURAL} від виробника Ultimate. {Типи/призначення} — {деталі}. Опт і роздріб."
  },
  "h1": "{H1_PLURAL}",  // ← МНОЖИНА!
  "h1": "{primary_keyword}",
  "keywords_in_content": {
    "primary": ["keyword1", "keyword2"],
    "secondary": ["keyword3", "keyword4"],
    "supporting": ["keyword5", "keyword6"]
  },
  "types": ["тип1", "тип2"],
  "forms": ["концентрат", "готовий"],
  "volumes": ["0.5л", "1л", "5л"],
  "updated_at": "2026-01-26"
}
```

---

## Workflow

1. **Прочитати** `uk/categories/{slug}/data/{slug}_clean.json`
   - Визначити `{primary_keyword}` (див. "Терміни та джерела істини" вище)
   - Перевірити довжину `{primary_keyword}` для вибору формули Title

2. **Знайти товари** в `data/generated/PRODUCTS_LIST.md`
   - Витягнути **типи**: лужні, кислотні, сольвентні
   - Витягнути **форми**: концентрати, готові, спреї
   - Витягнути **об'єми**: 0.5л, 1л, 5л, 20л

3. **Застосувати формули:**
   - Title: адаптивна формула (див. вище)
   - H1: `{primary_keyword}` (без "купити", без додавань)
   - Description: Producer/Shop формула (див. вище)

4. **Перевірити:**
   - ✅ Title містить primary_keyword ДОСЛІВНО (за словами і порядком)
   - ✅ Title 30-60 chars (унікальна частина)
   - ✅ H1 = primary_keyword ДОСЛІВНО (за словами і порядком)
   - ✅ Description 100-160 chars
   - ✅ Description містить primary_keyword і коректний патерн (Producer або Shop)
   - ❌ НЕМАє назв товарів, fluff, розведення

5. **Зберегти** в `uk/categories/{slug}/meta/{slug}_meta.json`

6. **Валідація:** `python3 scripts/validate_meta.py {path}` → має бути PASS

---

## Validation Checklist

### Title:
- [ ] **primary_keyword ДОСЛІВНО** (за словами і порядком) ← IRON RULE!
- [ ] **30-60 chars (унікальна частина, див. правило `|`)**
- [ ] **Містить "купити"** ПІСЛЯ primary_keyword
- [ ] Без двокрапки

### Description (Producer pattern — є товари Ultimate):
- [ ] **100-160 chars**
- [ ] **Починається з primary_keyword**
- [ ] **Містить "від виробника Ultimate"**
- [ ] **Містить "Опт і роздріб"**
- [ ] **НЕМАє** назв товарів, брендів, fluff, розведення

### Description (Shop pattern — НЕМАє товарів Ultimate):
- [ ] **100-160 chars**
- [ ] **Починається з primary_keyword**
- [ ] **Містить "в інтернет-магазині Ultimate"**
- [ ] **НЕМАє "Опт і роздріб"**
- [ ] **НЕМАє** назв товарів, брендів, fluff, розведення

### H1:
- [ ] **= primary_keyword ДОСЛІВНО** ← IRON RULE!
- [ ] **БЕЗ "Купити"**
- [ ] **БЕЗ додавань** ("для авто" тощо)

---

## 🚩 Red Flags — СТОП і виправ

Якщо ти думаєш щось із цього — ти раціоналізуєш:

| Думка | Реальність |
|-------|------------|
| "Автовіск звучить краще" | primary_keyword = дані семантики. Твоя думка ≠ дані. |
| "Додам для авто для ясності" | Якщо в primary_keyword немає "для авто" — НЕ додавай! |
| "Це ж синонім" | Синонім ≠ точний збіг. Google розрізняє. |
| "Так коротше/довше" | Довжина регулюється хвостом Title, НЕ ключем. |
| "Я оптимізую" | Оптимізація = використовувати primary_keyword за словами і порядком. |

**Всі ці думки = повернись до `_clean.json` і візьми primary_keyword ДОСЛІВНО (за словами і порядком).**

---

## Output

```
uk/categories/{slug}/meta/{slug}_meta.json (validated)

Status: ready for /uk-content-generator
```

---

**Version:** 16.1 — January 2026

**Changelog v16.1:**
- 🔧 Синхронізовано формулу Title з RU: "в інтернет-магазині" замість "в Україні"
- 📏 Виправлено Front-loading: ключ на початку, не "Купити"

**Changelog v16.0:**
- 🎯 **КРИТИЧНО: primary_keyword = MAX(volume)**, НЕ перший у списку
- 🔧 Додано Python-код для визначення primary_keyword
- 📋 Після semantic-cluster порядок ключів може змінитись — завжди шукати MAX

**Changelog v15.1:**
- ADDED: Reference to shared/meta-rules.md for common rules

**Changelog v15.0:**
- **Синхронізовано з RU v15.0** — повний паритет
- 🔧 Введено термін `{primary_keyword}` і описані 2 схеми `_clean.json` (list/dict)
- 📏 Уточнено правило підрахунку довжини Title (унікальна частина, логіка `|` як у валідаторі)
- 🧱 IRON RULE уточнено: слова/порядок незмінні, допускається капіталізація першої літери
- 🏭 **Producer vs Shop pattern:** два типи Description залежно від наявності товарів Ultimate
- ❌ **Заборонено:** назви брендів (Meguiar's, Gtechniq) — динамічні дані
- 📋 **Список Shop-категорій:** 14 категорій без товарів Ultimate

**Changelog v1.1:**
- Додано Red Flags секцію
- Базова синхронізація з generate-meta
