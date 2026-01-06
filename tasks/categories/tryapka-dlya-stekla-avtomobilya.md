# tryapka-dlya-stekla-avtomobilya — Тряпка для стекла автомобиля

**Priority:** LOW (volume 110)
**Type:** Cluster
**Parent:** mikrofibra-i-tryapki

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
| тряпка для стекла автомобиля | 50 |
| тряпка для стекол авто | 20 |
| тряпка для стекол автомобиля | 20 |
| тряпка для стекол машины | 10 |
| тряпка для автомобильных стекол | 10 |

**Total:** 5

---

## Stage 01: Init ⬜

- [ ] Папка создана: `categories/tryapka-dlya-stekla-avtomobilya/`
- [ ] `data/tryapka-dlya-stekla-avtomobilya_clean.json` создан
- [ ] Keywords кластеризованы
- [ ] `meta/tryapka-dlya-stekla-avtomobilya_meta.json` template
- [ ] `content/tryapka-dlya-stekla-avtomobilya_ru.md` placeholder
- [ ] `research/RESEARCH_DATA.md` template

**Init Validation:**

```bash
python3 -c "import json; json.load(open('categories/tryapka-dlya-stekla-avtomobilya/data/tryapka-dlya-stekla-avtomobilya_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ⬜

### Inputs

- [ ] Прочитать `data/tryapka-dlya-stekla-avtomobilya_clean.json`
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

- [ ] Записать в `meta/tryapka-dlya-stekla-avtomobilya_meta.json`

### Meta Validation

```bash
python3 scripts/validate_meta.py categories/tryapka-dlya-stekla-avtomobilya/meta/tryapka-dlya-stekla-avtomobilya_meta.json
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
grep -c "^## Block" categories/tryapka-dlya-stekla-avtomobilya/research/RESEARCH_DATA.md
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
python3 scripts/validate_content.py categories/tryapka-dlya-stekla-avtomobilya/content/tryapka-dlya-stekla-avtomobilya_ru.md "{keyword}" --mode seo
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
