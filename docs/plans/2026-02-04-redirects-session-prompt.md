# Session Prompt: 301 Redirects для отключенных категорий

Скопируй и вставь в новую сессию Claude Code:

---

```
Выполни план: docs/plans/2026-02-04-redirects-disabled-categories-plan.md

КОНТЕКСТ:
- 25 отключенных категорий в OpenCart генерируют 404
- Нужно добавить 44 редиректа (22 UK + 22 RU) через модуль slasoft_redirect
- Таблица: oc_slasoft_redirect (from_url, to_url, code=301, status=1)

ПОДКЛЮЧЕНИЕ:
- SSH: ssh ult
- DB: mysql -u root -pfr1daYTw1st yastman_test

ЗАДАЧИ:
1. Валидация — проверить что все target URL существуют в oc_seo_url
2. Создать SQL — data/generated/redirects_disabled_categories.sql
3. Деплой — выполнить SQL через SSH
4. Очистка кеша — rm cache.redirect.* файлы
5. Верификация — curl -I тесты 5 URL
6. Commit

SKILLS: superpowers:executing-plans, superpowers:verification-before-completion

ПРАВИЛА:
- Выполняй task за task, показывай результат каждого шага
- При ошибке — СТОП, не продолжай
- НЕ делай git commit до Task 6

Начни с Task 1: Валидация target URLs
```

---

## Quick Reference

**Проверка target URL:**
```bash
ssh ult "mysql -u root -pfr1daYTw1st yastman_test -e \"
SELECT keyword FROM oc_seo_url WHERE keyword IN ('poliroli-dlya-plastyku','antydoshch','nabory');
\""
```

**Деплой:**
```bash
cat data/generated/redirects_disabled_categories.sql | ssh ult "mysql -u root -pfr1daYTw1st yastman_test"
```

**Верификация:**
```bash
curl -sI https://ultimate.net.ua/zakhysni-pokryttia-dlia-plastyku | grep -E "^(HTTP|Location)"
```

**Rollback:**
```bash
ssh ult "mysql -u root -pfr1daYTw1st yastman_test -e \"DELETE FROM oc_slasoft_redirect WHERE created_at >= '2026-02-04';\""
```
