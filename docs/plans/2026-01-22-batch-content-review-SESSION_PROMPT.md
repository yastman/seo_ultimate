# Session Prompt: Batch Content Review

Скопируй этот промпт в новую сессию Claude Code:

---

```
Выполни план из docs/plans/2026-01-22-batch-content-review.md

Используй скилл superpowers:executing-plans.

Для каждой категории из списка (50 шт):
1. Вызови скилл: Skill(skill="content-reviewer", args="{path}")
2. Скилл выполнит полный workflow (10 шагов)
3. Покажи мне отчёт
4. Дождись моего "ок"
5. Перейди к следующей

Начни с категории #1: aksessuary

ВАЖНО:
- Использовать Skill(), не Task()
- Academic <7% — только INFO, не фиксить
- BLOCKER фиксить обязательно: H1≠name, stem>3%, nausea>4, how-to sections
- Не коммитить автоматически
```

---

## Альтернатива: непрерывный режим

```
Выполни план из docs/plans/2026-01-22-batch-content-review.md

Для каждой категории:
1. Skill(skill="content-reviewer", args="{path}")
2. Краткий отчёт (verdict + fixes)
3. Сразу следующая без ожидания

Режим: непрерывный, без остановок на "ок".
Останавливайся только если REWRITE NEEDED.

Начни с #1 aksessuary, закончи #50 zhidkiy-vosk.
```
