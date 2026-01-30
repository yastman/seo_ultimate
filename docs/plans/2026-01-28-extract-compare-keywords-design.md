# Дизайн: Извлечение и сравнение RU ключей

**Дата:** 2026-01-28
**Цель:** Извлечь все ключи из _clean.json категорий и сравнить с master CSV

---

## 1. Общая архитектура

**Два скрипта:**

1. **`extract_all_keywords.py`** — парсит _clean.json, создаёт CSV со всеми ключами
2. **`compare_with_master.py`** — сравнивает извлечённый CSV с `ru_semantics_master.csv`

**Почему два скрипта:**
- Извлечение можно запускать отдельно для анализа
- Сравнение можно повторять после правок в master
- Проще отлаживать и переиспользовать

**Файловая структура:**
```
data/
├── ru_semantics_master.csv          # Источник истины (существует)
└── generated/
    ├── all_from_categories.csv      # Результат extract
    └── comparison_report.md         # Результат compare
```

---

## 2. Скрипт extract_all_keywords.py

**Входные данные:**
- Все файлы `categories/**/*_clean.json`

**Выходной файл:** `data/generated/all_from_categories.csv`

**Формат CSV:**
```csv
keyword,volume,category,source_type
активная пена,720,aktivnaya-pena,keyword
шампунь для бесконтактной мойки,110,aktivnaya-pena,synonym
пена для авто,90,aktivnaya-pena,variation
```

**Алгоритм:**
1. Найти все `*_clean.json` через `pathlib.rglob()`
2. Для каждого файла:
   - Извлечь `id` (slug категории)
   - Пройти по `keywords[]` → записать с `source_type=keyword`
   - Пройти по `synonyms[]` → записать с `source_type=synonym`
   - Пройти по `variations[]` → записать с `source_type=variation`
3. Сохранить всё в CSV (без дедупликации)

**Поля из JSON:**
- `keyword` — текст ключа
- `volume` — частотность (если нет — 0)
- `use_in` — не извлекаем

**CLI:**
```bash
python3 scripts/extract_all_keywords.py
# → data/generated/all_from_categories.csv
```

---

## 3. Скрипт compare_with_master.py

**Входные данные:**
- `data/generated/all_from_categories.csv`
- `data/ru_semantics_master.csv`

**Выходной файл:** `data/generated/comparison_report.md`

**Что сравниваем:**
1. **В категориях, но нет в master** — добавить в master
2. **В master, но нет в категориях** — устаревшие или не распределены
3. **Разная частотность** — volume отличается
4. **Разный тип** — keyword vs synonym

**Формат отчёта:**
```markdown
# Сравнение ключей: Категории vs Master

## Статистика
- Ключей в категориях: 1234
- Ключей в master: 1100
- Совпадений: 1050
- Только в категориях: 184
- Только в master: 50

## Только в категориях (добавить в master?)
| keyword | volume | category | type |
|---------|--------|----------|------|
| пена для авто | 90 | aktivnaya-pena | variation |

## Только в master (устаревшие?)
| keyword | volume | category | type |
|---------|--------|----------|------|
| старый ключ | 10 | aktivnaya-pena | synonym |

## Разная частотность
| keyword | category | vol_cat | vol_master | diff |
|---------|----------|---------|------------|------|
| активная пена | aktivnaya-pena | 720 | 700 | +20 |
```

**CLI:**
```bash
python3 scripts/compare_with_master.py
# → data/generated/comparison_report.md
```

---

## 4. Edge cases

**Дубликаты внутри категорий:**
- Один ключ может быть в `keywords[]` и `synonyms[]` одновременно
- Записываем оба вхождения с разным `source_type`
- В compare показываем как "Дубли внутри категории"

**Один ключ в нескольких категориях:**
- Нормальная ситуация
- В extract записываем все вхождения
- В compare группируем по keyword

**Пустые поля:**
- `volume` отсутствует → 0
- `variations[]` отсутствует → пропускаем
- `keywords[]` пустой → warning

**Кодировка:**
- UTF-8 везде
- Master CSV: `utf-8-sig` при чтении

**Нормализация:**
- lowercase
- strip, single space
- Сравниваем нормализованные, выводим оригинал

---

## 5. План имплементации

| Шаг | Действие |
|-----|----------|
| 1 | Создать `scripts/extract_all_keywords.py` |
| 2 | Создать `scripts/compare_with_master.py` |
| 3 | Запустить extract, проверить CSV |
| 4 | Запустить compare, проверить отчёт |
| 5 | Принять решение по расхождениям |

**Новые файлы:**
- `scripts/extract_all_keywords.py`
- `scripts/compare_with_master.py`

**Генерируемые файлы:**
- `data/generated/all_from_categories.csv`
- `data/generated/comparison_report.md`
