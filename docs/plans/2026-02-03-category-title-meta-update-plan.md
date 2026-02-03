# Category Title Meta Update — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Добавить `category_title` в `_clean.json` для 10 составных категорий (RU+UK), перегенерировать мета-теги, обновить в БД OpenCart.

**Architecture:** Обновить JSON-файлы семантики → синхронизировать UK скилл → обновить мета-файлы → сгенерировать SQL → выполнить на сервере.

**Tech Stack:** JSON, Bash, MySQL, SSH

---

## Task 1: Update RU _clean.json files (10 files)

**Files:**
- Modify: `categories/glavnaya/data/glavnaya_clean.json`
- Modify: `categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json`
- Modify: `categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json`
- Modify: `categories/aksessuary/gubki-i-varezhki/data/gubki-i-varezhki_clean.json`
- Modify: `categories/aksessuary/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json`
- Modify: `categories/aksessuary/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json`
- Modify: `categories/aksessuary/vedra-i-emkosti/data/vedra-i-emkosti_clean.json`
- Modify: `categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json`
- Modify: `categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json`
- Modify: `categories/opt-i-b2b/data/opt-i-b2b_clean.json`

**Step 1: Add category_title to each file**

После `"id":` и `"name":` добавить поле `"category_title":`:

| File | category_title value |
|------|---------------------|
| glavnaya | `"Автохимия и автокосметика"` |
| moyka-i-eksterer | `"Мойка и экстерьер"` |
| glina-i-avtoskraby | `"Глина и автоскрабы"` |
| gubki-i-varezhki | `"Губки и варежки"` |
| mikrofibra-i-tryapki | `"Микрофибра и тряпки"` |
| raspyliteli-i-penniki | `"Распылители и пенники"` |
| vedra-i-emkosti | `"Вёдра и ёмкости"` |
| kisti-dlya-deteylinga | `"Щётки и кисти для детейлинга"` |
| keramika-i-zhidkoe-steklo | `"Керамика и жидкое стекло"` |
| opt-i-b2b | `"Автохимия оптом"` |

**Example edit (glavnaya):**
```json
{
  "id": "glavnaya",
  "name": "Главная",
  "category_title": "Автохимия и автокосметика",
  "type": "category",
  ...
}
```

**Step 2: Verify JSON validity**

Run: `python3 -c "import json; [json.load(open(f)) for f in ['categories/glavnaya/data/glavnaya_clean.json']]"`
Expected: No errors

---

## Task 2: Update UK _clean.json files (10 files)

**Files:**
- Modify: `uk/categories/glavnaya/data/glavnaya_clean.json`
- Modify: `uk/categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json`
- Modify: `uk/categories/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json`
- Modify: `uk/categories/gubki-i-varezhki/data/gubki-i-varezhki_clean.json`
- Modify: `uk/categories/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json`
- Modify: `uk/categories/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json`
- Modify: `uk/categories/vedra-i-emkosti/data/vedra-i-emkosti_clean.json`
- Modify: `uk/categories/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json`
- Modify: `uk/categories/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json`
- Modify: `uk/categories/opt-i-b2b/data/opt-i-b2b_clean.json`

**Step 1: Add category_title to each file**

| File | category_title value |
|------|---------------------|
| glavnaya | `"Автохімія та автокосметика"` |
| moyka-i-eksterer | `"Мийка та екстер'єр"` |
| glina-i-avtoskraby | `"Глина та автоскраби"` |
| gubki-i-varezhki | `"Губки та рукавички"` |
| mikrofibra-i-tryapki | `"Мікрофібра та ганчірки"` |
| raspyliteli-i-penniki | `"Розпилювачі та піноутворювачі"` |
| vedra-i-emkosti | `"Відра та ємності"` |
| kisti-dlya-deteylinga | `"Щітки та пензлі для детейлінгу"` |
| keramika-i-zhidkoe-steklo | `"Кераміка та рідке скло"` |
| opt-i-b2b | `"Автохімія оптом"` |

**Step 2: Verify JSON validity**

Run: `python3 -c "import json; json.load(open('uk/categories/glavnaya/data/glavnaya_clean.json'))"`
Expected: No errors

---

## Task 3: Sync UK skill to v17.0

**Files:**
- Modify: `.claude/skills/uk-generate-meta/SKILL.md`

