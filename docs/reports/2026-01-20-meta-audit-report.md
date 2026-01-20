# SEO Meta Audit Report

**Дата:** 2026-01-20
**Метод:** Ручной аудит через субагентов
**Проверено категорий:** 49

---

## Сводка результатов

| Статус | Количество | % |
|--------|-----------|---|
| PASS | 23 | 47% |
| WARNING | 15 | 31% |
| FAIL | 11 | 22% |

---

## Результаты по батчам

| Батч | Раздел | Категорий | PASS | FAIL | WARNING |
|------|--------|-----------|------|------|---------|
| 1 | aksessuary | 10 | 7 | 3 | 0 |
| 2 | avtoshampuni | 4 | 3 | 0 | 1 |
| 3 | ochistiteli-kuzova | 5 | 4 | 0 | 1 |
| 4 | sredstva-dlya-diskov-i-shin | 5 | 5 | 0 | 0 |
| 5 | sredstva-dlya-stekol | 4 | 4 | 0 | 0 |
| 6 | zashchitnye-pokrytiya | 7 | 0 | 1 | 6 |
| 7 | ukhod-za-intererom | 7 | 0 | 0 | 7 |
| 8 | polirovka + oborudovanie + opt | 7 | 0 | 7 | 0 |
| **Итого** | | **49** | **23** | **11** | **15** |

---

## Критические проблемы (FAIL) — 11 категорий

### IRON RULE нарушения (используется не primary_keyword)

| Категория | Текущий | Должен быть (primary_keyword) |
|-----------|---------|-------------------------------|
| kvik-deteylery | "полимер для авто" | "холодный воск для автомобиля" |

### Неправильный Description pattern (Shop вместо Producer или наоборот)

| Категория | Текущий pattern | Должен быть |
|-----------|-----------------|-------------|
| aksessuary-dlya-naneseniya-sredstv | Shop | Producer |
| mikrofibra-i-tryapki | Shop | Producer |
| nabory | Shop | Producer |
| mekhovye | Producer | Shop |
| akkumulyatornaya | Producer | Shop |

### Неправильный Title format

| Категория | Проблема |
|-----------|----------|
| polirovka | "— купить в интернет-магазине" |
| polirovalnye-pasty | "— купить в интернет-магазине" |
| oborudovanie | "— купить, цены |" |
| apparaty-tornador | "— купить в интернет-магазине" |
| opt-i-b2b | "— купить, цены |" |

---

## Предупреждения (WARNING) — 15 категорий

### Нестандартный Title format

Массовая проблема: вместо `{keyword} купить | Ultimate` используются варианты:
- `{keyword} — купить, цены | Ultimate`
- `{keyword} — купить в интернет-магазине Ultimate`

**Затронутые категории:**
1. avtoshampuni (morph: "Автошампуни" vs "автошампунь")
2. ukhod-za-naruzhnym-plastikom (Title 66 chars)
3. zashchitnye-pokrytiya
4. keramika-i-zhidkoe-steklo
5. silanty
6. voski
7. tverdyy-vosk
8. zhidkiy-vosk
9. ukhod-za-intererom
10. poliroli-dlya-plastika
11. pyatnovyvoditeli
12. neytralizatory-zapakha
13. sredstva-dlya-khimchistki-salona
14. ochistiteli-kozhi
15. ukhod-za-kozhey

---

## Рекомендации

### Приоритет 1: Исправить FAIL (11 категорий)

1. **kvik-deteylery** — заменить "полимер для авто" на "холодный воск для автомобиля" во всех полях
2. **aksessuary-dlya-naneseniya-sredstv, mikrofibra-i-tryapki, nabory** — изменить Description на Producer pattern
3. **mekhovye, akkumulyatornaya** — изменить Description на Shop pattern
4. **polirovka, polirovalnye-pasty, oborudovanie, apparaty-tornador, opt-i-b2b** — унифицировать Title format

### Приоритет 2: Унифицировать Title format (15 WARNING)

Все Title должны соответствовать формату:
```
{primary_keyword} купить | Ultimate
```

### Приоритет 3: Проверить отсутствующие категории

Не найдены meta-файлы для:
- polirovalnye-krugi (родительская)
- polirovalnye-mashinki (родительская)

---

## Исправленные JSON для FAIL категорий

### kvik-deteylery
```json
{
  "meta": {
    "title": "Холодный воск для автомобиля купить | Ultimate",
    "description": "Холодный воск для автомобиля от производителя Ultimate. Горячий воск, быстрый воск, квик-детейлеры. Опт и розница."
  },
  "h1": "Холодный воск для автомобиля"
}
```

### aksessuary-dlya-naneseniya-sredstv
```json
{
  "meta": {
    "description": "Аксессуары для нанесения средств от производителя Ultimate. Аппликаторы, губки, пады. Опт и розница."
  }
}
```

### mikrofibra-i-tryapki
```json
{
  "meta": {
    "description": "Микрофибра для авто от производителя Ultimate. Салфетки, полотенца, вафельные тряпки. Опт и розница."
  }
}
```

### nabory
```json
{
  "meta": {
    "description": "Наборы автохимии от производителя Ultimate. Комплекты для мойки, полировки, ухода за салоном. Опт и розница."
  }
}
```

### mekhovye
```json
{
  "meta": {
    "title": "Шерстяной круг для полировки купить | Ultimate",
    "description": "Шерстяной круг для полировки в интернет-магазине Ultimate. Натуральная и синтетическая шерсть, диаметр 125-150мм."
  }
}
```

### akkumulyatornaya
```json
{
  "meta": {
    "title": "Аккумуляторная полировальная машина купить | Ultimate",
    "description": "Аккумуляторная полировальная машина в интернет-магазине Ultimate. Эксцентриковые машинки на аккумуляторе."
  }
}
```

### polirovka
```json
{
  "meta": {
    "title": "Полировка авто купить | Ultimate"
  }
}
```

### polirovalnye-pasty
```json
{
  "meta": {
    "title": "Полировочная паста купить | Ultimate"
  }
}
```

### oborudovanie
```json
{
  "meta": {
    "title": "Оборудование для химчистки авто купить | Ultimate"
  }
}
```

### apparaty-tornador
```json
{
  "meta": {
    "title": "Торнадор купить | Ultimate"
  }
}
```

### opt-i-b2b
```json
{
  "meta": {
    "title": "Автохимия от производителя купить | Ultimate"
  }
}
```

---

## Статус аудита

- [x] Batch 1: aksessuary (10 категорий)
- [x] Batch 2: avtoshampuni (4 категории)
- [x] Batch 3: ochistiteli-kuzova (5 категорий)
- [x] Batch 4: sredstva-dlya-diskov-i-shin (5 категорий)
- [x] Batch 5: sredstva-dlya-stekol (4 категории)
- [x] Batch 6: zashchitnye-pokrytiya (7 категорий)
- [x] Batch 7: ukhod-za-intererom (7 категорий)
- [x] Batch 8: polirovka + oborudovanie + opt (7 категорий)

**Аудит завершён: 49/49 категорий проверено**
