# mikrofibra-dlya-moyki-avto — Микрофибра для мойки авто

**Priority:** LOW (volume 260)
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
| микрофибра для полировки авто | 50 |
| набор тряпок для авто | 50 |
| супер впитывающая тряпка для авто | 40 |
| микрофибра для мойки авто | 20 |
| микрофибра для автомобиля купить | 20 |
| купить микрофибру для авто | 20 |
| микрофибра для мойки автомобиля | 20 |
| микрофибра для мытья машины | 10 |
| микрофибра для протирки авто | 10 |
| тряпка для мытья машины без воды | 10 |
| тряпка мыть машину | 10 |
| микрофибра для машины купить | 0 |

**Total:** 12

---

## Stage 01: Init ⬜

- [ ] Папка создана: `categories/mikrofibra-dlya-moyki-avto/`
- [ ] `data/mikrofibra-dlya-moyki-avto_clean.json` создан
- [ ] Keywords кластеризованы
- [ ] `meta/mikrofibra-dlya-moyki-avto_meta.json` template
- [ ] `content/mikrofibra-dlya-moyki-avto_ru.md` placeholder
- [ ] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/mikrofibra-dlya-moyki-avto/data/mikrofibra-dlya-moyki-avto_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ⬜

### Inputs

- [ ] Прочитать `data/mikrofibra-dlya-moyki-avto_clean.json`
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

- [ ] Записать в `meta/mikrofibra-dlya-moyki-avto_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/mikrofibra-dlya-moyki-avto/meta/mikrofibra-dlya-moyki-avto_meta.json
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
grep -c "^## Block" categories/mikrofibra-dlya-moyki-avto/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/mikrofibra-dlya-moyki-avto/content/mikrofibra-dlya-moyki-avto_ru.md "{keyword}" --mode seo
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