**Step 1: Add category_title section after "Термини та джерела істини"**

Add this block after line with `### Що таке \`{primary_keyword}\``:

```markdown
### Що таке `{category_title}` (пріоритет над primary_keyword)

**Опціональне поле** в `_clean.json` для складених категорій або категорій з двома ВЧ-ключами.

```json
{
  "id": "gubki-i-varezhki",
  "category_title": "Губки та рукавички",  // ← пріоритет!
  "keywords": [...]
}
```

**Коли використовувати `category_title`:**
1. **Складена категорія** — назва містить "та" (Щітки та пензлі, Губки та рукавички)
2. **Два сильних ВЧ-ключі** — потрібно охопити обидва (Автохімія та автокосметика)

**Логіка вибору:**
```
ЯКЩО category_title існує:
  використовувати category_title для Title/H1/Description
ІНАКШЕ:
  використовувати primary_keyword (MAX volume)
```
```

**Step 2: Update Title section**

Change `{primary_keyword}` to `{title_phrase}` where:
```
{title_phrase} = category_title ?? primary_keyword
```

**Step 3: Update version to 17.0**

```markdown
**Version:** 17.0 — February 2026

**Changelog v17.0:**
- 🆕 **category_title**: нове опціональне поле для складених категорій та двох ВЧ-ключів
- 📋 **Пріоритет**: `category_title` > `primary_keyword` в Title/H1/Description
```

---

## Task 4: Update RU meta files (10 files)

**Files:**
- Modify: `categories/glavnaya/meta/glavnaya_meta.json`
- Modify: `categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json`
- Modify: `categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json`
- Modify: `categories/aksessuary/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json`
- Modify: `categories/aksessuary/mikrofibra-i-tryapki/meta/mikrofibra-i-tryapki_meta.json`
- Modify: `categories/aksessuary/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json`
- Modify: `categories/aksessuary/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json`
- Modify: `categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/meta/kisti-dlya-deteylinga_meta.json`
- Modify: `categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json`
- Modify: `categories/opt-i-b2b/meta/opt-i-b2b_meta.json`

**Step 1: Update meta for each category**

| slug | title | h1 | description pattern |
|------|-------|-----|---------------------|
| glavnaya | Автохимия и автокосметика — купить, цены \| Ultimate | Автохимия и автокосметика | Producer |
| moyka-i-eksterer | Мойка и экстерьер — купить, цены \| Ultimate | Мойка и экстерьер | Producer |
| glina-i-avtoskraby | Глина и автоскрабы — купить в интернет-магазине Ultimate | Глина и автоскрабы | Shop |
| gubki-i-varezhki | Губки и варежки — купить в интернет-магазине Ultimate | Губки и варежки | Shop |
| mikrofibra-i-tryapki | Микрофибра и тряпки — купить в интернет-магазине Ultimate | Микрофибра и тряпки | Producer |
| raspyliteli-i-penniki | Распылители и пенники — купить, цены \| Ultimate | Распылители и пенники | Shop |
| vedra-i-emkosti | Вёдра и ёмкости — купить в интернет-магазине Ultimate | Вёдра и ёмкости | Shop |
| kisti-dlya-deteylinga | Щётки и кисти для детейлинга — купить, цены \| Ultimate | Щётки и кисти для детейлинга | Shop |
| keramika-i-zhidkoe-steklo | Керамика и жидкое стекло — купить, цены \| Ultimate | Керамика и жидкое стекло | Producer |
| opt-i-b2b | Автохимия оптом — купить в интернет-магазине Ultimate | Автохимия оптом | Producer |

**Step 2: Validate each file**

Run: `python3 scripts/validate_meta.py categories/glavnaya/meta/glavnaya_meta.json`
Expected: `PASS`

---

## Task 5: Update UK meta files (10 files)

**Files:**
- Modify: `uk/categories/glavnaya/meta/glavnaya_meta.json`
- Modify: `uk/categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json`
- Modify: `uk/categories/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json`
- Modify: `uk/categories/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json`
- Modify: `uk/categories/mikrofibra-i-tryapki/meta/mikrofibra-i-tryapki_meta.json`
- Modify: `uk/categories/raspyliteli-i-penniki/meta/raspyliteli-i-penniki_meta.json`
- Modify: `uk/categories/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json`
- Modify: `uk/categories/kisti-dlya-deteylinga/meta/kisti-dlya-deteylinga_meta.json`
- Modify: `uk/categories/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json`
- Modify: `uk/categories/opt-i-b2b/meta/opt-i-b2b_meta.json`

