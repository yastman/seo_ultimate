# Category Migration Plan: OpenCart ↔ Project Sync

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Синхронизировать структуру категорий OpenCart с проектом (catalog_structure.json) — создать недостающие, перенести товары, скрыть лишние, обновить мета/контент.

**Architecture:** SSH через `ult` к серверу, прямые SQL запросы в БД `yastman_test`. Порядок: бэкап → создание категорий → перенос товаров → скрытие старых → обновление структуры → мета/контент.

**Tech Stack:** Bash, MySQL, SSH (`ult` alias), Python (для генерации SQL)

---

## Исходные данные

- **Источник истины:** `data/catalog_structure.json` (62 категории)
- **Маппинг:** `data/opencart_mapping.json` (slug → category_id)
- **БД:** yastman_test, language_id=3 (RU), language_id=1 (UK)
- **Бэкап:** `data/backups/yastman_test_full_2026-02-03_0634.sql`

---

## Task 1: Верификация бэкапа и состояния

**Files:**
- Read: `data/backups/yastman_test_full_2026-02-03_0634.sql`

**Step 1: Проверить наличие бэкапа**

Run:
```bash
ls -lh data/backups/yastman_test_full_2026-02-03_0634.sql
```

Expected: Файл ~67MB существует

**Step 2: Проверить текущее количество категорий на сервере**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e "SELECT COUNT(*) FROM oc_category WHERE status = 1;"'
```

Expected: 57 (или близко)

**Step 3: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 1: Backup verified, server has $(ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e \"SELECT COUNT(*) FROM oc_category WHERE status = 1;\"') active categories" >> logs/migration.log
```

---

## Task 2: Создать категорию `voski` (родительская для воска)

**Files:**
- Modify: `data/opencart_mapping.json`

**Step 1: Создать категорию в БД**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
-- Создаём voski под zashchitnye-pokrytiya (435)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified)
VALUES (435, 0, 1, 0, 1, NOW(), NOW());
SET @voski_id = LAST_INSERT_ID();

