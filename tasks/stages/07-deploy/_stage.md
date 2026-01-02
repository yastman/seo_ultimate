# Stage 07: Deploy to OpenCart

**Skill:** `/deploy-to-opencart {slug}`
**Progress:** 0/51 RU | 0/51 UK

---

## Checklist per Category

### Pre-flight

- [ ] Quality Gate пройден (Stage 06 PASS)
- [ ] QUALITY_REPORT.md существует со статусом PASS
- [ ] VPS доступен
- [ ] Доступ к БД MySQL

### Execution

#### 1. Подготовка данных

- [ ] Прочитать `meta/{slug}_meta.json`
- [ ] Прочитать `content/{slug}_ru.md`
- [ ] Конвертировать MD → HTML
- [ ] Подготовить SQL запросы

#### 2. Найти category_id

```sql
SELECT category_id
FROM oc_category_description
WHERE name LIKE '%{category_name}%'
AND language_id = 1;
```

- [ ] category_id найден для RU
- [ ] category_id найден для UK (language_id = 3)

#### 3. Обновить Meta Tags (RU)

```sql
UPDATE oc_category_description
SET
  meta_title = '{title_ru}',
  meta_description = '{description_ru}',
  meta_h1 = '{h1_ru}'
WHERE category_id = {id} AND language_id = 1;
```

- [ ] Meta RU обновлены

#### 4. Обновить Meta Tags (UK)

```sql
UPDATE oc_category_description
SET
  meta_title = '{title_uk}',
  meta_description = '{description_uk}',
  meta_h1 = '{h1_uk}'
WHERE category_id = {id} AND language_id = 3;
```

- [ ] Meta UK обновлены

#### 5. Обновить Description (HTML Content)

```sql
UPDATE oc_category_description
SET description = '{html_content_ru}'
WHERE category_id = {id} AND language_id = 1;

UPDATE oc_category_description
SET description = '{html_content_uk}'
WHERE category_id = {id} AND language_id = 3;
```

- [ ] Content RU обновлён
- [ ] Content UK обновлён

#### 6. Очистить кэш OpenCart

```bash
# SSH to VPS
ssh user@vps
cd /var/www/ultimate.net.ua
rm -rf system/storage/cache/*
```

- [ ] Кэш очищен

### Validation — Post-Deploy Check

#### 1. Визуальная проверка

- [ ] Открыть категорию на сайте
- [ ] H1 отображается корректно
- [ ] Текст форматирован правильно
- [ ] Таблицы рендерятся
- [ ] FAQ отображается

#### 2. SEO проверка

- [ ] View Source → <title> корректен
- [ ] View Source → <meta description> корректен
- [ ] H1 на странице = meta_h1

#### 3. Проверка UK версии

- [ ] Переключить язык на UK
- [ ] Контент на украинском
- [ ] Meta tags на украинском

### Rollback Plan

```sql
-- Если что-то пошло не так, восстановить из бэкапа
-- Перед деплоем всегда делать:
mysqldump -u user -p ultimate oc_category_description > backup_$(date +%Y%m%d).sql
```

### Acceptance Criteria

- [ ] Meta tags видны на сайте
- [ ] Контент отображается корректно
- [ ] Обе языковые версии работают
- [ ] Нет ошибок в консоли
- [ ] Кэш очищен

### Post-action

- [ ] Переместить из `pending/` в `completed/`
- [ ] Обновить счётчик в `PIPELINE_STATUS.md`
- [ ] Записать дату деплоя

---

## Pending (51)

*Все категории ожидают Quality Gate*

---

## Completed (0)

*Пока нет задеплоенных категорий*

---

## Deploy Log Template

```markdown
# Deploy Log: {slug}

**Date:** 2025-XX-XX
**Deployed by:** Claude Code

## Database Updates

| Table | Field | Language | Status |
|-------|-------|----------|--------|
| oc_category_description | meta_title | RU | ✅ |
| oc_category_description | meta_title | UK | ✅ |
| oc_category_description | meta_description | RU | ✅ |
| oc_category_description | meta_description | UK | ✅ |
| oc_category_description | meta_h1 | RU | ✅ |
| oc_category_description | meta_h1 | UK | ✅ |
| oc_category_description | description | RU | ✅ |
| oc_category_description | description | UK | ✅ |

## Verification

- [x] Site checked
- [x] RU version OK
- [x] UK version OK
- [x] Cache cleared

## Notes
- category_id: 123
- Backup: backup_20251231.sql
```

---

## VPS Connection Info

```
Host: vps.ultimate.net.ua (или IP)
User: deploy
Key: ~/.ssh/ultimate_deploy
DB: ultimate
DB User: opencart_user
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| category_id not found | Check name spelling in DB |
| HTML broken | Escape quotes in SQL |
| Cache not cleared | SSH and rm -rf cache |
| UK not showing | Check language_id = 3 |
| Encoding issues | Ensure UTF-8 in SQL |