**Step 1: Update meta for each category**

| slug | title | h1 |
|------|-------|-----|
| glavnaya | Автохімія та автокосметика — купити, ціни \| Ultimate | Автохімія та автокосметика |
| moyka-i-eksterer | Мийка та екстер'єр — купити, ціни \| Ultimate | Мийка та екстер'єр |
| glina-i-avtoskraby | Глина та автоскраби — купити в інтернет-магазині Ultimate | Глина та автоскраби |
| gubki-i-varezhki | Губки та рукавички — купити в інтернет-магазині Ultimate | Губки та рукавички |
| mikrofibra-i-tryapki | Мікрофібра та ганчірки — купити в інтернет-магазині Ultimate | Мікрофібра та ганчірки |
| raspyliteli-i-penniki | Розпилювачі та піноутворювачі — купити, ціни \| Ultimate | Розпилювачі та піноутворювачі |
| vedra-i-emkosti | Відра та ємності — купити в інтернет-магазині Ultimate | Відра та ємності |
| kisti-dlya-deteylinga | Щітки та пензлі для детейлінгу — купити, ціни \| Ultimate | Щітки та пензлі для детейлінгу |
| keramika-i-zhidkoe-steklo | Кераміка та рідке скло — купити, ціни \| Ultimate | Кераміка та рідке скло |
| opt-i-b2b | Автохімія оптом — купити в інтернет-магазині Ultimate | Автохімія оптом |

**Step 2: Validate each file**

Run: `python3 scripts/validate_meta.py uk/categories/glavnaya/meta/glavnaya_meta.json`
Expected: `PASS`

---

## Task 6: Generate SQL migration

**Files:**
- Create: `data/generated/category_title_meta_update.sql`

**Step 1: Write SQL file**

