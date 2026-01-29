# W4 Semantic Cluster Log

Дата: 2026-01-29

Категории: polirovka + ukhod-za-intererom (11 категорий)

---

## polirovka/polirovalnye-krugi
- Перенесено в synonyms з variant_of: 1 ключ ("полировочные круги")
- Видалено дублів: 2 (круги для полировальной машины/машинки)
- Додано variant_of до: 9 ключів
- Canonical: "полировальные круги", "диск для полировки авто", "круги для полировальной машины", "круг полировальный на липучке"

## polirovka/polirovalnye-krugi/mekhovye
- Додано variant_of до: 3 ключів
- Canonical: "шерстяной круг для полировки", "меховой круг для полировки"
- Примітка: шерстяной/меховой — синоніми, обидва canonical

## polirovka/polirovalnye-mashinki
- Перенесено з keywords в synonyms: 6 ключів
- Додано variant_of до: 15 ключів
- Canonical: "полировочная машинка" (8100), "полировальная машина для автомобиля", "машинка для полировки авто", "машинка для полировки"
- Кластери: машинка/машина, авто/автомобиля, полировочная/полировальная

## polirovka/polirovalnye-mashinki/akkumulyatornaya
- Перенесено з keywords в synonyms: 2 ключі
- Додано variant_of до: 6 ключів
- Canonical: "аккумуляторная полировальная машина" (260)
- Кластер: всі варіанти = один інтент (аккум машинка)

## polirovka/polirovalnye-pasty
- Перенесено з keywords в synonyms: 3 ключі
- Додано variant_of до: 14 ключів
- Видалено variations (перенесено в synonyms)
- Canonical: "полировочная паста" (1600), "пасты для полировки авто" (1000), "полировальная паста для автомобиля", "паста для полировки", "паста для полировки кузова"
- Кластери: полировочная/полировальная, авто/автомобиля/машины, кузов variants

## ukhod-za-intererom
- Перенесено variations в synonyms: 1 ключ
- Додано variant_of до: 4 ключів
- Canonical: "уход за салоном авто", "химчистка салона авто", "автохимия для салона"
- Кластери: авто/автомобиля/машины, химчистка/чистка

## ukhod-za-intererom/neytralizatory-zapakha
- Перенесено з keywords в synonyms: 1 ключ ("нейтрализатор запаха в авто")
- Додано "устранитель запаха" в keywords
- Видалено variations (перенесено в synonyms)
- Додано variant_of до: 16 ключів
- Canonical: "нейтрализатор запаха в автомобиле", "поглотитель запаха", "устранитель запаха", "нейтрализатор запахов в салоне авто"
- Кластери: авто/автомобиля/машину, нейтрализатор/поглотитель/устранитель

## ukhod-za-intererom/poliroli-dlya-plastika
- Перенесено з keywords в synonyms: 1 ключ
- Видалено variations (перенесено в synonyms)
- Додано variant_of до: 10 ключів
- Canonical: "полироль для торпеды", "полироль для панели авто", "полироль для пластика автомобиля", "средство для ухода за пластиком авто"
- Кластери: торпеды/торпедо, авто/автомобиля, панели/салона

## ukhod-za-intererom/pyatnovyvoditeli
- Видалено variations (перенесено в synonyms)
- Додано variant_of до: 3 ключі
- Canonical: "пятновыводитель" (2400), "пятновыводитель для авто", "пятновыводитель для салона авто"
- Кластери: авто/автомобіля/машини

## ukhod-za-intererom/sredstva-dlya-khimchistki-salona
- Перенесено з keywords в synonyms: 5 ключів (автомобіля variants)
- Видалено variations (перенесено в synonyms)
- Додано variant_of до: 32 ключів
- Canonical: "химия для чистки салона", "химия для химчистки авто", "средство для чистки салона авто", "химия для салона авто", "средство для химчистки салона авто", "очиститель салона автомобиля"
- Кластери: авто/автомобіля/машини, химчистка/чистка/очиститель

## ukhod-za-intererom/sredstva-dlya-kozhi
- Перенесено з keywords в synonyms: 1 ключ
- Видалено variations (перенесено в synonyms)
- Видалено дубль з variations: "средства для кожи авто"
- Додано variant_of до: 7 ключів
- Canonical: "средство для кожи авто" (280)
- Кластери: авто/автомобіля, салона variants

---

## Итог Semantic Cluster (session 3)

