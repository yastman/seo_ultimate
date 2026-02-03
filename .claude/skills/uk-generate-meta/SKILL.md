---
name: uk-generate-meta
description: Генерація українських мета-тегів (Title, Description, H1) для категорій Ultimate.net.ua. Use when /uk-generate-meta, генеруй UK мета, створи мета-теги українською, оновити українські мета, uk meta tags.
---

# UK Meta Tag Generator for Ultimate.net.ua

## Common Rules

See [../shared/meta-rules.md](../shared/meta-rules.md) for IRON RULE and common meta patterns.

This document contains **UK-specific** formulas only.

---

## February 2026 SEO Rules (UK)

| Параметр | Значення | Джерело |
|----------|----------|---------|
| Title | **30-60 chars (унікальна частина; до `\|` якщо `\|` використовується)** | validate_meta.py |
| Title formula | **{title_phrase} — купити** (Front-loading) | Ahrefs 2025 |
| Description | **100-160 chars** | validate_meta.py |
| H1 | **= {title_phrase} БЕЗ "Купити"** | John Mueller 2025 |
| Commercial modifiers | **Після ВЧ у Title** | Ahrefs, BigCommerce |
| Заборонено | Назви товарів/SKU, бренди конкурентів, marketing fluff, розведення | правила проекту + перевірки |

---

## Терміни та джерела істини

### Що таке `{title_phrase}` (головний термін!)

**🚨 КРИТИЧНО:** `{title_phrase}` — це фраза для Title/H1/Description.

```
{title_phrase} = category_title ?? primary_keyword
```

**Логіка:**
1. Якщо в `_clean.json` є поле `category_title` → використовувати його
2. Інакше → використовувати `primary_keyword` (MAX volume)

### Що таке `{category_title}`

**Опціональне поле** в `_clean.json` для складених категорій або категорій з двома ВЧ-ключами.

```json
{
  "id": "gubki-i-varezhki",
  "category_title": "Губки та рукавички",
  "keywords": [...]
}
```

**Коли є `category_title`:**
1. **Складена категорія** — назва містить "та" (Щітки та пензлі, Губки та рукавички)
2. **Два сильних ВЧ-ключі** — потрібно охопити обидва (Автохімія та автокосметика)

### Що таке `{primary_keyword}`

Це ключ з **максимальним volume** у категорії. Використовується як fallback якщо немає `category_title`.

**🚨 ВАЖЛИВО: primary_keyword = MAX(volume), НЕ перший у списку!**

**Алгоритм визначення з `uk/categories/{slug}/data/{slug}_clean.json`:**

```python
# Спочатку перевірити category_title
if data.get("category_title"):
    title_phrase = data["category_title"]
else:
    # Fallback: MAX(volume) з keywords
    keywords = data.get("keywords", [])
    if isinstance(keywords, list) and keywords:
        primary = max(keywords, key=lambda x: x.get("volume", 0))
        title_phrase = primary["keyword"]
```

### Acceptance criteria

Файл `uk/categories/{slug}/meta/{slug}_meta.json` повинен проходити:
`python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json --keywords uk/categories/{slug}/data/{slug}_clean.json`

---

## 🏭 Два типи категорій: Producer vs Shop

**ВАЖЛИВО:** Description залежить від наявності товарів бренду Ultimate в категорії.

### Категорії З товарами Ultimate (Producer pattern)
```
{title_phrase} від виробника Ultimate. {Типи} — {деталі}. Опт і роздріб.
```
- ✅ "від виробника Ultimate"
- ✅ "Опт і роздріб" в кінці

