# Журнал переноса ключей (Keyword Migration Log)

Этот файл служит буфером для ключей, которые нужно перенести из одной категории в другую.

**Обновлено:** 2026-01-01
**Проверено:** Все 65 категорий проверены вручную

---

## Завершённые миграции

| #   | Source → Target                                    | Keyword                                | Volume | Date       | Status                     |
| --- | -------------------------------------------------- | -------------------------------------- | ------ | ---------- | -------------------------- |
| 1   | aktivnaya-pena → glavnaya                          | автохимия купить украина               | 10     | 2026-01-01 | ✅ DONE                    |
| 2   | avtoshampuni → aktivnaya-pena                      | шампунь для моек высокого давления     | 50     | 2026-01-01 | ✅ DONE                    |
| 3   | ochistiteli-stekol → polirol-dlya-stekla           | средство для полировки лобового стекла | 30     | 2026-01-01 | ✅ DONE                    |
| 4   | chistka-kozhi → shchetki-i-kisti                   | щетка для чистки кожи авто             | 20     | 2026-01-01 | ✅ DONE                    |
| 5   | chistka-kozhi → shchetki-i-kisti                   | купить щетки для чистки кожи в авто    | 20     | 2026-01-01 | ✅ DONE                    |
| 6   | gubki-i-varezhki → aksessuary-dlya-naneseniya      | губка для полировки автомобиля         | 170    | 2026-01-01 | ✅ DONE                    |
| 7   | ochistiteli-shin → zashchitnoe-pokrytie-dlya-koles | защитное покрытие для дисков           | 10     | 2026-01-01 | ✅ DONE (уже был в target) |
| 8   | ochistiteli-shin → zashchitnoe-pokrytie-dlya-koles | защитное покрытие для литых дисков     | 10     | 2026-01-01 | ✅ DONE (уже был в target) |

**Итого перенесено:** 8 ключей, суммарный volume: 320

---

## Спорные (решено оставить)

| #   | Source Category    | Keyword                         | Volume | Target Category       | Status | Примечание                      |
| --- | ------------------ | ------------------------------- | ------ | --------------------- | ------ | ------------------------------- |
| S1  | aktivnaya-pena     | шампунь для бесконтактной мойки | 110    | avtoshampuni          | SKIP   | Синоним активной пены, оставить |
| S2  | ochistiteli-kuzova | автохимия для кузова            | 50     | moyka-i-eksteryer     | SKIP   | L2 категория, можно оставить    |
| S3  | polirovka          | набор для полировки авто        | 480    | nabory-dlya-polirovki | SKIP   | Норма для L1 hub                |
| S4  | nabory-dlya-moyki  | набор тряпок для машины         | 10     | mikrofibra-i-tryapki  | SKIP   | Набор ≠ отдельные тряпки        |

---

## Категории требующие чистки синонимов

После миграции эти категории нужно почистить от синонимов авто/автомобиля/машины:

| Категория                 | Ключей | Проблема                        | Статус          |
| ------------------------- | ------ | ------------------------------- | --------------- |
| dlya-khimchistki-salona   | 76     | авто/автомобиля/машины дубли    | ✅ DONE         |
| mikrofibra-i-tryapki      | 68     | много синонимов тряпка/салфетка | ✅ DONE         |
| ochistiteli-dvigatelya    | 43     | дубли                           | ✅ DONE         |
| shchetki-i-kisti          | 45     | кисточки/щётки дубли            | ✅ DONE         |
| glina-i-avtoskraby        | 34     | авто/автомобиля/машины          | ✅ DONE         |
| cherniteli-shin           | 19     | полироль синонимы               | ✅ DONE         |
| chistka-kozhi             | 21     | очиститель/средство дубли       | ✅ DONE         |
| neytralizatory-zapakha    | 22     | нейтрализатор/поглотитель       | ✅ DONE         |
| omyvatel                  | 32     | сезонные/синонимы               | ✅ DONE         |
| poliroli-dlya-plastika    | 18     | торпеда/панель/пластик          | ✅ DONE         |
| ochistiteli-shin          | 4      | уход за резиной                 | ✅ DONE         |
| silanty                   | 8      | силант/силанты                  | ✅ DONE         |
| vedra-i-emkosti           | 4      | ведро/ведра                     | ✅ DONE         |
| nabory-dlya-khimchistki   | 2      | набор для чистки                | ✅ DONE         |
| avtoshampuni              | 11     | авто/машины дубли               | ✅ DONE         |
| ochistiteli-diskov        | 19     | химия/средства дубли            | ✅ DONE         |
| obezzhirivateli           | 8      | применение/типы                 | ✅ DONE         |
| polirovalnye-pasty        | 13     | паста/полироль дубли            | ✅ DONE         |
| gubki-i-varezhki          | 20     | автомобиля/машины дубли         | ✅ DONE (20→11) |
| nabory                    | 9      | автомобиля/машины + JSON fix    | ✅ DONE         |
| keramika-i-zhidkoe-steklo | 28     | автомобилей→авто                | ✅ DONE         |
| chistka-kozhi             | 21     | автомобиля→авто                 | ✅ DONE         |

---

## Инструкция по переносу

1. **Добавить** ключ в target JSON (сохранить volume, cluster, добавить `"migrated_from": "slug"`)
1. **Удалить** ключ из source JSON
1. **Обновить** stats.after в обоих файлах
1. **Валидировать** JSON: `python3 -c "import json; json.load(open('path'))"`
1. **Отметить** статус DONE в этом файле

---
