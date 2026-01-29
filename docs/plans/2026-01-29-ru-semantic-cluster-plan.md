# RU Semantic Cluster Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Кластеризация ключей по стемам для всех 53 RU категорий с переносом variants в synonyms.

**Architecture:** 5 параллельных воркеров, каждый обрабатывает ~10-11 категорий через `/semantic-cluster`. Full режим: обновление `_clean.json` и `_meta.json`.

**Tech Stack:** `/semantic-cluster` skill, `python3 scripts/validate_meta.py`

**Design:** [2026-01-29-ru-semantic-cluster-design.md](2026-01-29-ru-semantic-cluster-design.md)

---

## Task 1: W1 — aksessuary + glavnaya (11 категорий)

**Files:**
- Modify: `categories/aksessuary/data/aksessuary_clean.json`
- Modify: `categories/aksessuary/meta/aksessuary_meta.json`
- (и так для каждой категории ниже)
- Create: `data/generated/audit-logs/W1_log.md`

**Step 1: Создать лог-файл**

```bash
mkdir -p data/generated/audit-logs
echo "# W1 Semantic Cluster Log" > data/generated/audit-logs/W1_log.md
echo "" >> data/generated/audit-logs/W1_log.md
echo "Дата: $(date '+%Y-%m-%d %H:%M')" >> data/generated/audit-logs/W1_log.md
```

**Step 2: Обработать aksessuary**

Run: `/semantic-cluster aksessuary`

Логировать результат:
```markdown
## aksessuary
- Найдено дублей: X
- Перенесено в synonyms: Y
- Canonical: [список]
```

**Step 3: Обработать aksessuary/aksessuary-dlya-naneseniya-sredstv**

Run: `/semantic-cluster aksessuary/aksessuary-dlya-naneseniya-sredstv`

**Step 4: Обработать aksessuary/gubki-i-varezhki**

Run: `/semantic-cluster aksessuary/gubki-i-varezhki`

**Step 5: Обработать aksessuary/malyarniy-skotch**

Run: `/semantic-cluster aksessuary/malyarniy-skotch`

**Step 6: Обработать aksessuary/mikrofibra-i-tryapki**

Run: `/semantic-cluster aksessuary/mikrofibra-i-tryapki`

**Step 7: Обработать aksessuary/nabory**

Run: `/semantic-cluster aksessuary/nabory`

**Step 8: Обработать aksessuary/raspyliteli-i-penniki**

Run: `/semantic-cluster aksessuary/raspyliteli-i-penniki`

**Step 9: Обработать aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga**

Run: `/semantic-cluster aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga`

**Step 10: Обработать aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto**

Run: `/semantic-cluster aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto`

**Step 11: Обработать aksessuary/vedra-i-emkosti**

Run: `/semantic-cluster aksessuary/vedra-i-emkosti`

**Step 12: Обработать glavnaya**

Run: `/semantic-cluster glavnaya`

**Step 13: Валидация**

```bash
python3 scripts/validate_meta.py categories/aksessuary/meta/aksessuary_meta.json
python3 scripts/validate_meta.py categories/glavnaya/meta/glavnaya_meta.json
```

Expected: Все валидации PASS

**Step 14: Финализация лога**

Добавить итог в лог:
```markdown
---
## Итог
- Обработано категорий: 11
- Всего дублей: X
- Всего перенесено: Y
```

**НЕ ДЕЛАТЬ git commit — коммиты делает оркестратор**

---

## Task 2: W2 — moyka-i-eksterer часть 1 (11 категорий)

**Files:**
- Modify: `categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json`
- Modify: `categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json`
- (и так для каждой категории ниже)
- Create: `data/generated/audit-logs/W2_log.md`

**Step 1: Создать лог-файл**

```bash
mkdir -p data/generated/audit-logs
echo "# W2 Semantic Cluster Log" > data/generated/audit-logs/W2_log.md
echo "" >> data/generated/audit-logs/W2_log.md
echo "Дата: $(date '+%Y-%m-%d %H:%M')" >> data/generated/audit-logs/W2_log.md
```

**Step 2: Обработать moyka-i-eksterer**

Run: `/semantic-cluster moyka-i-eksterer`

**Step 3: Обработать moyka-i-eksterer/avtoshampuni**

