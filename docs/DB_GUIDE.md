# Гид по работе с БД OpenCart

## Ожидаемый результат

После применения изменений в БД должно быть:

### Структура категорий

```
468: Мойка и Экстерьер (status=1)
  ├─ 469: Автошампуни
  │   ├─ 415: Активная пена
  │   └─ 412: Для ручной мойки
  ├─ 470: Средства для стекол
  │   ├─ 418: Очистители стекол
  │   └─ 424: Омыватели
  ├─ 471: Очистители кузова
  │   ├─ 423: Глина и автоскрабы
  │   ├─ 417: Антимошка
  │   └─ 426: Антибитум
  └─ 472: Средства для дисков и шин
      ├─ 421: Чернители шин
      ├─ 419: Очистители дисков
      └─ 420: Очистители шин

Скрыты (status=0): 411, 416
```

### SEO-контент (9 категорий × 2 языка)

| ID | Название RU | H1 | Контент | URL RU | URL UK |
|----|-------------|----|---------|---------| -------|
| 412 | Для ручной мойки | Автошампунь для ручной мойки | ~9000 символов HTML | dlya-ruchnoy-moyki | dlya-ruchnogo-myttya |
| 415 | Активная пена | Активная пена | ~9000 символов HTML | aktivnaya-pena | aktivna-pina |
| 417 | Антимошка | Антимошка | ~9000 символов HTML | antimoshka | antimoshka-ua |
| 418 | Очистители стекол | Очиститель стекла авто | ~9000 символов HTML | ochistiteli-stekol | ochysnyky-skla |
| 419 | Очистители дисков | Очиститель дисков | ~11000 символов HTML | ochistiteli-diskov | ochysnyky-dyskiv |
| 420 | Очистители шин | Очиститель шин | ~9000 символов HTML | ochistiteli-shin | ochysnyky-shyn |
| 421 | Чернители шин | Чернитель резины | ~7700 символов HTML | cherniteli-shin | chornyteli-shyn |
| 423 | Глина и автоскрабы | Глина для авто | ~9700 символов HTML | glina-i-avtoskraby | glyna-ta-avtoskraby |
| 426 | Антибитум | Антибитум | ~7600 символов HTML | antibitum | antibitum-ua |

### Контент содержит

- `<h2>` — секции (Как выбрать, Как применять, FAQ)
- `<h3>` — подзаголовки FAQ
- `<table>` — сравнительные таблицы
- `<ul>/<li>` — списки
- `<strong>` — акценты

---

## SQL-файлы

| Файл | Размер | Назначение |
|------|--------|------------|
| `ultimate_net_ua_backup.sql` | 62 MB | Исходный бэкап (старая структура) |
| `seo_migration_full.sql` | 283 KB | **Для импорта на продакшен** |

---

## Локальная база данных (для разработки)

✅ **MySQL сервер**: MariaDB 10.11.13
✅ **База**: `yastman_test`

### Бэкап базы

```
ultimate_net_ua_backup.sql (62 MB) — исходный дамп с продакшена (старая структура)
```

Восстановление с нуля (если нужно):

```bash
mysql -u ultimate -pultimate123 -e "DROP DATABASE IF EXISTS yastman_test; CREATE DATABASE yastman_test;"
mysql -u ultimate -pultimate123 yastman_test < ultimate_net_ua_backup.sql
```

### Подключение

```bash
# Подключиться к базе
mysql -u ultimate -pultimate123 yastman_test

# Проверить таблицы
mysql -u ultimate -pultimate123 yastman_test -e "SHOW TABLES;"

# Показать категории
mysql -u ultimate -pultimate123 yastman_test -e "SELECT category_id, name FROM oc_category_description WHERE language_id = 3 LIMIT 10;"
```

### Креды (в `.env`)

```
DB_HOST=localhost
DB_PORT=3306
DB_NAME=yastman_test
DB_USER=ultimate
DB_PASSWORD=ultimate123
```

### Запуск/остановка MySQL

```bash
# Запустить
echo 'fr1daYTw1st' | sudo -S service mariadb start

# Остановить
echo 'fr1daYTw1st' | sudo -S service mariadb stop

# Статус
echo 'fr1daYTw1st' | sudo -S service mariadb status
```

## Структура таблицы `oc_category_description`

