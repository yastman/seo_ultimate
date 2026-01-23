# UK Batch Content Generation

> **For Claude:** Use `/uk-content-generator {slug}` for each category sequentially.

**Goal:** Сгенерировать UK контент для 47 категорий со статусом `[~]` (init + meta done)

**Architecture:** Sequential content generation via uk-content-generator skill

**Tech Stack:** UK skills, check_seo_structure.py, content-reviewer

---

## Prerequisites

- [x] UK структура создана (50 папок)
- [x] _clean.json с переведёнными ключами
- [x] _meta.json с UK Title/Description/H1
- [x] RESEARCH_DATA.md скопирован из RU

---

## Pipeline для каждой категории

```
/uk-content-generator {slug}     → генерирует {slug}_uk.md
uk-content-reviewer {slug}       → проверяет и исправляет
/uk-quality-gate {slug}          → финальная валидация
```

---

## Task 1: L3 Categories (листовые) — 32 шт.

**Batch 1 (10):**
```
antidozhd, akkumulyatornaya, cherniteli-shin, glina-i-avtoskraby, gubki-i-varezhki,
keramika-dlya-diskov, kisti-dlya-deteylinga, malyarniy-skotch, mekhovye, nabory
```

**Batch 2 (10):**
```
neytralizatory-zapakha, obezzhirivateli, ochistiteli-diskov, ochistiteli-dvigatelya,
ochistiteli-kozhi, ochistiteli-shin, ochistiteli-stekol, omyvatel, polirol-dlya-stekla,
poliroli-dlya-plastika
```

**Batch 3 (12):**
```
polirovalnye-pasty, pyatnovyvoditeli, raspyliteli-i-penniki, shampuni-dlya-ruchnoy-moyki,
shchetka-dlya-moyki-avto, silanty, sredstva-dlya-khimchistki-salona, tverdyy-vosk,
ukhod-za-kozhey, ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, zhidkiy-vosk
```

---

## Task 2: L2 Categories — 8 шт.

```
aksessuary-dlya-naneseniya-sredstv, apparaty-tornador, avtoshampuni,
keramika-i-zhidkoe-steklo, kvik-deteylery, mikrofibra-i-tryapki,
sredstva-dlya-kozhi, voski
```

---

## Task 3: L1 Categories (хабы) — 7 шт.

```
aksessuary, moyka-i-eksterer, oborudovanie, opt-i-b2b,
polirovka, ukhod-za-intererom, zashchitnye-pokrytiya
```

---

## Task 4: Batch Review

После генерации каждого batch:
```bash
# Проверка SEO структуры
for slug in {batch}; do
  python3 scripts/check_seo_structure.py "uk/categories/${slug}/content/${slug}_uk.md" "ключове слово"
done

# Проверка word count
find uk/categories -name "*_uk.md" -exec wc -w {} \;
```

---

## Task 5: Quality Gate All

```bash
# Mass validation
for slug in $(ls uk/categories/); do
  echo "=== ${slug} ==="
  python3 scripts/validate_meta.py "uk/categories/${slug}/meta/${slug}_meta.json" 2>/dev/null || echo "meta: SKIP"
done
```

---

## Task 6: Commit

```bash
git add uk/categories/*/content/
git commit -m "feat(uk): batch content generation for 47 categories"
```

---

## Execution Strategy

**Вариант A: Последовательно (надёжно)**
- Запускать `/uk-content-generator {slug}` по одному
- Review после каждого batch (10 категорий)

**Вариант B: Параллельные агенты (быстро)**
- Запустить 5 агентов параллельно
- Каждый обрабатывает свой batch

**Рекомендация:** Вариант B с параллельными агентами для L3, затем A для L2/L1

---

## Session Prompt (для batch выполнения)

```
Выполни batch генерацию UK контента:

Для каждой категории из списка:
1. /uk-content-generator {slug}
2. Проверь word count (400-700)
3. Проверь H2 с ключевым словом (≥2)

Список: {batch_list}

После batch — commit.
```

---

## Acceptance Criteria

- [ ] 47 файлов `*_uk.md` созданы
- [ ] Word count: 400-700 для каждого
- [ ] H2 с ключевым словом: ≥2 для каждого
- [ ] Нет "Купити" в H1
- [ ] check_seo_structure.py PASS для всех
- [ ] Commit создан

---

## Progress Tracking

После выполнения обновить `tasks/TODO_UK_CONTENT.md`:
- `[~]` → `[x]` для завершённых категорий
- Обновить Progress: X/50

---

**Estimated:** 47 categories × ~2 min = ~90 min sequential, ~20 min parallel (5 agents)