- **Обработано категорий:** 11
- **Всего variant_of добавлено:** ~120 ключей
- **Перенесено из keywords в synonyms:** ~20 ключей
- **Удалено variations:** 8 файлов (перенесено в synonyms)
- **Валидация meta:** PASS (polirovka, ukhod-za-intererom)

**Типичные кластеры:**
- авто/автомобіля/машини
- полировочная/полировальная
- машинка/машина
- химчистка/чистка
- торпеды/торпедо

**НЕ КОММИТИТЬ — коммиты делает оркестратор**

---

# W4 Code Review Fixes (2026-01-29 session 2)

Задачи: Tasks 7, 9, 10 из docs/plans/2026-01-29-code-review-fixes-plan.md

---

## Task 7: Fix ruff auto-fixable lint errors ✅

**Файлы:**
- `scripts/compare_with_master.py` — B007: переименовано `key` → `_key` (unused loop variable)
- `tests/unit/test_audit_keyword_consistency.py` — F401: удалён неиспользуемый импорт `MagicMock, patch`
- `tests/unit/test_validate_uk.py` — F401: удалены неиспользуемые импорты `os`, `patch`

**Верификация:** `ruff check` → All checks passed!

---

## Task 9: Remove duplicate pytest config from pyproject.toml ✅

**Изменения:**
- Удалена секция `[tool.pytest.ini_options]` (строки 1-9)
- pytest.ini теперь единственный источник конфигурации pytest

**Верификация:** `pytest --collect-only` → configfile: pytest.ini, collected 330 items

---

## Task 10: Add ruff extend-exclude for non-project directories ✅

**Изменения в pyproject.toml:**
```toml
extend-exclude = [".github_repos", ".claude", "archive"]
```

**Верификация:** `ruff check .` → All checks passed!

---

**Итог:** 3 задачи выполнены. Коммиты НЕ созданы (делает оркестратор).

---

# W4 Keywords Coverage Audit (2026-01-29 session 3)

**Task:** Content review for 18 categories (keywords coverage check)

## Progress

| # | Category | Status | Notes |
|---|----------|--------|-------|
| 1 | moyka-i-eksterer/sredstva-dlya-stekol | SKIP | Зонтичная категория без контента |
| 2 | moyka-i-eksterer/avtoshampuni/aktivnaya-pena | ✅ PASS | Референсный текст, 8/8 keywords |
| 3 | moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki | ✅ PASS | 8/8 keywords |
| 4 | moyka-i-eksterer/ochistiteli-kuzova/antibitum | ✅ PASS | Референсный текст, 5/5 keywords |
| 5 | moyka-i-eksterer/ochistiteli-kuzova/antimoshka | ✅ PASS | 6/6 keywords |
| 6 | moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby | ✅ FIXED | +2 keywords |
| 7 | moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli | ✅ FIXED | +1 keyword |
| 8 | moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom | ✅ PASS | 10/10 keywords |
| 9 | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin | ✅ FIXED | +1 keyword, референс |
| 10 | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov | ✅ FIXED | +2 keywords |
| 11 | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov | ✅ FIXED | +1 keyword |
| 12 | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin | ✅ FIXED | +2 keywords |
| 13 | moyka-i-eksterer/sredstva-dlya-stekol/antidozhd | ✅ PASS | 5/5 keywords |
| 14 | moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol | ✅ PASS | 6/6 keywords |
| 15 | moyka-i-eksterer/sredstva-dlya-stekol/omyvatel | ✅ FIXED | +5 keywords |
| 16 | moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla | ✅ PASS | 6/6 keywords |
| 17 | glavnaya | SKIP | Нет content файла |
| 18 | opt-i-b2b | ✅ FIXED | +2 keywords |

## Summary

- **Проверено:** 18 категорий
- **PASS:** 8 категорий (без исправлений)
- **FIXED:** 8 категорий (добавлены недостающие keywords)
- **SKIP:** 2 категории (зонтичные без контента)

**Всего добавлено keywords:** ~22 ключа (включая падежные исправления)

**Файлы изменены:**
1. `glina-i-avtoskraby_ru.md` — +2 keywords
2. `obezzhirivateli_ru.md` — +1 keyword
3. `cherniteli-shin_ru.md` — +1 keyword
4. `keramika-dlya-diskov_ru.md` — +2 keywords
5. `ochistiteli-diskov_ru.md` — +1 keyword
6. `ochistiteli-shin_ru.md` — +2 keywords
7. `omyvatel_ru.md` — +5 keywords
8. `opt-i-b2b_ru.md` — +2 keywords