```sql
-- Category Title Meta Update
-- Generated: 2026-02-03
-- Affects: 10 categories × 2 languages = 20 rows

-- BACKUP FIRST
-- SELECT category_id, language_id, meta_title, meta_h1, meta_description
-- FROM oc_category_description
-- WHERE category_id IN (468, 423, 453, 446, 447, 448, 495, 439, 493)
-- INTO OUTFILE '/tmp/meta_backup_20260203.csv';

-- =====================
-- RU Updates (language_id=3)
-- =====================

-- glavnaya (468 - это корневая, но мета хранится где?)
-- Нужно уточнить category_id для glavnaya

UPDATE oc_category_description SET
  meta_title = 'Автохимия и автокосметика — купить, цены | Ultimate',
  meta_h1 = 'Автохимия и автокосметика',
  meta_description = 'Автохимия и автокосметика от производителя Ultimate. Профессиональная химия для детейлинга и автомоек — шампуни, полироли, защитные покрытия. Опт и розница.'
WHERE category_id = 468 AND language_id = 3;

UPDATE oc_category_description SET
  meta_title = 'Глина и автоскрабы — купить в интернет-магазине Ultimate',
  meta_h1 = 'Глина и автоскрабы',
  meta_description = 'Глина и автоскрабы в интернет-магазине Ultimate. Глубокая очистка ЛКП — синяя, жёлтая глина, автоскрабы разной абразивности.'
WHERE category_id = 423 AND language_id = 3;

UPDATE oc_category_description SET
  meta_title = 'Губки и варежки — купить в интернет-магазине Ultimate',
  meta_h1 = 'Губки и варежки',
  meta_description = 'Губки и варежки в интернет-магазине Ultimate. Для ручной мойки авто — поролон, микрофибра, шерсть разных размеров.'
WHERE category_id = 453 AND language_id = 3;

UPDATE oc_category_description SET
  meta_title = 'Микрофибра и тряпки — купить в интернет-магазине Ultimate',
  meta_h1 = 'Микрофибра и тряпки',
  meta_description = 'Микрофибра и тряпки от производителя Ultimate. Для сушки, полировки, нанесения составов — плотность 300–1200 GSM. Опт и розница.'
WHERE category_id = 446 AND language_id = 3;

UPDATE oc_category_description SET
  meta_title = 'Распылители и пенники — купить, цены | Ultimate',
  meta_h1 = 'Распылители и пенники',
  meta_description = 'Распылители и пенники в интернет-магазине Ultimate. Триггеры, помповые распылители, пеногенераторы для бесконтактной мойки.'
WHERE category_id = 447 AND language_id = 3;

UPDATE oc_category_description SET
  meta_title = 'Вёдра и ёмкости — купить в интернет-магазине Ultimate',
  meta_h1 = 'Вёдра и ёмкости',
  meta_description = 'Вёдра и ёмкости в интернет-магазине Ultimate. Детейлинг-вёдра с сепараторами, мерные ёмкости, канистры 5–20л.'
WHERE category_id = 448 AND language_id = 3;

UPDATE oc_category_description SET
  meta_title = 'Щётки и кисти для детейлинга — купить, цены | Ultimate',
  meta_h1 = 'Щётки и кисти для детейлинга',
  meta_description = 'Щётки и кисти для детейлинга в интернет-магазине Ultimate. Для салона, дисков, кузова — мягкие и жёсткие, наборы и поштучно.'
WHERE category_id = 495 AND language_id = 3;

UPDATE oc_category_description SET
  meta_title = 'Керамика и жидкое стекло — купить, цены | Ultimate',
  meta_h1 = 'Керамика и жидкое стекло',
  meta_description = 'Керамика и жидкое стекло от производителя Ultimate. Защитные покрытия 9H — гидрофоб, блеск, защита от царапин до 3 лет. Опт и розница.'
WHERE category_id = 439 AND language_id = 3;

UPDATE oc_category_description SET
  meta_title = 'Автохимия оптом — купить в интернет-магазине Ultimate',
  meta_h1 = 'Автохимия оптом',
  meta_description = 'Автохимия оптом от производителя Ultimate. Скидки от объёма, быстрая отгрузка — для автомоек, детейлинг-студий, СТО. Опт и розница.'
WHERE category_id = 493 AND language_id = 3;

-- =====================
-- UK Updates (language_id=1)
-- =====================

UPDATE oc_category_description SET
  meta_title = 'Автохімія та автокосметика — купити, ціни | Ultimate',
  meta_h1 = 'Автохімія та автокосметика',
  meta_description = 'Автохімія та автокосметика від виробника Ultimate. Професійна хімія для детейлінгу та автомийок — шампуні, поліролі, захисні покриття. Опт і роздріб.'
WHERE category_id = 468 AND language_id = 1;

UPDATE oc_category_description SET
  meta_title = 'Глина та автоскраби — купити в інтернет-магазині Ultimate',
  meta_h1 = 'Глина та автоскраби',
  meta_description = 'Глина та автоскраби в інтернет-магазині Ultimate. Глибоке очищення ЛФП — синя, жовта глина, автоскраби різної абразивності.'
WHERE category_id = 423 AND language_id = 1;

UPDATE oc_category_description SET
  meta_title = 'Губки та рукавички — купити в інтернет-магазині Ultimate',
  meta_h1 = 'Губки та рукавички',
  meta_description = 'Губки та рукавички в інтернет-магазині Ultimate. Для ручної мийки авто — поролон, мікрофібра, шерсть різних розмірів.'
WHERE category_id = 453 AND language_id = 1;

UPDATE oc_category_description SET
  meta_title = 'Мікрофібра та ганчірки — купити в інтернет-магазині Ultimate',
  meta_h1 = 'Мікрофібра та ганчірки',
  meta_description = 'Мікрофібра та ганчірки від виробника Ultimate. Для сушіння, полірування, нанесення складів — щільність 300–1200 GSM. Опт і роздріб.'
WHERE category_id = 446 AND language_id = 1;

UPDATE oc_category_description SET
  meta_title = 'Розпилювачі та піноутворювачі — купити, ціни | Ultimate',
  meta_h1 = 'Розпилювачі та піноутворювачі',
  meta_description = 'Розпилювачі та піноутворювачі в інтернет-магазині Ultimate. Тригери, помпові розпилювачі, піногенератори для безконтактної мийки.'
WHERE category_id = 447 AND language_id = 1;

UPDATE oc_category_description SET
  meta_title = 'Відра та ємності — купити в інтернет-магазині Ultimate',
  meta_h1 = 'Відра та ємності',
  meta_description = 'Відра та ємності в інтернет-магазині Ultimate. Детейлінг-відра з сепараторами, мірні ємності, каністри 5–20л.'
WHERE category_id = 448 AND language_id = 1;

UPDATE oc_category_description SET
  meta_title = 'Щітки та пензлі для детейлінгу — купити, ціни | Ultimate',
  meta_h1 = 'Щітки та пензлі для детейлінгу',
  meta_description = 'Щітки та пензлі для детейлінгу в інтернет-магазині Ultimate. Для салону, дисків, кузова — м''які та жорсткі, набори та поштучно.'
WHERE category_id = 495 AND language_id = 1;

UPDATE oc_category_description SET
  meta_title = 'Кераміка та рідке скло — купити, ціни | Ultimate',
  meta_h1 = 'Кераміка та рідке скло',
  meta_description = 'Кераміка та рідке скло від виробника Ultimate. Захисні покриття 9H — гідрофоб, блиск, захист від подряпин до 3 років. Опт і роздріб.'
WHERE category_id = 439 AND language_id = 1;

UPDATE oc_category_description SET
  meta_title = 'Автохімія оптом — купити в інтернет-магазині Ultimate',
  meta_h1 = 'Автохімія оптом',
  meta_description = 'Автохімія оптом від виробника Ultimate. Знижки від об''єму, швидке відвантаження — для автомийок, детейлінг-студій, СТО. Опт і роздріб.'
WHERE category_id = 493 AND language_id = 1;
```

