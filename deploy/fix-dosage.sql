-- Fix dosage in dlya-ruchnoy-moyki RU (category_id=412, language_id=3)
UPDATE oc_category_description SET
description = REPLACE(description,
'Разведите шампунь для мойки кузова авто в ведре (20–50 мл на 10 л воды).',
'Разведите шампунь для мойки кузова авто в ведре согласно инструкции производителя (дозировка зависит от концентрации).')
WHERE category_id = 412 AND language_id = 3;

-- Fix dosage in dlya-ruchnoy-moyki UK (category_id=412, language_id=1)
UPDATE oc_category_description SET
description = REPLACE(description,
'Розведіть шампунь для миття кузова авто у відрі (20–50 мл на 10 л води).',
'Розведіть шампунь для миття кузова авто у відрі згідно з інструкцією виробника (дозування залежить від концентрації).')
WHERE category_id = 412 AND language_id = 1;

-- Fix FAQ answer in UK (category_id=412, language_id=1)
UPDATE oc_category_description SET
description = REPLACE(description,
'<p>20–50 мл на 10 л води. Більше — не означає чистіше. Занадто багато шампуню залишає плівку на кузові та ускладнює сушіння.</p>',
'<p>Дозування залежить від концентрації — дивіться інструкцію виробника. Більше — не означає чистіше. Занадто багато шампуню залишає плівку на кузові та ускладнює сушіння.</p>')
WHERE category_id = 412 AND language_id = 1;