**НЕ КОММИТИТЬ — коммиты делает оркестратор**

---

## Detailed Results

### Детальное распределение добавленных ключей

#### 1. glina-i-avtoskraby (+2 keywords)

| Ключ | Группа | Куда добавлен |
|------|--------|---------------|
| очищающая глина для кузова автомобиля | supporting | Intro — заменено "очищающая глина для авто" |
| полимерная глина для авто | supporting | Intro — заменено "глина для кузова автомобиля готовит" → "полимерная глина для авто готовит" |

#### 2. obezzhirivateli (+1 keyword)

| Ключ | Группа | Куда добавлен |
|------|--------|---------------|
| обезжириватель кузова | supporting | Таблица сценариев — добавлена строка "Обезжириватель кузова перед мойкой" |

#### 3. cherniteli-shin (+1 keyword)

| Ключ | Группа | Куда добавлен |
|------|--------|---------------|
| средство для ухода за шинами | supporting | Intro — заменено "для ухода за боковиной" → "средство для ухода за шинами и боковиной" |

#### 4. keramika-dlya-diskov (+2 keywords)

| Ключ | Группа | Куда добавлен |
|------|--------|---------------|
| керамика для колёсных дисков | secondary | H2 — заменено "керамику для дисков" → "керамику для колёсных дисков" |
| защитное покрытие для литых дисков | supporting | Секция сценариев — добавлен новый сценарий |

#### 5. ochistiteli-diskov (+1 keyword)

| Ключ | Группа | Куда добавлен |
|------|--------|---------------|
| средство для очистки дисков | supporting | Сценарии подбора — добавлен пункт "Нужно универсальное средство для очистки дисков" |

#### 6. ochistiteli-shin (+2 keywords)

| Ключ | Группа | Куда добавлен |
|------|--------|---------------|
| средство для очистки резины | supporting | Intro — добавлено предложение в конец |
| очиститель для покрышек | supporting | Intro — добавлено предложение в конец |

#### 7. omyvatel (+5 keywords)

| Ключ | Группа | Куда добавлен |
|------|--------|---------------|
| омыватель стекла летний | secondary | Intro — заменено "состав с усиленными детергентами" → "омыватель стекла летний" |
| омыватель для стекол | supporting | Intro — добавлено предложение |
| омыватель заднего стекла | supporting | Intro — добавлено в предложение выше |
| омыватель стекла антимошка | supporting | Таблица — заменено "Омыватель-антимошка" → "Омыватель стекла антимошка" |
| омыватель для машины | supporting | Таблица — добавлена строка "Универсальный омыватель для машины" |

#### 8. opt-i-b2b (+2 keywords)

| Ключ | Группа | Куда добавлен |
|------|--------|---------------|
| автокосметика оптом | secondary | H2 — заменено "Автохимия оптом" → "Автохимия и автокосметика оптом" |
| химия для автомоек оптом | supporting | Секция оптовых закупок — добавлено предложение |

---

### Итого по группам

| Группа | Добавлено ключей |
|--------|------------------|
| primary | 0 |
| secondary | 3 |
| supporting | 14 |
| **TOTAL** | **17** |

---

### Дополнительные исправления (падежная точность)

После первичной проверки обнаружены ключи в неправильных падежах:

| Категория | Ключ | Проблема | Исправление |
|-----------|------|----------|-------------|
| glina-i-avtoskraby | глина для чистки авто | "глину" vs "глина" | Добавлено предложение с именительным падежом |
| omyvatel | омыватель заднего стекла | "омывателя" vs "омыватель" | Переписано предложение |
| opt-i-b2b | автохимия опт | отсутствовал | Изменён H1 на "Автохимия опт" |
| opt-i-b2b | B2B сотрудничество | отсутствовал | Добавлено предложение после H2 |
| keramika-dlya-diskov | керамика для колёсных дисков | "керамику" vs "керамика" | Добавлено в intro |
| keramika-dlya-diskov | нанокерамика для дисков | "нанокерамики" vs "нанокерамика" | Переписано начало секции |
| keramika-dlya-diskov | защитное покрытие для дисков | выпал при редактировании | Возвращено в intro |
| ochistiteli-diskov | химия для дисков | заменено на "химия для чистки" | Изменён H2 |

**Финальная верификация:** ✅ 100% coverage по всем 8 категориям
