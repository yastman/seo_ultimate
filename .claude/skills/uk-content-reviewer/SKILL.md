---
name: uk-content-reviewer
description: Ревізія та виправлення UK контенту категорії по плану v3.0. Use when uk-content-reviewer {slug}, перевір UK контент, ревізія українського контенту. Автономний режим — знаходить та виправляє проблеми без інтерактивності.
---

# UK Content Reviewer v2.1

Перевірка та виправлення контенту **однієї UK категорії** за виклик.

## Input

```
uk-content-reviewer {slug}
uk-content-reviewer aktivnaya-pena
```

## Data Files

```
uk/categories/{slug}/
├── content/{slug}_uk.md        # Контент для ревізії
├── data/{slug}_clean.json      # name, parent_id, keywords
├── meta/{slug}_meta.json       # h1, keywords_in_content
└── research/RESEARCH_DATA.md   # Джерело істини для фактів (або посилання на RU)
```

---

## Commercial Intent (центральний принцип)

**Головне питання тексту:** "Який товар мені купити?"

**Тест кожної секції:**
> "Ця секція допомагає ОБРАТИ товар чи ВЧИТЬ його використовувати?"

| Відповідь | Дія |
|-----------|-----|
| Допомагає обрати | ✅ Залишити |
| Вчить використовувати | ❌ Видалити або переробити |

### Комерційний vs Інформаційний

| ✅ Комерційний | ❌ Інформаційний |
|----------------|------------------|
| "Якщо потрібен X → обирай Y" | "Як працює X" |
| Таблиця "Тип → Коли брати" | Покрокова інструкція |
| Сценарії: новачок/профі/бюджет | Теорія та принципи |
| FAQ про вибір | FAQ про процеси |

---

## Dryness Diagnosis

| # | Ознака | Weight |
|---|--------|--------|
| 1 | Intro = визначення "X — це Y..." | 2 |
| 2 | Немає звернень "вам", "якщо ви" | 1 |
| 3 | <3 патернів "Якщо X → Y" | 1 |
| 4 | Таблиці без "Коли брати" | 1 |
| 5 | FAQ про процес | 2 |
| 6 | Academic <7% | 1 |
| 7 | Немає секції "Сценарії покупки" | 1 |

**Verdict:**
- 0-2 → ✅ TEXT OK
- 3-4 → ⚠️ MINOR FIXES
- 5+ → ❌ REWRITE NEEDED

---

## Workflow

```
Step 1: Read files (parallel)
Step 2: Run validators (parallel)
Step 3: Keywords Coverage (audit_coverage.py)
Step 4: Research Completeness
Step 5: Commercial Intent Check
Step 6: Dryness Diagnosis
Step 7: UK Terminology Check
Step 8: Verdict table
Step 9: Fix if BLOCKER or REWRITE if needed
Step 10: Re-validate
Step 11: Output verdict
```

### Step 1: Read files (parallel)

- `_clean.json` → name, parent_id
- `_meta.json` → h1, keywords_in_content
- `RESEARCH_DATA.md` → джерело істини
- `{slug}_uk.md` → контент

### Step 2: Run validators (parallel)

```bash
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
python3 scripts/validate_content.py uk/categories/{slug}/content/{slug}_uk.md "{primary}" --mode seo
python3 scripts/validate_density.py uk/categories/{slug}/content/{slug}_uk.md --lang uk
python3 scripts/check_water_natasha.py uk/categories/{slug}/content/{slug}_uk.md
python3 scripts/validate_seo.py uk/categories/{slug}/content/{slug}_uk.md "{primary}"
```

### Step 3: Keywords Coverage (audit_coverage.py)

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang uk --json --include-meta
```

**Інтерпретація JSON-виводу:**

JSON містить два блоки:
1. `keywords_in_content` — ключі з _meta.json (primary/secondary/supporting)
2. `keywords` — всі ключі з _clean.json

**Алгоритм валідації:**

```python
# 1. Перевірити keywords_in_content
primary = json["keywords_in_content"]["primary"]
secondary = json["keywords_in_content"]["secondary"]
supporting = json["keywords_in_content"]["supporting"]

