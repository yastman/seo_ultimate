# Session Prompt: Tests & Skills Implementation

**Copy this entire prompt into a new Claude Code session.**

---

## Context

Ты в проекте Ultimate.net.ua SEO pipeline. Есть готовый план реализации.

**Цель сессии:** Выполнить план из `docs/plans/2026-01-26-tests-and-skills-implementation.md`

## Твоя задача

1. Прочитай план: `docs/plans/2026-01-26-tests-and-skills-implementation.md`
2. Используй скилл `superpowers:executing-plans` для пошагового выполнения
3. Выполняй задачи по порядку (Task 1 → Task 10)
4. После каждой задачи — коммит
5. После Tasks 1-5 — checkpoint (проверь что тесты проходят)
6. После Tasks 6-9 — checkpoint (проверь что shared/ создан)

## Команда запуска

```
/superpowers:executing-plans docs/plans/2026-01-26-tests-and-skills-implementation.md
```

## Критерии успеха

**После выполнения:**
- [ ] `pytest -v` — все тесты проходят
- [ ] `ls .claude/skills/shared/` — 2 файла (validation-checklist.md, meta-rules.md)
- [ ] `grep -r "shared/" .claude/skills/uk-*/` — UK скиллы ссылаются на shared

## Важно

- **TDD:** сначала тест, потом проверка что проходит
- **Коммиты:** после каждой задачи
- **Не пропускай шаги:** каждый Step в задаче — отдельное действие
- **При ошибках:** фикси сразу, не переходи к следующей задаче

---

**Начни с:** Прочитай план и запусти executing-plans скилл.
