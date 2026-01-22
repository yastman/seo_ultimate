# UK Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать украинский контент для 50 категорий с корректной частотностью ключей.

**Architecture:** Фаза 1 собирает UK ключи (экспорт → сбор частотности пользователем → импорт). Фаза 2 последовательно обрабатывает каждую категорию через UK pipeline.

**Tech Stack:** Python scripts, Claude Code skills/agents, Git

---

## Task 1: Создать структуру папок

**Files:**
- Create: `data/generated/` (если не существует)
- Create: `uk/data/`
- Create: `tasks/TODO_UK_CONTENT.md`

**Step 1: Создать директории**

```bash
mkdir -p data/generated
mkdir -p uk/data
mkdir -p uk/categories
```

**Step 2: Проверить создание**

```bash
ls -la data/generated/
ls -la uk/data/
ls -la uk/categories/
```

Expected: Пустые директории существуют.

**Step 3: Создать TODO_UK_CONTENT.md**

Создать файл `tasks/TODO_UK_CONTENT.md` со списком всех 50 категорий:

```markdown
# TODO: UK Content для категорий

**Цель:** Создать UK контент для всех категорий

---

## Как работать

1. Убедиться что `uk/data/uk_keywords.json` содержит ключи для категории
2. Выполнить цикл:
   - `/uk-category-init {slug}`
   - `/uk-generate-meta {slug}`
   - `/uk-content-generator {slug}`
   - `uk-content-reviewer {slug}`
   - `/uk-quality-gate {slug}`
3. Commit
4. Отметить `[x]` в чеклисте

---

## Фаза 1: Сбор ключей

- [ ] `/uk-keywords-export` выполнен
- [ ] Частотность собрана (KeySO/Serpstat)
- [ ] `/uk-keywords-import` выполнен
- [ ] `uk/data/uk_keywords.json` создан

---

## Фаза 2: L3 Categories (листовые)

- [ ] aktivnaya-pena
- [ ] antibitum
- [ ] antimoshka
- [ ] antidozhd
- [ ] akkumulyatornaya
- [ ] cherniteli-shin
- [ ] glina-i-avtoskraby
- [ ] gubki-i-varezhki
- [ ] keramika-dlya-diskov
- [ ] kisti-dlya-deteylinga
- [ ] malyarniy-skotch
- [ ] mekhovye
- [ ] nabory
- [ ] neytralizatory-zapakha
- [ ] obezzhirivateli
- [ ] ochistiteli-diskov
- [ ] ochistiteli-dvigatelya
- [ ] ochistiteli-kozhi
- [ ] ochistiteli-shin
- [ ] ochistiteli-stekol
- [ ] omyvatel
- [ ] polirol-dlya-stekla
- [ ] poliroli-dlya-plastika
- [ ] polirovalnye-pasty
- [ ] pyatnovyvoditeli
- [ ] raspyliteli-i-penniki
- [ ] shampuni-dlya-ruchnoy-moyki
- [ ] shchetka-dlya-moyki-avto
- [ ] silanty
- [ ] sredstva-dlya-khimchistki-salona
- [ ] tverdyy-vosk
- [ ] ukhod-za-kozhey
- [ ] ukhod-za-naruzhnym-plastikom
- [ ] vedra-i-emkosti
- [ ] zhidkiy-vosk

## Фаза 2: L2 Categories

- [ ] aksessuary-dlya-naneseniya-sredstv
- [ ] apparaty-tornador
- [ ] avtoshampuni
- [ ] keramika-i-zhidkoe-steklo
- [ ] kvik-deteylery
- [ ] mikrofibra-i-tryapki
- [ ] sredstva-dlya-kozhi
- [ ] voski

## Фаза 2: L1 Categories (хабы)

- [ ] aksessuary
- [ ] moyka-i-eksterer
- [ ] oborudovanie
- [ ] opt-i-b2b
- [ ] polirovka
- [ ] ukhod-za-intererom
- [ ] zashchitnye-pokrytiya

---

**Progress:** 0/50
```

