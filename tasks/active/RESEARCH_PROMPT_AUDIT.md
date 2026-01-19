# Аудит RESEARCH_PROMPT.md — Результаты проверки (по факту файлов)

**Создано:** 2026-01-12
**Эталон:** categories/cherniteli-shin/research/RESEARCH_PROMPT.md
**Статус:** ✅ Обновлён

---

## Итоговая статистика

| Показатель | Значение |
|------------|----------|
| Всего проверено | 37 категорий (все, отмеченные ✅ в SEO_RESEARCH_BATCH.md) |
| Полностью соответствуют эталону (OK_FULL) | **3** ✅ |
| Частично соответствуют (PARTIAL) | **34** ⚠️ |
| Старый формат (v1) | **0** |

---

## Критерий соответствия (OK_FULL)

Категория считается соответствующей эталону только если в `categories/{slug}/research/RESEARCH_PROMPT.md`:

- есть секции: `ТЗ для Perplexity`, `Контекст`, `Семантическое ядро`, `Product Insights`, `Требования к ответам`, `Шаблон вывода`
- есть все блоки: `Блок 1` … `Блок 10` + `Блок 6а (PROOF)`
- нет заглушек вида `## Блок 1-10: ...` / `### Блок 8-10 (стандартные таблицы)`

---

## Проблемы, найденные при перепроверке

### 1) В SEO_RESEARCH_BATCH.md есть опечатка slug

- В Batch: `antidozh`
- В файловой структуре: `categories/antidozhd`

Проверка выполнена по реальному slug: `antidozhd`.

---

## Полностью соответствуют (3/37 ✅)

- `aktivnaya-pena`
- `shampuni-dlya-ruchnoy-moyki`
- `cherniteli-shin` (эталон)

---

## Частично соответствуют (34/37 ⚠️)

Ниже список категорий, отмеченных ✅ в Batch, но не проходящих строгую проверку на 100% соответствие эталону.

### Типовые причины PARTIAL

- в `Шаблон вывода` стоит заглушка `## Блок 1-10: ...`
- вместо блоков 8–10 стоит заглушка `### Блок 8-10: ... (стандартные таблицы)`
- отсутствуют секции `Product Insights` и/или `Требования к ответам`

### Сводная таблица (37 категорий из Batch)

