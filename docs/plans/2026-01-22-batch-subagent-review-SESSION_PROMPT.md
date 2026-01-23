# Session Prompt: Batch Content Review

Скопируй и вставь в новую сессию Claude Code:

---

```
Выполни план из docs/plans/2026-01-22-batch-subagent-content-review.md

Используй superpowers:executing-plans для пошагового выполнения.

Задача: проверить и автоматически исправить все 50 русских категорий через субагента content-reviewer.

Для каждой категории:
1. Запусти Task(subagent_type="content-reviewer", prompt="Review and auto-fix: {path}")
2. Дождись результата
3. Выведи краткий verdict (PASS/WARNING/FIXED)
4. Переходи к следующей

Батчи:
- Batch 1: aksessuary (10 шт)
- Batch 2: moyka-i-eksterer (18 шт)
- Batch 3: oborudovanie + polirovka (7 шт)
- Batch 4: ukhod-za-intererom (8 шт)
- Batch 5: zashchitnye-pokrytiya (7 шт)

После каждого батча — пауза для review.
После всех батчей — сводный отчёт и git commit.

НЕ коммить автоматически — только Edit файлы. Коммит в конце вручную.
```

---

## Альтернатива: параллельный запуск батча

Если хочешь быстрее — запускай 5-10 субагентов параллельно:

```
Выполни план из docs/plans/2026-01-22-batch-subagent-content-review.md

Запускай субагентов параллельно по 5 штук (run_in_background=true).
После завершения батча — собери результаты и выведи сводку.

Начни с Batch 1 (aksessuary, 10 категорий).
```
