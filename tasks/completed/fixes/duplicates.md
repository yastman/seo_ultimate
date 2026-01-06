# Fixes: Keyword Duplicates

**Status:** PENDING
**Priority:** MEDIUM

---

## Issue D1: polirovalnye-krugi ↔ mekhovye

### Problem

Ключевые слова "меховой круг" и "шерстяной круг" присутствуют в обеих категориях:

- `polirovalnye-krugi` (полировальные круги)
- `mekhovye` (меховые круги)

### Current State

```
polirovalnye-krugi/_clean.json:
  - "меховой полировальный круг"
  - "шерстяной круг для полировки"

mekhovye/_clean.json:
  - "меховой круг"
  - "шерстяной круг"
```

### Solution

Убрать из `polirovalnye-krugi` ключи, которые относятся к `mekhovye`:

```json
// polirovalnye-krugi/_clean.json — УДАЛИТЬ:
{
  "keyword": "меховой полировальный круг",
  "cluster": "...",
  "note": "REMOVED: belongs to mekhovye category"
}
```

### Checklist

- [ ] Открыть `categories/polirovalnye-krugi/data/polirovalnye-krugi_clean.json`
- [ ] Найти ключи с "меховой/шерстяной"
- [ ] Удалить их из keywords
- [ ] Обновить stats.after
- [ ] Добавить note в clustering_notes
- [ ] Сохранить файл
- [ ] Валидировать JSON

### Validation

```bash
python3 -c "
import json
data = json.load(open('categories/polirovalnye-krugi/data/polirovalnye-krugi_clean.json'))
keywords_text = str(data['keywords'])
if 'меховой' in keywords_text or 'шерстяной' in keywords_text:
    print('FAIL: меховой/шерстяной still present')
else:
    print('PASS: duplicates removed')
"
```

---

## Issue D2: voski restructure

### Problem

Категория `voski` является родительской для:

- `tverdyy-vosk`
- `zhidkiy-vosk`

После создания подкатегорий нужно убрать из `voski` ключи, которые теперь принадлежат подкатегориям.

### Current State

```
voski/_clean.json:
  - "воск для авто" (main)
  - "твердый воск" (should be in tverdyy-vosk)
  - "жидкий воск" (should be in zhidkiy-vosk)
```

### Solution

1. Оставить в `voski` только общие ключи
2. Специфичные ключи уже в подкатегориях

### Checklist

- [ ] Открыть `categories/voski/data/voski_clean.json`
- [ ] Найти ключи с "твердый/твёрдый"
- [ ] Найти ключи с "жидкий"
- [ ] Удалить их (они уже в подкатегориях)
- [ ] Обновить stats.after
- [ ] Добавить note: "L2 parent, specifics moved to L3"
- [ ] Сохранить файл
- [ ] Валидировать JSON

### Validation

```bash
python3 -c "
import json
data = json.load(open('categories/voski/data/voski_clean.json'))
keywords_text = str(data['keywords'])
issues = []
if 'твердый' in keywords_text.lower() or 'твёрдый' in keywords_text.lower():
    issues.append('твердый')
if 'жидкий' in keywords_text.lower():
    issues.append('жидкий')
if issues:
    print(f'FAIL: found {issues}')
else:
    print('PASS: L2/L3 separation correct')
"
```

---

## Process for Fixing

1. **Backup** — скопировать оригинальный файл
2. **Edit** — внести изменения
3. **Validate** — проверить JSON и логику
4. **Commit** — записать в git (если используется)
5. **Update** — отметить здесь как DONE

---

## Status Tracking

| Issue | Status | Fixed Date |
|-------|--------|------------|
| D1: polirovalnye-krugi ↔ mekhovye | ⬜ PENDING | — |
| D2: voski restructure | ⬜ PENDING | — |

---

**Last Updated:** 2025-12-31
