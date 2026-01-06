# ТЗ: Ручная проверка ключей в категориях

**Дата создания:** 2026-01-06  
**Статус:** ⬜ Не начато  
**Режим:** Ручной (без скриптов)

---

## Цель

Убедиться, что ключевые слова в `_clean.json` файлах каждой категории:

1. Соответствуют структуре из `CLUSTER_DISTRIBUTION.md`
2. Правильно спарсены (без дублей, с корректным volume)
3. Относятся к правильной категории (не перепутаны с соседними)

---

## Источники для сравнения

| Файл                                    | Назначение                    |
| --------------------------------------- | ----------------------------- |
| `tasks/reports/CLUSTER_DISTRIBUTION.md` | Маппинг кластеров → категорий |
| `tasks/reports/STRUCTURE_TREE.md`       | Визуальное дерево L1→L2→L3    |
| `data/generated/STRUCTURE.md`           | Исходная семантика из CSV     |

---

## Инструкция по проверке

Для каждой категории:

1. **Открыть файл** `categories/{slug}/data/{slug}_clean.json`
2. **Проверить метаданные:**
    - `id` совпадает со slug папки
    - `name` соответствует названию в STRUCTURE_TREE.md
    - `parent_id` указывает на правильного родителя
3. **Проверить ключи:**
    - Все ключи относятся к этой категории (не к родителю/соседу)
    - Нет дублей внутри массива `keywords`
    - Volume указан для каждого ключа
4. **Сравнить с STRUCTURE.md:**
    - Найти категорию в `data/generated/STRUCTURE.md`
    - Убедиться, что все ключи перенесены

---

## Чек-лист по категориям

### L1: Мойка и Экстерьер

---

#### `moyka-i-eksterer`

-   **Файл:** `categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json`
-   **Ожидаемое название:** Мойка и Экстерьер
-   **Уровень:** L1
-   [ ] Файл существует
-   [ ] `id` = `moyka-i-eksterer`
-   [ ] `name` = "Мойка и Экстерьер"
-   [ ] `parent_id` = `null` (L1)
-   [ ] Ключи соответствуют "Direct Keywords" из STRUCTURE.md
-   [ ] Нет ключей от дочерних L2/L3
-   [ ] Нет дублей

---

#### `avtoshampuni`

-   **Файл:** `categories/avtoshampuni/data/avtoshampuni_clean.json`
-   **Ожидаемое название:** Автошампуни
-   **Уровень:** L2
-   **Родитель:** moyka-i-eksterer
-   [ ] Файл существует
-   [ ] `id` = `avtoshampuni`
-   [ ] `name` = "Автошампуни"
-   [ ] `parent_id` = `moyka-i-eksterer`
-   [ ] Ключи соответствуют L2 уровню
-   [ ] Нет ключей от L3 (активная пена, ручная мойка, кислотный)
-   [ ] Нет дублей

---

#### `aktivnaya-pena`

-   **Файл:** `categories/aktivnaya-pena/data/aktivnaya-pena_clean.json`
-   **Ожидаемое название:** Активная пена
-   **Уровень:** L3
-   **Родитель:** avtoshampuni
-   [ ] Файл существует
-   [ ] `id` = `aktivnaya-pena`
-   [ ] `name` = "Активная пена"
-   [ ] `parent_id` = `avtoshampuni`
-   [ ] Все ключи содержат "пена" / "активная пена"
-   [ ] Нет общих ключей "автошампунь"
-   [ ] Нет дублей

---

#### `shampuni-dlya-ruchnoy-moyki`

-   **Файл:** `categories/shampuni-dlya-ruchnoy-moyki/data/shampuni-dlya-ruchnoy-moyki_clean.json`
-   **Ожидаемое название:** Шампуни для ручной мойки
-   **Уровень:** L3
-   **Родитель:** avtoshampuni
-   [ ] Файл существует
-   [ ] `id` = `shampuni-dlya-ruchnoy-moyki`
-   [ ] `name` = "Шампуни для ручной мойки"
-   [ ] `parent_id` = `avtoshampuni`
-   [ ] Все ключи про ручную мойку
-   [ ] Нет ключей про активную пену
-   [ ] Нет дублей

---

#### `kislotnyy`

-   **Файл:** `categories/kislotnyy/data/kislotnyy_clean.json`
-   **Ожидаемое название:** Кислотные шампуни
-   **Уровень:** L3
-   **Родитель:** avtoshampuni
-   [ ] Файл существует
-   [ ] `id` = `kislotnyy`
-   [ ] `name` = "Кислотные шампуни"
-   [ ] `parent_id` = `avtoshampuni`
-   [ ] Все ключи содержат "кислот"
-   [ ] Нет дублей

