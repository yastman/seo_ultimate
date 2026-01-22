# UK Full Pipeline Design

> **For Claude:** Используй этот документ как референс для UK pipeline. Выполнение начинается с Фазы 1.

**Goal:** Создать украинский контент для всех 50 категорий с правильной частотностью ключевых слов.

**Date:** 2026-01-22

---

## Архитектура

**Принцип:** UK pipeline зеркалирует RU, но ключи собираются отдельно, так как частотность в украинском языке отличается.

**Структура данных:**
```
uk/
├── data/
│   └── uk_keywords.json          # Все UK ключи с частотностью (после импорта)
└── categories/
    └── {slug}/
        ├── data/{slug}_clean.json   # UK семантика (keywords, synonyms)
        ├── meta/{slug}_meta.json    # UK мета-теги (Title, Description, H1)
        ├── content/{slug}_uk.md     # UK контент (buyer guide)
        └── research/CONTEXT.md      # Ссылка на RU research
```

**Ключевые отличия от RU:**
- Research НЕ дублируется — используем RU research как source of truth
- Ключи собираются с украинской частотностью
- Терминология: резина→гума, мойка→миття, стекло→скло
- Title обязательно содержит "Купити", H1 — без "Купити"

---

## Workflow (Этапы)

### Фаза 0: Подготовка инфраструктуры ✅

Все скиллы и агенты созданы:
- uk-keywords-export, uk-keywords-import
- uk-category-init, uk-content-init
- uk-generate-meta, uk-seo-research
- uk-content-generator, uk-content-reviewer
- uk-quality-gate, uk-deploy-to-opencart

### Фаза 1: Сбор UK ключей

```
/uk-keywords-export → [Пользователь собирает частотность] → /uk-keywords-import
```

| Шаг | Действие | Результат |
|-----|----------|-----------|
| 1.1 | `/uk-keywords-export` | `data/generated/UK_KEYWORDS_FOR_FREQUENCY.md` |
| 1.2 | Пользователь загружает в KeySO/Serpstat | CSV с частотностью |
| 1.3 | `/uk-keywords-import {csv}` | `uk/data/uk_keywords.json` |

### Фаза 2: Генерация UK контента (×50 категорий)

```
/uk-category-init → /uk-generate-meta → /uk-content-generator → uk-content-reviewer → /uk-quality-gate → git commit
```

| Шаг | Команда | Результат |
|-----|---------|-----------|
| 2.1 | `/uk-category-init {slug}` | Структура папок + `_clean.json` |
| 2.2 | `/uk-generate-meta {slug}` | `_meta.json` (Title, Description, H1) |
| 2.3 | `/uk-content-generator {slug}` | `{slug}_uk.md` |
| 2.4 | `uk-content-reviewer {slug}` | Ревизия и фиксы |
| 2.5 | `/uk-quality-gate {slug}` | Финальная валидация |
| 2.6 | `git commit` | Фиксация результата |

### Фаза 3: Деплой

```
/uk-deploy {slug}
```

---

## Фаза 1: Детали сбора ключей

### Шаг 1.1: Экспорт ключей

`/uk-keywords-export` делает:
1. Сканирует все `categories/**/data/*_clean.json` (50 файлов)
2. Извлекает: `keywords`, `synonyms`, `variations`
3. Переводит на украинский по `TRANSLATION_RULES.md`
4. Дедуплицирует
5. Сортирует по алфавиту
6. Записывает в `data/generated/UK_KEYWORDS_FOR_FREQUENCY.md`

**Формат выходного файла:**
```
активна піна
автошампунь
антибітум
антидощ
чорнитель гуми
очищувач дисків
...
```

Просто список — каждый ключ на новой строке. Удобно для загрузки в сервис сбора частотности.

### Шаг 1.2: Сбор частотности (задача пользователя)

Пользователь загружает MD файл в KeySO, Serpstat или аналог.

Результат — CSV:
```csv
keyword,volume
активна піна,1200
автошампунь,800
...
```

### Шаг 1.3: Импорт ключей

`/uk-keywords-import {path-to-csv}` делает:
1. Парсит CSV
2. Сопоставляет UK ключи с RU категориями (обратный перевод)
3. Группирует по slug категории
4. Записывает `uk/data/uk_keywords.json`

