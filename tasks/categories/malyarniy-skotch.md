# malyarniy-skotch — Малярний Скотч

**Priority:** HIGH (volume 10360)
**Type:** Cluster
**Parent:** malyarniy-skotch

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
| малярные скотчи | 4400 |
| малярный скотч | 4400 |
| скотч малярний | 1000 |
| купить малярный скотч | 210 |
| малярный скотч цена | 70 |
| малярная лента | 50 |
| малярная лента купить | 50 |
| малярный скотч 10мм | 40 |
| малярный скотч 10 мм | 30 |
| малярный скотч 1 см купить | 20 |
| скотч малярный автомобильный | 20 |
| малярский скотч | 10 |
| малярный скотч стоимость | 10 |
| скотч малярный купить в украине | 10 |
| купить малярную клейкую ленту | 10 |
| купить малярный скотч для авто | 10 |
| малярный скотч для авто | 10 |
| малярный скотч широкий | 10 |

**Total:** 18

---

## Stage 01: Init ⬜

- [ ] Папка создана: `categories/malyarniy-skotch/`
- [ ] `data/malyarniy-skotch_clean.json` создан
- [ ] Keywords кластеризованы
- [ ] `meta/malyarniy-skotch_meta.json` template
- [ ] `content/malyarniy-skotch_ru.md` placeholder
- [ ] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/malyarniy-skotch/data/malyarniy-skotch_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ⬜

### Inputs

- [ ] Прочитать `data/malyarniy-skotch_clean.json`
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

- [ ] Записать в `meta/malyarniy-skotch_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/malyarniy-skotch/meta/malyarniy-skotch_meta.json
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
grep -c "^## Block" categories/malyarniy-skotch/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/malyarniy-skotch/content/malyarniy-skotch_ru.md "{keyword}" --mode seo
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