**Step 4: Commit**

```bash
git add data/generated/.gitkeep uk/data/.gitkeep uk/categories/.gitkeep tasks/TODO_UK_CONTENT.md
git commit -m "chore: add UK pipeline folder structure and TODO checklist"
```

---

## Task 2: Экспорт UK ключей

**Files:**
- Read: `categories/**/data/*_clean.json` (все RU категории)
- Create: `data/generated/UK_KEYWORDS_FOR_FREQUENCY.md`

**Step 1: Запустить скрипт экспорта**

```bash
python3 .claude/skills/uk-keywords-export/scripts/export_uk_keywords.py
```

Expected output:
```
Processing 50 categories...
Extracted 1500 RU keywords
Translated to 1500 UK keywords
Deduplicated: 1200 unique
Written to data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
```

**Step 2: Проверить результат**

```bash
head -30 data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
```

Expected: Файл начинается с заголовка, затем список украинских ключей по одному на строку.

**Step 3: Проверить количество**

```bash
wc -l data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
```

Expected: >500 строк (включая заголовок).

**Step 4: Spot-check перевода**

```bash
grep -E "^(активна піна|чорнитель гуми|очищувач дисків|антидощ)$" data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
```

Expected: Все 4 ключа найдены (корректный перевод).

**Step 5: Commit**

```bash
git add data/generated/UK_KEYWORDS_FOR_FREQUENCY.md
git commit -m "data: export UK keywords for frequency collection"
```

---

## Task 3: CHECKPOINT — Сбор частотности

**Действие пользователя:**

1. Скопировать ключи из `data/generated/UK_KEYWORDS_FOR_FREQUENCY.md`
2. Загрузить в KeySO / Serpstat / Ahrefs
3. Экспортировать CSV с колонками `keyword,volume`
4. Сохранить как `data/input/uk_keywords_frequency.csv`

**Формат CSV:**

```csv
keyword,volume
активна піна,1200
чорнитель гуми,900
автошампунь,800
```

**Verification:**

```bash
head -10 data/input/uk_keywords_frequency.csv
wc -l data/input/uk_keywords_frequency.csv
```

Expected: CSV с числовой частотностью, >500 строк.

---

## Task 4: Импорт UK ключей с частотностью

**Files:**
- Read: `data/input/uk_keywords_frequency.csv`
- Create: `uk/data/uk_keywords.json`

**Step 1: Проверить входной файл**

```bash
head -5 data/input/uk_keywords_frequency.csv
```

Expected: CSV с keyword + volume.

**Step 2: Запустить скрипт импорта**

```bash
python3 .claude/skills/uk-keywords-import/scripts/import_uk_keywords.py \
    data/input/uk_keywords_frequency.csv \
    --output uk/data \
    --verbose
```

Expected output:
```
Parsing CSV: data/input/uk_keywords_frequency.csv
Found 1200 keywords
Matching to categories...
Matched: 1000 (83%)
Unmatched: 200 (17%)
Writing to uk/data/uk_keywords.json
Done!
```

**Step 3: Проверить результат**

```bash
cat uk/data/uk_keywords.json | python3 -m json.tool | head -50
```

Expected: Валидный JSON с категориями и ключами.

**Step 4: Проверить распределение по категориям**

```bash
cat uk/data/uk_keywords.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
cats = data.get('categories', {})
print(f'Categories with keywords: {len(cats)}')
for slug, info in sorted(cats.items(), key=lambda x: -x[1]['total_volume'])[:10]:
    print(f'  {slug}: {info[\"count\"]} keywords, volume={info[\"total_volume\"]}')
"
```

Expected: 30+ категорий с ключами.

**Step 5: Проверить unmatched**

```bash
cat uk/data/uk_keywords.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
unmatched = data.get('unmatched', [])
print(f'Unmatched keywords: {len(unmatched)}')
if unmatched:
    for kw in unmatched[:5]:
        print(f'  - {kw[\"keyword\"]} (vol={kw[\"volume\"]})')
"
```

Expected: <20% unmatched.