```sql
CREATE TABLE `oc_category_description` (
  `category_id` int(11) NOT NULL,      -- ID категории
  `language_id` int(11) NOT NULL,      -- 1=укр, 3=рус
  `name` varchar(255) NOT NULL,        -- Название в меню
  `description` text NOT NULL,         -- HTML КОНТЕНТ (сюда наш текст!)
  `meta_title` varchar(255) NOT NULL,  -- SEO Title
  `meta_description` varchar(255),     -- SEO Description
  `meta_keyword` varchar(255),         -- SEO Keywords
  `meta_h1` varchar(255) NOT NULL,     -- H1 заголовок
  PRIMARY KEY (`category_id`,`language_id`)
);
```

## Языки

| language_id | Язык |
|-------------|------|
| 1 | Украинский |
| 3 | Русский |

## Структура категорий (актуальная)

```
468: Мойка и Экстерьер (L1)
  ├─ 469: Автошампуни (L2)
  │   ├─ 415: Активная пена
  │   └─ 412: Для ручной мойки
  ├─ 470: Средства для стекол (L2)
  │   ├─ 418: Очистители стекол
  │   └─ 424: Омыватели
  ├─ 471: Очистители кузова (L2)
  │   ├─ 423: Глина и автоскрабы
  │   ├─ 417: Антимошка
  │   └─ 426: Антибитум
  └─ 472: Средства для дисков и шин (L2)
      ├─ 421: Чернители шин
      ├─ 419: Очистители дисков
      └─ 420: Очистители шин
```

### Наши 9 категорий (slug → ID)

| Slug | ID | Название | Родитель |
|------|-----|----------|----------|
| aktivnaya-pena | 415 | Активная пена | 469 Автошампуни |
| dlya-ruchnoy-moyki | 412 | Для ручной мойки | 469 Автошампуни |
| ochistiteli-stekol | 418 | Очистители стекол | 470 Средства для стекол |
| glina-i-avtoskraby | 423 | Глина и автоскрабы | 471 Очистители кузова |
| antimoshka | 417 | Антимошка | 471 Очистители кузова |
| antibitum | 426 | Антибитум | 471 Очистители кузова |
| cherniteli-shin | 421 | Чернители шин | 472 Средства для дисков и шин |
| ochistiteli-diskov | 419 | Очистители дисков | 472 Средства для дисков и шин |
| ochistiteli-shin | 420 | Очистители шин | 472 Средства для дисков и шин |

**Старые хабы (скрыты):** 411 Мойка авто, 416 Экстерьер

## Загрузка контента в БД

### Автоматическая загрузка (рекомендуется)

```bash
# Загрузить ВСЕ категории (RU + UK)
python3 scripts/upload_to_db.py

# Загрузить одну категорию
python3 scripts/upload_to_db.py antimoshka
```

Скрипт автоматически:

- Конвертирует MD → HTML (h2, h3, таблицы, списки)
- Читает meta из JSON
- Обновляет `description`, `meta_title`, `meta_description`, `meta_h1`
- Обрабатывает RU и UK версии

### Проверка загрузки

```bash
# Проверить все категории
mysql -u ultimate -pultimate123 yastman_test -e "
SELECT
    category_id,
    CASE language_id WHEN 3 THEN 'RU' ELSE 'UK' END as lang,
    LEFT(meta_h1, 30) as h1,
    LENGTH(description) as desc_len,
    CASE WHEN description LIKE '%<h2>%' THEN 'YES' ELSE 'NO' END as has_h2
FROM oc_category_description
WHERE category_id IN (415, 412, 418, 423, 417, 426, 421, 419, 420)
ORDER BY category_id, language_id;
"
```

### Ручной UPDATE (если нужно)

```sql
UPDATE `oc_category_description`
SET
    `description` = '<h2>Заголовок</h2><p>Текст...</p>',
    `meta_title` = 'Title',
    `meta_description` = 'Description',
    `meta_h1` = 'H1 заголовок'
WHERE `category_id` = 415 AND `language_id` = 3;
```

**Важно:** H1 в `meta_h1`, в `description` начинаем с `<h2>`

## Статус загрузки (2024-12-22)

| ID | Slug | RU | UK |
|----|------|:--:|:--:|
| 412 | dlya-ruchnoy-moyki | ✓ | ✓ |
| 415 | aktivnaya-pena | ✓ | ✓ |
| 417 | antimoshka | ✓ | ✓ |
| 418 | ochistiteli-stekol | ✓ | ✓ |
| 419 | ochistiteli-diskov | ✓ | ✓ |
| 420 | ochistiteli-shin | ✓ | ✓ |
| 421 | cherniteli-shin | ✓ | ✓ |
| 423 | glina-i-avtoskraby | ✓ | ✓ |
| 426 | antibitum | ✓ | ✓ |
