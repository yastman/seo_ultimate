# antidozhd — Antidozhd

**Priority:** HIGH (volume 1000)
**Type:** L3
**Parent:** sredstva-dlya-stekol

---

## Current Status

| Stage | RU | UK |
|-------|----|----|
| 01-Init | ✅ | ✅ |
| 02-Meta | ✅ | ✅ |
| 03-Research | ⬜ | — |
| 04-Content | ⬜ | ⬜ |
| 05-UK | — | ✅ |
| 06-Quality | ⬜ | ⬜ |
| 07-Deploy | ⬜ | ⬜ |

---

## Stage 01: Init ✅

- [x] Папка создана: `categories/antidozhd/`
- [x] `data/antidozhd_clean.json` создан
- [x] Keywords кластеризованы
- [x] `meta/antidozhd_meta.json` template
- [x] `content/antidozhd_ru.md` placeholder
- [x] `research/RESEARCH_DATA.md` template

**Validation:**
```bash
python3 -c "import json; json.load(open('categories/antidozhd/data/antidozhd_clean.json')); print('PASS')"
```

---

## Stage 02: Meta ✅

### Inputs
- [ ] Прочитать `data/antidozhd_clean.json`
- [ ] Определить primary keyword
- [ ] Загрузить товары из products_with_descriptions.md

### Tasks RU
- [ ] title_ru: 50-60 chars, содержит primary keyword
- [ ] description_ru: 150-160 chars, CTA "Доставка по Украине"
- [ ] h1_ru: primary keyword (без "купить")

### Tasks UK
- [ ] title_uk: 50-60 chars
- [ ] description_uk: 150-160 chars
- [ ] h1_uk: перевод primary keyword

### Output
- [ ] Записать в `meta/antidozhd_meta.json`

### Validation
```bash
python3 scripts/validate_meta.py categories/antidozhd/meta/antidozhd_meta.json
```

---

## Stage 03: Research ⬜

### Block 1: Product Analysis
- [ ] ТОП-5 брендов
- [ ] Ценовой диапазон
- [ ] Особенности товаров

### Block 2: Competitors
- [ ] WebSearch: "{primary keyword} купить украина"
- [ ] Найти 3-5 конкурентов
- [ ] Выписать структуру контента

### Block 3: Use Cases
- [ ] Для кого?
- [ ] Какие задачи решает?
- [ ] Где применяется?

### Block 4: Buying Guide
- [ ] Критерии выбора
- [ ] На что обратить внимание

### Block 5: FAQ
- [ ] Собрать 5-7 вопросов

### Block 6: Comparison Table
- [ ] Определить критерии
- [ ] 3-5 брендов/продуктов

### Block 7: How-To
- [ ] Пошаговая инструкция
- [ ] Необходимое оборудование

### Block 8: Interlink
- [ ] Связанные категории
- [ ] Дополняющие товары

### Output
- [ ] Записать в `research/RESEARCH_DATA.md`

### Validation
```bash
grep -c "^## Block" categories/antidozhd/research/RESEARCH_DATA.md
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

### Validation
```bash
python3 scripts/validate_content.py categories/antidozhd/content/antidozhd_ru.md "{keyword}" --mode seo
```

---

## Stage 05: UK ✅

### Create Structure
- [ ] `uk/categories/antidozhd/data/`
- [ ] `uk/categories/antidozhd/meta/`
- [ ] `uk/categories/antidozhd/content/`

### Translate
- [ ] Keywords
- [ ] Meta tags
- [ ] Content

### Quality Check
- [ ] Перевод (не транслитерация)
- [ ] Терминология
- [ ] CTA на украинском

---

## Stage 06: Quality Gate ⬜

### Checklist
- [ ] Data JSON valid (RU + UK)
- [ ] Meta valid (RU + UK)
- [ ] Content valid (RU + UK)
- [ ] Research complete
- [ ] SEO compliant

### Output
- [ ] Создать `QUALITY_REPORT.md`

---

## Stage 07: Deploy ⬜

### Pre-Deploy
- [ ] Quality Gate = PASS
- [ ] Backup DB

### Deploy
- [ ] Find category_id
- [ ] UPDATE meta RU
- [ ] UPDATE content RU
- [ ] UPDATE meta UK
- [ ] UPDATE content UK

### Post-Deploy
- [ ] Clear cache
- [ ] Visual check
- [ ] Verify both languages

---

## Notes

- Parent: sredstva-dlya-stekol
- Type: L3
- Volume: 1000

---

**Last Updated:** 2025-12-31
