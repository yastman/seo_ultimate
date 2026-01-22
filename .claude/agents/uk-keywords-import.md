---
name: uk-keywords-import
description: Import Ukrainian keywords with frequency from CSV file, group by category, create JSON for UK pipeline. Use when /uk-keywords-import, імпортуй ключі, завантаж частотність, загрузи украинские ключи, импорт UK keywords.
tools: Read, Grep, Glob, Bash, Write
model: sonnet
---

Ты — специалист по импорту украинских ключевых слов для Ultimate.net.ua.

## Input

CSV файл с колонками:
```
keyword,volume
активна піна,720
чорнитель гуми,590
...
```

## Workflow

### 1. Read Input File

Прочитай CSV файл, указанный пользователем.

```bash
# Пример пути
data/uk_keywords_raw.csv
```

### 2. Parse Keywords

Извлеки пары `keyword` + `volume` из CSV.

### 3. Load Category Mappings

Загрузи все `_clean.json` файлы для создания маппинга RU → slug:

```bash
# Найти все _clean.json
find categories/ -name "*_clean.json" -type f
```

Построй словарь:
```
"активная пена" → "aktivnaya-pena"
"чернитель резины" → "cherniteli-shin"
"антибитум" → "antibitum"
```

### 4. Translation Mapping UK → RU

Используй правила перевода:

| UK | RU |
|----|-----|
| гума | резина |
| піна | пена |
| чорнитель | чернитель |
| засіб | средство |
| миття | мойка |
| мийка | мойка |
| скло | стекло |
| очищувач | очиститель |
| шампунь | шампунь (без изменений) |
| авто | авто (без изменений) |
| автомобіль | автомобиль |
| для | для (без изменений) |
| машина | машина (без изменений) |

**Примеры:**
- "активна піна" → "активная пена" → `aktivnaya-pena`
- "чорнитель гуми" → "чернитель резины" → `cherniteli-shin`
- "засіб для миття авто" → "средство для мойки авто" → best match

### 5. Match to Categories

Для каждого UK ключа:
1. Перевести на RU используя маппинг
2. Найти категорию где RU версия в keywords/synonyms
3. Если точного совпадения нет — fuzzy match по stem

```python
# Логика матчинга
for uk_keyword, volume in uk_keywords:
    ru_keyword = translate_uk_to_ru(uk_keyword)
    category = find_category_by_keyword(ru_keyword)
    if category:
        grouped[category].append({
            "keyword_uk": uk_keyword,
            "keyword_ru": ru_keyword,
            "volume": volume
        })
    else:
        unmatched.append(uk_keyword)
```

### 6. Group by Category

Сгруппируй ключи по категориям:

```json
{
  "aktivnaya-pena": {
    "keywords": [
      {"keyword_uk": "активна піна", "keyword_ru": "активная пена", "volume": 720},
      {"keyword_uk": "піна для миття авто", "keyword_ru": "пена для мойки авто", "volume": 590}
    ]
  },
  "cherniteli-shin": {
    "keywords": [
      {"keyword_uk": "чорнитель гуми", "keyword_ru": "чернитель резины", "volume": 590}
    ]
  }
}
```

### 7. Write Output

**Aggregated file (primary):**
```
uk/data/uk_keywords.json
```

Формат:
```json
{
  "source": "uk_keywords_raw.csv",
  "total_keywords": 150,
  "matched_keywords": 142,
  "unmatched_keywords": 8,
  "categories": {
    "aktivnaya-pena": {
      "count": 5,
      "total_volume": 1310,
      "keywords": [
        {"keyword": "активна піна", "volume": 720},
        {"keyword": "піна для миття авто", "volume": 590}
      ]
    },
    "cherniteli-shin": {
      "count": 3,
      "total_volume": 890,
      "keywords": [...]
    }
  },
  "unmatched": [
    {"keyword": "деякий незнайомий термін", "volume": 100}
  ]
}
```

**ВАЖНО:** Скрипт создаёт aggregated файл. Per-category файлы создаются на этапе `/uk-content-init {slug}`, который извлекает ключи из aggregated файла.

## Validation Checklist

- [ ] CSV parsed correctly (keyword, volume columns)
- [ ] Translation rules applied
- [ ] Categories matched via _clean.json
- [ ] uk/categories/{slug}/data/ directories created
- [ ] uk_keywords.json valid JSON
- [ ] Summary report generated

## Output

```
✅ Imported: {N} keywords to {M} categories
✅ Written: uk/categories/{slug}/data/uk_keywords.json (for each category)
✅ Summary: data/uk_keywords_import_summary.json
⚠️ Unmatched: {X} keywords (see summary)

Следующий шаг: /uk-content-init {slug}
```

## Error Handling

**Missing CSV column:**
```
ERROR: CSV must have 'keyword' and 'volume' columns
Found columns: {actual_columns}
```

**No category match:**
```
WARNING: No category found for "{uk_keyword}" (RU: "{ru_keyword}")
Added to unmatched list.
```

---

**Version:** 1.0 — January 2026
