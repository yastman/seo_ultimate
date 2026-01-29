# Regenerate All RU Meta Tags — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Регенерировать все 53 RU мета-файла по актуальной семантике и правилам /generate-meta v16.0

**Architecture:** 4 параллельных воркера, каждый обрабатывает группу L1 категорий. Воркеры читают `_clean.json`, генерируют мету, валидируют, пишут логи. Оркестратор коммитит после завершения всех.

**Tech Stack:** spawn-claude, /generate-meta skill, validate_meta.py, tmux

---

## Task 1: Подготовка — очистка логов

**Files:**
- Delete: `data/generated/audit-logs/W*_meta_log.md` (если есть)

**Step 1: Проверить существующие логи**

```bash
ls -la data/generated/audit-logs/W*_meta_log.md 2>/dev/null || echo "No existing logs"
```

**Step 2: Удалить старые логи (если есть)**

```bash
rm -f data/generated/audit-logs/W*_meta_log.md
```

**Step 3: Создать директорию логов (если нет)**

```bash
mkdir -p data/generated/audit-logs
```

---

## Task 2: Запуск W1 — moyka-i-eksterer (18 категорий)

**Step 1: Запустить воркера W1**

```bash
spawn-claude "W1: Регенерация мета для moyka-i-eksterer (18 категорий).

ЗАДАЧА: Для КАЖДОЙ категории из списка выполни /generate-meta:

1. moyka-i-eksterer
2. moyka-i-eksterer/avtoshampuni
3. moyka-i-eksterer/avtoshampuni/aktivnaya-pena
4. moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki
5. moyka-i-eksterer/ochistiteli-dvigatelya
6. moyka-i-eksterer/ochistiteli-kuzova/antibitum
7. moyka-i-eksterer/ochistiteli-kuzova/antimoshka
8. moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby
9. moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli
10. moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom
11. moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin
12. moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov
13. moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov
14. moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin
15. moyka-i-eksterer/sredstva-dlya-stekol/antidozhd
16. moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol
17. moyka-i-eksterer/sredstva-dlya-stekol/omyvatel
18. moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla

АЛГОРИТМ для каждой категории:
1. Читай categories/{path}/data/{slug}_clean.json
2. Найди primary_keyword = ключ с MAX(volume) в keywords[]
3. Определи тип: Shop если slug в списке [glina-i-avtoskraby, cherniteli-shin], иначе Producer
4. Сгенерируй мету по /generate-meta формулам
5. Запиши в categories/{path}/meta/{slug}_meta.json
6. Валидируй: python3 scripts/validate_meta.py categories/{path}/meta/{slug}_meta.json
7. Если FAIL — исправь и повтори валидацию

ЛОГ: Пиши результаты в data/generated/audit-logs/W1_meta_log.md

НЕ ДЕЛАЙ git commit — коммиты делает оркестратор" "$(pwd)"
```

Expected: tmux окно W1 создано

---

## Task 3: Запуск W2 — aksessuary + oborudovanie (12 категорий)

**Step 1: Запустить воркера W2**

```bash
spawn-claude "W2: Регенерация мета для aksessuary + oborudovanie (12 категорий).

ЗАДАЧА: Для КАЖДОЙ категории из списка выполни /generate-meta:

1. aksessuary
2. aksessuary/aksessuary-dlya-naneseniya-sredstv
3. aksessuary/gubki-i-varezhki
4. aksessuary/malyarniy-skotch
5. aksessuary/mikrofibra-i-tryapki
6. aksessuary/nabory
7. aksessuary/raspyliteli-i-penniki
8. aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga
9. aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto
10. aksessuary/vedra-i-emkosti
11. oborudovanie
12. oborudovanie/apparaty-tornador

АЛГОРИТМ для каждой категории:
1. Читай categories/{path}/data/{slug}_clean.json
2. Найди primary_keyword = ключ с MAX(volume) в keywords[]
3. Определи тип: Shop если slug в списке [gubki-i-varezhki, raspyliteli-i-penniki, vedra-i-emkosti, kisti-dlya-deteylinga, shchetka-dlya-moyki-avto, malyarniy-skotch, oborudovanie, apparaty-tornador], иначе Producer
4. Сгенерируй мету по /generate-meta формулам
5. Запиши в categories/{path}/meta/{slug}_meta.json
6. Валидируй: python3 scripts/validate_meta.py categories/{path}/meta/{slug}_meta.json
7. Если FAIL — исправь и повтори валидацию

ЛОГ: Пиши результаты в data/generated/audit-logs/W2_meta_log.md

НЕ ДЕЛАЙ git commit — коммиты делает оркестратор" "$(pwd)"
```

