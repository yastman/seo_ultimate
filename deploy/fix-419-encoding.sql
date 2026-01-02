-- Fix: Decode HTML entities in category 419
-- База: yastman_test

UPDATE oc_category_description SET
  description = REPLACE(description, '&lt;', '<')
WHERE category_id = 419;

UPDATE oc_category_description SET
  description = REPLACE(description, '&gt;', '>')
WHERE category_id = 419;

UPDATE oc_category_description SET
  description = REPLACE(description, '&quot;', '"')
WHERE category_id = 419;

UPDATE oc_category_description SET
  description = REPLACE(description, '&amp;', '&')
WHERE category_id = 419;

-- Теперь добавляем стили и отступы как у остальных
UPDATE oc_category_description SET
  description = REPLACE(description, '<h2>', '<br><br><h2>')
WHERE category_id = 419 AND description NOT LIKE '%<br><br><h2>%';

UPDATE oc_category_description SET
  description = REPLACE(description, '<h3>', '<br><h3>')
WHERE category_id = 419 AND description NOT LIKE '%<br><h3>%';

UPDATE oc_category_description SET
  description = REPLACE(description, '</ul>
<strong>', '</ul>
<p><strong>')
WHERE category_id = 419;

-- Проверка
SELECT category_id, language_id,
  LEFT(description, 200) as preview
FROM oc_category_description WHERE category_id = 419;