| slug (Batch) | slug (FS) | Статус | Проблемы (кратко) |
|---|---|---|---|
| aktivnaya-pena | aktivnaya-pena | ✅ OK_FULL | — |
| shampuni-dlya-ruchnoy-moyki | shampuni-dlya-ruchnoy-moyki | ✅ OK_FULL | — |
| avtoshampuni | avtoshampuni | ⚠️ PARTIAL | заглушка: `## Блок 1-10: ...` |
| obezzhirivateli | obezzhirivateli | ⚠️ PARTIAL | заглушка: `## Блок 1-10: ...` |
| antibitum | antibitum | ⚠️ PARTIAL | заглушка: `## Блок 1-10: ...` |
| antimoshka | antimoshka | ⚠️ PARTIAL | заглушка: `## Блок 1-10: ...` |
| pyatnovyvoditeli | pyatnovyvoditeli | ⚠️ PARTIAL | заглушка: `## Блок 1-10: ...` |
| ochistiteli-diskov | ochistiteli-diskov | ⚠️ PARTIAL | нет `Product Insights/Требования/Шаблон`; заглушки 8–10 и 1–10 |
| ochistiteli-shin | ochistiteli-shin | ⚠️ PARTIAL | нет `Product Insights/Требования`; заглушки 8–10 и 1–10 |
| ochistiteli-stekol | ochistiteli-stekol | ⚠️ PARTIAL | нет `Product Insights/Требования`; заглушки 8–10 и 1–10 |
| ochistiteli-dvigatelya | ochistiteli-dvigatelya | ⚠️ PARTIAL | нет `Product Insights/Требования`; заглушки 8–10 и 1–10 |
| ochistiteli-kuzova | ochistiteli-kuzova | ⚠️ PARTIAL | нет `Product Insights/Требования`; заглушки 8–10 и 1–10 |
| sredstva-dlya-khimchistki-salona | sredstva-dlya-khimchistki-salona | ⚠️ PARTIAL | нет `Product Insights/Блок 6/Требования`; заглушка 1–10 |
| ochistiteli-kozhi | ochistiteli-kozhi | ⚠️ PARTIAL | нет `Product Insights/Требования`; заглушки 8–10 и 1–10 |
| neytralizatory-zapakha | neytralizatory-zapakha | ⚠️ PARTIAL | нет `Product Insights/Блок 6/Требования`; заглушка 1–10 |
| kislotnyy | kislotnyy | ⚠️ PARTIAL | нет `Product Insights/Требования`; заглушка 1–10 |
| omyvatel | omyvatel | ⚠️ PARTIAL | нет `Product Insights/Требования`; заглушка 1–10 |
| dlya-stekol | dlya-stekol | ⚠️ PARTIAL | нет `Product Insights/Блок 6а/Требования`; заглушка 1–10 |
| tverdyy-vosk | tverdyy-vosk | ⚠️ PARTIAL | нет `Product Insights/Блок 6/Требования`; заглушка 1–10 |
| zhidkiy-vosk | zhidkiy-vosk | ⚠️ PARTIAL | нет блоков 5–10/6а/7/Требований; заглушка 1–10 |
| voski | voski | ⚠️ PARTIAL | нет блоков 4–10/6а/7/Требований |
| keramika-i-zhidkoe-steklo | keramika-i-zhidkoe-steklo | ⚠️ PARTIAL | нет `Product Insights/Блок 6/Требования` |
| keramika-dlya-diskov | keramika-dlya-diskov | ⚠️ PARTIAL | нет блоков 4–10/6а/7/Требований |
| silanty | silanty | ⚠️ PARTIAL | нет блоков 5–10/6а/7/Требований |
| kvik-deteylery | kvik-deteylery | ⚠️ PARTIAL | нет блоков 5–10/6а/7/Требований |
| zashchitnye-pokrytiya | zashchitnye-pokrytiya | ⚠️ PARTIAL | нет блоков 4–10/6а/7/Требований |
| antidozh | antidozhd | ⚠️ PARTIAL | нет `Product Insights/Блок 6/Требования` |
| cherniteli-shin | cherniteli-shin | ✅ OK_FULL | эталон |
| poliroli-dlya-plastika | poliroli-dlya-plastika | ⚠️ PARTIAL | нет `Требования к ответам` |
| ukhod-za-intererom | ukhod-za-intererom | ⚠️ PARTIAL | нет `Требования к ответам` |
| ukhod-za-kozhey | ukhod-za-kozhey | ⚠️ PARTIAL | нет `Требования к ответам` |
| ukhod-za-naruzhnym-plastikom | ukhod-za-naruzhnym-plastikom | ⚠️ PARTIAL | нет `Требования к ответам` |
| polirovalnye-pasty | polirovalnye-pasty | ⚠️ PARTIAL | нет `Требования к ответам` |
| polirovalnye-krugi | polirovalnye-krugi | ⚠️ PARTIAL | нет `Требования к ответам` |
| polirovalnye-mashinki | polirovalnye-mashinki | ⚠️ PARTIAL | нет `Требования к ответам` |
| polirovka | polirovka | ⚠️ PARTIAL | нет `Требования к ответам` |
| glina-i-avtoskraby | glina-i-avtoskraby | ⚠️ PARTIAL | нет `Требования к ответам` |

## Рекомендуемые действия

### Шаг 1: Привести PARTIAL к эталону

Есть два пути:

- **Перегенерация** (проще и стабильнее): заново запустить `/seo-research {slug}` для всех PARTIAL.
- **Доточить вручную** (быстрее точечно): дописать недостающие секции и убрать заглушки (особенно `Требования к ответам`, `Product Insights`, блоки 8–10, `Шаблон вывода`).

### Шаг 2: Исправить опечатку в SEO_RESEARCH_BATCH.md

- `antidozh` → `antidozhd`

---

## Следующие шаги

- [x] Перепроверить все категории, отмеченные ✅ в Batch (37)
- [ ] Привести 34 PARTIAL к эталону (перегенерация или ручная правка)
- [ ] Исправить опечатку `antidozh` → `antidozhd` в Batch
- [ ] Повторно прогнать аудит после правок

---

## ГЛУБОКИЙ АУДИТ СОДЕРЖАНИЯ (Keywords, Products, Entities)

