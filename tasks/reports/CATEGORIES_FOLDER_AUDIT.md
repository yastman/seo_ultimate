# Аудит папки `categories/`

Цель: проверить, что фактически созданные папки категорий соответствуют структуре и готовы к выгрузке (данные/мета/контент/исследование).

Сопоставление делалось по SSOT-структуре `data/catalog_structure.json` + дереву `tasks/reports/STRUCTURE_TREE.md`.

## Сводка

-   Ожидаемых узлов по структуре: **63**
-   Папок в `categories/`: **58**
-   Лишних папок (не в структуре): **0**
-   Не хватает папок (есть в структуре, но нет на диске): **0**
-   `data/*_clean.json`:
    -   v2-схема (`{id,name,type,parent_id,keywords[]}`): **58**
    -   legacy-схема (`{slug,keywords{primary/...}}`): **0**
-   Полнота SEO-файлов:
    -   Полностью заполнено (есть `data` + `meta` + `content` + `research`): **9**
    -   Только `data` (нет `meta/content/research`): **49**

## 1) Что отсутствует (критичные расхождения со структурой)

### Отсутствующие папки (ID из `data/catalog_structure.json`)

Нет.

### Отсутствующие узлы в терминах `STRUCTURE_TREE.md`

Нет.

## 2) Проблемы целостности дерева (parent_id)

Не обнаружено.

## 3) Неполнота SEO-данных (meta/content/research)

### 3.1 Полностью заполненные (9)

-   `aktivnaya-pena`
-   `antibitum`
-   `antimoshka`
-   `avtoshampuni`
-   `cherniteli-shin`
-   `ochistiteli-diskov`
-   `ochistiteli-shin`
-   `ochistiteli-stekol`
-   `shampuni-dlya-ruchnoy-moyki`

### 3.2 Только данные (49)

У этих папок есть `data/{slug}_clean.json`, но нет SEO-пакета (`meta/`, `content/`, `research/`):

`aksessuary`, `aksessuary-dlya-naneseniya-sredstv`, `antidozhd`, `apparaty-tornador`, `glina-i-avtoskraby`, `gubki-i-varezhki`, `keramika-dlya-diskov`, `keramika-i-zhidkoe-steklo`, `kisti-dlya-deteylinga`, `kvik-deteylery`, `malyarniy-skotch`, `mekhovye`, `mikrofibra-i-tryapki`, `moyka-i-eksterer`, `nabory`, `nabory-dlya-moyki`, `nabory-dlya-salona`, `neytralizatory-zapakha`, `obezzhirivateli`, `oborudovanie`, `ochistiteli-dvigatelya`, `ochistiteli-kozhi`, `ochistiteli-kuzova`, `omyvatel`, `opt-i-b2b`, `poliroli-dlya-plastika`, `polirovalnye-krugi`, `polirovalnye-mashinki`, `polirovalnye-pasty`, `polirovka`, `pyatnovyvoditeli`, `raspyliteli-i-penniki`, `shchetka-dlya-moyki-avto`, `shchetki-i-kisti`, `silanty`, `sredstva-dlya-diskov-i-shin`, `sredstva-dlya-khimchistki-salona`, `sredstva-dlya-kozhi`, `sredstva-dlya-stekol`, `tryapka-dlya-avto`, `tryapka-dlya-vytiraniya-avto-posle-moyki`, `tverdyy-vosk`, `ukhod-za-intererom`, `ukhod-za-kozhey`, `ukhod-za-naruzhnym-plastikom`, `vedra-i-emkosti`, `voski`, `zashchitnye-pokrytiya`, `zhidkiy-vosk`.

## 4) Категории без семантики (0 keywords)

В v2-JSON есть 6 категорий с `keywords: []`:

-   `nabory`
-   `polirovka`
-   `shchetki-i-kisti`
-   `sredstva-dlya-diskov-i-shin`
-   `sredstva-dlya-stekol`
-   `ukhod-za-intererom`

Это может быть нормой для “хабов”, но тогда важно, чтобы:

-   они не ожидались как отдельные семантические страницы в маппингах/выгрузке;
-   у них были корректные `meta/content` (если такие страницы реально будут на сайте).

## Рекомендуемые правки (минимум)

На текущем этапе достаточно поддерживать заполнение `meta/content/research` для недостающих категорий.
