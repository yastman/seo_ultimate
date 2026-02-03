# Category Title Meta Update — Design Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Добавить поле `category_title` в `_clean.json` для категорий с составными названиями, перегенерировать мета-теги, обновить в БД OpenCart.

**Architecture:**
1. Идентифицировать категории требующие `category_title`
2. Обновить `_clean.json` файлы (RU + UK)
3. Синхронизировать UK скилл с RU
4. Перегенерировать мета через скилл
5. Сгенерировать SQL и выполнить на сервере

**Tech Stack:** JSON files, generate-meta skill, SSH + MySQL

---

## Phase 1: Identify Categories

### Критерии для `category_title`:

1. **Составная категория** — slug содержит "-i-" (и)
2. **Два сильных ВЧ-ключа** — нужно охватить оба в Title
3. **Название категории ≠ ВЧ-ключ** — Menu Name из OpenCart отличается от primary_keyword

### RU категории с "-i-" в slug (составные):

| slug | Menu Name (OpenCart) | Текущий primary_keyword | category_title |
|------|---------------------|------------------------|----------------|
| moyka-i-eksterer | Мойка и Экстерьер | — | Мойка и экстерьер |
| glina-i-avtoskraby | Глина и автоскрабы | глина для авто | Глина и автоскрабы |
| gubki-i-varezhki | Губки и варежки | мочалка для авто | Губки и варежки |
| mikrofibra-i-tryapki | Микрофибра и тряпки | микрофибра для авто | Микрофибра и тряпки |
| raspyliteli-i-penniki | Распылители и пенники | пенник для мойки авто | Распылители и пенники |
| vedra-i-emkosti | Вёдра и ёмкости | ведро для мойки авто | Вёдра и ёмкости |
| keramika-i-zhidkoe-steklo | Керамика и жидкое стекло | жидкое стекло для авто | Керамика и жидкое стекло |
| opt-i-b2b | Опт и B2B | автохимия опт | Автохимия оптом |

### RU категории с двумя ВЧ-ключами:

| slug | keyword 1 (vol) | keyword 2 (vol) | category_title |
|------|-----------------|-----------------|----------------|
| glavnaya | автохимия (2400) | автокосметика (480) | Автохимия и автокосметика |

### RU категории где название ≠ ВЧ:

| slug | Menu Name | primary_keyword | category_title |
|------|-----------|-----------------|----------------|
| kisti-dlya-deteylinga | Кисти для детейлинга | щетка для детейлинга (210) | Щётки и кисти для детейлинга |
| shchetka-dlya-moyki-avto | Щётка для мойки авто | щётка для мойки авто (260) | — (ВЧ совпадает) |

---

## Phase 2: Update _clean.json Files

### Task 2.1: RU categories (10 files)

```
categories/glavnaya/data/glavnaya_clean.json
  + "category_title": "Автохимия и автокосметика"

categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json
  + "category_title": "Мойка и экстерьер"

categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json
  + "category_title": "Глина и автоскрабы"

categories/aksessuary/gubki-i-varezhki/data/gubki-i-varezhki_clean.json
  + "category_title": "Губки и варежки"

categories/aksessuary/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json
  + "category_title": "Микрофибра и тряпки"

categories/aksessuary/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json
  + "category_title": "Распылители и пенники"

categories/aksessuary/vedra-i-emkosti/data/vedra-i-emkosti_clean.json
  + "category_title": "Вёдра и ёмкости"

categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json
  + "category_title": "Щётки и кисти для детейлинга"

categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json
  + "category_title": "Керамика и жидкое стекло"

categories/opt-i-b2b/data/opt-i-b2b_clean.json
  + "category_title": "Автохимия оптом"
```

### Task 2.2: UK categories (10 files)

