# Keywords Audit Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Проверить все 49 файлов `_clean.json` на правильность распределения ключей (1 корень в keywords) перед массовым написанием контента.

**Architecture:** 5 параллельных субагентов читают и анализируют группы файлов, возвращают отчёты. Затем консолидация, ручная проверка, исправление проблемных файлов.

**Tech Stack:** Task tool (субагенты), Read/Edit tools, Git

---

## Контекст

### Правило распределения ключей

| Поле | Содержимое | Пример |
|------|------------|--------|
| `keywords` | 1 ключ — Король (max volume) | "химия для мойки авто" (260) |
| `synonyms` | Другие корни + вариации | "средство для мойки авто" (70), "автохимия" (50) |

### Определение корня

**Корень** — главное существительное, которое Google НЕ синонимизирует автоматически.

| Разные корни | Один корень (синонимы) |
|--------------|------------------------|
| химия ≠ средство ≠ автохимия | авто = машина = автомобиль |
| шампунь ≠ пена | купить = заказать |
| воск ≠ полимер ≠ силант | для мойки = для мытья |
| губка ≠ варежка | |

### Алгоритм извлечения корня

```
"химия для мойки авто" → "химия"
"средство для мойки машины" → "средство"
"автохимия для мойки" → "автохимия"
"купить химию для авто" → "химия" (игнорируем "купить")
```

---

## Task 1: Запуск 5 параллельных агентов аудита

**Действие:** Запустить 5 агентов через Task tool ОДНОВРЕМЕННО (в одном сообщении).

### Группа 1: aksessuary (10 файлов)

**Файлы:**
```
categories/aksessuary/data/aksessuary_clean.json
categories/aksessuary/aksessuary-dlya-naneseniya-sredstv/data/aksessuary-dlya-naneseniya-sredstv_clean.json
categories/aksessuary/gubki-i-varezhki/data/gubki-i-varezhki_clean.json
categories/aksessuary/malyarniy-skotch/data/malyarniy-skotch_clean.json
categories/aksessuary/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json
categories/aksessuary/nabory/data/nabory_clean.json
categories/aksessuary/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json
categories/aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json
categories/aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto/data/shchetka-dlya-moyki-avto_clean.json
categories/aksessuary/vedra-i-emkosti/data/vedra-i-emkosti_clean.json
```

### Группа 2: moyka-i-eksterer часть 1 (10 файлов)

**Файлы:**
```
categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json
categories/moyka-i-eksterer/avtoshampuni/data/avtoshampuni_clean.json
categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/data/aktivnaya-pena_clean.json
categories/moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki/data/shampuni-dlya-ruchnoy-moyki_clean.json
categories/moyka-i-eksterer/ochistiteli-dvigatelya/data/ochistiteli-dvigatelya_clean.json
categories/moyka-i-eksterer/ochistiteli-kuzova/antibitum/data/antibitum_clean.json
categories/moyka-i-eksterer/ochistiteli-kuzova/antimoshka/data/antimoshka_clean.json
categories/moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json
categories/moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli/data/obezzhirivateli_clean.json
categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/data/ukhod-za-naruzhnym-plastikom_clean.json
```

### Группа 3: moyka-i-eksterer часть 2 (8 файлов)

**Файлы:**
```
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin/data/cherniteli-shin_clean.json
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov/data/keramika-dlya-diskov_clean.json
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov/data/ochistiteli-diskov_clean.json
categories/moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin/data/ochistiteli-shin_clean.json
categories/moyka-i-eksterer/sredstva-dlya-stekol/antidozhd/data/antidozhd_clean.json
categories/moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol/data/ochistiteli-stekol_clean.json
categories/moyka-i-eksterer/sredstva-dlya-stekol/omyvatel/data/omyvatel_clean.json
categories/moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla/data/polirol-dlya-stekla_clean.json
```

### Группа 4: polirovka + ukhod-za-intererom (11 файлов)

**Файлы:**
```
categories/polirovka/data/polirovka_clean.json
categories/polirovka/polirovalnye-krugi/mekhovye/data/mekhovye_clean.json
categories/polirovka/polirovalnye-mashinki/akkumulyatornaya/data/akkumulyatornaya_clean.json
categories/polirovka/polirovalnye-pasty/data/polirovalnye-pasty_clean.json
categories/ukhod-za-intererom/data/ukhod-za-intererom_clean.json
categories/ukhod-za-intererom/neytralizatory-zapakha/data/neytralizatory-zapakha_clean.json
categories/ukhod-za-intererom/poliroli-dlya-plastika/data/poliroli-dlya-plastika_clean.json
categories/ukhod-za-intererom/pyatnovyvoditeli/data/pyatnovyvoditeli_clean.json
categories/ukhod-za-intererom/sredstva-dlya-khimchistki-salona/data/sredstva-dlya-khimchistki-salona_clean.json
categories/ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi/data/ochistiteli-kozhi_clean.json
categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/data/ukhod-za-kozhey_clean.json
```

### Группа 5: zashchitnye-pokrytiya + oborudovanie + opt (10 файлов)

**Файлы:**
```
categories/zashchitnye-pokrytiya/data/zashchitnye-pokrytiya_clean.json
categories/zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json
categories/zashchitnye-pokrytiya/kvik-deteylery/data/kvik-deteylery_clean.json
categories/zashchitnye-pokrytiya/silanty/data/silanty_clean.json
categories/zashchitnye-pokrytiya/voski/data/voski_clean.json
categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/data/tverdyy-vosk_clean.json
categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/data/zhidkiy-vosk_clean.json
categories/oborudovanie/data/oborudovanie_clean.json
categories/oborudovanie/apparaty-tornador/data/apparaty-tornador_clean.json
categories/opt-i-b2b/data/opt-i-b2b_clean.json
```

