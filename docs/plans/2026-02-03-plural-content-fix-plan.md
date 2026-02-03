# Plural Content Fix — Manual Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Исправить H1 в контенте (description) на множественное число для 31 UK + 31 RU категорий, затем залить на сервер.

**Architecture:**
1. Воркер W1: UK категории 1-16 (A-O)
2. Воркер W2: UK категории 17-31 (P-Z)
3. Воркер W3: RU категории 1-16
4. Воркер W4: RU категории 17-31
5. Оркестратор: генерация SQL, деплой, валидация

**Tech Stack:** Ручное редактирование MD файлов, Python, MySQL, SSH

---

## Маппинг изменений

### UK (language_id=1)

| # | slug | Старый H1 | Новый H1 |
|---|------|-----------|----------|
| 1 | akkumulyatornaya | Акумуляторна полірувальна машина | **Акумуляторні полірувальні машинки** |
| 2 | aksessuary-dlya-naneseniya-sredstv | Губка для полірування | **Аплікатори та губки для нанесення** |
| 3 | antibitum | Антибітум | **Антибітумні засоби** |
| 4 | antidozhd | Антидощ | **Антидощ для скла** |
| 5 | antimoshka | Очищувач слідів комах | **Очищувачі від комах** |
| 6 | apparaty-tornador | Торнадор | **Апарати Торнадор** |
| 7 | avtoshampuni | Автошампунь | **Автошампуні** |
| 8 | gubki-i-varezhki | Губка для авто | **Губки та рукавички для миття** |
| 9 | mekhovye | Шерстяний круг | **Хутрові полірувальні круги** |
| 10 | nabory | Набір для миття авто | **Набори для авто** |
| 11 | neytralizatory-zapakha | Поглинач запахів | **Нейтралізатори запаху** |
| 12 | obezzhirivateli | Знежирювач для авто | **Знежирювачі для авто** |
| 13 | ochistiteli-diskov | Очищувач дисків | **Очищувачі дисків** |
| 14 | ochistiteli-dvigatelya | Очищувач двигуна | **Очищувачі двигуна** |
| 15 | ochistiteli-kozhi | Очищувач шкіри | **Очищувачі шкіри** |
| 16 | ochistiteli-kuzova | Очищувач кузова | **Очищувачі кузова** |
| 17 | ochistiteli-shin | Очищувач гуми | **Очищувачі шин** |
| 18 | ochistiteli-stekol | Очищувач скла | **Очищувачі скла** |
| 19 | polirol-dlya-stekla | Поліроль для скла | **Поліролі для скла** |
| 20 | poliroli-dlya-plastika | Поліроль для пластику | **Поліролі для пластику** |
| 21 | polirovalnye-mashinki | полірувальна машинка | **Полірувальні машинки** |
| 22 | pyatnovyvoditeli | Плямовивідник | **Плямовивідники** |
| 23 | shampuni-dlya-ruchnoy-moyki | Автошампунь для ручного миття | **Шампуні для ручного миття** |
| 24 | shchetka-dlya-moyki-avto | Щітка для миття авто | **Щітки для миття авто** |
| 25 | silanty | Силант | **Силанти для авто** |
| 26 | sredstva-dlya-kozhi | Засіб для шкіри авто | **Засоби для шкіри** |
| 27 | tverdyy-vosk | Твердий віск | **Тверді воски** |
| 28 | ukhod-za-naruzhnym-plastikom | Відновлювач пластику | **Відновлювачі пластику** |
| 29 | vedra-i-emkosti | Відро для миття авто | **Відра та ємності** |
| 30 | voski | Віск для авто | **Воски для авто** |
| 31 | zhidkiy-vosk | Рідкий віск | **Рідкі воски** |

### RU (language_id=3)

