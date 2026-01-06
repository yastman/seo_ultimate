# ТЗ: Ручная проверка ключей в категориях

**Дата создания:** 2026-01-06  
**Дата проверки:** 2026-01-06  
**Статус:** ✅ Выполнено  
**Режим:** Ручной (без скриптов)

---

## Результаты проверки

| Метрика                       | Значение |
| ----------------------------- | -------- |
| Всего категорий проверено     | 62/62    |
| Файлов не найдено             | 0        |
| Ошибок в `id`                 | 0        |
| **Ошибок в `parent_id`**      | **2**    |
| Ключей "не в своей" категории | 0        |
| Дублей найдено                | 0        |

---

## ❌ Найденные ошибки

### 1. `apparaty-tornador` — неверный parent_id

-   **Файл:** `categories/apparaty-tornador/data/apparaty-tornador_clean.json`
-   **Проблема:** `parent_id: "oborudovanie-l2"` — такой папки не существует
-   **Решение:** Изменить на `parent_id: "oborudovanie"`

### 2. `oborudovanie` — parent_id ссылается на себя

-   **Файл:** `categories/oborudovanie/data/oborudovanie_clean.json`
-   **Проблема:** `parent_id: "oborudovanie"` — категория ссылается на себя
-   **Решение:** Изменить на `parent_id: null` (L1 категория)

---

## ✅ Проверенные категории (статус OK)

### L1: Мойка и Экстерьер

| Категория                    | id  | parent_id                      | Ключи | Дубли |
| ---------------------------- | --- | ------------------------------ | ----- | ----- |
| moyka-i-eksterer             | ✅  | null ✅                        | ✅    | ✅    |
| avtoshampuni                 | ✅  | moyka-i-eksterer ✅            | ✅    | ✅    |
| aktivnaya-pena               | ✅  | avtoshampuni ✅                | ✅    | ✅    |
| shampuni-dlya-ruchnoy-moyki  | ✅  | avtoshampuni ✅                | ✅    | ✅    |
| kislotnyy                    | ✅  | avtoshampuni ✅                | ✅    | ✅    |
| sredstva-dlya-stekol         | ✅  | moyka-i-eksterer ✅            | ✅    | ✅    |
| omyvatel                     | ✅  | sredstva-dlya-stekol ✅        | ✅    | ✅    |
| antidozhd                    | ✅  | sredstva-dlya-stekol ✅        | ✅    | ✅    |
| ochistiteli-stekol           | ✅  | sredstva-dlya-stekol ✅        | ✅    | ✅    |
| ochistiteli-kuzova           | ✅  | moyka-i-eksterer ✅            | ✅    | ✅    |
| glina-i-avtoskraby           | ✅  | ochistiteli-kuzova ✅          | ✅    | ✅    |
| obezzhirivateli              | ✅  | ochistiteli-kuzova ✅          | ✅    | ✅    |
| antimoshka                   | ✅  | ochistiteli-kuzova ✅          | ✅    | ✅    |
| antibitum                    | ✅  | ochistiteli-kuzova ✅          | ✅    | ✅    |
| ukhod-za-naruzhnym-plastikom | ✅  | ochistiteli-kuzova ✅          | ✅    | ✅    |
| sredstva-dlya-diskov-i-shin  | ✅  | moyka-i-eksterer ✅            | ✅    | ✅    |
| cherniteli-shin              | ✅  | sredstva-dlya-diskov-i-shin ✅ | ✅    | ✅    |
| ochistiteli-diskov           | ✅  | sredstva-dlya-diskov-i-shin ✅ | ✅    | ✅    |
| ochistiteli-shin             | ✅  | sredstva-dlya-diskov-i-shin ✅ | ✅    | ✅    |
| keramika-dlya-diskov         | ✅  | sredstva-dlya-diskov-i-shin ✅ | ✅    | ✅    |
| ochistiteli-dvigatelya       | ✅  | moyka-i-eksterer ✅            | ✅    | ✅    |

### L1: Аксессуары

