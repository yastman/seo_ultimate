# omyvatel — Омыватель

**Priority:** HIGH (volume 3460)
**Type:** Cluster
**Parent:** sredstva-dlya-stekol

---

## Current Status

| Stage | RU | UK |
|-------|----|----|
| 01-Init | ✅ | ⬜ |
| 02-Meta | ✅ | ⬜ |
| 03-Research | ⬜ | — |
| 04-Content | ⬜ | ⬜ |
| 05-UK | — | ⬜ |
| 06-Quality | ⬜ | ⬜ |
| 07-Deploy | ⬜ | ⬜ |

---

## Keywords (из CSV)

| Keyword | Volume |
|---------|--------|
| омыватель стекла зимний | 1000 |
| омыватель стекла | 720 |
| зимний омыватель | 320 |
| омыватель | 260 |
| купить омыватель стекла зимний | 170 |
| купить омыватель стекол зимний | 170 |
| омыватель стекла летний | 140 |
| омыватель лобового стекла | 110 |
| стеклоомыватель | 110 |
| купить омыватель стекла | 50 |
| омыватель для стекол | 50 |
| купить зимний омыватель | 40 |
| омыватель летний | 40 |
| стеклоомыватель зимний | 40 |
| омыватель для машины | 30 |
| омыватель заднего стекла | 20 |
| купить омыватель | 20 |
| омыватель стекол купить | 20 |
| зимние омыватели стекол | 10 |
| жидкость стеклоомыватель для автомобиля | 10 |
| омыватели стекла цена | 10 |
| купить омыватель стекла авто | 10 |
| стеклоомыватель цена | 10 |
| стеклоомыватель в машине | 10 |
| купить стеклоомыватель для авто | 10 |
| стеклоомыватель для автомобиля | 10 |
| летний омыватель купить | 10 |
| летний стеклоомыватель | 10 |
| зимний стеклоомыватель купить | 10 |
| купить стеклоомыватель | 10 |
| омыватель стекла антимошка | 10 |
| омывайка антимошка | 10 |
| стеклоомыватель зимний цена | 10 |
| стеклоомыватель украина | 0 |
| купить стеклоомыватель цены | 0 |

**Total:** 35

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/omyvatel/`
- [x] `data/omyvatel_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/omyvatel_meta.json` template
- [x] `content/omyvatel_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/omyvatel/data/omyvatel_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/omyvatel_clean.json`
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

- [ ] Записать в `meta/omyvatel_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/omyvatel/meta/omyvatel_meta.json
```

---

## Stage 03: Research ⬜

### Block 1: Product Analysis

- [ ] ТОП-5 брендов
- [ ] Ценовой диапазон

### Block 2: Competitors

- [ ] WebSearch: "{primary keyword} купить украина"

### Block 3: Use Cases

- [ ] Для кого?
- [ ] Какие задачи решает?

### Research Output

- [ ] Записать в `research/RESEARCH_DATA.md`

### Research Validation

```bash
grep -c "^## Block" categories/omyvatel/research/RESEARCH_DATA.md
```

---

## Stage 04: Content ⬜

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
python3 scripts/validate_content.py categories/omyvatel/content/omyvatel_ru.md "{keyword}" --mode seo
```

---

## Stage 05: UK ⬜

- [ ] Structure created
- [ ] Translated Keywords, Meta, Content

---

## Stage 06: Quality Gate ⬜

- [ ] Data JSON valid
- [ ] Meta valid
- [ ] Content valid
- [ ] Research complete
- [ ] SEO compliant

---

## Stage 07: Deploy ⬜

- [ ] Backup DB
- [ ] Update Meta/Content RU/UK
- [ ] Clear cache

---

**Last Updated:** 2026-01-02
