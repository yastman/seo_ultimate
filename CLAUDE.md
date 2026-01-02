# CLAUDE.md — SEO Content Pipeline

Ultimate.net.ua — интернет-магазин автохимии и детейлинга.
**Язык ответов:** русский

---

## Pipeline

```
CSV → /category-init → /generate-meta → /seo-research → /content-generator → /uk-content-init → /quality-gate → /deploy
```

---

## Система задач

**Главный файл:** `tasks/PIPELINE_STATUS.md`

### Структура

```
tasks/
├── PIPELINE_STATUS.md      # Прогресс + текущая очередь
├── MASTER_CHECKLIST.md     # Все категории со статусами
├── categories/{slug}.md    # Чеклист категории
└── stages/0X-*/_stage.md   # Описание этапов
```

### Правила работы

1. **Перед работой** → читать `tasks/PIPELINE_STATUS.md`
2. **Работать** → по чеклисту `tasks/categories/{slug}.md`
3. **Отмечать** → `[x]` выполненные, статус ⬜ → ✅
4. **Обновлять** → счётчики в PIPELINE_STATUS и MASTER_CHECKLIST
5. **Валидировать** → после каждого этапа

---

## Структура категории

```
categories/{slug}/
├── data/{slug}_clean.json    # Ключи
├── meta/{slug}_meta.json     # Мета-теги
├── content/{slug}_ru.md      # Контент
└── research/RESEARCH_DATA.md # Исследование
```

UK версия: `uk/categories/{slug}/`

---

## Скиллы

| Триггер | Скилл |
|---------|-------|
| Новая категория | `/category-init {slug}` |
| Мета-теги | `/generate-meta {slug}` |
| Исследование | `/seo-research {slug}` |
| Контент | `/content-generator {slug}` |
| Batch контент | `/batch-content` |
| Украинская версия | `/uk-content-init {slug}` |
| Проверка | `/quality-gate {slug}` |
| Деплой | `/deploy-to-opencart {slug}` |

---

## Источники данных

| Файл | Расположение | Описание |
|------|--------------|----------|
| Структура категорий | `data/list_mode_export.csv` | CSV со всеми категориями |
| Товары | `categories/{slug}/products_with_descriptions.md` | Товары категории |
| Стоп-слова | `data/stopwords/` | Фильтры для ключей |
| Мета все | `data/all_meta.json` | Все мета-теги |

---

## Валидация

```bash
# Meta
python3 scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json

# Content
python3 scripts/validate_content.py categories/{slug}/content/{slug}_ru.md "{keyword}" --mode seo
```

Exit codes: 0=PASS, 1=WARNING, 2=FAIL

---

## Документация

| Файл | Описание |
|------|----------|
| `tasks/PIPELINE_STATUS.md` | **Текущий прогресс** |
| `tasks/MASTER_CHECKLIST.md` | Все категории |
| `tasks/MAINTENANCE.md` | Поддержка системы задач |
| `docs/CONTENT_GUIDE.md` | SEO Guide |

---

**Version:** 25.1
