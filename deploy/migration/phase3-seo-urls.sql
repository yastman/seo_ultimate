-- Phase 3: Update SEO URLs (RU language_id=3)
-- Run: cat deploy/migration/phase3-seo-urls.sql | ult 'sudo mysql -u root -pfr1daYTw1st yastman_test'
SET NAMES utf8mb4;

-- L1 categories
UPDATE oc_seo_url SET keyword = 'ukhod-za-intererom' WHERE query = 'category_id=425' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'zashchitnye-pokrytiya' WHERE query = 'category_id=435' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'polirovka' WHERE query = 'category_id=457' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'oborudovanie' WHERE query = 'category_id=462' AND language_id = 3;

-- L3 under avtoshampuni (469)
UPDATE oc_seo_url SET keyword = 'aktivnaya-pena' WHERE query = 'category_id=415' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'shampuni-dlya-ruchnoy-moyki' WHERE query = 'category_id=412' AND language_id = 3;

-- L3 under sredstva-dlya-stekol (470)
UPDATE oc_seo_url SET keyword = 'ochistiteli-stekol' WHERE query = 'category_id=418' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'omyvatel' WHERE query = 'category_id=424' AND language_id = 3;

-- L3 under ochistiteli-kuzova (471)
UPDATE oc_seo_url SET keyword = 'glina-i-avtoskraby' WHERE query = 'category_id=423' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'obezzhirivateli' WHERE query = 'category_id=426' AND language_id = 3;

-- L2 ochistiteli-dvigatelya (422)
UPDATE oc_seo_url SET keyword = 'ochistiteli-dvigatelya' WHERE query = 'category_id=422' AND language_id = 3;

-- L3 under sredstva-dlya-diskov-i-shin (472)
UPDATE oc_seo_url SET keyword = 'ochistiteli-diskov' WHERE query = 'category_id=419' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'ochistiteli-shin' WHERE query = 'category_id=420' AND language_id = 3;
UPDATE oc_seo_url SET keyword = 'cherniteli-shin' WHERE query = 'category_id=421' AND language_id = 3;

-- Verify
SELECT query, keyword FROM oc_seo_url
WHERE query IN ('category_id=425', 'category_id=435', 'category_id=415', 'category_id=418', 'category_id=419')
AND language_id = 3;
