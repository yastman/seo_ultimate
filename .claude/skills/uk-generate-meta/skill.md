---
name: uk-generate-meta
description: Генерація українських мета-тегів (Title, Description, H1) для категорій Ultimate.net.ua. Use when /uk-generate-meta, генеруй UK мета, створи мета-теги українською, оновити українські мета, uk meta tags.
---

# UK Meta Tag Generator for Ultimate.net.ua

---

## January 2026 SEO Rules (UK)

| Параметр | Значення |
|----------|----------|
| Title | **50-60 chars**, "Купити" ОБОВ'ЯЗКОВО на початку |
| Description | **100-160 chars** |
| H1 | **= {primary_keyword} БЕЗ "Купити"** |

---

## IRON RULE: primary_keyword — ДОСЛІВНО

`{primary_keyword}` з `uk/categories/{slug}/data/{slug}_clean.json` використовується в Title/H1/Description без зміни слів і порядку.

Допускається лише капіталізація першої літери.

---

## Title (50-60 chars)

### Адаптивна формула:

```
ЯКЩО primary_keyword ≤ 20 chars:
  Купити {primary_keyword} в Україні | Ultimate

ІНАКШЕ:
  {primary_keyword} — купити, ціни | Ultimate
```

**Приклади:**

| primary_keyword | Довжина | Title |
|-----------------|---------|-------|
| силант | 6 | Купити силант в Україні \| Ultimate |
| віск для авто | 13 | Купити віск для авто в Україні \| Ultimate |
| догляд за салоном | 17 | Купити догляд за салоном в Україні \| Ultimate |
| набори для детейлінгу | 21 | Набори для детейлінгу — купити, ціни \| Ultimate |
| акумуляторна полірувальна машина | 33 | Акумуляторна полірувальна машина — купити, ціни \| Ultimate |

**Правила:**
- **"Купити" ОБОВ'ЯЗКОВО** — або на початку, або після keyword
- Бренд **В КІНЕЦЬ** `| Ultimate`
- **БЕЗ двокрапки** (Google замінює на дефіс)

---

## Description (100-160 chars)

### Producer pattern (є товари Ultimate):

```
{primary_keyword} від виробника Ultimate. {Типи/призначення} — {деталі}. Опт і роздріб.
```

### Shop pattern (НЕМАє товарів Ultimate):

```
{primary_keyword} в інтернет-магазині Ultimate. {Типи/призначення} — {деталі}.
```

### Приклади Producer pattern:

```
✅ Силант від виробника Ultimate. Полімерний захист кузова — гідрофобний ефект, захист 3–6 місяців. Опт і роздріб.

✅ Активна піна від виробника Ultimate. Безконтактна мийка — лужні та нейтральні, концентрати й готові. Опт і роздріб.
```

### Приклади Shop pattern:

```
✅ Полірувальна машинка в інтернет-магазині Ultimate. Роторні, ексцентрикові, акумуляторні — діаметр 75–180мм.

✅ Глина для авто в інтернет-магазині Ultimate. Глибоке очищення кузова — синя, жовта, автоскраби.
```

### Shop-категорії (НЕМАє товарів Ultimate):

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

## H1 (= primary_keyword)

**Формула:** `{primary_keyword}`

**Правила:**
- **= primary_keyword ДОСЛІВНО**
- **БЕЗ "Купити"**
- НЕ додавати "для авто" якщо його немає в primary_keyword

```
✅ H1: Силант                    (primary_keyword = "силант")
✅ H1: Щітки для детейлінгу      (primary_keyword = "щітки для детейлінгу")

❌ H1: Купити силант             (додав "Купити")
❌ H1: Силант для авто           (додав "для авто")
```

---

## JSON Output Format

```json
{
  "slug": "{slug}",
  "language": "uk",
  "meta": {
    "title": "Купити {primary_keyword} в Україні | Ultimate",
    "description": "{primary_keyword} від виробника Ultimate. {Типи} — {деталі}. Опт і роздріб."
  },
  "h1": "{primary_keyword}",
  "keywords_in_content": {
    "primary": ["keyword1", "keyword2"],
    "secondary": ["keyword3", "keyword4"],
    "supporting": ["keyword5", "keyword6"]
  },
  "types": ["тип1", "тип2"],
  "forms": ["концентрат", "готовий"],
  "volumes": ["0.5л", "1л", "5л"],
  "updated_at": "2026-01-22"
}
```

---

## Workflow

1. **Прочитати** `uk/categories/{slug}/data/{slug}_clean.json`
   - Визначити `{primary_keyword}` (keywords[0].keyword або keywords.primary[0].keyword)
   - Перевірити довжину для вибору формули Title

2. **Отримати types/volumes** з `categories/{slug}/meta/{slug}_meta.json` (RU версія)
   - Типи, форми, об'єми вже зібрані в RU мета

3. **Застосувати формули:**
   - Title: адаптивна формула (див. вище)
   - H1: `{primary_keyword}` (без "купити")
   - Description: Producer/Shop формула

4. **Перевірити:**
   - ✅ Title містить "Купити"
   - ✅ Title 50-60 chars
   - ✅ H1 = primary_keyword ДОСЛІВНО
   - ✅ Description 100-160 chars

5. **Зберегти** в `uk/categories/{slug}/meta/{slug}_meta.json`

---

## Validation Checklist

### Title:
- [ ] **Містить "Купити"**
- [ ] **50-60 chars**
- [ ] primary_keyword ДОСЛІВНО
- [ ] Без двокрапки

### Description (Producer):
- [ ] **100-160 chars**
- [ ] **Містить "від виробника Ultimate"**
- [ ] **Містить "Опт і роздріб"**

### Description (Shop):
- [ ] **100-160 chars**
- [ ] **Містить "в інтернет-магазині Ultimate"**
- [ ] **НЕМАє "Опт і роздріб"**

### H1:
- [ ] **= primary_keyword ДОСЛІВНО**
- [ ] **БЕЗ "Купити"**

---

## Output

```
uk/categories/{slug}/meta/{slug}_meta.json (validated)

Status: ready for /uk-content-init
```

---

**Version:** 1.0 — January 2026
