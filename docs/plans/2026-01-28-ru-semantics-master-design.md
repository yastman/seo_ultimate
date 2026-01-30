# RU Semantics Master — Design Document

**Дата:** 2026-01-28
**Статус:** Draft
**Автор:** Claude + User

---

## Проблема

Русская семантика разбросана по множеству файлов:
- 50+ файлов `categories/**/data/*_clean.json`
- CSV файл `ull_all_rus_keys.csv` со структурой L1/L2/L3
- 2 Excel файла в `reports/` со свежей частотностью Adwords
- `data/all_keywords.json` — агрегация (не источник истины)

**Последствия:**
- Сложно обновить частотность (нужно пройти по всем `_clean.json`)
- Новые ключи из Excel не попадают в систему
- Нет единого места для аудита всей семантики
- Дубликаты и inconsistency между файлами

---

## Решение

**Один master CSV файл** как единственный источник истины для RU семантики.

```
data/ru_semantics_master.csv    ← РЕДАКТИРУЕМ ТОЛЬКО ЗДЕСЬ
         ↓
    sync_semantics.py           ← скрипт синхронизации
         ↓
categories/**/data/*_clean.json ← генерируются автоматически
```

---

## Формат master CSV

```csv
keyword,volume,category,type,use_in
пена для мойки авто,1300,aktivnaya-pena,keyword,
активная пена,720,aktivnaya-pena,keyword,
купить активную пену,260,aktivnaya-pena,synonym,meta_only
шампунь для бесконтактной мойки,110,aktivnaya-pena,synonym,
полировочная машинка,8100,polirovalnye-mashinki,keyword,
```

### Колонки

| Колонка | Тип | Обязательно | Описание |
|---------|-----|-------------|----------|
| `keyword` | string | ✅ | Ключевая фраза (lowercase, trimmed) |
| `volume` | int | ✅ | Частотность из Adwords/Serpstat |
| `category` | string | ✅ | slug категории (должен существовать в `categories/`) |
| `type` | enum | ✅ | `keyword` или `synonym` |
| `use_in` | string | ❌ | Пусто или `meta_only` (для коммерческих ключей) |

### Правила

1. **Один ключ = одна категория.** Если ключ подходит для нескольких — выбрать наиболее релевантную.
2. **Primary keyword** — первый `keyword` по volume в категории (автоматически).
3. **Коммерческие ключи** (`купить`, `цена`, `заказать`) — `type=synonym`, `use_in=meta_only`.
4. **Сортировка** в CSV: по `category`, затем по `volume` DESC.

---

## Скрипты

### 1. `scripts/merge_to_master.py`

**Назначение:** Создать initial master CSV из существующих источников.

**Input:**
- `categories/**/data/*_clean.json` — текущая семантика
- `reports/*.xlsx` — свежая частотность Adwords
- `ull_all_rus_keys.csv` — структурированный список (опционально)

**Output:**
- `data/ru_semantics_master.csv`

**Логика:**
```python
1. Собрать все ключи из _clean.json (с категориями)
2. Загрузить частотность из Excel файлов
3. Обновить volume для существующих ключей
4. Добавить новые ключи из Excel (без категории → category="uncategorized")
5. Дедупликация по keyword (оставить с большим volume)
6. Сохранить в CSV
```

**Использование:**
```bash
python scripts/merge_to_master.py
# или с указанием Excel файлов
python scripts/merge_to_master.py --excel reports/*.xlsx
```

---

### 2. `scripts/sync_semantics.py`

**Назначение:** Синхронизировать master CSV → `_clean.json` файлы.

**Input:**
- `data/ru_semantics_master.csv`

**Output:**
- Обновлённые `categories/**/data/*_clean.json`

**Логика:**
```python
1. Читать master CSV
2. Группировать по category
3. Для каждой категории:
   a. Найти _clean.json файл
   b. Прочитать существующий файл (сохранить id, name, parent_id, entities, micro_intents)
   c. Заменить keywords[] из CSV (type=keyword)
   d. Заменить synonyms[] из CSV (type=synonym)
   e. Сортировать по volume DESC
   f. Записать файл
4. Отчёт: сколько категорий обновлено, сколько ключей добавлено/удалено
```

**Использование:**
```bash
# Dry-run (показать что изменится)
python scripts/sync_semantics.py --dry-run

# Применить изменения
python scripts/sync_semantics.py --apply

# Только конкретные категории
python scripts/sync_semantics.py --apply --categories aktivnaya-pena,antibitum
```

---

### 3. `scripts/validate_master.py`

**Назначение:** Валидация master CSV перед синхронизацией.

**Проверки:**
- [ ] Все категории существуют в `categories/`
- [ ] Нет дубликатов keyword
- [ ] Volume — целое число ≥ 0
- [ ] Type — только `keyword` или `synonym`
- [ ] use_in — пусто или `meta_only`
- [ ] Каждая категория имеет минимум 1 keyword (не только synonyms)

