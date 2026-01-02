#!/usr/bin/env python3
"""
Generate individual checklist files for all categories.
"""

import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CATEGORIES_DIR = BASE_DIR / "categories"
TASKS_DIR = BASE_DIR / "tasks" / "categories"

# Category data with status and priority
CATEGORIES = {
    # COMPLETED (13) - all stages done except deploy
    "aktivnaya-pena": {"priority": "HIGH", "type": "L3", "parent": "avtoshampuni", "volume": "1000+", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "dlya-ruchnoy-moyki": {"priority": "MEDIUM", "type": "L3", "parent": "avtoshampuni", "volume": "390", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "ochistiteli-stekol": {"priority": "MEDIUM", "type": "L3", "parent": "sredstva-dlya-stekol", "volume": "170", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "glina-i-avtoskraby": {"priority": "MEDIUM", "type": "L3", "parent": "ochistiteli-kuzova", "volume": "390", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "antimoshka": {"priority": "MEDIUM", "type": "L3", "parent": "ochistiteli-kuzova", "volume": "320", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "antibitum": {"priority": "LOW", "type": "L3", "parent": "ochistiteli-kuzova", "volume": "20", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "cherniteli-shin": {"priority": "HIGH", "type": "L3", "parent": "sredstva-dlya-diskov-i-shin", "volume": "1000", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "ochistiteli-diskov": {"priority": "MEDIUM", "type": "L3", "parent": "sredstva-dlya-diskov-i-shin", "volume": "70", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "ochistiteli-shin": {"priority": "LOW", "type": "L3", "parent": "sredstva-dlya-diskov-i-shin", "volume": "70", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "dlya-khimchistki-salona": {"priority": "HIGH", "type": "L2", "parent": "ukhod-za-interierom", "volume": "590", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "ochistiteli-dvigatelya": {"priority": "MEDIUM", "type": "L2", "parent": "moyka-i-eksterior", "volume": "480", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "keramika-i-zhidkoe-steklo": {"priority": "MEDIUM", "type": "L2", "parent": "zashchitnye-pokrytiya", "volume": "480", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},
    "gubki-i-varezhki": {"priority": "MEDIUM", "type": "L2", "parent": "aksessuary", "volume": "320", "status": {"init": True, "meta": True, "research": True, "content": True, "uk": True, "quality": True, "deploy": False}},

    # INIT+META done, need Research+Content (21)
    "polirovalnye-mashinki": {"priority": "HIGH", "type": "L2", "parent": "polirovka", "volume": "8100", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "malyarnyy-skotch": {"priority": "HIGH", "type": "L2", "parent": "aksessuary", "volume": "4400", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "mikrofibra-i-tryapki": {"priority": "HIGH", "type": "L2", "parent": "aksessuary", "volume": "1300", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "polirovalnye-pasty": {"priority": "HIGH", "type": "L2", "parent": "polirovka", "volume": "1600", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "polirovalnye-krugi": {"priority": "MEDIUM", "type": "L2", "parent": "polirovka", "volume": "720", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "neytralizatory-zapakha": {"priority": "HIGH", "type": "L2", "parent": "ukhod-za-interierom", "volume": "2400", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "apparaty-tornador": {"priority": "HIGH", "type": "L3", "parent": "oborudovanie", "volume": "3600", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "raspyliteli-i-penniki": {"priority": "MEDIUM", "type": "L2", "parent": "aksessuary", "volume": "260", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "poliroli-dlya-plastika": {"priority": "MEDIUM", "type": "L2", "parent": "ukhod-za-interierom", "volume": "390", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "kvik-deteylery": {"priority": "MEDIUM", "type": "L2", "parent": "zashchitnye-pokrytiya", "volume": "140", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "obezzhirivateli": {"priority": "MEDIUM", "type": "L2", "parent": "moyka-i-eksterior", "volume": "590", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "voski": {"priority": "HIGH", "type": "L2", "parent": "zashchitnye-pokrytiya", "volume": "1600", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "antidozhd": {"priority": "HIGH", "type": "L3", "parent": "sredstva-dlya-stekol", "volume": "1000", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "aksessuary-dlya-naneseniya": {"priority": "MEDIUM", "type": "L2", "parent": "aksessuary", "volume": "170", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "sredstva-dlya-kozhi": {"priority": "MEDIUM", "type": "L2", "parent": "ukhod-za-interierom", "volume": "210", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "shchetki-i-kisti": {"priority": "MEDIUM", "type": "L2", "parent": "aksessuary", "volume": "480", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "omyvatel": {"priority": "HIGH", "type": "L3", "parent": "sredstva-dlya-stekol", "volume": "1000", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "polirol-dlya-stekla": {"priority": "MEDIUM", "type": "L3", "parent": "polirovka", "volume": "590", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "vedra-i-emkosti": {"priority": "LOW", "type": "L2", "parent": "aksessuary", "volume": "90", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "silanty": {"priority": "LOW", "type": "L3", "parent": "zashchitnye-pokrytiya", "volume": "50", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},
    "mekhovye": {"priority": "LOW", "type": "L3", "parent": "polirovalnye-krugi", "volume": "50", "status": {"init": True, "meta": True, "research": False, "content": False, "uk": True, "quality": False, "deploy": False}},

    # INIT done, need META (17)
    "tverdyy-vosk": {"priority": "HIGH", "type": "SEO-filter", "parent": "voski", "volume": "1000", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "zhidkiy-vosk": {"priority": "MEDIUM", "type": "SEO-filter", "parent": "voski", "volume": "480", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "pyatnovyvoditeli": {"priority": "HIGH", "type": "L3", "parent": "ukhod-za-interierom", "volume": "2400", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "ochistiteli-kuzova": {"priority": "MEDIUM", "type": "L2", "parent": "moyka-i-eksterior", "volume": "590", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "akkumulyatornye-mashinki": {"priority": "MEDIUM", "type": "SEO-filter", "parent": "polirovalnye-mashinki", "volume": "260", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "avtoshampuni": {"priority": "MEDIUM", "type": "L2", "parent": "moyka-i-eksterior", "volume": "480", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "sredstva-dlya-stekol": {"priority": "MEDIUM", "type": "L2", "parent": "moyka-i-eksterior", "volume": "L2", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "sredstva-dlya-diskov-i-shin": {"priority": "MEDIUM", "type": "L2", "parent": "moyka-i-eksterior", "volume": "L2", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "s-voskom": {"priority": "LOW", "type": "SEO-filter", "parent": "dlya-ruchnoy-moyki", "volume": "SEO", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "kislotnyy-shampun": {"priority": "LOW", "type": "SEO-filter", "parent": "avtoshampuni", "volume": "70", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "zashchitnoe-pokrytie-dlya-koles": {"priority": "LOW", "type": "L3", "parent": "sredstva-dlya-diskov-i-shin", "volume": "10", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "dlya-vneshnego-plastika": {"priority": "LOW", "type": "L3", "parent": "ochistiteli-kuzova", "volume": "40", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "mikrofibra-dlya-polirovki": {"priority": "LOW", "type": "SEO-filter", "parent": "mikrofibra-i-tryapki", "volume": "50", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "mikrofibra-dlya-stekol": {"priority": "LOW", "type": "SEO-filter", "parent": "mikrofibra-i-tryapki", "volume": "50", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "nabory-dlya-deteylinga": {"priority": "MEDIUM", "type": "L2", "parent": "aksessuary", "volume": "260", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "porolonovye": {"priority": "LOW", "type": "L3", "parent": "polirovalnye-krugi", "volume": "L3", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "oborudovanie": {"priority": "LOW", "type": "L2", "parent": "zashchitnye-pokrytiya", "volume": "90", "status": {"init": True, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},

    # NOT CREATED (7)
    "nabory-dlya-moyki": {"priority": "MEDIUM", "type": "L3", "parent": "nabory-dlya-deteylinga", "volume": "210", "status": {"init": False, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "nabory-dlya-polirovki": {"priority": "MEDIUM", "type": "L3", "parent": "nabory-dlya-deteylinga", "volume": "480", "status": {"init": False, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "nabory-dlya-khimchistki": {"priority": "MEDIUM", "type": "L3", "parent": "nabory-dlya-deteylinga", "volume": "170", "status": {"init": False, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "nabory-dlya-kozhi": {"priority": "LOW", "type": "L3", "parent": "nabory-dlya-deteylinga", "volume": "30", "status": {"init": False, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "podarochnye-nabory": {"priority": "MEDIUM", "type": "L3", "parent": "nabory-dlya-deteylinga", "volume": "140", "status": {"init": False, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "ukhod-za-kozhey": {"priority": "MEDIUM", "type": "L3", "parent": "sredstva-dlya-kozhi", "volume": "210", "status": {"init": False, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
    "chistka-kozhi": {"priority": "LOW", "type": "L3", "parent": "sredstva-dlya-kozhi", "volume": "70", "status": {"init": False, "meta": False, "research": False, "content": False, "uk": False, "quality": False, "deploy": False}},
}

TEMPLATE = '''# {slug} — {title}

**Priority:** {priority} (volume {volume})
**Type:** {type}
**Parent:** {parent}

---

## Current Status

| Stage | RU | UK |
|-------|----|----|
| 01-Init | {init} | {init_uk} |
| 02-Meta | {meta} | {meta_uk} |
| 03-Research | {research} | — |
| 04-Content | {content} | {content_uk} |
| 05-UK | — | {uk} |
| 06-Quality | {quality} | {quality_uk} |
| 07-Deploy | {deploy} | {deploy_uk} |

---

## Stage 01: Init {init}

- [{init_check}] Папка создана: `categories/{slug}/`
- [{init_check}] `data/{slug}_clean.json` создан
- [{init_check}] Keywords кластеризованы
- [{init_check}] `meta/{slug}_meta.json` template
- [{init_check}] `content/{slug}_ru.md` placeholder
- [{init_check}] `research/RESEARCH_DATA.md` template

**Validation:**
```bash
python3 -c "import json; json.load(open('categories/{slug}/data/{slug}_clean.json')); print('PASS')"
```

---

## Stage 02: Meta {meta}

### Inputs
- [ ] Прочитать `data/{slug}_clean.json`
- [ ] Определить primary keyword
- [ ] Загрузить товары из products_with_descriptions.md

### Tasks RU
- [ ] title_ru: 50-60 chars, содержит primary keyword
- [ ] description_ru: 150-160 chars, CTA "Доставка по Украине"
- [ ] h1_ru: primary keyword (без "купить")

### Tasks UK
- [ ] title_uk: 50-60 chars
- [ ] description_uk: 150-160 chars
- [ ] h1_uk: перевод primary keyword

### Output
- [ ] Записать в `meta/{slug}_meta.json`

### Validation
```bash
python3 scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json
```

---

## Stage 03: Research {research}

### Block 1: Product Analysis
- [ ] ТОП-5 брендов
- [ ] Ценовой диапазон
- [ ] Особенности товаров

### Block 2: Competitors
- [ ] WebSearch: "{{primary keyword}} купить украина"
- [ ] Найти 3-5 конкурентов
- [ ] Выписать структуру контента

### Block 3: Use Cases
- [ ] Для кого?
- [ ] Какие задачи решает?
- [ ] Где применяется?

### Block 4: Buying Guide
- [ ] Критерии выбора
- [ ] На что обратить внимание

### Block 5: FAQ
- [ ] Собрать 5-7 вопросов

### Block 6: Comparison Table
- [ ] Определить критерии
- [ ] 3-5 брендов/продуктов

### Block 7: How-To
- [ ] Пошаговая инструкция
- [ ] Необходимое оборудование

### Block 8: Interlink
- [ ] Связанные категории
- [ ] Дополняющие товары

### Output
- [ ] Записать в `research/RESEARCH_DATA.md`

### Validation
```bash
grep -c "^## Block" categories/{slug}/research/RESEARCH_DATA.md
```

---

## Stage 04: Content {content}

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

### Validation
```bash
python3 scripts/validate_content.py categories/{slug}/content/{slug}_ru.md "{{keyword}}" --mode seo
```

---

## Stage 05: UK {uk}

### Create Structure
- [ ] `uk/categories/{slug}/data/`
- [ ] `uk/categories/{slug}/meta/`
- [ ] `uk/categories/{slug}/content/`

### Translate
- [ ] Keywords
- [ ] Meta tags
- [ ] Content

### Quality Check
- [ ] Перевод (не транслитерация)
- [ ] Терминология
- [ ] CTA на украинском

---

## Stage 06: Quality Gate {quality}

### Checklist
- [ ] Data JSON valid (RU + UK)
- [ ] Meta valid (RU + UK)
- [ ] Content valid (RU + UK)
- [ ] Research complete
- [ ] SEO compliant

### Output
- [ ] Создать `QUALITY_REPORT.md`

---

## Stage 07: Deploy {deploy}

### Pre-Deploy
- [ ] Quality Gate = PASS
- [ ] Backup DB

### Deploy
- [ ] Find category_id
- [ ] UPDATE meta RU
- [ ] UPDATE content RU
- [ ] UPDATE meta UK
- [ ] UPDATE content UK

### Post-Deploy
- [ ] Clear cache
- [ ] Visual check
- [ ] Verify both languages

---

## Notes

- Parent: {parent}
- Type: {type}
- Volume: {volume}

---

**Last Updated:** 2025-12-31
'''

def get_status_icon(done):
    return "✅" if done else "⬜"

def get_check(done):
    return "x" if done else " "

def slug_to_title(slug):
    """Convert slug to readable title."""
    return slug.replace("-", " ").title()

def generate_checklist(slug, data):
    """Generate checklist markdown for a category."""
    status = data["status"]

    return TEMPLATE.format(
        slug=slug,
        title=slug_to_title(slug),
        priority=data["priority"],
        volume=data["volume"],
        type=data["type"],
        parent=data["parent"],
        init=get_status_icon(status["init"]),
        init_uk=get_status_icon(status["init"]) if status["uk"] else "⬜",
        meta=get_status_icon(status["meta"]),
        meta_uk=get_status_icon(status["meta"]) if status["uk"] else "⬜",
        research=get_status_icon(status["research"]),
        content=get_status_icon(status["content"]),
        content_uk=get_status_icon(status["content"]) if status["uk"] else "⬜",
        uk=get_status_icon(status["uk"]),
        quality=get_status_icon(status["quality"]),
        quality_uk=get_status_icon(status["quality"]) if status["uk"] else "⬜",
        deploy=get_status_icon(status["deploy"]),
        deploy_uk=get_status_icon(status["deploy"]) if status["uk"] else "⬜",
        init_check=get_check(status["init"]),
    )

def main():
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    count = 0
    for slug, data in CATEGORIES.items():
        filepath = TASKS_DIR / f"{slug}.md"
        content = generate_checklist(slug, data)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        count += 1
        print(f"Generated: {slug}.md")

    print(f"\nTotal: {count} checklists generated")

if __name__ == "__main__":
    main()
