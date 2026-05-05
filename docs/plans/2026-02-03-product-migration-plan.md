# Product Migration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Перенести ~100 товаров из проблемных категорий (477, 445, NULL) в правильные листовые категории.

**Architecture:**
1. Фаза 1: Воркеры изучают товары и составляют маппинг (TSV)
2. Фаза 2: Оркестратор ревьюит маппинг
3. Фаза 3: Генерация SQL из маппинга и выполнение

**Tech Stack:** MySQL, SSH, tmux, TSV

---

## Data Files

**Input:**
- `data/generated/all_products_dump.tsv` — 605 товаров (pid, model, mfr, name, categories)
- `data/generated/all_categories_dump.tsv` — 63 категории

**Output (маппинг):**
- `data/generated/mapping_W1.tsv` — маппинг из 477
- `data/generated/mapping_W2.tsv` — маппинг из 445
- `data/generated/mapping_W3.tsv` — маппинг orphans

## Target Categories Reference

| ID | Название | Ключевые слова в названии товара |
|----|----------|----------------------------------|
| 494 | Щётки для мойки | щітка + диск/колес/шин/двигун/арок/миття, жорстка, Vikan, Tampico, мідна, ПВХ |
| 495 | Кисти для детейлинга | пензель, детейлінг-пензель, щітка + салон/вентиляц/м'яка/шкіра/текстиль |
| 453 | Губки и варежки | губка для миття, рукавиця, варежка, аплікатор для шин |
| 485 | Аппликаторы | аплікатор для керамики/покриття/нанесення |
| 446 | Микрофибра | мікрофібра, серветка, рушник |
| 447 | Распылители | тригер, розпилювач, пінник, пляшка, помпа, дозатор |
| 448 | Вёдра | відро, сепаратор, візок для відра |
| 463 | Торнадор | торнадор, турбосушка, palm gun |
| 466 | Наборы | набір (может быть в 2х категориях) |
| 454 | Малярный скотч | скотч, нітрилові рукавиці |
| 423 | Глина | глина, автоскраб |

---

# ФАЗА 1: Изучение и маппинг

## Task 1 (W1): Изучить товары из категории 477

**Воркер:** W1-brushes
**Лог:** `logs/W1-migration.log`

**Step 1: Выгрузить товары из 477**

```bash
grep -E '\t477($|,)' data/generated/all_products_dump.tsv > /tmp/products_477.tsv
wc -l /tmp/products_477.tsv
```

**Step 2: Изучить каждый товар**

Для каждого товара:
1. Прочитать название
2. Определить тип: щётка для мойки vs кисть для детейлинга vs губка vs набор
3. Записать решение

**Step 3: Составить маппинг**

Формат `data/generated/mapping_W1.tsv`:
```
product_id	name	old_categories	new_categories	reason
3518	Щітка для Глибокого Миття Дисків	477	494	щітка для дисків
3534	Щітка для Чищення Шкіри	477	495	щітка для шкіри = детейлінг
3571	Рукавиця з Мікрофібри	477	453	рукавиця
3559	Набір Детейлінг-Пензлів	466,477	466,495	набір + пензлі
```

**Step 4: Записать лог**

```
[START] timestamp W1 - изучение категории 477
[ANALYZE] timestamp 3518: "Щітка для Дисків" → 494 (щітка для дисків)
[ANALYZE] timestamp 3534: "Щітка для Шкіри" → 495 (детейлінг)
...
[COMPLETE] timestamp W1 finished - X товаров в mapping_W1.tsv
```

---

## Task 2 (W2): Изучить товары из категории 445

**Воркер:** W2-accessories
**Лог:** `logs/W2-migration.log`

**Step 1: Выгрузить товары из 445**

```bash
grep -E '\t445($|,)' data/generated/all_products_dump.tsv > /tmp/products_445.tsv
wc -l /tmp/products_445.tsv
```

**Step 2: Изучить каждый товар**

Определить листовую категорию:
- мікрофібра/серветка/рушник → **446**
- тригер/розпилювач/пляшка → **447**
- відро/сепаратор → **448**
- губка/рукавиця → **453**
- нітрилові рукавиці → **454**
- набір → **466**
- щітка → **494** или **495**

**Step 3: Составить маппинг**

Формат `data/generated/mapping_W2.tsv`:
```
product_id	name	old_categories	new_categories	reason
3846	Нітрилові Рукавиці PROGRIP	445	454	нітрилові рукавиці = витратники
3560	Набір Щіток на Дриль	445,477	466	набір
```

**Step 4: Записать лог**

---

## Task 3 (W3): Изучить orphans и родительские

**Воркер:** W3-orphans
**Лог:** `logs/W3-migration.log`

