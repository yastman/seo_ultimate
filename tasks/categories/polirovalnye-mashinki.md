# polirovalnye-mashinki — Полировальные машинки

**Priority:** HIGH (volume 11880)
**Type:** L2
**Parent:** polirovka

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
| полировочная машинка | 8100 |
| купить полировочную машинку | 880 |
| купить полировочную машинку для авто | 320 |
| аккумуляторная полировальная машина | 260 |
| полировальная машина на аккумуляторе | 260 |
| полировальная машинка на аккумуляторе | 260 |
| полировальная машина для полировки авто | 260 |
| полировочная машинка для полировки авто | 260 |
| купить машинку для полировки авто | 210 |
| купить полировочную машину | 110 |
| аккумуляторная полировальная машина для авто | 90 |
| машина для полировки авто | 90 |
| машина для полировки автомобиля | 90 |
| купить полировочную машинку для автомобиля | 70 |
| купить полировальную машинку для авто в украине | 50 |
| полировочные машинки для авто | 40 |
| полировальные машинки для авто | 40 |
| полировальные машинки для автомобиля | 40 |
| машина для полировки | 40 |
| машинка для полировки кузова | 30 |
| машинка для полировки кузова авто | 30 |
| машинка для полировки машины | 30 |
| купить аккумуляторную полировальную машинку | 20 |
| полировальная машина для авто на аккумуляторе | 20 |
| полировальная машина для автомобиля | 20 |
| полироль машинка | 20 |
| полировальная машина для авто | 20 |
| полировочная машинка цена | 20 |
| купить машинку для полировки кузова авто | 20 |
| купить машинку для полировки кузова автомобиля | 20 |
| полировочная машинка на аккумуляторе | 10 |
| машинка для полировки авто на аккумуляторе | 10 |
| купить машинку для полировки автомобиля | 10 |
| полировочная машинка для автомобиля | 10 |
| купить полировочную машину для авто | 10 |
| полировочная машинка для машины | 10 |
| машинка для полировки | 10 |
| машинка для полировки автомобилей | 10 |
| полировочная машинка для автомобиля цена | 10 |
| полировочные машины | 10 |
| машинка для полировки авто | 10 |
| купить полировочная машинка в украине | 10 |
| купить полировочную машинку для авто в украине | 10 |
| купить полировочную машину для автомобиля | 10 |
| полировочные машинки для авто цены | 10 |
| полировочная машинка для детейлинга | 10 |

**Total:** 46

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/polirovalnye-mashinki/`
- [x] `data/polirovalnye-mashinki_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/polirovalnye-mashinki_meta.json` template
- [x] `content/polirovalnye-mashinki_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/polirovalnye-mashinki/data/polirovalnye-mashinki_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/polirovalnye-mashinki_clean.json`
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

- [ ] Записать в `meta/polirovalnye-mashinki_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/polirovalnye-mashinki/meta/polirovalnye-mashinki_meta.json
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
grep -c "^## Block" categories/polirovalnye-mashinki/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/polirovalnye-mashinki/content/polirovalnye-mashinki_ru.md "{keyword}" --mode seo
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
