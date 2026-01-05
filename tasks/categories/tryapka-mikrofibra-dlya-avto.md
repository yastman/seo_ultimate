# tryapka-mikrofibra-dlya-avto — Тряпка микрофибра для авто

**Priority:** HIGH (volume 1500)
**Type:** Cluster
**Parent:** mikrofibra-i-tryapki

---

## Current Status

| Stage       | RU  | UK  |
| ----------- | --- | --- |
| 01-Init     | ⬜  | ⬜  |
| 02-Meta     | ⬜  | ⬜  |
| 03-Research | ⬜  | —   |
| 04-Content  | ⬜  | ⬜  |
| 05-UK       | —   | ⬜  |
| 06-Quality  | ⬜  | ⬜  |
| 07-Deploy   | ⬜  | ⬜  |

---

## Keywords (из CSV)

| Keyword                             | Volume |
| ----------------------------------- | ------ |
| микрофибра для авто                 | 1300   |
| тряпка микрофибра для авто          | 90     |
| микрофибра для стекла авто          | 30     |
| микрофибра для машины               | 30     |
| тряпка из микрофибры для автомобиля | 20     |
| салфетка из микрофибры для авто     | 20     |
| фибра для авто                      | 10     |

**Total:** 7

---

## Stage 01: Init ⬜

-   [ ] Папка создана: `categories/tryapka-mikrofibra-dlya-avto/`
-   [ ] `data/tryapka-mikrofibra-dlya-avto_clean.json` создан
-   [ ] Keywords кластеризованы
-   [ ] `meta/tryapka-mikrofibra-dlya-avto_meta.json` template
-   [ ] `content/tryapka-mikrofibra-dlya-avto_ru.md` placeholder
-   [ ] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/tryapka-mikrofibra-dlya-avto/data/tryapka-mikrofibra-dlya-avto_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ⬜

### Inputs

-   [ ] Прочитать `data/tryapka-mikrofibra-dlya-avto_clean.json`
-   [ ] Определить primary keyword

### Tasks RU

-   [ ] title_ru: 50-60 chars, содержит primary keyword
-   [ ] description_ru: 150-160 chars, CTA "Доставка по Украине"
-   [ ] h1_ru: primary keyword (без "купить")

### Tasks UK

-   [ ] title_uk: 50-60 chars
-   [ ] description_uk: 150-160 chars
-   [ ] h1_uk: перевод primary keyword

### Meta Output

-   [ ] Записать в `meta/tryapka-mikrofibra-dlya-avto_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/tryapka-mikrofibra-dlya-avto/meta/tryapka-mikrofibra-dlya-avto_meta.json
```

---

## Stage 03: Research ⬜

### Block 1: Product Analysis

-   [ ] ТОП-5 брендов
-   [ ] Ценовой диапазон

### Block 2: Competitors

-   [ ] WebSearch: "{primary keyword} купить украина"

### Block 3: Use Cases

-   [ ] Для кого?
-   [ ] Какие задачи решает?

### Research Output

-   [ ] Записать в `research/RESEARCH_DATA.md`

### Research Validation

```bash
grep -c "^## Block" categories/tryapka-mikrofibra-dlya-avto/research/RESEARCH_DATA.md
```

---

## Stage 04: Content ⬜

### Structure

-   [ ] H1: primary keyword
-   [ ] Intro: 150-200 слов
-   [ ] H2: Buying Guide
-   [ ] Comparison Table
-   [ ] H2: How-To
-   [ ] H2: FAQ (5+ вопросов)
-   [ ] Conclusion + CTA

### SEO Requirements

-   [ ] Primary keyword: 3-5 раз
-   [ ] Word count: 1500-2500
-   [ ] Density: 1.5-2.5%
-   [ ] NO commercial keywords!

### Content Validation

```bash
python3 scripts/validate_content.py categories/tryapka-mikrofibra-dlya-avto/content/tryapka-mikrofibra-dlya-avto_ru.md "{keyword}" --mode seo
```

---

## Stage 05: UK ⬜

-   [ ] Structure created
-   [ ] Translated Keywords, Meta, Content

---

## Stage 06: Quality Gate ⬜

-   [ ] Data JSON valid
-   [ ] Meta valid
-   [ ] Content valid
-   [ ] Research complete
-   [ ] SEO compliant

---

## Stage 07: Deploy ⬜

-   [ ] Backup DB
-   [ ] Update Meta/Content RU/UK
-   [ ] Clear cache

---

**Last Updated:** 2026-01-02
