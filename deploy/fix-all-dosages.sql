-- Fix dosages in all categories

-- 1. dlya-ruchnoy-moyki RU (412, lang=3)
UPDATE oc_category_description SET
description = REPLACE(description,
'Разведите шампунь для мойки кузова авто в ведре (20–50 мл на 10 л воды).',
'Разведите шампунь для мойки кузова авто в ведре согласно инструкции производителя (дозировка зависит от концентрации).')
WHERE category_id = 412 AND language_id = 3;

-- 2. dlya-ruchnoy-moyki UK (412, lang=1)
UPDATE oc_category_description SET
description = REPLACE(description,
'Розведіть шампунь для миття кузова авто у відрі (20–50 мл на 10 л води).',
'Розведіть шампунь для миття кузова авто у відрі згідно з інструкцією виробника (дозування залежить від концентрації).')
WHERE category_id = 412 AND language_id = 1;

-- 3. dlya-ruchnoy-moyki UK FAQ (412, lang=1)
UPDATE oc_category_description SET
description = REPLACE(description,
'<p>20–50 мл на 10 л води. Більше — не означає чистіше.',
'<p>Дозування залежить від концентрації — дивіться інструкцію виробника. Більше — не означає чистіше.')
WHERE category_id = 412 AND language_id = 1;

-- 4. aktivnaya-pena RU (415, lang=3) - пенокомплект
UPDATE oc_category_description SET
description = REPLACE(description,
'пропорция 1:10 (100 мл на 1 л воды)',
'разбавляйте согласно инструкции производителя')
WHERE category_id = 415 AND language_id = 3;

-- 5. aktivnaya-pena RU (415, lang=3) - пеногенератор
UPDATE oc_category_description SET
description = REPLACE(description,
'пропорция 1:100–1:200. Бесконтактная химия',
'концентрация зависит от производителя и жёсткости воды — следуйте инструкции. Бесконтактная химия')
WHERE category_id = 415 AND language_id = 3;

-- 6. aktivnaya-pena RU (415, lang=3) - экономия
UPDATE oc_category_description SET
description = REPLACE(description,
'хватит на 40+ моек (30–50 мл на машину)',
'— расход зависит от концентрации, смотрите инструкцию производителя')
WHERE category_id = 415 AND language_id = 3;

-- 7. aktivnaya-pena UK (415, lang=1) - пінокомплект
UPDATE oc_category_description SET
description = REPLACE(description,
'пропорція 1:10 (100 мл на 1 л води)',
'розбавляйте згідно з інструкцією виробника')
WHERE category_id = 415 AND language_id = 1;

-- 8. aktivnaya-pena UK (415, lang=1) - піногенератор
UPDATE oc_category_description SET
description = REPLACE(description,
'пропорція 1:100–1:200. Безконтактна хімія',
'концентрація залежить від виробника та жорсткості води — дотримуйтесь інструкції. Безконтактна хімія')
WHERE category_id = 415 AND language_id = 1;

-- 9. aktivnaya-pena UK (415, lang=1) - пропорції помилка
UPDATE oc_category_description SET
description = REPLACE(description,
'Дотримуйтесь пропорцій: 1:10 для мінімийки, 1:100 для піногенератора.',
'Дотримуйтесь пропорцій згідно з інструкцією виробника.')
WHERE category_id = 415 AND language_id = 1;

-- 10. aktivnaya-pena UK (415, lang=1) - економія
UPDATE oc_category_description SET
description = REPLACE(description,
'вистачить на 40+ миттів (30–50 мл на машину)',
'— витрата залежить від концентрації, дивіться інструкцію виробника')
WHERE category_id = 415 AND language_id = 1;
