# Validation Skills Fix — Design Plan

> **Для Claude:** При редактировании скиллов ОБЯЗАТЕЛЬНО использовать `/skill-creator`.

**Дата:** 2026-01-30
**Статус:** Approved
**Цель:** Исправить скиллы валидации для корректной работы воркеров

---

## Проблемы

1. **Морфология:** pymorphy3 выдаёт фамилии (Surn) как normal_form → ложные PARTIAL
2. **SYNONYM считается покрытым:** ключ отсутствует, но covered=True
3. **keywords[] = WARNING:** воркеры игнорируют, пишут "FIXED" без фиксов
4. **Нет re-validate:** после фиксов не перепроверяется coverage
5. **Устаревшие скрипты:** `check_keyword_density.py`, `check_seo_structure.py` не существуют
6. **"Add organically":** слишком абстрактно, нет конкретики

---

## Согласованные правила Coverage

### Статусы

| Статус | covered | Действие |
|--------|---------|----------|
| EXACT | ✅ True | — |
| NORM | ✅ True | — |
| LEMMA | ✅ True | — |
| SYNONYM | ❌ **False** | Добавить сам ключ |
| PARTIAL | ❌ False | Собрать фразу |
| ABSENT | ❌ False | Добавить ключ |

### Severity

| Источник | Требование | Severity |
|----------|------------|----------|
| primary | 100% COVERED | BLOCKER |
| secondary | 100% COVERED | BLOCKER |
| supporting | ≥80% COVERED | WARNING |
| keywords[] | threshold (≤5→70%, 6-15→60%, >15→50%) | BLOCKER |

---

## Задачи

### Task 1: Fix morphology (keyword_utils.py)

**Файл:** `scripts/keyword_utils.py`

**Изменение:** В методе `get_lemma()` фильтровать фамилии:

```python
def get_lemma(self, word: str) -> str:
    parses = self._morph.parse(word)

    # Фильтруем фамилии (Surn) — дают ложные леммы
    non_surname = [p for p in parses if 'Surn' not in p.tag]

    if non_surname:
        return non_surname[0].normal_form

    return parses[0].normal_form if parses else word.lower()
```

**Тест:**
```python
assert morph.get_lemma("губка") == "губка"  # не "губко"
assert morph.get_lemma("губки") == "губка"
```

---

### Task 2: Fix coverage logic (coverage_matcher.py)

**Файл:** `scripts/coverage_matcher.py`

**Изменение:** SYNONYM → covered=False

```python
# При синоним-совпадении:
return MatchResult(
    status="SYNONYM",
    covered=False,  # было True
    covered_by=synonym_keyword,
    syn_match_method=method,
    reason="Synonym match only"
)
```

---

### Task 3: Fix audit_coverage.py verbose output

**Файл:** `scripts/audit_coverage.py`

**Изменение:** SYNONYM переносится в "✗ NOT COVERED":

```python
# Было: SYNONYM в "✓ COVERED"
# Стало: SYNONYM в "✗ NOT COVERED" или отдельный блок "⚠ SYNONYM-ONLY"
```

**Пример вывода:**
```
✗ NOT COVERED (3):
  - [SYNONYM] активна піна для авто (1600) ← via "активна піна для миття авто"
  - [PARTIAL] хімія для миття авто (1000) — 100% lemmas
  - [ABSENT] гель для миття авто (90)
```

---

### Task 4: Update skills (использовать /skill-creator)

**7 файлов:**

| Файл | Изменения |
|------|-----------|
| `content-reviewer/SKILL.md` | скрипты, re-validate, BLOCKER |
| `uk-content-reviewer/SKILL.md` | re-validate, BLOCKER |
| `quality-gate/SKILL.md` | скрипты |
| `uk-quality-gate/skill.md` | скрипты |
| `verify-content/SKILL.md` | скрипты |
| `uk-verify-content/SKILL.md` | re-validate |
| `shared/validation-checklist.md` | скрипты |

#### 4.1 Замена скриптов (все файлы)

```
check_keyword_density.py → validate_density.py
check_seo_structure.py   → validate_seo.py
```

#### 4.2 Новая severity table (content-reviewer, uk-content-reviewer, quality-gate, uk-quality-gate)

```markdown
| Источник | Требование | Severity |
|----------|------------|----------|
| primary | 100% COVERED | BLOCKER |
| secondary | 100% COVERED | BLOCKER |
| supporting | ≥80% COVERED | WARNING |
| keywords[] | threshold | BLOCKER |

**COVERED** = EXACT / NORM / LEMMA
**NOT COVERED** = SYNONYM / PARTIAL / ABSENT
```

#### 4.3 Новый Step: Re-validate (content-reviewer, uk-content-reviewer)

```markdown
### Step 10: Re-validate Coverage (ОБЯЗАТЕЛЬНО)

Після фіксів перезапустити:

```bash
python3 scripts/audit_coverage.py --slug {slug} --lang {ru|uk} --json --include-meta
```

**Критерії:**
- primary: 100% (EXACT/NORM/LEMMA)
- secondary: 100% (EXACT/NORM/LEMMA)
- keywords[]: ≥ threshold

**Якщо НЕ пройдено:**
1. Повернутись до Fix
2. Максимум 3 ітерації
3. Після 3-ї → FAILED

**Куди додавати ключі:**
- primary → Intro (перший абзац)
- secondary → H2 заголовки
- supporting → таблиці, сценарії, FAQ
- SYNONYM-only → вставити ключ поруч із синонімом
- PARTIAL 100% → зібрати слова у фразу
```

---

### Task 5: Update tests

**Файл:** `tests/unit/test_keyword_utils.py`

- Добавить тест на фильтрацию Surn
- Добавить тест "губка" → "губка" (не "губко")

**Файл:** `tests/unit/test_coverage_matcher.py`

- Добавить тест SYNONYM → covered=False

---

## Порядок выполнения

1. Task 1: Fix morphology
2. Task 5: Update tests (TDD)
3. Task 2: Fix coverage logic
4. Task 3: Fix audit verbose
5. Task 4: Update skills (через /skill-creator)
6. Commit всё вместе

---

## Verification

После всех изменений:

```bash
# 1. Тесты
pytest tests/unit/test_keyword_utils.py tests/unit/test_coverage_matcher.py -v

# 2. Проверка морфологии
python3 -c "from scripts.keyword_utils import MorphAnalyzer; m=MorphAnalyzer('uk'); print(m.get_lemma('губка'))"
# Ожидается: губка

# 3. Проверка coverage
python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --verbose
# SYNONYM должен быть в NOT COVERED

# 4. Batch audit
python3 scripts/audit_coverage.py --lang uk
```

---

**Version:** 1.0
