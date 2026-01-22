---
name: uk-content-adapter
description: >-
  Адаптирует RU контент на украинский с интеграцией UK ключей.
  НЕ полный рерайт — адаптация структуры с переводом по TRANSLATION_RULES.md.
  Use when: /uk-content-adapter, адаптуй контент на UK, переклади категорію,
  создай украинскую версию контента. ВАЖНО: использовать ПОСЛЕ /uk-content-init.
---

# UK Content Adapter v1.0

## Quick Start

```
/uk-content-adapter {slug}
```

**Input:**
- `categories/{slug}/content/{slug}_ru.md` (RU контент)
- `categories/{slug}/research/RESEARCH_DATA.md` (Research)
- `uk/categories/{slug}/data/{slug}_clean.json` (UK ключи)
- `uk/categories/{slug}/meta/{slug}_meta.json` (UK H1)

**Output:** `uk/categories/{slug}/content/{slug}_uk.md`

---

## Принцип: Адаптация, НЕ рерайт

**КРИТИЧНО:** Это НЕ генерация с нуля. Это адаптация существующего RU контента.

| Что делаем | Что НЕ делаем |
|------------|---------------|
| Переводим текст RU → UK | Генерируем новый контент |
| Интегрируем UK ключи | Меняем структуру |
| Сохраняем таблицы/FAQ | Добавляем новые секции |
| Адаптируем терминологию | Удаляем секции |

---

## Workflow

```
1. Read RU content    → categories/{slug}/content/{slug}_ru.md
2. Read UK keywords   → uk/categories/{slug}/data/{slug}_clean.json
3. Read UK meta       → uk/categories/{slug}/meta/{slug}_meta.json (H1)
4. Read research      → categories/{slug}/research/RESEARCH_DATA.md (FAQ)
5. Translate          → по TRANSLATION_RULES.md
6. Integrate keywords → по правилам ниже
7. Write UK content   → uk/categories/{slug}/content/{slug}_uk.md
8. Validate           → validate_content.py --mode seo
```

---

## Интеграция UK ключей

### Источники ключей

| Файл | Что берём |
|------|-----------|
| `uk/.../meta/{slug}_meta.json` | H1 (primary keyword) |
| `uk/.../data/{slug}_clean.json` | keywords.primary, secondary, supporting |

### Распределение ключей по контенту

| Место | Какие ключи | Обязательно |
|-------|-------------|-------------|
| **H1** | `h1` из meta (primary) | BLOCKER |
| **Intro** | primary + 1 secondary | BLOCKER |
| **H2 (минимум 1)** | secondary keyword | WARNING |
| **Таблицы** | supporting keywords | INFO |
| **FAQ** | secondary/supporting | INFO |
| **Итог** | primary | INFO |

### Пример интеграции

**RU (`_ru.md`):**
```markdown
# Чернитель резины
Чернитель резины возвращает насыщенный цвет боковине шин...
```

**UK (`_uk.md`):**
```markdown
# Чорнитель гуми
Чорнитель гуми повертає насичений колір боковині шин...
```

---

## Правила перевода

### Reference

Полный словарь: [../uk-content-init/TRANSLATION_RULES.md](../uk-content-init/TRANSLATION_RULES.md)

### Quick Reference

| RU | UK | Важно |
|----|----|----|
| резина | гума | ОБЯЗАТЕЛЬНО! |
| средство | засіб | |
| мойка (процесс) | миття | |
| мойка (место) | мийка | |
| стекло | скло | |
| чернитель | чорнитель | |
| очиститель | очищувач | |
| воск | віск | |
| защита | захист | |
| блеск | блиск | |

### Латиница (без перевода)

Оставляем как есть:
- pH, PPF, APC, SiO2, TiO2
- Термины в скобках: "гідрофобність (hydrophobic)"

**Правило:** Латиница в body только в скобках. Запрещено в H1/H2/H3.

---

## Адаптация терминологии

### Reference

Детальные правила: [references/adaptation-rules.md](references/adaptation-rules.md)

### Ключевые принципы

1. **Семантическая адаптация** — НЕ пословный перевод
2. **Сохранение интента** — commercial/informational
3. **UK ключи приоритетнее** — если в UK ядре другая формулировка
4. **Числа** — оставлять как есть (диапазоны из RU)

### Коммерческие ключи

| RU | UK | Где использовать |
|----|----|----|
| купить | купити | ТОЛЬКО в meta (Title) |
| цена | ціна | ТОЛЬКО в meta |
| заказать | замовити | ТОЛЬКО в meta |

**Запрещено:** коммерческие ключи в body текста.

---

## Структура UK контента

### Шаблон

```markdown
# {H1 з meta — БЕЗ "Купити"}

{Intro: що це + навіщо + ключове правило + 1 фраза про вибір фінішу}

## Як обрати {категорію}

| Тип | Особливості | Для кого |
|-----|-------------|----------|

**Сценарії:**
- **Якщо {X}** → обирайте {Y}

## Особливості використання *(коротко, 1-2 абзаци)*

{Профтермін} — {пояснення для вибору, НЕ інструкція}.

## FAQ

### {Питання про вибір}?
{Відповідь 2-3 речення}

---

**Підсумок:**
- Якщо {сценарій 1}: {рекомендація}
```

### Важливо

- **H1** = з meta, БЕЗ "Купити"
- **Intro** = 30-60 слів
- **H2** = мінімум 1 з secondary keyword
- **FAQ** = з RESEARCH_DATA.md або шаблони
- **Таблиці** = перекладені з RU

---

## Validation

### Команда валидации

```bash
python3 scripts/validate_content.py uk/categories/{slug}/content/{slug}_uk.md "{primary_keyword_uk}" --mode seo
```

### Checklist

- [ ] H1 = з meta (БЕЗ "Купити")
- [ ] Intro 30-60 слів
- [ ] Мінімум 1 H2 містить secondary keyword
- [ ] Таблиці перекладені
- [ ] FAQ перекладений
- [ ] Термінологія за TRANSLATION_RULES.md
- [ ] резина → гума (ОБОВ'ЯЗКОВО!)
- [ ] Латиниця тільки в дужках

---

## Common Mistakes

| Помилка | Правильно |
|---------|-----------|
| резина → резина | резина → гума |
| Латиниця в H2 | Тільки кирилиця в заголовках |
| Новий контент замість перекладу | Адаптація існуючого |
| Коммерційні ключі в body | Тільки в meta (Title) |
| Зміна структури | Зберігати структуру RU |

---

## Output

```
 Content: uk/categories/{slug}/content/{slug}_uk.md
 Validated: python3 scripts/validate_content.py {path} "{primary_keyword_uk}" --mode seo

Наступний крок: /quality-gate {slug}
```

---

**Version:** 1.0 — January 2026
