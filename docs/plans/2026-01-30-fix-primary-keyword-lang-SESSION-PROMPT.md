# Session Prompt: Fix Primary Keyword Lang

Скопируй этот промпт в новую сессию Claude Code:

---

```
/superpowers:executing-plans docs/plans/2026-01-30-fix-primary-keyword-lang.md

Контекст: Валидатор контента (validate_content.py) не передаёт параметр lang в check_primary_keyword(), из-за чего для UK контента используется русская морфология и "губка" не матчится с "губку".

Баг локализован:
- scripts/validate_content.py:927 — вызов без lang
- scripts/validate_content.py:294 — hardcoded lang="ru" в semantic функции

Fix простой: добавить lang=lang в 3 местах + тест.

Выполни все 6 задач из плана. После каждой задачи — короткий статус.
```

---

## Quick Reference

**Файлы для изменения:**
- `scripts/validate_content.py` (строки 927, 294, 932)
- `tests/unit/test_validate_content.py` (добавить 2 теста)

**Команды для проверки:**
```bash
pytest tests/unit/test_validate_content.py -v
python3 scripts/validate_content.py uk/categories/aktivnaya-pena/content/aktivnaya-pena_uk.md "активна піна" --mode seo --lang uk
```

**Ожидаемый результат:**
- UK ключи с падежами матчатся (губка ↔ губку)
- RU валидация не сломана
- Все тесты проходят