---

#### `dlya-stekol`

-   **Файл:** `categories/dlya-stekol/data/dlya-stekol_clean.json`
-   **Ожидаемое название:** Средства для стекол
-   **Уровень:** L2
-   **Родитель:** moyka-i-eksterer
-   [ ] Файл существует
-   [ ] `id` = `dlya-stekol` или `sredstva-dlya-stekol`
-   [ ] `parent_id` = `moyka-i-eksterer`
-   [ ] Ключи L2 уровня (общие про стекла)
-   [ ] Нет ключей L3 (омыватель, антидождь, очистители)
-   [ ] Нет дублей

---

#### `omyvatel`

-   **Файл:** `categories/omyvatel/data/omyvatel_clean.json`
-   **Ожидаемое название:** Омыватель
-   **Уровень:** L3
-   **Родитель:** sredstva-dlya-stekol
-   [ ] Файл существует
-   [ ] `id` = `omyvatel`
-   [ ] `name` = "Омыватель"
-   [ ] `parent_id` указывает на L2 для стекол
-   [ ] Все ключи про омыватель
-   [ ] Нет дублей

---

#### `antidozhd`

-   **Файл:** `categories/antidozhd/data/antidozhd_clean.json`
-   **Ожидаемое название:** Антидождь
-   **Уровень:** L3
-   **Родитель:** sredstva-dlya-stekol
-   [ ] Файл существует
-   [ ] `id` = `antidozhd`
-   [ ] `name` = "Антидождь"
-   [ ] `parent_id` указывает на L2 для стекол
-   [ ] Все ключи про антидождь
-   [ ] Нет дублей

---

#### `ochistiteli-stekol`

-   **Файл:** `categories/ochistiteli-stekol/data/ochistiteli-stekol_clean.json`
-   **Ожидаемое название:** Очистители стекол
-   **Уровень:** L3
-   **Родитель:** sredstva-dlya-stekol
-   [ ] Файл существует
-   [ ] `id` = `ochistiteli-stekol`
-   [ ] `name` = "Очистители стекол"
-   [ ] `parent_id` указывает на L2 для стекол
-   [ ] Все ключи про очистку стекол
-   [ ] Нет ключей про омыватель/антидождь
-   [ ] Нет дублей

---

#### `ochistiteli-kuzova`

-   **Файл:** `categories/ochistiteli-kuzova/data/ochistiteli-kuzova_clean.json`
-   **Ожидаемое название:** Очистители кузова
-   **Уровень:** L2
-   **Родитель:** moyka-i-eksterer
-   [ ] Файл существует
-   [ ] `id` = `ochistiteli-kuzova`
-   [ ] `name` = "Очистители кузова"
-   [ ] `parent_id` = `moyka-i-eksterer`
-   [ ] Ключи L2 (общие про кузов)
-   [ ] Нет ключей L3 (глина, обезжириватель, антимошка и т.д.)
-   [ ] Нет дублей

---

#### `glina-i-avtoskraby`

-   **Файл:** `categories/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json`
-   **Ожидаемое название:** Глина и автоскрабы
-   **Уровень:** L3
-   **Родитель:** ochistiteli-kuzova
-   [ ] Файл существует
-   [ ] `id` = `glina-i-avtoskraby`
-   [ ] `parent_id` = `ochistiteli-kuzova`
-   [ ] Все ключи про глину/скрабы
-   [ ] Нет дублей

---

#### `obezzhirivateli`

-   **Файл:** `categories/obezzhirivateli/data/obezzhirivateli_clean.json`
-   **Ожидаемое название:** Обезжириватели
-   **Уровень:** L3
-   **Родитель:** ochistiteli-kuzova
-   [ ] Файл существует
-   [ ] `id` = `obezzhirivateli`
-   [ ] `parent_id` = `ochistiteli-kuzova`
-   [ ] Все ключи про обезжиривание
-   [ ] Нет дублей

---

#### `antimoshka`

-   **Файл:** `categories/antimoshka/data/antimoshka_clean.json`
-   **Ожидаемое название:** Антимошка
-   **Уровень:** L3
-   **Родитель:** ochistiteli-kuzova
-   [ ] Файл существует
-   [ ] `id` = `antimoshka`
-   [ ] `parent_id` = `ochistiteli-kuzova`
-   [ ] Все ключи про антимошку/мошки
-   [ ] Нет дублей

