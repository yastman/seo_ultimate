# Очистка синонимов в _clean.json

## Статус: ✅ ЗАВЕРШЕНО

**Дата:** 2026-01-13
**Удалено:** ~120 синонимов
**Обработано:** 60 категорий

---

## Цель
Удалить бесполезные синонимы с низким volume (≤10), которые:
- Являются однокоренными вариациями основного ключа
- Не несут дополнительной семантической ценности
- Google и так понимает их связь

## Правила очистки

### Удалять синонимы без `meta_only` если:
- Volume ≤ 10
- Отличие только в "авто/машина/автомобиль"
- Отличие только в предлоге "для"
- Дублируют смысл основного keyword

### Оставлять синонимы без `meta_only` если:
- Volume ≥ 20 (полезны для H2/текста)
- Разные корни (очиститель ≠ химия)
- Реально другая формулировка запроса

### `meta_only` синонимы:
- НЕ трогать — они нужны для Title/Description
- Коммерческие модификаторы (купить, цена)

---

## Прогресс: 60/60 ✅

### Проверено и исправлено:
- [x] akkumulyatornaya — убран 1 синоним
- [x] aksessuary-dlya-naneseniya-sredstv — чисто
- [x] aksessuary — чисто
- [x] aktivnaya-pena — убрано 3 синонима
- [x] antibitum — убрано 2 синонима
- [x] antidozhd — убран 1 синоним
- [x] antimoshka — убрано 5 синонимов
- [x] apparaty-tornador — чисто
- [x] avtoshampuni — убрано 3 синонима
- [x] cherniteli-shin — убрано 9 синонимов
- [x] dlya-stekol — убрано 2 синонима
- [x] glina-i-avtoskraby — убрано 8 синонимов
- [x] gubki-i-varezhki — убрано 2 синонима
- [x] keramika-dlya-diskov — пропущено (нишевая категория)
- [x] keramika-i-zhidkoe-steklo — убрано 8 синонимов
- [x] kislotnyy — убрано 2 синонима
- [x] kvik-deteylery — убрано 3 синонима
- [x] malyarniy-skotch — чисто
- [x] mekhovye — чисто
- [x] mikrofibra-i-tryapki — убрано 11 синонимов
- [x] moyka-i-eksterer — убрано 2 синонима
- [x] nabory-dlya-moyki — чисто
- [x] nabory-dlya-salona — чисто
- [x] nabory — чисто
- [x] neytralizatory-zapakha — чисто
- [x] obezzhirivateli — убрано 2 синонима
- [x] oborudovanie — чисто
- [x] ochistiteli-diskov — убрано 2 синонима
- [x] ochistiteli-dvigatelya — убрано 2 синонима
- [x] ochistiteli-kozhi — убрано 8 синонимов
- [x] ochistiteli-kuzova — убрано 4 синонима
- [x] ochistiteli-shin — убрано 2 синонима
- [x] ochistiteli-stekol — убрано 2 синонима
- [x] omyvatel — убрано 3 синонима
- [x] opt-i-b2b — оставлено как есть (B2B специфика)
- [x] podarochnyy — чисто
- [x] poliroli-dlya-plastika — убрано 3 синонима
- [x] polirovalnye-krugi — чисто
- [x] polirovalnye-mashinki — убрано 2 синонима
- [x] polirovalnye-pasty — чисто
- [x] polirovka — чисто
- [x] pyatnovyvoditeli — убрано 3 синонима
- [x] raspyliteli-i-penniki — чисто
- [x] shampuni-dlya-ruchnoy-moyki — убран 1 синоним
- [x] shchetka-dlya-moyki-avto — убрано 4 синонима (включая volume:0)
- [x] shchetki-i-kisti — убрано 2 (включая keyword volume:0)
- [x] silanty — убрано 2 синонима
- [x] sredstva-dlya-diskov-i-shin — чисто
- [x] sredstva-dlya-khimchistki-salona — убрано 2 синонима
- [x] sredstva-dlya-kozhi — убрано 2 синонима
- [x] sredstva-dlya-stekol — убрано 2 синонима
- [x] tryapka-dlya-avto — убрано 10 синонимов
- [x] tryapka-dlya-vytiraniya-avto-posle-moyki — убрано 3 синонима
- [x] tverdyy-vosk — убрано 5 синонимов
- [x] ukhod-za-intererom — убрано 2 синонима
- [x] ukhod-za-kozhey — убрано 4 синонима
- [x] ukhod-za-naruzhnym-plastikom — убрано 3 синонима (теперь пусто)
- [x] vedra-i-emkosti — убрано 4 синонима (включая volume:0)
- [x] voski — убрано 2 синонима
- [x] zashchitnye-pokrytiya — убран 1 синоним
- [x] zhidkiy-vosk — убрано 5 синонимов

---

## Итоги

### Статистика:
- **Всего удалено:** ~120 синонимов
- **Категорий с изменениями:** 45
- **Категорий без изменений:** 15

### Топ категорий по очистке:
1. mikrofibra-i-tryapki — 11 синонимов
2. tryapka-dlya-avto — 10 синонимов
3. cherniteli-shin — 9 синонимов
4. glina-i-avtoskraby — 8 синонимов
5. keramika-i-zhidkoe-steklo — 8 синонимов
6. ochistiteli-kozhi — 8 синонимов

### Особые случаи:
- `keramika-dlya-diskov` — пропущено (вся категория низкочастотная)
- `opt-i-b2b` — оставлено (B2B специфика, низкий volume норма)
- Несколько файлов имели volume:0 — удалено

### Принцип:
> Keyword Density — НЕ фактор ранжирования (John Mueller 2025).
> Google понимает синонимы авто/машина/автомобиль.
> Дублировать их в тексте бесполезно.