# primary + secondary: 100% coverage required
ps_total = primary["total"] + secondary["total"]
ps_covered = primary["covered"] + secondary["covered"]
if ps_covered < ps_total:
    # BLOCKER — знайти NOT COVERED:
    not_covered = [r for r in primary["results"] + secondary["results"]
                   if not r["covered"]]
    # status: TOKENIZATION, PARTIAL, ABSENT = NOT COVERED

# supporting: ≥80% coverage
if supporting["coverage_percent"] < 80:
    # WARNING

# 2. Перевірити keywords[] (adaptive threshold)
kw = json["keywords"]
total = kw["total"]
threshold = 70 if total <= 5 else (60 if total <= 15 else 50)
if kw["coverage_percent"] < threshold:
    # WARNING
```

**Статуси покриття:**
- ✅ COVERED: `EXACT`, `NORM`, `LEMMA`, `SYNONYM`
- ❌ NOT COVERED: `TOKENIZATION`, `PARTIAL`, `ABSENT`

**Правила вердикту:**

| Джерело | Вимога | Severity |
|---------|--------|----------|
| primary+secondary | **100% COVERED** | BLOCKER |
| supporting | **≥80% COVERED** | WARNING |
| keywords[] | adaptive threshold | WARNING |

**Формат виводу в лог:**

```markdown
### Keywords Coverage

| Джерело | Covered | Total | % | Status |
|---------|---------|-------|---|--------|
| primary+secondary | 8/8 | 100% | ✅ PASS |
| supporting | 4/5 | 80% | ✅ PASS |
| keywords[] | 8/15 | 53% | ⚠️ WARNING (threshold 50%) |

**NOT COVERED (primary/secondary):** ключ1 (1200), ключ2 (800)
**NOT COVERED (keywords[]):** топ-5 по volume
```

**Куди розподіляти непокриті ключі:**
- primary → Intro (перший абзац)
- secondary → H2 заголовки
- supporting → Сценарії покупки, таблиці, FAQ

### Step 4: Research Completeness

| Блок Research | Перевірка | Severity |
|---------------|-----------|----------|
| Блок 2: Види та типи | **Всі типи** в тексті | BLOCKER |
| Блок 6а: Спірні | НЕ використані | BLOCKER |
| Блок 1, 3, 5 | Факти відображені | WARNING |

### Step 5: Commercial Intent Check

Кожна секція про ВИБІР, не про використання?

### Step 6: Dryness Diagnosis

Підрахунок ознак → verdict (TEXT OK / MINOR / REWRITE)

### Step 7: UK Terminology Check (BLOCKER)

| RU термін | UK термін | Статус |
|-----------|-----------|--------|
| резина | гума | BLOCKER |
| мойка | миття | BLOCKER |
| стекло | скло | BLOCKER |
| чернитель | чорнитель | WARNING |
| очиститель | очищувач | WARNING |
| покрытие | покриття | WARNING |
| поверхность | поверхня | WARNING |
| защита | захист | WARNING |
| блеск | блиск | WARNING |
| нанесение | нанесення | WARNING |
| чистка | чищення | WARNING |

```bash
# Перевірка RU термінів, яких НЕ повинно бути
grep -c "резина" uk/categories/{slug}/content/{slug}_uk.md  # Має бути 0
grep -c "мойка" uk/categories/{slug}/content/{slug}_uk.md   # Має бути 0
grep -c "стекло" uk/categories/{slug}/content/{slug}_uk.md  # Має бути 0
```

### Step 8: Verdict table

| Критерій | Результат | Примітка |
|----------|-----------|----------|
| Meta | ✅/❌ | validate_meta.py |
| Density | ✅/⚠️/❌ | stem max X% |
| Academic | ✅/⚠️ | X% (≥7%) |
| **Keywords** | ✅/⚠️/❌ | **primary+secondary X/X, supporting X/X** |
| **Research Types** | ✅/❌ | **всі типи з Блок 2** |
| **Commercial Intent** | ✅/❌ | всі секції про вибір |
| **Dryness** | ✅/⚠️/❌ | TEXT OK / MINOR / REWRITE |
| **UK Terminology** | ✅/❌ | немає RU термінів |
| H2 з keyword | ✅/⚠️ | мін. 2 H2 |
| Intro | ✅/❌ | buyer guide / визначення |
| Сценарії покупки | ✅/❌ | є секція |
| FAQ | ✅/❌ | про вибір / про процес |
| **VERDICT** | **✅/⚠️/❌** | |

---

## Reference-based Rewrite

**Коли:** REWRITE NEEDED (Dryness 5+)

### Референсні тексти

```
uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md
uk/categories/antibitum/content/antibitum_uk.md
uk/categories/cherniteli-shin/content/cherniteli-shin_uk.md
```

### Патерни з референсів

| Елемент | Патерн |
|---------|--------|
| **Intro** | користь + "якщо X → Y" + звернення |
| **Таблиця типів** | колонка "Коли брати" |
| **Сценарії покупки** | **Жирна умова** → рішення |
| **FAQ** | Питання про ВИБІР |
| **Підсумок** | → сценарії |

---

## BLOCKER Fixes

| Issue | Fix |
|-------|-----|
| H1 ≠ name | Replace H1 |
| How-to sections | Delete or convert |
| Stem >3.0% | Replace with synonyms |
| Intro = визначення | Rewrite: користь + сценарій |
| >2 primary missing | Add keywords organically |
| Research types missing | Add all types |
| RU термін знайдено | Replace with UK термін |

## How-to STOP-LIST

| ❌ Заборонено | ✅ Альтернатива |
|---------------|-----------------|
| "Як наносити X" | "Що врахувати при виборі" |
| "Техніка застосування" | Прибрати секцію |
| "Покрокова інструкція" | Видалити |

---

## Output Format

```markdown
## Review: {slug} (UK)

