# W1: audit_coverage.py --include-meta Integration Log

**Date:** 2026-01-30
**Task:** Завершить интеграцию флага --include-meta в audit_coverage.py

---

## Tasks Completed

### 1. Подключение --include-meta к JSON выводу в main()

**File:** `scripts/audit_coverage.py`

**Changes:**
- Перестроена логика вывода в single category mode (строки 348-368)
- Когда `args.json and args.include_meta` — вызывается `audit_with_meta()` вместо `audit_category()`
- Добавлена загрузка мета-ключей через `load_meta_keywords()`

```python
if args.json and args.include_meta:
    # --include-meta mode: audit both keywords_in_content and keywords[]
    meta_kw = load_meta_keywords(args.slug, lang)
    if meta_kw is None:
        meta_kw = {"primary": [], "secondary": [], "supporting": []}
    result = audit_with_meta(keywords, synonyms, meta_kw, content, lang)
    result["slug"] = args.slug
    result["lang"] = lang
    print(json.dumps(result, ensure_ascii=False, indent=2))
else:
    # Standard mode: only keywords[]
    result = audit_category(keywords, synonyms, content, lang)
    ...
```

### 2. Исправление теста test_audit_with_meta_groups_coverage_correctly

**File:** `tests/unit/test_coverage_matcher.py`

**Problem:** Тест использовал ключи "ключ1", "ключ2", "ключ3", "ключ4", которые все сводятся к одной лемме "ключ" (MorphAnalyzer отбрасывает цифры). Поэтому "ключ4" находился как LEMMA-match.

**Solution:** Заменил тестовые данные на реальные ключевые слова, которые не пересекаются по леммам:
- "активна піна", "безконтактна мийка", "автошампунь"
- "неіснуюче слово" — для проверки NOT COVERED

### 3. Запуск тестов

```bash
pytest tests/unit/test_coverage_matcher.py -v
```

**Result:** 40/40 PASSED

### 4. Ручное тестирование

```bash
python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --json --include-meta | head -60
```

**Result:** JSON содержит обе секции:
- `keywords_in_content` с группами primary/secondary/supporting
- `keywords` со всеми ключами из _clean.json

---

## Output Structure

```json
{
  "keywords_in_content": {
    "primary": {
      "total": 1,
      "covered": 1,
      "coverage_percent": 100.0,
      "results": [...]
    },
    "secondary": { ... },
    "supporting": { ... }
  },
  "keywords": {
    "total": N,
    "covered": M,
    "coverage_percent": X,
    "results": [...]
  },
  "slug": "aktivnaya-pena",
  "lang": "uk"
}
```

---

## Files Modified

1. `scripts/audit_coverage.py` — main() logic for --include-meta
2. `tests/unit/test_coverage_matcher.py` — test data fix

---

## Status: COMPLETE

Tasks 1-5 из плана выполнены. Коммиты не делались (по инструкции).
