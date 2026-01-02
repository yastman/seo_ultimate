# neytralizatory-zapakha — Нейтрализаторы запаха

**Priority:** HIGH (volume 3740)
**Type:** Cluster
**Parent:** neytralizatory-zapakha

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
| нейтрализаторы запаха | 2400 |
| поглотитель запаха | 260 |
| нейтрализатор запаха в автомобиле | 170 |
| профессиональный нейтрализатор запаха | 170 |
| нейтрализатор запаха в авто | 140 |
| устранитель запаха | 90 |
| купить нейтрализатор запахов | 90 |
| нейтрализатор для авто | 70 |
| нейтрализатор запахов в салоне авто | 50 |
| нейтрализатор запаха автомобильный | 40 |
| средство для удаления запаха в салоне автомобиля | 30 |
| нейтрализатор запаха в машину | 30 |
| устранение запаха в автомобиле | 30 |
| устранитель запахов в авто | 20 |
| устранитель запаха купить | 10 |
| поглотитель запахов купить | 10 |
| поглотитель запаха для автомобиля | 10 |
| нейтрализатор запаха для автомобиля купить | 10 |
| устранитель запаха в машине | 10 |
| поглотитель запаха для авто | 10 |
| поглотитель запаха автомобильный | 10 |
| поглотитель запаха в машину | 10 |
| нейтрализатор запахов в салоне | 10 |
| удаление запаха в машине | 10 |
| удаление запахов в автомобиле | 10 |
| удалить запах в салоне автомобиля | 10 |
| устранение запаха в салоне автомобиля | 10 |
| устранение неприятных запахов в автомобиле | 10 |
| устранитель запаха в автомобиле | 10 |

**Total:** 29

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/neytralizatory-zapakha/`
- [x] `data/neytralizatory-zapakha_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/neytralizatory-zapakha_meta.json` template
- [x] `content/neytralizatory-zapakha_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/neytralizatory-zapakha/data/neytralizatory-zapakha_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/neytralizatory-zapakha_clean.json`
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

- [ ] Записать в `meta/neytralizatory-zapakha_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/neytralizatory-zapakha/meta/neytralizatory-zapakha_meta.json
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
grep -c "^## Block" categories/neytralizatory-zapakha/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/neytralizatory-zapakha/content/neytralizatory-zapakha_ru.md "{keyword}" --mode seo
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
