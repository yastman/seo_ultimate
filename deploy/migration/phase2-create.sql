-- Phase 2: Create NEW categories
-- Backup: /home/yastman/backups/categories_backup_20260121_191135.sql
-- Run: cat deploy/migration/phase2-create.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
SET NAMES utf8mb4;

-- 1. opt-i-b2b (L1, parent=0)
INSERT INTO oc_category (category_id, parent_id, top, `column`, sort_order, status, date_added, date_modified)
VALUES (476, 0, 1, 1, 99, 1, NOW(), NOW());

INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_h1)
VALUES
(476, 3, 'Опт и B2B', '', 'Опт и B2B — Ultimate', 'Оптовые поставки автохимии и детейлинг средств', 'Опт и B2B'),
(476, 1, 'Опт та B2B', '', 'Опт та B2B — Ultimate', 'Оптові поставки автохімії та засобів детейлінгу', 'Опт та B2B');

INSERT INTO oc_category_path (category_id, path_id, level) VALUES (476, 476, 0);

INSERT INTO oc_seo_url (store_id, language_id, query, keyword)
VALUES
(0, 3, 'category_id=476', 'opt-i-b2b'),
(0, 1, 'category_id=476', 'opt-i-b2b');

-- 2. polirol-dlya-stekla (L3, parent=470 Средства для стекол)
INSERT INTO oc_category (category_id, parent_id, top, `column`, sort_order, status, date_added, date_modified)
VALUES (477, 470, 0, 1, 4, 1, NOW(), NOW());

INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_h1)
VALUES
(477, 3, 'Полироль для стекла', '', 'Полироль для стекла авто — купить | Ultimate', 'Полироль для автостекла. Удаление царапин и водного камня.', 'Полироль для стекла'),
(477, 1, 'Поліроль для скла', '', 'Поліроль для скла авто — купити | Ultimate', 'Поліроль для автоскла. Видалення подряпин та водного каменю.', 'Поліроль для скла');

INSERT INTO oc_category_path (category_id, path_id, level) VALUES (477, 468, 0), (477, 470, 1), (477, 477, 2);

INSERT INTO oc_seo_url (store_id, language_id, query, keyword)
VALUES
(0, 3, 'category_id=477', 'polirol-dlya-stekla'),
(0, 1, 'category_id=477', 'polirol-dlya-stekla');

-- 3. ukhod-za-naruzhnym-plastikom (L3, parent=471 Очистители кузова)
INSERT INTO oc_category (category_id, parent_id, top, `column`, sort_order, status, date_added, date_modified)
VALUES (478, 471, 0, 1, 5, 1, NOW(), NOW());

INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_h1)
VALUES
(478, 3, 'Уход за наружным пластиком', '', 'Уход за наружным пластиком авто | Ultimate', 'Средства для восстановления и защиты наружного пластика автомобиля.', 'Уход за наружным пластиком'),
(478, 1, 'Догляд за зовнішнім пластиком', '', 'Догляд за зовнішнім пластиком авто | Ultimate', 'Засоби для відновлення та захисту зовнішнього пластику автомобіля.', 'Догляд за зовнішнім пластиком');

INSERT INTO oc_category_path (category_id, path_id, level) VALUES (478, 468, 0), (478, 471, 1), (478, 478, 2);

INSERT INTO oc_seo_url (store_id, language_id, query, keyword)
VALUES
(0, 3, 'category_id=478', 'ukhod-za-naruzhnym-plastikom'),
(0, 1, 'category_id=478', 'ukhod-za-naruzhnym-plastikom');

-- 4. keramika-dlya-diskov (L3, parent=472 Средства для дисков и шин)
INSERT INTO oc_category (category_id, parent_id, top, `column`, sort_order, status, date_added, date_modified)
VALUES (479, 472, 0, 1, 4, 1, NOW(), NOW());

INSERT INTO oc_category_description (category_id, language_id, name, description, meta_title, meta_description, meta_h1)
VALUES
(479, 3, 'Керамика для дисков', '', 'Керамика для дисков — купить | Ultimate', 'Керамическое покрытие для колесных дисков. Защита от тормозной пыли.', 'Керамика для дисков'),
(479, 1, 'Кераміка для дисків', '', 'Кераміка для дисків — купити | Ultimate', 'Керамічне покриття для колісних дисків. Захист від гальмівного пилу.', 'Кераміка для дисків');

INSERT INTO oc_category_path (category_id, path_id, level) VALUES (479, 468, 0), (479, 472, 1), (479, 479, 2);

INSERT INTO oc_seo_url (store_id, language_id, query, keyword)
VALUES
(0, 3, 'category_id=479', 'keramika-dlya-diskov'),
(0, 1, 'category_id=479', 'keramika-dlya-diskov');

-- Verify
SELECT category_id, name FROM oc_category_description WHERE category_id >= 476 AND language_id = 3;