**Path:** uk/categories/{slug}
**Verdict:** ✅ PASS / ⚠️ WARNING / ❌ FIXED

### Verdict Table

| Критерій | Результат | Примітка |
|----------|-----------|----------|
| ... | ... | ... |

### Виправлення (якщо були)

1. ...
2. ...

### Re-validation

✅ All validators passed after fixes
```

---

## ВАЖЛИВО

1. **НЕ комітити** — тільки Edit. Коміт вручну.
2. **RESEARCH_DATA.md — джерело істини** для фактів.
3. **Одна категорія за виклик**.
4. **Buyer guide, не how-to**.
5. **Academic ≥7%** — якщо нижче, додати звернення.
6. **UK термінологія** — BLOCKER якщо знайдено RU терміни.
7. **НЕ ВИГАДУЙ факти** — при додаванні ключів використовуй ТІЛЬКИ інформацію з RESEARCH_DATA.md. Якщо немає відповідного факту — впроваджуй ключ в існуючий контекст без нових тверджень.

---

**Version:** 2.2 — January 2026

**Changelog v2.2:**
- **ADDED: JSON інтерпретація** — детальний алгоритм валідації JSON-виводу audit_coverage.py
- Пояснення статусів покриття (EXACT/NORM/LEMMA/SYNONYM vs TOKENIZATION/PARTIAL/ABSENT)
- Інструкція куди розподіляти непокриті ключі

**Changelog v2.1:**
- **ADDED: audit_coverage.py інтеграція** — Step 3 використовує `--include-meta` для детальної перевірки coverage
- Автоматична перевірка primary/secondary/supporting з JSON-виводом
- Чіткі severity: BLOCKER для primary+secondary, WARNING для supporting та keywords[]

**Changelog v2.0:**
- **Синхронізовано з RU content-reviewer v2.0** — повний паритет
- ADDED: UK Terminology Check (Step 7)
- ADDED: check_seo_structure.py валідація
- ADDED: H2 з keyword перевірка
- ADDED: Розширена таблиця термінології
- Українізовані всі тексти та приклади
