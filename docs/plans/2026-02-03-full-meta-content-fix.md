# Full Meta & Content Fix — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Исправить все нарушения мета-тегов и контента: Title формула (Front-loading), H1 во множественном, description во множественном.

**Architecture:**
1. W1: Исправить UK _meta.json (Title + H1) — 31 категория
2. W2: Исправить UK content MD файлы (единственное → множественное везде)
3. W3: Генерация SQL и деплой UK
4. W4: Генерация SQL и деплой RU (description only)
5. Оркестратор: валидация

**Tech Stack:** JSON, Markdown, Python, MySQL, SSH

---

## Проблемы для исправления

### 1. Title нарушает Front-loading (UK)

**Сейчас:** `Купити {keyword} в Україні | Ultimate` ❌
**Нужно:** `{primary_keyword} — купити, ціни | Ultimate` ✅

| cat_id | slug | Текущий Title | Правильный Title |
|--------|------|---------------|------------------|
| 419 | ochistiteli-diskov | Купити Очищувачі дисків в Україні | **Очищувачі дисків — купити, ціни \| Ultimate** |
| 422 | ochistiteli-dvigatelya | Купити Очищувачі двигуна в Україні | **Очищувачі двигуна — купити, ціни \| Ultimate** |
| 424 | omyvatel | Купити омивач скла в Україні | **Омивач скла — купити, ціни \| Ultimate** |
| 428 | sredstva-dlya-kozhi | Купити Засоби для шкіри в Україні | **Засоби для шкіри — купити, ціни \| Ultimate** |
| 434 | pyatnovyvoditeli | Купити Плямовивідники для авто | **Плямовивідники — купити, ціни \| Ultimate** |
| 439 | keramika-i-zhidkoe-steklo | Купити кераміка для авто | **Кераміка для авто — купити, ціни \| Ultimate** |
| 446 | mikrofibra-i-tryapki | Купити мікрофібра для авто | **Мікрофібра для авто — купити, ціни \| Ultimate** |
| 447 | raspyliteli-i-penniki | Купити розпилювач для води | **Розпилювачі для води — купити, ціни \| Ultimate** |
| 454 | malyarniy-skotch | Купити малярний скотч | **Малярний скотч — купити, ціни \| Ultimate** |
| 457 | polirovka | Купити засоби для полірування | **Полірування авто — купити, ціни \| Ultimate** |
| 458 | polirovalnye-pasty | Купити полірувальну пасту | **Полірувальні пасти — купити, ціни \| Ultimate** |
| 478 | obezzhirivateli | Купити Знежирювачі для авто | **Знежирювачі для авто — купити, ціни \| Ultimate** |
| 492 | ochistiteli-kozhi | Купити Очищувачі шкіри | **Очищувачі шкіри — купити, ціни \| Ultimate** |

### 2. H1 во множественном числе (UK + RU)

Уже частично исправлено в meta_h1, но нужно проверить все категории.

### 3. Description содержит единственное число

В тексте description встречается единственное число вместо множественного:
- "Очищувач дисків видаляє..." → "Очищувачі дисків видаляють..."
- "Знежирювач для авто..." → "Знежирювачі для авто..."

---

## Маппинг: slug → primary_keyword (UK)

Из `uk/categories/{slug}/data/{slug}_clean.json` берём MAX(volume):

| slug | primary_keyword (UK) | Для Title/H1 |
|------|---------------------|--------------|
| akkumulyatornaya | акумуляторна полірувальна машина | Акумуляторні полірувальні машинки |
| aksessuary-dlya-naneseniya-sredstv | губка для полірування | Аплікатори та губки для нанесення |
| antibitum | антибітум | Антибітумні засоби |
| antidozhd | антидощ | Антидощ для скла |
| antimoshka | очищувач слідів комах | Очищувачі від комах |
| apparaty-tornador | торнадор | Апарати Торнадор |
| avtoshampuni | автошампунь | Автошампуні |
| gubki-i-varezhki | губка для авто | Губки та рукавички |
| mekhovye | шерстяний круг | Хутрові полірувальні круги |
| nabory | набір для миття авто | Набори для авто |
| neytralizatory-zapakha | поглинач запахів | Нейтралізатори запаху |
| obezzhirivateli | знежирювач для авто | Знежирювачі для авто |
| ochistiteli-diskov | очищувач дисків | Очищувачі дисків |
| ochistiteli-dvigatelya | очищувач двигуна | Очищувачі двигуна |
| ochistiteli-kozhi | очищувач шкіри авто | Очищувачі шкіри |
| ochistiteli-kuzova | очищувач кузова | Очищувачі кузова |
| ochistiteli-shin | очищувач гуми | Очищувачі шин |
| ochistiteli-stekol | очищувач скла | Очищувачі скла |
| omyvatel | омивач скла | Омивачі скла |
| polirol-dlya-stekla | поліроль для скла | Поліролі для скла |
| poliroli-dlya-plastika | поліроль для пластику | Поліролі для пластику |
| polirovalnye-mashinki | полірувальна машинка | Полірувальні машинки |
| polirovalnye-pasty | паста для полірування | Полірувальні пасти |
| pyatnovyvoditeli | плямовивідник | Плямовивідники |
| raspyliteli-i-penniki | розпилювач для води | Розпилювачі для води |
| shampuni-dlya-ruchnoy-moyki | засіб для миття авто | Шампуні для ручного миття |
| shchetka-dlya-moyki-avto | щітка для миття авто | Щітки для миття авто |
| silanty | силант | Силанти для авто |
| sredstva-dlya-kozhi | засоби для шкіри авто | Засоби для шкіри |
| tverdyy-vosk | твердий віск | Тверді воски |
| ukhod-za-naruzhnym-plastikom | відновлювач пластику | Відновлювачі пластику |
| vedra-i-emkosti | відро для миття авто | Відра та ємності |
| voski | віск для авто | Воски для авто |
| zhidkiy-vosk | рідкий віск | Рідкі воски |

