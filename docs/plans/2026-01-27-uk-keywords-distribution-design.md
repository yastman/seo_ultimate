# UK Keywords Distribution Design

**Дата:** 2026-01-27
**Статус:** Approved

---

## Проблема

- 356 правильних UK ключів у CSV (`uk/data/uk_keywords_source.csv`)
- 52 UK категорії в проекті
- Старий `uk_keywords.json` містив суржик — видалено
- Потрібно розподілити ключі по категоріях з ручною перевіркою

## Рішення

Чек-лист `tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md` з:
- Секцією по кожній категорії
- Чекбоксами для підтвердження кожного ключа
- Прогрес-трекером зверху

---

## Структура чек-листа

```markdown
# UK Keywords Distribution Checklist

**Джерело:** `uk/data/uk_keywords_source.csv` (356 ключів)
**Дата:** 2026-01-27

## Прогрес
- [ ] aktivnaya-pena (0/12 ключів)
- [ ] antidozhd (0/8 ключів)
...

---

## aktivnaya-pena

**Поточні ключі в _clean.json:** (список або "немає")

**Запропоновані з CSV:**
- [ ] `активна піна для авто` (1600)
- [ ] `активна піна` (1000)
- [ ] `піна для миття авто` (1300)
...

**Статус:** ⏳ Очікує перевірки

---
```

---

## Маппінг ключів → категорій

| Слово в ключі | Категорія |
|---------------|-----------|
| `піна`, `активна піна` | aktivnaya-pena |
| `антидощ` | antidozhd |
| `антибітум`, `бітум` | antibitum |
| `антимошка`, `комах` | antimoshka |
| `торнадор` | apparaty-tornador |
| `автошампунь`, `шампунь` | avtoshampuni / shampuni-dlya-ruchnoy-moyki |
| `чорніння`, `чорнитель` | cherniteli-shin |
| `глина`, `скраб` | glina-i-avtoskraby |
| `губка`, `рукавиця` | gubki-i-varezhki |
| `кераміка для диск` | keramika-dlya-diskov |
| `кераміка`, `рідке скло`, `нанокераміка` | keramika-i-zhidkoe-steklo |
| `кисті`, `щітка` | kisti-dlya-deteylinga / shchetka-dlya-moyki-avto |
| `квік`, `швидкий детейлер` | kvik-deteylery |
| `малярний скотч`, `малярна стрічка` | malyarniy-skotch |
| `мікрофібра`, `ганчірка`, `серветка`, `рушник` | mikrofibra-i-tryapki |
| `нейтралізатор`, `поглинач запах` | neytralizatory-zapakha |
| `знежирювач`, `антисилікон` | obezzhirivateli |
| `очищувач диск` | ochistiteli-diskov |
| `очищувач двигун` | ochistiteli-dvigatelya |
| `очищувач шкір` | ochistiteli-kozhi |
| `очищувач кузов`, `плям` | ochistiteli-kuzova |
| `очищувач шин`, `гум` | ochistiteli-shin |
| `очищувач скл` | ochistiteli-stekol |
| `омивач` | omyvatel |
| `поліроль для скла` | polirol-dlya-stekla |
| `поліроль для пластик`, `торпед` | poliroli-dlya-plastika |
| `полірувальна машинка` | polirovalnye-mashinki |
| `паста для полірування`, `полірувальна паста` | polirovalnye-pasty |
| `полірування` | polirovka |
| `плямовивідник` | pyatnovyvoditeli |
| `розпилювач`, `пінник`, `піногенератор` | raspyliteli-i-penniki |
| `силант` | silanty |
| `хімчистка салон`, `чищення салон` | sredstva-dlya-khimchistki-salona |
| `кондиціонер для шкіри`, `догляд за шкір` | sredstva-dlya-kozhi / ukhod-za-kozhey |
| `твердий віск` | tverdyy-vosk |
| `салон`, `інтер'єр` | ukhod-za-intererom |
| `пластик` (зовнішній) | ukhod-za-naruzhnym-plastikom |
| `відро` | vedra-i-emkosti |
| `віск` (загальний) | voski |
| `захисн`, `покритт` | zashchitnye-pokrytiya |
| `рідкий віск` | zhidkiy-vosk |

**Пріоритет:** Більш специфічне слово > загальне (напр. "твердий віск" > "віск")

---

## Workflow

### Етапи

1. **Генерація чек-листа** — створюю `tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md`
2. **Ручна перевірка** — користувач переглядає кожну категорію, ставить ✓ або виправляє
3. **Застосування** — по команді оновлюю `{slug}_clean.json`

### Файли

| Файл | Призначення |
|------|-------------|
| `uk/data/uk_keywords_source.csv` | Єдине джерело істини (356 ключів) |
| `tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md` | Чек-лист для ручної перевірки |
| `uk/categories/{slug}/data/{slug}_clean.json` | Оновлюється після підтвердження |

### Команда для застосування

```
/apply-uk-keywords {slug}
```

Бере підтверджені ключі з чек-листа і записує в `_clean.json`.

---

## Наступні кроки

1. [ ] Згенерувати чек-лист `tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md`
2. [ ] Ручна перевірка по категоріях
3. [ ] Застосувати підтверджені ключі до `_clean.json`