Expected: tmux окно W2 создано

---

## Task 4: Запуск W3 — ukhod-za-intererom + polirovka (14 категорий)

**Step 1: Запустить воркера W3**

```bash
spawn-claude "W3: Регенерация мета для ukhod-za-intererom + polirovka (14 категорий).

ЗАДАЧА: Для КАЖДОЙ категории из списка выполни /generate-meta:

1. ukhod-za-intererom
2. ukhod-za-intererom/neytralizatory-zapakha
3. ukhod-za-intererom/poliroli-dlya-plastika
4. ukhod-za-intererom/pyatnovyvoditeli
5. ukhod-za-intererom/sredstva-dlya-khimchistki-salona
6. ukhod-za-intererom/sredstva-dlya-kozhi
7. ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi
8. ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey
9. polirovka
10. polirovka/polirovalnye-krugi
11. polirovka/polirovalnye-krugi/mekhovye
12. polirovka/polirovalnye-mashinki
13. polirovka/polirovalnye-mashinki/akkumulyatornaya
14. polirovka/polirovalnye-pasty

АЛГОРИТМ для каждой категории:
1. Читай categories/{path}/data/{slug}_clean.json
2. Найди primary_keyword = ключ с MAX(volume) в keywords[]
3. Определи тип: Shop если slug в списке [polirovka, polirovalnye-krugi, polirovalnye-mashinki], иначе Producer
4. Сгенерируй мету по /generate-meta формулам
5. Запиши в categories/{path}/meta/{slug}_meta.json
6. Валидируй: python3 scripts/validate_meta.py categories/{path}/meta/{slug}_meta.json
7. Если FAIL — исправь и повтори валидацию

ЛОГ: Пиши результаты в data/generated/audit-logs/W3_meta_log.md

НЕ ДЕЛАЙ git commit — коммиты делает оркестратор" "$(pwd)"
```

Expected: tmux окно W3 создано

---

## Task 5: Запуск W4 — zashchitnye-pokrytiya + opt-i-b2b + glavnaya (9 категорий)

**Step 1: Запустить воркера W4**

```bash
spawn-claude "W4: Регенерация мета для zashchitnye-pokrytiya + opt-i-b2b + glavnaya (9 категорий).

ЗАДАЧА: Для КАЖДОЙ категории из списка выполни /generate-meta:

1. zashchitnye-pokrytiya
2. zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo
3. zashchitnye-pokrytiya/kvik-deteylery
4. zashchitnye-pokrytiya/silanty
5. zashchitnye-pokrytiya/voski
6. zashchitnye-pokrytiya/voski/tverdyy-vosk
7. zashchitnye-pokrytiya/voski/zhidkiy-vosk
8. opt-i-b2b
9. glavnaya

АЛГОРИТМ для каждой категории:
1. Читай categories/{path}/data/{slug}_clean.json
2. Найди primary_keyword = ключ с MAX(volume) в keywords[]
3. Тип: Producer для всех (есть товары Ultimate)
4. Сгенерируй мету по /generate-meta формулам
5. Запиши в categories/{path}/meta/{slug}_meta.json
6. Валидируй: python3 scripts/validate_meta.py categories/{path}/meta/{slug}_meta.json
7. Если FAIL — исправь и повтори валидацию

ЛОГ: Пиши результаты в data/generated/audit-logs/W4_meta_log.md

НЕ ДЕЛАЙ git commit — коммиты делает оркестратор" "$(pwd)"
```

