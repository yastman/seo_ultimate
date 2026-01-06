# ochistiteli-dvigatelya — Очистители двигателя

**Priority:** HIGH (volume 2310)
**Type:** Cluster
**Parent:** ochistiteli-dvigatelya

---

## Current Status

| Stage | RU | UK |
|-------|----|----|
| 01-Init | ✅ | ✅ |
| 02-Meta | ✅ | ✅ |
| 03-Research | ✅ | — |
| 04-Content | ✅ | ✅ |
| 05-UK | — | ✅ |
| 06-Quality | ⬜ | ⬜ |
| 07-Deploy | ⬜ | ⬜ |

---

## Keywords (из CSV)

| Keyword | Volume |
|---------|--------|
| очиститель двигателя | 480 |
| химия для мойки двигателя | 320 |
| средства для мойки двигателя | 260 |
| очиститель двигателя от масла и грязи | 210 |
| средство для мытья двигателя | 140 |
| очиститель двигателя от масляных загрязнений | 110 |
| купить химию для мойки двигателя | 90 |
| химия для мотора | 70 |
| купить очиститель двигателя | 50 |
| химия для очистки двигателя снаружи | 40 |
| химия для мойки мотора | 40 |
| профессиональная химия для мойки двигателя | 40 |
| средство для мытья двигателя от масла | 20 |
| жидкость для мытья двигателя | 20 |
| химия для чистки двигателя | 20 |
| автохимия для двигателя | 20 |
| средство для мытья мотора | 20 |
| купить средство для мойки двигателя | 20 |
| химия для очистки двигателя | 20 |
| средство для очистки двигателя | 20 |
| средство для очистки двигателя от масла | 20 |
| очиститель двигателя от масла | 20 |
| средство для очистки двигателя снаружи | 20 |
| средство для мойки двигателя от масла | 20 |
| очиститель двигателя наружный | 20 |
| химия для мойки деталей двигателя | 20 |
| средства для мытья двигателя автомобиля | 10 |
| моющее средство для двигателя автомобиля | 10 |
| средство для мытья двигателя авто | 10 |
| автохимия для очистки двигателя | 10 |
| химия для мойки двигателя цена | 10 |
| моющее средство для мойки двигателя | 10 |
| химия для мытья двигателя | 10 |
| химия для двигателя | 10 |
| средство для мойки двигателя цена | 10 |
| средство для мойки двигателя авто | 10 |
| средства для мойки двигателя автомобиля | 10 |
| очиститель двигателя цена | 10 |
| для очистки двигателя | 10 |
| очиститель поверхности двигателя | 10 |
| очиститель двигателя автомобиля | 10 |
| купить средство для очистки двигателя | 10 |
| жидкость для очистки двигателя | 10 |
| мощный очиститель двигателя | 10 |

**Total:** 44

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/ochistiteli-dvigatelya/`
- [x] `data/ochistiteli-dvigatelya_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/ochistiteli-dvigatelya_meta.json` template
- [x] `content/ochistiteli-dvigatelya_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/ochistiteli-dvigatelya/data/ochistiteli-dvigatelya_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/ochistiteli-dvigatelya_clean.json`
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

- [ ] Записать в `meta/ochistiteli-dvigatelya_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/ochistiteli-dvigatelya/meta/ochistiteli-dvigatelya_meta.json
```

---

## Stage 03: Research ✅

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
grep -c "^## Block" categories/ochistiteli-dvigatelya/research/RESEARCH_DATA.md
```

---

## Stage 04: Content ✅

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
python3 scripts/validate_content.py categories/ochistiteli-dvigatelya/content/ochistiteli-dvigatelya_ru.md "{keyword}" --mode seo
```

---

## Stage 05: UK ✅

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
