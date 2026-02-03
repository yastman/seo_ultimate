# Plural Meta Validation — Design Document

## Problem

16 UK категорій FAIL валідацію:
- `primary_keyword` = "очищувач слідів комах" (однина)
- Title/H1 = "Очищувачі від комах" (множина + інша фраза)

**Дві проблеми:**
1. Title/H1 використовують **іншу фразу** (порушення IRON RULE)
2. Title/H1 у **множині**, а валідатор шукає однину

## Root Cause

Скілл має неоднозначну логіку:
- Каже "конвертувати в множину"
- Не чітко прописано ЩО конвертувати
- Claude "творчо" скорочує фрази

## Solution

### Principle

**Title = H1 = plural(title_phrase)** — множина, бо категорія магазину з багатьма товарами.

```
title_phrase = category_title ?? primary_keyword
H1 = plural(title_phrase)      # множина першого слова
Title = H1 + " — купити..."    # той самий H1
Description = title_phrase...   # може бути однина
```

### Components to Update

1. **keyword_utils.py** — додати `to_plural()`, `phrase_to_plural()`
2. **generate-meta SKILL.md** (RU) — чітка формула Title = H1
3. **uk-generate-meta SKILL.md** (UK) — чітка формула Title = H1
4. **validate_meta.py** — перевіряти plural форму title_phrase

---

## Component 1: keyword_utils.py

### New Functions

```python
class MorphAnalyzer:

    # Fallback dictionaries for words pymorphy can't inflect
    _PLURAL_FALLBACK_RU = {"набор": "наборы", "губка": "губки", ...}
    _PLURAL_FALLBACK_UK = {"набір": "набори", "губка": "губки", ...}

    def to_plural(self, word: str) -> str:
        """
        Конвертувати слово в множину (називний відмінок).

        очиститель → очистители
        губка → губки
        """
        # 1. Check fallback dict
        # 2. Try pymorphy3 inflect({'plur', 'nomn'})
        # 3. Return original if fails

    def phrase_to_plural(self, phrase: str) -> str:
        """
        Конвертувати фразу в множину (тільки перше слово).

        "очиститель дисков" → "Очистители дисков"
        """
```

### Test Cases

| Input (RU) | Expected |
|------------|----------|
| очиститель | очистители |
| набор | наборы |
| губка | губки |
| ведро | вёдра |
| воск | воски |

| Input (UK) | Expected |
|------------|----------|
| очищувач | очищувачі |
| набір | набори |
| губка | губки |
| відро | відра |
| віск | воски |

| Phrase (RU) | Expected |
|-------------|----------|
| очиститель дисков | Очистители дисков |
| губка для авто | Губки для авто |

---

## Component 2: generate-meta SKILL.md (RU)

### Current (broken)

```
H1 = plural(primary_keyword)
Title = ??? (неоднозначно)
```

### New (clear)

```markdown
## Формула

title_phrase = category_title ?? primary_keyword
H1 = phrase_to_plural(title_phrase)
Title = H1 + " — купить, цены | Ultimate"

## Приклад

_clean.json: primary_keyword = "очиститель дисков"

H1: "Очистители дисков"
Title: "Очистители дисков — купить, цены | Ultimate"
Description: "Очиститель дисков от производителя..."
```

### IRON RULE (updated)

```
title_phrase використовується ДОСЛІВНО.
Дозволено ТІЛЬКИ:
1. Капіталізація першої літери
2. Конвертація першого слова в множину

НЕ ДОЗВОЛЕНО:
- Скорочувати фразу
- Міняти слова
- "Оптимізувати"
```

---

## Component 3: uk-generate-meta SKILL.md (UK)

Same changes as RU, with Ukrainian examples.

---

## Component 4: validate_meta.py

### Current Logic

```python
# Шукає exact match або lemma match
primary_keywords = [category_title] or [max_volume_keyword]
keyword_matches(primary_keywords[0], title)
```

### New Logic

```python
# Шукає title_phrase АБО plural(title_phrase)
title_phrase = category_title or max_volume_keyword
plural_phrase = phrase_to_plural(title_phrase)

# Match якщо знайдено або однину, або множину
found = keyword_matches(title_phrase, title) or keyword_matches(plural_phrase, title)
```

---

## Validation Checklist

After implementation:

```bash
# All должны PASS
python3 scripts/validate_meta.py --all

# Specific tests
python3 -c "
from scripts.keyword_utils import MorphAnalyzer
m = MorphAnalyzer('uk')
assert m.phrase_to_plural('очищувач слідів комах') == 'Очищувачі слідів комах'
assert m.phrase_to_plural('набір для авто') == 'Набори для авто'
print('OK')
"
```

---

## Implementation Order

1. **keyword_utils.py** — add `to_plural()`, `phrase_to_plural()`
2. **Tests** — verify plural conversion works
3. **validate_meta.py** — update to accept plural
4. **generate-meta SKILL.md** — clarify formulas (RU)
5. **uk-generate-meta SKILL.md** — clarify formulas (UK)
6. **Fix 16 UK meta files** — regenerate with correct plural

---

**Version:** 1.0 — February 2026