> **Дата аудита:** 2026-01-12
> **Методология:** Сравнение `_clean.json` + `PRODUCTS_LIST.md` с содержимым `RESEARCH_PROMPT.md`

---

### cherniteli-shin (ЭТАЛОН) ⚠️

**Статус:** Структура OK, но есть расхождения в объёмах ключей

| Проверка | Результат |
|----------|-----------|
| Keywords | ⚠️ Объёмы не совпадают с _clean.json |
| Entities | ✅ Все 7 включены |
| Micro_intents | ✅ Все 4 включены |
| Products | ✅ Все 3 товара |
| Структура | ✅ Полная |

**Расхождения в объёмах:**
| Ключ | _clean.json | RESEARCH_PROMPT |
|------|-------------|-----------------|
| чернитель резины | 1000 | 720 |
| чернение резины | 390 | 260 |
| полироль для колес | 170 | 10 |
| средства для чернения шин | 90 | 50 |
| полироль для шин | 90 | 50 |
| чернитель колёс | 50 | 40 |

---

### aktivnaya-pena ⚠️

**Статус:** Структура OK, но пропущены 9 synonyms

| Проверка | Результат |
|----------|-----------|
| Keywords | ⚠️ 14/23 — пропущено 9 synonyms |
| Entities | ✅ Все 9 включены |
| Micro_intents | ✅ Все 5 включены |
| Products | ✅ Все товары учтены |
| Структура | ✅ Полная |

**Пропущенные ключи:**
- активная пена для авто (50)
- активная пена для мойки (50)
- пена для мойки машины (50)
- пена для автомойки (40)
- пена для машины (40)
- пена для бесконтактной мойки авто (30)
- бесконтактная пена (20)
- бесконтактная химия для автомойки (20)
- профессиональная пена для мойки авто (10)

---

### shampuni-dlya-ruchnoy-moyki ⚠️

**Статус:** Структура OK, пропущен 1 товар

| Проверка | Результат |
|----------|-----------|
| Keywords | ✅ Все 5 включены |
| Entities | ✅ Все 5 включены |
| Micro_intents | ✅ Все 4 включены |
| Products | ⚠️ Пропущен Ultimate Unlim Shampoo |
| Структура | ✅ Полная |

---

### poliroli-dlya-plastika ❌ КРИТИЧЕСКИЕ ОШИБКИ

**Статус:** Keywords полностью НЕ соответствуют _clean.json!

| Проверка | Результат |
|----------|-----------|
| Keywords | ❌ **ПОЛНОЕ НЕСООТВЕТСТВИЕ** — ключи взяты не из _clean.json |
| Entities | ⚠️ 4/6 по смыслу |
| Micro_intents | ⚠️ 2/4 не соответствуют |
| Products | ❌ Бренды неверные, нет объёмов |
| Структура | ⚠️ Нет "Требования к ответам", сокращённый шаблон |

**Ключи в RESEARCH_PROMPT (ОШИБОЧНЫЕ):**
- полироль для пластика авто (1600) — ❌ НЕТ в _clean.json
- полироль для пластика (1600) — ❌ НЕТ в _clean.json
- матовая полироль для пластика (210) — ❌ НЕТ в _clean.json

**Должны быть (из _clean.json):**
- полироль для салона автомобиля (390)
- полироль для пластика автомобиля (320)
- полироль для пластику авто (320)
- полироль для торпеды (260)
- полироль для панели авто (170)
- ... и 11 synonyms

**Product Insights — ошибки:**
- ❌ Meguiar's — НЕТ в товарах секции 429
- ❌ "Cockpit Matte" — нет такого товара
- ❌ НЕ указан Gtechniq (C6 Matte Dash AB есть в товарах!)
- ❌ НЕ указаны объёмы: 100мл, 200мл, 500мл, 1л
- ❌ НЕ указаны форматы: покрытие, консервант, квік-детейлер, набор

**Действие:** Полная перегенерация через `/seo-research poliroli-dlya-plastika`

---

### ukhod-za-intererom ⚠️

**Статус:** Keywords не соответствуют _clean.json

| Проверка | Результат |
|----------|-----------|
| Keywords | ❌ Ключи взяты не из _clean.json |
| Entities | ⚠️ Частичное соответствие |
| Micro_intents | ⚠️ Частичное соответствие |
| Products | ⚠️ Слишком общее описание |
| Структура | ⚠️ Нет "Требования к ответам" |

