# OpenCart Category Sync Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Синхронизировать структуру категорий OpenCart с нашим деревом (L1→L2→L3), обновить SEO URL, мета-теги и контент (RU + UK). Без glavnaya. Товары — потом.

**Architecture:** SSH через `ult` к серверу 193.169.188.9:41229, прямые SQL запросы в БД `yastman_test`. Сначала структура (parent_id), затем SEO URL, потом мета+контент. Новые категории создаются последними.

**Tech Stack:** Bash, MySQL, SSH (`ult` alias), Python (`scripts/upload_to_db.py` для md→html)

---

## Сводка изменений

### Текущее состояние сервера

| Level | Категорий |
|-------|-----------|
| L1 (parent=0) | 8 |
| L2 | 42 |
| L3 | 7 |
| **Всего** | 57 |

### Целевое состояние (наше дерево)

| Level | Категорий |
|-------|-----------|
| L1 | 7 (без glavnaya) |
| L2 | ~20 |
| L3 | ~25 |
| **Всего** | 52 (без glavnaya) |

### Ключевые различия

1. **Наборы (466)** — на сервере L1, у нас L2 под Аксессуары
2. **Воски** — у нас L2, на сервере нет (есть только Твердые воска 437)
3. **11 категорий нужно создать** (obezzhirivateli, mekhovye, akkumulyatornaya...)
4. **Slug'и** — на сервере украинская транслитерация

---

## Task 1: Создать маппинг slug → category_id

**Files:**
- Create: `data/opencart_mapping.json`

**Step 1: Выгрузить все категории с сервера**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e "
SELECT
    c.category_id,
    u.keyword as slug,
    cd.name,
    c.parent_id
FROM oc_category c
LEFT JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) AND u.language_id = 3
JOIN oc_category_description cd ON c.category_id = cd.category_id AND cd.language_id = 3
WHERE c.status = 1
ORDER BY c.category_id;
"' > /tmp/server_categories.tsv
```

**Step 2: Создать JSON маппинг**

```json
{
  "slug_to_id": {
    "aktivnaya-pena": 415,
    "shampuni-dlya-ruchnoy-moyki": 412,
    "avtoshampuni": 469,
    "moyka-i-eksterer": 468,
    "ochistiteli-stekol": 418,
    "sredstva-dlya-stekol": 470,
    "omyvatel": 424,
    "antidozhd": 473,
    "glina-i-avtoskraby": 423,
    "ochistiteli-kuzova": 471,
    "antimoshka": 474,
    "antibitum": 475,
    "ochistiteli-dvigatelya": 422,
    "cherniteli-shin": 421,
    "ochistiteli-diskov": 419,
    "ochistiteli-shin": 420,
    "sredstva-dlya-diskov-i-shin": 472,
    "ukhod-za-intererom": 425,
    "sredstva-dlya-khimchistki-salona": 427,
    "sredstva-dlya-kozhi": 428,
    "poliroli-dlya-plastika": 429,
    "neytralizatory-zapakha": 431,
    "pyatnovyvoditeli": 434,
    "zashchitnye-pokrytiya": 435,
    "voski": 437,
    "tverdyy-vosk": 437,
    "zhidkiy-vosk": 456,
    "keramika-i-zhidkoe-steklo": 439,
    "kvik-deteylery": 436,
    "silanty": 438,
    "aksessuary": 445,
    "mikrofibra-i-tryapki": 446,
    "raspyliteli-i-penniki": 447,
    "vedra-i-emkosti": 448,
    "gubki-i-varezhki": 453,
    "malyarniy-skotch": 454,
    "nabory": 466,
    "polirovka": 457,
    "polirovalnye-pasty": 458,
    "polirovalnye-krugi": 459,
    "polirovalnye-mashinki": 461,
    "oborudovanie": 462,
    "apparaty-tornador": 463
  },
  "needs_creation": [
    "obezzhirivateli",
    "polirol-dlya-stekla",
    "keramika-dlya-diskov",
    "ukhod-za-naruzhnym-plastikom",
    "akkumulyatornaya",
    "mekhovye",
    "kisti-dlya-deteylinga",
    "shchetka-dlya-moyki-avto",
    "ochistiteli-kozhi",
    "ukhod-za-kozhey",
    "opt-i-b2b",
    "aksessuary-dlya-naneseniya-sredstv"
  ],
  "excluded": ["glavnaya"]
}
```

**Step 3: Валидация**

Run:
```bash
python3 -c "import json; d=json.load(open('data/opencart_mapping.json')); print(f'Mapped: {len(d[\"slug_to_id\"])}'); print(f'To create: {len(d[\"needs_creation\"])}')"
```

Expected: `Mapped: 42`, `To create: 12`

---

## Task 2: Обновить структуру дерева (parent_id)

**Files:**
- Create: `deploy/sync/01_update_structure.sql`

**Step 1: Создать папку deploy/sync**

Run:
```bash
mkdir -p deploy/sync
```

**Step 2: Изменения parent_id**

На сервере `Наборы (466)` имеет parent_id=0 (L1), у нас это L2 под Аксессуары (445).

```sql
-- deploy/sync/01_update_structure.sql
-- Синхронизация структуры дерева

