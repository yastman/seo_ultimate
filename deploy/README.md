# Deploy — SQL файлы для OpenCart

**[← Назад в корень](../README.md)**

---

## Структура файлов

| Паттерн | Назначение |
|---------|------------|
| `{slug}.sql` | Полный деплой (meta + content) |
| `{slug}_ru.sql` | Только RU версия |
| `{slug}_uk.sql` | Только UK версия |
| `{slug}_update.sql` | Обновление существующего |
| `fix-*.sql` | Исправления багов |

---

## Как применять

### 1. Подключиться к VPS

```bash
ssh user@vps.ultimate.net.ua
```

### 2. Сделать бэкап

```bash
mysqldump -u opencart_user -p ultimate oc_category_description > backup_$(date +%Y%m%d).sql
```

### 3. Применить SQL

```bash
mysql -u opencart_user -p ultimate < deploy/{slug}.sql
```

### 4. Очистить кэш

```bash
rm -rf /var/www/ultimate.net.ua/system/storage/cache/*
```

### 5. Проверить на сайте

- Открыть категорию
- Проверить RU и UK версии
- View Source → проверить meta tags

---

## Генерация SQL

```bash
python3 scripts/generate_sql.py {slug}
```

---

## Откат

```bash
mysql -u opencart_user -p ultimate < backup_YYYYMMDD.sql
```

---

## Таблица в БД

```sql
-- Структура oc_category_description
category_id     INT
language_id     INT (1=RU, 3=UK)
name            VARCHAR
description     TEXT (HTML контент)
meta_title      VARCHAR
meta_description VARCHAR
meta_h1         VARCHAR
```
