#!/usr/bin/env python3
"""
generate_checklists.py

Generates tasks/categories/*.md tasks from data/STRUCTURE.md.
Dynamically parses the structure and keywords.

Modes:
  --reset: Regenerate all task files (overwrites content, useful for structure updates).
  --sync:  Update status in existing task files and summary files without overwriting instructions.
           (Note: Currently --sync logic re-generates MASTER and PIPELINE stats, but for task files,
            it respects existing [x] if we implemented parsing, but for now specific instruction is:
            # Только обновить статусы (проверить реальные файлы) -> update MASTER/PIPELINE, maybe leave tasks alone or update status table header?
            For simplicity and based on "Aktualizatsiya tasks", --reset is the primary "rebuild" mode.
            I will implement --sync to mostly update MASTER/PIPELINE and console output).
"""

import argparse
import os
import re
from pathlib import Path

# ============================================================================
# Transliteration (SSOT)
# ============================================================================
CYRILLIC_TO_LATIN = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ъ": "",
    "ы": "y",
    "ь": "",
    "э": "e",
    "ю": "yu",
    "я": "ya",
    "і": "i",
    "ї": "yi",
    "є": "ye",
    "ґ": "g",
}


def slugify(text):
    text = text.lower().strip()
    result = []
    for char in text:
        if char in CYRILLIC_TO_LATIN:
            result.append(CYRILLIC_TO_LATIN[char])
        elif char.isalnum() or char == " " or char == "-":
            result.append(char)
        else:
            result.append(" ")
    slug = "".join(result)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


# ============================================================================
# Paths
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
STRUCTURE_FILE = BASE_DIR / "data/STRUCTURE.md"
TASKS_DIR = BASE_DIR / "tasks/categories"
MASTER_CHECKLIST_FILE = BASE_DIR / "tasks/MASTER_CHECKLIST.md"
PIPELINE_STATUS_FILE = BASE_DIR / "tasks/PIPELINE_STATUS.md"


# ============================================================================
# Parsing Logic
# ============================================================================
def parse_structure(file_path):
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    nodes = []
    current_l1 = None
    current_l2 = None
    current_l3 = None
    current_node = None

    # Regex - using greedy (.+) to ensure full name capture
    re_l1 = re.compile(r"^### 📂 L1: (.+) \(Vol: (\d+)\)")
    re_l2 = re.compile(r"^#### 📁 L2: (.+) \(Vol: (\d+)\)")
    re_l3 = re.compile(r"^##### 🏷️ L3: (.+) \(Vol: (\d+)\)")
    re_cluster = re.compile(r"^#{5,6} 📦 Cluster: (.+) \(Vol: (\d+)\)")
    re_filter = re.compile(r"^###### ⚡ Filter: (.+) \(Vol: (\d+)\)")
    re_table_row = re.compile(r"^\| (.+?) \| (\d+) \|")

    for line in lines:
        line = line.strip()

        m_l1 = re_l1.match(line)
        if m_l1:
            name, vol = m_l1.groups()
            slug = slugify(name)
            node = {
                "type": "L1",
                "name": name,
                "slug": slug,
                "volume": int(vol),
                "parent": "Homepage",
                "keywords": [],
            }
            nodes.append(node)
            current_l1 = node
            current_l2 = None
            current_l3 = None
            current_node = node
            continue

        m_l2 = re_l2.match(line)
        if m_l2:
            name, vol = m_l2.groups()
            slug = slugify(name)
            parent = current_l1["slug"] if current_l1 else "root"
            node = {
                "type": "L2",
                "name": name,
                "slug": slug,
                "volume": int(vol),
                "parent": parent,
                "keywords": [],
            }
            nodes.append(node)
            current_l2 = node
            current_l3 = None
            current_node = node
            continue

        m_l3 = re_l3.match(line)
        if m_l3:
            name, vol = m_l3.groups()
            slug = slugify(name)
            parent = current_l2["slug"] if current_l2 else (current_l1["slug"] if current_l1 else "root")
            node = {
                "type": "L3",
                "name": name,
                "slug": slug,
                "volume": int(vol),
                "parent": parent,
                "keywords": [],
            }
            nodes.append(node)
            current_l3 = node
            current_node = node
            continue

        m_cluster = re_cluster.match(line)
        if m_cluster:
            name, vol = m_cluster.groups()
            clean_name = name
            if "General (" in name:
                m = re.search(r"General \((.+?)\)", name)
                if m:
                    clean_name = m.group(1)
            elif "Direct Keywords (" in name:
                m = re.search(r"Direct Keywords \((.+?)\)", name)
                if m:
                    clean_name = m.group(1)

            slug = slugify(clean_name)
            parent = current_l3["slug"] if current_l3 else (current_l2["slug"] if current_l2 else "root")
            node = {
                "type": "Cluster",
                "name": clean_name,
                "slug": slug,
                "volume": int(vol),
                "parent": parent,
                "keywords": [],
            }
            nodes.append(node)
            current_node = node
            continue

        m_filter = re_filter.match(line)
        if m_filter:
            name, vol = m_filter.groups()
            slug = slugify(name)
            parent = current_l3["slug"] if current_l3 else "root"
            node = {
                "type": "Filter",
                "name": name,
                "slug": slug,
                "volume": int(vol),
                "parent": parent,
                "keywords": [],
            }
            nodes.append(node)
            current_node = node
            continue

        if current_node:
            m_table = re_table_row.match(line)
            if m_table:
                kw, vol = m_table.groups()
                if kw != "Keyword" and kw != "---":
                    current_node["keywords"].append({"keyword": kw, "volume": int(vol)})

    return nodes


