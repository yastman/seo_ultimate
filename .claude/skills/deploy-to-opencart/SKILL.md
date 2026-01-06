---
name: deploy-to-opencart
description: Deploy SEO meta tags and content to Ultimate.net.ua OpenCart database via VPS. Updates category descriptions, titles, H1, HTML content. Use when you see /deploy, залей на сайт, деплой мета, обнови на сайте.
---

# Deploy to OpenCart — Ultimate.net.ua

Deploy meta tags and content to OpenCart database.

**Supporting files:**

- [DB_REFERENCE.md](DB_REFERENCE.md) — Category mapping, schema details

**Connection:** `ult` (SSH alias)
**Database:** `yastman_test`

---

## Input Validation

Before deployment, verify:

```
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

See [DB_REFERENCE.md](DB_REFERENCE.md) for known category IDs.

### Step 3: Convert MD → HTML

| Markdown | HTML |
|----------|------|
| `# H1` | (remove — goes to meta_h1) |
| `## Heading` | `<h2>Heading</h2>` |
| `### Sub` | `<h3>Sub</h3>` |
| `**bold**` | `<strong>bold</strong>` |
| `- item` | `<ul><li>item</li></ul>` |
| Table | `<table class="table table-bordered">` |

Use script:

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

| Slug | ID | Name RU | Name UK |
|------|-----|---------|---------|
| dlya-ruchnoy-moyki | 412 | Шампуни для ручной мойки | Шампуні для ручного миття |
| aktivnaya-pena | 415 | Активная пена | Активна піна |
| ochistiteli-stekol | 418 | Очиститель стекол | Очисник скла |
| ochistiteli-diskov | 419 | Средства для дисков | Засоби для дисків |
| ochistiteli-shin | 420 | Средства для шин | Засоби для шин |
| cherniteli-shin | 421 | Для пластика и резины | Для пластику та гуми |
| glina-i-avtoskraby | 423 | Глина и автоскрабы | Глина та автоскраби |

**Language IDs:**

- `language_id=1` → Українська (UK)
- `language_id=3` → Русский (RU)

---

## Safety Rules

1. **SELECT before UPDATE** — always verify what will change
2. **Escape quotes** — `'` → `\'` in SQL strings
3. **Verify after UPDATE** — check result
4. **One category at a time** — no mass updates
5. **Backup first** — for critical changes

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

| Problem | Solution |
|---------|----------|
| Access denied | Use `sudo mysql -u root -pfr1daYTw1st` |
| No database | Add database name: `yastman_test` |
| Quote errors | Escape: `'` → `\'` |
| Connection failed | Check SSH: `ult 'echo test'` |

---

**Version:** 3.0 — December 2025 (with input validation)
**Connection:** `ult` = `ssh -i ~/.ssh/server_key_new -p 41229 admin@193.169.188.9`
