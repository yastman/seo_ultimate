# glina-i-avtoskraby — Глина и автоскрабы

**Priority:** HIGH (volume 1090)
**Type:** L3
**Parent:** ochistiteli-kuzova

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
| глина для авто | 390 |
| синяя глина для авто | 140 |
| автоскраб | 90 |
| глина для чистки авто | 50 |
| глина для чистки автомобиля | 40 |
| голубая глина для авто | 20 |
| автомобильная глина | 20 |
| глина для кузова автомобиля | 20 |
| глина для полировки автомобиля | 20 |
| глина для кузова авто | 20 |
| купить синюю глину для авто | 20 |
| глина для полировки авто | 20 |
| автоскраб купить | 20 |
| глина для полировки | 10 |
| глина для кузова | 10 |
| глина для мойки авто | 10 |
| глина для удаления загрязнений автомобиля | 10 |
| глина для чистки машины | 10 |
| очищающая глина для кузова автомобиля | 10 |
| глина для очистки кузова автомобиля | 10 |
| глина для очистки авто | 10 |
| глина для очистки кузова авто | 10 |
| очищающая глина для авто | 10 |
| купить глину для автомобиля | 10 |
| глина для очистки кузова автомобиля купить | 10 |
| купить глину для полировки авто | 10 |
| купить глину для очистки авто | 10 |
| авто глина купить | 10 |
| глина для полировки автомобиля купить | 10 |
| полимерная глина для авто | 10 |
| глина для очистки кузова | 10 |
| глина для машины | 10 |
| глина для мытья машины | 10 |
| глина для очистки автомобиля | 10 |
| полировочная глина для авто | 10 |
| глина для авто цена | 0 |
| глина для чистки авто купить | 0 |
| глина автоскраб | 0 |
| глина для авто украина | 0 |

**Total:** 39

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/glina-i-avtoskraby/`
- [x] `data/glina-i-avtoskraby_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/glina-i-avtoskraby_meta.json` template
- [x] `content/glina-i-avtoskraby_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs

- [ ] Прочитать `data/glina-i-avtoskraby_clean.json`
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

- [ ] Записать в `meta/glina-i-avtoskraby_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/glina-i-avtoskraby/meta/glina-i-avtoskraby_meta.json
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
grep -c "^## Block" categories/glina-i-avtoskraby/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/glina-i-avtoskraby/content/glina-i-avtoskraby_ru.md "{keyword}" --mode seo
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