---

#### `antibitum`

-   **Файл:** `categories/antibitum/data/antibitum_clean.json`
-   **Ожидаемое название:** Антибитум
-   **Уровень:** L3
-   **Родитель:** ochistiteli-kuzova
-   [ ] Файл существует
-   [ ] `id` = `antibitum`
-   [ ] `parent_id` = `ochistiteli-kuzova`
-   [ ] Все ключи про антибитум/битум/смола
-   [ ] Нет дублей

---

#### `ukhod-za-naruzhnym-plastikom`

-   **Файл:** `categories/ukhod-za-naruzhnym-plastikom/data/ukhod-za-naruzhnym-plastikom_clean.json`
-   **Ожидаемое название:** Уход за наружным пластиком
-   **Уровень:** L3
-   **Родитель:** ochistiteli-kuzova
-   [ ] Файл существует
-   [ ] `id` = `ukhod-za-naruzhnym-plastikom`
-   [ ] `parent_id` = `ochistiteli-kuzova`
-   [ ] Все ключи про наружный пластик
-   [ ] Нет ключей про пластик салона
-   [ ] Нет дублей

---

#### `sredstva-dlya-diskov-i-shin`

-   **Файл:** `categories/sredstva-dlya-diskov-i-shin/data/sredstva-dlya-diskov-i-shin_clean.json`
-   **Ожидаемое название:** Средства для дисков и шин
-   **Уровень:** L2
-   **Родитель:** moyka-i-eksterer
-   [ ] Файл существует
-   [ ] `id` = `sredstva-dlya-diskov-i-shin`
-   [ ] `parent_id` = `moyka-i-eksterer`
-   [ ] Ключи L2 (общие про диски/шины)
-   [ ] Нет ключей L3 (чернители, очистители дисков/шин)
-   [ ] Нет дублей

---

#### `cherniteli-shin`

-   **Файл:** `categories/cherniteli-shin/data/cherniteli-shin_clean.json`
-   **Ожидаемое название:** Чернители шин
-   **Уровень:** L3
-   **Родитель:** sredstva-dlya-diskov-i-shin
-   [ ] Файл существует
-   [ ] `id` = `cherniteli-shin`
-   [ ] `parent_id` = `sredstva-dlya-diskov-i-shin`
-   [ ] Все ключи про чернители/чернение шин
-   [ ] Нет ключей про диски
-   [ ] Нет дублей

---

#### `ochistiteli-diskov`

-   **Файл:** `categories/ochistiteli-diskov/data/ochistiteli-diskov_clean.json`
-   **Ожидаемое название:** Очистители дисков
-   **Уровень:** L3
-   **Родитель:** sredstva-dlya-diskov-i-shin
-   [ ] Файл существует
-   [ ] `id` = `ochistiteli-diskov`
-   [ ] `parent_id` = `sredstva-dlya-diskov-i-shin`
-   [ ] Все ключи про очистку дисков
-   [ ] Нет ключей про шины
-   [ ] Нет дублей

---

#### `ochistiteli-shin`

-   **Файл:** `categories/ochistiteli-shin/data/ochistiteli-shin_clean.json`
-   **Ожидаемое название:** Очистители шин
-   **Уровень:** L3
-   **Родитель:** sredstva-dlya-diskov-i-shin
-   [ ] Файл существует
-   [ ] `id` = `ochistiteli-shin`
-   [ ] `parent_id` = `sredstva-dlya-diskov-i-shin`
-   [ ] Все ключи про очистку шин
-   [ ] Нет ключей про чернение
-   [ ] Нет дублей

---

#### `keramika-dlya-diskov`

-   **Файл:** `categories/keramika-dlya-diskov/data/keramika-dlya-diskov_clean.json`
-   **Ожидаемое название:** Керамика для дисков
-   **Уровень:** L3
-   **Родитель:** sredstva-dlya-diskov-i-shin
-   [ ] Файл существует
-   [ ] `id` = `keramika-dlya-diskov`
-   [ ] `parent_id` = `sredstva-dlya-diskov-i-shin`
-   [ ] Все ключи про керамику для дисков
-   [ ] Нет ключей про кузовную керамику
-   [ ] Нет дублей

---

#### `ochistiteli-dvigatelya`

