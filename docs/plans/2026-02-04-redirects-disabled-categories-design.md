# Design: 301 Redirects для отключенных категорий

**Дата:** 2026-02-04
**Статус:** Deployed
**Deployed:** 2026-02-04
**Note:** All targets changed to UK slugs (site defaults to UK)

---

## Проблема

25 отключенных категорий в OpenCart генерируют 404 ошибки. Нужно настроить 301 редиректы на семантически близкие активные категории через модуль `slasoft_redirect`.

---

## Решение

Использовать существующий модуль `slasoft_redirect` для добавления 301 редиректов в таблицу `oc_slasoft_redirect`.

### Структура модуля

**Таблица:** `oc_slasoft_redirect`

| Поле | Тип | Описание |
|------|-----|----------|
| redirect_id | int | PK, auto_increment |
| from_url | varchar(512) | Старый URL (без `/` в начале) |
| to_url | char(255) | Целевой URL |
| code | smallint | 301, 302, 307, 403, 404, 410 |
| status | tinyint | 1=активен, 0=неактивен |
| cnt | int | Счётчик срабатываний |
| last_date | datetime | Последнее срабатывание |
| created_at | timestamp | Дата создания |

**Особенности:**
- Поддержка RegEx (если `from_url` начинается с `#`)
- Автозамена при дубликате `from_url`
- Автоматический счётчик переходов

---

## Маппинг редиректов

### Уже настроены (пропускаем)

| from_url | to_url | Статус |
|----------|--------|--------|
| eksterier | moyka-i-eksterer | ✅ |
| eksterier/ | moyka-i-eksterer | ✅ |
| ksterer | moyka-i-eksterer | ✅ |
| ochyshchennia-kuzova-ta-khromu | moyka-i-eksterer/ochistiteli-kuzova | ✅ |
| konservatsiia-ta-sushinnia-lkp | shvydkyi-blyskpolimer | ✅ |

### Новые редиректы

#### Корневые категории

| ID | from_url (UK) | from_url (RU) | to_url | Логика |
|----|---------------|---------------|--------|--------|
| 467 | specials/ | ru-specials/ | / | SALE → главная |
| 493 | opt-ta-b2b | opt-i-b2b | / | B2B отключен |

#### Защитные покрытия (parent=435)

| ID | from_url (UK) | from_url (RU) | to_url (UK) | to_url (RU) | Логика |
|----|---------------|---------------|-------------|-------------|--------|
| 440 | zakhysni-pokryttia-dlia-plastyku | zashchytnye-pokrytyia-dlia-plastyka | poliroli-dlya-plastyku | poliroli-dlya-plastika | похожая |
| 441 | zakhysni-pokryttia-dlia-skla | zashchytnye-pokrytyia-dlia-stekol | antydoshch | antidozhd | защита стекла |
| 442 | zakhysni-pokryttia-dlia-shkiry | zashchytnye-pokrytyia-dlia-kozhy | zasoby-dlya-shkiry | sredstva-dlya-kozhi | похожая |
| 443 | zakhysni-pokryttia-dlia-tkanyny | zashchytnye-pokrytyia-dlia-tkany | zakhysni-pokryttya | zashchitnye-pokrytiya | parent |
| 444 | zakhysni-pokryttia-dlia-kolis | zashchytnye-pokrytyia-dlia-koles | zasoby-dlya-dyskiv-i-shyn | sredstva-dlya-diskov-i-shin | похожая |

#### Аксессуары (parent=445)

| ID | from_url (UK) | from_url (RU) | to_url (UK) | to_url (RU) | Логика |
|----|---------------|---------------|-------------|-------------|--------|
| 449 | shchitky-aplikatory-penzli-dlia-interieru | shchetky-applykatory-kysty-dlia-ynterera | shchitky-i-penzli | shchetki-i-kisti | похожая |
| 450 | mochalky-skrebky-shchitky-dlia-eksterieru | mochalky-skrebky-shchetky-dlia-ksterera | hubky-i-rukavychky | gubki-i-varezhki | похожая |
| 451 | hanchirka-dlia-avto | triapky-dlia-avto | mikrofibra-i-ganchirky | mikrofibra-i-tryapki | похожая |
| 452 | shchitky-ta-penzlyky | shchetky-y-kysty | shchitky-i-penzli | shchetki-i-kisti | похожая |

