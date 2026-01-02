-- Fix: Add CSS styles for spacing and mobile tables
-- База: yastman_test
-- Добавляет <style> блок в начало description для отступов и адаптивности

SET @css_block = '<style>
.category-description h2 { margin-top: 1.5em; margin-bottom: 0.5em; }
.category-description h3 { margin-top: 1.2em; margin-bottom: 0.4em; }
.category-description p { margin-bottom: 1em; }
.category-description ul { margin-bottom: 1em; }
.category-description table { width: 100%; margin-bottom: 1em; }
@media (max-width: 767px) {
  .category-description table { display: block; overflow-x: auto; white-space: nowrap; }
  .category-description th, .category-description td { min-width: 100px; }
}
</style>
<div class="category-description">
';

SET @close_div = '
</div>';

-- Категория 412 (dlya-ruchnoy-moyki)
UPDATE oc_category_description SET
  description = CONCAT(@css_block, description, @close_div)
WHERE category_id = 412 AND description NOT LIKE '%category-description%';

-- Категория 415 (aktivnaya-pena)
UPDATE oc_category_description SET
  description = CONCAT(@css_block, description, @close_div)
WHERE category_id = 415 AND description NOT LIKE '%category-description%';

-- Категория 418 (ochistiteli-stekol)
UPDATE oc_category_description SET
  description = CONCAT(@css_block, description, @close_div)
WHERE category_id = 418 AND description NOT LIKE '%category-description%';

-- Категория 419 (ochistiteli-diskov)
UPDATE oc_category_description SET
  description = CONCAT(@css_block, description, @close_div)
WHERE category_id = 419 AND description NOT LIKE '%category-description%';

-- Категория 420 (ochistiteli-shin)
UPDATE oc_category_description SET
  description = CONCAT(@css_block, description, @close_div)
WHERE category_id = 420 AND description NOT LIKE '%category-description%';

-- Категория 421 (cherniteli-shin)
UPDATE oc_category_description SET
  description = CONCAT(@css_block, description, @close_div)
WHERE category_id = 421 AND description NOT LIKE '%category-description%';

-- Категория 423 (glina-i-avtoskraby)
UPDATE oc_category_description SET
  description = CONCAT(@css_block, description, @close_div)
WHERE category_id = 423 AND description NOT LIKE '%category-description%';

-- Проверка
SELECT category_id, language_id,
  CASE WHEN description LIKE '%category-description%' THEN '✅ Styled' ELSE '❌ Not styled' END as status
FROM oc_category_description
WHERE category_id IN (412, 415, 418, 419, 420, 421, 423)
ORDER BY category_id, language_id;
