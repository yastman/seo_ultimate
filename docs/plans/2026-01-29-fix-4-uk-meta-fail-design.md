# Design: Fix 4 UK Meta FAIL

## Problem

`validate_meta.py --all` returns 4 FAIL for UK categories — primary_keyword in meta doesn't match MAX(volume) keyword from `_clean.json`.

## Root Cause Analysis

| # | Category | primary_keyword (MAX vol) | Current Issue | Pattern |
|---|----------|---------------------------|---------------|---------|
| 1 | ochistiteli-shin | очищувач гуми (260) | Title OK, Description uses "очищувач шин" (70) | Producer |
| 2 | poliroli-dlya-plastika | поліроль для пластику (1300) | Uses "...авто" (1000) everywhere | Producer |
| 3 | raspyliteli-i-penniki | розпилювач для води (480) | Uses "піноутворювач" (not in keywords!) | Shop |
| 4 | shchetka-dlya-moyki-avto | щітка для миття авто (1000) | Title: old formula "в Україні" | Shop |

## Formulas (from uk-generate-meta v16.1)

### Title
- pk ≤20 chars: `{pk} — купити в інтернет-магазині Ultimate`
- pk >20 chars: `{pk} — купити, ціни | Ultimate`

### H1
`{pk}` (no "Купити")

### Description

**Producer pattern** (ochistiteli-shin, poliroli-dlya-plastika):
```
{pk} від виробника Ultimate. {details}. Опт і роздріб.
```

**Shop pattern** (raspyliteli-i-penniki, shchetka-dlya-moyki-avto):
```
{pk} в інтернет-магазині Ultimate. {details}.
```

## Fixes

### 1. ochistiteli-shin (Producer)

**primary_keyword:** очищувач гуми (260)

```json
{
  "meta": {
    "title": "Очищувач гуми — купити в інтернет-магазині Ultimate",
    "description": "Очищувач гуми від виробника Ultimate. Засоби для чищення гуми перед чорнінням — готові та концентрати у тарі 0.5л, 1л, 5л. Опт і роздріб."
  },
  "h1": "Очищувач гуми"
}
```

### 2. poliroli-dlya-plastika (Producer)

**primary_keyword:** поліроль для пластику (1300) — NOT "...авто"!

```json
{
  "meta": {
    "title": "Поліроль для пластику — купити в інтернет-магазині Ultimate",
    "description": "Поліроль для пластику від виробника Ultimate. Догляд за торпедо та панелями — матові, глянцеві, з UV-захистом та антистатиком. Опт і роздріб."
  },
  "h1": "Поліроль для пластику"
}
```

### 3. raspyliteli-i-penniki (Shop)

**primary_keyword:** розпилювач для води (480)

Note: Current meta uses "піноутворювач" which is NOT in _clean.json keywords. Using actual primary from data.

```json
{
  "meta": {
    "title": "Розпилювач для води — купити в інтернет-магазині Ultimate",
    "description": "Розпилювач для води в інтернет-магазині Ultimate. Тригери, помпові розпилювачі, пінні насадки для мийок високого тиску."
  },
  "h1": "Розпилювач для води"
}
```

### 4. shchetka-dlya-moyki-avto (Shop)

**primary_keyword:** щітка для миття авто (1000)

```json
{
  "meta": {
    "title": "Щітка для миття авто — купити в інтернет-магазині Ultimate",
    "description": "Щітка для миття авто в інтернет-магазині Ultimate. М'які для кузова, жорсткі для дисків — телескопічні ручки, набори."
  },
  "h1": "Щітка для миття авто"
}
```

## Validation

After each fix:
```bash
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json --keywords uk/categories/{slug}/data/{slug}_clean.json
```

Final check:
```bash
python3 scripts/validate_meta.py --all
```

Expected: 0 FAIL

---

**Version:** 1.0
**Date:** 2026-01-29