---

## Task 1 (W1): Исправить UK _meta.json — Title + H1

**Воркер:** W1-uk-meta
**Файлы:** `uk/categories/{slug}/meta/{slug}_meta.json`

**Для каждой категории:**

1. Прочитать `uk/categories/{slug}/data/{slug}_clean.json`
2. Найти primary_keyword = MAX(volume)
3. Обновить `_meta.json`:
   - **H1** = primary_keyword во множественном (из таблицы выше)
   - **Title** = `{H1} — купити, ціни | Ultimate`

**Формула Title:**
```
ЕСЛИ len(H1) ≤ 20:
  {H1} — купити в інтернет-магазині Ultimate
ИНАЧЕ:
  {H1} — купити, ціни | Ultimate
```

**Категории (31 шт):**
akkumulyatornaya, aksessuary-dlya-naneseniya-sredstv, antibitum, antidozhd, antimoshka, apparaty-tornador, avtoshampuni, gubki-i-varezhki, mekhovye, nabory, neytralizatory-zapakha, obezzhirivateli, ochistiteli-diskov, ochistiteli-dvigatelya, ochistiteli-kozhi, ochistiteli-kuzova, ochistiteli-shin, ochistiteli-stekol, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-mashinki, pyatnovyvoditeli, shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto, silanty, sredstva-dlya-kozhi, tverdyy-vosk, ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, voski, zhidkiy-vosk

**Дополнительные категории с нарушением Title (не в списке 31):**
- omyvatel (424)
- keramika-i-zhidkoe-steklo (439)
- mikrofibra-i-tryapki (446)
- raspyliteli-i-penniki (447)
- malyarniy-skotch (454)
- polirovka (457)
- polirovalnye-pasty (458)

**Лог:** `logs/W1-uk-meta.log`

```
[START] timestamp slug
[DONE] timestamp slug - H1: "X" → "Y", Title fixed
[COMPLETE] timestamp W1 finished
```

**НЕ делай git commit.**

---

## Task 2 (W2): Исправить UK content — единственное → множественное

**Воркер:** W2-uk-content
**Файлы:** `uk/categories/{slug}/content/{slug}_uk.md`

**Для каждой категории:**

1. Прочитать content файл
2. Заменить ВСЕ вхождения единственного числа на множественное:

| Найти | Заменить на |
|-------|-------------|
| Очищувач дисків | Очищувачі дисків |
| Очищувач двигуна | Очищувачі двигуна |
| Очищувач шкіри | Очищувачі шкіри |
| Очищувач кузова | Очищувачі кузова |
| Очищувач гуми | Очищувачі шин |
| Очищувач скла | Очищувачі скла |
| Знежирювач для авто | Знежирювачі для авто |
| Знежирювач | Знежирювачі |
| Силант для авто | Силанти для авто |
| Силант | Силанти |
| Поліроль для пластику | Поліролі для пластику |
| Поліроль для скла | Поліролі для скла |
| Губка для авто | Губки для авто |
| Губка для полірування | Губки для полірування |
| Щітка для миття | Щітки для миття |
| Плямовивідник | Плямовивідники |
| Поглинач запахів | Нейтралізатори запаху |
| Набір для | Набори для |
| Відро для | Відра для |
| Віск для авто | Воски для авто |
| Твердий віск | Тверді воски |
| Рідкий віск | Рідкі воски |
| Автошампунь | Автошампуні |
| Торнадор | Торнадори |
| Відновлювач пластику | Відновлювачі пластику |

**ВАЖНО:** Заменять осторожно — "Очищувач" в начале предложения, но не внутри слов.

**Лог:** `logs/W2-uk-content.log`

