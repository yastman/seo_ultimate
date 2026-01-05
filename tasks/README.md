# Task Management

**[← Назад в корень](../README.md)**

Система управления задачами проекта.

## Основные файлы

- [`PIPELINE_STATUS.md`](PIPELINE_STATUS.md): **Главный дашборд**. Текущий статус всех категорий и очередь задач.
- [`ROADMAP.md`](ROADMAP.md): Глобальный план по этапам работ.
- [`STRUCTURE_CHANGES_PLAN.md`](STRUCTURE_CHANGES_PLAN.md): Актуальный план изменений структуры (L3, Merge, Relocate).
- [`IDEAL_STRUCTURE_TARGET.md`](IDEAL_STRUCTURE_TARGET.md): Эталон целевой структуры для валидации.
- [`MASTER_CHECKLIST.md`](MASTER_CHECKLIST.md): Полный список всех категорий со статусами.
- [`MAINTENANCE.md`](MAINTENANCE.md): Инструкции по поддержке системы задач.

## Папки

- `categories/`: Индивидуальные чеклисты для каждой категории.
- `stages/`: Описание этапов работы (SOP).
- `fixes/`: Актуальные задачи на исправление ошибок.
- `archive/`: Устаревшие ТЗ и выполненные задачи.

## Workflow

1. Открыть `PIPELINE_STATUS.md`, выбрать категорию.
2. Открыть чеклист категории в `tasks/categories/{slug}.md`.
3. Выполнять пункты, отмечать `[x]`.
4. Обновлять статус в `PIPELINE_STATUS.md` по завершению этапов.