**Ключи в RESEARCH_PROMPT:**
- уход за салоном авто (590) — в _clean: 170
- уход за интерьером автомобиля (140) — ❌ НЕТ в _clean
- средства для чистки салона (110) — ❌ НЕТ в _clean

**Должны быть (из _clean.json):**
- химчистка салона авто (320)
- уход за салоном авто (170)
- средства для салона автомобиля (90)
- ... и 3 synonyms

---

### ukhod-za-kozhey ❌ КРИТИЧЕСКИЕ ОШИБКИ

**Статус:** Бренды в Product Insights не соответствуют товарам!

| Проверка | Результат |
|----------|-----------|
| Keywords | ⚠️ Частично |
| Entities | ✅ OK |
| Micro_intents | ⚠️ Частично |
| Products | ❌ **Бренды неверные!** |
| Структура | ⚠️ Нет "Требования к ответам" |

**Product Insights в RESEARCH_PROMPT (ОШИБКИ):**
- ❌ Meguiar's — НЕТ в товарах секции 428
- ❌ Gtechniq (L1) — НЕТ в товарах секции 428
- ❌ **Furniture Clinic** — НЕ упомянут (а это 4 товара!)
- ❌ Форматы неверные: "пены, лосьоны" → реально: бальзам, крем-молочко, пятновыводитель

**Реальные бренды в секции 428:**
- Ultimate (Leather Balsam, LeatherCream SP8, Easy Leather, Skin Care Kit)
- Furniture Clinic (Stain Remover, Protection Cream, Degreaser, REVIVE)
- Koch-Chemie (Leather Star)

**Действие:** Полная перегенерация через `/seo-research ukhod-za-kozhey`

---

### ukhod-za-naruzhnym-plastikom ⚠️

**Статус:** Keywords OK, но объёмы низкие

| Проверка | Результат |
|----------|-----------|
| Keywords | ✅ Все 6 включены |
| Entities | ⚠️ 3/5 — добавить "неокрашенный пластик", "текстурированный пластик" |
| Micro_intents | ⚠️ 2/4 не из _clean |
| Products | ⚠️ Секция 421 = cherniteli-shin (shared) |
| Структура | ⚠️ Нет "Требования к ответам" |

---

## ИТОГОВАЯ СТАТИСТИКА ГЛУБОКОГО АУДИТА

| Категория | Keywords | Entities | Products | Структура | Действие |
|-----------|----------|----------|----------|-----------|----------|
| cherniteli-shin | ⚠️ объёмы | ✅ | ✅ | ✅ | Обновить объёмы |
| aktivnaya-pena | ⚠️ -9 | ✅ | ✅ | ✅ | Добавить 9 synonyms |
| shampuni-dlya-ruchnoy-moyki | ✅ | ✅ | ⚠️ -1 | ✅ | Добавить Unlim Shampoo |
| poliroli-dlya-plastika | ❌ | ⚠️ | ❌ | ⚠️ | **ПЕРЕГЕНЕРАЦИЯ** |
| ukhod-za-intererom | ❌ | ⚠️ | ⚠️ | ⚠️ | **ПЕРЕГЕНЕРАЦИЯ** |
| ukhod-za-kozhey | ⚠️ | ✅ | ❌ | ⚠️ | **ПЕРЕГЕНЕРАЦИЯ** |
| ukhod-za-naruzhnym-plastikom | ✅ | ⚠️ | ⚠️ | ⚠️ | Доработать вручную |

---

## ПРИОРИТЕТЫ ИСПРАВЛЕНИЙ

### Критические (перегенерация обязательна):
1. `poliroli-dlya-plastika` — ключи полностью не из _clean.json
2. `ukhod-za-kozhey` — бренды не соответствуют товарам
3. `ukhod-za-intererom` — ключи не из _clean.json

### Средние (можно доработать вручную):
4. `aktivnaya-pena` — добавить 9 пропущенных synonyms
5. `shampuni-dlya-ruchnoy-moyki` — добавить Ultimate Unlim Shampoo
6. `cherniteli-shin` — обновить объёмы ключей
7. `ukhod-za-naruzhnym-plastikom` — добавить entities, структуру

---

**Последнее обновление:** 2026-01-12
