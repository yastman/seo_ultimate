# glavnaya — Главная

**Priority:** HIGH (volume 3180)
**Type:** Cluster
**Parent:** apparaty-tornador

---

## Current Status

| Stage | RU | UK |
|-------|----|----|
| 01-Init | ✅ | ⬜ |
| 02-Meta | ⬜ | ⬜ |
| 03-Research | ⬜ | — |
| 04-Content | ⬜ | ⬜ |
| 05-UK | — | ⬜ |
| 06-Quality | ⬜ | ⬜ |
| 07-Deploy | ⬜ | ⬜ |

---

## Keywords (из CSV)

| Keyword | Volume |
|---------|--------|
| автокосметика | 480 |
| автохимия | 470 |
| авто химия | 320 |
| магазин автохимии | 260 |
| автохимия для авто | 140 |
| косметика для авто | 140 |
| косметика для автомобиля | 140 |
| автокосметика для авто | 90 |
| автокосметика для автомобиля | 90 |
| автодетейлинг | 90 |
| автохимия купить | 70 |
| химия для автомойки | 70 |
| химия для детейлинга | 50 |
| магазин автокосметики | 50 |
| химия для машины | 50 |
| косметика для машин | 40 |
| химия для бесконтактной мойки | 30 |
| купить химию для автомобиля | 30 |
| детейлинг магазин киев | 30 |
| купить химию для авто | 30 |
| автокосметика купить | 20 |
| автокосметика украина | 20 |
| автокосметика для детейлинга | 20 |
| автохимия для детейлинга | 20 |
| автокосметика купить киев | 10 |
| химия для автомобиля | 10 |
| автохимия для автомобиля | 10 |
| автохимия украина | 10 |
| химия для бесконтактной мойки автомобиля | 10 |
| химия для бесконтактной мойки авто | 10 |
| автокосметика для машины | 10 |
| косметика для автомобиля купить | 10 |
| автохимия интернет магазин украина | 10 |
| автохимия купить украина | 10 |
| автохимия для автомобиля интернет магазин | 10 |
| автохимия и автокосметика интернет магазин | 10 |
| автохимия и косметика | 10 |
| автохимия интернет магазин | 10 |
| где купить автохимию | 10 |
| продажа автохимии | 10 |
| автокосметика автохимия | 10 |
| интернет магазин автокосметики | 10 |
| химия автомобильная | 10 |
| детейлинг шоп | 10 |
| автохимия каталог | 10 |
| автокосметика для автомобиля интернет магазин | 10 |
| автокосметика купить в украине | 10 |
| профессиональная автохимия и автокосметика | 10 |
| автомобильная косметика | 10 |
| автокосметика для автомоек | 10 |
| химия для автомоек киев | 10 |
| автокосметика киев | 10 |
| автокосметика профессиональная | 10 |
| автохимия и автокосметика описание | 10 |
| автохимия киев интернет магазин | 10 |
| детейлинг химия | 10 |
| автохимия купить киев | 10 |
| магазин автохимии киев | 10 |
| химия для автомойки украина | 10 |
| профессиональная химия для автомоек | 10 |
| купить химию для автомойки | 10 |
| химия для мытья машин | 10 |
| автокосметика для салона | 10 |
| автокосметика цены | 10 |
| каталог автокосметики | 10 |
| элитная автокосметика | 10 |
| автохимия цена | 10 |

**Total:** 67

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/glavnaya/`
- [x] `data/glavnaya_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/glavnaya_meta.json` template
- [x] `content/glavnaya_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/glavnaya/data/glavnaya_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ⬜

### Inputs

- [ ] Прочитать `data/glavnaya_clean.json`
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

- [ ] Записать в `meta/glavnaya_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/glavnaya/meta/glavnaya_meta.json
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
grep -c "^## Block" categories/glavnaya/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/glavnaya/content/glavnaya_ru.md "{keyword}" --mode seo
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
