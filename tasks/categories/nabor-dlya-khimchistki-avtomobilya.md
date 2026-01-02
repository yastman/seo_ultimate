# nabor-dlya-khimchistki-avtomobilya — Набор для химчистки автомобиля

**Priority:** MEDIUM (volume 690)
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
| набор для химчистки автомобиля | 170 |
| набор для химчистки салона | 140 |
| набор для химчистки авто | 140 |
| набор для чистки салона автомобиля | 110 |
| наборы автокосметики | 40 |
| подарочный набор для авто | 20 |
| авто набор в машину | 20 |
| набор для химчистки салона авто | 20 |
| набор для чистки машины | 20 |
| набор химии для автомобиля | 10 |

**Total:** 10

---

## Stage 01: Init ⬜

- [ ] Папка создана: `categories/nabor-dlya-khimchistki-avtomobilya/`
- [ ] `data/nabor-dlya-khimchistki-avtomobilya_clean.json` создан
- [ ] Keywords кластеризованы
- [ ] `meta/nabor-dlya-khimchistki-avtomobilya_meta.json` template
- [ ] `content/nabor-dlya-khimchistki-avtomobilya_ru.md` placeholder
- [ ] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/nabor-dlya-khimchistki-avtomobilya/data/nabor-dlya-khimchistki-avtomobilya_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ⬜

### Inputs

- [ ] Прочитать `data/nabor-dlya-khimchistki-avtomobilya_clean.json`
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

- [ ] Записать в `meta/nabor-dlya-khimchistki-avtomobilya_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/nabor-dlya-khimchistki-avtomobilya/meta/nabor-dlya-khimchistki-avtomobilya_meta.json
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
grep -c "^## Block" categories/nabor-dlya-khimchistki-avtomobilya/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/nabor-dlya-khimchistki-avtomobilya/content/nabor-dlya-khimchistki-avtomobilya_ru.md "{keyword}" --mode seo
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
