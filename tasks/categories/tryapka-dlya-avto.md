# tryapka-dlya-avto — Тряпка для авто

**Priority:** HIGH (volume 4310)
**Type:** Cluster
**Parent:** mikrofibra-i-tryapki

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
| тряпка для авто | 1300 |
| тряпки для автомобиля | 1300 |
| тряпки для машины | 260 |
| тряпочки для машины | 210 |
| тряпки для сушки авто | 170 |
| тряпки для сушки автомобиля | 170 |
| влаговпитывающая тряпка для авто | 110 |
| тряпка для мойки авто | 90 |
| купить тряпку для мойки автомобиля | 90 |
| купить тряпку для мойки авто | 90 |
| купить тряпку для сушки авто | 50 |
| набор тряпок для автомобиля | 50 |
| профессиональная тряпка для авто | 40 |
| автомобильные тряпки | 40 |
| тряпки для мойки автомобиля | 40 |
| тряпка для кузова авто | 30 |
| тряпки для мойки машин | 30 |
| тряпка для салона автомобиля | 30 |
| тряпка для салона авто | 20 |
| тряпка для протирки авто | 20 |
| профессиональные тряпки для мытья машины | 20 |
| тряпка для протирки автомобиля | 20 |
| тряпка для панели авто | 10 |
| тряпка для мытья машины цена | 10 |
| тряпка для протирки машины | 10 |
| тряпка для автомобиля купить | 10 |
| купити тряпку для авто | 10 |
| супер тряпка для авто | 10 |
| тряпка для машины цена | 10 |
| тряпка микрофибра для машины | 10 |
| тряпка для сушки машины | 10 |
| купить тряпку для мытья машины | 10 |
| тряпка для полировки машины | 10 |
| впитывающая тряпка для авто | 10 |
| набор тряпок для мойки авто | 10 |

**Total:** 35

---

## Stage 01: Init ⬜

- [ ] Папка создана: `categories/tryapka-dlya-avto/`
- [ ] `data/tryapka-dlya-avto_clean.json` создан
- [ ] Keywords кластеризованы
- [ ] `meta/tryapka-dlya-avto_meta.json` template
- [ ] `content/tryapka-dlya-avto_ru.md` placeholder
- [ ] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/tryapka-dlya-avto/data/tryapka-dlya-avto_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ⬜

### Inputs

- [ ] Прочитать `data/tryapka-dlya-avto_clean.json`
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

- [ ] Записать в `meta/tryapka-dlya-avto_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/tryapka-dlya-avto/meta/tryapka-dlya-avto_meta.json
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
grep -c "^## Block" categories/tryapka-dlya-avto/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/tryapka-dlya-avto/content/tryapka-dlya-avto_ru.md "{keyword}" --mode seo
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
