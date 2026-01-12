---
name: content-generator
description: >-
  Генерирует SEO-контент для категорий интернет-магазина Ultimate.net.ua.
  Использует данные из research (RESEARCH_DATA.md) для создания контента с E-E-A-T сигналами.
  Use when: /content-generator, напиши текст, сгенерируй контент, создай контент для категории,
  напиши описание категории. ВАЖНО: использовать ПОСЛЕ завершения /seo-research.
---

# Content Generator

## Quick Start

```
/content-generator {slug}
```

**Input:** `_clean.json` + `_meta.json` + `RESEARCH_DATA.md`
**Output:** `categories/{slug}/content/{slug}_ru.md`

---

## Workflow

```
1. Read data        → _clean.json (keywords, entities, micro_intents)
2. Read meta        → _meta.json (H1)
3. Read research    → RESEARCH_DATA.md (факты с источниками)
4. Write content    → по структуре ниже
5. Validate         → python scripts/validate_content.py
```

---

## Research → Content Mapping

> ⚠️ **Без источника в research → НЕ писать в контент!**

| Research блок | Content секция |
|---------------|----------------|
| Блок 1 (Что это) | **Intro** (30-60 слов) |
| Блок 2 (Виды) | **Таблица сравнения** |
| Блок 3 (Как выбрать) | **Сценарии выбора** |
| Блок 4 (Как применять) | **How-to шаги** |
| Блок 5 (Ошибки) | **Частые ошибки** |
| Блок 7 (FAQ) | **FAQ секция** |
| Блок 10 (Цифры) | **Практические данные** |
| Блок 6а (Спорные) | ⛔ НЕ публиковать без proof |

**Детали маппинга:** См. [references/research-mapping.md](references/research-mapping.md)

---

## Структура контента

```markdown
# {H1 из meta — БЕЗ "Купить"}

{Intro: 30-60 слов}

## Как выбрать {категорию}

| Тип | Плюсы | Минусы | Когда брать |
|-----|-------|--------|-------------|

**Сценарии:**
- **{Задача}** → {решение}

## Как применять

1. **{Шаг}:** {инструкция}

**Ошибки:**
- **{Ошибка}** — {последствие}

## Практические данные

| Параметр | Значение |
|----------|----------|

## FAQ

### {Вопрос}?
{Ответ 2-3 предложения}

---

**Итог:**
- Для {сценарий 1}: {рекомендация}
```

**Шаблоны по типам категорий:** См. [references/templates.md](references/templates.md)

---

## SEO Rules (January 2026)

| Правило | Значение |
|---------|----------|
| Intro | 30-60 слов (AI Direct Answer) |
| H1 | БЕЗ "Купить" |
| Tables | Обязательны |
| FAQ | 3-5 вопросов, без schema |
| E-E-A-T | Конкретные цифры из research |

---

## Validation Checklist

- [ ] H1 без "Купить"
- [ ] Intro 30-60 слов
- [ ] Таблица сравнения
- [ ] How-to с шагами
- [ ] FAQ 3-5 вопросов
- [ ] Цифры из research (расход, время)
- [ ] Primary keyword в первых 100 словах
- [ ] Нет спорных утверждений без proof

---

## Output

```
✅ Content: categories/{slug}/content/{slug}_ru.md

Следующий шаг: /uk-content-init {slug}
```

---

**Version:** 3.1 — January 2026
