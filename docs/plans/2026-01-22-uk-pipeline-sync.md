# UK Pipeline Sync v2.0

**Дата:** 2026-01-22
**Статус:** PLAN
**Цель:** Синхронизировать UK pipeline с RU — полная копия скиллов и субагентов

---

## Принцип

UK pipeline = полная копия RU pipeline:
- Папка `uk/categories/{slug}/` вместо `categories/{slug}/`
- Язык украинский
- Ключи украинские (с проверенной частотностью)

---

## UK Pipeline (целевой)

```
/uk-category-init → /uk-generate-meta → /uk-seo-research → /uk-content-generator → uk-content-reviewer → /uk-quality-gate → /uk-deploy
```

---

## Фаза 1: Удаление мусора

- [ ] Удалить `.claude/skills/uk-content-adapter/`
- [ ] Удалить `.claude/agents/uk-content-adapter.md`

---

## Фаза 2: Создание скиллов (skill-creator)

| # | Скилл | Источник | Изменения |
|---|-------|----------|-----------|
| 1 | `uk-seo-research` | `seo-research` | Пути uk/, язык UK |
| 2 | `uk-content-generator` | `content-generator` v3.2 | Пути uk/, язык UK, терминология |
| 3 | `uk-quality-gate` | `quality-gate` | Пути uk/, язык UK |
| 4 | `uk-deploy-to-opencart` | `deploy-to-opencart` | Пути uk/, язык UK |

### Правила адаптации RU → UK:

**Пути:**
- `categories/{slug}/` → `uk/categories/{slug}/`
- `{slug}_ru.md` → `{slug}_uk.md`
- `{slug}_meta.json` → без изменений (тот же формат)

**Язык:**
- `language: "ru"` → `language: "uk"`
- Все инструкции на украинском
- Примеры на украинском

**Терминология:**
- резина → гума
- мойка → миття
- стекло → скло
- средство → засіб
- защита → захист
- блеск → блиск
- купить → купити (только в meta)

---

## Фаза 3: Создание субагентов (subagent-creator)

| # | Агент | Источник | Tools |
|---|-------|----------|-------|
| 1 | `uk-seo-research` | `seo-research.md` | Read, Grep, Glob, Bash, Write |
| 2 | `uk-content-generator` | `content-generator.md` | Read, Grep, Glob, Bash, Write |
| 3 | `uk-quality-gate` | `quality-gate.md` | Read, Grep, Glob, Bash, Write |
| 4 | `uk-deploy-to-opencart` | `deploy-to-opencart.md` | Read, Grep, Glob, Bash, Write |

---

## Фаза 4: Синхронизация существующих

### uk-generate-meta

- [ ] Сравнить с `generate-meta` v15.0
- [ ] Добавить недостающие правила (IRON RULE, Producer/Shop pattern)
- [ ] Синхронизировать validation checklist

### uk-category-init

- [ ] Сравнить с `category-init` v3.0
- [ ] Проверить workflow соответствие

### uk-content-reviewer

- [ ] Сравнить с `content-reviewer`
- [ ] Убедиться что все проверки синхронизированы

---

## Фаза 5: Обновить CLAUDE.md

Добавить секцию UK Pipeline:

```markdown
## UK Pipeline

| Когда использовать | Команда | Описание |
| ------------------ | ------- | -------- |
| UK категория нужна | `/uk-category-init {slug}` | Создаёт UK структуру |
| UK мета-теги | `/uk-generate-meta {slug}` | Генерирует UK мета |
| UK research | `/uk-seo-research {slug}` | Промпт для Perplexity UK |
| UK контент | `/uk-content-generator {slug}` | Генерирует UK buyer guide |
| UK ревизия | `uk-content-reviewer {slug}` | Проверяет UK контент |
| UK валидация | `/uk-quality-gate {slug}` | Финальная проверка UK |
| UK деплой | `/uk-deploy {slug}` | Деплой UK на сайт |
```

---

## Checklist выполнения

### Фаза 1
- [ ] `rm -rf .claude/skills/uk-content-adapter/`
- [ ] `rm .claude/agents/uk-content-adapter.md`

### Фаза 2 (skill-creator)
- [ ] `/skill-creator uk-seo-research`
- [ ] `/skill-creator uk-content-generator`
- [ ] `/skill-creator uk-quality-gate`
- [ ] `/skill-creator uk-deploy-to-opencart`

### Фаза 3 (subagent-creator)
- [ ] `/subagent-creator uk-seo-research`
- [ ] `/subagent-creator uk-content-generator`
- [ ] `/subagent-creator uk-quality-gate`
- [ ] `/subagent-creator uk-deploy-to-opencart`

### Фаза 4
- [ ] Sync `uk-generate-meta`
- [ ] Check `uk-category-init`
- [ ] Check `uk-content-reviewer`

### Фаза 5
- [ ] Update CLAUDE.md

---

## Acceptance Criteria

1. UK pipeline полностью зеркалит RU pipeline
2. Все скиллы работают с `uk/categories/{slug}/`
3. Все инструкции и примеры на украинском
4. `uk-content-adapter` удалён
5. CLAUDE.md содержит UK pipeline документацию

---

**Version:** 1.0
