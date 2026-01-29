# W5 Semantic Cluster Log

**Дата:** 2026-01-29
**Worker:** W5
**Категорії:** 45-53 (9 категорій)

---

## Підсумок

| Категорія | До (kw/syn) | Після (kw/syn) | Зміни |
|-----------|-------------|----------------|-------|
| sredstva-dlya-kozhi | 1/13 | 7/8 | +6 keywords |
| tverdyy-vosk | 2/7 | 3/8 | +1 keyword |
| ukhod-za-intererom | 2/7 | 5/5 | +3 keywords |
| ukhod-za-kozhey | 2/22 | 8/16 | +6 keywords |
| ukhod-za-naruzhnym-plastikom | 1/4 | 4/2 | +3 keywords |
| vedra-i-emkosti | 2/4 | 4/4 | +2 keywords |
| voski | 4/7 | 7/5 | +3 keywords |
| zashchitnye-pokrytiya | 3/2 | 3/2 | без змін |
| zhidkiy-vosk | 2/9 | 5/8 | +3 keywords |

**Всього:** +27 нових унікальних інтентів перенесено в keywords

---

## Детальний аналіз по категоріях

### 1. sredstva-dlya-kozhi

**Шлях:** `categories/ukhod-za-intererom/sredstva-dlya-kozhi/`

**Нові keywords (унікальні інтенти):**
- полироль для кожи автомобиля (50) — ІНШЕ СЛОВО
- химия для кожи авто (50) — ІНШЕ СЛОВО
- крем для кожи автомобиля (40) — ІНШЕ СЛОВО
- средство для кожаного салона (40) — +контекст "кожаный салон"
- средство для чистки кожаного салона авто (30) — +сценарій "чистка"
- автокосметика для кожи (10) — ІНШЕ СЛОВО

**Логіка:** "полироль", "химия", "крем", "автокосметика" — різні типи продуктів, кожен має свій пошуковий інтент.

---

### 2. tverdyy-vosk

**Шлях:** `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/`

**Нові keywords:**
- твёрдый воск для полировки авто (10) — +сценарій "полировка"

**Логіка:** Мінімальні зміни, категорія вже добре структурована. Додано лише сценарій застосування.

---

### 3. ukhod-za-intererom

**Шлях:** `categories/ukhod-za-intererom/`

**Нові keywords:**
- химчистка салона авто (320) — ІНШЕ СЛОВО, вищий volume!
- автохимия для салона (30) — ІНШЕ СЛОВО
- автокосметика для салона (10) — ІНШЕ СЛОВО

**Логіка:** "химчистка" — головний пошуковий запит (320), перенесено з synonyms в primary.

---

### 4. ukhod-za-kozhey

**Шлях:** `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/`

**Нові keywords:**
- полироль для кожи (170) — ІНШЕ СЛОВО
- средство по уходу за кожей авто (90) — варіант формулювання
- полироль для кожи авто (90) — +модифікатор "авто"
- крем для кожи авто (70) — ІНШЕ СЛОВО
- набор для ухода за кожей авто (30) — +тип продукту "набор"
- уход за кожей салона авто (20) — +контекст "салон"

**Логіка:** Очищено variations[], перенесено унікальні інтенти в keywords.

---

### 5. ukhod-za-naruzhnym-plastikom

**Шлях:** `categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/`

**Нові keywords:**
- восстановитель пластика авто (10) — ІНШЕ СЛОВО
- чернитель для наружного пластика (10) — ІНШЕ СЛОВО
- уход за бамперами (10) — ІНШИЙ СЦЕНАРІЙ

**Логіка:** "полироль", "восстановитель", "чернитель" — різні типи продуктів.

---

### 6. vedra-i-emkosti

**Шлях:** `categories/aksessuary/vedra-i-emkosti/`

**Нові keywords:**
- ведро с сеткой для мойки (10) — +модифікатор "с сеткой"
- профессиональное ведро для мойки (10) — +модифікатор "профессиональное"

**Логіка:** Видалено variations[], перенесено унікальні інтенти.

---

### 7. voski

**Шлях:** `categories/zashchitnye-pokrytiya/voski/`

**Нові keywords:**
- воск для мойки авто (70) — +сценарій "мойка"
- воск для кузова авто (50) — +контекст "кузов"
- восковый полироль для авто (50) — ІНШЕ СЛОВО

**Логіка:** Додано сценарії застосування воску.

---

### 8. zashchitnye-pokrytiya

**Шлях:** `categories/zashchitnye-pokrytiya/`

**Без змін.** Батьківська категорія, семантика адекватна.

---

### 9. zhidkiy-vosk

**Шлях:** `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/`

**Нові keywords:**
- жидкий воск для кузова (10) — +контекст "кузов"
- жидкий воск для мойки авто (10) — +сценарій "мойка"
- жидкий воск для автомойки (10) — +сценарій "автомойка"

**Логіка:** Додано різні сценарії застосування жидкого воску.

---

## Оновлені файли

### _clean.json (8 файлів)
1. `categories/ukhod-za-intererom/sredstva-dlya-kozhi/data/sredstva-dlya-kozhi_clean.json`
2. `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/data/tverdyy-vosk_clean.json`
3. `categories/ukhod-za-intererom/data/ukhod-za-intererom_clean.json`
4. `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/data/ukhod-za-kozhey_clean.json`
5. `categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/data/ukhod-za-naruzhnym-plastikom_clean.json`
6. `categories/aksessuary/vedra-i-emkosti/data/vedra-i-emkosti_clean.json`
7. `categories/zashchitnye-pokrytiya/voski/data/voski_clean.json`
8. `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/data/zhidkiy-vosk_clean.json`

### _meta.json (9 файлів)
1. `categories/ukhod-za-intererom/sredstva-dlya-kozhi/meta/sredstva-dlya-kozhi_meta.json`
2. `categories/zashchitnye-pokrytiya/voski/tverdyy-vosk/meta/tverdyy-vosk_meta.json`
3. `categories/ukhod-za-intererom/meta/ukhod-za-intererom_meta.json`
4. `categories/ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey/meta/ukhod-za-kozhey_meta.json`
5. `categories/moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom/meta/ukhod-za-naruzhnym-plastikom_meta.json`
6. `categories/aksessuary/vedra-i-emkosti/meta/vedra-i-emkosti_meta.json`
7. `categories/zashchitnye-pokrytiya/voski/meta/voski_meta.json`
8. `categories/zashchitnye-pokrytiya/meta/zashchitnye-pokrytiya_meta.json`
9. `categories/zashchitnye-pokrytiya/voski/zhidkiy-vosk/meta/zhidkiy-vosk_meta.json`

---

## Принципи кластеризації

1. **ІНШЕ СЛОВО** → keywords (полироль vs крем vs химия)
2. **ІНШИЙ СЦЕНАРІЙ** → keywords (для мойки vs для полировки)
3. **+контекст** → keywords (для салона vs для кузова)
4. **+тип продукту** → keywords (набор vs средство)
5. **Словоформи** → synonyms з variant_of (авто/автомобіль/машина)
6. **Комерційні** → synonyms з meta_only (купить X, X цена)

---

**Worker W5 completed.**
**НЕ коммічено — очікує оркестратора.**
