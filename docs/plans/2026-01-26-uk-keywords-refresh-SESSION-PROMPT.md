# Session Prompt: UK Keywords Refresh

Скопируй этот промпт в новую сессию Claude Code:

---

```
Выполни план из docs/plans/2026-01-26-uk-keywords-refresh.md

Используй superpowers:executing-plans skill.

Контекст:
- 355 UK ключей уже импортированы в uk/data/uk_keywords.json
- 42 категории получили ключи
- 40 категорий имеют контент (нужна перевалидация)
- 2 категории без контента (ochistiteli-kuzova, polirovalnye-mashinki)

Порядок выполнения:
1. Task 1: Создать и запустить скрипт update_uk_clean_json.py
2. Task 2: Batch генерация мета через uk-generate-meta агент (42 категории)
3. Task 3: Генерация контента для 2 категорий через uk-content-generator
4. Task 4: Перевалидация контента через uk-content-reviewer (40 категорий)
5. Task 5: Quality-gate для всех 42 категорий

Работай batch'ами по 5-10 категорий. После каждого batch — commit.

Начни с Task 1.
```

---

**Как запустить:**
1. Открой новый терминал в той же директории
2. Запусти `claude`
3. Вставь промпт выше
