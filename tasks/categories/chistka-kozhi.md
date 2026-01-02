# chistka-kozhi — Чистка кожи

**Priority:** MEDIUM (volume 340)
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
| средства для чистки кожи автомобиля | 70 |
| средство для чистки кожи авто | 70 |
| химия для чистки кожи авто | 20 |
| купить очиститель кожи авто | 20 |
| средство для очистки кожи авто | 20 |
| средства для чистки кожаного салона | 20 |
| лучшее средство для чистки кожи авто | 10 |
| очиститель кожи авто | 10 |
| купить средство для чистки кожи авто | 10 |
| средство для кожи салона | 10 |
| средство для очистки кожи салона | 10 |
| очиститель кожи салона автомобиля | 10 |
| средство для чистки кожи салона автомобиля | 10 |
| средство для химчистки кожаного салона | 10 |
| средство для чистки кожаного салона авто | 10 |
| чистящее средство для кожи авто | 10 |
| средства для чистки кожи салона авто | 10 |
| средство для химчистки кожи автомобиля | 10 |
| купить средство для кожи автомобиля | 0 |

**Total:** 19

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/chistka-kozhi/`
- [x] `data/chistka-kozhi_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/chistka-kozhi_meta.json` template
- [x] `content/chistka-kozhi_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/chistka-kozhi/data/chistka-kozhi_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/chistka-kozhi_clean.json`
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

- [ ] Записать в `meta/chistka-kozhi_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/chistka-kozhi/meta/chistka-kozhi_meta.json
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
grep -c "^## Block" categories/chistka-kozhi/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/chistka-kozhi/content/chistka-kozhi_ru.md "{keyword}" --mode seo
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
