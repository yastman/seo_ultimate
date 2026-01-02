# shchetka-dlya-avtomobilya — Щетка для автомобиля

**Priority:** HIGH (volume 1050)
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
| щетка для автомобиля | 390 |
| щетка для мытья машины | 390 |
| щетка автомобильная | 90 |
| щетка скребок для авто | 90 |
| щетка для чистки авто | 30 |
| купить скребок для автомобиля | 30 |
| купить щетку для машины | 20 |
| щетка для мытья машины цена | 10 |
| щетки для мойки автомобилей | 0 |

**Total:** 9

---

## Stage 01: Init ⬜

- [ ] Папка создана: `categories/shchetka-dlya-avtomobilya/`
- [ ] `data/shchetka-dlya-avtomobilya_clean.json` создан
- [ ] Keywords кластеризованы
- [ ] `meta/shchetka-dlya-avtomobilya_meta.json` template
- [ ] `content/shchetka-dlya-avtomobilya_ru.md` placeholder
- [ ] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/shchetka-dlya-avtomobilya/data/shchetka-dlya-avtomobilya_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ⬜

### Inputs

- [ ] Прочитать `data/shchetka-dlya-avtomobilya_clean.json`
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

- [ ] Записать в `meta/shchetka-dlya-avtomobilya_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/shchetka-dlya-avtomobilya/meta/shchetka-dlya-avtomobilya_meta.json
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
grep -c "^## Block" categories/shchetka-dlya-avtomobilya/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/shchetka-dlya-avtomobilya/content/shchetka-dlya-avtomobilya_ru.md "{keyword}" --mode seo
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
