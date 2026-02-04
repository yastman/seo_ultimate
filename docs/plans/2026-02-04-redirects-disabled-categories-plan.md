# 301 Redirects для отключенных категорий — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Настроить 301 редиректы для 25 отключенных категорий через модуль slasoft_redirect в OpenCart.

**Architecture:** SQL INSERT в таблицу `oc_slasoft_redirect`. Модуль автоматически обрабатывает редиректы на уровне PHP startup. Валидация target URL перед деплоем.

**Tech Stack:** MySQL, SSH, curl для верификации

**Reference:** `docs/plans/2026-02-04-redirects-disabled-categories-design.md`

---

## Task 1: Валидация target URLs

**Цель:** Убедиться что все целевые URL существуют в `oc_seo_url`.

**Step 1: Получить список всех target URLs из дизайна**

Run:
```bash
cat << 'EOF'
poliroli-dlya-plastyku
poliroli-dlya-plastika
antydoshch
antidozhd
zasoby-dlya-shkiry
sredstva-dlya-kozhi
zakhysni-pokryttya
zashchitnye-pokrytiya
zasoby-dlya-dyskiv-i-shyn
sredstva-dlya-diskov-i-shin
shchitky-i-penzli
shchetki-i-kisti
hubky-i-rukavychky
gubki-i-varezhki
mikrofibra-i-ganchirky
mikrofibra-i-tryapki
poliruvalni-kruhy
polirovalnye-krugi
obladnannya
oborudovanie
nabory
znezhyryuvachi
obezzhirivateli
avtoshampuny
avtoshampuni
EOF
```

**Step 2: Проверить существование каждого URL в БД**

Run:
```bash
ssh ult "mysql -u root -pfr1daYTw1st yastman_test -e \"
SELECT keyword, query
FROM oc_seo_url
WHERE keyword IN (
  'poliroli-dlya-plastyku',
  'poliroli-dlya-plastika',
  'antydoshch',
  'antidozhd',
  'zasoby-dlya-shkiry',
  'sredstva-dlya-kozhi',
  'zakhysni-pokryttya',
  'zashchitnye-pokrytiya',
  'zasoby-dlya-dyskiv-i-shyn',
  'sredstva-dlya-diskov-i-shin',
  'shchitky-i-penzli',
  'shchetki-i-kisti',
  'hubky-i-rukavychky',
  'gubki-i-varezhki',
  'mikrofibra-i-ganchirky',
  'mikrofibra-i-tryapki',
  'poliruvalni-kruhy',
  'polirovalnye-krugi',
  'obladnannya',
  'oborudovanie',
  'nabory',
  'znezhyryuvachi',
  'obezzhirivateli',
  'avtoshampuny',
  'avtoshampuni'
)
ORDER BY keyword;
\""
```

Expected: 25 rows (все URL найдены). Если меньше — найти отсутствующие и исправить маппинг.

**Step 3: Проверить существующие редиректы (избежать дубликатов)**

Run:
```bash
ssh ult "mysql -u root -pfr1daYTw1st yastman_test -e \"
SELECT from_url, to_url FROM oc_slasoft_redirect WHERE status = 1 ORDER BY from_url;
\""
```

Expected: Список текущих редиректов. Сравнить с планируемыми — исключить дубликаты.

---

## Task 2: Создать SQL файл с редиректами

**Files:**
- Create: `data/generated/redirects_disabled_categories.sql`

**Step 1: Создать SQL файл**

