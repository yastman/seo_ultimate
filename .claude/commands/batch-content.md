# Batch Content Generation

Обработай все pending категории из списка:

## Workflow для каждой категории

1. **Анализ:** `python3 scripts/analyze_category.py {slug} --json`
2. **Генерация:** Создай контент по seo-content skill
3. **Сохранение:** `categories/{slug}/content/{slug}_ru.md`
4. **Валидация:** `python3 scripts/validate_content.py <file> "<keyword>"`
5. **Исправление:** Если FAIL — исправь и повтори валидацию
6. **Meta:** Создай `categories/{slug}/meta/{slug}_meta.json`

## Категории для обработки

```bash
python3 scripts/batch_generate.py --list
```

Обрабатывай по одной, показывая прогресс:

- [1/9] aktivnaya-pena → DONE
- [2/9] cherniteli-shin → IN PROGRESS
- ...

## После каждой категории

Запусти валидацию и покажи результат (PASS/WARN/FAIL).
Если FAIL — исправь автоматически до 3 попыток.