-   **Файл:** `categories/ochistiteli-dvigatelya/data/ochistiteli-dvigatelya_clean.json`
-   **Ожидаемое название:** Очистители двигателя
-   **Уровень:** L2
-   **Родитель:** moyka-i-eksterer
-   [ ] Файл существует
-   [ ] `id` = `ochistiteli-dvigatelya`
-   [ ] `parent_id` = `moyka-i-eksterer`
-   [ ] Все ключи про мойку двигателя
-   [ ] ⚠️ Проверить: нет ли "общих" ключей типа "химия для мойки авто"
-   [ ] Нет дублей

---

### L1: Аксессуары

---

#### `aksessuary`

-   **Файл:** `categories/aksessuary/data/aksessuary_clean.json`
-   **Ожидаемое название:** Аксессуары
-   **Уровень:** L1
-   [ ] Файл существует
-   [ ] `id` = `aksessuary`
-   [ ] `name` = "Аксессуары"
-   [ ] `parent_id` = `null`
-   [ ] Общие ключи L1
-   [ ] Нет ключей L2/L3
-   [ ] Нет дублей

---

#### `malyarniy-skotch`

-   **Файл:** `categories/malyarniy-skotch/data/malyarniy-skotch_clean.json`
-   **Ожидаемое название:** Малярний Скотч
-   **Уровень:** L2
-   **Родитель:** aksessuary
-   [ ] Файл существует
-   [ ] `id` = `malyarniy-skotch`
-   [ ] `parent_id` = `aksessuary`
-   [ ] Все ключи про скотч
-   [ ] Нет дублей

---

#### `mikrofibra-i-tryapki`

-   **Файл:** `categories/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json`
-   **Ожидаемое название:** Микрофибра и тряпки
-   **Уровень:** L2
-   **Родитель:** aksessuary
-   [ ] Файл существует
-   [ ] `id` = `mikrofibra-i-tryapki`
-   [ ] `parent_id` = `aksessuary`
-   [ ] Общие ключи про микрофибру/тряпки
-   [ ] Нет ключей L3 (для стекол, для вытирания)
-   [ ] Нет дублей

---

#### `tryapka-dlya-avto`

-   **Файл:** `categories/tryapka-dlya-avto/data/tryapka-dlya-avto_clean.json`
-   **Ожидаемое название:** Тряпка для авто
-   **Уровень:** L3
-   **Родитель:** mikrofibra-i-tryapki
-   [ ] Файл существует
-   [ ] `id` = `tryapka-dlya-avto`
-   [ ] `parent_id` = `mikrofibra-i-tryapki`
-   [ ] Ключи про тряпки для авто (общие)
-   [ ] Нет дублей

---

#### `tryapka-dlya-vytiraniya-avto-posle-moyki`

-   **Файл:** `categories/tryapka-dlya-vytiraniya-avto-posle-moyki/data/tryapka-dlya-vytiraniya-avto-posle-moyki_clean.json`
-   **Ожидаемое название:** Тряпка для вытирания авто после мойки
-   **Уровень:** L3
-   **Родитель:** mikrofibra-i-tryapki
-   [ ] Файл существует
-   [ ] `id` = `tryapka-dlya-vytiraniya-avto-posle-moyki`
-   [ ] `parent_id` = `mikrofibra-i-tryapki`
-   [ ] Ключи про сушку/вытирание после мойки
-   [ ] Нет дублей

---

#### `dlya-stekol` (микрофибра)

-   **Файл:** `categories/dlya-stekol/data/dlya-stekol_clean.json`
-   **Ожидаемое название:** Микрофибра для стекол
-   **Уровень:** L3
-   **Родитель:** mikrofibra-i-tryapki
-   [ ] ⚠️ Проверить: slug может конфликтовать с "Средства для стекол"
-   [ ] Файл существует
-   [ ] Ключи про микрофибру для стекол
-   [ ] Нет дублей

---

#### `shchetki-i-kisti`

-   **Файл:** `categories/shchetki-i-kisti/data/shchetki-i-kisti_clean.json`
-   **Ожидаемое название:** Щетки и кисти
-   **Уровень:** L2
-   **Родитель:** aksessuary
-   [ ] Файл существует
-   [ ] `id` = `shchetki-i-kisti`
-   [ ] `parent_id` = `aksessuary`
-   [ ] Общие ключи про щетки/кисти
-   [ ] Нет дублей

---

#### `shchetka-dlya-moyki-avto`

