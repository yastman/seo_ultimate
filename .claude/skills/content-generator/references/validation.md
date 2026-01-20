# Validation Checklist

Финальная проверка перед сдачей контента.

---

## Команды валидации

```bash
# Плотность ключей и переспам
python3 scripts/check_keyword_density.py categories/{slug}/content/{slug}_ru.md

# Тошнота и вода
python3 scripts/check_water_natasha.py categories/{slug}/content/{slug}_ru.md

# SEO валидация
python3 scripts/validate_content.py categories/{slug}/content/{slug}_ru.md "{primary_keyword}" --mode seo
```

---

## Метрики

| Метрика | Цель | Блокер |
|---------|------|--------|
| Stem-группа ключа | ≤2.5% | >3.0% = SPAM |
| Классическая тошнота | ≤3.5 | >4.0 |
| Вода | 40-65% | >75% |

---

## Checklist: Коммерческий интент

- [ ] **Первый H2 = "Как выбрать" / "Сценарии"**
- [ ] **Паттерн "Если X → Y"** минимум 3 раза
- [ ] **Таблица Задача → Тип → Почему** (3 колонки!)
- [ ] **Итог с рекомендациями по сценариям**
- [ ] **НЕТ секции "Как применять" с 5+ шагами**
- [ ] **НЕТ секции "Типы X" как справочник**

---

## Checklist: Заголовки H1/H2/H3

- [ ] **H1 = `name` из `_clean.json`** (не primary keyword!)
- [ ] H1 без "Купить"
- [ ] **H2 содержит secondary keyword** (минимум 1 H2)
- [ ] H3 в FAQ — вопросы про выбор (из RESEARCH_DATA.md или шаблоны)
- [ ] Intro 40-60 слов (без "мы предлагаем")

---

## Checklist: Распределение ключей

| Источник | Где | Проверить |
|----------|-----|-----------|
| `keywords_in_content.primary[0]` | H1 + intro | BLOCKER если нет |
| `keywords_in_content.primary[1-2]` | Intro или body | 1 каждый |
| `keywords_in_content.secondary` | **H2 заголовки** | Минимум 1 H2 |
| `keywords_in_content.supporting` | Таблицы, body, FAQ | 1-2 |
| `synonyms` (без meta_only) | По тексту | 1-2 |
| `entities` | Таблицы, FAQ | 3-4 минимум |

**Проверка покрытия:**
```bash
grep -i "ключ1\|ключ2\|ключ3" categories/{slug}/content/{slug}_ru.md
```

---

## Checklist: Качество контента

- [ ] **Нет спорных утверждений без смягчения**
- [ ] **Нет брендов/процентов/точных цифр**
- [ ] **RU-first:** русский термин первым, англ. в скобках
- [ ] **Без "коммерческих" ключей в body** (купить, цена, заказать)
- [ ] **3-4 entity-термина** из `_clean.json` → `entities`

---

## Checklist: Тошнота и переспам

- [ ] Stem-группы ≤2.5%
- [ ] Классическая тошнота ≤3.5
- [ ] Тематические слова разбавлены синонимами (см. lsi-synonyms.md)

---

## Известные ограничения

| Ограничение | Что делать |
|-------------|------------|
| Grammar check требует Java | Не блокер — пропускается |
| `--mode quality` даёт WARNING по "Water" | Для SEO — не критично |

---

**Version:** 1.1 — January 2026 (убраны micro_intents, уточнено распределение ключей)
