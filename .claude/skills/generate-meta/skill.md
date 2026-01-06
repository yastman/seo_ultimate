---
name: generate-meta
description: Generates SEO meta tags (title, description, h1) for Ultimate.net.ua categories in Russian and Ukrainian. Extracts real product data from products_with_descriptions.md. Use when you see /generate-meta, генерируй мета, создай мета теги, оновити мета, обнови мета.
---

# Meta Tag Generator for Ultimate.net.ua

---

## December 2025 SEO Rules

| Параметр | Значение | Источник |
|----------|----------|----------|
| Title | **50-60 chars** | Zyppy Q1 2025 |
| Title rewrites | 76% переписывается | McAlpin Q1 2025 |
| Description | **120-160 chars** | Best practice |
| H1 | **БЕЗ "Купить"** | John Mueller 2025 |
| Keyword density | НЕ фактор | John Mueller 2025 |
| Commercial modifiers | **Обязательно в Title** | Ahrefs, BigCommerce |

---

## Title (50-60 chars)

**Формула RU:** `{Primary} — купить, цены | Ultimate`
**Формула UK:** `{Primary} — купити, ціни | Ultimate`

**Правила:**

- Primary keyword **В НАЧАЛО**
- Commercial modifiers ("купить/купити", "цены/ціни") **ОБЯЗАТЕЛЬНО**
- Бренд **В КОНЕЦ** `| Ultimate`
- **БЕЗ двоеточий** (Google заменяет на дефис в 41%)
- Скобки только для **синонимов с разными корнями**

**Примеры:**

```
✅ Чорнитель шин — купити, ціни | Ultimate          (42 chars)
✅ Активна піна для миття авто — купити | Ultimate  (48 chars)
❌ Чернители резины: купить в Киеве                 (нет бренда, двоеточие)
❌ Чорнитель шин (Матовий ефект) | Ultimate         (нет коммерции)
```

---

## Description (120-160 chars)

**Формула RU:** `{Категория} от производителя Ultimate. {Типы}. {Назначение}. {Volumes}. Опт и розница.`
**Формула UK:** `{Категорія} від виробника Ultimate. {Типи}. {Призначення}. {Volumes}. Опт і роздріб.`

**Правила:**

- НЕ дублировать Title
- "Производитель/Виробник Ultimate" — USP
- Типы из товаров (факты, не маркетинг)
- **БЕЗ emoji**

**Что извлекать из товаров:**

| Поле | Откуда | Пример |
|------|--------|--------|
| Типы | Названия товаров | готові, концентрати |
| Объёмы | Названия товаров | 0.5, 1, 5л |
| Назначение | Описания | "видаляє X" |

---

## H1 (чистый, без коммерции)

**Формула:** `{Primary keyword} для авто`

**Правила:**

- **БЕЗ "Купить/Купити"**
- H1 ≠ Title
- H1 — для людей, Title — для поиска

```
✅ H1: Чорнитель шин
✅ H1: Активна піна для безконтактного миття
❌ H1: Купити чорнитель шин
❌ H1: Чорнитель шин — купити | Ultimate
```

---

## JSON Output Format

```json
{
  "slug": "{slug}",
  "language": "ru",
  "meta": {
    "title": "{Title 50-60 chars}",
    "description": "{Description 120-160 chars}"
  },
  "h1": "{H1 без купить}",
  "keywords_in_content": {
    "primary": ["keyword1", "keyword2"],
    "secondary": ["keyword3", "keyword4"],
    "supporting": ["keyword5", "keyword6"]
  },
  "types": ["тип1", "тип2"],
  "forms": ["концентрат", "готовый"],
  "volumes": ["0.5л", "1л", "5л"],
  "status": "generated"
}
```

---

## Workflow

1. Прочитать `categories/{slug}/data/{slug}_clean.json` — primary keyword
2. Найти товары в `products_with_descriptions.md` — типы, объёмы
3. Применить формулы Title, Description, H1
4. Сохранить в `categories/{slug}/meta/{slug}_meta.json`
5. Валидация: `python3 scripts/validate_meta.py {path}`

---

## Validation Checklist

- [ ] Title: 50-60 chars
- [ ] Title: Primary keyword в начале
- [ ] Title: Содержит "купить/купити"
- [ ] Title: Без двоеточия
- [ ] Description: 120-160 chars
- [ ] Description: Без emoji
- [ ] H1: БЕЗ "Купить/Купити"
- [ ] H1 ≠ Title

---

## Quick Translation RU → UK

| RU | UK |
|----|-----|
| Купить | Купити |
| в Украине | в Україні |
| производителя | виробника |
| опт и розница | опт і роздріб |
| щелочная | лужна |
| кислотная | кислотна |
| нейтральная | нейтральна |

---

## Output

```
categories/{slug}/meta/{slug}_meta.json (validated)

Status: ready for /seo-research
```

---

**Version:** 9.0 — December 2025