-   **Файл:** `categories/shchetka-dlya-moyki-avto/data/shchetka-dlya-moyki-avto_clean.json`
-   **Ожидаемое название:** Щетка для мойки авто
-   **Уровень:** L3
-   **Родитель:** shchetki-i-kisti
-   [ ] Файл существует
-   [ ] `id` = `shchetka-dlya-moyki-avto`
-   [ ] `parent_id` = `shchetki-i-kisti`
-   [ ] Ключи про щетки для мойки
-   [ ] Нет дублей

---

#### `kisti-dlya-deteylinga`

-   **Файл:** `categories/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json`
-   **Ожидаемое название:** Кисти для детейлинга
-   **Уровень:** L3
-   **Родитель:** shchetki-i-kisti
-   [ ] Файл существует
-   [ ] `id` = `kisti-dlya-deteylinga`
-   [ ] `parent_id` = `shchetki-i-kisti`
-   [ ] Ключи про кисти/детейлинг кисти
-   [ ] Нет дублей

---

#### `gubki-i-varezhki`

-   **Файл:** `categories/gubki-i-varezhki/data/gubki-i-varezhki_clean.json`
-   **Ожидаемое название:** Губки и варежки
-   **Уровень:** L2
-   **Родитель:** aksessuary
-   [ ] Файл существует
-   [ ] `id` = `gubki-i-varezhki`
-   [ ] `parent_id` = `aksessuary`
-   [ ] Ключи про губки/варежки
-   [ ] Нет дублей

---

#### `raspyliteli-i-penniki`

-   **Файл:** `categories/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json`
-   **Ожидаемое название:** Распылители и пенники
-   **Уровень:** L2
-   **Родитель:** aksessuary
-   [ ] Файл существует
-   [ ] `id` = `raspyliteli-i-penniki`
-   [ ] `parent_id` = `aksessuary`
-   [ ] Ключи про распылители/пенники
-   [ ] Нет дублей

---

#### `aksessuary-dlya-naneseniya-sredstv`

-   **Файл:** `categories/aksessuary-dlya-naneseniya-sredstv/data/aksessuary-dlya-naneseniya-sredstv_clean.json`
-   **Ожидаемое название:** Аксессуары для нанесения средств
-   **Уровень:** L2
-   **Родитель:** aksessuary
-   [ ] Файл существует
-   [ ] `id` = `aksessuary-dlya-naneseniya-sredstv`
-   [ ] `parent_id` = `aksessuary`
-   [ ] Ключи про аппликаторы/нанесение
-   [ ] Нет дублей

---

#### `vedra-i-emkosti`

-   **Файл:** `categories/vedra-i-emkosti/data/vedra-i-emkosti_clean.json`
-   **Ожидаемое название:** Ведра и емкости
-   **Уровень:** L2
-   **Родитель:** aksessuary
-   [ ] Файл существует
-   [ ] `id` = `vedra-i-emkosti`
-   [ ] `parent_id` = `aksessuary`
-   [ ] Ключи про ведра/емкости
-   [ ] Нет дублей

---

#### `nabory`

-   **Файл:** `categories/nabory/data/nabory_clean.json`
-   **Ожидаемое название:** Наборы
-   **Уровень:** L2
-   **Родитель:** aksessuary
-   [ ] Файл существует
-   [ ] `id` = `nabory`
-   [ ] `parent_id` = `aksessuary`
-   [ ] Общие ключи про наборы
-   [ ] Нет ключей L3
-   [ ] Нет дублей

---

#### `nabory-dlya-moyki`

-   **Файл:** `categories/nabory-dlya-moyki/data/nabory-dlya-moyki_clean.json`
-   **Ожидаемое название:** Наборы для мойки
-   **Уровень:** L3
-   **Родитель:** nabory
-   [ ] Файл существует
-   [ ] `id` = `nabory-dlya-moyki`
-   [ ] `parent_id` = `nabory`
-   [ ] Ключи про наборы для мойки
-   [ ] Нет дублей

---

#### `nabory-dlya-salona`

-   **Файл:** `categories/nabory-dlya-salona/data/nabory-dlya-salona_clean.json`
-   **Ожидаемое название:** Наборы для салона
-   **Уровень:** L3
-   **Родитель:** nabory
-   [ ] Файл существует
-   [ ] `id` = `nabory-dlya-salona`
-   [ ] `parent_id` = `nabory`
-   [ ] Ключи про наборы для салона
-   [ ] Нет дублей

---

#### `podarochnyy`

