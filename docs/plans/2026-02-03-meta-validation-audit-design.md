# Meta Validation & Audit Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Забезпечити що скрипти валідації мета-тегів працюють коректно для RU та UK категорій, покрити тестами, пофіксити знайдені проблеми.

**Architecture:** Виправити пошук файлів в `validate_meta.py` (rglob замість glob), додати unit та E2E тести, провести аудит скіллів generate-meta, пофіксити мета-дані.

**Tech Stack:** Python, pytest, pytest markers (e2e), subprocess для E2E тестів.

---

## Поточний стан (результати аудиту)

| Перевірка | RU | UK |
|-----------|----|----|
| validate_meta.py --all | 8 знайдено (баг!) | 54 PASS |
| audit_h1_primary.py | 7 OK, 1 MISMATCH (glavnaya) | 54 OK |

**Реальні проблеми:**
1. **Баг пошуку:** `--all` знаходить тільки 8 RU категорій замість 53 (вкладені ігноруються)
2. **RU glavnaya:** H1 "Автохимия" ≠ category_title "Автохимия и автокосметика"

---

## Структура категорій

```
categories/                          # RU root
├── aktivnaya-pena/meta/*.json       # L1 (8 шт)
├── moyka-i-eksterer/
│   ├── meta/*.json                  # L1
│   └── ochistiteli-diskov/meta/*.json  # L2 вкладена (45 шт)
└── ...

uk/categories/                       # UK root
├── aktivnaya-pena/meta/*.json       # 54 шт (плоска структура)
└── ...
```

---

## Milestone 1: Фікс пошуку файлів

**Files:**
- Modify: `scripts/validate_meta.py`
- Test: `tests/unit/test_validate_meta.py`

### Task 1.1: Виправити glob → rglob

```python
# Було:
Path("categories").glob("*/meta/*_meta.json")

# Стане:
Path("categories").rglob("*_meta.json")
```

### Task 1.2: Unit-тест для RU

```python
def test_find_all_meta_files_ru():
    files = find_all_meta_files(lang="ru")
    assert len(files) >= 50  # мінімум 50 RU категорій
```

### Task 1.3: Unit-тест для UK

```python
def test_find_all_meta_files_uk():
    files = find_all_meta_files(lang="uk")
    assert len(files) >= 50  # мінімум 50 UK категорій
```

### Task 1.4: Запустити тести

```bash
pytest tests/unit/test_validate_meta.py -v -k "find_all"
```

---

## Milestone 2: Unit-тести валідації H1

**Files:**
- Test: `tests/unit/test_audit_h1_primary.py`

### Task 2.1: Тест на виявлення mismatch

```python
def test_audit_finds_mismatch():
    # H1 = "Очиститель", primary = "очистители дисков"
    result = validate_h1("Очиститель", "очистители дисков", lang="ru")
    assert result["passed"] is False
```

### Task 2.2: Тест на plural форму

```python
def test_audit_accepts_plural():
    # H1 = "Очистители дисков", primary = "очиститель дисков"
    result = validate_h1("Очистители дисков", "очиститель дисков", lang="ru")
    assert result["passed"] is True
    assert result["form"] == "plural"
```

### Task 2.3: Тест на category_title

```python
def test_audit_handles_category_title():
    # category_title має пріоритет над primary_keyword
    # Потребує мок даних з category_title
    pass
```

### Task 2.4: Запустити тести

```bash
pytest tests/unit/test_audit_h1_primary.py -v
```

---

## Milestone 3: E2E тести

**Files:**
- Create: `tests/e2e/test_meta_validation.py`
- Create: `tests/e2e/conftest.py`

### Task 3.1: Створити conftest з маркером

```python
# tests/e2e/conftest.py
import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "e2e: end-to-end tests on real data")
```

### Task 3.2: E2E validate_meta RU

```python
@pytest.mark.e2e
def test_e2e_validate_all_ru_categories():
    result = subprocess.run(
        ["python3", "scripts/validate_meta.py", "--all", "--lang", "ru"],
        capture_output=True, text=True
    )
    assert "FAIL: 0" in result.stdout or result.returncode == 0
```

### Task 3.3: E2E validate_meta UK

```python
@pytest.mark.e2e
def test_e2e_validate_all_uk_categories():
    result = subprocess.run(
        ["python3", "scripts/validate_meta.py", "--all", "--lang", "uk"],
        capture_output=True, text=True
    )
    assert "FAIL: 0" in result.stdout or result.returncode == 0
```

### Task 3.4: E2E audit_h1 RU

```python
@pytest.mark.e2e
def test_e2e_audit_h1_ru():
    result = subprocess.run(
        ["python3", "scripts/audit_h1_primary.py", "--lang", "ru"],
        capture_output=True, text=True
    )
    assert "MISMATCH: 0" in result.stdout or result.returncode == 0
```

### Task 3.5: E2E audit_h1 UK

```python
@pytest.mark.e2e
def test_e2e_audit_h1_uk():
    result = subprocess.run(
        ["python3", "scripts/audit_h1_primary.py", "--lang", "uk"],
        capture_output=True, text=True
    )
    assert "MISMATCH: 0" in result.stdout or result.returncode == 0
```

### Task 3.6: Запустити E2E тести

```bash
pytest -m e2e -v
# Зафіксувати поточний стан (можуть бути FAIL)
```

---

## Milestone 4: Аудит скіллів generate-meta

**Files:**
- Audit: `.claude/skills/generate-meta/SKILL.md`
- Audit: `.claude/skills/uk-generate-meta/SKILL.md`

### Task 4.1: Checklist RU скілла

| Перевірка | Статус |
|-----------|--------|
| Title формула: `{title_phrase} — купить` | ? |
| H1 = title_phrase (без "Купить") | ? |
| Description: Producer vs Shop pattern | ? |
| Посилання на `validate_meta.py` | ? |
| category_title ?? primary_keyword логіка | ? |

### Task 4.2: Checklist UK скілла

| Перевірка | Статус |
|-----------|--------|
| Title формула: `{title_phrase} — купити` | ? |
| H1 = title_phrase (без "Купити") | ? |
| Description: Producer vs Shop pattern | ? |
| Посилання на `validate_meta.py` | ? |
| category_title ?? primary_keyword логіка | ? |

### Task 4.3: Виправити розбіжності

- Синхронізувати формули між RU та UK
- Оновити посилання на скрипти якщо потрібно

### Task 4.4: Оновити версії скіллів

- RU: v17.0
- UK: v17.0

---

## Milestone 5: Фікс мета-даних

### Task 5.1: Запустити E2E, отримати список FAIL

```bash
pytest -m e2e -v 2>&1 | tee /tmp/e2e_results.txt
```

### Task 5.2: Пофіксити мета-дані

Для кожної категорії з FAIL:
1. Прочитати `_clean.json` — визначити title_phrase
2. Прочитати `_meta.json` — знайти проблему
3. Виправити H1/Title/Description по скіллу
4. Валідувати: `python3 scripts/validate_meta.py <path>`

### Task 5.3: Фінальний E2E тест

```bash
pytest -m e2e -v
# Очікувано: всі PASS
```

### Task 5.4: Коміт

```bash
git add -A
git commit -m "fix(meta): validate and fix meta tags for RU/UK categories"
```

---

## Запуск тестів

```bash
# Unit тести (швидко)
pytest tests/unit/test_validate_meta.py tests/unit/test_audit_h1_primary.py -v

# E2E тести (реальні дані)
pytest -m e2e -v

# Всі тести
pytest -v
```

---

**Version:** 1.0 — February 2026