-- Наборы: L1 → L2 под Аксессуары
UPDATE oc_category SET parent_id = 445 WHERE category_id = 466;

-- Пересчитать category_path для Наборы
DELETE FROM oc_category_path WHERE category_id = 466;
INSERT INTO oc_category_path (category_id, path_id, level) VALUES
(466, 445, 0),
(466, 466, 1);
```

**Step 3: Применить SQL**

Run:
```bash
cat deploy/sync/01_update_structure.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

Expected: No errors

**Step 4: Верификация**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "SELECT category_id, parent_id FROM oc_category WHERE category_id = 466;"'
```

Expected: `466 | 445`

---

## Task 3: Обновить SEO URL (slug'и)

**Files:**
- Create: `deploy/sync/02_update_seo_urls.sql`

**Step 1: Генерировать SQL**

```sql
-- deploy/sync/02_update_seo_urls.sql
-- Обновление SEO URL на наши slug'и (RU + UK)

-- Активная пена (415)
UPDATE oc_seo_url SET keyword = 'aktivnaya-pena' WHERE query = 'category_id=415' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'aktivna-pina' WHERE query = 'category_id=415' AND language_id = 1;

-- Шампуни для ручной мойки (412)
UPDATE oc_seo_url SET keyword = 'shampuni-dlya-ruchnoy-moyki' WHERE query = 'category_id=412' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'shampuni-dlya-ruchnogo-myttya' WHERE query = 'category_id=412' AND language_id = 1;

-- Автошампуни (469)
UPDATE oc_seo_url SET keyword = 'avtoshampuni' WHERE query = 'category_id=469' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'avtoshampuny' WHERE query = 'category_id=469' AND language_id = 1;

-- Мойка и Экстерьер (468)
UPDATE oc_seo_url SET keyword = 'moyka-i-eksterer' WHERE query = 'category_id=468' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'myjka-i-eksterier' WHERE query = 'category_id=468' AND language_id = 1;

-- Очистители стекол (418)
UPDATE oc_seo_url SET keyword = 'ochistiteli-stekol' WHERE query = 'category_id=418' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'ochyshchuvachi-skla' WHERE query = 'category_id=418' AND language_id = 1;

-- Средства для стекол (470)
UPDATE oc_seo_url SET keyword = 'sredstva-dlya-stekol' WHERE query = 'category_id=470' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'zasoby-dlya-skla' WHERE query = 'category_id=470' AND language_id = 1;

-- Омыватель (424)
UPDATE oc_seo_url SET keyword = 'omyvatel' WHERE query = 'category_id=424' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'omyvach' WHERE query = 'category_id=424' AND language_id = 1;

-- Антидождь (473)
UPDATE oc_seo_url SET keyword = 'antidozhd' WHERE query = 'category_id=473' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'antydoshch' WHERE query = 'category_id=473' AND language_id = 1;

