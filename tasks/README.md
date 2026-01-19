# Task Management

**Обновлено:** 2026-01-19

---

## Текущий этап: Research → Content

```
/seo-research → Perplexity → /content-generator → /quality-gate → /deploy
```

---

## Ключевые файлы

| Файл | Назначение |
|------|------------|
| **[`CONTENT_STATUS.md`](CONTENT_STATUS.md)** | Статус research/content по категориям |
| **[`active/README.md`](active/README.md)** | Текущие задачи и очереди |
| [`MASTER_CHECKLIST.md`](MASTER_CHECKLIST.md) | Полный список категорий (устаревает) |

---

## Структура

```
tasks/
├── CONTENT_STATUS.md   # Актуальный статус категорий
├── active/             # Текущие задачи и справочники
├── completed/          # Архив выполненных ТЗ
├── reference/          # Справочные документы
├── categories/         # Чеклисты по категориям (legacy)
├── stages/             # Описание этапов (SOP)
└── reports/            # Отчёты
```

---

## Статус (2026-01-19)

| Метрика | Значение |
|---------|----------|
| Research готов | ~20 категорий |
| Research заглушка | ~27 категорий |
| Content готов | ~31 файлов |
| Content нужен | ~23 категории |

---

## Workflow

1. Открой `CONTENT_STATUS.md` — смотри что нужно
2. Для research: `/seo-research {slug}` → Perplexity → сохрани в `RESEARCH_DATA.md`
3. Для content: `/content-generator {slug}`
4. Проверка: `/quality-gate {slug}`
5. Деплой: `/deploy-to-opencart {slug}`
