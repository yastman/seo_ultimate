# polirovalnye-pasty — Полировальные пасты

**Priority:** HIGH (volume 4160)
**Type:** Cluster
**Parent:** polirovalnye-pasty

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
| полировочная паста | 1600 |
| полировочная паста для авто | 590 |
| паста для полировки | 320 |
| полировочная паста для авто от царапин | 260 |
| купить пасту для полировки авто | 260 |
| полировочная паста для автомобиля | 170 |
| купить полировочную пасту | 140 |
| купить полировочную пасту для автомобиля | 110 |
| купить полировочную пасту для авто | 110 |
| купить полировальную пасту для автомобиля | 80 |
| полировальная паста купить | 60 |
| купить полировальную пасту для авто | 50 |
| паста для автомобиля | 50 |
| паста для полировки кузова | 40 |
| полироль паста для авто | 30 |
| полировочная паста для кузова авто | 20 |
| полировальная паста для автомобиля | 20 |
| купить пасту для полировки автомобиля | 20 |
| паста для полировки кузова автомобиля | 20 |
| паста для полировки машины | 20 |
| паста для полировки кузова авто | 20 |
| пасты полировальные для авто | 20 |
| полировочная паста для кузова | 20 |
| полировочная паста для кузова автомобиля | 20 |
| полировальная паста для кузова автомобиля | 20 |
| пасты для полировки авто | 20 |
| полировальная паста | 20 |
| полировочная паста для машины | 10 |
| полировочная паста для авто цена | 10 |
| паста для полировки автомобиля | 10 |
| паста авто | 10 |
| паста для полировки авто машинкой | 10 |

**Total:** 32

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/polirovalnye-pasty/`
- [x] `data/polirovalnye-pasty_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/polirovalnye-pasty_meta.json` template
- [x] `content/polirovalnye-pasty_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/polirovalnye-pasty/data/polirovalnye-pasty_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/polirovalnye-pasty_clean.json`
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

- [ ] Записать в `meta/polirovalnye-pasty_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/polirovalnye-pasty/meta/polirovalnye-pasty_meta.json
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
grep -c "^## Block" categories/polirovalnye-pasty/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/polirovalnye-pasty/content/polirovalnye-pasty_ru.md "{keyword}" --mode seo
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
