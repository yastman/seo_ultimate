# nabor-dlya-moyki-avto — Набор для мойки авто

**Priority:** MEDIUM (volume 720)
**Type:** Cluster
**Parent:** apparaty-tornador

---

## Current Status

| Stage | RU | UK |
|-------|----|----|
| 01-Init | ⬜ | ⬜ |
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
| набор для мойки авто | 210 |
| набор для чистки салона авто | 140 |
| набор для чистки автомобиля | 50 |
| набор для ухода за машиной | 50 |
| набор для мойки автомобиля | 30 |
| набор для мойки машины | 30 |
| набор кругов для полировки авто | 30 |
| набор кисточек для детейлинга | 30 |
| набор для ухода за кожей авто | 30 |
| набор паст для полировки авто | 20 |
| набор для салона автомобиля | 20 |
| купить набор для мойки автомобиля | 10 |
| набор для мытья автомобиля | 10 |
| подарочный набор для ухода за автомобилем | 10 |
| диски для полировки | 10 |
| набор кистей для детейлинга | 10 |
| набор тряпок для машины | 10 |
| набор салфеток для автомобиля | 10 |
| набор щеток для химчистки авто | 10 |

**Total:** 19

---

## Stage 01: Init ⬜

- [ ] Папка создана: `categories/nabor-dlya-moyki-avto/`
- [ ] `data/nabor-dlya-moyki-avto_clean.json` создан
- [ ] Keywords кластеризованы
- [ ] `meta/nabor-dlya-moyki-avto_meta.json` template
- [ ] `content/nabor-dlya-moyki-avto_ru.md` placeholder
- [ ] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/nabor-dlya-moyki-avto/data/nabor-dlya-moyki-avto_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ⬜

### Inputs

- [ ] Прочитать `data/nabor-dlya-moyki-avto_clean.json`
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

- [ ] Записать в `meta/nabor-dlya-moyki-avto_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/nabor-dlya-moyki-avto/meta/nabor-dlya-moyki-avto_meta.json
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
grep -c "^## Block" categories/nabor-dlya-moyki-avto/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/nabor-dlya-moyki-avto/content/nabor-dlya-moyki-avto_ru.md "{keyword}" --mode seo
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
