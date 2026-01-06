# Итоговый отчёт по расхождениям и проблемам

Проверено:

-   `tasks/reports/STRUCTURE_TREE.md` — целевое дерево категорий (L1/L2/L3/Filter)
-   `tasks/reports/CLUSTER_DISTRIBUTION.md` — маппинг кластеров → страницы/фильтры
-   `data/catalog_structure.json` — SSOT-структура (id/parent/level/path)
-   `categories/` — фактически созданные папки категорий и их файлы

Связанные отчёты (детализация):

-   `tasks/reports/CLUSTER_DISTRIBUTION_VS_STRUCTURE_TREE_DIFF.md`
-   `tasks/reports/CATEGORIES_FOLDER_AUDIT.md`

---

## 1) CLUSTER_DISTRIBUTION vs STRUCTURE_TREE

### 1.1 Несоответствия путей

-   **Не найдено**: все назначения (destination) из `tasks/reports/CLUSTER_DISTRIBUTION.md` существуют в `tasks/reports/STRUCTURE_TREE.md`.

### 1.2 Узлы структуры без маппинга (семантика не назначена)

В `STRUCTURE_TREE.md` есть **8** узлов, которые **ни разу не встречаются** как destination в `CLUSTER_DISTRIBUTION.md`:

-   `L1: Полировка`
-   `L1: Уход за интерьером`
-   `L1: Оборудование`
-   `L1: Аксессуары → L2: Наборы`
-   `L1: Аксессуары → L2: Щетки и кисти`
-   `L1: Мойка и Экстерьер → L2: Автошампуни`
-   `L1: Мойка и Экстерьер → L2: Средства для стекол`
-   `L1: Мойка и Экстерьер → L2: Средства для дисков и шин`

Риск: если генерация контента/мета/выгрузок опирается на `CLUSTER_DISTRIBUTION.md`, эти страницы могут остаться без семантики и не попасть в пайплайн.

### 1.3 Дублирование назначения (page + merge)

-   `L1: Полировка → L2: Полировальные круги` — destination встречается 2 раза (и как `page`, и как `merge`).

Риск: конфликт “page vs merge” или двойной учёт при сборке.

### 1.4 Семантические предупреждения (⚠️) из CLUSTER_DISTRIBUTION

-   `L1: Мойка и Экстерьер → L2: Очистители двигателя` — внутри есть “общая мойка авто”, требуется чистка/перенос.
-   `L1: Полировка → L2: Полировальные круги` — в general-кластере есть ключи уровня “оборудование”, возможно перенести в “машинки”.
-   `L1: Защитные покрытия → L2: Воски → L3: Жидкий воск` — ключи про “жидкое стекло” перенести в `L2: Керамика и жидкое стекло`.

---

## 2) Папка categories vs структура (catalog_structure + STRUCTURE_TREE)

### 2.1 Отсутствуют папки из структуры (5 шт.)

Не хватает узлов (есть в структуре, но нет папок в `categories/`):

-   `oborudovanie-l2` — L2: Оборудование
-   `kislotnyy` — Filter: Кислотный
-   `akkumulyatornaya` — Filter: Аккумуляторная
-   `dlya-stekol` — Filter: Для стекол
-   `podarochnyy` — Filter: Подарочный

Риск: отсутствующие страницы/фильтры не будут выгружены/созданы, а также ломаются связи дочерних категорий.

### 2.2 Поломка целостности дерева (parent_id)

-   `categories/oborudovanie/data/oborudovanie_clean.json` — **самоссылка** (`parent_id = oborudovanie`).
-   `categories/apparaty-tornador/data/apparaty-tornador_clean.json` — **осиротевший parent** (`parent_id = oborudovanie-l2`, которого нет на диске).

Риск: некорректные пути/SQL/генерация дерева при обходе по `parent_id`.

### 2.3 Несогласованность формата данных (clean.json)

-   1 папка в legacy-формате `_clean.json`: `categories/shampuni-dlya-ruchnoy-moyki/data/shampuni-dlya-ruchnoy-moyki_clean.json`.

Риск: часть инструментов может ожидать единый v2-формат (`id/name/type/parent_id/keywords[]`) и падать/пропускать данные.

### 2.4 Неполнота SEO-пакета (meta/content/research)

-   Полностью заполнено (есть `data` + `meta` + `content` + `research`): **9** категорий.
-   У остальных: в основном **только `data/*_clean.json`** без `meta/content/research`.

Риск: при выгрузке в CMS/SQL часть категорий будет без текста и мета.

---

## 3) Что критично исправить в первую очередь

1. Восстановить недостающие узлы структуры: `oborudovanie-l2`, `kislotnyy`, `akkumulyatornaya`, `dlya-stekol`, `podarochnyy`.
2. Починить связи дерева:
    - убрать самоссылку `parent_id` у `oborudovanie` (L1 должен иметь `parent_id: null`);
    - вернуть корректный L2-узел “Оборудование” и привязать к нему `apparaty-tornador`.
3. Привести `_clean.json` к единой схеме (или зафиксировать поддержку legacy во всех генераторах).
4. Решить стратегию по Filter-узлам: либо они действительно как отдельные “страницы” (тогда нужны папки и SEO-пакет), либо это чисто фасеты (тогда не должны попадать в генерацию категорий/контента).