### Категорії БЕЗ товарів Ultimate (Shop pattern)
```
{title_phrase} в інтернет-магазині Ultimate. {Типи} — {деталі}.
```
- ✅ "в інтернет-магазині Ultimate"
- ❌ НЕМАє "Опт і роздріб"
- ❌ НЕМАє назв брендів (Meguiar's, Gtechniq, Koch тощо)

### Категорії БЕЗ товарів Ultimate (Shop pattern):
*(Знімок на February 2026; список може застарівати. При конфлікті довіряй факту з SQL.)*
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

## Title та H1 Формула

**КРИТИЧНО:** Title і H1 використовують **множину**, бо це категорія магазину з багатьма товарами.

```
title_phrase = category_title ?? primary_keyword
H1 = phrase_to_plural(title_phrase)   # множина першого слова
Title = H1 + " — купити..."           # той самий H1
```

**Приклад:**
```
_clean.json: primary_keyword = "очищувач слідів комах"

H1: "Очищувачі слідів комах"      ✅ (множина)
Title: "Очищувачі слідів комах — купити, ціни | Ultimate"  ✅

НЕ ПРАВИЛЬНО:
H1: "Очищувачі від комах"          ❌ (інша фраза!)
```

---

## 🚨 IRON RULE: title_phrase — ДОСЛІВНО (уточнено)

**`{title_phrase}` використовується в Title/H1/Description без зміни слів і порядку.**

**Дозволено ТІЛЬКИ:**
1. Капіталізація першої літери
2. Конвертація першого слова в множину (phrase_to_plural)

**НЕ ДОЗВОЛЕНО:**
- Скорочувати фразу ("слідів комах" → "від комах")
- Міняти порядок слів
- Додавати слова
- Змінювати відмінки
- "Покращувати" або "оптимізувати"
- Використовувати синоніми

```
_clean.json: "category_title": "Губки та рукавички"

✅ Title: Губки та рукавички — купити, ціни | Ultimate
✅ H1: Губки та рукавички

❌ Title: Рукавички та губки — купити | Ultimate    ← ЗМІНИВ ПОРЯДОК!
❌ H1: Губки й рукавиці                             ← ЗМІНИВ СЛОВА!
```

---

## Title (30-60 chars, унікальна частина)

**Як рахувати довжину (як у `validate_meta.py`):**
- якщо в Title є `|` → довжина рахується тільки для частини зліва від `|`
- якщо `|` немає → довжина рахується по всьому рядку

### Адаптивна формула:

```
ЯКЩО title_phrase ≤ 20 chars:
  {title_phrase} — купити в інтернет-магазині Ultimate

ІНАКШЕ:
  {title_phrase} — купити, ціни | Ultimate
```

**Приклади:**

| title_phrase | Довжина | Title |
|--------------|---------|-------|
| Силанти | 7 | Силанти — купити в інтернет-магазині Ultimate |
| Губки та рукавички | 18 | Губки та рукавички — купити в інтернет-магазині Ultimate |
| Щітки та пензлі для детейлінгу | 30 | Щітки та пензлі для детейлінгу — купити, ціни \| Ultimate |

**Правила:**
- **title_phrase В НАЧАЛО** (Front-loading!)
- Commercial modifiers **ПІСЛЯ** title_phrase
- Бренд **В КІНЕЦЬ** `| Ultimate`
- **БЕЗ двокрапки** (Google замінює на дефіс)
- **Мінімум 30 chars** в унікальній частині — інакше WARNING

---

## Description (100-160 chars)

### Формула (Producer pattern — є товари Ultimate):

```
{title_phrase} від виробника Ultimate. {Призначення/типи} — {деталі}. Опт і роздріб.
```

### Формула (Shop pattern — НЕМАє товарів Ultimate):

```
{title_phrase} в інтернет-магазині Ultimate. {Призначення/типи} — {деталі}.
```

### Приклади:

```
✅ Губки та рукавички в інтернет-магазині Ultimate. Для миття та полірування авто — поролон, мікрофібра, овчина.

✅ Автохімія та автокосметика від виробника Ultimate. Засоби для догляду за авто — шампуні, воски, полірувальні пасти. Опт і роздріб.

✅ Щітки та пензлі для детейлінгу в інтернет-магазині Ultimate. Для салону, дисків, кузова — м'які та жорсткі, набори та поштучно.
```

### 🚨 ОБОВ'ЯЗКОВІ ЕЛЕМЕНТИ:

**Producer pattern:**
1. **title_phrase** — на початку Description
2. **"від виробника Ultimate"** — одразу після
3. **"Опт і роздріб"** — в кінці

**Shop pattern:**
1. **title_phrase** — на початку Description
2. **"в інтернет-магазині Ultimate"** — одразу після
3. ❌ НЕМАє "Опт і роздріб"
4. ❌ НЕМАє назв брендів

### ❌ ЗАБОРОНЕНО в Description:

| Заборонено | Чому | Правильно |
|------------|------|-----------|
| Назви товарів (Bitumen Buster) | Користувач не знає SKU | Типи: "сольвентні", "лужні" |
| Назви брендів (Meguiar's, Gtechniq) | Динамічні дані | Тільки "Ultimate" як магазин |
| Marketing fluff (швидко, якісно) | Валідатор відхилить | Факти: "видаляє смолу" |

---

## H1 (= title_phrase → PLURAL)

**🚨 КРИТИЧНО: H1 має бути у МНОЖИНІ, бо категорія містить багато товарів.**

**Формула:** `{title_phrase}` → конвертувати в множину (якщо потрібно)

### Таблиця конвертації (UK)

| Однина | Множина |
|--------|---------|
| Очищувач | **Очищувачі** |
| Поліроль | **Поліролі** |
| Силант | **Силанти** |
| Губка | **Губки** |
| Відро | **Відра** |
| Набір | **Набори** |
| Віск | **Воски** |
| Шампунь | **Шампуні** |
| Щітка | **Щітки** |
| Машинка | **Машинки** |

### Алгоритм

1. Взяти `{title_phrase}` (category_title або primary_keyword)
2. Якщо однина — конвертувати **перше слово** в множину
3. Якщо category_title вже у множині (Губки та рукавички) — залишити як є

```
category_title: "Губки та рукавички" (вже множина)
H1: "Губки та рукавички" ✅

primary_keyword: "силант для авто" (однина)
H1: "Силанти для авто" (множина) ✅
```

### Виключення (вже множина або збірне)

НЕ конвертувати:
- Автохімія (збірне)
- Аксесуари (вже множина)
- Обладнання (збірне)
- Захисні покриття (вже множина)
- Полірування (процес)

**Інші правила:**
- **БЕЗ "Купити"**
- НЕ додавати слова яких немає в title_phrase

---

## JSON Output Format

```json
{
  "slug": "{slug}",
  "language": "uk",
  "meta": {
    "title": "{title_phrase} — купити, ціни | Ultimate",
    "description": "{title_phrase} від виробника Ultimate. {Типи} — {деталі}. Опт і роздріб."
  },
  "h1": "{title_phrase}",
  "keywords_in_content": {
    "primary": ["keyword1", "keyword2"],
    "secondary": ["keyword3", "keyword4"],
    "supporting": ["keyword5", "keyword6"]
  },
  "updated_at": "2026-02-03"
}
```

---

## Workflow

1. **Прочитати** `uk/categories/{slug}/data/{slug}_clean.json`
   - Перевірити наявність `category_title`
   - Якщо є → `title_phrase = category_title`
   - Якщо немає → `title_phrase = primary_keyword` (MAX volume)

2. **Визначити тип** (Producer vs Shop)

3. **Застосувати формули:**
   - Title: адаптивна формула з `{title_phrase}`
   - H1: `{title_phrase}` (множина, без "купити")
   - Description: Producer/Shop формула з `{title_phrase}`

4. **Перевірити:**
   - ✅ Title містить title_phrase ДОСЛІВНО
   - ✅ Title 30-60 chars (унікальна частина)
   - ✅ H1 = title_phrase ДОСЛІВНО
   - ✅ Description 100-160 chars
   - ✅ Description містить title_phrase і коректний патерн

5. **Зберегти** в `uk/categories/{slug}/meta/{slug}_meta.json`

6. **Валідація:** `python3 scripts/validate_meta.py {path} --keywords {clean_path}` → PASS

---

## Validation Checklist

**Нагадування:** `{title_phrase} = category_title ?? primary_keyword`

### Title:
- [ ] **title_phrase ДОСЛІВНО** ← IRON RULE!
- [ ] **30-60 chars** (унікальна частина)
- [ ] **Містить "купити"** ПІСЛЯ title_phrase
- [ ] Без двокрапки

### Description (Producer):
- [ ] **100-160 chars**
- [ ] **Починається з title_phrase**
- [ ] **"від виробника Ultimate"**
- [ ] **"Опт і роздріб"**
- [ ] НЕМАє назв товарів, брендів, fluff

### Description (Shop):
- [ ] **100-160 chars**
- [ ] **Починається з title_phrase**
- [ ] **"в інтернет-магазині Ultimate"**
- [ ] НЕМАє "Опт і роздріб"
- [ ] НЕМАє назв брендів

### H1:
- [ ] **= title_phrase** ← IRON RULE!
- [ ] **БЕЗ "Купити"**
- [ ] Множина (якщо потрібно)

---

## 🚩 Red Flags — СТОП і виправ

| Думка | Реальність |
|-------|------------|
| "Змінити порядок слів" | title_phrase = дані. НЕ змінюй! |
| "Додам для авто для ясності" | Якщо в title_phrase немає — НЕ додавай! |
| "Це ж синонім" | Синонім ≠ точний збіг. |
| "Я оптимізую" | Оптимізація = використовувати title_phrase дослівно. |

---

## Output

```
uk/categories/{slug}/meta/{slug}_meta.json (validated)

Status: ready for /uk-content-generator
```

---

**Version:** 17.2 — February 2026

**Changelog v17.2:**
- 🔧 **Чітка формула**: Title = H1 = phrase_to_plural(title_phrase)
- 📋 **IRON RULE уточнено**: дозволено тільки капіталізація + множина
- ❌ **Заборонено**: скорочувати або змінювати фразу

**Changelog v17.1:**
- 🔧 **Консистентність**: всі формули використовують `{title_phrase}` замість `{primary_keyword}`
- 📋 **Validation Checklist**: оновлено для title_phrase
- 🧹 **Спрощення**: видалено дублювання, скорочено документ

**Changelog v17.0:**
- 🆕 **category_title**: нове опціональне поле для складених категорій та двох ВЧ-ключів
- 📋 **Пріоритет**: `category_title` > `primary_keyword` в Title/H1/Description
- 🔧 **title_phrase**: `category_title ?? primary_keyword`
