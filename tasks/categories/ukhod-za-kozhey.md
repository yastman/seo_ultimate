# ukhod-za-kozhey — Уход за кожей

**Priority:** HIGH (volume 1710)
**Type:** Cluster
**Parent:** sredstva-dlya-kozhi

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
| уход за кожей авто | 210 |
| уход за кожей автомобиля | 210 |
| полироль для кожи | 170 |
| лучшее средство по уходу за кожей авто | 140 |
| средство для кожи авто | 110 |
| средства для кожи автомобиля | 90 |
| средство по уходу за кожей авто | 90 |
| полироль для кожи авто | 90 |
| полироль для кожи автомобиля | 90 |
| крем для кожи авто | 70 |
| средства по уходу за кожей автомобиля | 70 |
| крем для кожи автомобиля | 70 |
| для кожи автомобиля | 40 |
| средства для чистки кожаного салона автомобиля | 40 |
| уход за кожей салона автомобиля | 20 |
| химия для кожи авто | 20 |
| средство за уходом кожаного салона | 20 |
| купить средство для ухода за кожей авто | 20 |
| уход за кожей салона авто | 20 |
| уход за кожей салона | 10 |
| уход за кожей в машине | 10 |
| средство для кожи салона авто | 10 |
| средства для очистки кожи салона авто | 10 |
| очиститель кожи автомобиля | 10 |
| средство для ухода за кожей салона | 10 |
| химия для чистки кожаного салона | 10 |
| средства для ухода за кожей салона авто | 10 |
| лучшее средство для ухода за кожей автомобиля | 10 |
| средства для ухода за кожей салона автомобиля | 10 |
| автохимия для кожаного салона | 10 |
| лосьон для кожи авто | 10 |
| средство для сохранения кожи авто | 0 |
| средство для защиты кожаного салона авто | 0 |
| уход за кожей автомобиля купить | 0 |

**Total:** 34

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/ukhod-za-kozhey/`
- [x] `data/ukhod-za-kozhey_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/ukhod-za-kozhey_meta.json` template
- [x] `content/ukhod-za-kozhey_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/ukhod-za-kozhey/data/ukhod-za-kozhey_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/ukhod-za-kozhey_clean.json`
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

- [ ] Записать в `meta/ukhod-za-kozhey_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/ukhod-za-kozhey/meta/ukhod-za-kozhey_meta.json
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
grep -c "^## Block" categories/ukhod-za-kozhey/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/ukhod-za-kozhey/content/ukhod-za-kozhey_ru.md "{keyword}" --mode seo
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
