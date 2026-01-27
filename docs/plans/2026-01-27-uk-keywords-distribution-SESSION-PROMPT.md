# Session Prompt: UK Keywords Distribution

**Копіюй цей промпт в нову сесію Claude Code:**

---

```
REQUIRED: використовуй superpowers:executing-plans

План: docs/plans/2026-01-27-uk-keywords-distribution-plan.md
Дизайн: docs/plans/2026-01-27-uk-keywords-distribution-design.md

Твоя задача: Task 1 — згенерувати чек-лист

Файли:
- Читати: uk/data/uk_keywords_source.csv (356 UK ключів)
- Читати: дизайн (маппінг ключів → категорій)
- Створити: tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md

Алгоритм:
1. Прочитай CSV — 356 ключів з частотністю
2. Прочитай маппінг з дизайну (яке слово → яка категорія)
3. Розподіли кожен ключ по категорії за маппінгом
4. Пріоритет: специфічне > загальне ("твердий віск" > "віск")
5. Ключі без категорії → секція "Нерозподілені"
6. Створи чек-лист з чекбоксами по кожній категорії
7. git commit

Формат чек-листа:
- Прогрес-трекер зверху
- Секція по кожній категорії з ключами
- Чекбокс для кожного ключа: - [ ] `ключ` (volume)

НЕ ЧІПАЙ інші файли. Тільки генерація чек-листа.
```

---

**Запуск:**

```bash
spawn-claude "REQUIRED: використовуй superpowers:executing-plans

План: docs/plans/2026-01-27-uk-keywords-distribution-plan.md

Твоя задача: Task 1 — згенерувати чек-лист tasks/TODO_UK_KEYWORDS_DISTRIBUTION.md

Читай CSV (uk/data/uk_keywords_source.csv), маппінг з дизайну, розподіли 356 ключів по категоріях. git commit після." /mnt/c/Users/user/Documents/Сайты/Ultimate.net.ua/сео_для_категорий_ультимейт
```
