# Manual Keywords Import — Design Document

## Цель

Добавить 451 uncategorized ключ из `ru_semantics_master.csv` в соответствующие `_clean.json` файлы категорий.

---

## Источники данных

### Review файлы (заполнены воркерами)
```
data/generated/review/
├── 01_polirovochnye_mashinki.md  (44 ключа)
├── 02_krugi_dlya_polirovki.md    (27 ключей)
├── 03_pasty.md                   (13 ключей)
├── 04_vosk.md                    (15 ключей)
├── 06_khimchistka.md             (38 ключей)
├── 07_avtokhimiya.md             (47 ключей)
├── 08_gubki_shchetki.md          (31 ключей)
├── 09_prochee_part1.md           (78 ключей)
├── 09_prochee_part2.md           (78 ключей)
└── 09_prochee_part3.md           (80 ключей)
```

### Формат review файла
```markdown
| keyword | volume | type | decision |
|---------|--------|------|----------|
| пасты для полировки авто | 1000 | keyword | polirovalnye-pasty |
| автохимия | 2400 | keyword | HOME |
| полировочная машинка | 6600 | keyword | NEW:polirovalnye-mashinki |
```

### Decision типы
- `{slug}` — добавить в существующую категорию
- `HOME` — пропустить (общие ключи для главной)
- `NEW:{slug}` — создать новую категорию
- пусто — пропустить

---

## Распределение по категориям

### Пропускаем (HOME) — ~58 ключей
Общие ключи типа "автохимия", "автокосметика" — не добавляем.

### Новые категории — 2 шт
| Категория | Ключей | Действие |
|-----------|--------|----------|
| polirovalnye-mashinki | 37 | Создать _clean.json |
| polirovalnye-krugi | 26 | Проверить/создать |

### Существующие категории — топ-20
| Категория | Ключей |
|-----------|--------|
| sredstva-dlya-khimchistki-salona | ~46 |
| aktivnaya-pena | ~38 |
| moyka-i-eksterer | ~27 |
| nabory | ~23 |
| ochistiteli-dvigatelya | ~21 |
| gubki-i-varezhki | ~17 |
| polirovalnye-pasty | ~15 |
| neytralizatory-zapakha | ~12 |
| ochistiteli-diskov | ~12 |
| glina-i-avtoskraby | ~11 |
| tverdyy-vosk | ~11 |
| ukhod-za-kozhey | ~11 |
| shchetka-dlya-moyki-avto | ~10 |
| opt-i-b2b | ~10 |
| avtoshampuni | ~9 |
| sredstva-dlya-kozhi | ~9 |
| keramika-i-zhidkoe-steklo | ~8 |
| omyvatel | ~7 |
| raspyliteli-i-penniki | ~6 |
| polirovka | ~6 |

---

## Процесс импорта для каждой категории

### Шаг 1: Извлечь ключи из review файлов
Собрать все ключи с decision = `{slug}` для данной категории.

### Шаг 2: Прочитать _clean.json
```bash
categories/{parent}/{slug}/data/{slug}_clean.json
# или
categories/{slug}/data/{slug}_clean.json
```

### Шаг 3: Проверить дубликаты
Сравнить новые ключи с существующими в:
- `keywords[]`
- `synonyms[]`
- `variations[]`

### Шаг 4: Классифицировать новые ключи
| Критерий | Куда добавлять |
|----------|----------------|
| Volume ≥ 50, основное значение | `keywords[]` |
| Volume < 50, или вариация | `synonyms[]` |
| Коммерческий (купить, цена) | `synonyms[]` с `"use_in": "meta_only"` |

### Шаг 5: Добавить через Edit tool
Сортировка: по убыванию volume внутри массива.

### Шаг 6: Отчёт
```
✅ polirovalnye-pasty: +4 keywords, +8 synonyms
```

---

## Правила добавления

### Формат записи
```json
{"keyword": "пасты для полировки авто", "volume": 1000}
{"keyword": "купить пасту", "volume": 210, "use_in": "meta_only"}
```

### Коммерческие ключи (meta_only)
Слова-маркеры: купить, цена, заказать, стоимость, недорого, дешево

### Сортировка
Внутри `keywords[]` и `synonyms[]` — по убыванию volume.

---

## Создание новых категорий

### polirovalnye-mashinki (37 ключей)
```
categories/polirovka/polirovalnye-mashinki/
├── data/polirovalnye-mashinki_clean.json
├── meta/
├── content/
└── research/
```

### Шаблон _clean.json
```json
{
  "id": "polirovalnye-mashinki",
  "name": "Полировальные машинки",
  "type": "category",
  "parent_id": "polirovka",
  "keywords": [...],
  "synonyms": [...],
  "variations": [],
  "entities": [],
  "micro_intents": [],
  "source": "manual-import"
}
```

---

## Порядок выполнения

### Фаза 1: Существующие категории (по убыванию ключей)
1. sredstva-dlya-khimchistki-salona (46)
2. aktivnaya-pena (38)
3. moyka-i-eksterer (27)
4. nabory (23)
5. ochistiteli-dvigatelya (21)
6. gubki-i-varezhki (17)
7. polirovalnye-pasty (15)
8. ...и остальные

### Фаза 2: Новые категории
1. polirovalnye-mashinki — создать структуру + добавить ключи
2. polirovalnye-krugi — проверить существование, создать если нужно

### Фаза 3: Финальная проверка
- Подсчёт добавленных ключей
- Сверка с исходными 451

---

## Ограничения

- **Master CSV НЕ ТРОГАЕМ** — только _clean.json файлы
- **HOME ключи пропускаем** — ~58 ключей не добавляем
- **NEW:porolonovye пропускаем** — только 1 ключ, не создаём категорию

---

## Отчёт (шаблон)

```markdown
## Import Report

| Категория | Было keywords | Добавлено | Стало | Было synonyms | Добавлено | Стало |
|-----------|---------------|-----------|-------|---------------|-----------|-------|
| polirovalnye-pasty | 5 | +4 | 9 | 13 | +8 | 21 |
| aktivnaya-pena | ... | ... | ... | ... | ... | ... |

**Итого:** X ключей добавлено в Y категорий
**Пропущено:** ~58 HOME ключей
**Новые категории:** polirovalnye-mashinki, polirovalnye-krugi
```
