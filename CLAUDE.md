# CLAUDE.md — SEO Content Pipeline

Ultimate.net.ua — интернет-магазин автохимии и детейлинга.
**Язык ответов:** русский

---

## Pipeline

```
CSV → /category-init → /generate-meta → /seo-research → /content-generator → /uk-content-init → /quality-gate → /deploy
```

---

## 🛠 Система задач

**Главный файл:** `tasks/PIPELINE_STATUS.md`

### Структура `tasks/`

```
tasks/
├── active/                 # Активные ТЗ
├── completed/              # Выполненные задачи
├── reference/              # Справочные материалы
├── categories/{slug}.md    # Чеклисты по категориям
└── stages/                 # Описание этапов
```

### Правила работы

1. **Перед работой** → читать `tasks/PIPELINE_STATUS.md`
2. **Работать** → по чеклисту `tasks/categories/{slug}.md`
3. **Отмечать** → `[x]` выполненные, статус ⬜ → ✅
4. **Обновлять** → счётчики в PIPELINE_STATUS
5. **Валидировать** → после каждого этапа

---

## 📁 Структура проекта

```
categories/{slug}/          # Данные категории (RU)
├── data/{slug}_clean.json    # Ключи
├── meta/{slug}_meta.json     # Мета-теги
├── content/{slug}_ru.md      # Контент
└── research/RESEARCH_DATA.md # Исследование

uk/categories/{slug}/       # Локализация (UK)

data/                       # Центральное хранилище
├── raw/                      # Исходные данные
├── generated/                # Авто-генерация
├── dumps/                    # SQL дампы
└── sql_output/               # Готовые скрипты
```

---

## ⚡ Скиллы (Slash Commands)

| Триггер           | Скилл                        |
| ----------------- | ---------------------------- |
| Новая категория   | `/category-init {slug}`      |
| Мета-теги         | `/generate-meta {slug}`      |
| Исследование      | `/seo-research {slug}`       |
| Контент           | `/content-generator {slug}`  |
| Украинская версия | `/uk-content-init {slug}`    |
| Проверка          | `/quality-gate {slug}`       |
| Деплой            | `/deploy-to-opencart {slug}` |

---

## 🔍 Инструменты (Scripts)

```bash
# Meta Validation
python scripts/validate_meta.py categories/{slug}/meta/{slug}_meta.json

# Content Validation
python scripts/validate_content.py categories/{slug}/content/{slug}_ru.md "{keyword}" --mode seo

# HTML Preview
python scripts/md_to_html.py categories/{slug}/content/{slug}_ru.md
```

---

## Git

**После любых изменений файлов — делать коммит.**

```bash
git add <files>
git commit -m "feat/fix/docs: краткое описание"
```

---

**Version:** 27.0