**Step 1: Найти товары без категорий**

```bash
grep 'NULL$' data/generated/all_products_dump.tsv > /tmp/products_null.tsv
```

**Step 2: Найти товары в родительских категориях**

```bash
grep -E '\t(435|457|462|468|425)($|,)' data/generated/all_products_dump.tsv >> /tmp/products_parent.tsv
```

Родительские (не должны содержать товары):
- 435 (Защитные покрытия) → 436/437/438/439
- 457 (Полировка) → 458/459/461
- 462 (Оборудование) → 463
- 468 (Мойка) → 469/470/471/472
- 425 (Интерьер) → 427/428/429/431/434

**Step 3: Изучить и составить маппинг**

Формат `data/generated/mapping_W3.tsv`:
```
product_id	name	old_categories	new_categories	reason
4103	Віск для сушки Apricot	NULL	436	віск для сушки = квік-детейлер
3993	Щітка для хімчистки	435	495	щітка для салону
```

---

# ФАЗА 2: Review маппинга

## Task 4 (Orchestrator): Проверить маппинг

**Step 1: Проверить что воркеры завершились**

```bash
grep -l '\[COMPLETE\]' logs/W*-migration.log | wc -l
# Expected: 3
```

**Step 2: Посмотреть маппинги**

```bash
cat data/generated/mapping_W1.tsv
cat data/generated/mapping_W2.tsv
cat data/generated/mapping_W3.tsv
```

**Step 3: Проверить**

- Все категории валидны (существуют)
- Нет противоречий
- Логика маппинга понятна

**Step 4: Объединить в финальный маппинг**

```bash
cat data/generated/mapping_W1.tsv data/generated/mapping_W2.tsv data/generated/mapping_W3.tsv > data/generated/mapping_final.tsv
```

---

# ФАЗА 3: Генерация SQL и выполнение

## Task 5: Генерация SQL из маппинга

**Step 1: Создать SQL из маппинга**

Для каждой строки в `mapping_final.tsv`:
```sql
-- {product_id}: {name}
-- Reason: {reason}
DELETE FROM oc_product_to_category WHERE product_id = {product_id};
INSERT INTO oc_product_to_category (product_id, category_id) VALUES ({product_id}, {cat1});
-- если 2 категории:
INSERT INTO oc_product_to_category (product_id, category_id) VALUES ({product_id}, {cat2});
```

**Step 2: Сохранить**

```bash
# Записать в data/generated/migration_final.sql
```

---

## Task 6: Backup и выполнение

**Step 1: Backup**

```bash
ssh ult "mysqldump yastman_test oc_product_to_category > /tmp/p2c_backup_$(date +%Y%m%d).sql"
```

**Step 2: Загрузить и выполнить**

```bash
scp data/generated/migration_final.sql ult:/tmp/
ssh ult "mysql yastman_test < /tmp/migration_final.sql"
```

**Step 3: Очистить кэш**

```bash
ssh ult "rm -rf /home/yastman/web/ultimate.net.ua/public_html/system/storage/cache/*"
```

---

## Task 7: Валидация

**Step 1: Проверить проблемные категории**

```bash
# 477 должна быть пустая
ssh ult "mysql yastman_test -N -e 'SELECT COUNT(*) FROM oc_product_to_category WHERE category_id = 477;'"
# Expected: 0

# 445 — пустая или минимум
ssh ult "mysql yastman_test -N -e 'SELECT COUNT(*) FROM oc_product_to_category WHERE category_id = 445;'"
# Expected: 0
```

**Step 2: Проверить orphans**

```bash
ssh ult "mysql yastman_test -N -e '
SELECT COUNT(*)
FROM oc_product p
LEFT JOIN oc_product_to_category p2c ON p.product_id = p2c.product_id
WHERE p2c.product_id IS NULL AND p.status = 1;
'"
# Expected: 0
```

**Step 3: Проверить распределение**

```bash
ssh ult "mysql yastman_test -N -e '
SELECT c.category_id, cd.meta_h1, COUNT(p2c.product_id)
FROM oc_category c
JOIN oc_category_description cd ON c.category_id = cd.category_id AND cd.language_id = 3
LEFT JOIN oc_product_to_category p2c ON c.category_id = p2c.category_id
WHERE c.category_id IN (494, 495, 453, 446, 447, 448)
GROUP BY c.category_id;
'"
```

**Step 4: Commit**

```bash
git add data/generated/mapping_*.tsv data/generated/migration_final.sql logs/W*-migration.log
git commit -m "fix(products): migrate products to correct leaf categories

Mapping:
- 477 → 494/495 (brushes/detailing)
- 445 → leaf categories
- Fixed orphans

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Spawn Commands (Фаза 1)

```bash
# Создать окна
tmux new-window -n "W1-brush"
tmux new-window -n "W2-access"
tmux new-window -n "W3-orphan"

