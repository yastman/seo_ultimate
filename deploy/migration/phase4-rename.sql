-- Phase 4: Rename category names
-- Run: cat deploy/migration/phase4-rename.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
SET NAMES utf8mb4;

-- L1: Интерьер → Уход за интерьером
UPDATE oc_category_description SET name = 'Уход за интерьером' WHERE category_id = 425 AND language_id = 3;
UPDATE oc_category_description SET name = 'Догляд за інтер\'єром' WHERE category_id = 425 AND language_id = 1;

-- L1: Защита → Защитные покрытия
UPDATE oc_category_description SET name = 'Защитные покрытия' WHERE category_id = 435 AND language_id = 3;
UPDATE oc_category_description SET name = 'Захисні покриття' WHERE category_id = 435 AND language_id = 1;

-- L3: Очиститель стекол авто → Очистители стекол
UPDATE oc_category_description SET name = 'Очистители стекол' WHERE category_id = 418 AND language_id = 3;
UPDATE oc_category_description SET name = 'Очисники скла' WHERE category_id = 418 AND language_id = 1;

-- L3: Очистители и обезжириватели → Обезжириватели
UPDATE oc_category_description SET name = 'Обезжириватели' WHERE category_id = 426 AND language_id = 3;
UPDATE oc_category_description SET name = 'Знежирювачі' WHERE category_id = 426 AND language_id = 1;

-- L3: Средства для колесных дисков → Очистители дисков
UPDATE oc_category_description SET name = 'Очистители дисков' WHERE category_id = 419 AND language_id = 3;
UPDATE oc_category_description SET name = 'Очисники дисків' WHERE category_id = 419 AND language_id = 1;

-- L3: Средства для шин → Очистители шин
UPDATE oc_category_description SET name = 'Очистители шин' WHERE category_id = 420 AND language_id = 3;
UPDATE oc_category_description SET name = 'Очисники шин' WHERE category_id = 420 AND language_id = 1;

-- Verify
SELECT category_id, language_id, name FROM oc_category_description
WHERE category_id IN (425, 435, 418, 426, 419, 420)
ORDER BY category_id, language_id;
