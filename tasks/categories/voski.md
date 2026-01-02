# voski — Воски

**Priority:** HIGH (volume 2840)
**Type:** Cluster
**Parent:** voski

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
| воск для авто | 1600 |
| твердый воск для авто | 1000 |
| жидкий воск для авто | 480 |
| твердый воск | 390 |
| купить воск для авто | 320 |
| купить воск для автомобиля | 320 |
| жидкий воск | 320 |
| воск для машины | 210 |
| купить твердый воск для авто | 210 |
| воск для полировки авто | 90 |
| воск автомобильный | 90 |
| жидкий стекло цена | 90 |
| воск для мойки авто | 70 |
| купить жидкий воск для авто | 70 |
| воск для кузова авто | 50 |
| восковый полироль для авто | 50 |
| купить жидкий воск | 40 |
| купить воск для машины | 30 |
| купить воск для полировки авто | 20 |
| купить воск для мойки авто | 20 |
| купить жидкий воск для автомобиля | 20 |
| жидкий воск для автомобиля | 20 |
| купить твердый воск для авто в украине | 10 |
| твердый воск для авто цена | 10 |
| купить твердый воск для машины | 10 |
| твердый воск купить | 10 |
| твердый воск для автомобиля цена | 10 |
| твердый воск для машины | 10 |
| твердый воск цена | 10 |
| жидкий воск для кузова | 10 |
| жидкий воск для авто цена | 10 |
| жидкий воск для мойки авто | 10 |
| жидкий воск для автомойки | 10 |
| жидкий воск для машин | 10 |
| жидкий воск для кузова автомобиля | 10 |
| купить жидкий воск для машины | 10 |
| жидке стекло для авто | 10 |
| твердый воск для полировки авто | 0 |

**Total:** 38

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/voski/`
- [x] `data/voski_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/voski_meta.json` template
- [x] `content/voski_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/voski/data/voski_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/voski_clean.json`
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

- [ ] Записать в `meta/voski_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/voski/meta/voski_meta.json
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
grep -c "^## Block" categories/voski/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/voski/content/voski_ru.md "{keyword}" --mode seo
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