| Категория                                | id  | parent_id               | Ключи | Дубли |
| ---------------------------------------- | --- | ----------------------- | ----- | ----- |
| aksessuary                               | ✅  | null ✅                 | ✅    | ✅    |
| malyarniy-skotch                         | ✅  | aksessuary ✅           | ✅    | ✅    |
| mikrofibra-i-tryapki                     | ✅  | aksessuary ✅           | ✅    | ✅    |
| tryapka-dlya-avto                        | ✅  | mikrofibra-i-tryapki ✅ | ✅    | ✅    |
| tryapka-dlya-vytiraniya-avto-posle-moyki | ✅  | mikrofibra-i-tryapki ✅ | ✅    | ✅    |
| dlya-stekol                              | ✅  | mikrofibra-i-tryapki ✅ | ✅    | ✅    |
| shchetki-i-kisti                         | ✅  | aksessuary ✅           | ✅    | ✅    |
| shchetka-dlya-moyki-avto                 | ✅  | shchetki-i-kisti ✅     | ✅    | ✅    |
| kisti-dlya-deteylinga                    | ✅  | shchetki-i-kisti ✅     | ✅    | ✅    |
| gubki-i-varezhki                         | ✅  | aksessuary ✅           | ✅    | ✅    |
| raspyliteli-i-penniki                    | ✅  | aksessuary ✅           | ✅    | ✅    |
| aksessuary-dlya-naneseniya-sredstv       | ✅  | aksessuary ✅           | ✅    | ✅    |
| vedra-i-emkosti                          | ✅  | aksessuary ✅           | ✅    | ✅    |
| nabory                                   | ✅  | aksessuary ✅           | ✅    | ✅    |
| nabory-dlya-moyki                        | ✅  | nabory ✅               | ✅    | ✅    |
| nabory-dlya-salona                       | ✅  | nabory ✅               | ✅    | ✅    |
| podarochnyy                              | ✅  | nabory ✅               | ✅    | ✅    |

### L1: Полировка

| Категория             | id  | parent_id                | Ключи | Дубли |
| --------------------- | --- | ------------------------ | ----- | ----- |
| polirovka             | ✅  | null ✅                  | ✅    | ✅    |
| polirovalnye-mashinki | ✅  | polirovka ✅             | ✅    | ✅    |
| akkumulyatornaya      | ✅  | polirovalnye-mashinki ✅ | ✅    | ✅    |
| polirovalnye-pasty    | ✅  | polirovka ✅             | ✅    | ✅    |
| polirovalnye-krugi    | ✅  | polirovka ✅             | ✅    | ✅    |
| mekhovye              | ✅  | polirovalnye-krugi ✅    | ✅    | ✅    |

### L1: Уход за интерьером

| Категория                        | id  | parent_id              | Ключи | Дубли |
| -------------------------------- | --- | ---------------------- | ----- | ----- |
| ukhod-za-intererom               | ✅  | null ✅                | ✅    | ✅    |
| neytralizatory-zapakha           | ✅  | ukhod-za-intererom ✅  | ✅    | ✅    |
| poliroli-dlya-plastika           | ✅  | ukhod-za-intererom ✅  | ✅    | ✅    |
| sredstva-dlya-kozhi              | ✅  | ukhod-za-intererom ✅  | ✅    | ✅    |
| ukhod-za-kozhey                  | ✅  | sredstva-dlya-kozhi ✅ | ✅    | ✅    |
| ochistiteli-kozhi                | ✅  | sredstva-dlya-kozhi ✅ | ✅    | ✅    |
| sredstva-dlya-khimchistki-salona | ✅  | ukhod-za-intererom ✅  | ✅    | ✅    |
| pyatnovyvoditeli                 | ✅  | ukhod-za-intererom ✅  | ✅    | ✅    |

### L1: Защитные покрытия

| Категория                 | id  | parent_id                | Ключи | Дубли |
| ------------------------- | --- | ------------------------ | ----- | ----- |
| zashchitnye-pokrytiya     | ✅  | null ✅                  | ✅    | ✅    |
| voski                     | ✅  | zashchitnye-pokrytiya ✅ | ✅    | ✅    |
| tverdyy-vosk              | ✅  | voski ✅                 | ✅    | ✅    |
| zhidkiy-vosk              | ✅  | voski ✅                 | ✅    | ✅    |
| keramika-i-zhidkoe-steklo | ✅  | zashchitnye-pokrytiya ✅ | ✅    | ✅    |
| kvik-deteylery            | ✅  | zashchitnye-pokrytiya ✅ | ✅    | ✅    |
| silanty                   | ✅  | zashchitnye-pokrytiya ✅ | ✅    | ✅    |

### L1: Оборудование

| Категория         | id  | parent_id                                         | Ключи | Дубли |
| ----------------- | --- | ------------------------------------------------- | ----- | ----- |
| oborudovanie      | ✅  | ❌ **oborudovanie** (должен быть null)            | ✅    | ✅    |
| apparaty-tornador | ✅  | ❌ **oborudovanie-l2** (должен быть oborudovanie) | ✅    | ✅    |

### L1: Опт и B2B

| Категория | id  | parent_id | Ключи | Дубли |
| --------- | --- | --------- | ----- | ----- |
| opt-i-b2b | ✅  | null ✅   | ✅    | ✅    |

---

## Следующие шаги

1. [x] Ручная проверка всех категорий
2. [x] **Исправить `apparaty-tornador`:** `parent_id` → `"oborudovanie"`
3. [x] **Исправить `oborudovanie`:** `parent_id` → `null`
4. [x] Коммит с исправлениями
5. [x] Обновить `PIPELINE_STATUS.md`
