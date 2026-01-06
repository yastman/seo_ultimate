# shchetki-dlya-khimchistki-avto — Щетки для химчистки авто

**Priority:** MEDIUM (volume 580)
**Type:** Cluster
**Parent:** shchetki-i-kisti

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
| щетка для чистки салона автомобиля | 70 |
| щетка для чистки салона авто | 70 |
| щетки для химчистки авто | 50 |
| щетка для дисков авто | 50 |
| щетка для салона авто | 40 |
| купить кисточки для детейлинга | 40 |
| щетка для чистки салона | 20 |
| щетка для чистки сидений авто | 20 |
| щетка для чистки кожи авто | 20 |
| купить щетки для чистки кожи в авто | 20 |
| щетка для кожи авто | 20 |
| кисточка для чистки салона авто | 20 |
| кисточки для химчистки авто | 20 |
| кисточка для авто | 20 |
| кисточка для автомобилей | 20 |
| щетка для мытья дисков авто | 10 |
| кисти для детейлинга | 10 |
| кисти для мойки авто | 10 |
| кисточка для машины | 10 |
| кисточки для детейлинга | 10 |
| кисточки для детейлинга авто | 10 |
| кисточки для мойки авто | 10 |
| кисточки для мытья машины | 10 |

**Total:** 23

---

## Stage 01: Init ⬜

- [ ] Папка создана: `categories/shchetki-dlya-khimchistki-avto/`
- [ ] `data/shchetki-dlya-khimchistki-avto_clean.json` создан
- [ ] Keywords кластеризованы
- [ ] `meta/shchetki-dlya-khimchistki-avto_meta.json` template
- [ ] `content/shchetki-dlya-khimchistki-avto_ru.md` placeholder
- [ ] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/shchetki-dlya-khimchistki-avto/data/shchetki-dlya-khimchistki-avto_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ⬜

### Inputs

- [ ] Прочитать `data/shchetki-dlya-khimchistki-avto_clean.json`
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

- [ ] Записать в `meta/shchetki-dlya-khimchistki-avto_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/shchetki-dlya-khimchistki-avto/meta/shchetki-dlya-khimchistki-avto_meta.json
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
grep -c "^## Block" categories/shchetki-dlya-khimchistki-avto/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/shchetki-dlya-khimchistki-avto/content/shchetki-dlya-khimchistki-avto_ru.md "{keyword}" --mode seo
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
