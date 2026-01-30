# Session Prompt: UK Full Cycle v3

Скопируй этот промпт в новую сессию Claude Code.

---

## Prompt

```
/superpowers:executing-plans

План: docs/plans/2026-01-26-uk-full-cycle-plan-v3.md

Контекст:
- 52 UK категории для SEO
- v3 критическое изменение: интеграция ВСЕХ ключей (keywords + secondary + supporting)
- Уже обработано 10 категорий из FAIL группы
- Начинай с Task 0 (commit uncommitted changes), затем оставшиеся 9 FAIL

Правила распределения ключей:
- PRIMARY (keywords[0]): H1 + intro + 2-3x в тексте
- SECONDARY (use_in=content): минимум 1 в H2 заголовке
- SUPPORTING (use_in=content): 1-2 в таблицах/body/FAQ
- Игнорировать use_in=meta_only

Двигайся по всем задачам без остановки.
```

---

## Checklist перед запуском

- [ ] Открыта новая сессия Claude Code
- [ ] Рабочая директория: `/mnt/c/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт`
- [ ] Скопирован промпт выше
