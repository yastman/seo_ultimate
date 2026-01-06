# Stage 02: Meta Tags

**Skill:** `/generate-meta {slug}`
**Progress:** 34/51 RU | 34/51 UK

---

## Checklist per Category

### Pre-flight

- [ ] `data/{slug}_clean.json` существует и валиден
- [ ] Прочитать primary keywords и volumes
- [ ] Загрузить товары из `products_with_descriptions.md`

### Execution

- [ ] Сгенерировать **title RU** (50-60 символов)
  - Формула: `{Primary Keyword} | Купить в Ultimate`
  - Включить: primary keyword + commercial intent
- [ ] Сгенерировать **description RU** (150-160 символов)
  - Включить: primary + secondary keyword
  - CTA: "Доставка по Украине"
- [ ] Сгенерировать **h1 RU**
  - Точное совпадение с primary keyword
  - Без commercial слов
- [ ] То же для **UK** версии
- [ ] Записать в `meta/{slug}_meta.json`

### Validation Script

```bash
python3 scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json
```

**Что проверяет скрипт:**

| Check | Rule | Status |
|-------|------|--------|
| title_ru length | 50-60 chars | ✅/❌ |
| title_uk length | 50-60 chars | ✅/❌ |
| description_ru length | 150-160 chars | ✅/❌ |
| description_uk length | 150-160 chars | ✅/❌ |
| h1_ru exists | not empty | ✅/❌ |
| h1_uk exists | not empty | ✅/❌ |
| keyword in title | primary keyword present | ✅/❌ |
| keyword in h1 | primary keyword present | ✅/❌ |

### Acceptance Criteria

- [ ] Exit code 0 от validate_meta.py
- [ ] title содержит primary keyword
- [ ] description содержит CTA
- [ ] h1 НЕ содержит "купить/цена"
- [ ] UK версия — перевод, не транслитерация

### Post-action

- [ ] Переместить из `pending/` в `completed/`
- [ ] Обновить счётчик в `PIPELINE_STATUS.md`

---

## Pending (17)

| Slug | Volume | Priority |
|------|--------|----------|
| tverdyy-vosk | 1000+ | HIGH |
| pyatnovyvoditeli | 2400 | HIGH |
| ochistiteli-kuzova | 590 | HIGH |
| zhidkiy-vosk | 480+ | MEDIUM |
| avtoshampuni | 480 | MEDIUM |
| nabory-dlya-deteylinga | 260 | MEDIUM |
| akkumulyatornye-mashinki | 260 | MEDIUM |
| oborudovanie | 90 | LOW |
| kislotnyy-shampun | 70 | LOW |
| mikrofibra-dlya-polirovki | 50 | LOW |
| mikrofibra-dlya-stekol | 50 | LOW |
| dlya-vneshnego-plastika | 40 | LOW |
| zashchitnoe-pokrytie-dlya-koles | 10 | LOW |
| sredstva-dlya-stekol | L2 | LOW |
| sredstva-dlya-diskov-i-shin | L2 | LOW |
| s-voskom | SEO | LOW |
| porolonovye | L3 | LOW |

---

## Completed (34)

aktivnaya-pena, aksessuary-dlya-naneseniya, antibitum, antidozhd, antimoshka, apparaty-tornador, cherniteli-shin, dlya-khimchistki-salona, dlya-ruchnoy-moyki, glina-i-avtoskraby, gubki-i-varezhki, keramika-i-zhidkoe-steklo, kvik-deteylery, malyarnyy-skotch, mekhovye, mikrofibra-i-tryapki, neytralizatory-zapakha, obezzhirivateli, ochistiteli-diskov, ochistiteli-dvigatelya, ochistiteli-shin, ochistiteli-stekol, omyvatel, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-krugi, polirovalnye-mashinki, polirovalnye-pasty, raspyliteli-i-penniki, shchetki-i-kisti, silanty, sredstva-dlya-kozhi, vedra-i-emkosti, voski

---

## Common Issues

| Issue | Solution |
|-------|----------|
| title > 60 chars | Сократить, убрать лишние слова |
| description > 160 | Переформулировать CTA |
| keyword не в h1 | Использовать primary из _clean.json |
| UK = транслит | Перевести правильно |
