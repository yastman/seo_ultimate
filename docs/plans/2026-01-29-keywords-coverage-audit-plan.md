# Keywords Coverage Audit via Content-Reviewer

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Проверить и исправить keywords coverage во всех 53 RU категориях через существующий скилл content-reviewer.

**Architecture:** Воркеры параллельно запускают content-reviewer для групп категорий. Скилл сам находит missing keywords и фиксит их, используя только факты из RESEARCH_DATA.md.

**Tech Stack:** content-reviewer skill, spawn-claude, tmux

---

## Список всех RU категорий (53)

```
# L1 категории
aksessuary
zashchitnye-pokrytiya
oborudovanie
ukhod-za-intererom
polirovka
moyka-i-eksterer
glavnaya
opt-i-b2b

# L2 категории (aksessuary)
aksessuary/nabory
aksessuary/aksessuary-dlya-naneseniya-sredstv
aksessuary/gubki-i-varezhki
aksessuary/malyarniy-skotch
aksessuary/raspyliteli-i-penniki
aksessuary/vedra-i-emkosti
aksessuary/mikrofibra-i-tryapki
aksessuary/shchetki-i-kisti

# L3 категории (aksessuary)
aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto
aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga

# L2 категории (zashchitnye-pokrytiya)
zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo
zashchitnye-pokrytiya/kvik-deteylery
zashchitnye-pokrytiya/silanty
zashchitnye-pokrytiya/voski

# L3 категории (zashchitnye-pokrytiya)
zashchitnye-pokrytiya/voski/tverdyy-vosk
zashchitnye-pokrytiya/voski/zhidkiy-vosk

# L2 категории (oborudovanie)
oborudovanie/apparaty-tornador

# L2 категории (ukhod-za-intererom)
ukhod-za-intererom/neytralizatory-zapakha
ukhod-za-intererom/poliroli-dlya-plastika
ukhod-za-intererom/pyatnovyvoditeli
ukhod-za-intererom/sredstva-dlya-kozhi
ukhod-za-intererom/sredstva-dlya-khimchistki-salona

# L3 категории (ukhod-za-intererom)
ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi
ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey

# L2 категории (polirovka)
polirovka/polirovalnye-pasty
polirovka/polirovalnye-mashinki
polirovka/polirovalnye-krugi

# L3 категории (polirovka)
polirovka/polirovalnye-mashinki/akkumulyatornaya
polirovka/polirovalnye-krugi/mekhovye

# L2 категории (moyka-i-eksterer)
moyka-i-eksterer/avtoshampuni
moyka-i-eksterer/ochistiteli-dvigatelya
moyka-i-eksterer/ochistiteli-kuzova
moyka-i-eksterer/sredstva-dlya-diskov-i-shin
moyka-i-eksterer/sredstva-dlya-stekol

# L3 категории (moyka-i-eksterer/avtoshampuni)
moyka-i-eksterer/avtoshampuni/aktivnaya-pena
moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki

# L3 категории (moyka-i-eksterer/ochistiteli-kuzova)
moyka-i-eksterer/ochistiteli-kuzova/antibitum
moyka-i-eksterer/ochistiteli-kuzova/antimoshka
moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby
moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli
moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom

# L3 категории (moyka-i-eksterer/sredstva-dlya-diskov-i-shin)
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov
moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin

# L3 категории (moyka-i-eksterer/sredstva-dlya-stekol)
moyka-i-eksterer/sredstva-dlya-stekol/antidozhd
moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol
moyka-i-eksterer/sredstva-dlya-stekol/omyvatel
moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla
```

---

## Распределение по воркерам (4 воркера × ~13 категорий)

### W1: Aksessuary + Zashchitnye-pokrytiya (13 категорий)

```
aksessuary
aksessuary/nabory
aksessuary/aksessuary-dlya-naneseniya-sredstv
aksessuary/gubki-i-varezhki
aksessuary/malyarniy-skotch
aksessuary/raspyliteli-i-penniki
aksessuary/vedra-i-emkosti
aksessuary/mikrofibra-i-tryapki
aksessuary/shchetki-i-kisti
aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto
aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga
zashchitnye-pokrytiya
zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo
```

### W2: Zashchitnye-pokrytiya (остаток) + Oborudovanie + Ukhod-za-intererom (13 категорий)

```
zashchitnye-pokrytiya/kvik-deteylery
zashchitnye-pokrytiya/silanty
zashchitnye-pokrytiya/voski
zashchitnye-pokrytiya/voski/tverdyy-vosk
zashchitnye-pokrytiya/voski/zhidkiy-vosk
oborudovanie
oborudovanie/apparaty-tornador
ukhod-za-intererom
ukhod-za-intererom/neytralizatory-zapakha
ukhod-za-intererom/poliroli-dlya-plastika
ukhod-za-intererom/pyatnovyvoditeli
ukhod-za-intererom/sredstva-dlya-kozhi
ukhod-za-intererom/sredstva-dlya-khimchistki-salona
```

### W3: Ukhod-za-intererom (остаток) + Polirovka + Moyka-i-eksterer (начало) (13 категорий)

```
ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi
ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey
polirovka
polirovka/polirovalnye-pasty
polirovka/polirovalnye-mashinki
polirovka/polirovalnye-krugi
polirovka/polirovalnye-mashinki/akkumulyatornaya
polirovka/polirovalnye-krugi/mekhovye
moyka-i-eksterer
moyka-i-eksterer/avtoshampuni
moyka-i-eksterer/ochistiteli-dvigatelya
moyka-i-eksterer/ochistiteli-kuzova
moyka-i-eksterer/sredstva-dlya-diskov-i-shin
```

