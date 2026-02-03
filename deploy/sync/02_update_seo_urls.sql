-- deploy/sync/02_update_seo_urls.sql
-- Обновление SEO URL на наши slug'и (ТОЛЬКО RU, UK не трогаем)

-- Активная пена (415)
UPDATE oc_seo_url SET keyword = 'aktivnaya-pena' WHERE query = 'category_id=415' AND language_id = 3;

-- Шампуни для ручной мойки (412)
UPDATE oc_seo_url SET keyword = 'shampuni-dlya-ruchnoy-moyki' WHERE query = 'category_id=412' AND language_id = 3;

-- Автошампуни (469)
UPDATE oc_seo_url SET keyword = 'avtoshampuni' WHERE query = 'category_id=469' AND language_id = 3;

-- Мойка и Экстерьер (468)
UPDATE oc_seo_url SET keyword = 'moyka-i-eksterer' WHERE query = 'category_id=468' AND language_id = 3;

-- Очистители стекол (418)
UPDATE oc_seo_url SET keyword = 'ochistiteli-stekol' WHERE query = 'category_id=418' AND language_id = 3;

-- Средства для стекол (470)
UPDATE oc_seo_url SET keyword = 'sredstva-dlya-stekol' WHERE query = 'category_id=470' AND language_id = 3;

-- Омыватель (424)
UPDATE oc_seo_url SET keyword = 'omyvatel' WHERE query = 'category_id=424' AND language_id = 3;

-- Антидождь (473)
UPDATE oc_seo_url SET keyword = 'antidozhd' WHERE query = 'category_id=473' AND language_id = 3;

-- Глина и автоскрабы (423)
UPDATE oc_seo_url SET keyword = 'glina-i-avtoskraby' WHERE query = 'category_id=423' AND language_id = 3;

-- Очистители кузова (471)
UPDATE oc_seo_url SET keyword = 'ochistiteli-kuzova' WHERE query = 'category_id=471' AND language_id = 3;

-- Антимошка (474)
UPDATE oc_seo_url SET keyword = 'antimoshka' WHERE query = 'category_id=474' AND language_id = 3;

-- Антибитум (475)
UPDATE oc_seo_url SET keyword = 'antibitum' WHERE query = 'category_id=475' AND language_id = 3;

-- Очистители двигателя (422)
UPDATE oc_seo_url SET keyword = 'ochistiteli-dvigatelya' WHERE query = 'category_id=422' AND language_id = 3;

-- Чернители шин (421)
UPDATE oc_seo_url SET keyword = 'cherniteli-shin' WHERE query = 'category_id=421' AND language_id = 3;

-- Очистители дисков (419)
UPDATE oc_seo_url SET keyword = 'ochistiteli-diskov' WHERE query = 'category_id=419' AND language_id = 3;

-- Очистители шин (420)
UPDATE oc_seo_url SET keyword = 'ochistiteli-shin' WHERE query = 'category_id=420' AND language_id = 3;

-- Средства для дисков и шин (472)
UPDATE oc_seo_url SET keyword = 'sredstva-dlya-diskov-i-shin' WHERE query = 'category_id=472' AND language_id = 3;

-- Уход за интерьером (425)
UPDATE oc_seo_url SET keyword = 'ukhod-za-intererom' WHERE query = 'category_id=425' AND language_id = 3;

-- Средства для химчистки салона (427)
UPDATE oc_seo_url SET keyword = 'sredstva-dlya-khimchistki-salona' WHERE query = 'category_id=427' AND language_id = 3;

-- Средства для кожи (428)
UPDATE oc_seo_url SET keyword = 'sredstva-dlya-kozhi' WHERE query = 'category_id=428' AND language_id = 3;

-- Полироли для пластика (429)
UPDATE oc_seo_url SET keyword = 'poliroli-dlya-plastika' WHERE query = 'category_id=429' AND language_id = 3;

-- Нейтрализаторы запаха (431)
UPDATE oc_seo_url SET keyword = 'neytralizatory-zapakha' WHERE query = 'category_id=431' AND language_id = 3;

-- Пятновыводители (434)
UPDATE oc_seo_url SET keyword = 'pyatnovyvoditeli' WHERE query = 'category_id=434' AND language_id = 3;

-- Защитные покрытия (435)
UPDATE oc_seo_url SET keyword = 'zashchitnye-pokrytiya' WHERE query = 'category_id=435' AND language_id = 3;

-- Твердый воск (437)
UPDATE oc_seo_url SET keyword = 'tverdyy-vosk' WHERE query = 'category_id=437' AND language_id = 3;

-- Жидкий воск (456)
UPDATE oc_seo_url SET keyword = 'zhidkiy-vosk' WHERE query = 'category_id=456' AND language_id = 3;

-- Керамика и жидкое стекло (439)
UPDATE oc_seo_url SET keyword = 'keramika-i-zhidkoe-steklo' WHERE query = 'category_id=439' AND language_id = 3;

-- Квик-детейлеры (436)
UPDATE oc_seo_url SET keyword = 'kvik-deteylery' WHERE query = 'category_id=436' AND language_id = 3;

-- Силанты (438)
UPDATE oc_seo_url SET keyword = 'silanty' WHERE query = 'category_id=438' AND language_id = 3;

-- Аксессуары (445)
UPDATE oc_seo_url SET keyword = 'aksessuary' WHERE query = 'category_id=445' AND language_id = 3;

-- Микрофибра и тряпки (446)
UPDATE oc_seo_url SET keyword = 'mikrofibra-i-tryapki' WHERE query = 'category_id=446' AND language_id = 3;

-- Распылители и пенники (447)
UPDATE oc_seo_url SET keyword = 'raspyliteli-i-penniki' WHERE query = 'category_id=447' AND language_id = 3;

-- Ведра и емкости (448)
UPDATE oc_seo_url SET keyword = 'vedra-i-emkosti' WHERE query = 'category_id=448' AND language_id = 3;

-- Губки и варежки (453)
UPDATE oc_seo_url SET keyword = 'gubki-i-varezhki' WHERE query = 'category_id=453' AND language_id = 3;

-- Малярный скотч (454)
UPDATE oc_seo_url SET keyword = 'malyarniy-skotch' WHERE query = 'category_id=454' AND language_id = 3;

-- Наборы (466)
UPDATE oc_seo_url SET keyword = 'nabory' WHERE query = 'category_id=466' AND language_id = 3;

-- Полировка (457)
UPDATE oc_seo_url SET keyword = 'polirovka' WHERE query = 'category_id=457' AND language_id = 3;

-- Полировальные пасты (458)
UPDATE oc_seo_url SET keyword = 'polirovalnye-pasty' WHERE query = 'category_id=458' AND language_id = 3;

-- Полировальные круги (459)
UPDATE oc_seo_url SET keyword = 'polirovalnye-krugi' WHERE query = 'category_id=459' AND language_id = 3;

-- Полировальные машинки (461)
UPDATE oc_seo_url SET keyword = 'polirovalnye-mashinki' WHERE query = 'category_id=461' AND language_id = 3;

-- Оборудование (462)
UPDATE oc_seo_url SET keyword = 'oborudovanie' WHERE query = 'category_id=462' AND language_id = 3;

-- Аппараты Tornador (463)
UPDATE oc_seo_url SET keyword = 'apparaty-tornador' WHERE query = 'category_id=463' AND language_id = 3;
