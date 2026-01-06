-- Add comparison table to ochistiteli-stekol UK (category_id=418, language_id=1)
UPDATE oc_category_description SET
description = REPLACE(description,
'<h2>Який склад обрати</h2>\n\n<p>Вибір залежить від наявності тонування, типу забруднень і бажаного ефекту.</p>\n\n<h3>',
'<h2>Який склад обрати</h2>

<p>Вибір залежить від наявності тонування, типу забруднень і бажаного ефекту.</p>

<table class="table table-bordered">
<thead><tr><th>Тип</th><th>Основа</th><th>Призначення</th><th>Тонування</th><th>Антидощ</th></tr></thead>
<tbody>
<tr><td>Спиртовий</td><td>Ізопропіловий спирт</td><td>Жир, масляна плівка</td><td>Безпечно</td><td>Може змити</td></tr>
<tr><td>Безспиртовий (Tint Safe)</td><td>Вода + ПАР</td><td>Пил, відбитки</td><td>Безпечно</td><td>Безпечно</td></tr>
<tr><td>З гідрофобом (2-в-1)</td><td>Спирт + полімер</td><td>Очищення + захист</td><td>Безпечно</td><td>Оновлює</td></tr>
<tr><td>Концентрат</td><td>Розбавляємий 1:3–1:10</td><td>Профі-формат</td><td>Залежить від типу</td><td>Залежить від типу</td></tr>
</tbody>
</table>

<h3>')
WHERE category_id = 418 AND language_id = 1;
