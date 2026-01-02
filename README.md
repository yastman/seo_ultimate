# Ultimate.net.ua — SEO Content Pipeline

Автоматизированная система генерации SEO-контента для категорий интернет-магазина автохимии.

**Архитектура:** Skills-based Pipeline
**SSOT (контент):** `docs/CONTENT_GUIDE.md` v20.0
**Оркестратор:** `CLAUDE.md` v25.1
**Задачи:** `tasks/PIPELINE_STATUS.md`
**Язык:** RU + UK
**Version:** 8.0

---

## Pipeline

```
CSV → /category-init → /generate-meta → /seo-research → /content-generator → /quality-gate → /deploy-to-opencart
                                                                ↓
                                                    /uk-content-init (parallel)
```

---

## Quick Links 📂

| Раздел | Ссылка | Описание |
|--------|--------|----------|
| 📚 **Документация** | [`docs/`](docs/README.md) | Все гайды и инструкции |
| 📋 **Задачи** | [`tasks/`](tasks/README.md) | Статусы, пайплайн, чеклисты |
| 📦 **Категории** | [`categories/`](categories/README.md) | Данные категорий (RU) |
| 🛠️ **Скрипты** | [`scripts/`](scripts/README.md) | Утилиты автоматизации |
| 🇺🇦 **UK Версия** | [`uk/`](uk/README.md) | Локализация |
| 🧹 **Архив** | [`archive/`](archive/README.md) | Устаревшие файлы |
| 📊 **Отчеты** | [`reports/`](reports/README.md) | Логи авто-проверок |
| 🧪 **Тесты** | [`tests/`](tests/README.md) | Pytest Suite |
| 🏗️ **Артефакты** | [`artifacts/`](artifacts/README.md) | Временные файлы |
| 🤖 **Промпты** | [`prompts/`](prompts/README.md) | Шаблоны для AI агентов |
| 🚀 **Деплой** | [`deploy/`](deploy/README.md) | SQL скрипты |

---

## Быстрый старт

### Новая категория (полный цикл)

```bash
# 1. Инициализация из CSV
/category-init aktivnaya-pena

# 2. Мета-теги
/generate-meta aktivnaya-pena

# 3. Исследование
/seo-research aktivnaya-pena

# 4. Генерация контента
/content-generator aktivnaya-pena

# 5. Украинская версия (опционально)
/uk-content-init aktivnaya-pena

# 6. Проверка качества
/quality-gate aktivnaya-pena

# 7. Деплой
/deploy-to-opencart aktivnaya-pena
```

### Короткие команды

```
создай категорию aktivnaya-pena     → /category-init
сгенерируй мета                      → /generate-meta
исследуй категорию                   → /seo-research
напиши контент                       → /content-generator
створи UK версію                     → /uk-content-init
проверь перед деплоем               → /quality-gate
залей на сайт                        → /deploy-to-opencart
```

---

## Skills

| Skill | Версия | Input | Output |
|-------|--------|-------|--------|
| `/category-init` | 1.0 | slug из CSV | folders + _clean.json |
| `/generate-meta` | 8.0 | _clean.json | _meta.json |
| `/seo-research` | 1.0 | _meta.json | RESEARCH_DATA.md |
| `/content-generator` | 1.0 | research + meta | _ru.md |
| `/batch-content` | 1.0 | multiple slugs | batch processing |
| `/uk-content-init` | 4.0 | RU complete | uk/ structure |
| `/quality-gate` | 1.0 | all files | PASS/FAIL report |
| `/deploy-to-opencart` | 3.0 | quality PASS | DB updated |

---

## Структура проекта

```
/
├── CLAUDE.md                 # Оркестратор (v25.1)
├── README.md                 # Этот файл
│
├── docs/                     # Документация + README.md
│   ├── CONTENT_GUIDE.md      # SEO Guide v20.0
│   └── RESEARCH_GUIDE.md     # Гайд по исследованиям
│
├── tasks/                    # Система задач + README.md
│   ├── PIPELINE_STATUS.md    # Текущий прогресс
│   ├── MASTER_CHECKLIST.md   # Все категории
│   ├── categories/           # Чеклисты (58 файлов)
│   └── stages/               # Описание этапов
│
├── categories/               # Данные категорий + README.md
│   └── {slug}/               # Папка категории
│       ├── data/{slug}_clean.json
│       ├── meta/{slug}_meta.json
│       ├── content/{slug}_ru.md
│       └── research/RESEARCH_DATA.md
│
├── uk/                       # UK локализация + README.md
│   └── categories/{slug}/
│
├── scripts/                  # Скрипты (60+) + README.md
├── tests/                    # Тесты + README.md
├── archive/                  # Архив + README.md
├── data/                     # Input/Output data + README.md
├── reports/                  # Отчеты и логи + README.md
├── prompts/                  # Промпты для агентов + README.md
│
└── deploy/                   # SQL для OpenCart + README.md
```

---

## Validation

Каждый skill имеет input/output валидацию:

| Skill | Input Check | Output Check | Script |
|-------|-------------|--------------|--------|
| category-init | slug в CSV | JSON valid | — |
| generate-meta | _clean.json | Title/Desc length | validate_meta.py |
| seo-research | meta exists | 8 blocks | — |
| content-generator | research | structure | validate_content.py |
| uk-content-init | RU complete | translation | validate_meta.py |
| quality-gate | all files | all checks | analyze_category.py |
| deploy-to-opencart | PASS | DB updated | — |

---

## December 2025 Rules

| Parameter | Value |
|-----------|-------|
| Title | **50-60 chars**, "Купить/Купити" REQUIRED |
| Description | **120-160 chars**, NO emojis |
| H1 | **NO "Купить"**, H1 ≠ Title |
| Intro | **30-60 words** |
| Keyword density | **NOT a factor** — write naturally |
| FAQ | **3-5 questions**, real user queries |

---

## Категории

**Total:** 58 категорий (RU + UK = 116 страниц)

| Статус | Количество | Описание |
|--------|------------|----------|
| ✅ Готово к Deploy | 13 | Полный цикл завершён |
| 🔄 Meta готово | 21 | Нужен Research + Content |
| ⬜ Init готово | 24 | Нужен Meta |

**Детали:** `tasks/PIPELINE_STATUS.md`

---

## Scripts

| Script | Назначение |
|--------|------------|
| `analyze_category.py` | Анализ категории |
| `validate_content.py` | Валидация контента |
| `validate_meta.py` | Валидация мета-тегов |
| `md_to_html.py` | Конвертация MD → HTML |
| `upload_to_db.py` | Upload в OpenCart |

---

## Changelog

### v8.0 (2025-12-31)
- Task system: PIPELINE_STATUS, MASTER_CHECKLIST, MAINTENANCE
- 58 категорий (13 готовы к deploy)
- 8 skills (добавлен batch-content)
- scripts/README.md, deploy/README.md
- validate_uk.py

### v7.0 (2025-12-30)
- Skills-based pipeline architecture
- 7 specialized skills with validation
- Cloned Anthropic skills examples
- CLAUDE.md v22.0 with full routing
- Input/output validation at each step

### v6.1 (2025-12-16)
- SSOT: CONTENT_GUIDE.md v4.4
- Two-mode validation (quality/seo)

### v6.0 (2025-12-15)
- v8.5 SEO Standard
- 4 basic skills

---

**Updated:** 2025-12-31
**Version:** 8.0