### W4: Moyka-i-eksterer (остаток) + Glavnaya + Opt (14 категорий)

```
moyka-i-eksterer/sredstva-dlya-stekol
moyka-i-eksterer/avtoshampuni/aktivnaya-pena
moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki
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
glavnaya
opt-i-b2b
```

---

## Task 1: Запустить W1

**Команда:**

```bash
spawn-claude "W1: Проверка keywords coverage.

/superpowers:executing-plans docs/plans/2026-01-29-keywords-coverage-audit-plan.md

Выполни ТОЛЬКО категории W1:
- aksessuary
- aksessuary/nabory
- aksessuary/aksessuary-dlya-naneseniya-sredstv
- aksessuary/gubki-i-varezhki
- aksessuary/malyarniy-skotch
- aksessuary/raspyliteli-i-penniki
- aksessuary/vedra-i-emkosti
- aksessuary/mikrofibra-i-tryapki
- aksessuary/shchetki-i-kisti
- aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto
- aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga
- zashchitnye-pokrytiya
- zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo

Для каждой: /content-reviewer {path}

Пиши лог в data/generated/audit-logs/W1_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

---

## Task 2: Запустить W2

**Команда:**

```bash
spawn-claude "W2: Проверка keywords coverage.

/superpowers:executing-plans docs/plans/2026-01-29-keywords-coverage-audit-plan.md

Выполни ТОЛЬКО категории W2:
- zashchitnye-pokrytiya/kvik-deteylery
- zashchitnye-pokrytiya/silanty
- zashchitnye-pokrytiya/voski
- zashchitnye-pokrytiya/voski/tverdyy-vosk
- zashchitnye-pokrytiya/voski/zhidkiy-vosk
- oborudovanie
- oborudovanie/apparaty-tornador
- ukhod-za-intererom
- ukhod-za-intererom/neytralizatory-zapakha
- ukhod-za-intererom/poliroli-dlya-plastika
- ukhod-za-intererom/pyatnovyvoditeli
- ukhod-za-intererom/sredstva-dlya-kozhi
- ukhod-za-intererom/sredstva-dlya-khimchistki-salona

Для каждой: /content-reviewer {path}

Пиши лог в data/generated/audit-logs/W2_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

---

## Task 3: Запустить W3

**Команда:**

```bash
spawn-claude "W3: Проверка keywords coverage.

/superpowers:executing-plans docs/plans/2026-01-29-keywords-coverage-audit-plan.md

Выполни ТОЛЬКО категории W3:
- ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi
- ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey
- polirovka
- polirovka/polirovalnye-pasty
- polirovka/polirovalnye-mashinki
- polirovka/polirovalnye-krugi
- polirovka/polirovalnye-mashinki/akkumulyatornaya
- polirovka/polirovalnye-krugi/mekhovye
- moyka-i-eksterer
- moyka-i-eksterer/avtoshampuni
- moyka-i-eksterer/ochistiteli-dvigatelya
- moyka-i-eksterer/ochistiteli-kuzova
- moyka-i-eksterer/sredstva-dlya-diskov-i-shin

Для каждой: /content-reviewer {path}

Пиши лог в data/generated/audit-logs/W3_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

---

## Task 4: Запустить W4

**Команда:**

```bash
spawn-claude "W4: Проверка keywords coverage.

/superpowers:executing-plans docs/plans/2026-01-29-keywords-coverage-audit-plan.md

Выполни ТОЛЬКО категории W4:
- moyka-i-eksterer/sredstva-dlya-stekol
- moyka-i-eksterer/avtoshampuni/aktivnaya-pena
- moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki
- moyka-i-eksterer/ochistiteli-kuzova/antibitum
- moyka-i-eksterer/ochistiteli-kuzova/antimoshka
- moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby
- moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli
- moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom
- moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin
- moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov
- moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov
- moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin
- moyka-i-eksterer/sredstva-dlya-stekol/antidozhd
- moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol
- moyka-i-eksterer/sredstva-dlya-stekol/omyvatel
- moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla
- glavnaya
- opt-i-b2b

Для каждой: /content-reviewer {path}

Пиши лог в data/generated/audit-logs/W4_log.md

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

---

## Task 5: Собрать результаты и закоммитить

**После завершения всех воркеров:**

**Step 1: Проверить логи**

```bash
cat data/generated/audit-logs/W1_log.md
cat data/generated/audit-logs/W2_log.md
cat data/generated/audit-logs/W3_log.md
cat data/generated/audit-logs/W4_log.md
```

**Step 2: Проверить изменения**

```bash
git status
git diff --stat categories/
```

**Step 3: Закоммитить**

```bash
git add categories/*/content/*.md
git add categories/*/*/content/*.md
git add categories/*/*/*/content/*.md
git add data/generated/audit-logs/

git commit -m "fix: add missing keywords to RU content (53 categories)

Reviewed all 53 RU categories via content-reviewer skill.
Fixed missing primary/secondary keywords using RESEARCH_DATA.md.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Checklist

- [ ] Task 1: Запустить W1 (13 категорий)
- [ ] Task 2: Запустить W2 (13 категорий)
- [ ] Task 3: Запустить W3 (13 категорий)
- [ ] Task 4: Запустить W4 (14 категорий)
- [ ] Task 5: Собрать результаты и закоммитить
