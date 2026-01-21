# Content Revision v4.0: 50 Categories via Subagent

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Ревизия контента 50 категорий Ultimate.net.ua через субагента `content-reviewer`.

**Architecture:**
- Субагент `content-reviewer` выполняет полный цикл ревизии одной категории
- Параллельный запуск до 3 агентов одновременно
- Human review между батчами, коммиты после каждого батча

**Tech Stack:** Субагент `content-reviewer` (Opus 4.5), Python validators, Task tool для параллельного запуска.

**Key Changes v4.0:**
- Автоматизация через субагента вместо ручных Steps 1-9
- Параллельная обработка (до 3 категорий за раз)
- Обновлены статусы: 4 категории уже проревьюированы

---

## How It Works

### One Agent Call = Full Review

```
Task tool → content-reviewer {path} → Agent does:
  1. Read 4 data files
  2. Run 4 validators
  3. Keywords coverage check
  4. Facts vs Research check
  5. 6 qualitative criteria
  6. Fix BLOCKERs and WARNINGs
  7. Re-validate
  8. Output verdict report
```

### Parallel Execution

```python
# До 3 категорий параллельно
Task(content-reviewer, "path1")  # parallel
Task(content-reviewer, "path2")  # parallel
Task(content-reviewer, "path3")  # parallel
# Wait for all → review outputs → commit batch
```

---

## Progress Tracking

| Batch | Categories | Done | Status |
|-------|------------|------|--------|
| 1. Мойка и экстерьер | 18 | 4 | 🟡 in progress |
| 2. Аксессуары | 10 | 0 | ⬜ pending |
| 3. Уход за интерьером | 8 | 0 | ⬜ pending |
| 4. Защитные покрытия | 7 | 0 | ⬜ pending |
| 5. Полировка | 4 | 0 | ⬜ pending |
| 6. Оборудование и Опт | 3 | 0 | ⬜ pending |
| **TOTAL** | **50** | **4** | **8%** |

---

## Task 1: Batch 1 — Мойка и экстерьер (14 remaining)

**Already done (4):**
- ✅ moyka-i-eksterer (Hub)
- ✅ avtoshampuni (Hub)
- ✅ aktivnaya-pena (Product)
- ✅ shampuni-dlya-ruchnoy-moyki (Product)

**Step 1: Run 3 agents in parallel**

```
content-reviewer moyka-i-eksterer/ochistiteli-dvigatelya
content-reviewer moyka-i-eksterer/ochistiteli-kuzova/glina-i-avtoskraby
content-reviewer moyka-i-eksterer/ochistiteli-kuzova/antibitum
```

**Step 2: Review outputs, verify fixes are good**

Check git diff for each category.

**Step 3: Run next 3 agents**

```
content-reviewer moyka-i-eksterer/ochistiteli-kuzova/antimoshka
content-reviewer moyka-i-eksterer/ochistiteli-kuzova/obezzhirivateli
content-reviewer moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom
```

**Step 4: Review outputs**

**Step 5: Run next 3 agents**

```
content-reviewer moyka-i-eksterer/sredstva-dlya-diskov-i-shin/cherniteli-shin
content-reviewer moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-diskov
content-reviewer moyka-i-eksterer/sredstva-dlya-diskov-i-shin/ochistiteli-shin
```

**Step 6: Review outputs**

**Step 7: Run next 3 agents**

```
content-reviewer moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov
content-reviewer moyka-i-eksterer/sredstva-dlya-stekol/ochistiteli-stekol
content-reviewer moyka-i-eksterer/sredstva-dlya-stekol/antidozhd
```

**Step 8: Review outputs**

**Step 9: Run last 2 agents**

```
content-reviewer moyka-i-eksterer/sredstva-dlya-stekol/omyvatel
content-reviewer moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla
```

**Step 10: Review and commit batch**

```bash
git add categories/moyka-i-eksterer/
git commit -m "review(content): batch 1 moyka-i-eksterer - 18 categories validated v4.0"
```

---

## Task 2: Batch 2 — Аксессуары (10 categories)

**Step 1: Run 3 agents**

```
content-reviewer aksessuary
content-reviewer aksessuary/mikrofibra-i-tryapki
content-reviewer aksessuary/gubki-i-varezhki
```

**Step 2: Review outputs**

**Step 3: Run 3 agents**

```
content-reviewer aksessuary/raspyliteli-i-penniki
content-reviewer aksessuary/aksessuary-dlya-naneseniya-sredstv
content-reviewer aksessuary/nabory
```

**Step 4: Review outputs**

**Step 5: Run 3 agents**

```
content-reviewer aksessuary/vedra-i-emkosti
content-reviewer aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto
content-reviewer aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga
```

**Step 6: Review outputs**

**Step 7: Run last agent**

```
content-reviewer aksessuary/malyarniy-skotch
```

**Step 8: Commit batch**

```bash
git add categories/aksessuary/
git commit -m "review(content): batch 2 aksessuary - 10 categories validated v4.0"
```

---

## Task 3: Batch 3 — Уход за интерьером (8 categories)

**Step 1: Run 3 agents**

```
content-reviewer ukhod-za-intererom
content-reviewer ukhod-za-intererom/sredstva-dlya-khimchistki-salona
content-reviewer ukhod-za-intererom/sredstva-dlya-kozhi
```

