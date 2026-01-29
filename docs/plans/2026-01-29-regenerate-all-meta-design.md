# Design: Регенерация всех RU мета-тегов

**Дата:** 2026-01-29
**Статус:** Draft

---

## Цель

Регенерировать все 53 мета-файла (`*_meta.json`) для RU категорий по актуальной семантике из `*_clean.json` и правилам `/generate-meta` v16.0.

---

## Контекст

### Почему нужна регенерация
- `primary_keyword` теперь = MAX(volume), не первый в списке
- Семантика обновлялась через `ru_semantics_master.csv`
- Правила generate-meta эволюционировали (Producer vs Shop pattern)

### Исходные данные
- **53 категории** с мета-файлами
- **Скилл:** `/generate-meta` v16.0
- **Валидатор:** `scripts/validate_meta.py`

---

## Архитектура решения

### 4 параллельных воркера

| Воркер | L1 категории | Кол-во |
|--------|--------------|--------|
| W1 | moyka-i-eksterer | 18 |
| W2 | aksessuary, oborudovanie | 12 |
| W3 | ukhod-za-intererom, polirovka | 14 |
| W4 | zashchitnye-pokrytiya, opt-i-b2b, glavnaya | 9 |

### Workflow воркера

```
1. Получить список категорий (slug + path)
2. Для каждой категории:
   a. Читать {slug}_clean.json
   b. Определить primary_keyword = MAX(volume)
   c. Определить тип (Producer/Shop)
   d. Сгенерировать Title/Description/H1 по формулам
   e. Записать {slug}_meta.json
   f. Валидировать: python3 scripts/validate_meta.py {path}
   g. Если FAIL — исправить и повторить
3. Записать лог в data/generated/audit-logs/W{N}_meta_log.md
```

### Формулы (из /generate-meta v16.0)

**Title:**
```
IF len(primary_keyword) <= 20:
  {primary_keyword} — купить в интернет-магазине Ultimate
ELSE:
  {primary_keyword} — купить, цены | Ultimate
```

**H1:**
```
{primary_keyword}
```

**Description (Producer — есть товары Ultimate):**
```
{primary_keyword} от производителя Ultimate. {Типы} — {подробности}. Опт и розница.
```

**Description (Shop — НЕТ товаров Ultimate):**
```
{primary_keyword} в интернет-магазине Ultimate. {Типы} — {подробности}.
```

### Shop-категории (без товаров Ultimate)
```
glina-i-avtoskraby, gubki-i-varezhki, cherniteli-shin,
raspyliteli-i-penniki, vedra-i-emkosti, kisti-dlya-deteylinga,
shchetka-dlya-moyki-avto, shchetki-i-kisti, malyarniy-skotch,
polirovka, polirovalnye-krugi, polirovalnye-mashinki,
oborudovanie, apparaty-tornador
```

---

## Распределение категорий

### W1: moyka-i-eksterer (18)
```
moyka-i-eksterer
moyka-i-eksterer/avtoshampuni
moyka-i-eksterer/avtoshampuni/aktivnaya-pena
moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki
moyka-i-eksterer/ochistiteli-dvigatelya
moyka-i-eksterer/ochistiteli-kuzova/antibitum
moyka-i-eksterer/ochistiteli-kuzova/antimoshka
moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby
moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli
moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin
moyka-i-eksterer/sredstva-dlya-stekol/antidozhd
moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol
moyka-i-eksterer/sredstva-dlya-stekol/omyvatel
moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla
```

### W2: aksessuary + oborudovanie (12)
```
aksessuary
aksessuary/aksessuary-dlya-naneseniya-sredstv
aksessuary/gubki-i-varezhki
aksessuary/malyarniy-skotch
aksessuary/mikrofibra-i-tryapki
aksessuary/nabory
aksessuary/raspyliteli-i-penniki
aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga
aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto
aksessuary/vedra-i-emkosti
oborudovanie
oborudovanie/apparaty-tornador
```

### W3: ukhod-za-intererom + polirovka (14)
```
ukhod-za-intererom
ukhod-za-intererom/neytralizatory-zapakha
ukhod-za-intererom/poliroli-dlya-plastika
ukhod-za-intererom/pyatnovyvoditeli
ukhod-za-intererom/sredstva-dlya-khimchistki-salona
ukhod-za-intererom/sredstva-dlya-kozhi
ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi
ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey
polirovka
polirovka/polirovalnye-krugi
polirovka/polirovalnye-krugi/mekhovye
polirovka/polirovalnye-mashinki
polirovka/polirovalnye-mashinki/akkumulyatornaya
polirovka/polirovalnye-pasty
```

### W4: zashchitnye-pokrytiya + opt-i-b2b + glavnaya (9)
```
zashchitnye-pokrytiya
zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo
zashchitnye-pokrytiya/kvik-deteylery
zashchitnye-pokrytiya/silanty
zashchitnye-pokrytiya/voski
zashchitnye-pokrytiya/voski/tverdyy-vosk
zashchitnye-pokrytiya/voski/zhidkiy-vosk
opt-i-b2b
glavnaya
```

---

## Логи воркеров

Каждый воркер создаёт лог:
```
data/generated/audit-logs/W{N}_meta_log.md
```