-   **Файл:** `categories/podarochnyy/data/podarochnyy_clean.json`
-   **Ожидаемое название:** Подарочные наборы
-   **Уровень:** L3
-   **Родитель:** nabory
-   [ ] Файл существует
-   [ ] `id` = `podarochnyy`
-   [ ] `parent_id` = `nabory`
-   [ ] Ключи про подарки/подарочные
-   [ ] Нет дублей

---

### L1: Полировка

---

#### `polirovka`

-   **Файл:** `categories/polirovka/data/polirovka_clean.json`
-   **Ожидаемое название:** Полировка
-   **Уровень:** L1
-   [ ] Файл существует
-   [ ] `id` = `polirovka`
-   [ ] `parent_id` = `null`
-   [ ] Общие ключи L1 (если есть)
-   [ ] Нет дублей

---

#### `polirovalnye-mashinki`

-   **Файл:** `categories/polirovalnye-mashinki/data/polirovalnye-mashinki_clean.json`
-   **Ожидаемое название:** Полировальные машинки
-   **Уровень:** L2
-   **Родитель:** polirovka
-   [ ] Файл существует
-   [ ] `id` = `polirovalnye-mashinki`
-   [ ] `parent_id` = `polirovka`
-   [ ] Ключи про полировальные машинки (общие)
-   [ ] Нет ключей L3 (аккумуляторные)
-   [ ] Нет дублей

---

#### `akkumulyatornaya`

-   **Файл:** `categories/akkumulyatornaya/data/akkumulyatornaya_clean.json`
-   **Ожидаемое название:** Аккумуляторные полировальные машинки
-   **Уровень:** L3
-   **Родитель:** polirovalnye-mashinki
-   [ ] Файл существует
-   [ ] `id` = `akkumulyatornaya`
-   [ ] `parent_id` = `polirovalnye-mashinki`
-   [ ] Все ключи содержат "аккумулятор"
-   [ ] Нет общих ключей про машинки
-   [ ] Нет дублей

---

#### `polirovalnye-pasty`

-   **Файл:** `categories/polirovalnye-pasty/data/polirovalnye-pasty_clean.json`
-   **Ожидаемое название:** Полировальные пасты
-   **Уровень:** L2
-   **Родитель:** polirovka
-   [ ] Файл существует
-   [ ] `id` = `polirovalnye-pasty`
-   [ ] `parent_id` = `polirovka`
-   [ ] Ключи про пасты/полировка
-   [ ] Нет дублей

---

#### `polirovalnye-krugi`

-   **Файл:** `categories/polirovalnye-krugi/data/polirovalnye-krugi_clean.json`
-   **Ожидаемое название:** Полировальные круги
-   **Уровень:** L2
-   **Родитель:** polirovka
-   [ ] Файл существует
-   [ ] `id` = `polirovalnye-krugi`
-   [ ] `parent_id` = `polirovka`
-   [ ] Ключи про круги (общие)
-   [ ] Нет ключей L3 (меховые)
-   [ ] Нет дублей

---

#### `mekhovye`

-   **Файл:** `categories/mekhovye/data/mekhovye_clean.json`
-   **Ожидаемое название:** Меховые
-   **Уровень:** L3
-   **Родитель:** polirovalnye-krugi
-   [ ] Файл существует
-   [ ] `id` = `mekhovye`
-   [ ] `parent_id` = `polirovalnye-krugi`
-   [ ] Ключи про меховые круги
-   [ ] Нет дублей

---

### L1: Уход за интерьером

---

#### `ukhod-za-intererom`

-   **Файл:** `categories/ukhod-za-intererom/data/ukhod-za-intererom_clean.json`
-   **Ожидаемое название:** Уход за интерьером
-   **Уровень:** L1
-   [ ] Файл существует
-   [ ] `id` = `ukhod-za-intererom`
-   [ ] `parent_id` = `null`
-   [ ] Общие ключи L1
-   [ ] Нет дублей

---

#### `neytralizatory-zapakha`

-   **Файл:** `categories/neytralizatory-zapakha/data/neytralizatory-zapakha_clean.json`
-   **Ожидаемое название:** Нейтрализаторы запаха
-   **Уровень:** L2
-   **Родитель:** ukhod-za-intererom
-   [ ] Файл существует
-   [ ] `id` = `neytralizatory-zapakha`
-   [ ] `parent_id` = `ukhod-za-intererom`
-   [ ] Ключи про нейтрализацию запаха
-   [ ] Нет дублей

---

#### `poliroli-dlya-plastika`