**Step 2: Review outputs**

**Step 3: Run 3 agents**

```
content-reviewer ukhod-za-intererom/sredstva-dlya-kozhi/ochistiteli-kozhi
content-reviewer ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey
content-reviewer ukhod-za-intererom/poliroli-dlya-plastika
```

**Step 4: Review outputs**

**Step 5: Run 2 agents**

```
content-reviewer ukhod-za-intererom/pyatnovyvoditeli
content-reviewer ukhod-za-intererom/neytralizatory-zapakha
```

**Step 6: Commit batch**

```bash
git add categories/ukhod-za-intererom/
git commit -m "review(content): batch 3 ukhod-za-intererom - 8 categories validated v4.0"
```

---

## Task 4: Batch 4 — Защитные покрытия (7 categories)

**Step 1: Run 3 agents**

```
content-reviewer zashchitnye-pokrytiya
content-reviewer zashchitnye-pokrytiya/keramika-i-zhidkoe-steklo
content-reviewer zashchitnye-pokrytiya/voski
```

**Step 2: Review outputs**

**Step 3: Run 3 agents**

```
content-reviewer zashchitnye-pokrytiya/voski/tverdyy-vosk
content-reviewer zashchitnye-pokrytiya/voski/zhidkiy-vosk
content-reviewer zashchitnye-pokrytiya/silanty
```

**Step 4: Review outputs**

**Step 5: Run last agent**

```
content-reviewer zashchitnye-pokrytiya/kvik-deteylery
```

**Step 6: Commit batch**

```bash
git add categories/zashchitnye-pokrytiya/
git commit -m "review(content): batch 4 zashchitnye-pokrytiya - 7 categories validated v4.0"
```

---

## Task 5: Batch 5 — Полировка (4 categories)

**Step 1: Run 3 agents**

```
content-reviewer polirovka
content-reviewer polirovka/polirovalnye-pasty
content-reviewer polirovka/polirovalnye-krugi/mekhovye
```

**Step 2: Review outputs**

**Step 3: Run last agent**

```
content-reviewer polirovka/polirovalnye-mashinki/akkumulyatornaya
```

**Step 4: Commit batch**

```bash
git add categories/polirovka/
git commit -m "review(content): batch 5 polirovka - 4 categories validated v4.0"
```

---

## Task 6: Batch 6 — Оборудование и Опт (3 categories)

**Step 1: Run all 3 agents**

```
content-reviewer oborudovanie
content-reviewer oborudovanie/apparaty-tornador
content-reviewer opt-i-b2b
```

**Step 2: Review outputs**

**Step 3: Commit batch**

```bash
git add categories/oborudovanie/ categories/opt-i-b2b/
git commit -m "review(content): batch 6 oborudovanie + opt - 3 categories validated v4.0"
```

---

## Task 7: Final Validation

**Step 1: Run full validation**

```bash
python3 scripts/validate_meta.py --all
```

**Step 2: Spot-check keyword distribution**

```bash
# Pick 5 random categories, verify keywords present
```

**Step 3: Final commit**

```bash
git commit -m "review(content): complete revision of 50 categories v4.0"
```

---

## Execution Checklist

| Task | Batch | Categories | Status |
|------|-------|------------|--------|
| 1 | Мойка и экстерьер | 14 remaining | ⬜ |
| 2 | Аксессуары | 10 | ⬜ |
| 3 | Уход за интерьером | 8 | ⬜ |
| 4 | Защитные покрытия | 7 | ⬜ |
| 5 | Полировка | 4 | ⬜ |
| 6 | Оборудование и Опт | 3 | ⬜ |
| 7 | Final Validation | — | ⬜ |

---

## Reference: Agent Invocation

```python
# Single category
Task(
    subagent_type="content-reviewer",
    prompt="moyka-i-eksterer/ochistiteli-dvigatelya",
    description="Review ochistiteli-dvigatelya"
)

# Parallel (3 at once)
Task(content-reviewer, "path1")  # Call 1
Task(content-reviewer, "path2")  # Call 2
Task(content-reviewer, "path3")  # Call 3
# All in same message = parallel execution
```

---

## Reference: What Agent Does

Субагент `content-reviewer` автоматически:

1. **Читает 4 файла:** `_clean.json`, `_meta.json`, `RESEARCH_DATA.md`, `_ru.md`
2. **Запускает 4 валидатора:** meta, content, density, water
3. **Проверяет Keywords:** primary 100%, secondary/supporting ≥80%
4. **Сверяет Facts vs Research:** RESEARCH_DATA.md = источник истины
5. **Оценивает 6 качественных критериев:** intro, обращения, паттерны, таблицы, FAQ, buyer-oriented
6. **Исправляет BLOCKERs:** H1, how-to, keywords, facts
7. **Исправляет WARNINGs:** вода, паттерны, обращения
8. **Re-validates:** запускает валидаторы повторно
9. **Выводит verdict report**

**Агент НЕ коммитит** — коммит делается вручную после review.

---

**Plan Version:** 4.0 | **Created:** 2026-01-21

**Changelog v4.0:**
- Автоматизация через субагента `content-reviewer`
- Параллельный запуск до 3 агентов
- Обновлены статусы: 4/50 категорий done
- Убраны ручные Steps 1-9 (теперь внутри агента)
- Добавлен Reference раздел
