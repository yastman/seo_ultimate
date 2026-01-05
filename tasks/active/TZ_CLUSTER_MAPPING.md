# ТЗ: Маппинг кластеров CSV → категории сайта

**Дата:** 2026-01-05
**Этап:** 3
**Статус:** ⬜ К выполнению
**Оценка:** ~2 часа

---

## Цель

Создать файл маппинга `data/cluster_map.json`, который связывает:

-   **52 кластера** из CSV (`Структура _Ultimate.csv`)
-   **~96 категорий** сайта (slug, category_id)

---

## Проблема

| Источник | Что содержит             | Пример                       |
| -------- | ------------------------ | ---------------------------- |
| CSV      | Иерархия L1→L2→L3, ключи | `L3: Активная пена`          |
| Сайт     | Категории со slug        | `aktivnaya-pena`             |
| Папки    | `categories/{slug}/`     | `categories/aktivnaya-pena/` |

**Нет явной связи между ними!**

Примеры несоответствий:

-   `L3: Шампуни для ручной мойки` → slug `dlya-ruchnoy-moyki` (не очевидно)
-   `Filter: Аккумуляторные` → нет отдельной категории, это фильтр
-   `L2: Полировальные машинки (General)` → slug `polirovalnye-mashinki`

---

## Артефакт

**Файл:** `data/cluster_map.json`

**Формат:**

```json
{
    "version": "1.0",
    "created_at": "2026-01-05",
    "clusters": {
        "L3: Активная пена": {
            "slug": "aktivnaya-pena",
            "type": "category",
            "category_id": 123,
            "parent_slug": "moyka-i-eksteryer",
            "keywords_count": 52
        },
        "L3: Шампуни для ручной мойки": {
            "slug": "dlya-ruchnoy-moyki",
            "type": "category",
            "category_id": 456,
            "parent_slug": "avtoshampuni",
            "keywords_count": 15
        },
        "Filter: Аккумуляторные": {
            "slug": null,
            "type": "filter",
            "target_slug": "polirovalnye-mashinki",
            "note": "Ключи идут в родительскую категорию"
        },
        "Special: Опт и B2B": {
            "slug": "opt",
            "type": "skip",
            "note": "B2B раздел, контент не генерируем"
        }
    },
    "stats": {
        "total_clusters": 52,
        "type_category": 45,
        "type_filter": 5,
        "type_skip": 2
    }
}
```

**Типы:**
| Тип | Описание | Действие |
|-----|----------|----------|
| `category` | Отдельная страница на сайте | Создать `_clean.json`, генерировать контент |
| `filter` | Фильтр внутри категории | Ключи идут в `target_slug` |
| `skip` | B2B, opt, служебные | Пропустить, контент не нужен |

---

## Входные данные

### 1. Список кластеров из CSV

**Источник:** `Структура _Ultimate.csv` или `data/generated/STRUCTURE.md`

Нужно извлечь все уникальные кластеры:

-   L1: ...
-   L2: ...
-   L3: ...
-   Cluster: ...
-   Filter: ...
-   Special: ...

### 2. Список категорий с сайта

**Источник:** База данных OpenCart

SQL запрос:

```sql
SELECT
    c.category_id,
    cd.name,
    c.parent_id,
    su.keyword as slug
FROM oc_category c
JOIN oc_category_description cd ON c.category_id = cd.category_id
LEFT JOIN oc_seo_url su ON su.query = CONCAT('category_id=', c.category_id)
WHERE cd.language_id = 1
ORDER BY c.parent_id, c.sort_order;
```

**Или:** выгрузить из `data/list_mode_export.csv` если там есть slug.

### 3. Существующие папки

```bash
ls -d categories/*/
```

---

## Чеклист выполнения

### Шаг 1: Собрать данные

-   [ ] Выгрузить список кластеров из CSV (52 шт)
-   [ ] Выгрузить категории с сайта (ID, name, slug, parent_id)
-   [ ] Получить список папок `categories/*/`

### Шаг 2: Сопоставить

-   [ ] Для каждого кластера найти соответствующий slug
-   [ ] Определить тип: category / filter / skip
-   [ ] Для filter указать target_slug
-   [ ] Для skip указать причину

### Шаг 3: Создать маппинг

-   [ ] Создать `data/cluster_map.json`
-   [ ] Заполнить все 52 кластера
-   [ ] Проверить: нет ли пропущенных

### Шаг 4: Валидация

-   [ ] Все кластеры имеют тип
-   [ ] Все `type: category` имеют slug
-   [ ] Все slug существуют в папках `categories/`
-   [ ] Нет дублей slug

---

## Ожидаемые проблемы

### 1. Кластер без категории на сайте

**Пример:** `L3: Чернители наружного пластика` — есть в CSV, нет на сайте

**Решение:**

-   Если нужна категория → создать на сайте
-   Если не нужна → `type: filter`, ключи в родителя

### 2. Категория без кластера в CSV

**Пример:** На сайте есть `nabory-dlya-deteylinga`, но в CSV нет отдельного кластера

**Решение:**

-   Проверить: может ключи в другом кластере?
-   Или добавить кластер в CSV

### 3. Неоднозначное соответствие

**Пример:** `L2: Микрофибра и тряпки` → slug `mikrofibra-i-tryapki` или `mikrofibra-dlya-polirovki`?

**Решение:**

-   Проверить parent_id на сайте
-   Выбрать более общий slug для L2

---

## Критерии приёмки

1. ✅ Файл `data/cluster_map.json` создан
2. ✅ Все 52 кластера имеют запись
3. ✅ Каждая запись имеет тип (category/filter/skip)
4. ✅ Для `type: category` указан существующий slug
5. ✅ Статистика в `stats` корректна

---

## После выполнения

1. Обновить `tasks/PIPELINE_STATUS.md` — Этап 3 ✅
2. Перенести это ТЗ в `tasks/completed/`
3. Перейти к Этапу 4 (Чистка синонимов)

---

## Примечания

-   Маппинг создаётся ОДИН раз
-   При добавлении новых категорий — обновить маппинг
-   `cluster_map.json` используется скриптами для:
    -   Генерации `_clean.json`
    -   Валидации структуры
    -   Деплоя на сайт
