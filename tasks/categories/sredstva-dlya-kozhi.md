# sredstva-dlya-kozhi — Средства для кожи

**Priority:** LOW (volume 190)
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
| для химчистки салона | 50 |
| средство для кожи | 30 |
| для химчистки салона автомобиля | 20 |
| жидкость для химчистки салона | 20 |
| средство для кожаного салона | 10 |
| автокосметика для кожи | 10 |
| купить химчистку для салона автомобиля | 10 |
| средства для химчистки автомобиля | 10 |
| средство для химчистки автосалона | 10 |
| средство для химчистки салона автомобиля цена | 10 |
| средство для химчистки салона украина | 10 |

**Total:** 11

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/sredstva-dlya-kozhi/`
- [x] `data/sredstva-dlya-kozhi_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/sredstva-dlya-kozhi_meta.json` template
- [x] `content/sredstva-dlya-kozhi_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/sredstva-dlya-kozhi/data/sredstva-dlya-kozhi_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/sredstva-dlya-kozhi_clean.json`
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

- [ ] Записать в `meta/sredstva-dlya-kozhi_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/sredstva-dlya-kozhi/meta/sredstva-dlya-kozhi_meta.json
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
grep -c "^## Block" categories/sredstva-dlya-kozhi/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/sredstva-dlya-kozhi/content/sredstva-dlya-kozhi_ru.md "{keyword}" --mode seo
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
