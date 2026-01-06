# TASKS — SEO Content Pipeline

> **Структурированная система задач в папке `tasks/`**

---

## Главные файлы

| Файл | Описание |
|------|----------|
| **[tasks/PIPELINE_STATUS.md](tasks/PIPELINE_STATUS.md)** | Общий прогресс, текущая очередь |
| **[tasks/MASTER_CHECKLIST.md](tasks/MASTER_CHECKLIST.md)** | Все 58 категорий в одной таблице |

---

## Индивидуальные чеклисты

Каждая категория имеет свой файл с подзадачами:

```
tasks/categories/{slug}.md
```

**Пример:** [tasks/categories/tverdyy-vosk.md](tasks/categories/tverdyy-vosk.md)

---

## Этапы пайплайна

| Stage | Skill | Описание | Чеклист |
|-------|-------|----------|---------|
| 01 | /category-init | Создание папок, кластеризация | [_stage.md](tasks/stages/01-init/_stage.md) |
| 02 | /generate-meta | Title, description, h1 | [_stage.md](tasks/stages/02-meta/_stage.md) |
| 03 | /seo-research | Исследование (8 блоков) | [_stage.md](tasks/stages/03-research/_stage.md) |
| 04 | /content-generator | SEO-контент (1500-2500 слов) | [_stage.md](tasks/stages/04-content/_stage.md) |
| 05 | /uk-content-init | Украинская версия | [_stage.md](tasks/stages/05-uk/_stage.md) |
| 06 | /quality-gate | Финальная проверка | [_stage.md](tasks/stages/06-quality/_stage.md) |
| 07 | /deploy-to-opencart | Заливка в БД | [_stage.md](tasks/stages/07-deploy/_stage.md) |

---

## Текущий статус

| Metric | Value |
|--------|-------|
| Total categories | 58 |
| RU + UK pages | 116 |
| Ready for deploy | 13 |
| Need meta | 24 |
| Need research | 45 |
| Not created | 7 |

---

## Следующие действия

1. **Создать 7 новых категорий** → `/category-init`
2. **Meta для 24 категорий** → `/generate-meta`
3. **Research для 45 категорий** → `/seo-research`
4. **Content для 45 категорий** → `/content-generator`

---

## Workflow

```
1. Открыть tasks/PIPELINE_STATUS.md
2. Найти текущую очередь
3. Открыть tasks/categories/{slug}.md
4. Работать по чеклисту
5. Отмечать выполненное
6. Запускать валидацию
7. Обновлять статусы
```

---

## Исправления

- [tasks/fixes/duplicates.md](tasks/fixes/duplicates.md) — дубли ключей

---

**Version:** 11.0
**Last Updated:** 2025-12-31
