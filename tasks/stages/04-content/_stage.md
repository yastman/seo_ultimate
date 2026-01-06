# Stage 04: Content Generation

**Skill:** `/content-generator {slug}`
**Progress:** 13/51 RU | 13/51 UK

---

## Checklist per Category

### Pre-flight

- [ ] `research/RESEARCH_DATA.md` готов (Status: COMPLETED)
- [ ] `meta/{slug}_meta.json` готов
- [ ] `data/{slug}_clean.json` готов
- [ ] Прочитать все 3 файла

### Content Structure (обязательные секции)

#### 1. Intro (150-200 слов)

- [ ] H1 = primary keyword
- [ ] Первый абзац содержит primary keyword
- [ ] Упомянуть преимущества категории
- [ ] CTA к каталогу

#### 2. Buying Guide (H2)

- [ ] Заголовок с secondary keyword
- [ ] 3-5 критериев выбора
- [ ] Практические советы

#### 3. Comparison Table

- [ ] Минимум 3 товара/бренда
- [ ] 3-4 характеристики
- [ ] Markdown table format

#### 4. How-To Section (H2)

- [ ] Пошаговая инструкция
- [ ] 5-7 шагов
- [ ] Упомянуть supporting keywords

#### 5. FAQ (H2)

- [ ] Минимум 5 вопросов
- [ ] Формат Q&A
- [ ] Ответы 50-100 слов

#### 6. Conclusion

- [ ] Краткое резюме
- [ ] CTA к покупке
- [ ] Ссылки на связанные категории

### SEO Requirements

- [ ] Primary keyword: 3-5 раз в тексте
- [ ] Secondary keywords: по 1-2 раза
- [ ] Commercial keywords: ТОЛЬКО в meta, НЕ в тексте!
- [ ] Общий объём: 1500-2500 слов
- [ ] Density: 1.5-2.5%

### Validation Script

```bash
python3 scripts/validate_content.py \
  categories/{slug}/content/{slug}_ru.md \
  "{primary_keyword}" \
  --mode seo
```

**Что проверяет скрипт:**

| Check | Rule | Status |
|-------|------|--------|
| word_count | 1500-2500 | ✅/❌ |
| keyword_density | 1.5-2.5% | ✅/❌ |
| h2_count | >= 4 | ✅/❌ |
| faq_count | >= 5 | ✅/❌ |
| table_exists | yes | ✅/❌ |
| intro_length | 150-200 words | ✅/❌ |

### Acceptance Criteria

- [ ] Exit code 0 от validate_content.py
- [ ] Все обязательные секции присутствуют
- [ ] Нет commercial keywords в тексте
- [ ] Keyword density в норме
- [ ] Таблица сравнения есть

### Post-action

- [ ] Переместить из `pending/` в `completed/`
- [ ] Обновить счётчик в `PIPELINE_STATUS.md`
- [ ] Запустить Stage 05 (UK) для этой категории

---

## Pending (38)

### Blocked by Research (38)

_Все категории ожидают завершения Stage 03_

---

## Completed (13)

aktivnaya-pena, dlya-ruchnoy-moyki, ochistiteli-stekol, glina-i-avtoskraby, antimoshka, antibitum, cherniteli-shin, ochistiteli-diskov, ochistiteli-shin, dlya-khimchistki-salona, ochistiteli-dvigatelya, keramika-i-zhidkoe-steklo, gubki-i-varezhki

---

## Content Template

```markdown
# {H1 — Primary Keyword}

{Intro paragraph — 150-200 слов, primary keyword в первом предложении}

## Как выбрать {secondary keyword}

{Buying guide — критерии выбора}

### Сравнение {products}

| Бренд | Особенность 1 | Особенность 2 | Цена |
| ----- | ------------- | ------------- | ---- |
| ...   | ...           | ...           | ...  |

## Как использовать {supporting keyword}

1. Шаг 1...
2. Шаг 2...
   ...

## Частые вопросы

### Вопрос 1?

Ответ...

### Вопрос 2?

Ответ...

...

## Заключение

{Резюме + CTA}
```

---

## Common Issues

| Issue               | Solution                  |
| ------------------- | ------------------------- |
| density > 2.5%      | Убрать повторы keyword    |
| density < 1.5%      | Добавить keyword в H2/FAQ |
| < 1500 слов         | Расширить FAQ и How-To    |
| > 2500 слов         | Сократить, убрать воду    |
| commercial в тексте | Удалить "купить/цена"     |