```
uk/categories/glavnaya/data/glavnaya_clean.json
  + "category_title": "Автохімія та автокосметика"

uk/categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json
  + "category_title": "Мийка та екстер'єр"

uk/categories/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json
  + "category_title": "Глина та автоскраби"

uk/categories/gubki-i-varezhki/data/gubki-i-varezhki_clean.json
  + "category_title": "Губки та рукавички"

uk/categories/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json
  + "category_title": "Мікрофібра та ганчірки"

uk/categories/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json
  + "category_title": "Розпилювачі та піноутворювачі"

uk/categories/vedra-i-emkosti/data/vedra-i-emkosti_clean.json
  + "category_title": "Відра та ємності"

uk/categories/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json
  + "category_title": "Щітки та пензлі для детейлінгу"

uk/categories/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json
  + "category_title": "Кераміка та рідке скло"

uk/categories/opt-i-b2b/data/opt-i-b2b_clean.json
  + "category_title": "Автохімія оптом"
```

---

## Phase 3: Sync UK Skill

### Task 3.1: Update uk-generate-meta SKILL.md

Добавить секцию `category_title` аналогично RU скиллу (v17.0):
- Определение `category_title`
- Приоритет над `primary_keyword`
- Примеры UK

---

## Phase 4: Regenerate Meta

### Task 4.1: RU meta regeneration (10 categories)

Для каждой категории:
```bash
# Валидация после ручного обновления _meta.json:
python3 scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json
```

### Task 4.2: UK meta regeneration (10 categories)

```bash
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
```

---

## Phase 5: Generate SQL & Deploy

### Task 5.1: Generate SQL for RU (language_id=3)

```sql
-- RU Meta Updates (language_id=3)
UPDATE oc_category_description
SET meta_title = 'Автохимия и автокосметика — купить, цены | Ultimate',
    meta_h1 = 'Автохимия и автокосметика',
    meta_description = 'Автохимия и автокосметика от производителя Ultimate. Профессиональная химия для детейлинга и автомоек. Опт и розница.'
WHERE category_id = 468 AND language_id = 3;

-- ... (остальные 9 категорий)
```

### Task 5.2: Generate SQL for UK (language_id=1)

```sql
-- UK Meta Updates (language_id=1)
UPDATE oc_category_description
SET meta_title = 'Автохімія та автокосметика — купити, ціни | Ultimate',
    meta_h1 = 'Автохімія та автокосметика',
    meta_description = 'Автохімія та автокосметика від виробника Ultimate. Професійна хімія для детейлінгу та автомийок. Опт і роздріб.'
WHERE category_id = 468 AND language_id = 1;

-- ... (остальные 9 категорий)
```

### Task 5.3: Execute on server

```bash
ssh user@ultimate.net.ua "mysql -u user -p ultimate_db < /tmp/meta_update.sql"
```

### Task 5.4: Clear cache

```bash
ssh user@ultimate.net.ua "rm -rf /var/www/ultimate/system/storage/cache/*"
```

---

## Category ID Mapping

| slug | category_id | RU language_id | UK language_id |
|------|-------------|----------------|----------------|
| glavnaya | 468 | 3 | 1 |
| moyka-i-eksterer | 468 | 3 | 1 |
| glina-i-avtoskraby | 423 | 3 | 1 |
| gubki-i-varezhki | 453 | 3 | 1 |
| mikrofibra-i-tryapki | 446 | 3 | 1 |
| raspyliteli-i-penniki | 447 | 3 | 1 |
| vedra-i-emkosti | 448 | 3 | 1 |
| kisti-dlya-deteylinga | 495 | 3 | 1 |
| keramika-i-zhidkoe-steklo | 439 | 3 | 1 |
| opt-i-b2b | 493 | 3 | 1 |

---

## Validation Checklist

- [ ] All `_clean.json` have `category_title` field
- [ ] All `_meta.json` pass `validate_meta.py`
- [ ] UK skill synced to v17.0
- [ ] SQL generated with correct category_id
- [ ] SQL executed on server
- [ ] Cache cleared
- [ ] Site verified (spot-check 3 categories)

---

## Rollback Plan

```sql
-- Backup current values before update
SELECT category_id, meta_title, meta_h1, meta_description
FROM oc_category_description
WHERE category_id IN (468, 423, 453, 446, 447, 448, 495, 439, 493)
INTO OUTFILE '/tmp/meta_backup.csv';
```

---

**Version:** 1.0 — February 2026