| # | slug | Старый H1 | Новый H1 |
|---|------|-----------|----------|
| 1 | akkumulyatornaya | Аккумуляторная машинка | **Аккумуляторные полировальные машинки** |
| 2 | aksessuary-dlya-naneseniya-sredstv | Губка для полировки | **Аппликаторы и губки для нанесения** |
| 3 | antibitum | Антибитум | **Антибитумные средства** |
| 4 | antidozhd | Антидождь | **Антидождь для стекол** |
| 5 | antimoshka | Очиститель следов насекомых | **Очистители от насекомых** |
| 6 | apparaty-tornador | Торнадор | **Аппараты Торнадор** |
| 7 | avtoshampuni | Автошампунь | **Автошампуни** |
| 8 | gubki-i-varezhki | Губка для авто | **Губки и варежки для мойки** |
| 9 | mekhovye | Шерстяной круг | **Меховые полировальные круги** |
| 10 | nabory | Набор для мойки авто | **Наборы для авто** |
| 11 | neytralizatory-zapakha | Нейтрализатор запаха | **Нейтрализаторы запаха** |
| 12 | obezzhirivateli | Обезжириватель | **Обезжириватели для авто** |
| 13 | ochistiteli-diskov | Очиститель дисков | **Очистители дисков** |
| 14 | ochistiteli-dvigatelya | Очиститель двигателя | **Очистители двигателя** |
| 15 | ochistiteli-kozhi | Очиститель кожи | **Очистители кожи** |
| 16 | ochistiteli-kuzova | Очиститель кузова | **Очистители кузова** |
| 17 | ochistiteli-shin | Очиститель шин | **Очистители шин** |
| 18 | ochistiteli-stekol | Очиститель стекол | **Очистители стекол** |
| 19 | polirol-dlya-stekla | Полироль для стекла | **Полироли для стекла** |
| 20 | poliroli-dlya-plastika | Полироль для пластика | **Полироли для пластика** |
| 21 | polirovalnye-mashinki | Полировальная машинка | **Полировальные машинки** |
| 22 | pyatnovyvoditeli | Пятновыводитель | **Пятновыводители** |
| 23 | shampuni-dlya-ruchnoy-moyki | Шампунь для ручной мойки | **Шампуни для ручной мойки** |
| 24 | shchetka-dlya-moyki-avto | Щётка для мойки авто | **Щётки для мойки авто** |
| 25 | silanty | Силант | **Силанты для авто** |
| 26 | sredstva-dlya-kozhi | Средство для кожи | **Средства для кожи** |
| 27 | tverdyy-vosk | Твёрдый воск | **Твёрдые воски** |
| 28 | ukhod-za-naruzhnym-plastikom | Восстановитель пластика | **Восстановители пластика** |
| 29 | vedra-i-emkosti | Ведро для мойки | **Вёдра и ёмкости** |
| 30 | voski | Воск для авто | **Воски для авто** |
| 31 | zhidkiy-vosk | Жидкий воск | **Жидкие воски** |

### Дополнительные исправления (пропущены ранее)

| slug | lang | Новый H1 |
|------|------|----------|
| cherniteli-shin | RU | **Чернители шин** |
| polirovalnye-krugi | RU | **Полировальные круги** |

---

## Task 1 (W1): UK категории 1-16

**Воркер:** W1-uk-content
**Файлы:** `uk/categories/{slug}/content/{slug}_uk.md`

**Категории:**
1. akkumulyatornaya
2. aksessuary-dlya-naneseniya-sredstv
3. antibitum
4. antidozhd
5. antimoshka
6. apparaty-tornador
7. avtoshampuni
8. gubki-i-varezhki
9. mekhovye
10. nabory
11. neytralizatory-zapakha
12. obezzhirivateli
13. ochistiteli-diskov
14. ochistiteli-dvigatelya
15. ochistiteli-kozhi
16. ochistiteli-kuzova

**Действия для каждого файла:**

1. Открыть `uk/categories/{slug}/content/{slug}_uk.md`
2. Найти старый H1 в тексте (в первом абзаце, заголовках)
3. Заменить на новый H1 из таблицы
4. Сохранить файл
5. НЕ коммитить

**Лог:** `logs/W1-uk-content.log`

```
[START] 2026-02-03 HH:MM akkumulyatornaya
[DONE] 2026-02-03 HH:MM akkumulyatornaya - заменено "Акумуляторна" → "Акумуляторні"
...
[COMPLETE] 2026-02-03 HH:MM W1 finished - 16 files
```

---

## Task 2 (W2): UK категории 17-31

**Воркер:** W2-uk-content
**Файлы:** `uk/categories/{slug}/content/{slug}_uk.md`

**Категории:**
17. ochistiteli-shin
18. ochistiteli-stekol
19. polirol-dlya-stekla
20. poliroli-dlya-plastika
21. polirovalnye-mashinki
22. pyatnovyvoditeli
23. shampuni-dlya-ruchnoy-moyki
24. shchetka-dlya-moyki-avto
25. silanty
26. sredstva-dlya-kozhi
27. tverdyy-vosk
28. ukhod-za-naruzhnym-plastikom
29. vedra-i-emkosti
30. voski
31. zhidkiy-vosk

**Лог:** `logs/W2-uk-content.log`

---

## Task 3 (W3): RU категории 1-16

**Воркер:** W3-ru-content
**Файлы:** `categories/{slug}/content/{slug}_ru.md` (если существует)

**ВАЖНО:** Многие RU категории не имеют локальных content файлов — только на сервере. Для таких категорий:
1. Скачать текущий description с сервера
2. Исправить H1
3. Подготовить SQL

**Лог:** `logs/W3-ru-content.log`

---

## Task 4 (W4): RU категории 17-31

**Воркер:** W4-ru-content
**Лог:** `logs/W4-ru-content.log`

---

## Task 5 (Оркестратор): Генерация SQL

**После завершения W1-W4:**

**Step 1:** Проверить все логи на [COMPLETE]

```bash
grep -l '\[COMPLETE\]' logs/W*-content.log | wc -l
# Expected: 4
```

**Step 2:** Сгенерировать SQL для UK description

```bash
python3 scripts/upload_to_db.py --lang uk --dry-run
python3 scripts/upload_to_db.py --lang uk --generate-sql > data/generated/plural_content_uk.sql
```