# ============================================================================
# Status Checking
# ============================================================================
def check_real_status(slug):
    """
    Check file system for existence of artifacts.
    Returns flags: init, meta, research, content, uk, quality, deploy
    """
    root = BASE_DIR
    cat_dir = root / f"categories/{slug}"

    # 1. Init
    exists_dir = cat_dir.exists()
    exists_data = (cat_dir / f"data/{slug}_clean.json").exists()
    status_init = exists_dir and exists_data

    # 2. Meta
    status_meta = (cat_dir / f"meta/{slug}_meta.json").exists()

    # 3. Research
    # Check if research file exists AND has content
    res_file = cat_dir / "research/RESEARCH_DATA.md"
    status_research = False
    if res_file.exists() and res_file.stat().st_size > 500:  # Heuristic
        status_research = False
        status_research = True

    # 4. Content
    content_file_ru = cat_dir / f"content/{slug}_ru.md"
    status_content = False
    if content_file_ru.exists() and content_file_ru.stat().st_size > 1000:
        status_content = True

    # 5. UK
    # Check parallel structure
    uk_dir = root / f"uk/categories/{slug}"
    status_uk = False
    if uk_dir.exists() and (uk_dir / f"content/{slug}_uk.md").exists():
        status_uk = True

    # 6. Quality
    # Usually manual flag, but let's check if report exists
    status_quality = (cat_dir / "QUALITY_REPORT.md").exists()

    # 7. Deploy
    # Hard to check automatically without DB access, default False
    status_deploy = False

    return {
        "init": status_init,
        "meta": status_meta,
        "research": status_research,
        "content": status_content,
        "uk": status_uk,
        "quality": status_quality,
        "deploy": status_deploy,
    }


