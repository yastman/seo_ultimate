# Session Prompt: UK Skills Sync

Скопируй этот промпт в новую сессию Claude Code:

---

```
/superpowers:executing-plans docs/plans/2026-01-29-uk-skills-sync-plan.md

Выполни план полностью — 10 задач.

Контекст:
- UK скиллы используют неправильную формулу Title "Купити {pk} в Україні"
- Правильная формула: "{pk} — купити в інтернет-магазині Ultimate"
- 5 UK meta файлов имеют WARNING (короткий Title или marketing fluff)

После каждого Task запускай валидацию изменённого файла.
После Task 10 — полная валидация и коммит.
```

---

## Файлы плана

- **Design:** `docs/plans/2026-01-29-uk-skills-sync-design.md`
- **Plan:** `docs/plans/2026-01-29-uk-skills-sync-plan.md`

## Ожидаемый результат

```
python3 scripts/validate_meta.py --all

Total files: 60
✅ PASS: 60
⚠️  WARNING: 0
❌ FAIL: 0
```
