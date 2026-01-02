-- Fix: Mobile responsive tables for all categories
-- База: yastman_test
-- Заменяет <table class="table на <div class="table-responsive"><table class="table
-- И закрывает </table> на </table></div>

-- Категория: dlya-ruchnoy-moyki (412)
UPDATE oc_category_description SET
  description = REPLACE(
    REPLACE(description, '<table class=\"table', '<div class=\"table-responsive\"><table class=\"table'),
    '</table>', '</table></div>'
  )
WHERE category_id = 412 AND description LIKE '%<table class=%' AND description NOT LIKE '%table-responsive%';

-- Категория: aktivnaya-pena (415)
UPDATE oc_category_description SET
  description = REPLACE(
    REPLACE(description, '<table class=\"table', '<div class=\"table-responsive\"><table class=\"table'),
    '</table>', '</table></div>'
  )
WHERE category_id = 415 AND description LIKE '%<table class=%' AND description NOT LIKE '%table-responsive%';

-- Категория: ochistiteli-stekol (418)
UPDATE oc_category_description SET
  description = REPLACE(
    REPLACE(description, '<table class=\"table', '<div class=\"table-responsive\"><table class=\"table'),
    '</table>', '</table></div>'
  )
WHERE category_id = 418 AND description LIKE '%<table class=%' AND description NOT LIKE '%table-responsive%';

-- Категория: ochistiteli-diskov (419)
UPDATE oc_category_description SET
  description = REPLACE(
    REPLACE(description, '<table class=\"table', '<div class=\"table-responsive\"><table class=\"table'),
    '</table>', '</table></div>'
  )
WHERE category_id = 419 AND description LIKE '%<table class=%' AND description NOT LIKE '%table-responsive%';

-- Категория: ochistiteli-shin (420)
UPDATE oc_category_description SET
  description = REPLACE(
    REPLACE(description, '<table class=\"table', '<div class=\"table-responsive\"><table class=\"table'),
    '</table>', '</table></div>'
  )
WHERE category_id = 420 AND description LIKE '%<table class=%' AND description NOT LIKE '%table-responsive%';

-- Категория: cherniteli-shin (421)
UPDATE oc_category_description SET
  description = REPLACE(
    REPLACE(description, '<table class=\"table', '<div class=\"table-responsive\"><table class=\"table'),
    '</table>', '</table></div>'
  )
WHERE category_id = 421 AND description LIKE '%<table class=%' AND description NOT LIKE '%table-responsive%';

-- Категория: glina-i-avtoskraby (423)
UPDATE oc_category_description SET
  description = REPLACE(
    REPLACE(description, '<table class=\"table', '<div class=\"table-responsive\"><table class=\"table'),
    '</table>', '</table></div>'
  )
WHERE category_id = 423 AND description LIKE '%<table class=%' AND description NOT LIKE '%table-responsive%';

-- Проверка результата
SELECT category_id, language_id,
  CASE WHEN description LIKE '%table-responsive%' THEN '✅ Responsive' ELSE '❌ Not fixed' END as status
FROM oc_category_description
WHERE category_id IN (412, 415, 418, 419, 420, 421, 423)
ORDER BY category_id, language_id;
