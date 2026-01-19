# Tasks

**Обновлено:** 2026-01-19

---

## Текущий этап: Research → Content

```
/seo-research → Perplexity → /content-generator → /quality-gate → /deploy
```

---

## Файлы

| Файл | Назначение |
|------|------------|
| **[`CONTENT_STATUS.md`](CONTENT_STATUS.md)** | Статус research/content по всем категориям |
| [`active/README.md`](active/README.md) | Очереди на обработку |

---

## Статус (2026-01-19)

| Метрика | Значение |
|---------|----------|
| Research готов (>2KB) | ~20 категорий |
| Research заглушка (<2KB) | ~27 категорий |
| Content готов (>1KB) | ~31 файлов |
| Content нужен | ~23 категории |

---

## Workflow

1. Смотри **`CONTENT_STATUS.md`** — что нужно сделать
2. Research: `/seo-research {slug}` → Perplexity Deep Research → сохрани `RESEARCH_DATA.md`
3. Content: `/content-generator {slug}`
4. Проверка: `/quality-gate {slug}`
5. Деплой: `/deploy-to-opencart {slug}`