**Использование:**
```bash
python scripts/validate_master.py
# Exit code 0 = OK, 1 = errors
```

---

## Workflow

### Обновление частотности (регулярно)

```bash
# 1. Получить свежий Excel из Adwords/Serpstat
# 2. Положить в reports/

# 3. Обновить master CSV
python scripts/merge_to_master.py --excel reports/new_frequency.xlsx

# 4. Проверить
python scripts/validate_master.py

# 5. Синхронизировать в _clean.json
python scripts/sync_semantics.py --apply

# 6. Commit
git add data/ru_semantics_master.csv categories/
git commit -m "semantics(ru): update frequency from Adwords"
```

### Добавление новых ключей

```bash
# 1. Открыть data/ru_semantics_master.csv в Excel/редакторе
# 2. Добавить строки с новыми ключами
# 3. Сохранить

# 4. Валидация
python scripts/validate_master.py

# 5. Синхронизация
python scripts/sync_semantics.py --apply
```

### Перенос ключа в другую категорию

```bash
# 1. Изменить category в CSV для нужного ключа
# 2. sync_semantics.py удалит из старой, добавит в новую
python scripts/sync_semantics.py --apply
```

---

## Миграция (первый запуск)

### Шаг 1: Создать initial master CSV

```bash
python scripts/merge_to_master.py
```

**Результат:** `data/ru_semantics_master.csv` со всеми ключами из `_clean.json` + обновлённой частотностью из Excel.

### Шаг 2: Ручной review

Открыть CSV, проверить:
- [ ] Ключи без категории (`uncategorized`) — распределить вручную
- [ ] Дубликаты с разными категориями — выбрать правильную
- [ ] Некорректные данные — исправить

### Шаг 3: Первая синхронизация

```bash
python scripts/sync_semantics.py --dry-run  # посмотреть изменения
python scripts/sync_semantics.py --apply    # применить
```

### Шаг 4: Commit

```bash
git add data/ru_semantics_master.csv categories/
git commit -m "semantics(ru): migrate to master CSV as single source of truth"
```

---

## Сохраняемые поля в _clean.json

При синхронизации **НЕ затрагиваются:**
- `id`
- `name`
- `type`
- `parent_id`
- `entities`
- `micro_intents`
- `variations`
- `source`

**Заменяются полностью:**
- `keywords[]`
- `synonyms[]`

---

## Edge Cases

### Категория есть в CSV, но нет папки

→ `validate_master.py` выдаст ошибку. Нужно либо создать категорию (`/category-init`), либо исправить slug в CSV.

### Ключ без категории

→ `category="uncategorized"`. `sync_semantics.py` пропустит такие ключи с WARNING. Нужно распределить вручную.

### _clean.json не существует

→ `sync_semantics.py` создаст базовый файл:
```json
{
  "id": "{slug}",
  "name": "{slug}",
  "keywords": [...],
  "synonyms": [...]
}
```

### Пустая категория (0 ключей в CSV)

→ WARNING, но файл не удаляется. `keywords` и `synonyms` станут пустыми массивами.

---

## Файловая структура после миграции

```
data/
├── ru_semantics_master.csv      ← ИСТОЧНИК ИСТИНЫ
├── all_keywords.json            ← deprecated, можно удалить
└── generated/
    ├── ALL_KEYWORDS.txt         ← deprecated
    └── ru_keywords_mapping.json ← deprecated

scripts/
├── merge_to_master.py           ← NEW
├── sync_semantics.py            ← NEW
├── validate_master.py           ← NEW
├── update_volume.py             ← deprecated (заменён merge_to_master.py)
├── collect_keywords.py          ← deprecated
└── ...
```

---

## Риски и митигация

| Риск | Митигация |
|------|-----------|
| Случайно удалить ключи при sync | `--dry-run` по умолчанию, явный `--apply` |
| Потерять entities/micro_intents | Скрипт сохраняет все поля кроме keywords/synonyms |
| Неверная категория | `validate_master.py` проверяет существование |
| Merge conflict в CSV | CSV легко мержить (построчно) |

---

## Acceptance Criteria

- [ ] `merge_to_master.py` создаёт корректный CSV из существующих данных
- [ ] `validate_master.py` находит все проблемы в CSV
- [ ] `sync_semantics.py --dry-run` показывает diff без изменений
- [ ] `sync_semantics.py --apply` корректно обновляет `_clean.json`
- [ ] Все существующие ключи сохранены после миграции
- [ ] Pipeline (`/generate-meta`, `/content-generator`) работает как раньше

---

## Следующие шаги

1. [ ] Утвердить дизайн
2. [ ] Реализовать `merge_to_master.py`
3. [ ] Реализовать `validate_master.py`
4. [ ] Реализовать `sync_semantics.py`
5. [ ] Тестовая миграция (dry-run)
6. [ ] Review результата
7. [ ] Полная миграция
8. [ ] Обновить CLAUDE.md (новый workflow)

---

**Version:** 1.0