**Step 6: Commit**

```bash
git add uk/data/uk_keywords.json data/input/uk_keywords_frequency.csv
git commit -m "data: import UK keywords with frequency"
```

---

## Task 5: Обновить TODO чеклист

**Files:**
- Modify: `tasks/TODO_UK_CONTENT.md`

**Step 1: Отметить Фазу 1 как завершённую**

В файле `tasks/TODO_UK_CONTENT.md` изменить:

```markdown
## Фаза 1: Сбор ключей

- [x] `/uk-keywords-export` выполнен
- [x] Частотность собрана (KeySO/Serpstat)
- [x] `/uk-keywords-import` выполнен
- [x] `uk/data/uk_keywords.json` создан
```

**Step 2: Commit**

```bash
git add tasks/TODO_UK_CONTENT.md
git commit -m "docs: mark Phase 1 complete in UK TODO"
```

---

## Task 6-55: Обработка категорий (×50)

**Шаблон для каждой категории {slug}:**

### Step 1: Инициализация

```bash
# Или через skill:
/uk-category-init {slug}
```

Verify:
```bash
ls -la uk/categories/{slug}/
ls -la uk/categories/{slug}/data/
```

Expected: Структура папок создана, `{slug}_clean.json` содержит UK ключи.

### Step 2: Генерация мета

```bash
/uk-generate-meta {slug}
```

Verify:
```bash
cat uk/categories/{slug}/meta/{slug}_meta.json | python3 -m json.tool
```

Expected: Title содержит "Купити", H1 не содержит "Купити".

### Step 3: Генерация контента

```bash
/uk-content-generator {slug}
```

Verify:
```bash
wc -c uk/categories/{slug}/content/{slug}_uk.md
```

Expected: >2000 bytes.

### Step 4: Ревизия контента

```bash
uk-content-reviewer {slug}
```

Verify: Контент проверен, терминология корректна (гума, миття, скло).

### Step 5: Quality gate

```bash
/uk-quality-gate {slug}
```

Expected: PASS без критических ошибок.

### Step 6: Commit

```bash
git add uk/categories/{slug}/
git commit -m "content(uk): add {slug}"
```

### Step 7: Обновить TODO

В `tasks/TODO_UK_CONTENT.md` отметить `[x] {slug}`.

---

## Task 56: Финальная валидация

**Step 1: Проверить количество UK категорий**

```bash
ls -d uk/categories/*/ | wc -l
```

Expected: 50

**Step 2: Проверить все meta файлы**

```bash
for f in uk/categories/*/meta/*.json; do
    echo "Checking $f..."
    python3 scripts/validate_meta.py "$f"
done
```

Expected: Все PASS.

**Step 3: Проверить все content файлы**

```bash
for f in uk/categories/*/content/*.md; do
    size=$(wc -c < "$f")
    if [ $size -lt 2000 ]; then
        echo "WARNING: $f is only $size bytes"
    fi
done
```

Expected: Все файлы ≥2000 bytes.

**Step 4: Проверить терминологию**

```bash
grep -r "резина\|мойка\|стекло" uk/categories/*/content/*.md
```

Expected: Нет результатов (нет русских терминов).

**Step 5: Финальный коммит**

```bash
git add tasks/TODO_UK_CONTENT.md
git commit -m "content(uk): complete all 50 categories"
```

---

## Acceptance Criteria

- [ ] `data/generated/UK_KEYWORDS_FOR_FREQUENCY.md` — создан, >500 ключей
- [ ] `uk/data/uk_keywords.json` — создан, 30+ категорий
- [ ] `uk/categories/` — 50 папок
- [ ] Каждая категория содержит: `data/`, `meta/`, `content/`
- [ ] Все meta: Title с "Купити", H1 без "Купити"
- [ ] Все content: ≥2KB, терминология UK (гума, миття, скло)
- [ ] `tasks/TODO_UK_CONTENT.md` — все 50 чекбоксов отмечены
- [ ] Git history: отдельный коммит на каждую категорию

---

**Version:** 1.0
