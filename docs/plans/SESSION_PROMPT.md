# Session Prompt: Content Revision Execution

Скопируй этот промпт в новую сессию Claude Code:

---

```
/superpowers:executing-plans

Выполни план ревизии контента из docs/plans/2026-01-21-content-revision-plan.md

## Контекст

- 50 категорий интернет-магазина Ultimate.net.ua (автохимия и детейлинг)
- Тексты и мета-теги написаны субагентами, нужна ручная проверка
- Стандарты: content-generator v3.2, generate-meta

## Текущий прогресс

- ✅ moyka-i-eksterer — PASS (уже проверена)
- ⬜ avtoshampuni — следующая категория

## Workflow на категорию

1. Read: _clean.json, _meta.json, *_ru.md
2. Validate: 4 скрипта параллельно (validate_meta, validate_content, check_keyword_density, check_water_natasha)
3. Checklist: v3.2 (H1=name, intro 30-60, таблица, FAQ, no how-to, H2+secondary, entities, RU-first)
4. Verdict: PASS / WARNING / BLOCKER
5. Fix: если нужно
6. Re-validate: после фикса

## Критерии

BLOCKER (обязательный фикс):
- H1 ≠ name
- How-to секции
- Stem >3.0%
- Тошнота >4.0

WARNING (желательно):
- H2 без secondary keyword
- Вода >75%
- Англицизмы без RU-first

## Начни с

Batch 1, категория #2: avtoshampuni (Hub Page)
Path: categories/moyka-i-eksterer/avtoshampuni/

Показывай результат проверки каждой категории в формате таблицы:

| Проверка | Статус | Комментарий |
|----------|--------|-------------|
| Meta | ✅/⚠️/❌ | ... |
| Content SEO | ✅/⚠️/❌ | ... |
| Keyword Density | ✅/⚠️/❌ | ... |
| Тошнота/Вода | ✅/⚠️/❌ | ... |
| Ручной чеклист | ✅/⚠️/❌ | ... |

После каждой категории спрашивай: "Переходим к следующей?"
```

---

**Как использовать:**

1. Открой новую сессию Claude Code в этой директории
2. Вставь промпт выше
3. Claude активирует executing-plans и начнёт с avtoshampuni
