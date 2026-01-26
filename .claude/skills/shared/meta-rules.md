# Shared Meta Rules

Common meta tag rules for RU and UK categories.

---

## IRON RULE: primary_keyword — VERBATIM

`{primary_keyword}` from `_clean.json` is used in Title/H1/Description **without changing words or order**.

Only allowed: capitalize first letter.

```
_clean.json: "keywords": [{"keyword": "воск для авто", "volume": 1000}]

✅ Title: Воск для авто — купить...
✅ H1: Воск для авто

❌ Title: Автовоск — купить...     ← CHANGED KEYWORD!
❌ H1: Автомобильный воск          ← CHANGED KEYWORD!
```

**NOT allowed:**
- Change word order
- Add words ("авто" → "автомобильный")
- Merge words ("воск для авто" → "автовоск")
- "Improve" or "optimize" the keyword
- Use synonyms instead of primary_keyword

---

## Title Rules

| Rule | Value |
|------|-------|
| Length | 50-60 chars (unique part) |
| Structure | {primary_keyword} + commercial + brand |
| Commercial | "купить/купити" AFTER keyword |
| Brand | "Ultimate" at end |
| Forbidden | Colons (Google replaces with dash) |

---

## Description Rules

### Producer Pattern (has Ultimate products)

```
{primary_keyword} от производителя Ultimate. {Types} — {details}. Опт и розница.
```

### Shop Pattern (NO Ultimate products)

```
{primary_keyword} в интернет-магазине Ultimate. {Types} — {details}.
```

**Shop categories (no Ultimate products):**
- glina-i-avtoskraby
- gubki-i-varezhki
- cherniteli-shin
- raspyliteli-i-penniki
- vedra-i-emkosti
- kisti-dlya-deteylinga
- shchetka-dlya-moyki-avto
- polirovalnye-krugi
- polirovalnye-mashinki

---

## H1 Rules

**Formula:** `{primary_keyword}`

**Rules:**
- = primary_keyword VERBATIM
- NO "Купить/Купити"
- NO additions ("для авто" if not in keyword)

---

## Red Flags — STOP and fix

| Thought | Reality |
|---------|---------|
| "Sounds better this way" | primary_keyword = semantic data. Your opinion ≠ data. |
| "I'll add 'для авто' for clarity" | If not in primary_keyword — DON'T add! |
| "It's a synonym" | Synonym ≠ exact match. Google distinguishes. |
| "This way it's shorter/longer" | Length is adjusted by Title tail, NOT keyword. |

**All these thoughts = go back to `_clean.json` and take primary_keyword VERBATIM.**
