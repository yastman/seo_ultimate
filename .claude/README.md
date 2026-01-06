# `.claude/` — Skills & Configuration

**Архитектура:** Hybrid (Scripts + Claude Code CLI)
**SEO Standard:** v8.5 (Google 2025)
**Updated:** 2025-12-15

**Navigation:** [`../README.md`](../README.md) | [`../CLAUDE.md`](../CLAUDE.md)

---

## Структура

```
.claude/
├── README.md                 # Этот файл
│
├── skills/                   # 4 Skills
│   ├── seo-init/            # Инициализация категории
│   ├── seo-clean/           # Кластеризация keywords
│   ├── seo-validate/        # Валидация контента
│   └── seo-meta/            # Генерация meta tags
│
└── agents_archive/          # Архив старых агентов (deprecated)
```

---

## Skills (4 штуки)

| Skill            | Триггер           | Что делает                       | Версия |
| ---------------- | ----------------- | -------------------------------- | ------ |
| **seo-init**     | `init {slug}`     | Создаёт папки + анализ категории | v2.1   |
| **seo-clean**    | `clean {slug}`    | Кластеризация keywords (52 → 12) | v2.1   |
| **seo-validate** | `проверь {slug}`  | Валидация контента (two modes)   | v7.0   |
| **seo-meta**     | `meta для {slug}` | Генерация Title/Description      | v3.0   |

**Остальные задачи** Opus выполняет напрямую:

- Data extraction → `parse_semantics_to_json.py`
- Research → Perplexity MCP
- Content generation → LLM напрямую (инструкции в CLAUDE.md)
- Packaging → по запросу

---

## Как работают Skills

```
┌─────────────────────────────────────────┐
│  Команда: "контент для aktivnaya-pena"  │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Orchestrator (Opus 4.5)                │
│                                         │
│  1. analyze_category.py → контекст      │
│  2. Генерация контента (LLM)            │
│  3. validate_content.py → проверка      │
│  4. Fix если нужно                      │
│  5. Повторить до PASS                   │
└─────────────────────────────────────────┘
```

**Принцип:** Скрипты = инструменты, Opus = мозг + руки

---

## Two-Mode Validation (v8.5)

```
validate_content.py
├── --mode quality (DEFAULT) — полная проверка, ловит LLM-деградацию
└── --mode seo              — минимум для публикации
```

### --mode quality (DEFAULT)

| Check            | Статус  | Назначение |
| ---------------- | ------- | ---------- |
| H1 + keyword     | BLOCKER | SEO        |
| Primary в intro  | BLOCKER | SEO        |
| Structure (H2)   | BLOCKER | SEO        |
| Coverage core    | WARNING | QA         |
| Water/Nausea     | WARNING | QA         |
| Strict blacklist | BLOCKER | Антиспам   |

### --mode seo (минимум)

| Check            | Статус  | Назначение |
| ---------------- | ------- | ---------- |
| H1 + keyword     | BLOCKER | SEO        |
| Primary в intro  | BLOCKER | SEO        |
| Strict blacklist | BLOCKER | Антиспам   |

---

## Coverage Split (v8.5)

| Тип keywords     | Где использовать                | Валидация |
| ---------------- | ------------------------------- | --------- |
| **Core (topic)** | В тексте контента               | WARNING   |
| **Commercial**   | В meta tags (Title/Description) | INFO only |

**Commercial modifiers:** купить, цена, заказать, в наличии, доставка, недорого

---

## Связанные файлы

| Файл                                               | Назначение                          |
| -------------------------------------------------- | ----------------------------------- |
| [`/CLAUDE.md`](../CLAUDE.md)                       | Главные инструкции для Orchestrator |
| [`/README.md`](../README.md)                       | Документация проекта                |
| [`/scripts/README.md`](../scripts/README.md)       | Документация Python скриптов        |
| [`/categories/README.md`](../categories/README.md) | Документация структуры категорий    |
| [`/master_plan.md`](../master_plan.md)             | План и статус проекта               |

---

## Архив

Папка `agents_archive/` содержит старые агенты из предыдущей архитектуры.

**Не использовать** — оставлены для справки.

---

**Version:** 6.0 (4 Skills + Hybrid Architecture)
**Updated:** 2025-12-15
**SEO Standard:** v8.5 (Google 2025 — People-first Content)