---

## Task 7: Verify category IDs

**Step 1: Check category_id mapping**

Run on server:
```bash
ssh user@server "mysql -u user -p -e \"
SELECT cd.category_id, c.parent_id, cd.meta_h1, cd.name
FROM oc_category_description cd
JOIN oc_category c ON c.category_id = cd.category_id
WHERE cd.language_id = 3
AND cd.name IN ('Мойка и Экстерьер', 'Глина и автоскрабы', 'Губки и варежки', 'Микрофибра и тряпки', 'Распылители и пенники', 'Ведра и емкости', 'Кисти для детейлинга', 'Керамика и жидкое стекло', 'Опт и B2B')
\" ultimate_db"
```

Expected: List of category_ids to verify mapping

**Step 2: Update SQL if needed**

If category_ids differ from plan, update `data/generated/category_title_meta_update.sql`

---

## Task 8: Execute SQL on server

**Step 1: Copy SQL to server**

Run: `scp data/generated/category_title_meta_update.sql user@server:/tmp/`
Expected: File copied

**Step 2: Create backup**

Run on server:
```bash
ssh user@server "mysql -u user -p -e \"
SELECT category_id, language_id, meta_title, meta_h1, meta_description
FROM oc_category_description
WHERE category_id IN (468, 423, 453, 446, 447, 448, 495, 439, 493)
\" ultimate_db > /tmp/meta_backup_20260203.tsv"
```

**Step 3: Execute migration**

Run: `ssh user@server "mysql -u user -p ultimate_db < /tmp/category_title_meta_update.sql"`
Expected: Query OK, 18 rows affected

**Step 4: Clear cache**

Run: `ssh user@server "rm -rf /var/www/ultimate/system/storage/cache/*"`
Expected: Cache cleared

---

## Task 9: Verify on site

**Step 1: Spot-check 3 categories**

Open in browser:
1. https://ultimate.net.ua/ — check Title = "Автохимия и автокосметика..."
2. https://ultimate.net.ua/glina-i-avtoskraby — check H1 = "Глина и автоскрабы"
3. https://ultimate.net.ua/uk/gubki-i-varezhki — check H1 = "Губки та рукавички"

**Step 2: View source to verify meta tags**

Check `<title>` and `<meta name="description">` match expected values

---

## Validation Checklist

- [ ] All 10 RU `_clean.json` have `category_title`
- [ ] All 10 UK `_clean.json` have `category_title`
- [ ] UK skill synced to v17.0
- [ ] All 10 RU `_meta.json` updated and validated
- [ ] All 10 UK `_meta.json` updated and validated
- [ ] SQL generated with correct category_ids
- [ ] Backup created on server
- [ ] SQL executed successfully
- [ ] Cache cleared
- [ ] Site verified (3 spot-checks passed)

---

**Version:** 1.0 — February 2026
