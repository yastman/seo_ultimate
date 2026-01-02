-- Fix: Wrap strong tags in paragraphs for category 419
-- База: yastman_test

UPDATE oc_category_description SET
  description = REPLACE(description, 'варежка.\n<strong>', 'варежка.</p>\n<p><strong>')
WHERE category_id = 419;

UPDATE oc_category_description SET
  description = REPLACE(description, 'болтов.\n<strong>', 'болтов.</p>\n<p><strong>')
WHERE category_id = 419;

UPDATE oc_category_description SET
  description = REPLACE(description, 'шины.\n<br>', 'шины.</p>\n<br>')
WHERE category_id = 419;

-- UK version
UPDATE oc_category_description SET
  description = REPLACE(description, 'рукавичка.\n<strong>', 'рукавичка.</p>\n<p><strong>')
WHERE category_id = 419;

-- Проверка
SELECT category_id, language_id,
  CASE WHEN description LIKE '%<p><strong>%' THEN '✅' ELSE '❌' END as fixed
FROM oc_category_description WHERE category_id = 419;
