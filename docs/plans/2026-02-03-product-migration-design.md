# Product Migration Design

## Problem

После переезда на новую структуру категорий товары распределились криво:

1. **Категория 477** (без названия, "Щетки и кисти") — 68 товаров
   - Должны распределиться между 494 (Щётки для мойки) и 495 (Кисти для детейлинга)

2. **Категория 445** (Аксессуары — родительская) — товары в родительской вместо листовых
   - Должны уйти в 446/447/448/453/485

3. **Товары в нескольких категориях** — допустимо (max 2 для удобства навигации)

4. **Товары без категорий** (NULL) — несколько штук, нужно назначить

## Data Sources

- `data/generated/all_products_dump.tsv` — 605 товаров (product_id, model, manufacturer_id, name, current_categories)
- `data/generated/all_categories_dump.tsv` — 63 категории (category_id, parent_id, meta_h1, menu_name)

## Target Categories (листовые)

| ID | Slug | Название | Что сюда |
|----|------|----------|----------|
| 494 | shchetka-dlya-moyki-avto | Щётки для мойки авто | щётки для дисков, шин, кузова, двигуна, арок |
| 495 | kisti-dlya-deteylinga | Кисти для детейлинга | пензлі, м'які щітки для салону, вентиляції |
| 453 | gubki-i-varezhki | Губки и варежки | губки для мийки, рукавиці, варежки |
| 485 | aksessuary-dlya-naneseniya | Аппликаторы для нанесения | аплікатори для керамики, воска |
| 446 | mikrofibra-i-tryapki | Микрофибра | серветки, рушники, мікрофібра |
| 447 | raspyliteli-i-penniki | Распылители и пенники | тригери, пінники, пляшки, дозатори |
| 448 | vedra-i-emkosti | Вёдра и ёмкости | відра, сепаратори, візки |
| 463 | apparaty-tornador | Торнадор | торнадори, турбосушки, palm gun |
| 466 | nabory | Наборы | набори (можуть бути в 2х категоріях) |
| 454 | malyarniy-skotch | Малярный скотч | скотч, нітрилові рукавиці |
| 423 | glina-i-avtoskraby | Глина | глина, автоскраби |

## Migration Rules

### Щётки vs Кисти (из 477)

**→ 494 (Щётки для мойки):**
- "щітка для дисків/коліс/шин"
- "щітка для двигуна/арок"
- "щітка для миття"
- "жорстка щітка"
- "Vikan", "Tampico"
- "мідна щітка"
- "ПВХ щітка"

**→ 495 (Кисти для детейлинга):**
- "пензель", "пензлі"
- "детейлінг-пензель"
- "щітка для салону/інтер'єру"
- "щітка для вентиляції"
- "м'яка щітка", "ультрам'яка"
- "щітка для шкіри/текстилю/пластику"
- "Vent Duster"

### Губки vs Аппликаторы

**→ 453 (Губки и варежки):**
- "губка для миття/мойки"
- "рукавиця для миття"
- "варежка"
- "аплікатор для шин/чорніння"
- "поролоновий аплікатор"

**→ 485 (Аппликаторы для нанесения):**
- "аплікатор для керамики/покриття"
- "аплікатор для нанесення"

### Наборы (466)

Набори можуть залишатися в 2х категоріях:
- 466 (Наборы) + тематична категорія
- Наприклад: "Набір для дисків" → 466 + 419

## Worker Split

| Worker | Категории для аналізу | Товарів |
|--------|----------------------|---------|
| W1 | 477 (щітки/кисті) → 494/495 | ~68 |
| W2 | 445 (аксесуари) → листові | ~20 |
| W3 | NULL + перевірка інших | ~15 |

## Output Format

Кожен воркер генерує SQL:

```sql
-- W1: Щітки/Кисті migration
-- Product: {name}
DELETE FROM oc_product_to_category WHERE product_id = {id};
INSERT INTO oc_product_to_category (product_id, category_id) VALUES ({id}, {new_cat});
-- якщо 2 категорії:
INSERT INTO oc_product_to_category (product_id, category_id) VALUES ({id}, {second_cat});
```

## Validation

Після міграції:
1. Категорія 477 має бути порожня
2. Категорія 445 має містити тільки підкатегорії (не товари)
3. Всі товари мають хоча б 1 категорію

```sql
-- Перевірка: товари в 477
SELECT COUNT(*) FROM oc_product_to_category WHERE category_id = 477;
-- Expected: 0

-- Перевірка: товари в 445
SELECT COUNT(*) FROM oc_product_to_category WHERE category_id = 445;
-- Expected: 0 (або мінімум)

-- Перевірка: товари без категорій
SELECT p.product_id, pd.name
FROM oc_product p
LEFT JOIN oc_product_to_category p2c ON p.product_id = p2c.product_id
JOIN oc_product_description pd ON p.product_id = pd.product_id AND pd.language_id = 3
WHERE p2c.product_id IS NULL AND p.status = 1;
-- Expected: 0
```

## Execution

1. Backup: `mysqldump oc_product_to_category > backup.sql`
2. Workers генерують SQL в `data/generated/migration_W{N}.sql`
3. Review SQL
4. Execute: `mysql < migration_W{N}.sql`
5. Clear cache
6. Validate

---

**Version:** 1.0
**Date:** 2026-02-03
