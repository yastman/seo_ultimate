# Session Prompt: UK Pipeline Implementation

## Для новой сессии Claude Code

Скопируй и вставь в новую сессию:

---

```
/superpowers:executing-plans docs/plans/2026-01-22-uk-pipeline-implementation.md

Контекст: Создаём полный UK pipeline для Ultimate.net.ua — скиллы и субагенты для украинских категорий. UK pipeline должен зеркалить RU pipeline.

Используй:
- skill-creator для создания скиллов (Tasks 2-5)
- subagent-creator для создания субагентов (Tasks 6-9)

Начни с Task 1 (удаление uk-content-adapter).
```

---

## Альтернатива: Ручной запуск

Если executing-plans недоступен:

```
Выполни план из docs/plans/2026-01-22-uk-pipeline-implementation.md

Порядок:
1. Task 1: rm -rf .claude/skills/uk-content-adapter/ && rm .claude/agents/uk-content-adapter.md
2. Tasks 2-5: /skill-creator для каждого UK скилла
3. Tasks 6-9: /subagent-creator для каждого UK агента
4. Task 10: Синхронизировать uk-generate-meta
5. Task 11: Обновить CLAUDE.md
6. Task 12: Финальная проверка

Коммить после каждого таска.
```
