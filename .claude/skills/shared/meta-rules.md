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
| Length | 30-60 chars (unique part before `\|`) |
| Structure | **{H1}** + commercial + brand |
| Formula | `{H1} — купить/купити, цены/ціни \| Ultimate` |
| Front-loading | **Keyword FIRST** (NOT "Купить {keyword}") |
| Brand | "Ultimate" at end |
| Forbidden | Colons (Google replaces with dash) |

### Title Formula

```
✅ CORRECT: {H1} — купити, ціни | Ultimate
❌ WRONG:   Купити {H1} в Україні | Ultimate
```

**H1 = primary_keyword in PLURAL form** (see H1 Rules below)

### Examples

| H1 (plural) | Title |
|-------------|-------|
| Очищувачі дисків | **Очищувачі дисків — купити, ціни \| Ultimate** |
| Силанти для авто | **Силанти для авто — купити, ціни \| Ultimate** |
| Знежирювачі | **Знежирювачі — купити в інтернет-магазині Ultimate** |

**Adaptive formula:**
- If H1 ≤ 20 chars: `{H1} — купити в інтернет-магазині Ultimate`
- If H1 > 20 chars: `{H1} — купити, ціни | Ultimate`

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

**Formula:** `{primary_keyword}` → **PLURAL FORM**

**🚨 CRITICAL: H1 must be in PLURAL form because category contains multiple products.**

### Plural Conversion Table

| Singular (RU) | Plural (RU) | Singular (UK) | Plural (UK) |
|---------------|-------------|---------------|-------------|
| Очиститель | **Очистители** | Очищувач | **Очищувачі** |
| Полироль | **Полироли** | Поліроль | **Поліролі** |
| Силант | **Силанты** | Силант | **Силанти** |
| Обезжириватель | **Обезжириватели** | Знежирювач | **Знежирювачі** |
| Пятновыводитель | **Пятновыводители** | Плямовивідник | **Плямовивідники** |
| Нейтрализатор | **Нейтрализаторы** | Поглинач | **Нейтралізатори** |
| Губка | **Губки** | Губка | **Губки** |
| Ведро | **Вёдра** | Відро | **Відра** |
| Набор | **Наборы** | Набір | **Набори** |
| Воск | **Воски** | Віск | **Воски** |
| Шампунь | **Шампуни** | Шампунь | **Шампуні** |
| Щётка | **Щётки** | Щітка | **Щітки** |
| Машинка | **Машинки** | Машинка | **Машинки** |
| Круг | **Круги** | Круг | **Круги** |
| Средство | **Средства** | Засіб | **Засоби** |
| Торнадор | **Торнадоры** | Торнадор | **Торнадори** |
| Восстановитель | **Восстановители** | Відновлювач | **Відновлювачі** |

### Algorithm

1. Take `{primary_keyword}` from `_clean.json` (MAX volume)
2. Convert first word to **plural** using table above
3. Keep rest of phrase unchanged

```
primary_keyword: "очиститель дисков" (singular)
H1: "Очистители дисков" (plural)

primary_keyword: "силант для авто" (singular)
H1: "Силанты для авто" (plural)

primary_keyword: "губка для авто" (singular)
H1: "Губки для авто" (plural)
```

### Exceptions (already plural or collective)

These categories DON'T need conversion:
- glavnaya (Автохімія/Автохимия — collective)
- aksessuary (Аксесуари — already plural)
- oborudovanie (Обладнання — collective)
- zashchitnye-pokrytiya (Захисні покриття — already plural)
- polirovka (Полірування — process, not product)

**Other rules:**
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