-- Глина и автоскрабы (423)
UPDATE oc_seo_url SET keyword = 'glina-i-avtoskraby' WHERE query = 'category_id=423' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'hlyna-ta-avtoskraby' WHERE query = 'category_id=423' AND language_id = 1;

-- Очистители кузова (471)
UPDATE oc_seo_url SET keyword = 'ochistiteli-kuzova' WHERE query = 'category_id=471' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'ochyshchuvachi-kuzova' WHERE query = 'category_id=471' AND language_id = 1;

-- Антимошка (474)
UPDATE oc_seo_url SET keyword = 'antimoshka' WHERE query = 'category_id=474' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'antymoshka' WHERE query = 'category_id=474' AND language_id = 1;

-- Антибитум (475)
UPDATE oc_seo_url SET keyword = 'antibitum' WHERE query = 'category_id=475' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'antybitum' WHERE query = 'category_id=475' AND language_id = 1;

-- Очистители двигателя (422)
UPDATE oc_seo_url SET keyword = 'ochistiteli-dvigatelya' WHERE query = 'category_id=422' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'ochyshchuvachi-dvyhuna' WHERE query = 'category_id=422' AND language_id = 1;

-- Чернители шин (421)
UPDATE oc_seo_url SET keyword = 'cherniteli-shin' WHERE query = 'category_id=421' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'chornyteli-shyn' WHERE query = 'category_id=421' AND language_id = 1;

-- Очистители дисков (419)
UPDATE oc_seo_url SET keyword = 'ochistiteli-diskov' WHERE query = 'category_id=419' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'ochyshchuvachi-dyskiv' WHERE query = 'category_id=419' AND language_id = 1;

-- Очистители шин (420)
UPDATE oc_seo_url SET keyword = 'ochistiteli-shin' WHERE query = 'category_id=420' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'ochyshchuvachi-shyn' WHERE query = 'category_id=420' AND language_id = 1;

-- Средства для дисков и шин (472)
UPDATE oc_seo_url SET keyword = 'sredstva-dlya-diskov-i-shin' WHERE query = 'category_id=472' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'zasoby-dlya-dyskiv-i-shyn' WHERE query = 'category_id=472' AND language_id = 1;

-- Уход за интерьером (425)
UPDATE oc_seo_url SET keyword = 'ukhod-za-intererom' WHERE query = 'category_id=425' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'dohlyad-za-interierom' WHERE query = 'category_id=425' AND language_id = 1;

-- Средства для химчистки салона (427)
UPDATE oc_seo_url SET keyword = 'sredstva-dlya-khimchistki-salona' WHERE query = 'category_id=427' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'zasoby-dlya-khimchystky-salonu' WHERE query = 'category_id=427' AND language_id = 1;

-- Средства для кожи (428)
UPDATE oc_seo_url SET keyword = 'sredstva-dlya-kozhi' WHERE query = 'category_id=428' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'zasoby-dlya-shkiry' WHERE query = 'category_id=428' AND language_id = 1;

-- Полироли для пластика (429)
UPDATE oc_seo_url SET keyword = 'poliroli-dlya-plastika' WHERE query = 'category_id=429' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'poliroli-dlya-plastyku' WHERE query = 'category_id=429' AND language_id = 1;

-- Нейтрализаторы запаха (431)
UPDATE oc_seo_url SET keyword = 'neytralizatory-zapakha' WHERE query = 'category_id=431' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'neytralizatory-zapakhu' WHERE query = 'category_id=431' AND language_id = 1;

-- Пятновыводители (434)
UPDATE oc_seo_url SET keyword = 'pyatnovyvoditeli' WHERE query = 'category_id=434' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'plyamovyvidnyky' WHERE query = 'category_id=434' AND language_id = 1;

-- Защитные покрытия (435)
UPDATE oc_seo_url SET keyword = 'zashchitnye-pokrytiya' WHERE query = 'category_id=435' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'zakhysni-pokryttya' WHERE query = 'category_id=435' AND language_id = 1;

