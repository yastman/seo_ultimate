# W2-3: Миграция validate_content.py на text_utils

**Task:** Task 7 из docs/plans/2026-01-29-scripts-refactoring-plan.md
**Worker:** W2-3
**Date:** 2026-01-29

---

## Выполненные действия

### 1. Проверка baseline (Step 1)

```bash
pytest tests/unit/test_validate_content.py -v
# Result: 17 tests PASSED
```

### 2. Обновление импортов (Step 2)

**Изменения в scripts/validate_content.py:**

#### 2.1 Добавлен project root в sys.path
```python
# Add scripts and project root to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(PROJECT_ROOT))
```

#### 2.2 Обновлены импорты text_utils
```python
# SSOT: Use core functions from text_utils
try:
    from scripts.text_utils import (
        clean_markdown,
        count_chars_no_spaces,
        count_words,
        extract_h1,
        extract_h2s,
        extract_intro,
    )
except ImportError:
    from text_utils import (  # type: ignore
        clean_markdown,
        count_chars_no_spaces,
        count_words,
        extract_h1,
        extract_h2s,
        extract_intro,
    )
```

#### 2.3 Выделен импорт get_adaptive_requirements из seo_utils
```python
# SSOT: get_adaptive_requirements from seo_utils
try:
    from scripts.seo_utils import get_adaptive_requirements
except ImportError:
    from seo_utils import get_adaptive_requirements  # type: ignore
```

### 3. Удаление локальных реализаций (Step 3)

Удалены локальные функции (старые строки 127-156):
- `extract_h1(text: str) -> str | None`
- `extract_h2s(text: str) -> list[str]`
- `extract_intro(text: str) -> str`

Заменены на импорт из `text_utils.py`.

### 4. Верификация (Step 4)

```bash
pytest tests/unit/test_validate_content.py -v --no-cov
# Result: 17 passed in 2.02s

python3 scripts/validate_content.py "categories/moyka-i-eksterer/avtoshampuni/aktivnaya-pena/content/aktivnaya-pena_ru.md" "активная пена" --mode seo
# Result: PASS - CLI работает корректно
```

---

## Результаты

| Метрика | До | После |
|---------|-----|-------|
| Тесты | 17 passed | 17 passed |
| LOC удалено | 0 | ~30 строк |
| Импорты из text_utils | 0 | 6 функций |

### Функции теперь импортируются из text_utils:
- `clean_markdown`
- `count_chars_no_spaces`
- `count_words`
- `extract_h1`
- `extract_h2s`
- `extract_intro`

### Функции остаются в seo_utils:
- `get_adaptive_requirements` (специфичная для SEO логика)

---

## Статус

**DONE** - Task 7 выполнена успешно.

Миграция validate_content.py на text_utils SSOT завершена:
- Импорты обновлены
- Локальные дубликаты удалены
- Все 17 тестов проходят
- CLI работает корректно