Run: `/semantic-cluster moyka-i-eksterer/avtoshampuni`

**Step 4: Обработать moyka-i-eksterer/avtoshampuni/aktivnaya-pena**

Run: `/semantic-cluster moyka-i-eksterer/avtoshampuni/aktivnaya-pena`

**Step 5: Обработать moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki**

Run: `/semantic-cluster moyka-i-eksterer/avtoshampuni/shampuni-dlya-ruchnoy-moyki`

**Step 6: Обработать moyka-i-eksterer/ochistiteli-dvigatelya**

Run: `/semantic-cluster moyka-i-eksterer/ochistiteli-dvigatelya`

**Step 7: Обработать moyka-i-eksterer/ochistiteli-kuzova/antibitum**

Run: `/semantic-cluster moyka-i-eksterer/ochistiteli-kuzova/antibitum`

**Step 8: Обработать moyka-i-eksterer/ochistiteli-kuzova/antimoshka**

Run: `/semantic-cluster moyka-i-eksterer/ochistiteli-kuzova/antimoshka`

**Step 9: Обработать moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby**

Run: `/semantic-cluster moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby`

**Step 10: Обработать moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli**

Run: `/semantic-cluster moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli`

**Step 11: Обработать moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom**

Run: `/semantic-cluster moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom`

**Step 12: Обработать moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin**

Run: `/semantic-cluster moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin`

**Step 13: Валидация**

```bash
python3 scripts/validate_meta.py categories/moyka-i-eksterer/meta/moyka-i-eksterer_meta.json
```

Expected: PASS

**Step 14: Финализация лога**

**НЕ ДЕЛАТЬ git commit**

---

## Task 3: W3 — moyka-i-eksterer часть 2 + oborudovanie (11 категорий)

**Files:**
- Create: `data/generated/audit-logs/W3_log.md`

**Step 1: Создать лог-файл**

```bash
mkdir -p data/generated/audit-logs
echo "# W3 Semantic Cluster Log" > data/generated/audit-logs/W3_log.md
```

**Step 2: Обработать moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov**

Run: `/semantic-cluster moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov`

**Step 3: Обработать moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov**

Run: `/semantic-cluster moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov`

**Step 4: Обработать moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin**

Run: `/semantic-cluster moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin`

**Step 5: Обработать moyka-i-eksterer/sredstva-dlya-stekol/antidozhd**

Run: `/semantic-cluster moyka-i-eksterer/sredstva-dlya-stekol/antidozhd`

**Step 6: Обработать moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol**

Run: `/semantic-cluster moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol`

**Step 7: Обработать moyka-i-eksterer/sredstva-dlya-stekol/omyvatel**

Run: `/semantic-cluster moyka-i-eksterer/sredstva-dlya-stekol/omyvatel`

**Step 8: Обработать moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla**

Run: `/semantic-cluster moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla`

**Step 9: Обработать oborudovanie**

Run: `/semantic-cluster oborudovanie`

**Step 10: Обработать oborudovanie/apparaty-tornador**

Run: `/semantic-cluster oborudovanie/apparaty-tornador`

**Step 11: Обработать opt-i-b2b**

Run: `/semantic-cluster opt-i-b2b`

**Step 12: Обработать polirovka**

Run: `/semantic-cluster polirovka`

**Step 13: Валидация и финализация лога**

**НЕ ДЕЛАТЬ git commit**

---

## Task 4: W4 — polirovka + ukhod-za-intererom (11 категорий)

**Files:**
- Create: `data/generated/audit-logs/W4_log.md`

**Step 1: Создать лог-файл**

```bash
mkdir -p data/generated/audit-logs
echo "# W4 Semantic Cluster Log" > data/generated/audit-logs/W4_log.md
```

**Step 2: Обработать polirovka/polirovalnye-krugi**

Run: `/semantic-cluster polirovka/polirovalnye-krugi`

**Step 3: Обработать polirovka/polirovalnye-krugi/mekhovye**

Run: `/semantic-cluster polirovka/polirovalnye-krugi/mekhovye`

**Step 4: Обработать polirovka/polirovalnye-mashinki**

Run: `/semantic-cluster polirovka/polirovalnye-mashinki`

