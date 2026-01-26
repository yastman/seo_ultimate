---
name: uk-deploy-to-opencart
description: >-
  Деплой UK мета-тегів та контенту в OpenCart. Оновлює language_id=1 (українська).
  Use when /uk-deploy, залий UK на сайт, деплой UK мета, оновити UK на сайті.
---

# UK Deploy to OpenCart — Ultimate.net.ua

Деплой UK мета-тегів та контенту в OpenCart (language_id=1).

**Supporting files:**

- [../deploy-to-opencart/DB_REFERENCE.md](../deploy-to-opencart/DB_REFERENCE.md) — Category mapping, schema details

**Connection:** `ult` (SSH alias)
**Database:** `yastman_test`

---

## Input Validation

Before deployment, verify:

```
Prerequisites:
- [ ] /uk-quality-gate {slug} returned PASS
- [ ] uk/categories/{slug}/QUALITY_REPORT.md shows PASS

If not passed, run /uk-quality-gate {slug} first.
```

---

## Quick Start

```bash
# 1. Check connection
ult 'echo Connected!'

# 2. Verify category in DB (UK = language_id=1)
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e \
  "SELECT category_id, language_id, name, meta_title \
   FROM oc_category_description WHERE category_id=412 AND language_id=1;"'

# 3. Deploy via SQL file
cat deploy/uk/{slug}.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

---

## Workflow

### Step 1: Load Local Data

```bash
# UK meta + content
uk/categories/{slug}/meta/{slug}_meta.json
uk/categories/{slug}/content/{slug}_uk.md
```

### Step 2: Find category_id

```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e \
  "SELECT category_id, language_id, name \
   FROM oc_category_description \
   WHERE name LIKE \"%keyword%\" AND language_id=1;"'
```

See [../deploy-to-opencart/DB_REFERENCE.md](../deploy-to-opencart/DB_REFERENCE.md) for known category IDs.

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
python3 scripts/md_to_html.py uk/categories/{slug}/content/{slug}_uk.md
```

### Step 4: Generate SQL

```sql
-- UK Deploy: {slug} (category_id={ID})
-- Language: Українська (language_id=1)

UPDATE oc_category_description SET
  meta_title = '{title_uk}',
  meta_description = '{description_uk}',
  meta_h1 = '{h1_uk}',
  description = '{html_content_uk}'
WHERE category_id = {ID} AND language_id = 1;
```

Save to `deploy/uk/{slug}.sql`

### Step 5: Deploy

```bash
mkdir -p deploy/uk
cat deploy/uk/{slug}.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```

### Step 6: Verify

```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e \
  "SELECT category_id, language_id, meta_title, meta_h1, \
   LENGTH(description) as content_len \
   FROM oc_category_description \
   WHERE category_id={ID} AND language_id=1;"'
```

---

## Language ID Reference

| Language | language_id | Used for |
|----------|-------------|----------|
| Українська (UK) | **1** | This skill |
| Русский (RU) | 3 | Use /deploy-to-opencart |

---

## Category Mapping

| Slug | ID | Name UK |
|------|-----|---------|
| dlya-ruchnoy-moyki | 412 | Шампуні для ручного миття |
| aktivnaya-pena | 415 | Активна піна |
| ochistiteli-stekol | 418 | Очисник скла |
| ochistiteli-diskov | 419 | Засоби для дисків |
| ochistiteli-shin | 420 | Засоби для шин |
| cherniteli-shin | 421 | Для пластику та гуми |
| glina-i-avtoskraby | 423 | Глина та автоскраби |

---

## Safety Rules

1. **SELECT before UPDATE** — always verify what will change
2. **Escape quotes** — `'` → `\'` in SQL strings
3. **Verify after UPDATE** — check result
4. **One category at a time** — no mass updates
5. **language_id=1 ONLY** — this skill is UK-only

---

## Output

```
deploy/uk/{slug}.sql (SQL file)

Report:
✅ Deployed UK: {slug} (category_id={ID})

| Lang | meta_title | meta_h1 | content |
|------|------------|---------|---------|
| UK (1) | ✅ {title} | ✅ {h1} | {N} chars |
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Access denied | Use `sudo mysql -u root -pfr1daYTw1st` |
| No database | Add database name: `yastman_test` |
| Quote errors | Escape: `'` → `\'` |
| Connection failed | Check SSH: `ult 'echo test'` |
| Wrong language | Verify `language_id=1` in WHERE clause |

---

**Version:** 3.0 — January 2026

**Changelog v3.0:**
- **Синхронізовано з RU deploy-to-opencart v3.0** — повний паритет
- Версія оновлена з 1.0 до 3.0 для відповідності RU нумерації

**Connection:** `ult` = `ssh -i ~/.ssh/server_key_new -p 41229 admin@193.169.188.9`
