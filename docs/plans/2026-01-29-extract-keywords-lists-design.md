# Design: Extract Keywords Lists (RU/UK)

## Цель

Создать два скрипта для извлечения всех ключевых слов из категорий в MD файлы.

## Скрипты

### `extract_ru_keywords_list.py`

**Источник:** `categories/**/*_clean.json` (53 файла)

**Выход:** `data/generated/RU_KEYWORDS.md` (~1131 ключ)

**Логика:**
1. Рекурсивно найти все `*_clean.json` в `categories/`
2. Из каждого файла извлечь:
   - `keywords[].keyword`
   - `synonyms[].keyword`
   - `variations[].keyword`
3. Обработать legacy формат (если `keywords` — dict с группами)
4. Собрать в set (дедупликация)
5. Отсортировать по алфавиту
6. Записать в MD — один ключ на строку

### `extract_uk_keywords_list.py`

**Источник:** `uk/categories/**/*_clean.json` (53 файла)

**Выход:** `data/generated/UK_KEYWORDS.md` (~449 ключей)

**Логика:** Аналогична RU, но читает из `uk/categories/`

## Формат выходного файла

```markdown
активная пена
антибитум
антидождь
воск для авто
...
```

Простой список, один ключ на строку, сортировка по алфавиту.

## Обработка legacy формата

Некоторые `_clean.json` имеют старый формат:

```json
{
  "keywords": {
    "primary": [{"keyword": "..."}],
    "synonyms_base": [{"keyword": "..."}]
  }
}
```

Скрипт должен обрабатывать оба формата:
- Новый: `keywords` — список
- Legacy: `keywords` — dict с группами

## Статистика

При запуске выводить:
```
Найдено 53 файлов _clean.json
Извлечено 1131 уникальных ключей
✅ Сохранено → data/generated/RU_KEYWORDS.md
```

## Зависимости

- Python 3.10+
- Стандартная библиотека (json, pathlib)

## Тесты

Не требуются — утилитарные скрипты для разовых задач.
