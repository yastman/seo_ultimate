# Session Prompt: UK Skills Sync

Скопируй всё ниже и вставь в новую сессию Claude Code:

---

## Задача

Выполни план синхронизации UK скиллов с RU: `docs/plans/2026-01-26-uk-skills-sync.md`

## Контекст

- RU скиллы = эталон
- UK скиллы должны быть идентичны по структуре и логике
- Адаптация: пути `uk/categories/`, термины (гума, миття, скло), язык інтерфейсу → українська
- 17 задач, 17 файлов

## Инструкции

1. Прочитай план: `docs/plans/2026-01-26-uk-skills-sync.md`
2. Используй skill: `/superpowers:executing-plans`
3. Выполняй задачи последовательно (Task 1 → Task 17)
4. После каждой задачи — коммит
5. Чекпоинт после каждого batch (Tasks 1-6, 7-12, 13-15, 16)

## Таблица адаптации (держи под рукой)

| RU | UK |
|----|-----|
| `categories/{slug}/` | `uk/categories/{slug}/` |
| `{slug}_ru.md` | `{slug}_uk.md` |
| `/content-generator` | `/uk-content-generator` |
| `language_id=3` | `language_id=1` |
| резина | гума |
| мойка | миття |
| стекло | скло |
| чернитель | чорнитель |
| очиститель | очищувач |
| покрытие | покриття |
| поверхность | поверхня |
| защита | захист |

## Старт

```
/superpowers:executing-plans docs/plans/2026-01-26-uk-skills-sync.md
```

---
