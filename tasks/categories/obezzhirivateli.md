# obezzhirivateli — Обезжириватели

**Priority:** HIGH (volume 1630)
**Type:** Cluster
**Parent:** obezzhirivateli

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
| шампунь для авто | 480 |
| купить химию для мойки авто | 260 |
| шампунь для мойки авто | 110 |
| средство для мойки авто | 70 |
| химия для мойки | 70 |
| химия для мойки машины | 50 |
| автохимия для мойки | 50 |
| автохимия для мойки авто | 50 |
| шампунь для автомойки | 50 |
| шампунь для моек высокого давления | 50 |
| полироль для наружного пластика автомобиля | 40 |
| полироль для наружного пластика авто | 40 |
| химия для мойки автомобиля | 20 |
| автохимия для мойки автомобиля | 20 |
| купить автохимию для мойки авто | 20 |
| шампунь для мойки | 20 |
| купить автошампунь | 20 |
| шампунь для мойки машины | 20 |
| жидкость для мойки авто | 10 |
| средство для мойки автомобиля | 10 |
| жидкость для мойки автомобиля | 10 |
| химия для мойки автомобиля цена | 10 |
| средство для мойки машин | 10 |
| химия для мойки авто цена | 10 |
| купить химию для мойки авто в украине | 10 |
| профессиональная химия для мойки авто | 10 |
| купить химию для мойки машин | 10 |
| полироль для наружного пластика | 10 |
| купить шампунь для мойки авто | 10 |
| шампунь для машины | 10 |
| шампунь для машини | 10 |
| купить шампунь для авто | 10 |
| автомобильный шампунь | 10 |
| купить шампунь для автомойки | 10 |
| купить шампунь для автомобиля | 10 |
| шампунь для минимойки | 10 |
| шампунь для автомойки высокого давления | 10 |
| автохимия для мойки кузова | 0 |
| химия для мойки авто украина | 0 |
| моющее средство для мойки авто | 0 |
| автомосметика и автохимия для мойки авто | 0 |

**Total:** 41

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/obezzhirivateli/`
- [x] `data/obezzhirivateli_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/obezzhirivateli_meta.json` template
- [x] `content/obezzhirivateli_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/obezzhirivateli/data/obezzhirivateli_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/obezzhirivateli_clean.json`
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

- [ ] Записать в `meta/obezzhirivateli_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/obezzhirivateli/meta/obezzhirivateli_meta.json
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
grep -c "^## Block" categories/obezzhirivateli/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/obezzhirivateli/content/obezzhirivateli_ru.md "{keyword}" --mode seo
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
