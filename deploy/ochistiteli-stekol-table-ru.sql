-- Add comparison table to ochistiteli-stekol RU (category_id=418, language_id=3)
UPDATE oc_category_description SET
description = REPLACE(description,
'<h2>Какой состав выбрать</h2>\n\n<p>Выбор зависит от наличия тонировки, типа загрязнений и желаемого эффекта.</p>\n\n<h3>',
'<h2>Какой состав выбрать</h2>

<p>Выбор зависит от наличия тонировки, типа загрязнений и желаемого эффекта.</p>

<table class="table table-bordered">
<thead><tr><th>Тип</th><th>Основа</th><th>Назначение</th><th>Тонировка</th><th>Антидождь</th></tr></thead>
<tbody>
<tr><td>Спиртовой</td><td>Изопропиловый спирт</td><td>Жир, масляная плёнка</td><td>Безопасно</td><td>Может смыть</td></tr>
<tr><td>Безспиртовой (Tint Safe)</td><td>Вода + ПАВ</td><td>Пыль, отпечатки</td><td>Безопасно</td><td>Безопасно</td></tr>
<tr><td>С гидрофобом (2-в-1)</td><td>Спирт + полимер</td><td>Очистка + защита</td><td>Безопасно</td><td>Обновляет</td></tr>
<tr><td>Концентрат</td><td>Разбавляемый 1:3–1:10</td><td>Профи-формат</td><td>Зависит от типа</td><td>Зависит от типа</td></tr>
</tbody>
</table>

<h3>')
WHERE category_id = 418 AND language_id = 3;
