# gubki-i-varezhki — Губки и варежки

**Priority:** HIGH (volume 1820)
**Type:** Cluster
**Parent:** gubki-i-varezhki

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
| мочалка для автомобиля | 320 |
| мочалка для авто | 320 |
| губка для авто | 110 |
| губки для автомобиля | 110 |
| мочалка для машины | 90 |
| перчатка для мойки авто | 90 |
| перчатка для мойки автомобиля | 90 |
| губка для мойки авто | 70 |
| губки для мытья машины | 70 |
| губки для мойки автомобиля | 70 |
| мочалка для мойки автомобиля | 70 |
| мочалки для мойки авто | 70 |
| губка для машины | 50 |
| варежка для мойки авто | 40 |
| варежка для мойки автомобиля | 40 |
| мочалка для мытья машины | 30 |
| купить мочалку для мойки авто | 30 |
| перчатка для мытья машины | 30 |
| губка для мытья машины купить | 10 |
| губка для машины купить | 10 |
| купить губку для автомобиля | 10 |
| мочалка автомобильная | 10 |
| купить губку для мойки авто | 10 |
| губка для мытья автомобиля купить | 10 |
| губки автомобильные | 10 |
| губка для мойки машины | 10 |
| губка для мойки автомобиля купить | 10 |
| губка для мытья авто | 10 |
| большая губка для мытья авто | 10 |
| губки для мытья автомобиля | 10 |
| мочалка для авто цена | 0 |
| мочалка для профессиональной мойки автомобилей | 0 |
| купить мочалку для авто | 0 |
| купить мочалку для мытья авто | 0 |
| мочалка для мытья авто | 0 |
| мочалки для мойки автомобиля купить | 0 |
| мочалка для мытья автомобиля | 0 |

**Total:** 37

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/gubki-i-varezhki/`
- [x] `data/gubki-i-varezhki_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/gubki-i-varezhki_meta.json` template
- [x] `content/gubki-i-varezhki_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/gubki-i-varezhki/data/gubki-i-varezhki_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/gubki-i-varezhki_clean.json`
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

- [ ] Записать в `meta/gubki-i-varezhki_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/gubki-i-varezhki/meta/gubki-i-varezhki_meta.json
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
grep -c "^## Block" categories/gubki-i-varezhki/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/gubki-i-varezhki/content/gubki-i-varezhki_ru.md "{keyword}" --mode seo
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
