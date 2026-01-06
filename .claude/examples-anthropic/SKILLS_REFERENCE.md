# Anthropic Skills Reference

Официальные примеры скиллов от Anthropic для изучения паттернов и best practices.

**Источник:** <https://github.com/anthropics/skills>

---

## Структура репозитория

```
examples-anthropic/
├── skills/           # Примеры скиллов
├── spec/             # Спецификация Agent Skills
├── template/         # Шаблон для создания скилла
└── SKILLS_REFERENCE.md  # Этот файл
```

---

## Каталог скиллов

### Документы (Document Skills)

| Скилл | Описание | Файлы |
|-------|----------|-------|
| **docx** | Создание, редактирование Word документов | SKILL.md, docx-js.md, ooxml.md |
| **pdf** | Работа с PDF: извлечение, создание, формы | SKILL.md, forms.md, reference.md |
| **pptx** | Создание PowerPoint презентаций | SKILL.md, html2pptx.md, ooxml.md |
| **xlsx** | Работа с Excel файлами | SKILL.md |

### Разработка (Development & Technical)

| Скилл | Описание | Файлы |
|-------|----------|-------|
| **mcp-builder** | Создание MCP серверов | SKILL.md + reference/*.md |
| **webapp-testing** | Тестирование веб-приложений | SKILL.md |
| **skill-creator** | Создание новых скиллов | SKILL.md + references/*.md |
| **web-artifacts-builder** | Создание веб-артефактов | SKILL.md |

### Дизайн (Creative & Design)

| Скилл | Описание | Файлы |
|-------|----------|-------|
| **algorithmic-art** | Генеративное искусство | SKILL.md |
| **canvas-design** | Дизайн на Canvas | SKILL.md |
| **frontend-design** | Frontend дизайн | SKILL.md |
| **theme-factory** | Создание тем оформления | SKILL.md + themes/*.md |
| **slack-gif-creator** | Создание GIF для Slack | SKILL.md |

### Бизнес (Enterprise & Communication)

| Скилл | Описание | Файлы |
|-------|----------|-------|
| **brand-guidelines** | Брендбук и гайдлайны | SKILL.md |
| **internal-comms** | Внутренние коммуникации | SKILL.md + examples/*.md |
| **doc-coauthoring** | Совместное редактирование документов | SKILL.md |

---

## Ключевые паттерны

### 1. Progressive Disclosure

```
skill/
├── SKILL.md           # Основное (≤500 строк)
├── reference.md       # Детали (загружается по необходимости)
└── examples.md        # Примеры (загружается по необходимости)
```

### 2. Domain Organization

```
bigquery-skill/
├── SKILL.md
└── reference/
    ├── finance.md     # Загружается для финансовых запросов
    ├── sales.md       # Загружается для sales запросов
    └── product.md     # Загружается для product запросов
```

### 3. Frontmatter

```yaml
---
name: skill-name
description: Что делает И когда использовать. Включить триггеры.
---
```

---

## Best Practices (из skill-creator)

### Concise is Key

- Claude уже умный — добавляй только то, чего он не знает
- Каждый параграф должен оправдывать свои токены
- Примеры лучше объяснений

### Degrees of Freedom

| Уровень | Когда использовать |
|---------|-------------------|
| High (текст) | Много валидных подходов |
| Medium (псевдокод) | Есть предпочтительный паттерн |
| Low (конкретный скрипт) | Критичная последовательность |

### Description — это триггер

- Включать ЧТО делает И КОГДА использовать
- Конкретные триггеры: "Use when...", "применять когда..."
- НЕ писать "When to use" в body — оно загружается ПОСЛЕ триггера

### Не создавать лишние файлы

- НЕ нужны: README.md, CHANGELOG.md, INSTALLATION.md
- Только: SKILL.md + references/ + scripts/ + assets/

---

## Применение для SEO Pipeline

### Что взять из примеров

1. **skill-creator** — паттерны создания скиллов
2. **pdf** — progressive disclosure (SKILL.md → forms.md → reference.md)
3. **mcp-builder** — фазовый workflow (Research → Implementation → Test → Evaluate)
4. **internal-comms** — domain-specific examples

### Структура для наших скиллов

```
.claude/skills/
├── category-init/
│   └── SKILL.md
├── generate-meta/
│   ├── SKILL.md
│   └── REFERENCE.md        # ← уже есть
├── seo-research/
│   ├── SKILL.md
│   └── RESEARCH_MATRIX.md  # По типам товаров
├── content-generator/
│   ├── SKILL.md
│   └── STRUCTURE.md        # Шаблоны структуры
├── uk-content-init/
│   ├── SKILL.md
│   └── TRANSLATION_RULES.md # ← уже есть
├── quality-gate/
│   └── SKILL.md
└── deploy-to-opencart/
    ├── SKILL.md
    └── DB_SCHEMA.md        # Вынести из SKILL.md
```

---

## Полезные ссылки

- [Agent Skills Spec](https://agentskills.io/specification)
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Creating custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)

---

**Обновлено:** December 2025