# W1: Изучить 477
tmux send-keys -t "W1-brush" "claude --dangerously-skip-permissions 'W1: Изучить товары из категории 477 и составить маппинг.

ПЛАН: docs/plans/2026-02-03-product-migration-plan.md — Task 1

ДАННЫЕ: data/generated/all_products_dump.tsv
Формат: product_id<TAB>model<TAB>manufacturer_id<TAB>name<TAB>categories

КАТЕГОРИИ для маппинга:
- 494 = Щётки для мойки (диски, шини, двигун, жорстка, Vikan, Tampico)
- 495 = Кисти для детейлинга (пензель, м\\'яка, салон, вентиляція, шкіра)
- 453 = Губки (губка, рукавиця)
- 466 = Наборы (набір — залишити в 2х категоріях)

WORKFLOW:
1. Виведи товари з 477: grep -E \"\\t477(\$|,)\" data/generated/all_products_dump.tsv
2. Для кожного товару визнач категорію за назвою
3. Створи маппинг TSV: product_id<TAB>name<TAB>old<TAB>new<TAB>reason
4. Збережи в data/generated/mapping_W1.tsv

ЛОГ: /home/user/projects/llm-keywords-pipeline/logs/W1-migration.log
Формат: [START/ANALYZE/COMPLETE] timestamp message

НЕ делай git commit. НЕ генеруй SQL — тільки маппинг.'" Enter

# W2: Изучить 445
tmux send-keys -t "W2-access" "claude --dangerously-skip-permissions 'W2: Изучить товары из категории 445 и составить маппинг.

ПЛАН: docs/plans/2026-02-03-product-migration-plan.md — Task 2

ДАННЫЕ: data/generated/all_products_dump.tsv

КАТЕГОРИИ:
- 446 = Микрофибра (мікрофібра, серветка, рушник)
- 447 = Распылители (тригер, пінник, пляшка)
- 448 = Вёдра (відро, сепаратор)
- 453 = Губки (губка, рукавиця)
- 454 = Скотч (нітрилові рукавиці)
- 466 = Наборы
- 494/495 = Щітки/Кисті

WORKFLOW:
1. Виведи товари з 445: grep -E \"\\t445(\$|,)\" data/generated/all_products_dump.tsv
2. Визнач листову категорію за назвою
3. Створи маппинг TSV
4. Збережи в data/generated/mapping_W2.tsv

ЛОГ: /home/user/projects/llm-keywords-pipeline/logs/W2-migration.log

НЕ делай git commit. НЕ генеруй SQL — тільки маппинг.'" Enter

# W3: Orphans + родительские
tmux send-keys -t "W3-orphan" "claude --dangerously-skip-permissions 'W3: Изучить orphans и товары в родительских категориях.

ПЛАН: docs/plans/2026-02-03-product-migration-plan.md — Task 3

ДАННЫЕ: data/generated/all_products_dump.tsv

WORKFLOW:
1. Знайди товари без категорій: grep \"NULL\$\" data/generated/all_products_dump.tsv
2. Знайди товари в родительських (435,457,462,468,425): grep -E \"\\t(435|457|462|468|425)(\$|,)\"
3. Визнач правильні категорії за назвою
4. Створи маппинг TSV
5. Збережи в data/generated/mapping_W3.tsv

Родительські → листові:
- 435 (Покриття) → 436/437/438/439
- 457 (Полірування) → 458/459/461
- 462 (Обладнання) → 463
- 468 (Мийка) → 469/470/471/472
- 425 (Інтер\\'єр) → 427/428/429/431/434

ЛОГ: /home/user/projects/llm-keywords-pipeline/logs/W3-migration.log

НЕ делай git commit. НЕ генеруй SQL — тільки маппинг.'" Enter
```

---

## Checklist

### Фаза 1: Маппинг
- [ ] W1: mapping_W1.tsv создан
- [ ] W2: mapping_W2.tsv создан
- [ ] W3: mapping_W3.tsv создан
- [ ] Все [COMPLETE] в логах

### Фаза 2: Review
- [ ] Маппинги просмотрены
- [ ] Категории валидны
- [ ] mapping_final.tsv создан

### Фаза 3: Выполнение
- [ ] Backup создан
- [ ] SQL сгенерирован
- [ ] Миграция выполнена
- [ ] Кэш очищен

### Валидация
- [ ] 477 пустая
- [ ] 445 пустая
- [ ] Нет orphans
- [ ] Распределение корректное
- [ ] Git commit

---

**Version:** 2.0
**Date:** 2026-02-03