**Формат uk_keywords.json:**
```json
{
  "aktivnaya-pena": {
    "keywords": [
      {"keyword": "активна піна", "volume": 1200},
      {"keyword": "піна для безконтактної мийки", "volume": 400}
    ]
  },
  "cherniteli-shin": {
    "keywords": [
      {"keyword": "чорнитель гуми", "volume": 900}
    ]
  }
}
```

---

## Фаза 2: Batch-обработка категорий

### Стратегия

**Последовательная обработка по одной категории.**

### Порядок

1. **L3 (листовые)** — сначала (конкретная семантика, товары)
2. **L2** — после L3
3. **L1 (хабы)** — в конце (обзорные страницы)

### Цикл для каждой категории

```bash
/uk-category-init {slug}
/uk-generate-meta {slug}
/uk-content-generator {slug}
uk-content-reviewer {slug}
/uk-quality-gate {slug}
git add uk/categories/{slug}/ && git commit -m "content(uk): add {slug}"
```

### Преимущества последовательного подхода

- Полный контроль на каждом шаге
- Легко откатить если что-то не так
- Можно остановиться в любой момент
- Чистая git история

### Чеклист

Создать `tasks/TODO_UK_CONTENT.md` — список всех 50 категорий с чекбоксами для отслеживания прогресса.

---

## Список категорий (50 шт.)

### L1 Categories (7):
- aksessuary
- moyka-i-eksterer
- oborudovanie
- opt-i-b2b
- polirovka
- ukhod-za-intererom
- zashchitnye-pokrytiya

### L2/L3 Categories (43):
- aktivnaya-pena
- antibitum
- antimoshka
- antidozhd
- apparaty-tornador
- aksessuary-dlya-naneseniya-sredstv
- akkumulyatornaya
- avtoshampuni
- cherniteli-shin
- glina-i-avtoskraby
- gubki-i-varezhki
- keramika-dlya-diskov
- keramika-i-zhidkoe-steklo
- kisti-dlya-deteylinga
- kvik-deteylery
- malyarniy-skotch
- mekhovye
- mikrofibra-i-tryapki
- nabory
- neytralizatory-zapakha
- obezzhirivateli
- ochistiteli-diskov
- ochistiteli-dvigatelya
- ochistiteli-kozhi
- ochistiteli-shin
- ochistiteli-stekol
- omyvatel
- polirol-dlya-stekla
- poliroli-dlya-plastika
- polirovalnye-pasty
- pyatnovyvoditeli
- raspyliteli-i-penniki
- shampuni-dlya-ruchnoy-moyki
- shchetka-dlya-moyki-avto
- silanty
- sredstva-dlya-khimchistki-salona
- sredstva-dlya-kozhi
- tverdyy-vosk
- ukhod-za-kozhey
- ukhod-za-naruzhnym-plastikom
- vedra-i-emkosti
- voski
- zhidkiy-vosk

---

## Критерии приёмки (Acceptance Criteria)

### Фаза 1 завершена когда:

- [ ] `data/generated/UK_KEYWORDS_FOR_FREQUENCY.md` создан
- [ ] Содержит все уникальные ключи на украинском
- [ ] Пользователь вернул CSV с частотностью
- [ ] `uk/data/uk_keywords.json` создан и содержит ключи по категориям

### Фаза 2 завершена для категории когда:

- [ ] `uk/categories/{slug}/data/{slug}_clean.json` — UK ключи
- [ ] `uk/categories/{slug}/meta/{slug}_meta.json` — Title с "Купити", H1 без "Купити"
- [ ] `uk/categories/{slug}/content/{slug}_uk.md` — контент ≥2KB
- [ ] Терминология корректна (гума, миття, скло — не резина, мойка, стекло)
- [ ] `/uk-quality-gate` прошёл без ошибок
- [ ] Коммит создан

### Весь UK pipeline завершён когда:

- [ ] 50 категорий обработаны
- [ ] `tasks/TODO_UK_CONTENT.md` — все чекбоксы отмечены
- [ ] Финальный коммит: `content(uk): complete all 50 categories`

---

## Следующий шаг

Начать с Фазы 1:
```
/uk-keywords-export
```

---

**Version:** 1.0