### Формат лога
```markdown
# W{N} Meta Regeneration Log

## Статистика
- Обработано: X категорий
- Успешно: Y
- Исправлено после валидации: Z

## Детали по категориям

### {slug}
- primary_keyword: "{keyword}" (volume: {N})
- Тип: Producer/Shop
- Title: {title} ({len} chars)
- Статус: PASS/FIXED

### {slug}
...
```

---

## Команды запуска

### Оркестратор запускает 4 воркера:

```bash
# W1: moyka-i-eksterer (18 категорий)
spawn-claude "W1: Регенерация мета для moyka-i-eksterer.

Выполни /generate-meta для КАЖДОЙ категории из списка:
moyka-i-eksterer, avtoshampuni, aktivnaya-pena, shampuni-dlya-ruchnoy-moyki,
ochistiteli-dvigatelya, antibitum, antimoshka, glina-i-avtoskraby,
obezzhirivateli, ukhod-za-naruzhnym-plastikom, cherniteli-shin,
keramika-dlya-diskov, ochistiteli-diskov, ochistiteli-shin,
antidozhd, ochistiteli-stekol, omyvatel, polirol-dlya-stekla

Для каждой:
1. Читай _clean.json, найди primary_keyword = MAX(volume)
2. Определи Producer/Shop тип
3. Сгенерируй мету по формулам /generate-meta
4. Валидируй: python3 scripts/validate_meta.py {path}
5. Если FAIL — исправь

Пиши лог в data/generated/audit-logs/W1_meta_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"

# W2: aksessuary + oborudovanie (12 категорий)
spawn-claude "W2: Регенерация мета для aksessuary + oborudovanie.

Выполни /generate-meta для КАЖДОЙ категории из списка:
aksessuary, aksessuary-dlya-naneseniya-sredstv, gubki-i-varezhki,
malyarniy-skotch, mikrofibra-i-tryapki, nabory, raspyliteli-i-penniki,
kisti-dlya-deteylinga, shchetka-dlya-moyki-avto, vedra-i-emkosti,
oborudovanie, apparaty-tornador

Для каждой:
1. Читай _clean.json, найди primary_keyword = MAX(volume)
2. Определи Producer/Shop тип
3. Сгенерируй мету по формулам /generate-meta
4. Валидируй: python3 scripts/validate_meta.py {path}
5. Если FAIL — исправь

Пиши лог в data/generated/audit-logs/W2_meta_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"

# W3: ukhod-za-intererom + polirovka (14 категорий)
spawn-claude "W3: Регенерация мета для ukhod-za-intererom + polirovka.

Выполни /generate-meta для КАЖДОЙ категории из списка:
ukhod-za-intererom, neytralizatory-zapakha, poliroli-dlya-plastika,
pyatnovyvoditeli, sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi,
ochistiteli-kozhi, ukhod-za-kozhey, polirovka, polirovalnye-krugi,
mekhovye, polirovalnye-mashinki, akkumulyatornaya, polirovalnye-pasty

Для каждой:
1. Читай _clean.json, найди primary_keyword = MAX(volume)
2. Определи Producer/Shop тип
3. Сгенерируй мету по формулам /generate-meta
4. Валидируй: python3 scripts/validate_meta.py {path}
5. Если FAIL — исправь

Пиши лог в data/generated/audit-logs/W3_meta_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"

# W4: zashchitnye-pokrytiya + opt-i-b2b + glavnaya (9 категорий)
spawn-claude "W4: Регенерация мета для zashchitnye-pokrytiya + opt-i-b2b + glavnaya.

Выполни /generate-meta для КАЖДОЙ категории из списка:
zashchitnye-pokrytiya, keramika-i-zhidkoe-steklo, kvik-deteylery,
silanty, voski, tverdyy-vosk, zhidkiy-vosk, opt-i-b2b, glavnaya

Для каждой:
1. Читай _clean.json, найди primary_keyword = MAX(volume)
2. Определи Producer/Shop тип
3. Сгенерируй мету по формулам /generate-meta
4. Валидируй: python3 scripts/validate_meta.py {path}
5. Если FAIL — исправь

Пиши лог в data/generated/audit-logs/W4_meta_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

---

## После завершения воркеров

### 1. Проверить логи
```bash
cat data/generated/audit-logs/W*_meta_log.md
```

### 2. Финальная валидация
```bash
python3 scripts/validate_meta.py --all
```

### 3. Коммит
```bash
git add categories/*/meta/*_meta.json data/generated/audit-logs/
git commit -m "feat(meta): regenerate all 53 RU meta files per generate-meta v16.0"
```

---

## Риски и митигация

| Риск | Митигация |
|------|-----------|
| _clean.json отсутствует | Воркер пропускает, пишет в лог |
| keywords пуст | Воркер пропускает, пишет в лог |
| Валидация FAIL | Воркер исправляет и повторяет |
| Воркеры конфликтуют | Распределение по L1 исключает пересечения |

---

## Критерии успеха

- [ ] Все 53 `*_meta.json` обновлены
- [ ] `python3 scripts/validate_meta.py --all` → PASS
- [ ] Логи воркеров в `data/generated/audit-logs/`
- [ ] Коммит с описанием изменений
