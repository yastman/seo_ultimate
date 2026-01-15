---
name: deploy-to-opencart
description: >-
    Deploy meta tags and content to OpenCart database for Ultimate.net.ua.
    Converts MD to HTML, generates SQL, executes via SSH.
    Use when: /deploy {slug}, залей на сайт, деплой мета, обнови на сайте.
---

# Deploy to OpenCart

Deploy meta tags and content to OpenCart database.

**Connection:** `ult` (SSH alias)
**Database:** `yastman_test`

---

## Input Validation

```text
Prerequisites:
- [ ] /quality-gate {slug} returned PASS
- [ ] categories/{slug}/QUALITY_REPORT.md shows PASS
- [ ] Both RU and UK versions validated

If not passed, run /quality-gate {slug} first.
```

---

## Quick Start

```bash
# 1. Check connection
ult 'echo Connected!'

# 2. Verify category in DB
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e \
  "SELECT category_id, language_id, name, meta_title \
   FROM oc_category_description WHERE category_id=412;"'

# 3. Deploy via SQL file
cat deploy/{slug}.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

---

## Workflow

### Step 1: Load Local Data

```bash
# RU meta + content
categories/{slug}/meta/{slug}_meta.json
categories/{slug}/content/{slug}_ru.md

# UK meta + content
uk/categories/{slug}/meta/{slug}_meta.json
uk/categories/{slug}/content/{slug}_uk.md
```

### Step 2: Find category_id

```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e \
  "SELECT category_id, language_id, name \
   FROM oc_category_description \
   WHERE name LIKE \"%keyword%\";"'
```

### Step 3: Convert MD → HTML

| Markdown     | HTML                                   |
| ------------ | -------------------------------------- |
| `# H1`       | (remove — goes to meta_h1)             |
| `## Heading` | `<h2>Heading</h2>`                     |
| `**bold**`   | `<strong>bold</strong>`                |
| `- item`     | `<ul><li>item</li></ul>`               |
| Table        | `<table class="table table-bordered">` |

```bash
python scripts/md_to_html.py categories/{slug}/content/{slug}_ru.md
```

### Step 4: Generate SQL

```sql
-- Deploy: {slug} (category_id={ID})

-- RU (language_id=3)
UPDATE oc_category_description SET
  meta_title = '{title_ru}',
  meta_description = '{description_ru}',
  meta_h1 = '{h1_ru}',
  description = '{html_content_ru}'
WHERE category_id = {ID} AND language_id = 3;

-- UK (language_id=1)
UPDATE oc_category_description SET
  meta_title = '{title_uk}',
  meta_description = '{description_uk}',
  meta_h1 = '{h1_uk}',
  description = '{html_content_uk}'
WHERE category_id = {ID} AND language_id = 1;
```

Save to `deploy/{slug}.sql`

### Step 5: Deploy

```bash
cat deploy/{slug}.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

### Step 6: Verify

```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e \
  "SELECT category_id, language_id, meta_title, meta_h1, \
   LENGTH(description) as content_len \
   FROM oc_category_description \
   WHERE category_id={ID};"'
```

---

## Category Mapping

| Slug               | ID  | Name RU                  |
| ------------------ | --- | ------------------------ |
| dlya-ruchnoy-moyki | 412 | Шампуни для ручной мойки |
| aktivnaya-pena     | 415 | Активная пена            |
| ochistiteli-stekol | 418 | Очиститель стекол        |
| ochistiteli-diskov | 419 | Средства для дисков      |
| ochistiteli-shin   | 420 | Средства для шин         |
| cherniteli-shin    | 421 | Для пластика и резины    |
| glina-i-avtoskraby | 423 | Глина и автоскрабы       |

**Language IDs:**

-   `language_id=1` → Українська (UK)
-   `language_id=3` → Русский (RU)

---

## Safety Rules

1. **SELECT before UPDATE** — always verify what will change
2. **Escape quotes** — `'` → `\'` in SQL strings
3. **Verify after UPDATE** — check result
4. **One category at a time** — no mass updates

---

## Output

```
deploy/{slug}.sql (SQL file)

Report:
✅ Deployed: {slug} (category_id={ID})

| Lang | meta_title | meta_h1 | content |
|------|------------|---------|---------|
| UK (1) | ✅ {title} | ✅ {h1} | {N} chars |
| RU (3) | ✅ {title} | ✅ {h1} | {N} chars |
```

---

## Troubleshooting

| Problem           | Solution                               |
| ----------------- | -------------------------------------- |
| Access denied     | Use `sudo mysql -u root -pfr1daYTw1st` |
| No database       | Add database name: `yastman_test`      |
| Quote errors      | Escape: `'` → `\'`                     |
| Connection failed | Check SSH: `ult 'echo test'`           |

---

**Version:** 3.0 — January 2026
**Connection:** `ult` = `ssh -i ~/.ssh/server_key_new -p 41229 admin@193.169.188.9`
