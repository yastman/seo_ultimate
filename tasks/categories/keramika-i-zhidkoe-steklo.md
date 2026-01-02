# keramika-i-zhidkoe-steklo — Керамика и жидкое стекло

**Priority:** HIGH (volume 2500)
**Type:** Cluster
**Parent:** keramika-i-zhidkoe-steklo

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
| жидкое стекло для автомобилей | 480 |
| нанокерамика | 480 |
| нанокерамика для авто | 390 |
| нанокерамика для автомобиля | 390 |
| керамическое покрытие авто | 170 |
| купить жидкое стекло для авто | 140 |
| нано керамика на авто | 50 |
| жидкое стекло для полировки авто | 20 |
| жидкое стекло для полировки автомобиля | 20 |
| купить жидкое стекло для автомобиля | 20 |
| купить жидкое стекло для полировки авто | 20 |
| купить жидкое стекло для полировки автомобиля | 20 |
| жидкое стекло на машину | 20 |
| керамика для авто | 20 |
| нанокерамика купить | 20 |
| керамика для кузова | 20 |
| купить керамика для авто | 20 |
| купить керамику для авто в украине | 20 |
| нанокерамика для авто цена | 20 |
| покрытие жидкое стекло для авто | 10 |
| покрытие для автомобиля жидкое стекло | 10 |
| жидкое стекло для кузова авто | 10 |
| жидкое стекло на лобовое | 10 |
| купить жидкое стекло для машины | 10 |
| купить жидкое стекло для покрытия автомобиля | 10 |
| жидкое стекло на кузов | 10 |
| цена на жидкое стекло для авто | 10 |
| купить полироль жидкое стекло | 10 |
| купить жидкое стекло для кузова | 10 |
| жидкое стекло на машину цена | 10 |
| жидкое стекло полироль для автомобиля | 10 |
| нанокерамика для кузова автомобиля | 10 |
| нанокерамика на авто купить | 10 |
| нанокерамика стоимость | 10 |
| нанокерамика цена | 10 |
| покрытие для авто нанокерамика | 0 |
| нанокерамика для авто салона | 0 |
| нанокерамика покрытие | 0 |
| нанокерамика на машину | 0 |

**Total:** 39

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/keramika-i-zhidkoe-steklo/`
- [x] `data/keramika-i-zhidkoe-steklo_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/keramika-i-zhidkoe-steklo_meta.json` template
- [x] `content/keramika-i-zhidkoe-steklo_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/keramika-i-zhidkoe-steklo_clean.json`
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

- [ ] Записать в `meta/keramika-i-zhidkoe-steklo_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/keramika-i-zhidkoe-steklo/meta/keramika-i-zhidkoe-steklo_meta.json
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
grep -c "^## Block" categories/keramika-i-zhidkoe-steklo/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/keramika-i-zhidkoe-steklo/content/keramika-i-zhidkoe-steklo_ru.md "{keyword}" --mode seo
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