### Промпт для каждого агента

```markdown
## Задача: Аудит keywords в _clean.json (Группа N)

### Файлы для проверки:
[СПИСОК ФАЙЛОВ]

### Алгоритм для каждого файла:

1. Прочитать файл, извлечь массив `keywords`
2. Для каждого ключа определить корень:
   - Корень = первое существительное (главное слово)
   - Игнорировать: "для", "авто", "машины", "автомобиля", "купить", "цена", "заказать"
   - "химия для мойки авто" → "химия"
   - "средство для авто" → "средство"
3. Определить уникальные корни
4. Присвоить статус:
   - ✅ OK — 1 уникальный корень
   - ⚠️ REVIEW — 2+ уникальных корня
   - ❌ ERROR — нет keywords или пустой

### Формат отчёта:

## Аудит группы N

**Проверено:** X | **✅ OK:** Y | **⚠️ REVIEW:** Z

| Категория | Keywords | Корни | Статус |
|-----------|----------|-------|--------|
| slug | ключ1 (vol), ключ2 (vol) | корень1, корень2 | ⚠️ |

### ⚠️ Требуют проверки:
1. **slug** — корни: X, Y. Рекомендация: оставить "ключ1" (max vol), перенести остальные в synonyms.

### Важно:
- НЕ изменять файлы, только анализ
- Если сомневаетесь — пометить ⚠️
```

**Ожидаемый результат:** 5 отчётов в формате markdown.

---

## Task 2: Консолидация отчётов

**Действие:** Собрать отчёты от 5 агентов, создать сводную таблицу.

**Шаг 1:** Дождаться завершения всех 5 агентов.

**Шаг 2:** Объединить результаты в сводку:

```markdown
## Сводка аудита keywords

**Всего категорий:** 49
**✅ OK:** X
**⚠️ REVIEW:** Y
**❌ ERROR:** Z

### Категории для ручной проверки (⚠️):

| # | Категория | Keywords | Корни | Рекомендация |
|---|-----------|----------|-------|--------------|
| 1 | slug1 | ... | ... | ... |
| 2 | slug2 | ... | ... | ... |
```

**Шаг 3:** Сохранить сводку в `docs/plans/2026-01-20-keywords-audit-results.md`

---

## Task 3: Ручная проверка (интерактивно)

**Действие:** Показать пользователю список ⚠️ REVIEW, получить подтверждение.

**Шаг 1:** Вывести список проблемных категорий с рекомендациями.

**Шаг 2:** Спросить пользователя:
- "Подтвердить рекомендации?"
- "Есть исключения?" (особенно silanty, kvik-deteylery)

**Шаг 3:** Зафиксировать финальный список для исправления.

---

## Task 4: Исправление _clean.json файлов

**Действие:** Для каждой подтверждённой категории — Edit файл.

**Для каждого файла:**

**Шаг 1:** Прочитать текущий _clean.json

**Шаг 2:** Определить:
- Король (max volume) → остаётся в keywords
- Остальные → переносятся в synonyms

**Шаг 3:** Edit файл:
- Оставить в `keywords` только 1 ключ
- Добавить остальные в начало `synonyms`

**Пример изменения:**

До:
```json
"keywords": [
  { "keyword": "химия для мойки авто", "volume": 260 },
  { "keyword": "средство для мойки авто", "volume": 70 }
],
"synonyms": [...]
```

После:
```json
"keywords": [
  { "keyword": "химия для мойки авто", "volume": 260 }
],
"synonyms": [
  { "keyword": "средство для мойки авто", "volume": 70 },
  ...остальные synonyms...
]
```

---

## Task 5: Валидация исправлений

**Действие:** Повторно проверить исправленные файлы.

**Шаг 1:** Для каждого исправленного файла — убедиться что в keywords ровно 1 ключ.

**Шаг 2:** Вывести финальную сводку:
```
✅ Исправлено: X категорий
✅ Все файлы соответствуют правилу "1 корень в keywords"
```

---

## Task 6: Коммит изменений

**Шаг 1:** Git status

```bash
git status
```

**Шаг 2:** Git add

```bash
git add categories/*/data/*_clean.json
git add docs/plans/2026-01-20-keywords-audit*.md
```

**Шаг 3:** Git commit

```bash
git commit -m "$(cat <<'EOF'
fix(seo): normalize keywords structure in _clean.json

- Ensure only 1 primary keyword (max volume) in keywords array
- Move alternative roots to synonyms for LSI coverage
- Preserves all data for rollback capability

Audited: 49 categories
Fixed: X categories

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Чеклист готовности

- [ ] Task 1: 5 агентов запущены и вернули отчёты
- [ ] Task 2: Сводка создана и сохранена
- [ ] Task 3: Пользователь подтвердил рекомендации
- [ ] Task 4: Все проблемные файлы исправлены
- [ ] Task 5: Валидация пройдена
- [ ] Task 6: Изменения закоммичены

---

## После аудита

Можно запускать массовую генерацию контента:
- `/content-generator {slug}` — теперь знает что брать из keywords (1 Король)
- Другие корни из synonyms — вписывать в текст по 1 разу для LSI

---

**Version:** 1.0
**Created:** 2026-01-20
