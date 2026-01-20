# Дизайн: Пакетная генерация RESEARCH_PROMPT.md

**Дата:** 2026-01-20
**Статус:** Утверждён

---

## Цель

Сгенерировать RESEARCH_PROMPT.md для 16 категорий без research через параллельных агентов, чтобы затем прогнать их через Perplexity Deep Research.

---

## Категории (16 шт.)

| Группа | Категории | Статус |
|--------|-----------|--------|
| 1 | antidozhd, zashchitnye-pokrytiya, keramika-dlya-diskov, kislotnyy | ⏳ |
| 2 | kvik-deteylery, zhidkiy-vosk, tverdyy-vosk, silanty | ⏳ |
| 3 | podarochnyy, vedra-i-emkosti, nabory-dlya-moyki, nabory-dlya-salona | ⏳ |
| 4 | opt-i-b2b, kisti-dlya-deteylinga, polirol-dlya-stekla, shchetka-dlya-moyki-avto | ⏳ |

---

## Процесс

```
[Группа N: 4 категории]
        │
        ▼
┌───────────────────────────────────────────────┐
│  4 параллельных агента (Task tool)            │
│  Каждый выполняет логику /seo-research        │
└───────────────────────────────────────────────┘
        │
        ▼
[Output: 4 файла RESEARCH_PROMPT.md]
        │
        ▼
[Пользователь копирует в Perplexity → RESEARCH_DATA.md]
        │
        ▼
[Следующая группа]
```

---

## Что делает каждый агент

1. Читает `categories/{slug}/data/{slug}_clean.json` → keywords, entities, micro_intents
2. Находит section ID в `data/category_ids.json`
3. Извлекает товары из `data/generated/PRODUCTS_LIST.md` по section ID
4. Извлекает Product Insights:
   - Формы выпуска (гель, спрей, аэрозоль)
   - Объёмы (250мл, 500мл, 1л)
   - База (водная, силиконовая, растворитель)
   - Эффекты (матовый, глянцевый, сатиновый)
   - pH / тип (кислотный, щелочной, нейтральный)
5. Генерирует `RESEARCH_PROMPT.md` с 11 блоками исследования
6. Создаёт скелет `RESEARCH_DATA.md`

---

## Output на каждую группу

- 4 файла `categories/{slug}/research/RESEARCH_PROMPT.md`
- 4 файла `categories/{slug}/research/RESEARCH_DATA.md` (скелет)

---

## Структура RESEARCH_PROMPT.md

1. Шапка: название категории, slug, ТЗ
2. Семантика: таблица keywords, entities, micro_intents
3. Product Insights: таблица характеристик товаров
4. **11 блоков исследования:**
   - Блок 1: Что это и зачем
   - Блок 2: Виды и классификация
   - Блок 3: Как выбрать
   - Блок 4: Применение
   - Блок 5: Типичные ошибки
   - Блок 6: Безопасность
   - Блок 6а: Спорные утверждения (мифы)
   - Блок 7: FAQ
   - Блок 8: Troubleshooting
   - Блок 9: Совместимость
   - Блок 10: Цифры и метрики

---

## Правила классификации (Блок 2)

НЕ смешивать оси:
- **Ось 1 — Носитель:** водная / растворитель
- **Ось 2 — Активный компонент:** силикон / полимер / масла
- **Ось 3 — Финиш:** матовый / сатиновый / глянцевый

---

## Следующие шаги после генерации

1. Пользователь загружает RESEARCH_PROMPT.md в Perplexity Deep Research
2. Результат сохраняется в RESEARCH_DATA.md
3. Запускается `/content-generator {slug}` для генерации контента

---

## Команда запуска

```
Группа 1: запустить 4 параллельных агента для antidozhd, zashchitnye-pokrytiya, keramika-dlya-diskov, kislotnyy
```

---

## Зависимости

- `categories/{slug}/data/{slug}_clean.json` — должен существовать
- `data/category_ids.json` — маппинг slug → section ID
- `data/generated/PRODUCTS_LIST.md` — список товаров по секциям
- `.claude/agents/seo-research.md` — инструкции агента