**Step 3:** Сгенерировать SQL для RU description

```bash
python3 scripts/upload_to_db.py --lang ru --generate-sql > data/generated/plural_content_ru.sql
```

---

## Task 6 (Оркестратор): Деплой на сервер

**Step 1:** Upload SQL

```bash
scp data/generated/plural_content_uk.sql ult:/tmp/
scp data/generated/plural_content_ru.sql ult:/tmp/
```

**Step 2:** Execute

```bash
ssh ult "mysql yastman_test < /tmp/plural_content_uk.sql"
ssh ult "mysql yastman_test < /tmp/plural_content_ru.sql"
```

**Step 3:** Также исправить пропущенные meta_h1

```sql
-- cherniteli-shin RU
UPDATE oc_category_description SET meta_h1='Чернители шин', meta_title='Чернители шин — купить, цены | Ultimate' WHERE category_id=421 AND language_id=3;

-- polirovalnye-krugi RU
UPDATE oc_category_description SET meta_h1='Полировальные круги', meta_title='Полировальные круги — купить, цены | Ultimate' WHERE category_id=459 AND language_id=3;
```

**Step 4:** Clear cache

```bash
ssh ult "rm -rf /home/yastman/web/ultimate.net.ua/public_html/system/storage/cache/*"
```

---

## Task 7 (Оркестратор): Валидация

**Step 1:** Проверить meta_h1 на сервере (выборка 10 категорий)

```bash
ssh ult "mysql yastman_test -N -e \"
SELECT category_id,
       (SELECT meta_h1 FROM oc_category_description WHERE category_id=c.category_id AND language_id=1) as uk_h1,
       (SELECT meta_h1 FROM oc_category_description WHERE category_id=c.category_id AND language_id=3) as ru_h1
FROM oc_category c
WHERE c.category_id IN (419,421,422,438,459,476,478,437,489,494)
ORDER BY c.category_id;
\""
```

**Expected:**
```
419  Очищувачі дисків       Очистители дисков
421  Чорніння гуми          Чернители шин
422  Очищувачі двигуна      Очистители двигателя
...
```

**Step 2:** Проверить description содержит plural H1

```bash
ssh ult "mysql yastman_test -N -e \"
SELECT category_id,
       CASE WHEN description LIKE '%Очищувачі%' THEN 'OK' ELSE 'FAIL' END as check_plural
FROM oc_category_description
WHERE category_id=419 AND language_id=1;
\""
```

**Step 3:** Visual check на сайте

- https://ultimate.net.ua/ochistiteli-diskov — H1 = "Очистители дисков"
- https://ultimate.net.ua/uk/ochistiteli-diskov — H1 = "Очищувачі дисків"

---

## Task 8: Commit

```bash
git add uk/categories/ categories/ logs/
git commit -m "fix(content): convert H1 to plural in descriptions (62 categories)

- UK: 31 categories updated
- RU: 31 categories updated
- Additional fixes: cherniteli-shin, polirovalnye-krugi

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Checklist

### Подготовка
- [ ] План прочитан и понят
- [ ] logs/ директория создана
- [ ] Воркеры готовы к запуску

### Выполнение
- [ ] W1: UK 1-16 — [COMPLETE]
- [ ] W2: UK 17-31 — [COMPLETE]
- [ ] W3: RU 1-16 — [COMPLETE]
- [ ] W4: RU 17-31 — [COMPLETE]

### Деплой
- [ ] SQL сгенерирован
- [ ] SQL выполнен на сервере
- [ ] Кэш очищен

### Валидация
- [ ] meta_h1 проверен (UK + RU)
- [ ] description содержит plural
- [ ] Сайт проверен визуально
- [ ] Git commit создан

---

## Spawn Commands

```bash
# W1: UK 1-16
tmux new-window -n "W1-uk"
tmux send-keys -t "W1-uk" "claude --dangerously-skip-permissions 'W1: UK content plural fix.

ПЛАН: docs/plans/2026-02-03-plural-content-fix-plan.md
ЗАДАЧА: Task 1 — UK категории 1-16

Для каждой категории из списка:
1. Читай uk/categories/{slug}/content/{slug}_uk.md
2. Находи старый H1 (единственное число) в тексте
3. Заменяй на новый H1 (множественное) из таблицы в плане
4. Сохраняй файл

ЛОГ: $(pwd)/logs/W1-uk-content.log
Формат: [START/DONE/COMPLETE] timestamp message

НЕ делай git commit.'" Enter

# W2: UK 17-31
tmux new-window -n "W2-uk"
tmux send-keys -t "W2-uk" "claude --dangerously-skip-permissions 'W2: UK content plural fix.

ПЛАН: docs/plans/2026-02-03-plural-content-fix-plan.md
ЗАДАЧА: Task 2 — UK категории 17-31

ЛОГ: $(pwd)/logs/W2-uk-content.log

НЕ делай git commit.'" Enter
```