#### Микрофибра (parent=446)

| ID | from_url (UK) | from_url (RU) | to_url (UK) | to_url (RU) | Логика |
|----|---------------|---------------|-------------|-------------|--------|
| 482 | hanchirka-dlya-avto | tryapka-dlya-avto | mikrofibra-i-ganchirky | mikrofibra-i-tryapki | parent |
| 483 | hanchirka-dlya-vytyrannya-avto-pislya-myiky | tryapka-dlya-vytiraniya-avto-posle-moyki | mikrofibra-i-ganchirky | mikrofibra-i-tryapki | parent |
| 484 | dlya-skla | dlya-stekol | mikrofibra-i-ganchirky | mikrofibra-i-tryapki | parent |

#### Полировка (parent=457)

| ID | from_url (UK) | from_url (RU) | to_url (UK) | to_url (RU) | Логика |
|----|---------------|---------------|-------------|-------------|--------|
| 460 | opravlennia-pidkladky-utrymuvachi-kruhiv | opravky-podlozhky-derzhately-kruhov | poliruvalni-kruhy | polirovalnye-krugi | parent |

#### Оборудование (parent=462)

| ID | from_url (UK) | from_url (RU) | to_url (UK) | to_url (RU) | Логика |
|----|---------------|---------------|-------------|-------------|--------|
| 464 | pylososy-dlia-avtomyiky | pylesosy-dlia-avtomoiky | obladnannya | oborudovanie | parent |
| 465 | ozonoheneratory | ozonoheneratory-1 | obladnannya | oborudovanie | parent |

#### Наборы (parent=466)

| ID | from_url (UK) | from_url (RU) | to_url (UK) | to_url (RU) | Логика |
|----|---------------|---------------|-------------|-------------|--------|
| 486 | nabory-dlya-myiky | nabory-dlya-moyki | nabory | nabory | parent |
| 487 | nabory-dlya-salonu | nabory-dlya-salona | nabory | nabory | parent |
| 488 | podarunkovyi | podarochnyy | nabory | nabory | parent |

#### Мойка

| ID | from_url (UK) | from_url (RU) | to_url (UK) | to_url (RU) | Логика |
|----|---------------|---------------|-------------|-------------|--------|
| 426 | ochyshchuvachi-ta-znezhyriuvachi | ochystytely-y-obezzhyryvately | znezhyryuvachi | obezzhirivateli | активная категория |
| 479 | kyslotnyi | kislotnyy | avtoshampuny | avtoshampuni | parent |
| 481 | keramika-dlya-dyskiv | keramika-dlya-diskov | zasoby-dlya-dyskiv-i-shyn | sredstva-dlya-diskov-i-shin | parent |

---

## SQL для добавления редиректов