-- Описания RU и UK
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1)
VALUES
(@voski_id, 3, \"Воски\", \"\", \"\", \"\", \"\", \"\"),
(@voski_id, 1, \"Воски\", \"\", \"\", \"\", \"\", \"\");

-- SEO URL
INSERT INTO oc_seo_url (store_id, language_id, query, keyword)
VALUES
(0, 3, CONCAT(\"category_id=\", @voski_id), \"voski\"),
(0, 1, CONCAT(\"category_id=\", @voski_id), \"vosky\");

-- Category path
INSERT INTO oc_category_path (category_id, path_id, level)
SELECT @voski_id, path_id, level FROM oc_category_path WHERE category_id = 435
UNION ALL SELECT @voski_id, @voski_id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 435);

-- Вывести ID
SELECT @voski_id as new_voski_id;
"'
```

Expected: new_voski_id = <число>

**Step 2: Получить ID и обновить маппинг**

Run:
```bash
VOSKI_ID=$(ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e "SELECT category_id FROM oc_category c JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) WHERE u.keyword = \"voski\" AND u.language_id = 3;"')
echo "voski ID: $VOSKI_ID"
```

**Step 3: Обновить маппинг в JSON**

Run:
```bash
python3 -c "
import json
m = json.load(open('data/opencart_mapping.json'))
m['slug_to_id']['voski'] = $(ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e "SELECT category_id FROM oc_category c JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) WHERE u.keyword = \"voski\" AND u.language_id = 3;"')
json.dump(m, open('data/opencart_mapping.json', 'w'), indent=2, ensure_ascii=False)
print('Updated mapping with voski')
"
```

**Step 4: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 2: Created voski category" >> logs/migration.log
```

---

## Task 3: Переместить tverdyy-vosk и zhidkiy-vosk под voski

**Step 1: Обновить parent_id**

Run:
```bash
VOSKI_ID=$(ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e "SELECT category_id FROM oc_category c JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) WHERE u.keyword = \"voski\" AND u.language_id = 3;"')

ult "sudo mysql -u root -pfr1daYTw1st yastman_test -e \"
-- tverdyy-vosk (437) → voski
UPDATE oc_category SET parent_id = $VOSKI_ID WHERE category_id = 437;

-- zhidkiy-vosk (456) → voski
UPDATE oc_category SET parent_id = $VOSKI_ID WHERE category_id = 456;

-- Пересчитать category_path для 437
DELETE FROM oc_category_path WHERE category_id = 437;
INSERT INTO oc_category_path (category_id, path_id, level)
SELECT 437, path_id, level FROM oc_category_path WHERE category_id = $VOSKI_ID
UNION ALL SELECT 437, 437, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = $VOSKI_ID);

-- Пересчитать category_path для 456
DELETE FROM oc_category_path WHERE category_id = 456;
INSERT INTO oc_category_path (category_id, path_id, level)
SELECT 456, path_id, level FROM oc_category_path WHERE category_id = $VOSKI_ID
UNION ALL SELECT 456, 456, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = $VOSKI_ID);
\""
```

**Step 2: Верификация**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "SELECT category_id, parent_id, (SELECT name FROM oc_category_description WHERE category_id = c.category_id AND language_id = 3) as name FROM oc_category c WHERE category_id IN (437, 456);"'
```

Expected: Оба с parent_id = <voski_id>

**Step 3: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 3: Moved tverdyy-vosk and zhidkiy-vosk under voski" >> logs/migration.log
```

---

## Task 4: Создать категорию `shchetki-i-kisti`

**Step 1: Создать в БД**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified)
VALUES (445, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();

INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1)
VALUES
(@id, 3, \"Щетки и кисти\", \"\", \"\", \"\", \"\", \"\"),
(@id, 1, \"Щітки і пензлі\", \"\", \"\", \"\", \"\", \"\");

INSERT INTO oc_seo_url (store_id, language_id, query, keyword)
VALUES
(0, 3, CONCAT(\"category_id=\", @id), \"shchetki-i-kisti\"),
(0, 1, CONCAT(\"category_id=\", @id), \"shchitky-i-penzli\");

INSERT INTO oc_category_path (category_id, path_id, level)
SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 445
UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 445);

INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

SELECT @id as new_id;
"'
```

**Step 2: Обновить маппинг**

Run:
```bash
python3 -c "
import json
import subprocess
result = subprocess.run(['ult', 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e \"SELECT category_id FROM oc_category c JOIN oc_seo_url u ON u.query = CONCAT(\\\"category_id=\\\", c.category_id) WHERE u.keyword = \\\"shchetki-i-kisti\\\" AND u.language_id = 3;\"'], capture_output=True, text=True)
cat_id = int(result.stdout.strip())
m = json.load(open('data/opencart_mapping.json'))
m['slug_to_id']['shchetki-i-kisti'] = cat_id
json.dump(m, open('data/opencart_mapping.json', 'w'), indent=2, ensure_ascii=False)
print(f'Added shchetki-i-kisti with id {cat_id}')
"
```

**Step 3: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 4: Created shchetki-i-kisti" >> logs/migration.log
```

---

## Task 5: Создать категорию `obezzhirivateli`

**Step 1: Создать в БД**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified)
VALUES (471, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();

INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1)
VALUES
(@id, 3, \"Обезжириватели\", \"\", \"\", \"\", \"\", \"\"),
(@id, 1, \"Знежирювачі\", \"\", \"\", \"\", \"\", \"\");

INSERT INTO oc_seo_url (store_id, language_id, query, keyword)
VALUES
(0, 3, CONCAT(\"category_id=\", @id), \"obezzhirivateli\"),
(0, 1, CONCAT(\"category_id=\", @id), \"znezhyryuvachi\");

INSERT INTO oc_category_path (category_id, path_id, level)
SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 471
UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 471);

INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

SELECT @id as new_id;
"'
```

**Step 2: Обновить маппинг**

Run:
```bash
python3 -c "
import json
import subprocess
result = subprocess.run(['ult', 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e \"SELECT category_id FROM oc_category c JOIN oc_seo_url u ON u.query = CONCAT(\\\"category_id=\\\", c.category_id) WHERE u.keyword = \\\"obezzhirivateli\\\" AND u.language_id = 3;\"'], capture_output=True, text=True)
cat_id = int(result.stdout.strip())
m = json.load(open('data/opencart_mapping.json'))
m['slug_to_id']['obezzhirivateli'] = cat_id
json.dump(m, open('data/opencart_mapping.json', 'w'), indent=2, ensure_ascii=False)
print(f'Added obezzhirivateli with id {cat_id}')
"
```

**Step 3: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 5: Created obezzhirivateli" >> logs/migration.log
```

---

## Task 6: Создать остальные категории (batch)

**Категории для создания:**

| Slug | Parent | Name RU | Name UK |
|------|--------|---------|---------|
| kislotnyy | avtoshampuni (469) | Кислотные шампуни | Кислотні шампуні |
| ukhod-za-naruzhnym-plastikom | ochistiteli-kuzova (471) | Уход за наружным пластиком | Догляд за зовнішнім пластиком |
| keramika-dlya-diskov | sredstva-dlya-diskov-i-shin (472) | Керамика для дисков | Кераміка для дисків |
| tryapka-dlya-avto | mikrofibra-i-tryapki (446) | Тряпка для авто | Ганчірка для авто |
| tryapka-dlya-vytiraniya-avto-posle-moyki | mikrofibra-i-tryapki (446) | Тряпка для вытирания авто после мойки | Ганчірка для витирання авто після мийки |
| dlya-stekol | mikrofibra-i-tryapki (446) | Микрофибра для стекол | Мікрофібра для скла |
| shchetka-dlya-moyki-avto | shchetki-i-kisti (NEW) | Щетка для мойки авто | Щітка для миття авто |
| kisti-dlya-deteylinga | shchetki-i-kisti (NEW) | Кисти для детейлинга | Пензлі для детейлінгу |
| aksessuary-dlya-naneseniya-sredstv | aksessuary (445) | Аксессуары для нанесения средств | Аксесуари для нанесення засобів |
| nabory-dlya-moyki | nabory (466) | Наборы для мойки | Набори для мийки |
| nabory-dlya-salona | nabory (466) | Наборы для салона | Набори для салону |
| podarochnyy | nabory (466) | Подарочные наборы | Подарункові набори |
| akkumulyatornaya | polirovalnye-mashinki (461) | Аккумуляторные полировальные машинки | Акумуляторні полірувальні машинки |
| mekhovye | polirovalnye-krugi (459) | Меховые круги | Хутряні круги |
| ukhod-za-kozhey | sredstva-dlya-kozhi (428) | Уход за кожей | Догляд за шкірою |
| ochistiteli-kozhi | sredstva-dlya-kozhi (428) | Очистители кожи | Очищувачі шкіри |
| opt-i-b2b | 0 (root) | Опт и B2B | Опт та B2B |

**Step 1: Создать SQL скрипт**

Run:
```bash
cat > /tmp/create_categories.sql << 'EOSQL'
-- kislotnyy под avtoshampuni (469)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (469, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Кислотные шампуни', '', '', '', '', ''), (@id, 1, 'Кислотні шампуні', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'kislotnyy'), (0, 1, CONCAT('category_id=', @id), 'kyslotnyi');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 469 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 469);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- ukhod-za-naruzhnym-plastikom под ochistiteli-kuzova (471)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (471, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Уход за наружным пластиком', '', '', '', '', ''), (@id, 1, 'Догляд за зовнішнім пластиком', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'ukhod-za-naruzhnym-plastikom'), (0, 1, CONCAT('category_id=', @id), 'dohlyad-za-zovnishnim-plastykom');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 471 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 471);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- keramika-dlya-diskov под sredstva-dlya-diskov-i-shin (472)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (472, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Керамика для дисков', '', '', '', '', ''), (@id, 1, 'Кераміка для дисків', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'keramika-dlya-diskov'), (0, 1, CONCAT('category_id=', @id), 'keramika-dlya-dyskiv');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 472 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 472);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- tryapka-dlya-avto под mikrofibra-i-tryapki (446)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (446, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Тряпка для авто', '', '', '', '', ''), (@id, 1, 'Ганчірка для авто', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'tryapka-dlya-avto'), (0, 1, CONCAT('category_id=', @id), 'hanchirka-dlya-avto');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 446 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 446);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- tryapka-dlya-vytiraniya-avto-posle-moyki под mikrofibra-i-tryapki (446)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (446, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Тряпка для вытирания авто после мойки', '', '', '', '', ''), (@id, 1, 'Ганчірка для витирання авто після мийки', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'tryapka-dlya-vytiraniya-avto-posle-moyki'), (0, 1, CONCAT('category_id=', @id), 'hanchirka-dlya-vytyrannya-avto-pislya-myiky');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 446 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 446);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- dlya-stekol под mikrofibra-i-tryapki (446)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (446, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Микрофибра для стекол', '', '', '', '', ''), (@id, 1, 'Мікрофібра для скла', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'dlya-stekol'), (0, 1, CONCAT('category_id=', @id), 'dlya-skla');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 446 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 446);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- aksessuary-dlya-naneseniya-sredstv под aksessuary (445)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (445, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Аксессуары для нанесения средств', '', '', '', '', ''), (@id, 1, 'Аксесуари для нанесення засобів', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'aksessuary-dlya-naneseniya-sredstv'), (0, 1, CONCAT('category_id=', @id), 'aksesuary-dlya-nanesennya-zasobiv');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 445 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 445);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- nabory-dlya-moyki под nabory (466)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (466, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Наборы для мойки', '', '', '', '', ''), (@id, 1, 'Набори для мийки', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'nabory-dlya-moyki'), (0, 1, CONCAT('category_id=', @id), 'nabory-dlya-myiky');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 466 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 466);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- nabory-dlya-salona под nabory (466)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (466, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Наборы для салона', '', '', '', '', ''), (@id, 1, 'Набори для салону', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'nabory-dlya-salona'), (0, 1, CONCAT('category_id=', @id), 'nabory-dlya-salonu');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 466 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 466);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- podarochnyy под nabory (466)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (466, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Подарочные наборы', '', '', '', '', ''), (@id, 1, 'Подарункові набори', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'podarochnyy'), (0, 1, CONCAT('category_id=', @id), 'podarunkovyi');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 466 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 466);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- akkumulyatornaya под polirovalnye-mashinki (461)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (461, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Аккумуляторные полировальные машинки', '', '', '', '', ''), (@id, 1, 'Акумуляторні полірувальні машинки', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'akkumulyatornaya'), (0, 1, CONCAT('category_id=', @id), 'akumulyatorna');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 461 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 461);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- mekhovye под polirovalnye-krugi (459)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (459, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Меховые круги', '', '', '', '', ''), (@id, 1, 'Хутряні круги', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'mekhovye'), (0, 1, CONCAT('category_id=', @id), 'khutryani');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 459 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 459);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- ukhod-za-kozhey под sredstva-dlya-kozhi (428)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (428, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Уход за кожей', '', '', '', '', ''), (@id, 1, 'Догляд за шкірою', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'ukhod-za-kozhey'), (0, 1, CONCAT('category_id=', @id), 'dohlyad-za-shkiroyu');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 428 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 428);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- ochistiteli-kozhi под sredstva-dlya-kozhi (428)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (428, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Очистители кожи', '', '', '', '', ''), (@id, 1, 'Очищувачі шкіри', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'ochistiteli-kozhi'), (0, 1, CONCAT('category_id=', @id), 'ochyshchuvachi-shkiry');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = 428 UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = 428);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- opt-i-b2b (корневая, parent=0)
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES (0, 0, 1, 100, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Опт и B2B', '', '', '', '', ''), (@id, 1, 'Опт та B2B', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'opt-i-b2b'), (0, 1, CONCAT('category_id=', @id), 'opt-ta-b2b');
INSERT INTO oc_category_path (category_id, path_id, level) VALUES (@id, @id, 0);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);
EOSQL
```

**Step 2: Выполнить SQL**

Run:
```bash
cat /tmp/create_categories.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

Expected: No errors

**Step 3: Создать shchetka-dlya-moyki-avto и kisti-dlya-deteylinga (зависят от shchetki-i-kisti)**

Run:
```bash
SHCHETKI_ID=$(ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e "SELECT category_id FROM oc_category c JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) WHERE u.keyword = \"shchetki-i-kisti\" AND u.language_id = 3;"')

ult "sudo mysql -u root -pfr1daYTw1st yastman_test -e \"
-- shchetka-dlya-moyki-avto
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES ($SHCHETKI_ID, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Щетка для мойки авто', '', '', '', '', ''), (@id, 1, 'Щітка для миття авто', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'shchetka-dlya-moyki-avto'), (0, 1, CONCAT('category_id=', @id), 'shchitka-dlya-myyttya-avto');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = $SHCHETKI_ID UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = $SHCHETKI_ID);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);

-- kisti-dlya-deteylinga
INSERT INTO oc_category (parent_id, top, column, sort_order, status, date_added, date_modified) VALUES ($SHCHETKI_ID, 0, 1, 0, 1, NOW(), NOW());
SET @id = LAST_INSERT_ID();
INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_keyword, meta_h1) VALUES (@id, 3, 'Кисти для детейлинга', '', '', '', '', ''), (@id, 1, 'Пензлі для детейлінгу', '', '', '', '', '');
INSERT INTO oc_seo_url (store_id, language_id, query, keyword) VALUES (0, 3, CONCAT('category_id=', @id), 'kisti-dlya-deteylinga'), (0, 1, CONCAT('category_id=', @id), 'penzli-dlya-deteylingu');
INSERT INTO oc_category_path (category_id, path_id, level) SELECT @id, path_id, level FROM oc_category_path WHERE category_id = $SHCHETKI_ID UNION ALL SELECT @id, @id, (SELECT MAX(level)+1 FROM oc_category_path WHERE category_id = $SHCHETKI_ID);
INSERT INTO oc_category_to_store (category_id, store_id) VALUES (@id, 0);
\""
```

**Step 4: Обновить маппинг всех новых категорий**

Run:
```bash
python3 << 'PYEOF'
import json
import subprocess

slugs = [
    'kislotnyy', 'ukhod-za-naruzhnym-plastikom', 'keramika-dlya-diskov',
    'tryapka-dlya-avto', 'tryapka-dlya-vytiraniya-avto-posle-moyki', 'dlya-stekol',
    'aksessuary-dlya-naneseniya-sredstv', 'nabory-dlya-moyki', 'nabory-dlya-salona',
    'podarochnyy', 'akkumulyatornaya', 'mekhovye', 'ukhod-za-kozhey', 'ochistiteli-kozhi',
    'opt-i-b2b', 'shchetka-dlya-moyki-avto', 'kisti-dlya-deteylinga'
]

m = json.load(open('data/opencart_mapping.json'))

for slug in slugs:
    cmd = f'ult \'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e "SELECT category_id FROM oc_category c JOIN oc_seo_url u ON u.query = CONCAT(\\"category_id=\\", c.category_id) WHERE u.keyword = \\"{slug}\\" AND u.language_id = 3;"\''
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        cat_id = int(result.stdout.strip())
        m['slug_to_id'][slug] = cat_id
        print(f'{slug}: {cat_id}')

# Удалить из needs_creation
m['needs_creation'] = [s for s in m.get('needs_creation', []) if s not in m['slug_to_id']]

json.dump(m, open('data/opencart_mapping.json', 'w'), indent=2, ensure_ascii=False)
print(f"\nUpdated mapping: {len(m['slug_to_id'])} categories")
PYEOF
```

**Step 5: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 6: Created 17 new categories" >> logs/migration.log
```

---

## Task 7: Перенести товары из старых категорий

**Step 1: Перенос в antidozhd (441 → 473)**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
-- Защитные покрытия для стекол (441) → Антидождь (473)
UPDATE oc_product_to_category SET category_id = 473 WHERE category_id = 441;
SELECT ROW_COUNT() as moved_to_antidozhd;
"'
```

Expected: moved_to_antidozhd = 13

**Step 2: Перенос в keramika-i-zhidkoe-steklo (440, 442, 443, 444 → 439)**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
-- Защитные покрытия для пластика (440) → Керамика (439)
UPDATE oc_product_to_category SET category_id = 439 WHERE category_id = 440;
-- Защитные покрытия для кожи (442) → Керамика (439)
UPDATE oc_product_to_category SET category_id = 439 WHERE category_id = 442;
-- Защитные покрытия для ткани (443) → Керамика (439)
UPDATE oc_product_to_category SET category_id = 439 WHERE category_id = 443;
-- Защитные покрытия для колёс (444) → Керамика (439)
UPDATE oc_product_to_category SET category_id = 439 WHERE category_id = 444;
"'
```

**Step 3: Перенос в polirovalnye-krugi (460 → 459)**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
-- Оправки, подложки (460) → Полировальные круги (459)
UPDATE oc_product_to_category SET category_id = 459 WHERE category_id = 460;
"'
```

**Step 4: Перенос в oborudovanie (464 → 462)**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
-- Пылесосы (464) → Оборудование (462)
UPDATE oc_product_to_category SET category_id = 462 WHERE category_id = 464;
"'
```

**Step 5: Перенос в shchetki-i-kisti (449, 450, 452 → NEW)**

Run:
```bash
SHCHETKI_ID=$(ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e "SELECT category_id FROM oc_category c JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) WHERE u.keyword = \"shchetki-i-kisti\" AND u.language_id = 3;"')

ult "sudo mysql -u root -pfr1daYTw1st yastman_test -e \"
-- Щетки, аппликаторы для интерьера (449) → shchetki-i-kisti
UPDATE oc_product_to_category SET category_id = $SHCHETKI_ID WHERE category_id = 449;
-- Мочалки, щётки для экстерьера (450) → shchetki-i-kisti
UPDATE oc_product_to_category SET category_id = $SHCHETKI_ID WHERE category_id = 450;
-- Щетки и кисти старая (452) → shchetki-i-kisti
UPDATE oc_product_to_category SET category_id = $SHCHETKI_ID WHERE category_id = 452;
\""
```

**Step 6: Перенос в mikrofibra-i-tryapki (451 → 446)**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
-- Тряпки для авто (451) → Микрофибра и тряпки (446)
UPDATE oc_product_to_category SET category_id = 446 WHERE category_id = 451;
"'
```

**Step 7: Перенос в obezzhirivateli (426 → NEW)**

Run:
```bash
OBEZZHIR_ID=$(ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e "SELECT category_id FROM oc_category c JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) WHERE u.keyword = \"obezzhirivateli\" AND u.language_id = 3;"')

ult "sudo mysql -u root -pfr1daYTw1st yastman_test -e \"
-- Очистители и обезжириватели (426) → obezzhirivateli
UPDATE oc_product_to_category SET category_id = $OBEZZHIR_ID WHERE category_id = 426;
\""
```

**Step 8: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 7: Migrated ~174 products to new categories" >> logs/migration.log
```

---

## Task 8: Скрыть старые категории

**Step 1: Установить status=0**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
UPDATE oc_category SET status = 0 WHERE category_id IN (
    440,  -- Защитные покрытия для пластика
    441,  -- Защитные покрытия для стекол
    442,  -- Защитные покрытия для кожи
    443,  -- Защитные покрытия для ткани
    444,  -- Защитные покрытия для колёс
    449,  -- Щетки, аппликаторы для интерьера
    450,  -- Мочалки, щётки для экстерьера
    451,  -- Тряпки для авто (старая)
    452,  -- Щетки и кисти (старая)
    460,  -- Оправки, подложки
    464,  -- Пылесосы
    465,  -- Озоногенераторы
    426   -- Очистители и обезжириватели
);
SELECT ROW_COUNT() as hidden_categories;
"'
```

Expected: hidden_categories = 13

**Step 2: Верификация**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "SELECT category_id, status, (SELECT name FROM oc_category_description WHERE category_id = c.category_id AND language_id = 3) as name FROM oc_category c WHERE category_id IN (440,441,442,443,444,449,450,451,452,460,464,465,426);"'
```

Expected: Все со status=0

**Step 3: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 8: Hidden 13 old categories" >> logs/migration.log
```

---

## Task 9: Обновить SEO URL существующих категорий

**Step 1: Генерировать SQL из маппинга**

Run:
```bash
python3 << 'PYEOF'
import json

m = json.load(open('data/opencart_mapping.json'))

# UK slugs маппинг
uk_slugs = {
    'aktivnaya-pena': 'aktivna-pina',
    'shampuni-dlya-ruchnoy-moyki': 'shampuni-dlya-ruchnogo-myttya',
    'avtoshampuni': 'avtoshampuny',
    'moyka-i-eksterer': 'myjka-i-eksterier',
    'ochistiteli-stekol': 'ochyshchuvachi-skla',
    'sredstva-dlya-stekol': 'zasoby-dlya-skla',
    'omyvatel': 'omyvach',
    'antidozhd': 'antydoshch',
    'glina-i-avtoskraby': 'hlyna-ta-avtoskraby',
    'ochistiteli-kuzova': 'ochyshchuvachi-kuzova',
    'antimoshka': 'antymoshka',
    'antibitum': 'antybitum',
    'ochistiteli-dvigatelya': 'ochyshchuvachi-dvyhuna',
    'cherniteli-shin': 'chornyteli-shyn',
    'ochistiteli-diskov': 'ochyshchuvachi-dyskiv',
    'ochistiteli-shin': 'ochyshchuvachi-shyn',
    'sredstva-dlya-diskov-i-shin': 'zasoby-dlya-dyskiv-i-shyn',
    'ukhod-za-intererom': 'dohlyad-za-interierom',
    'sredstva-dlya-khimchistki-salona': 'zasoby-dlya-khimchystky-salonu',
    'sredstva-dlya-kozhi': 'zasoby-dlya-shkiry',
    'poliroli-dlya-plastika': 'poliroli-dlya-plastyku',
    'neytralizatory-zapakha': 'neytralizatory-zapakhu',
    'pyatnovyvoditeli': 'plyamovyvidnyky',
    'zashchitnye-pokrytiya': 'zakhysni-pokryttya',
    'tverdyy-vosk': 'tverdyy-visk',
    'zhidkiy-vosk': 'ridkyy-visk',
    'keramika-i-zhidkoe-steklo': 'keramika-i-ridke-sklo',
    'kvik-deteylery': 'kvik-deteylery',
    'silanty': 'sylanty',
    'aksessuary': 'aksesuary',
    'mikrofibra-i-tryapki': 'mikrofibra-i-ganchirky',
    'raspyliteli-i-penniki': 'rozpylyuvachi-i-pinnyky',
    'vedra-i-emkosti': 'vidra-i-yemnosti',
    'gubki-i-varezhki': 'hubky-i-rukavychky',
    'malyarniy-skotch': 'malyarnyy-skotch',
    'nabory': 'nabory',
    'polirovka': 'poliruvannya',
    'polirovalnye-pasty': 'poliruvalni-pasty',
    'polirovalnye-krugi': 'poliruvalni-kruhy',
    'polirovalnye-mashinki': 'poliruvalni-mashynky',
    'oborudovanie': 'obladnannya',
    'apparaty-tornador': 'aparaty-tornador',
}

sql_lines = ['-- SEO URL updates']
for slug, cat_id in m['slug_to_id'].items():
    uk_slug = uk_slugs.get(slug, slug)
    sql_lines.append(f"UPDATE oc_seo_url SET keyword = '{slug}' WHERE query = 'category_id={cat_id}' AND language_id = 3;")
    sql_lines.append(f"UPDATE oc_seo_url SET keyword = '{uk_slug}' WHERE query = 'category_id={cat_id}' AND language_id = 1;")

with open('/tmp/update_seo_urls.sql', 'w') as f:
    f.write('\n'.join(sql_lines))

print(f"Generated {len(sql_lines)} SQL statements")
PYEOF
```

**Step 2: Применить SQL**

Run:
```bash
cat /tmp/update_seo_urls.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

**Step 3: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 9: Updated SEO URLs" >> logs/migration.log
```

---

## Task 10: Обновить мета-теги RU

**Step 1: Генерировать SQL из мета-файлов**

Run:
```bash
python3 << 'PYEOF'
import json
import os

m = json.load(open('data/opencart_mapping.json'))
sql_lines = ['-- Meta tags RU (language_id=3)']

for slug, cat_id in m['slug_to_id'].items():
    # Поиск мета-файла
    for root, dirs, files in os.walk('categories'):
        meta_file = f'{slug}_meta.json'
        if meta_file in files:
            meta_path = os.path.join(root, meta_file)
            with open(meta_path) as f:
                meta = json.load(f)
            title = meta['meta']['title'].replace("'", "\\'")
            desc = meta['meta']['description'].replace("'", "\\'")
            h1 = meta.get('h1', '').replace("'", "\\'")
            sql_lines.append(f"UPDATE oc_category_description SET meta_title = '{title}', meta_description = '{desc}', meta_h1 = '{h1}' WHERE category_id = {cat_id} AND language_id = 3;")
            break

with open('/tmp/update_meta_ru.sql', 'w') as f:
    f.write('\n'.join(sql_lines))

print(f"Generated {len(sql_lines)-1} meta updates for RU")
PYEOF
```

**Step 2: Применить SQL**

Run:
```bash
cat /tmp/update_meta_ru.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

**Step 3: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 10: Updated RU meta tags" >> logs/migration.log
```

---

## Task 11: Обновить мета-теги UK

**Step 1: Генерировать SQL из UK мета-файлов**

Run:
```bash
python3 << 'PYEOF'
import json
import os

m = json.load(open('data/opencart_mapping.json'))
sql_lines = ['-- Meta tags UK (language_id=1)']

for slug, cat_id in m['slug_to_id'].items():
    meta_path = f'uk/categories/{slug}/meta/{slug}_meta.json'
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        title = meta['meta']['title'].replace("'", "\\'")
        desc = meta['meta']['description'].replace("'", "\\'")
        h1 = meta.get('h1', '').replace("'", "\\'")
        sql_lines.append(f"UPDATE oc_category_description SET meta_title = '{title}', meta_description = '{desc}', meta_h1 = '{h1}' WHERE category_id = {cat_id} AND language_id = 1;")

with open('/tmp/update_meta_uk.sql', 'w') as f:
    f.write('\n'.join(sql_lines))

print(f"Generated {len(sql_lines)-1} meta updates for UK")
PYEOF
```

**Step 2: Применить SQL**

Run:
```bash
cat /tmp/update_meta_uk.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

**Step 3: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 11: Updated UK meta tags" >> logs/migration.log
```

---

## Task 12: Обновить контент RU

**Step 1: Использовать upload_to_db.py или генерировать SQL**

Run:
```bash
python3 scripts/upload_to_db.py --lang ru --generate-sql > /tmp/update_content_ru.sql 2>/dev/null || echo "Script not found, manual generation needed"
```

Если скрипт не найден, генерируем вручную:

Run:
```bash
python3 << 'PYEOF'
import json
import os
import re

def md_to_html(md):
    html = md
    # Убрать H1
    html = re.sub(r'^# .+\n\n?', '', html, count=1, flags=re.MULTILINE)
    # H2, H3
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # Paragraphs
    paragraphs = html.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<h'):
            result.append(f'<p>{p}</p>')
        elif p:
            result.append(p)
    return '\n'.join(result)

m = json.load(open('data/opencart_mapping.json'))
sql_lines = ['-- Content RU (language_id=3)']

for slug, cat_id in m['slug_to_id'].items():
    for root, dirs, files in os.walk('categories'):
        content_file = f'{slug}_ru.md'
        if content_file in files:
            content_path = os.path.join(root, content_file)
            with open(content_path) as f:
                md = f.read()
            html = md_to_html(md).replace("'", "\\'").replace('\n', '\\n')
            sql_lines.append(f"UPDATE oc_category_description SET description = '{html}' WHERE category_id = {cat_id} AND language_id = 3;")
            break

with open('/tmp/update_content_ru.sql', 'w') as f:
    f.write('\n'.join(sql_lines))

print(f"Generated {len(sql_lines)-1} content updates for RU")
PYEOF
```

**Step 2: Применить SQL**

Run:
```bash
cat /tmp/update_content_ru.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

**Step 3: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 12: Updated RU content" >> logs/migration.log
```

---

## Task 13: Обновить контент UK

**Step 1: Генерировать SQL**

Run:
```bash
python3 << 'PYEOF'
import json
import os
import re

def md_to_html(md):
    html = md
    html = re.sub(r'^# .+\n\n?', '', html, count=1, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    paragraphs = html.split('\n\n')
    result = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<h'):
            result.append(f'<p>{p}</p>')
        elif p:
            result.append(p)
    return '\n'.join(result)

m = json.load(open('data/opencart_mapping.json'))
sql_lines = ['-- Content UK (language_id=1)']

for slug, cat_id in m['slug_to_id'].items():
    content_path = f'uk/categories/{slug}/content/{slug}_uk.md'
    if os.path.exists(content_path):
        with open(content_path) as f:
            md = f.read()
        html = md_to_html(md).replace("'", "\\'").replace('\n', '\\n')
        sql_lines.append(f"UPDATE oc_category_description SET description = '{html}' WHERE category_id = {cat_id} AND language_id = 1;")

with open('/tmp/update_content_uk.sql', 'w') as f:
    f.write('\n'.join(sql_lines))

print(f"Generated {len(sql_lines)-1} content updates for UK")
PYEOF
```

**Step 2: Применить SQL**

Run:
```bash
cat /tmp/update_content_uk.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

**Step 3: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 13: Updated UK content" >> logs/migration.log
```

---

## Task 14: Финальная верификация

**Step 1: Проверить количество активных категорий**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
SELECT
    (SELECT COUNT(*) FROM oc_category WHERE status = 1) as active_categories,
    (SELECT COUNT(*) FROM oc_category WHERE status = 0) as hidden_categories,
    (SELECT COUNT(DISTINCT category_id) FROM oc_product_to_category) as categories_with_products;
"'
```

Expected: ~64 active, 13 hidden

**Step 2: Проверить структуру дерева**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
SELECT c.category_id, c.parent_id, cd.name, u.keyword
FROM oc_category c
JOIN oc_category_description cd ON c.category_id = cd.category_id AND cd.language_id = 3
LEFT JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) AND u.language_id = 3
WHERE c.status = 1 AND c.parent_id = 0
ORDER BY c.sort_order;
"'
```

Expected: L1 категории с правильными slug'ами

**Step 3: Проверить voski структуру**

Run:
```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
SELECT c.category_id, c.parent_id, cd.name, u.keyword
FROM oc_category c
JOIN oc_category_description cd ON c.category_id = cd.category_id AND cd.language_id = 3
LEFT JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) AND u.language_id = 3
WHERE c.category_id IN (437, 456) OR u.keyword = \"voski\";
"'
```

Expected: voski как parent для tverdyy-vosk и zhidkiy-vosk

**Step 4: Визуальная проверка сайта**

Run:
```bash
echo "Проверить вручную:"
echo "- https://ultimate.net.ua/aktivnaya-pena"
echo "- https://ultimate.net.ua/voski"
echo "- https://ultimate.net.ua/shchetki-i-kisti"
echo "- https://ultimate.net.ua/uk/aktivna-pina"
```

**Step 5: Записать в лог**

Run:
```bash
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Task 14: Verification complete" >> logs/migration.log
echo "[$(date '+%Y-%m-%d %H:%M:%S')] MIGRATION COMPLETE" >> logs/migration.log
```

---

## Task 15: Коммит

**Step 1: Добавить файлы**

Run:
```bash
git add data/opencart_mapping.json logs/migration.log
```

**Step 2: Коммит**

Run:
```bash
git commit -m "$(cat <<'EOF'
feat(deploy): complete category migration to OpenCart

- Created 20 new categories matching project structure
- Migrated ~174 products from old categories
- Hidden 13 deprecated categories (status=0)
- Updated SEO URLs (RU + UK)
- Updated meta tags (RU + UK)
- Updated content (RU + UK)
- Restructured voski hierarchy (tverdyy-vosk, zhidkiy-vosk under voski)

Categories: 64 active, 13 hidden
Languages: RU (3), UK (1)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Checklist

- [ ] Task 1: Бэкап верифицирован
- [ ] Task 2: voski создана
- [ ] Task 3: tverdyy-vosk, zhidkiy-vosk перемещены
- [ ] Task 4: shchetki-i-kisti создана
- [ ] Task 5: obezzhirivateli создана
- [ ] Task 6: Остальные 17 категорий созданы
- [ ] Task 7: Товары перенесены (~174 шт)
- [ ] Task 8: Старые категории скрыты (13 шт)
- [ ] Task 9: SEO URL обновлены
- [ ] Task 10: Мета-теги RU обновлены
- [ ] Task 11: Мета-теги UK обновлены
- [ ] Task 12: Контент RU загружен
- [ ] Task 13: Контент UK загружен
- [ ] Task 14: Верификация пройдена
- [ ] Task 15: Коммит сделан

---

## Rollback

```bash
# Восстановить из бэкапа
cat data/backups/yastman_test_full_2026-02-03_0634.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

---

## Notes

- **glavnaya** — не трогаем
- **SALE (467)** — оставляем как есть
- **Мерч (455)** — оставляем как есть
- **language_id=3** → RU
- **language_id=1** → UK
