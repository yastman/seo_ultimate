---
name: category-init
description: Use when you see /category-init, создай категорию, инициализируй категорию, новая категория, подготовь папку для категории. (project)
---

# Category Init v3.0

Initialize new category folder + minimal data for SEO content pipeline.

Цель: чтобы категория была готова к следующему шагу `/generate-meta {slug}` и дальнейшему `/seo-research` и `/content-generator`.

---

## Source of truth (SSOT)

Единственный источник правды по семантике и структуре — `Структура _Ultimate.csv` (см. `docs/WORKFLOW_SEMANTICS.md`).

Если ты добавляешь новую категорию или меняешь ключи — сначала правь CSV, затем запускай:

```bash
python3 scripts/fix_csv_structure.py
python3 scripts/csv_to_readable_md.py
```

Чеклисты задач генерируются из `data/generated/STRUCTURE.md`:
`python3 scripts/generate_checklists.py`

---

## Workflow

### Step 1: Validate Input

```
Input: slug (e.g., "aktivnaya-pena", "cherniteli-shin")
Validate:
- slug is kebab-case (lowercase, hyphens)
- slug exists in Структура _Ultimate.csv (SSOT)
- folder categories/{slug}/ exists or can be created
```

### Step 2: Ensure checklist exists (recommended)

Проверь, что есть `tasks/categories/{slug}.md`.

Если файла нет — сгенерируй чеклисты:

```bash
python3 scripts/generate_checklists.py
```

После генерации открой `tasks/categories/{slug}.md` и проверь секцию Keywords (ключи + volume).

### Step 3: Create category folders

Создай структуру папок категории:

```text
categories/{slug}/
  data/
  meta/
  content/
  research/
```

### Step 4: Create or refresh `data/{slug}_clean.json`

#### Режим A (recommended): из чеклистов

Запусти инициализацию данных из `tasks/categories/*.md`:

```bash
python3 scripts/init_categories_from_checklists.py
```

Этот скрипт создаёт/обновляет `categories/{slug}/data/{slug}_clean.json` (и другие категории тоже).

#### Режим B (manual): вручную (если нужен точечный init)

Создай `categories/{slug}/data/{slug}_clean.json` в формате проекта (list-схема):

```json
{
  "id": "{slug}",
  "name": "{Category Name}",
  "type": "category",
  "parent_id": "{parent_slug}",
  "keywords": [
    {"keyword": "вч ключ 1", "volume": 1000},
    {"keyword": "вч ключ 2", "volume": 800}
  ],
  "synonyms": [
    {"keyword": "вариант формулировки", "volume": 120},
    {"keyword": "купить ...", "volume": 90, "use_in": "meta_only"}
  ],
  "entities": ["тип товара", "форма", "объём", "материал"],
  "micro_intents": ["как выбрать", "как использовать", "ошибки"],
  "source": "manual"
}
```

**Правила:**
- `keywords[0]` = primary keyword (макс volume) для Title/H1/Description.
- `synonyms` с `use_in: "meta_only"` — только для мета (не в H1 и не в body).

### Step 5: Create templates (stubs)

Создай минимальные шаблоны, чтобы пайплайн был непрерывным:

**meta/{slug}_meta.json**

```json
{"slug": "{slug}", "language": "ru", "meta": {"title": "", "description": ""}, "h1": "", "status": "template"}
```

**content/{slug}_ru.md**

```markdown
# {H1}

<!-- Status: DRAFT -->
```

**research/RESEARCH_DATA.md**

```markdown
# Research: {slug}

## Status: PENDING
```

### Step 6: Validate output

Check:

- [ ] JSON is valid
- [ ] `categories/{slug}/data/{slug}_clean.json` содержит `keywords` (list)
- [ ] `keywords[0].keyword` заполнен (primary keyword)
- [ ] `synonyms` с `use_in: "meta_only"` не будут использоваться в H1/тексте
- [ ] Папки `meta/ content/ research/` существуют
- [ ] Созданы stub-файлы (meta/content/research)

---

## Output

```
categories/{slug}/
  - data/{slug}_clean.json (keywords + optional synonyms/entities/micro_intents)
  - meta/{slug}_meta.json (template/stub)
  - content/{slug}_ru.md (stub)
  - research/RESEARCH_DATA.md (stub)

Status: ready for /generate-meta
```

---

## Next Step

After category-init, run `/generate-meta {slug}` to generate meta tags.

---

**Version:** 3.0 — January 2026
**Change:** Align category-init with current project SSOT + scripts (`generate_checklists.py`, `init_categories_from_checklists.py`) and list-schema `_clean.json`.