Expected: tmux окно W4 создано

---

## Task 6: Мониторинг воркеров

**Step 1: Переключиться на список окон tmux**

```
Ctrl+A, w
```

Expected: Список окон W1, W2, W3, W4

**Step 2: Проверять прогресс каждого воркера**

Переключаться между окнами: `Ctrl+A, n` (следующее) или `Ctrl+A, p` (предыдущее)

**Step 3: Дождаться завершения всех воркеров**

Воркер завершён когда видишь prompt без активной работы.

---

## Task 7: Проверка логов воркеров

**Step 1: Проверить что все логи созданы**

```bash
ls -la data/generated/audit-logs/W*_meta_log.md
```

Expected: 4 файла (W1, W2, W3, W4)

**Step 2: Прочитать логи**

```bash
cat data/generated/audit-logs/W1_meta_log.md
cat data/generated/audit-logs/W2_meta_log.md
cat data/generated/audit-logs/W3_meta_log.md
cat data/generated/audit-logs/W4_meta_log.md
```

Expected: Статистика по каждой категории, статусы PASS

**Step 3: Проверить на ошибки**

```bash
grep -i "fail\|error\|skip" data/generated/audit-logs/W*_meta_log.md
```

Expected: Пусто (нет ошибок) или список проблем для ручного решения

---

## Task 8: Финальная валидация

**Step 1: Запустить валидацию всех мета-файлов**

```bash
python3 scripts/validate_meta.py --all
```

Expected: Все PASS

**Step 2: Если есть FAIL — исправить вручную**

Для каждого FAIL:
1. Читать ошибку валидатора
2. Исправить `_meta.json`
3. Перезапустить валидацию

---

## Task 9: Коммит результатов

**Step 1: Проверить изменённые файлы**

```bash
git status
```

Expected: Изменены `*_meta.json` файлы и созданы логи

**Step 2: Добавить файлы в staging**

```bash
git add categories/*/meta/*_meta.json categories/*/*/meta/*_meta.json categories/*/*/*/meta/*_meta.json data/generated/audit-logs/W*_meta_log.md
```

**Step 3: Коммит**

```bash
git commit -m "feat(meta): regenerate all 53 RU meta files per generate-meta v16.0

- primary_keyword = MAX(volume)
- Producer/Shop patterns applied
- All pass validate_meta.py

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Критерии успеха

- [ ] Все 4 воркера завершились
- [ ] 4 лога в `data/generated/audit-logs/`
- [ ] `python3 scripts/validate_meta.py --all` → все PASS
- [ ] Коммит создан

---

## Справка: Shop-категории (без товаров Ultimate)

```
glina-i-avtoskraby, gubki-i-varezhki, cherniteli-shin,
raspyliteli-i-penniki, vedra-i-emkosti, kisti-dlya-deteylinga,
shchetka-dlya-moyki-avto, shchetki-i-kisti, malyarniy-skotch,
polirovka, polirovalnye-krugi, polirovalnye-mashinki,
oborudovanie, apparaty-tornador
```

---

## Справка: Формулы /generate-meta v16.0

**Title:**
```
IF len(primary_keyword) <= 20:
  {primary_keyword} — купить в интернет-магазине Ultimate
ELSE:
  {primary_keyword} — купить, цены | Ultimate
```

**H1:** `{primary_keyword}` (дословно, без "Купить")

**Description (Producer):**
```
{primary_keyword} от производителя Ultimate. {Типы} — {подробности}. Опт и розница.
```

**Description (Shop):**
```
{primary_keyword} в интернет-магазине Ultimate. {Типы} — {подробности}.
```
