# Prompts — Sub-agent Templates

**[← Назад в корень](../README.md)**


**Sub-agents Architecture v5.0**

Prompt templates для 3-этапного workflow.

---

## Структура

| Файл | Этап | Sub-agent | Модель | Описание |
|------|------|-----------|--------|----------|
| **[prepare.md](prepare.md)** | PREPARE | `general-purpose` | haiku | Init + Data + URLs |
| **[produce.md](produce.md)** | PRODUCE | `seo-content-writer` | sonnet | Content RU + Meta |
| **[deliver.md](deliver.md)** | DELIVER | `seo-content-auditor` | sonnet | Validate + Package |

---

## Workflow

```
Orchestrator
    ↓
    ├─→ PREPARE (haiku) ────→ Folders + JSON
    │
    ├─→ PRODUCE (sonnet) ───→ Content + Meta
    │
    └─→ DELIVER (sonnet) ───→ Validation + Deliverables
```

---

## Использование

### Из Orchestrator (CLAUDE.md)

```python
# Команда: "полный dlya-ruchnoy-moyki tier A"

Task(
  subagent_type="general-purpose",
  model="haiku",
  prompt=read("prompts/prepare.md").format(slug="dlya-ruchnoy-moyki", tier="A")
)

Task(
  subagent_type="seo-content-writer",
  model="sonnet",
  prompt=read("prompts/produce.md").format(slug="dlya-ruchnoy-moyki", tier="A")
)

Task(
  subagent_type="seo-content-auditor",
  model="sonnet",
  prompt=read("prompts/deliver.md").format(slug="dlya-ruchnoy-moyki", tier="A")
)
```

---

## Спецификация

Все промпты следуют **SEO_MASTER.md v7.3**:

- Tier Targets (Chars, H2, FAQ, Density, Water, Nausea)
- Commercial Markers (купить, цена, доставка)
- Synonym Rotation (макс 2 повтора/параграф)
- Anti-Fluff (запрещённые клише)
- Tone: Expert & Direct

---

## Преимущества Sub-agents

| Преимущество | Эффект |
|--------------|--------|
| Изолированный контекст | ~70% экономия токенов |
| Параллельное выполнение | Можно запускать stages независимо |
| Специализация | Каждый агент — свой SSOT |
| Модульность | Легко обновить один prompt |

---

**Version:** 5.0
**Updated:** 2025-12-11
**Spec:** SEO_MASTER.md v7.3
