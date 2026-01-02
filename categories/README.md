# Categories Data Structure

**[← Назад в корень](../README.md)**


Каждая папка здесь представляет одну категорию товаров.
Slug папки совпадает с URL на сайте.

## Структура папки категории:

*   `data/{slug}_clean.json`: **Очищенные ключевые слова** (семантическое ядро).
*   `meta/{slug}_meta.json`: **Мета-теги** (Title, Description, H1, UTP, Template).
*   `content/{slug}_ru.md`: **Текст категории** на русском языке.
*   `research/RESEARCH_DATA.md`: **SEO исследование** (конкуренты, структура, интент).

## UK версия

Украинские версии находятся в параллельной структуре (root/uk): `uk/categories/{slug}/`.

*   `uk/categories/{slug}/content/{slug}_uk.md`: Текст на украинском.
*   `uk/categories/{slug}/meta/{slug}_meta.json`: Мета-теги на украинском.

## Связанные скрипты

*   `scripts/analyze_category.py`: Проверка наличия всех файлов в категории.
*   `scripts/generate_sql.py`: Сборка данных из папок в SQL для деплоя.