-   **Файл:** `categories/poliroli-dlya-plastika/data/poliroli-dlya-plastika_clean.json`
-   **Ожидаемое название:** Полироли для пластика
-   **Уровень:** L2
-   **Родитель:** ukhod-za-intererom
-   [ ] Файл существует
-   [ ] `id` = `poliroli-dlya-plastika`
-   [ ] `parent_id` = `ukhod-za-intererom`
-   [ ] Ключи про полироль пластика салона
-   [ ] Нет ключей про наружный пластик
-   [ ] Нет дублей

---

#### `sredstva-dlya-kozhi`

-   **Файл:** `categories/sredstva-dlya-kozhi/data/sredstva-dlya-kozhi_clean.json`
-   **Ожидаемое название:** Средства для кожи
-   **Уровень:** L2
-   **Родитель:** ukhod-za-intererom
-   [ ] Файл существует
-   [ ] `id` = `sredstva-dlya-kozhi`
-   [ ] `parent_id` = `ukhod-za-intererom`
-   [ ] Общие ключи про кожу
-   [ ] Нет ключей L3 (уход, очистка)
-   [ ] Нет дублей

---

#### `ukhod-za-kozhey`

-   **Файл:** `categories/ukhod-za-kozhey/data/ukhod-za-kozhey_clean.json`
-   **Ожидаемое название:** Уход за кожей
-   **Уровень:** L3
-   **Родитель:** sredstva-dlya-kozhi
-   [ ] Файл существует
-   [ ] `id` = `ukhod-za-kozhey`
-   [ ] `parent_id` = `sredstva-dlya-kozhi`
-   [ ] Ключи про уход/кондиционирование кожи
-   [ ] Нет дублей

---

#### `ochistiteli-kozhi`

-   **Файл:** `categories/ochistiteli-kozhi/data/ochistiteli-kozhi_clean.json`
-   **Ожидаемое название:** Очистители кожи
-   **Уровень:** L3
-   **Родитель:** sredstva-dlya-kozhi
-   [ ] Файл существует
-   [ ] `id` = `ochistiteli-kozhi`
-   [ ] `parent_id` = `sredstva-dlya-kozhi`
-   [ ] Ключи про очистку кожи
-   [ ] Нет дублей

---

#### `sredstva-dlya-khimchistki-salona`

-   **Файл:** `categories/sredstva-dlya-khimchistki-salona/data/sredstva-dlya-khimchistki-salona_clean.json`
-   **Ожидаемое название:** Средства для химчистки салона
-   **Уровень:** L2
-   **Родитель:** ukhod-za-intererom
-   [ ] Файл существует
-   [ ] `id` = `sredstva-dlya-khimchistki-salona`
-   [ ] `parent_id` = `ukhod-za-intererom`
-   [ ] Ключи про химчистку салона
-   [ ] Нет ключей про пятновыводители (отдельная категория)
-   [ ] Нет дублей

---

#### `pyatnovyvoditeli`

-   **Файл:** `categories/pyatnovyvoditeli/data/pyatnovyvoditeli_clean.json`
-   **Ожидаемое название:** Пятновыводители
-   **Уровень:** L2
-   **Родитель:** ukhod-za-intererom
-   [ ] Файл существует
-   [ ] `id` = `pyatnovyvoditeli`
-   [ ] `parent_id` = `ukhod-za-intererom`
-   [ ] Ключи про пятновыводители
-   [ ] Нет дублей

---

### L1: Защитные покрытия

---

#### `zashchitnye-pokrytiya`

-   **Файл:** `categories/zashchitnye-pokrytiya/data/zashchitnye-pokrytiya_clean.json`
-   **Ожидаемое название:** Защитные покрытия
-   **Уровень:** L1
-   [ ] Файл существует
-   [ ] `id` = `zashchitnye-pokrytiya`
-   [ ] `parent_id` = `null`
-   [ ] Общие ключи L1
-   [ ] Нет дублей

---

#### `voski`

-   **Файл:** `categories/voski/data/voski_clean.json`
-   **Ожидаемое название:** Воски
-   **Уровень:** L2
-   **Родитель:** zashchitnye-pokrytiya
-   [ ] Файл существует
-   [ ] `id` = `voski`
-   [ ] `parent_id` = `zashchitnye-pokrytiya`
-   [ ] Общие ключи про воски
-   [ ] Нет ключей L3 (твердый, жидкий)
-   [ ] Нет дублей

---

#### `tverdyy-vosk`