-- Твердый воск / Воски (437)
UPDATE oc_seo_url SET keyword = 'tverdyy-vosk' WHERE query = 'category_id=437' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'tverdyy-visk' WHERE query = 'category_id=437' AND language_id = 1;

-- Жидкий воск (456)
UPDATE oc_seo_url SET keyword = 'zhidkiy-vosk' WHERE query = 'category_id=456' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'ridkyy-visk' WHERE query = 'category_id=456' AND language_id = 1;

-- Керамика и жидкое стекло (439)
UPDATE oc_seo_url SET keyword = 'keramika-i-zhidkoe-steklo' WHERE query = 'category_id=439' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'keramika-i-ridke-sklo' WHERE query = 'category_id=439' AND language_id = 1;

-- Квик-детейлеры (436)
UPDATE oc_seo_url SET keyword = 'kvik-deteylery' WHERE query = 'category_id=436' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'kvik-deteylery-uk' WHERE query = 'category_id=436' AND language_id = 1;

-- Силанты (438)
UPDATE oc_seo_url SET keyword = 'silanty' WHERE query = 'category_id=438' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'sylanty' WHERE query = 'category_id=438' AND language_id = 1;

-- Аксессуары (445)
UPDATE oc_seo_url SET keyword = 'aksessuary' WHERE query = 'category_id=445' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'aksesuary' WHERE query = 'category_id=445' AND language_id = 1;

-- Микрофибра и тряпки (446)
UPDATE oc_seo_url SET keyword = 'mikrofibra-i-tryapki' WHERE query = 'category_id=446' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'mikrofibra-i-ganchirky' WHERE query = 'category_id=446' AND language_id = 1;

-- Распылители и пенники (447)
UPDATE oc_seo_url SET keyword = 'raspyliteli-i-penniki' WHERE query = 'category_id=447' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'rozpylyuvachi-i-pinnyky' WHERE query = 'category_id=447' AND language_id = 1;

-- Ведра и емкости (448)
UPDATE oc_seo_url SET keyword = 'vedra-i-emkosti' WHERE query = 'category_id=448' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'vidra-i-yemnosti' WHERE query = 'category_id=448' AND language_id = 1;

-- Губки и варежки (453)
UPDATE oc_seo_url SET keyword = 'gubki-i-varezhki' WHERE query = 'category_id=453' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'hubky-i-rukavychky' WHERE query = 'category_id=453' AND language_id = 1;

-- Малярный скотч (454)
UPDATE oc_seo_url SET keyword = 'malyarniy-skotch' WHERE query = 'category_id=454' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'malyarnyy-skotch' WHERE query = 'category_id=454' AND language_id = 1;

-- Наборы (466)
UPDATE oc_seo_url SET keyword = 'nabory' WHERE query = 'category_id=466' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'nabory-uk' WHERE query = 'category_id=466' AND language_id = 1;

-- Полировка (457)
UPDATE oc_seo_url SET keyword = 'polirovka' WHERE query = 'category_id=457' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'poliruvannya' WHERE query = 'category_id=457' AND language_id = 1;

-- Полировальные пасты (458)
UPDATE oc_seo_url SET keyword = 'polirovalnye-pasty' WHERE query = 'category_id=458' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'poliruvalni-pasty' WHERE query = 'category_id=458' AND language_id = 1;

-- Полировальные круги (459)
UPDATE oc_seo_url SET keyword = 'polirovalnye-krugi' WHERE query = 'category_id=459' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'poliruvalni-kruhy' WHERE query = 'category_id=459' AND language_id = 1;

-- Полировальные машинки (461)
UPDATE oc_seo_url SET keyword = 'polirovalnye-mashinki' WHERE query = 'category_id=461' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'poliruvalni-mashynky' WHERE query = 'category_id=461' AND language_id = 1;

-- Оборудование (462)
UPDATE oc_seo_url SET keyword = 'oborudovanie' WHERE query = 'category_id=462' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'obladnannya' WHERE query = 'category_id=462' AND language_id = 1;

