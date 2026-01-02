# Test Suite

**[← Назад в корень](../README.md)**

Здесь находятся автоматические тесты для проверки скриптов пайплайна.
Используется pytest.

## Структура

* `test_*.py`: Файлы с тестами. Имя файла обычно соответствует тестируемому скрипту.
  * Пример: `test_validate_content.py` тестирует `scripts/validate_content.py`.
* `conftest.py`: Общие фикстуры (fixtures) для тестов.
* `fixtures/`: Тестовые данные (образцы файлов).

## Запуск тестов

1. **Запуск всех тестов:**

    ```bash
    python -m pytest
    ```

2. **Запуск конкретного теста:**

    ```bash
    python -m pytest tests/test_validate_content.py
    ```

3. **Запуск с подробным выводом:**

    ```bash
    python -m pytest -v
    ```