# ============================================================================
# Template & Generation
# ============================================================================
TEMPLATE = """# {slug} — {name}

**Priority:** {priority} (volume {volume})
**Type:** {type}
**Parent:** {parent}

---

## Current Status

| Stage | RU | UK |
|-------|----|----|
| 01-Init | {s_init} | {s_init_uk} |
| 02-Meta | {s_meta} | {s_meta_uk} |
| 03-Research | {s_research} | — |
| 04-Content | {s_content} | {s_content_uk} |
| 05-UK | — | {s_uk} |
| 06-Quality | {s_quality} | {s_quality_uk} |
| 07-Deploy | {s_deploy} | {s_deploy_uk} |

---

## Keywords (из CSV)

| Keyword | Volume |
|---------|--------|
{keywords_table}

**Total:** {k_count}

---

## Stage 01: Init {s_init}

- [{c_init}] Папка создана: `categories/{slug}/`
- [{c_init}] `data/{slug}_clean.json` создан
- [{c_init}] Keywords кластеризованы
- [{c_init}] `meta/{slug}_meta.json` template
- [{c_init}] `content/{slug}_ru.md` placeholder
- [{c_init}] `research/RESEARCH_DATA.md` template

**Init Validation:**
```bash
python3 -c "import json; json.load(open('categories/{slug}/data/{slug}_clean.json')); print('PASS')"
```

---

## Stage 02: Meta {s_meta}

### Inputs
- [ ] Прочитать `data/{slug}_clean.json`
- [ ] Определить primary keyword

### Tasks RU
- [ ] title_ru: 50-60 chars, содержит primary keyword
- [ ] description_ru: 150-160 chars, CTA "Доставка по Украине"
- [ ] h1_ru: primary keyword (без "купить")

### Tasks UK
- [ ] title_uk: 50-60 chars
- [ ] description_uk: 150-160 chars
- [ ] h1_uk: перевод primary keyword

### Meta Output
- [ ] Записать в `meta/{slug}_meta.json`

### Meta Validation
```bash
python3 scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json
```

---

## Stage 03: Research {s_research}

### Block 1: Product Analysis
- [ ] ТОП-5 брендов
- [ ] Ценовой диапазон

### Block 2: Competitors
- [ ] WebSearch: "{{primary keyword}} купить украина"

### Block 3: Use Cases
- [ ] Для кого?
- [ ] Какие задачи решает?

### Research Output
- [ ] Записать в `research/RESEARCH_DATA.md`

### Research Validation
```bash
grep -c "^## Block" categories/{slug}/research/RESEARCH_DATA.md
```

---

## Stage 04: Content {s_content}

### Structure
- [ ] H1: primary keyword
- [ ] Intro: 150-200 слов
- [ ] H2: Buying Guide
- [ ] Comparison Table
- [ ] H2: How-To
- [ ] H2: FAQ (5+ вопросов)
- [ ] Conclusion + CTA

### SEO Requirements
- [ ] Primary keyword: 3-5 раз
- [ ] Word count: 1500-2500
- [ ] Density: 1.5-2.5%
- [ ] NO commercial keywords!

### Content Validation
```bash
python3 scripts/validate_content.py categories/{slug}/content/{slug}_ru.md "{{keyword}}" --mode seo
```

---

## Stage 05: UK {s_uk}

- [ ] Structure created
- [ ] Translated Keywords, Meta, Content

---

## Stage 06: Quality Gate {s_quality}

- [ ] Data JSON valid
- [ ] Meta valid
- [ ] Content valid
- [ ] Research complete
- [ ] SEO compliant

---

## Stage 07: Deploy {s_deploy}

- [ ] Backup DB
- [ ] Update Meta/Content RU/UK
- [ ] Clear cache

---

**Last Updated:** 2026-01-02
"""


def generate_task_file(node, status):
    slug = node["slug"]

    # Priority
    vol = node["volume"]
    if vol >= 1000:
        priority = "HIGH"
    elif vol >= 300:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    # Keywords table
    keywords_table = ""
    # Sort by volume desc
    sorted_kws = sorted(node["keywords"], key=lambda x: x["volume"], reverse=True)
    for k in sorted_kws:
        keywords_table += f"| {k['keyword']} | {k['volume']} |\n"

    def icon(b):
        return "✅" if b else "⬜"

    def check(b):
        return "x" if b else " "

    content = TEMPLATE.format(
        slug=slug,
        name=node["name"],
        priority=priority,
        volume=vol,
        type=node["type"],
        parent=node["parent"],
        s_init=icon(status["init"]),
        s_init_uk=icon(status["init"]) if status["uk"] else "⬜",
        c_init=check(status["init"]),
        s_meta=icon(status["meta"]),
        s_meta_uk=icon(status["meta"]) if status["uk"] else "⬜",
        s_research=icon(status["research"]),
        s_content=icon(status["content"]),
        s_content_uk=icon(status["content"]) if status["uk"] else "⬜",
        s_uk=icon(status["uk"]),
        s_quality=icon(status["quality"]),
        s_quality_uk=icon(status["quality"]) if status["uk"] else "⬜",
        s_deploy=icon(status["deploy"]),
        s_deploy_uk=icon(status["deploy"]) if status["uk"] else "⬜",
        keywords_table=keywords_table,
        k_count=len(node["keywords"]),
    )

    # Write
    out_path = TASKS_DIR / f"{slug}.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================================