-   **Файл:** `categories/tverdyy-vosk/data/tverdyy-vosk_clean.json`
-   **Ожидаемое название:** Твердый воск
-   **Уровень:** L3
-   **Родитель:** voski
-   [ ] Файл существует
-   [ ] `id` = `tverdyy-vosk`
-   [ ] `parent_id` = `voski`
-   [ ] Ключи про твердый/пастообразный воск
-   [ ] Нет дублей

---

#### `zhidkiy-vosk`

-   **Файл:** `categories/zhidkiy-vosk/data/zhidkiy-vosk_clean.json`
-   **Ожидаемое название:** Жидкий воск
-   **Уровень:** L3
-   **Родитель:** voski
-   [ ] Файл существует
-   [ ] `id` = `zhidkiy-vosk`
-   [ ] `parent_id` = `voski`
-   [ ] Ключи про жидкий воск
-   [ ] ⚠️ Проверить: нет ли ключей "жидкое стекло" (должны быть в керамике)
-   [ ] Нет дублей

---

#### `keramika-i-zhidkoe-steklo`

-   **Файл:** `categories/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json`
-   **Ожидаемое название:** Керамика и жидкое стекло
-   **Уровень:** L2
-   **Родитель:** zashchitnye-pokrytiya
-   [ ] Файл существует
-   [ ] `id` = `keramika-i-zhidkoe-steklo`
-   [ ] `parent_id` = `zashchitnye-pokrytiya`
-   [ ] Ключи про керамику/жидкое стекло для кузова
-   [ ] Нет ключей про керамику для дисков
-   [ ] Нет дублей

---

#### `kvik-deteylery`

-   **Файл:** `categories/kvik-deteylery/data/kvik-deteylery_clean.json`
-   **Ожидаемое название:** Квик-детейлеры
-   **Уровень:** L2
-   **Родитель:** zashchitnye-pokrytiya
-   [ ] Файл существует
-   [ ] `id` = `kvik-deteylery`
-   [ ] `parent_id` = `zashchitnye-pokrytiya`
-   [ ] Ключи про квик-детейлер
-   [ ] Нет ключей про силанты
-   [ ] Нет дублей

---

#### `silanty`

-   **Файл:** `categories/silanty/data/silanty_clean.json`
-   **Ожидаемое название:** Силанты
-   **Уровень:** L2
-   **Родитель:** zashchitnye-pokrytiya
-   [ ] Файл существует
-   [ ] `id` = `silanty`
-   [ ] `parent_id` = `zashchitnye-pokrytiya`
-   [ ] Ключи про силанты
-   [ ] Нет дублей

---

### L1: Оборудование

---

#### `oborudovanie`

-   **Файл:** `categories/oborudovanie/data/oborudovanie_clean.json`
-   **Ожидаемое название:** Оборудование
-   **Уровень:** L1 или L2
-   [ ] Файл существует
-   [ ] `id` = `oborudovanie`
-   [ ] Проверить иерархию
-   [ ] Нет дублей

---

#### `apparaty-tornador`

-   **Файл:** `categories/apparaty-tornador/data/apparaty-tornador_clean.json`
-   **Ожидаемое название:** Аппараты Tornador
-   **Уровень:** L3
-   **Родитель:** oborudovanie
-   [ ] Файл существует
-   [ ] `id` = `apparaty-tornador`
-   [ ] `parent_id` = `oborudovanie`
-   [ ] Ключи про Tornador
-   [ ] Нет дублей

---

### L1: Опт и B2B

---

#### `opt-i-b2b`

-   **Файл:** `categories/opt-i-b2b/data/opt-i-b2b_clean.json`
-   **Ожидаемое название:** Опт и B2B
-   **Уровень:** Special
-   [ ] Файл существует
-   [ ] `id` = `opt-i-b2b`
-   [ ] Ключи про оптовые закупки/B2B
-   [ ] Нет дублей

---

## Итоговая статистика

После проверки заполнить:

| Метрика                       | Значение |
| ----------------------------- | -------- |
| Всего категорий проверено     | /62      |
| Файлов не найдено             |          |
| Ошибок в `id`                 |          |
| Ошибок в `parent_id`          |          |
| Ключей "не в своей" категории |          |
| Дублей найдено                |          |

---

## Следующие шаги после проверки

1. [ ] Исправить найденные ошибки в `_clean.json`
2. [ ] Обновить `PIPELINE_STATUS.md`
3. [ ] Коммит с результатами QA
