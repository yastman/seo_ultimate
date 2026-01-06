# ochistiteli-kuzova — Очистители кузова

**Priority:** MEDIUM (volume 920)
**Type:** Cluster
**Parent:** glina-i-avtoskraby

---

## Current Status

| Stage | RU | UK |
|-------|----|----|
| 01-Init | ✅ | ⬜ |
| 02-Meta | ✅ | ⬜ |
| 03-Research | ✅ | — |
| 04-Content | ⬜ | ⬜ |
| 05-UK | — | ⬜ |
| 06-Quality | ⬜ | ⬜ |
| 07-Deploy | ⬜ | ⬜ |

---

## Keywords (из CSV)

| Keyword | Volume |
|---------|--------|
| химия для мойки авто | 590 |
| очиститель кузова авто | 70 |
| очиститель кузова автомобиля | 70 |
| автохимия для кузова | 50 |
| очиститель кузова | 40 |
| средство для очистки кузова авто | 20 |
| средство для очистки кузова автомобиля | 10 |
| автохимия очиститель кузова | 10 |
| купить очиститель кузова | 10 |
| купить очиститель кузова автомобиля | 10 |
| универсальный очиститель кузова | 10 |
| химия для кузова авто | 10 |
| химия для кузова автомобиля | 10 |
| автокосметика для кузова | 10 |
| очистители кузова цена | 0 |
| универсальный очиститель для кузова авто | 0 |

**Total:** 16

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/ochistiteli-kuzova/`
- [x] `data/ochistiteli-kuzova_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/ochistiteli-kuzova_meta.json` template
- [x] `content/ochistiteli-kuzova_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/ochistiteli-kuzova/data/ochistiteli-kuzova_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/ochistiteli-kuzova_clean.json`
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

- [ ] Записать в `meta/ochistiteli-kuzova_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/ochistiteli-kuzova/meta/ochistiteli-kuzova_meta.json
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
grep -c "^## Block" categories/ochistiteli-kuzova/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/ochistiteli-kuzova/content/ochistiteli-kuzova_ru.md "{keyword}" --mode seo
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