```sql
-- =============================================
-- 301 Redirects: Disabled Categories
-- Generated: 2026-02-04
-- Total: 44 redirects (22 UK + 22 RU)
-- =============================================

-- Корневые категории (SALE, B2B → главная)
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('specials/', '/', 301, 1, NOW()),
('ru-specials/', '/', 301, 1, NOW()),
('opt-ta-b2b', '/', 301, 1, NOW()),
('opt-i-b2b', '/', 301, 1, NOW());

-- Защитные покрытия (5 категорий × 2 языка = 10 редиректов)
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('zakhysni-pokryttia-dlia-plastyku', 'poliroli-dlya-plastyku', 301, 1, NOW()),
('zashchytnye-pokrytyia-dlia-plastyka', 'poliroli-dlya-plastika', 301, 1, NOW()),
('zakhysni-pokryttia-dlia-skla', 'antydoshch', 301, 1, NOW()),
('zashchytnye-pokrytyia-dlia-stekol', 'antidozhd', 301, 1, NOW()),
('zakhysni-pokryttia-dlia-shkiry', 'zasoby-dlya-shkiry', 301, 1, NOW()),
('zashchytnye-pokrytyia-dlia-kozhy', 'sredstva-dlya-kozhi', 301, 1, NOW()),
('zakhysni-pokryttia-dlia-tkanyny', 'zakhysni-pokryttya', 301, 1, NOW()),
('zashchytnye-pokrytyia-dlia-tkany', 'zashchitnye-pokrytiya', 301, 1, NOW()),
('zakhysni-pokryttia-dlia-kolis', 'zasoby-dlya-dyskiv-i-shyn', 301, 1, NOW()),
('zashchytnye-pokrytyia-dlia-koles', 'sredstva-dlya-diskov-i-shin', 301, 1, NOW());

-- Аксессуары (4 категории × 2 языка = 8 редиректов)
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('shchitky-aplikatory-penzli-dlia-interieru', 'shchitky-i-penzli', 301, 1, NOW()),
('shchetky-applykatory-kysty-dlia-ynterera', 'shchetki-i-kisti', 301, 1, NOW()),
('mochalky-skrebky-shchitky-dlia-eksterieru', 'hubky-i-rukavychky', 301, 1, NOW()),
('mochalky-skrebky-shchetky-dlia-ksterera', 'gubki-i-varezhki', 301, 1, NOW()),
('hanchirka-dlia-avto', 'mikrofibra-i-ganchirky', 301, 1, NOW()),
('triapky-dlia-avto', 'mikrofibra-i-tryapki', 301, 1, NOW()),
('shchitky-ta-penzlyky', 'shchitky-i-penzli', 301, 1, NOW()),
('shchetky-y-kysty', 'shchetki-i-kisti', 301, 1, NOW());

-- Микрофибра (3 категории × 2 языка = 6 редиректов)
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('hanchirka-dlya-avto', 'mikrofibra-i-ganchirky', 301, 1, NOW()),
('tryapka-dlya-avto', 'mikrofibra-i-tryapki', 301, 1, NOW()),
('hanchirka-dlya-vytyrannya-avto-pislya-myiky', 'mikrofibra-i-ganchirky', 301, 1, NOW()),
('tryapka-dlya-vytiraniya-avto-posle-moyki', 'mikrofibra-i-tryapki', 301, 1, NOW()),
('dlya-skla', 'mikrofibra-i-ganchirky', 301, 1, NOW()),
('dlya-stekol', 'mikrofibra-i-tryapki', 301, 1, NOW());

-- Полировка (1 категория × 2 языка = 2 редиректа)
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('opravlennia-pidkladky-utrymuvachi-kruhiv', 'poliruvalni-kruhy', 301, 1, NOW()),
('opravky-podlozhky-derzhately-kruhov', 'polirovalnye-krugi', 301, 1, NOW());

-- Оборудование (2 категории × 2 языка = 4 редиректа)
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('pylososy-dlia-avtomyiky', 'obladnannya', 301, 1, NOW()),
('pylesosy-dlia-avtomoiky', 'oborudovanie', 301, 1, NOW()),
('ozonoheneratory', 'obladnannya', 301, 1, NOW()),
('ozonoheneratory-1', 'oborudovanie', 301, 1, NOW());

-- Наборы (3 категории × 2 языка = 6 редиректов)
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('nabory-dlya-myiky', 'nabory', 301, 1, NOW()),
('nabory-dlya-moyki', 'nabory', 301, 1, NOW()),
('nabory-dlya-salonu', 'nabory', 301, 1, NOW()),
('nabory-dlya-salona', 'nabory', 301, 1, NOW()),
('podarunkovyi', 'nabory', 301, 1, NOW()),
('podarochnyy', 'nabory', 301, 1, NOW());

-- Мойка (3 категории × 2 языка = 6 редиректов)
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('ochyshchuvachi-ta-znezhyriuvachi', 'znezhyryuvachi', 301, 1, NOW()),
('ochystytely-y-obezzhyryvately', 'obezzhirivateli', 301, 1, NOW()),
('kyslotnyi', 'avtoshampuny', 301, 1, NOW()),
('kislotnyy', 'avtoshampuni', 301, 1, NOW()),
('keramika-dlya-dyskiv', 'zasoby-dlya-dyskiv-i-shyn', 301, 1, NOW()),
('keramika-dlya-diskov', 'sredstva-dlya-diskov-i-shin', 301, 1, NOW());

-- =============================================
-- Summary: 44 redirects added
-- =============================================
```

**Step 2: Сохранить файл**

Run:
```bash
cat > data/generated/redirects_disabled_categories.sql << 'SQLEOF'
[SQL content above]
SQLEOF
```

---

## Task 3: Деплой редиректов на продакшен

**Step 1: Загрузить SQL на сервер и выполнить**

Run:
```bash
cat data/generated/redirects_disabled_categories.sql | ssh ult "mysql -u root -pfr1daYTw1st yastman_test"
```

Expected: No errors. Query OK messages.

