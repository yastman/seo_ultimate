# Stage 03: SEO Research

**Skill:** `/seo-research {slug}`
**Progress:** 13/51 RU

---

## Checklist per Category

### Pre-flight

- [ ] `meta/{slug}_meta.json` готов (Stage 02 completed)
- [ ] Primary keyword известен
- [ ] Определить тип категории (L2/L3/SEO-filter)

### Execution — 8 Обязательных Блоков

#### Block 1: Анализ товаров

- [ ] Открыть категорию на сайте
- [ ] Выписать ТОП-5 брендов
- [ ] Отметить ценовой диапазон
- [ ] Записать особенности товаров

#### Block 2: Конкуренты (WebSearch)

```text
Поисковые запросы:
- "{primary keyword} купить украина"
- "{primary keyword} топ 10"
- "{primary keyword} рейтинг 2024"
```

- [ ] Найти 3-5 конкурентов
- [ ] Выписать структуру их контента
- [ ] Отметить их H2/H3 заголовки

#### Block 3: Use Cases

- [ ] Для кого этот продукт?
- [ ] Какие задачи решает?
- [ ] Где применяется? (частный авто, автомойка, детейлинг)

#### Block 4: Buying Guide

- [ ] На что обратить внимание при выборе?
- [ ] Какие характеристики важны?
- [ ] Критерии качества

#### Block 5: FAQ вопросы

- [ ] Собрать 5-7 частых вопросов
- [ ] Источники: Google "Люди также спрашивают"
- [ ] Источники: форумы, отзывы

#### Block 6: Сравнение продуктов

- [ ] Определить 2-3 критерия сравнения
- [ ] Подготовить данные для таблицы
- [ ] Бренды для сравнения

#### Block 7: Инструкция по применению

- [ ] Как использовать?
- [ ] Какое оборудование нужно?
- [ ] Ошибки применения

#### Block 8: Интерлинк

- [ ] Связанные категории
- [ ] Дополняющие товары
- [ ] Родительская категория

### Validation

```bash
# Проверить наличие всех 8 блоков
grep -c "^## Block" categories/{slug}/research/RESEARCH_DATA.md
# Должно быть >= 8

# Проверить статус
grep "Status:" categories/{slug}/research/RESEARCH_DATA.md
# Должно быть "COMPLETED"
```

### Acceptance Criteria

- [ ] Все 8 блоков заполнены
- [ ] Минимум 5 FAQ вопросов
- [ ] Минимум 3 конкурента проанализированы
- [ ] Данные для comparison table есть
- [ ] Status: COMPLETED

### Post-action

- [ ] Переместить из `pending/` в `completed/`
- [ ] Обновить счётчик в `PIPELINE_STATUS.md`

---

## Pending (38)

### Нужен Meta сначала (17)

tverdyy-vosk, zhidkiy-vosk, pyatnovyvoditeli, ochistiteli-kuzova, akkumulyatornye-mashinki, avtoshampuni, sredstva-dlya-stekol, sredstva-dlya-diskov-i-shin, s-voskom, kislotnyy-shampun, zashchitnoe-pokrytie-dlya-koles, dlya-vneshnego-plastika, mikrofibra-dlya-polirovki, mikrofibra-dlya-stekol, nabory-dlya-deteylinga, porolonovye, oborudovanie

### Meta готов, Research pending (21)

polirovalnye-mashinki, malyarnyy-skotch, mikrofibra-i-tryapki, polirovalnye-pasty, polirovalnye-krugi, neytralizatory-zapakha, apparaty-tornador, raspyliteli-i-penniki, poliroli-dlya-plastika, kvik-deteylery, obezzhirivateli, voski, antidozhd, aksessuary-dlya-naneseniya, sredstva-dlya-kozhi, shchetki-i-kisti, omyvatel, polirol-dlya-stekla, vedra-i-emkosti, silanty, mekhovye

---

## Completed (13)

aktivnaya-pena, dlya-ruchnoy-moyki, ochistiteli-stekol, glina-i-avtoskraby, antimoshka, antibitum, cherniteli-shin, ochistiteli-diskov, ochistiteli-shin, dlya-khimchistki-salona, ochistiteli-dvigatelya, keramika-i-zhidkoe-steklo, gubki-i-varezhki

---

## Research Template

```markdown
# Research: {slug}

## Status: COMPLETED
## Date: 2025-XX-XX

---

## Block 1: Product Analysis
- Brands: ...
- Price range: ...
- Features: ...

## Block 2: Competitors
| Site | URL | Content Structure |
|------|-----|-------------------|
| ... | ... | ... |

## Block 3: Use Cases
- Target audience: ...
- Problems solved: ...
- Applications: ...

## Block 4: Buying Guide
- Key factors: ...
- Quality criteria: ...

## Block 5: FAQ
1. ...?
2. ...?
3. ...?
4. ...?
5. ...?

## Block 6: Comparison
| Brand | Feature 1 | Feature 2 | Price |
|-------|-----------|-----------|-------|

## Block 7: How-to
1. Step...
2. Step...

## Block 8: Interlink
- Related: [category1], [category2]
- Complementary: ...
- Parent: ...
```