-- Аппараты Tornador (463)
UPDATE oc_seo_url SET keyword = 'apparaty-tornador' WHERE query = 'category_id=463' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'aparaty-tornador' WHERE query = 'category_id=463' AND language_id = 1;
```

**Step 2: Применить SQL**

Run:
```bash
cat deploy/sync/02_update_seo_urls.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

Expected: No errors

**Step 3: Верификация**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "SELECT keyword FROM oc_seo_url WHERE query = \"category_id=415\" AND language_id = 3;"'
```

Expected: `aktivnaya-pena`

---

## Task 4: Обновить мета-теги (RU)

**Files:**
- Create: `deploy/sync/03_update_meta_ru.sql`
- Read: `categories/*/meta/*_meta.json`

**Step 1: Скрипт генерации SQL**

Run:
```bash
python3 -c "
import json
import os
from pathlib import Path

mapping = json.load(open('data/opencart_mapping.json'))
sql_lines = ['-- deploy/sync/03_update_meta_ru.sql', '-- Мета-теги RU (language_id=3)', '']

for slug, cat_id in mapping['slug_to_id'].items():
    # Найти meta файл
    for root, dirs, files in os.walk('categories'):
        for f in files:
            if f == f'{slug}_meta.json':
                meta_path = os.path.join(root, f)
                with open(meta_path) as mf:
                    meta = json.load(mf)
                title = meta['meta']['title'].replace(\"'\", \"\\\\'\")
                desc = meta['meta']['description'].replace(\"'\", \"\\\\'\")
                h1 = meta.get('h1', '').replace(\"'\", \"\\\\'\")
                sql_lines.append(f\"-- {slug} ({cat_id})\")
                sql_lines.append(f\"UPDATE oc_category_description SET meta_title = '{title}', meta_description = '{desc}', meta_h1 = '{h1}' WHERE category_id = {cat_id} AND language_id = 3;\")
                sql_lines.append('')
                break

print('\\n'.join(sql_lines))
" > deploy/sync/03_update_meta_ru.sql
```

**Step 2: Проверить SQL**

Run:
```bash
head -30 deploy/sync/03_update_meta_ru.sql
```

Expected: SQL с UPDATE для мета-тегов

**Step 3: Применить SQL**

Run:
```bash
cat deploy/sync/03_update_meta_ru.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

---

## Task 5: Обновить мета-теги (UK)

**Files:**
- Create: `deploy/sync/04_update_meta_uk.sql`
- Read: `uk/categories/*/meta/*_meta.json`

**Step 1: Скрипт генерации SQL**

Run:
```bash
python3 -c "
import json
import os
from pathlib import Path

mapping = json.load(open('data/opencart_mapping.json'))
sql_lines = ['-- deploy/sync/04_update_meta_uk.sql', '-- Мета-теги UK (language_id=1)', '']

for slug, cat_id in mapping['slug_to_id'].items():
    # Найти UK meta файл
    meta_path = f'uk/categories/{slug}/meta/{slug}_meta.json'
    if os.path.exists(meta_path):
        with open(meta_path) as mf:
            meta = json.load(mf)
        title = meta['meta']['title'].replace(\"'\", \"\\\\'\")
        desc = meta['meta']['description'].replace(\"'\", \"\\\\'\")
        h1 = meta.get('h1', '').replace(\"'\", \"\\\\'\")
        sql_lines.append(f\"-- {slug} ({cat_id})\")
        sql_lines.append(f\"UPDATE oc_category_description SET meta_title = '{title}', meta_description = '{desc}', meta_h1 = '{h1}' WHERE category_id = {cat_id} AND language_id = 1;\")
        sql_lines.append('')

print('\\n'.join(sql_lines))
" > deploy/sync/04_update_meta_uk.sql
```

**Step 2: Применить SQL**

Run:
```bash
cat deploy/sync/04_update_meta_uk.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

---

## Task 6: Обновить контент (RU)

**Files:**
- Create: `deploy/sync/05_update_content_ru.sql`
- Read: `categories/*/content/*_ru.md`

**Step 1: Использовать upload_to_db.py логику**

Скрипт `scripts/upload_to_db.py` уже умеет:
- Конвертировать MD → HTML
- Убирать H1 (идёт в meta_h1)
- Формировать SQL

Run:
```bash
python3 scripts/upload_to_db.py --dry-run 2>&1 | head -50
```

**Step 2: Генерация SQL для контента**

```bash
python3 -c "
import json
import os
import re

def md_to_html(md):
    html = md
    html = re.sub(r'^# .+\n\n', '', html, count=1, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # Simplified - full version in upload_to_db.py
    return html.strip()

mapping = json.load(open('data/opencart_mapping.json'))
sql_lines = ['-- deploy/sync/05_update_content_ru.sql', '-- Контент RU (language_id=3)', '']

for slug, cat_id in mapping['slug_to_id'].items():
    # Найти content файл
    for root, dirs, files in os.walk('categories'):
        for f in files:
            if f == f'{slug}_ru.md':
                content_path = os.path.join(root, f)
                with open(content_path) as cf:
                    md = cf.read()
                html = md_to_html(md).replace(\"'\", \"\\\\'\")
                sql_lines.append(f\"-- {slug} ({cat_id})\")
                sql_lines.append(f\"UPDATE oc_category_description SET description = '{html}' WHERE category_id = {cat_id} AND language_id = 3;\")
                sql_lines.append('')
                break

print('\\n'.join(sql_lines[:100]))  # Preview
"
```

**Step 3: Полная генерация через upload_to_db.py**

Run:
```bash
# Модифицировать upload_to_db.py для генерации SQL файла вместо прямого подключения
# Или использовать --dry-run и парсить вывод
python3 scripts/upload_to_db.py --generate-sql > deploy/sync/05_update_content_ru.sql
```

**Step 4: Применить SQL**

Run:
```bash
cat deploy/sync/05_update_content_ru.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

---

## Task 7: Обновить контент (UK)

**Files:**
- Create: `deploy/sync/06_update_content_uk.sql`
- Read: `uk/categories/*/content/*_uk.md`

Аналогично Task 6, но для UK файлов и language_id=1.

---

## Task 8: Создать новые категории

**Files:**
- Create: `deploy/sync/07_create_categories.sql`

**Step 1: Список категорий для создания**

| Slug | Parent | Name RU | Name UK |
|------|--------|---------|---------|
| obezzhirivateli | 471 | Обезжириватели | Знежирювачі |
| polirol-dlya-stekla | 470 | Полироль для стекла | Поліроль для скла |
| keramika-dlya-diskov | 472 | Керамика для дисков | Кераміка для дисків |
| ukhod-za-naruzhnym-plastikom | 471 | Уход за наружным пластиком | Догляд за зовнішнім пластиком |
| akkumulyatornaya | 461 | Аккумуляторные машинки | Акумуляторні машинки |
| mekhovye | 459 | Меховые круги | Хутряні круги |
| kisti-dlya-deteylinga | 452 | Кисти для детейлинга | Пензлі для детейлінгу |
| shchetka-dlya-moyki-avto | 452 | Щетка для мойки авто | Щітка для миття авто |
| ochistiteli-kozhi | 428 | Очистители кожи | Очищувачі шкіри |
| ukhod-za-kozhey | 428 | Уход за кожей | Догляд за шкірою |
| opt-i-b2b | 0 | Опт и B2B | Опт та B2B |
| aksessuary-dlya-naneseniya-sredstv | 445 | Аксессуары для нанесения | Аксесуари для нанесення |

**Step 2: Генерация SQL**

```sql
-- deploy/sync/07_create_categories.sql
-- Создание новых категорий

-- obezzhirivateli (parent=471)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified)
VALUES (471, 0, 1, 0, 1, NOW(), NOW());
SET @id_obezzhirivateli = LAST_INSERT_ID();

INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1)
VALUES
(@id_obezzhirivateli, 3, 'Обезжириватели', '', '', '', '', ''),
(@id_obezzhirivateli, 1, 'Знежирювачі', '', '', '', '', '');

INSERT INTO oc_seo_url (store_id, language_id, query, keyword)
VALUES
(0, 3, CONCAT('category_id=', @id_obezzhirivateli), 'obezzhirivateli'),
(0, 1, CONCAT('category_id=', @id_obezzhirivateli), 'znezhyryuvachi');

INSERT INTO oc_category_path (category_id, path_id, level)
SELECT @id_obezzhirivateli, path_id, level FROM oc_category_path WHERE category_id = 471
UNION ALL SELECT @id_obezzhirivateli, @id_obezzhirivateli, 3;

-- Повторить для остальных 11 категорий...
```

**Step 3: Применить SQL**

Run:
```bash
cat deploy/sync/07_create_categories.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

**Step 4: Получить новые ID**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "SELECT category_id, name FROM oc_category_description WHERE language_id=3 ORDER BY category_id DESC LIMIT 15;"'
```

**Step 5: Обновить маппинг**

Добавить новые ID в `data/opencart_mapping.json`

---

## Task 9: Верификация

**Step 1: Проверить структуру**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
SELECT c.category_id, c.parent_id, cd.name
FROM oc_category c
JOIN oc_category_description cd ON c.category_id = cd.category_id AND cd.language_id = 3
WHERE c.status = 1
ORDER BY c.parent_id, c.category_id;"'
```

**Step 2: Проверить SEO URL**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
SELECT
    REPLACE(query, 'category_id=', '') as id,
    keyword,
    language_id
FROM oc_seo_url
WHERE query LIKE 'category_id=%'
ORDER BY CAST(REPLACE(query, 'category_id=', '') AS UNSIGNED), language_id
LIMIT 30;"'
```

**Step 3: Проверить мета-теги**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
SELECT
    category_id,
    language_id,
    LEFT(meta_title, 40) as title,
    LEFT(meta_h1, 25) as h1,
    LENGTH(description) as content_len
FROM oc_category_description
WHERE category_id IN (415, 412, 423, 459, 461)
ORDER BY category_id, language_id;"'
```

**Step 4: Визуальная проверка**

Открыть на сайте:
- https://ultimate.net.ua/aktivnaya-pena
- https://ultimate.net.ua/polirovalnye-krugi
- https://ultimate.net.ua/uk/aktivna-pina

---

## Task 10: Коммит

**Step 1: Добавить файлы**

Run:
```bash
git add data/opencart_mapping.json deploy/sync/
```

**Step 2: Коммит**

Run:
```bash
git commit -m "$(cat <<'EOF'
feat(deploy): sync OpenCart categories with project structure

- Added opencart_mapping.json (slug → category_id)
- Updated SEO URLs to use our slugs (RU + UK)
- Updated meta tags (title, description, h1)
- Updated content (MD → HTML)
- Created 12 new categories
- Restructured tree (Наборы: L1 → L2)

Categories: 52 (excluding glavnaya)
Languages: RU (3), UK (1)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Checklist

- [ ] Task 1: Маппинг создан
- [ ] Task 2: Структура (parent_id) обновлена
- [ ] Task 3: SEO URL обновлены
- [ ] Task 4: Мета-теги RU обновлены
- [ ] Task 5: Мета-теги UK обновлены
- [ ] Task 6: Контент RU загружен
- [ ] Task 7: Контент UK загружен
- [ ] Task 8: Новые категории созданы
- [ ] Task 9: Верификация пройдена
- [ ] Task 10: Коммит сделан

---

## Rollback

```bash
# Восстановить из бэкапа
cat data/backups/categories_backup_2026-02-03.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

---

## Notes

- **language_id=3** → Русский (RU)
- **language_id=1** → Українська (UK)
- **glavnaya** — НЕ ТРОГАТЬ
- **Товары** — отдельная задача ПОТОМ
- Экранирование: `'` → `\'` в SQL строках
