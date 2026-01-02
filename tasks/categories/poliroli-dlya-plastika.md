# poliroli-dlya-plastika — Полироли для пластика

**Priority:** HIGH (volume 2170)
**Type:** Cluster
**Parent:** poliroli-dlya-plastika

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
| полироль для салона автомобиля | 390 |
| полироль для пластика автомобиля | 320 |
| полироль для пластику авто | 320 |
| полироль для торпеды | 260 |
| полироль для панели авто | 170 |
| полироль для торпеды автомобиля | 170 |
| полироль для торпедо авто | 140 |
| полироль для торпеды авто | 140 |
| полироль для панели автомобиля | 70 |
| полироль для салона | 40 |
| полироль для пластика салона | 20 |
| средство для ухода за пластиком авто | 20 |
| средство для ухода за пластиком автомобиля | 20 |
| полироль для автомобильного пластика | 10 |
| купить полироль для панели авто | 10 |
| купить полироль для пластика | 10 |
| полироль для пластика | 10 |
| купить полироль для пластика авто | 10 |
| купить полироль для салона автомобиля | 10 |
| средство для полировки салона автомобиля | 10 |
| купить полироль для торпеды автомобиля | 10 |
| средство для ухода за пластиком | 10 |

**Total:** 22

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/poliroli-dlya-plastika/`
- [x] `data/poliroli-dlya-plastika_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/poliroli-dlya-plastika_meta.json` template
- [x] `content/poliroli-dlya-plastika_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/poliroli-dlya-plastika/data/poliroli-dlya-plastika_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/poliroli-dlya-plastika_clean.json`
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

- [ ] Записать в `meta/poliroli-dlya-plastika_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/poliroli-dlya-plastika/meta/poliroli-dlya-plastika_meta.json
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
grep -c "^## Block" categories/poliroli-dlya-plastika/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/poliroli-dlya-plastika/content/poliroli-dlya-plastika_ru.md "{keyword}" --mode seo
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
