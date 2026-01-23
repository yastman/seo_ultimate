# UK Batch Init + Meta + Research Copy

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Создать UK структуру, мета-теги и скопировать research для всех 47 категорий (без генерации контента)

**Architecture:** Batch выполнение через UK скиллы: init → meta → copy research

**Tech Stack:** UK skills, Bash

---

## Scope

**Готово (3):** aktivnaya-pena, antibitum, antimoshka

**К созданию (47):**
- akkumulyatornaya, aksessuary, aksessuary-dlya-naneseniya-sredstv, antidozhd
- apparaty-tornador, avtoshampuni, cherniteli-shin, glina-i-avtoskraby
- gubki-i-varezhki, keramika-dlya-diskov, keramika-i-zhidkoe-steklo, kisti-dlya-deteylinga
- kvik-deteylery, malyarniy-skotch, mekhovye, mikrofibra-i-tryapki
- moyka-i-eksterer, nabory, neytralizatory-zapakha, obezzhirivateli
- oborudovanie, ochistiteli-diskov, ochistiteli-dvigatelya, ochistiteli-kozhi
- ochistiteli-shin, ochistiteli-stekol, omyvatel, opt-i-b2b
- polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-pasty, polirovka
- pyatnovyvoditeli, raspyliteli-i-penniki, shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto
- silanty, sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi, tverdyy-vosk
- ukhod-za-intererom, ukhod-za-kozhey, ukhod-za-naruzhnym-plastikom, vedra-i-emkosti
- voski, zashchitnye-pokrytiya, zhidkiy-vosk

---

## Pipeline для каждой категории

```
/uk-content-init {slug}     → создаёт структуру + _clean.json
/uk-generate-meta {slug}    → создаёт _meta.json
copy RU research            → копирует RESEARCH_DATA.md из RU
```

---

## Task 1: Batch uk-content-init

**Действие:** Запустить `/uk-content-init` для каждой из 47 категорий

**Результат для каждой:**
- `uk/categories/{slug}/data/{slug}_clean.json`
- `uk/categories/{slug}/meta/` (пустая папка)
- `uk/categories/{slug}/content/` (пустая папка)
- `uk/categories/{slug}/research/CONTEXT.md`

**Проверка:**
```bash
ls uk/categories/ | wc -l
# Expected: 50
```

---

## Task 2: Batch uk-generate-meta

**Действие:** Запустить `/uk-generate-meta` для каждой из 47 категорий

**Результат для каждой:**
- `uk/categories/{slug}/meta/{slug}_meta.json`

**Проверка:**
```bash
find uk/categories -name "*_meta.json" | wc -l
# Expected: 50
```

---

## Task 3: Copy RU Research

**Действие:** Скопировать `RESEARCH_DATA.md` из RU категорий в UK

**Логика:**
1. Найти RU путь категории (может быть вложенная: `categories/parent/child/{slug}/`)
2. Скопировать `research/RESEARCH_DATA.md` в `uk/categories/{slug}/research/`

**Скрипт:**
```bash
for slug in $(jq -r '.categories | keys[]' uk/data/uk_keywords.json); do
  # Найти RU research
  ru_research=$(find categories -path "*/${slug}/research/RESEARCH_DATA.md" 2>/dev/null | head -1)
  if [ -n "$ru_research" ]; then
    mkdir -p "uk/categories/${slug}/research"
    cp "$ru_research" "uk/categories/${slug}/research/RESEARCH_DATA.md"
    echo "Copied: ${slug}"
  else
    echo "NOT FOUND: ${slug}"
  fi
done
```

**Проверка:**
```bash
find uk/categories -name "RESEARCH_DATA.md" | wc -l
```

---

## Task 4: Commit

```bash
git add uk/categories/
git commit -m "feat(uk): batch init + meta + research for 47 categories"
```

---

## Task 5: Update TODO

Отметить в `tasks/TODO_UK_CONTENT.md`:
- Все 47 категорий: `[~]` (init + meta done, content pending)

---

## Execution Strategy

**Вариант A: Последовательно (надёжно)**
- Запускать скиллы по одному
- Проверять результат после каждого batch

**Вариант B: Параллельные агенты (быстро)**
- Запустить 5-10 агентов параллельно
- Каждый обрабатывает группу категорий

**Рекомендация:** Вариант A для первых 5-10, затем B для остальных

---

## Acceptance Criteria

- [ ] 50 папок в `uk/categories/`
- [ ] 50 файлов `*_clean.json`
- [ ] 50 файлов `*_meta.json`
- [ ] Research скопирован где есть RU версия
- [ ] Commit создан
