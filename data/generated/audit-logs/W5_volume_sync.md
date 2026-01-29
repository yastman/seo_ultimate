# W5 Volume Sync Log

**Worker:** W5
**Дата:** 2026-01-29
**Категории:** polirovka (6 файлов)

---

## polirovka
- Проверено keywords: 3
- Проверено synonyms: 5
- **Обновлено: 0 ключей**
- Без изменений: 8 ключей (все volume совпадают с master)

## polirovalnye-krugi
- **Категория отсутствует в master CSV**
- Keywords в JSON: 5
- Synonyms в JSON: 28
- Обновлено: 0 ключей (нет данных в master для сравнения)

## mekhovye
- Проверено keywords: 2
- Проверено synonyms: 6
- **Обновлено: 0 ключей**
- Без изменений: 8 ключей (все volume совпадают с master)

## polirovalnye-mashinki
- **Категория отсутствует в master CSV**
- Keywords в JSON: 10
- Synonyms в JSON: 29
- Обновлено: 0 ключей (нет данных в master для сравнения)

## akkumulyatornaya
- Проверено keywords: 3
- Проверено synonyms: 5
- **Обновлено: 0 ключей**
- Без изменений: 8 ключей (все volume совпадают с master)

## polirovalnye-pasty
- Проверено keywords: 9
- Проверено synonyms: 24
- **Обновлено: 0 ключей**
- Ключи в master (polirovalnye-pasty): 18
- Все совпадающие ключи имеют корректный volume

---

## Итого

| Метрика | Значение |
|---------|----------|
| Файлов проверено | 6 |
| Категорий в master | 4 (polirovka, mekhovye, akkumulyatornaya, polirovalnye-pasty) |
| Категорий НЕ в master | 2 (polirovalnye-krugi, polirovalnye-mashinki) |
| Ключей обновлено | **0** |
| Ключей совпадает | 42 |

**Статус:** ✅ Все volume уже синхронизированы, изменения не требуются.

---

## Примечания

1. Категории `polirovalnye-krugi` и `polirovalnye-mashinki` полностью отсутствуют в `ru_semantics_master.csv` — их ключи не были импортированы или собраны.

2. Некоторые ключи из JSON (например "пасты для полировки авто" volume=1000) находятся в master с category=`uncategorized`. По правилам задачи синхронизация выполняется только для ключей той же категории, поэтому эти ключи не обновлялись.