**НЕ делай git commit.**

---

## Task 3 (W3): Генерация и деплой UK SQL

**Воркер:** W3-uk-deploy

**Step 1:** Сгенерировать SQL для meta_h1 + meta_title

```python
# Для каждой UK категории
for slug in mapping:
    cat_id = slug_to_id[slug]
    meta = load_json(f'uk/categories/{slug}/meta/{slug}_meta.json')
    h1 = meta['h1'].replace("'", "\\'")
    title = meta['meta']['title'].replace("'", "\\'")

    print(f"UPDATE oc_category_description SET meta_h1='{h1}', meta_title='{title}' WHERE category_id={cat_id} AND language_id=1;")
```

**Step 2:** Сгенерировать SQL для description

```python
# Конвертировать MD → HTML и обновить description
for content_file in uk_content_files:
    html = md_to_html(content_file.read_text())
    print(f"UPDATE oc_category_description SET description='{html}' WHERE category_id={cat_id} AND language_id=1;")
```

**Step 3:** Выполнить SQL

```bash
scp data/generated/uk_full_fix.sql ult:/tmp/
ssh ult "mysql yastman_test < /tmp/uk_full_fix.sql"
```

**Лог:** `logs/W3-uk-deploy.log`

**НЕ делай git commit.**

---

## Task 4 (W4): RU description fix

**Воркер:** W4-ru-deploy

RU content файлов нет локально — исправляем напрямую на сервере через REPLACE:

```sql
-- Замена единственного на множественное в RU description
UPDATE oc_category_description SET description=REPLACE(description, 'Очиститель дисков', 'Очистители дисков') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Очиститель двигателя', 'Очистители двигателя') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Обезжириватель для авто', 'Обезжириватели для авто') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Обезжириватель', 'Обезжириватели') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Силант для авто', 'Силанты для авто') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Силант ', 'Силанты ') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Полироль для пластика', 'Полироли для пластика') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Губка для авто', 'Губки для авто') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Щётка для мойки', 'Щётки для мойки') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Пятновыводитель', 'Пятновыводители') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Набор для', 'Наборы для') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Ведро для', 'Вёдра для') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Воск для авто', 'Воски для авто') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Твёрдый воск', 'Твёрдые воски') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Жидкий воск', 'Жидкие воски') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Автошампунь', 'Автошампуни') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Торнадор', 'Торнадоры') WHERE language_id=3;
UPDATE oc_category_description SET description=REPLACE(description, 'Восстановитель пластика', 'Восстановители пластика') WHERE language_id=3;
```

**Лог:** `logs/W4-ru-deploy.log`

**НЕ делай git commit.**

---

## Task 5 (Оркестратор): Валидация

**После завершения W1-W4:**

### Step 1: Проверить логи

```bash
grep -l '\[COMPLETE\]' logs/W*.log | wc -l
# Expected: 4
```

### Step 2: Очистить кэш

```bash
ssh ult "rm -rf /home/yastman/web/ultimate.net.ua/public_html/system/storage/cache/*"
```

### Step 3: Проверить Title (Front-loading)

```bash
ssh ult "mysql yastman_test -N -e \"
SELECT category_id, meta_title
FROM oc_category_description
WHERE language_id=1 AND meta_title LIKE 'Купити%'
LIMIT 5;
\""
# Expected: 0 rows (все Title начинаются с keyword, не с "Купити")
```

### Step 4: Проверить H1 (множественное)

```bash
ssh ult "mysql yastman_test -N -e \"
SELECT category_id, meta_h1
FROM oc_category_description
WHERE language_id=1 AND category_id IN (419,422,438,478)
ORDER BY category_id;
\""
# Expected:
# 419 Очищувачі дисків
# 422 Очищувачі двигуна
# 438 Силанти для авто
# 478 Знежирювачі для авто
```

### Step 5: Проверить description (множественное)

```bash
ssh ult "mysql yastman_test -N -e \"
SELECT category_id,
       CASE WHEN description LIKE '%Очищувач дисків%' THEN 'FAIL: singular' ELSE 'OK' END
FROM oc_category_description
WHERE language_id=1 AND category_id=419;
\""
# Expected: OK
```

### Step 6: Visual check

- https://ultimate.net.ua/ochistiteli-diskov
  - Title в браузере: "Очистители дисков — купить, цены | Ultimate"
  - H1 на странице: "Очистители дисков"

- https://ultimate.net.ua/uk/ochistiteli-diskov
  - Title: "Очищувачі дисків — купити, ціни | Ultimate"
  - H1: "Очищувачі дисків"

---

## Task 6: Git commit