**Step 2: Проверить количество добавленных записей**

Run:
```bash
ssh ult "mysql -u root -pfr1daYTw1st yastman_test -e \"
SELECT COUNT(*) as total_redirects FROM oc_slasoft_redirect WHERE status = 1;
\""
```

Expected: Число увеличилось на 44 (было ~7, стало ~51).

**Step 3: Проверить что записи добавлены корректно**

Run:
```bash
ssh ult "mysql -u root -pfr1daYTw1st yastman_test -e \"
SELECT from_url, to_url, code, created_at
FROM oc_slasoft_redirect
WHERE created_at >= CURDATE()
ORDER BY redirect_id DESC
LIMIT 10;
\""
```

Expected: Последние 10 добавленных редиректов с датой сегодня.

---

## Task 4: Очистка кеша редиректов

**Step 1: Найти директорию кеша**

Run:
```bash
ssh ult "find /home/yastman/sites/ultimate.net.ua -type d -name 'cache' 2>/dev/null | head -5"
```

**Step 2: Удалить файл кеша редиректов**

Run:
```bash
ssh ult "rm -f /home/yastman/sites/storageawdawdG11231251561/cache/cache.redirect.* 2>/dev/null; echo 'Cache cleared'"
```

Expected: "Cache cleared"

---

## Task 5: Верификация редиректов

**Step 1: Тест UK редиректа (защитные покрытия для пластика)**

Run:
```bash
curl -sI https://ultimate.net.ua/zakhysni-pokryttia-dlia-plastyku | grep -E "^(HTTP|Location)"
```

Expected:
```
HTTP/2 301
location: https://ultimate.net.ua/poliroli-dlya-plastyku
```

**Step 2: Тест RU редиректа (аксессуары)**

Run:
```bash
curl -sI https://ultimate.net.ua/shchetky-y-kysty | grep -E "^(HTTP|Location)"
```

Expected:
```
HTTP/2 301
location: https://ultimate.net.ua/shchetki-i-kisti
```

**Step 3: Тест корневого редиректа (SALE)**

Run:
```bash
curl -sI https://ultimate.net.ua/specials/ | grep -E "^(HTTP|Location)"
```

Expected:
```
HTTP/2 301
location: https://ultimate.net.ua/
```

**Step 4: Тест микрофибры**

Run:
```bash
curl -sI https://ultimate.net.ua/dlya-skla | grep -E "^(HTTP|Location)"
```

Expected:
```
HTTP/2 301
location: https://ultimate.net.ua/mikrofibra-i-ganchirky
```

**Step 5: Тест оборудования**

Run:
```bash
curl -sI https://ultimate.net.ua/ozonoheneratory | grep -E "^(HTTP|Location)"
```

Expected:
```
HTTP/2 301
location: https://ultimate.net.ua/obladnannya
```

---

## Task 6: Финальная проверка и отчёт

**Step 1: Сводка по всем редиректам**

Run:
```bash
ssh ult "mysql -u root -pfr1daYTw1st yastman_test -e \"
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN status = 1 THEN 1 ELSE 0 END) as active,
  SUM(CASE WHEN cnt > 0 THEN 1 ELSE 0 END) as used
FROM oc_slasoft_redirect;
\""
```

Expected: total ~51, active ~51, used — число редиректов со срабатываниями.

**Step 2: Обновить статус дизайн-документа**

Edit `docs/plans/2026-02-04-redirects-disabled-categories-design.md`:
- Изменить **Статус:** Draft → **Статус:** Deployed
- Добавить дату деплоя

**Step 3: Commit**

Run:
```bash
git add data/generated/redirects_disabled_categories.sql docs/plans/2026-02-04-redirects-disabled-categories-*.md
git commit -m "feat(redirects): add 301 redirects for 25 disabled categories

- 44 new redirects (22 UK + 22 RU)
- Routes disabled categories to semantically similar active ones
- Uses slasoft_redirect OpenCart module

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Rollback Plan

Если нужно откатить:

```bash
ssh ult "mysql -u root -pfr1daYTw1st yastman_test -e \"
DELETE FROM oc_slasoft_redirect WHERE created_at >= '2026-02-04';
\""
```

Или отключить конкретный редирект:

```bash
ssh ult "mysql -u root -pfr1daYTw1st yastman_test -e \"
UPDATE oc_slasoft_redirect SET status = 0 WHERE from_url = 'some-url';
\""
```

---

## Checklist

- [ ] Task 1: Валидация target URLs
- [ ] Task 2: Создать SQL файл
- [ ] Task 3: Деплой на продакшен
- [ ] Task 4: Очистка кеша
- [ ] Task 5: Верификация (5 curl тестов)
- [ ] Task 6: Финальный отчёт и commit
