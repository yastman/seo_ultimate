# W1 Semantic Cluster Log

Дата: 2026-01-29 11:44


## aksessuary
- Найдено дублей: 1
- Перенесено в synonyms: 1 (уже в synonyms, добавлен use_in: lsi)
- Canonical: все для мойки авто
- Variants: все для мойки автомобилей → lsi

## aksessuary-dlya-naneseniya-sredstv
- Найдено дублей: 2
- Перенесено в synonyms: 2
- Canonical: губка для полировки авто
- Variants: губка для полировки автомобиля, полировочная губка для авто → lsi

## gubki-i-varezhki
- Найдено дублей: 6
- Перенесено в synonyms: 6
- Canonical: мочалка для авто, губка для авто, перчатка для мойки авто, губка для мойки авто, мочалки для мойки авто, варежка для мойки авто
- Variants: мочалка для автомобиля, губки для автомобиля, губки для мойки автомобиля, мочалка для мойки автомобиля, перчатка для мойки автомобиля, варежка для мойки автомобиля → lsi

## malyarniy-skotch
- Найдено дублей: 2
- Перенесено в synonyms: 2
- Canonical: малярный скотч, малярный скотч 10мм
- Variants: малярные скотчи, малярный скотч 10 мм → lsi

## mikrofibra-i-tryapki
- Найдено дублей: 0 (уже организовано с synonym_of)
- Перенесено в synonyms: 0
- Статус: Уже кластеризовано - synonym_of поля на месте
- Примечание: Нестандартная структура keywords (вложенный объект), но synonym_of корректны

## nabory
- Найдено дублей: 4
- Перенесено в synonyms: 4
- Canonical: набор для ухода за авто, набор для мойки авто, набор для химчистки автомобиля, набор для полировки авто
- Variants: наборы для ухода за автомобилем, набор для мойки автомобиля, набор для химчистки авто, комплект для полировки авто → lsi

## raspyliteli-i-penniki
- Найдено дублей: 3
- Перенесено в synonyms: 3
- Canonical: помповый распылитель для мойки авто, распылитель для мойки авто
- Variants: помповый распылитель для авто, распылитель для мойки машины, распылитель для мытья машины → lsi

## kisti-dlya-deteylinga
- Найдено дублей: 2
- Перенесено в synonyms: 2
- Canonical: щетка для чистки салона авто, кисти для детейлинга
- Variants: щетка для чистки салона автомобиля, кисточки для детейлинга → lsi

## shchetka-dlya-moyki-avto
- Найдено дублей: 4
- Перенесено в synonyms: 4
- Canonical: щетка для мойки авто, щетка для мытья машины, щетка для автомобиля
- Variants: щетки для мойки машины, щетка для мытья авто, щетка для мытья автомобиля, щетка автомобильная → lsi

## vedra-i-emkosti
- Найдено дублей: 1
- Перенесено в synonyms: 1
- Canonical: ведро для мойки автомобиля
- Variants: ведра для мойки авто → lsi

## glavnaya
- Найдено дублей: 5
- Перенесено в synonyms: 5
- Canonical: автохимия, автохимия для авто, косметика для авто, автокосметика для авто
- Variants: авто химия, автохимия для автомобиля, химия для автомобиля, косметика для автомобиля, автокосметика для автомобиля → lsi

---
## Валидация
- aksessuary_meta.json: ✅ PASS
- glavnaya_clean.json: ✅ valid JSON (meta не создан)

---
## Итог
- Обработано категорий: 11
- Всего дублей: 24
- Всего перенесено в synonyms: 24

**Статус: ГОТОВО**

---

# W1 Code Review Fixes Log

Дата: 2026-01-29 (Session 2)

## Assigned Tasks: 1, 2, 8 (seo_utils.py fixes)

---

## Task 1: Fix clean_markdown() to handle numbered lists

**File:** `scripts/seo_utils.py:391-392`

**Problem:** `clean_markdown()` did not remove ordered list markers (1. 2.)

**Fix:** Added regex pattern to strip ordered list markers:
```python
# Remove list markers (unordered and ordered)
text = re.sub(r"^[-*+]\s+", "", text, flags=re.MULTILINE)
text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.MULTILINE)
```

**Verification:**
```
pytest tests/unit/test_seo_utils.py::TestCleanMarkdown::test_remove_lists -v --no-cov
PASSED
```

---

## Task 2: Fix normalize_text() to remove punctuation

**File:** `scripts/seo_utils.py:437-441`

**Problem:** `normalize_text()` did not remove punctuation marks

**Fix:** Added punctuation removal step (preserving apostrophes in contractions):
```python
# 7. Remove punctuation (preserve apostrophes in contractions and hyphens in words)
text = re.sub(r"[,!?;:\"(){}[\]<>]", "", text)
text = re.sub(r"\.(?=\s|$)", "", text)  # Remove periods at word boundaries
```

**Verification:**
```
pytest tests/unit/test_seo_utils.py::TestNormalizeText -v --no-cov
3 passed
```

---

## Task 8: Add is_blacklisted_domain to seo_utils.py exports

**File:** `scripts/seo_utils.py` (imports section)

**Problem:** `is_blacklisted_domain` was not re-exported from seo_utils.py, breaking backwards compatibility for competitors.py

**Fix:** Added re-export:
```python
# URL utilities moved to scripts/utils/url.py
# Re-export for backwards compatibility
from scripts.utils.url import is_blacklisted_domain
```

**Verification:**
```bash
python3 -c "from scripts.seo_utils import is_blacklisted_domain; print('OK')"
OK
```

---

## Final Verification

All seo_utils tests pass (29/29):
```
pytest tests/unit/test_seo_utils.py -v --no-cov
29 passed
```

---

## Status: COMPLETE

All 3 tasks (1, 2, 8) completed successfully. No regressions detected.