```sql
-- =============================================
-- 301 Redirects: Disabled Categories
-- Generated: 2026-02-04
-- =============================================

-- Корневые
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('specials/', '/', 301, 1, NOW()),
('ru-specials/', '/', 301, 1, NOW()),
('opt-ta-b2b', '/', 301, 1, NOW()),
('opt-i-b2b', '/', 301, 1, NOW());

-- Защитные покрытия
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

-- Аксессуары
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('shchitky-aplikatory-penzli-dlia-interieru', 'shchitky-i-penzli', 301, 1, NOW()),
('shchetky-applykatory-kysty-dlia-ynterera', 'shchetki-i-kisti', 301, 1, NOW()),
('mochalky-skrebky-shchitky-dlia-eksterieru', 'hubky-i-rukavychky', 301, 1, NOW()),
('mochalky-skrebky-shchetky-dlia-ksterera', 'gubki-i-varezhki', 301, 1, NOW()),
('hanchirka-dlia-avto', 'mikrofibra-i-ganchirky', 301, 1, NOW()),
('triapky-dlia-avto', 'mikrofibra-i-tryapki', 301, 1, NOW()),
('shchitky-ta-penzlyky', 'shchitky-i-penzli', 301, 1, NOW()),
('shchetky-y-kysty', 'shchetki-i-kisti', 301, 1, NOW());

-- Микрофибра
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('hanchirka-dlya-avto', 'mikrofibra-i-ganchirky', 301, 1, NOW()),
('tryapka-dlya-avto', 'mikrofibra-i-tryapki', 301, 1, NOW()),
('hanchirka-dlya-vytyrannya-avto-pislya-myiky', 'mikrofibra-i-ganchirky', 301, 1, NOW()),
('tryapka-dlya-vytiraniya-avto-posle-moyki', 'mikrofibra-i-tryapki', 301, 1, NOW()),
('dlya-skla', 'mikrofibra-i-ganchirky', 301, 1, NOW()),
('dlya-stekol', 'mikrofibra-i-tryapki', 301, 1, NOW());

-- Полировка
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('opravlennia-pidkladky-utrymuvachi-kruhiv', 'poliruvalni-kruhy', 301, 1, NOW()),
('opravky-podlozhky-derzhately-kruhov', 'polirovalnye-krugi', 301, 1, NOW());

-- Оборудование
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('pylososy-dlia-avtomyiky', 'obladnannya', 301, 1, NOW()),
('pylesosy-dlia-avtomoiky', 'oborudovanie', 301, 1, NOW()),
('ozonoheneratory', 'obladnannya', 301, 1, NOW()),
('ozonoheneratory-1', 'oborudovanie', 301, 1, NOW());

-- Наборы
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('nabory-dlya-myiky', 'nabory', 301, 1, NOW()),
('nabory-dlya-moyki', 'nabory', 301, 1, NOW()),
('nabory-dlya-salonu', 'nabory', 301, 1, NOW()),
('nabory-dlya-salona', 'nabory', 301, 1, NOW()),
('podarunkovyi', 'nabory', 301, 1, NOW()),
('podarochnyy', 'nabory', 301, 1, NOW());

-- Мойка
INSERT INTO oc_slasoft_redirect (from_url, to_url, code, status, created_at) VALUES
('ochyshchuvachi-ta-znezhyriuvachi', 'znezhyryuvachi', 301, 1, NOW()),
('ochystytely-y-obezzhyryvately', 'obezzhirivateli', 301, 1, NOW()),
('kyslotnyi', 'avtoshampuny', 301, 1, NOW()),
('kislotnyy', 'avtoshampuni', 301, 1, NOW()),
('keramika-dlya-dyskiv', 'zasoby-dlya-dyskiv-i-shyn', 301, 1, NOW()),
('keramika-dlya-diskov', 'sredstva-dlya-diskov-i-shin', 301, 1, NOW());
```

---

## План выполнения

### Task 1: Валидация маппинга
- [ ] Проверить что все `to_url` существуют в `oc_seo_url`
- [ ] Проверить что нет дубликатов в `oc_slasoft_redirect`

### Task 2: Деплой SQL
- [ ] Выполнить SQL на продакшене через SSH
- [ ] Очистить кеш редиректов

### Task 3: Верификация
- [ ] Проверить 5-10 редиректов через curl
- [ ] Мониторинг `cnt` через неделю

---

## Команды

```bash
# Деплой
ssh ult "mysql -u root -pfr1daYTw1st yastman_test < redirects.sql"

# Очистка кеша (через PHP)
ssh ult "cd /home/yastman/sites/ultimate.net.ua && php -r \"
\\\$cache = new Cache('file', 864000);
\\\$cache->delete('redirect');
echo 'Cache cleared';
\""

# Проверка редиректа
curl -I https://ultimate.net.ua/zakhysni-pokryttia-dlia-plastyku

# Статистика
ssh ult "mysql -u root -pfr1daYTw1st yastman_test -e \"
SELECT from_url, to_url, cnt, last_date
FROM oc_slasoft_redirect
WHERE cnt > 0
ORDER BY cnt DESC LIMIT 20;
\""
```

---

## Риски

| Риск | Митигация |
|------|-----------|
| Дубликат from_url | Модуль автоматически заменяет старую запись |
| Неверный to_url (404) | Валидация перед деплоем |
| Кеш не обновился | Ручная очистка кеша |

---

## Итого

- **Новых редиректов:** 46 (all targets → UK slugs)
- **Уже настроено:** 7
- **Всего после деплоя:** 53
- **Всего категорий:** 25 отключенных
