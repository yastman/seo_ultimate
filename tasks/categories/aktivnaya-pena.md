# aktivnaya-pena — Активная пена

**Priority:** HIGH (volume 8260)
**Type:** L3
**Parent:** avtoshampuni

---

## Current Status

| Stage | RU | UK |
|-------|----|----|
| 01-Init | ✅ | ✅ |
| 02-Meta | ✅ | ✅ |
| 03-Research | ✅ | — |
| 04-Content | ✅ | ✅ |
| 05-UK | — | ✅ |
| 06-Quality | ⬜ | ⬜ |
| 07-Deploy | ⬜ | ⬜ |

---

## Keywords (из CSV)

| Keyword | Volume |
|---------|--------|
| пена для мойки автомобиля | 1300 |
| пена для мойки авто | 1300 |
| активная пена для мойки авто | 1000 |
| активная пена для мойки автомобиля | 880 |
| активная пена | 720 |
| купить пену для мойки авто | 590 |
| активная пена для бесконтактной мойки | 320 |
| купить активная пена | 260 |
| купить активную пену для мойки авто | 210 |
| купить активную пену для мойки автомобиля | 170 |
| шампунь для бесконтактной мойки | 110 |
| купить активную пену для минимойки | 100 |
| шампунь для бесконтактной мойки авто | 90 |
| пена для автомобиля | 90 |
| пена для авто | 90 |
| пена для мытья машины | 90 |
| шампунь для бесконтактной мойки автомобилей | 70 |
| пена для бесконтактной мойки | 70 |
| пена для минимойки | 70 |
| активная пена для авто | 50 |
| активная пена для мойки | 50 |
| пена для мойки машины | 50 |
| пена для автомойки | 40 |
| пена для машины | 40 |
| купить активную пену для бесконтактной мойки | 40 |
| пена для бесконтактной мойки автомобилей | 30 |
| купить бесконтактную пену | 30 |
| пена для бесконтактной мойки авто | 30 |
| купить пену для мытья машины | 30 |
| купить пену для мойки высокого давления | 30 |
| купить пену для мойки | 30 |
| пена для мытья автомобиля | 20 |
| пена для мытья авто | 20 |
| купить пену для автомойки | 20 |
| купить пену для бесконтактной мойки | 20 |
| активная пена для мойки машин | 20 |
| бесконтактная пена | 20 |
| бесконтактная пена для автомойки | 20 |
| купить пену для мойки машин | 20 |
| купить активную пену для мойки | 20 |
| бесконтактная химия для автомойки | 20 |
| пена для мойки автомобиля купить | 10 |
| активная пена для автомойки | 10 |
| активная пена для мытья машины | 10 |
| профессиональная пена для мойки авто | 10 |
| бесконтактная пена для автомобилей | 10 |
| купить активную пену для мойки машин | 10 |
| активная пена цена | 10 |
| купить пену для бесконтактной мойки автомобиля | 10 |
| купить пену для машины | 0 |
| активная пена для мойки автомобиля цена | 0 |
| купить активную пену для мытья автомобиля | 0 |

**Total:** 52

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/aktivnaya-pena/`
- [x] `data/aktivnaya-pena_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/aktivnaya-pena_meta.json` template
- [x] `content/aktivnaya-pena_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/aktivnaya-pena/data/aktivnaya-pena_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/aktivnaya-pena_clean.json`
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

- [ ] Записать в `meta/aktivnaya-pena_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/aktivnaya-pena/meta/aktivnaya-pena_meta.json
```

---

## Stage 03: Research ✅

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
grep -c "^## Block" categories/aktivnaya-pena/research/RESEARCH_DATA.md
```

---

## Stage 04: Content ✅

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
python3 scripts/validate_content.py categories/aktivnaya-pena/content/aktivnaya-pena_ru.md "{keyword}" --mode seo
```

---

## Stage 05: UK ✅

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