```bash
git add uk/categories/ logs/ data/generated/
git commit -m "fix(meta+content): Front-loading Title, plural H1 and description

UK:
- Title: '{keyword} — купити' (not 'Купити {keyword}')
- H1: plural form (Очищувачі, Знежирювачі, etc.)
- Description: all singular → plural

RU:
- Description: all singular → plural

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Checklist

### Подготовка
- [ ] План прочитан
- [ ] logs/ директория существует
- [ ] Маппинг slug → cat_id загружен

### W1: UK Meta
- [ ] Все 31+ категорий обработаны
- [ ] Title начинается с keyword (не "Купити")
- [ ] H1 во множественном числе
- [ ] [COMPLETE] в логе

### W2: UK Content
- [ ] Все MD файлы обработаны
- [ ] Единственное число заменено на множественное
- [ ] [COMPLETE] в логе

### W3: UK Deploy
- [ ] SQL сгенерирован
- [ ] SQL выполнен на сервере
- [ ] [COMPLETE] в логе

### W4: RU Deploy
- [ ] REPLACE SQL выполнен
- [ ] [COMPLETE] в логе

### Валидация
- [ ] Кэш очищен
- [ ] Title не начинаются с "Купити" (0 rows)
- [ ] H1 во множественном
- [ ] Description во множественном
- [ ] Сайт проверен визуально
- [ ] Git commit создан

---

## Spawn Commands

```bash
# W1: UK Meta fix
tmux new-window -n "W1-meta"
tmux send-keys -t "W1-meta" "claude --dangerously-skip-permissions 'W1: UK Meta fix — Title Front-loading + H1 plural.

ПЛАН: docs/plans/2026-02-03-full-meta-content-fix.md
ЗАДАЧА: Task 1

Для каждой UK категории из списка в плане:
1. Прочитай uk/categories/{slug}/meta/{slug}_meta.json
2. Обнови H1 на множественное число (из таблицы в плане)
3. Обнови Title по формуле: {H1} — купити, ціни | Ultimate
   (если H1 ≤ 20 chars: {H1} — купити в інтернет-магазині Ultimate)
4. Сохрани файл

Также исправь категории с нарушением Title:
- omyvatel, keramika-i-zhidkoe-steklo, mikrofibra-i-tryapki, raspyliteli-i-penniki, malyarniy-skotch, polirovka, polirovalnye-pasty

ЛОГ: $(pwd)/logs/W1-uk-meta.log
Формат: [START/DONE/COMPLETE] timestamp message

НЕ делай git commit.'" Enter

# W2: UK Content fix
tmux new-window -n "W2-content"
tmux send-keys -t "W2-content" "claude --dangerously-skip-permissions 'W2: UK Content fix — singular → plural everywhere.

ПЛАН: docs/plans/2026-02-03-full-meta-content-fix.md
ЗАДАЧА: Task 2

Для каждого UK content файла (uk/categories/*/content/*_uk.md):
1. Прочитай файл
2. Замени ВСЕ вхождения единственного числа на множественное (таблица в плане)
3. Сохрани файл

Таблица замен в плане — используй её.

ЛОГ: $(pwd)/logs/W2-uk-content.log

НЕ делай git commit.'" Enter

# W3: UK Deploy
tmux new-window -n "W3-deploy"
tmux send-keys -t "W3-deploy" "claude --dangerously-skip-permissions 'W3: UK SQL generation and deploy.

ПЛАН: docs/plans/2026-02-03-full-meta-content-fix.md
ЗАДАЧА: Task 3

1. Сгенерируй SQL для UK meta_h1 + meta_title из локальных _meta.json
2. Сгенерируй SQL для UK description из локальных _uk.md (MD → HTML)
3. Объедини в data/generated/uk_full_fix.sql
4. Загрузи и выполни на сервере:
   scp data/generated/uk_full_fix.sql ult:/tmp/
   ssh ult \"mysql yastman_test < /tmp/uk_full_fix.sql\"

Используй scripts/upload_to_db.py как референс для MD → HTML конвертации.

ЛОГ: $(pwd)/logs/W3-uk-deploy.log

НЕ делай git commit.'" Enter

# W4: RU Deploy
tmux new-window -n "W4-ru"
tmux send-keys -t "W4-ru" "claude --dangerously-skip-permissions 'W4: RU description fix via REPLACE.

ПЛАН: docs/plans/2026-02-03-full-meta-content-fix.md
ЗАДАЧА: Task 4

Выполни SQL REPLACE команды из плана для RU description (language_id=3):
- Очиститель → Очистители
- Обезжириватель → Обезжириватели
- И т.д. (полный список в плане)

ssh ult \"mysql yastman_test -e \\\"
UPDATE oc_category_description SET description=REPLACE(description, \\\"Очиститель дисков\\\", \\\"Очистители дисков\\\") WHERE language_id=3;
...
\\\"\"

ЛОГ: $(pwd)/logs/W4-ru-deploy.log

НЕ делай git commit.'" Enter
```