**Step 5: Обработать polirovka/polirovalnye-mashinki/akkumulyatornaya**

Run: `/semantic-cluster polirovka/polirovalnye-mashinki/akkumulyatornaya`

**Step 6: Обработать polirovka/polirovalnye-pasty**

Run: `/semantic-cluster polirovka/polirovalnye-pasty`

**Step 7: Обработать ukhod-za-intererom**

Run: `/semantic-cluster ukhod-za-intererom`

**Step 8: Обработать ukhod-za-intererom/neytralizatory-zapakha**

Run: `/semantic-cluster ukhod-za-intererom/neytralizatory-zapakha`

**Step 9: Обработать ukhod-za-intererom/poliroli-dlya-plastika**

Run: `/semantic-cluster ukhod-za-intererom/poliroli-dlya-plastika`

**Step 10: Обработать ukhod-za-intererom/pyatnovyvoditeli**

Run: `/semantic-cluster ukhod-za-intererom/pyatnovyvoditeli`

**Step 11: Обработать ukhod-za-intererom/sredstva-dlya-khimchistki-salona**

Run: `/semantic-cluster ukhod-za-intererom/sredstva-dlya-khimchistki-salona`

**Step 12: Обработать ukhod-za-intererom/sredstva-dlya-kozhi**

Run: `/semantic-cluster ukhod-za-intererom/sredstva-dlya-kozhi`

**Step 13: Валидация и финализация лога**

**НЕ ДЕЛАТЬ git commit**

---

## Task 5: W5 — ukhod-za-kozhi + zashchitnye-pokrytiya (9 категорий)

**Files:**
- Create: `data/generated/audit-logs/W5_log.md`

**Step 1: Создать лог-файл**

```bash
mkdir -p data/generated/audit-logs
echo "# W5 Semantic Cluster Log" > data/generated/audit-logs/W5_log.md
```

**Step 2: Обработать ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi**

Run: `/semantic-cluster ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi`

**Step 3: Обработать ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey**

Run: `/semantic-cluster ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey`

**Step 4: Обработать zashchitnye-pokrytiya**

Run: `/semantic-cluster zashchitnye-pokrytiya`

**Step 5: Обработать zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo**

Run: `/semantic-cluster zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo`

**Step 6: Обработать zashchitnye-pokrytiya/kvik-deteylery**

Run: `/semantic-cluster zashchitnye-pokrytiya/kvik-deteylery`

**Step 7: Обработать zashchitnye-pokrytiya/silanty**

Run: `/semantic-cluster zashchitnye-pokrytiya/silanty`

**Step 8: Обработать zashchitnye-pokrytiya/voski**

Run: `/semantic-cluster zashchitnye-pokrytiya/voski`

**Step 9: Обработать zashchitnye-pokrytiya/voski/tverdyy-vosk**

Run: `/semantic-cluster zashchitnye-pokrytiya/voski/tverdyy-vosk`

**Step 10: Обработать zashchitnye-pokrytiya/voski/zhidkiy-vosk**

Run: `/semantic-cluster zashchitnye-pokrytiya/voski/zhidkiy-vosk`

**Step 11: Валидация и финализация лога**

**НЕ ДЕЛАТЬ git commit**

---

## Запуск через /parallel

```
/parallel docs/plans/2026-01-29-ru-semantic-cluster-plan.md
W1: Task 1
W2: Task 2
W3: Task 3
W4: Task 4
W5: Task 5
```

---

## После завершения воркеров (оркестратор)

**Step 1: Проверить логи**

```bash
cat data/generated/audit-logs/W1_log.md
cat data/generated/audit-logs/W2_log.md
cat data/generated/audit-logs/W3_log.md
cat data/generated/audit-logs/W4_log.md
cat data/generated/audit-logs/W5_log.md
```

**Step 2: Проверить изменения**

```bash
git diff --stat categories/
```

**Step 3: Валидация всех meta**

```bash
python3 scripts/validate_meta.py --all
python3 scripts/audit_keyword_consistency.py
```

Expected: Все PASS

**Step 4: Коммит**

```bash
git add categories/ data/generated/audit-logs/
git commit -m "cluster(ru): semantic clustering for 53 categories

- Moved stem variants to synonyms with use_in: lsi
- Updated keywords_in_content to canonical forms only
- 5 parallel workers

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```
