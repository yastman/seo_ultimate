-- Fix: Wrap loose text in <p> tags and add line breaks before headers
-- База: yastman_test

-- Добавляем <br><br> перед каждым <h2> и <h3> для визуального отступа
-- Оборачиваем <strong>Text</strong> — в <p> если они идут подряд

UPDATE oc_category_description SET
  description = REPLACE(description, '<h2>', '<br><h2>'),
  description = REPLACE(description, '<h3>', '<br><h3>'),
  description = REPLACE(description, '</ul>\n<strong>', '</ul>\n<p><strong>'),
  description = REPLACE(description, '</table></div>\n<strong>', '</table></div>\n<p><strong>')
WHERE category_id IN (412, 415, 418, 419, 420, 421, 423);

-- Проверка
SELECT category_id, language_id,
  CASE WHEN description LIKE '%<br><h2>%' THEN '✅' ELSE '❌' END as h2_spaced
FROM oc_category_description
WHERE category_id IN (412, 415, 418, 419, 420, 421, 423)
ORDER BY category_id;