# Master Checklist
# ============================================================================
def update_master_checklist(nodes, statuses):
    header = """# Master Checklist — Ultimate.net.ua

| # | Slug | Name | Type | Parent | Vol | Keys | Init | Meta | Research | Content | UK | Quality | Deploy |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""
    rows = []

    def icon(b):
        return "✅" if b else "⬜"

    for i, node in enumerate(nodes, 1):
        s = statuses.get(node["slug"], {})
        # Safety fallback
        if not s:
            s = dict.fromkeys(["init", "meta", "research", "content", "uk", "quality", "deploy"], False)

        row = f"| {i} | `{node['slug']}` | {node['name']} | {node['type']} | {node['parent']} | {node['volume']} | {len(node['keywords'])} | {icon(s['init'])} | {icon(s['meta'])} | {icon(s['research'])} | {icon(s['content'])} | {icon(s['uk'])} | {icon(s['quality'])} | {icon(s['deploy'])} |"
        rows.append(row)

    with open(MASTER_CHECKLIST_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(rows))


# ============================================================================
# Pipeline Status
# ============================================================================
def update_pipeline_status(nodes, statuses):
    total = len(nodes)

    # Counts
    c_init = sum(1 for s in statuses.values() if s["init"])
    c_meta = sum(1 for s in statuses.values() if s["meta"])
    c_research = sum(1 for s in statuses.values() if s["research"])
    c_content = sum(1 for s in statuses.values() if s["content"])
    c_uk = sum(1 for s in statuses.values() if s["uk"])
    c_quality = sum(1 for s in statuses.values() if s["quality"])
    c_deploy = sum(1 for s in statuses.values() if s["deploy"])

    content = f"""# Pipeline Status — Ultimate.net.ua SEO

**Total Categories:** {total}
**Updated:** 2026-01-02

---

## Progress Overview

| Stage | Skill | RU | UK | Pending |
|-------|-------|----|----|---------|
| 01-init | /category-init | {c_init}/{total} | {c_init}/{total} | {total - c_init} |
| 02-meta | /generate-meta | {c_meta}/{total} | {c_meta}/{total} | {total - c_meta} |
| 03-research | /seo-research | {c_research}/{total} | — | {total - c_research} |
| 04-content | /content-generator | {c_content}/{total} | {c_content}/{total} | {total - c_content} |
| 05-uk | /uk-content-init | — | {c_uk}/{total} | {total - c_uk} |
| 06-quality | /quality-gate | {c_quality}/{total} | {c_quality}/{total} | {total - c_quality} |
| 07-deploy | /deploy-to-opencart | {c_deploy}/{total} | {c_deploy}/{total} | {total - c_deploy} |

---

## Next Steps needed (Top 5 Priority)

"""

    # Find next things to do
    # Priority: High volume categories that are not done

    todo = []
    seen = set()
    for node in nodes:
        slug = node["slug"]
        if slug in seen:
            continue
        seen.add(slug)

        s = statuses.get(slug, {})
        if not s["meta"]:
            todo.append(f"- {slug} (Meta)")
        elif not s["research"]:
            todo.append(f"- {slug} (Research)")
        elif not s["content"]:
            todo.append(f"- {slug} (Content)")

    content += "\n".join(todo[:10])

    with open(PIPELINE_STATUS_FILE, "w", encoding="utf-8") as f:
        f.write(content)


# ============================================================================
# Main
# ============================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Regenerate all task files")
    parser.add_argument("--sync", action="store_true", help="Sync statuses without overwriting task files")
    args = parser.parse_args()

    # Default behavior if no args? The user prompt implies we should support these modes.
    # If no args, maybe just print stats? Or default to sync?
    # Let's default to sync if nothing specified, safer.
    mode = "sync"
    if args.reset:
        mode = "reset"

    print(f"Parsing {STRUCTURE_FILE}...")
    nodes = parse_structure(STRUCTURE_FILE)
    print(f"Found {len(nodes)} nodes.")

    # Build statuses
    statuses = {}
    print("Checking statuses...")
    for node in nodes:
        statuses[node["slug"]] = check_real_status(node["slug"])

    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    if mode == "reset":
        print("Regenerating task files...")
        valid_slugs = set()
        for node in nodes:
            generate_task_file(node, statuses[node["slug"]])
            valid_slugs.add(node["slug"])

        # Cleanup
        for f in TASKS_DIR.glob("*.md"):
            if f.stem not in valid_slugs:
                print(f"Removing orphan task: {f.name}")
                os.remove(f)

    else:
        print("Sync mode: Skipping task file regeneration (only updating stats).")

    print("Updating MASTER_CHECKLIST.md...")
    update_master_checklist(nodes, statuses)

    print("Updating PIPELINE_STATUS.md...")
    update_pipeline_status(nodes, statuses)

    print("Done!")


if __name__ == "__main__":
    main()
