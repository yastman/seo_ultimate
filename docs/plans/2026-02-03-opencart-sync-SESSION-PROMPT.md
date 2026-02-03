# OpenCart Category Sync — Session Prompt

Скопируй и вставь в новую сессию Claude Code:

---

```
Выполни план синхронизации категорий OpenCart.

Прочитай план: docs/plans/2026-02-03-opencart-category-sync.md

Используй скилл: superpowers:executing-plans

Выполняй задачи последовательно (Task 1 → Task 10).

ВАЖНО:
- glavnaya — НЕ ТРОГАТЬ
- Товары — НЕ ТРОГАТЬ (потом)
- SSH через `ult`
- БД: yastman_test
- language_id=3 (RU), language_id=1 (UK)

После каждой задачи — верификация перед следующей.

НЕ делай git commit до Task 10.
```

---

**Бэкап уже сделан:** `data/backups/categories_backup_2026-02-03.sql`

**Rollback если что-то пойдёт не так:**
```bash
cat data/backups/categories_backup_2026-02-03.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
```
