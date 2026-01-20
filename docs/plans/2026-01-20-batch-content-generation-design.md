# Batch Content Generation Design

**Дата:** 2026-01-20
**Статус:** Draft

---

## Цель

Сгенерировать SEO-контент (buyer guide) для **20 категорий** через параллельные субагенты с автоматической валидацией.

---

## Исходные данные

### Категории для генерации (20 шт.)

Все категории имеют: `_clean.json` ✅ + `_meta.json` ✅ + `RESEARCH_DATA.md` ✅

| # | Slug | Research | Тип | Path |
|---|------|----------|-----|------|
| 1 | neytralizatory-zapakha | 32KB | Product | ukhod-za-intererom/neytralizatory-zapakha |
| 2 | nabory | 24KB | Product | aksessuary/nabory |
| 3 | voski | 20KB | Product | zashchitnye-pokrytiya/voski |
| 4 | akkumulyatornaya | 21KB | Product | polirovka/polirovalnye-mashinki/akkumulyatornaya |
| 5 | zhidkiy-vosk | 15KB | Product | zashchitnye-pokrytiya/voski/zhidkiy-vosk |
| 6 | tverdyy-vosk | 15KB | Product | zashchitnye-pokrytiya/voski/tverdyy-vosk |
| 7 | zashchitnye-pokrytiya | 15KB | **Hub** | zashchitnye-pokrytiya |
| 8 | polirol-dlya-stekla | 10KB | Product | moyka-i-eksterer/sredstva-dlya-stekol/polirol-dlya-stekla |
| 9 | vedra-i-emkosti | 9KB | Product | aksessuary/vedra-i-emkosti |
| 10 | opt-i-b2b | 7KB | **Hub** | opt-i-b2b |
| 11 | mekhovye | 6KB | Product | polirovka/polirovalnye-krugi/mekhovye |
| 12 | keramika-dlya-diskov | 5KB | Product | moyka-i-eksterer/sredstva-dlya-diskov-i-shin/keramika-dlya-diskov |
| 13 | kvik-deteylery | 5KB | Product | zashchitnye-pokrytiya/kvik-deteylery |
| 14 | ukhod-za-naruzhnym-plastikom | 5KB | Product | moyka-i-eksterer/ochistiteli-kuzova/ukhod-za-naruzhnym-plastikom |
| 15 | kisti-dlya-deteylinga | 5KB | Product | aksessuary/shchetki-i-kisti/kisti-dlya-deteylinga |
| 16 | shchetka-dlya-moyki-avto | 5KB | Product | aksessuary/shchetki-i-kisti/shchetka-dlya-moyki-avto |
| 17 | poliroli-dlya-plastika | 4KB | Product | ukhod-za-intererom/poliroli-dlya-plastika |
| 18 | ukhod-za-kozhey | 4KB | Product | ukhod-za-intererom/sredstva-dlya-kozhi/ukhod-za-kozhey |
| 19 | ukhod-za-intererom | 4KB | **Hub** | ukhod-za-intererom |
| 20 | silanty | 3KB | Product | zashchitnye-pokrytiya/silanty |

**Типы страниц:**
- **17 Product Pages** — buyer guide формат
- **3 Hub Pages** — zashchitnye-pokrytiya, opt-i-b2b, ukhod-za-intererom (отдельный шаблон)

---

## Архитектура

### Подход: Параллельные субагенты (5-6 одновременно)

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Agent (Orchestrator)                 │
│  - Распределяет категории по волнам                         │
│  - Запускает 5-6 субагентов параллельно                     │
│  - Собирает результаты после каждой волны                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Subagent 1   │     │  Subagent 2   │     │  Subagent N   │
│               │     │               │     │               │
│  1. Read data │     │  1. Read data │     │  1. Read data │
│  2. Generate  │     │  2. Generate  │     │  2. Generate  │
│  3. Validate  │     │  3. Validate  │     │  3. Validate  │
│  4. Fix       │     │  4. Fix       │     │  4. Fix       │
│  5. Save      │     │  5. Save      │     │  5. Save      │
└───────────────┘     └───────────────┘     └───────────────┘
```

---

## Распределение по волнам

### Wave 1 — богатый research (6 категорий)

| Slug | Research | Тип |
|------|----------|-----|
| neytralizatory-zapakha | 32KB | Product |
| nabory | 24KB | Product |
| akkumulyatornaya | 21KB | Product |
| voski | 20KB | Product |
| zhidkiy-vosk | 15KB | Product |
| tverdyy-vosk | 15KB | Product |

### Wave 2 — средний research (6 категорий)

| Slug | Research | Тип |
|------|----------|-----|
| zashchitnye-pokrytiya | 15KB | **Hub** |
| polirol-dlya-stekla | 10KB | Product |
| vedra-i-emkosti | 9KB | Product |
| opt-i-b2b | 7KB | **Hub** |
| mekhovye | 6KB | Product |
| keramika-dlya-diskov | 5KB | Product |

### Wave 3 — компактный research (6 категорий)

| Slug | Research | Тип |
|------|----------|-----|
| kvik-deteylery | 5KB | Product |
| ukhod-za-naruzhnym-plastikom | 5KB | Product |
| kisti-dlya-deteylinga | 5KB | Product |
| shchetka-dlya-moyki-avto | 5KB | Product |
| poliroli-dlya-plastika | 4KB | Product |
| ukhod-za-kozhey | 4KB | Product |

### Wave 4 — финальная (2 категории)

| Slug | Research | Тип |
|------|----------|-----|
| ukhod-za-intererom | 4KB | **Hub** |
| silanty | 3KB | Product |

---

## Workflow субагента

```
1. Read input files:
   - categories/{path}/data/{slug}_clean.json
   - categories/{path}/meta/{slug}_meta.json
   - categories/{path}/research/RESEARCH_DATA.md

2. Check page type (parent_id):
   - null → Hub Page → references/hub-pages.md
   - not null → Product Page → buyer guide

3. Generate content:
   - Follow content-generator skill v3.1
   - H1 from _meta.json (без "Купить")
   - Minimum 1 H2 with secondary keyword
   - FAQ from research or templates
   - No citations, percentages, brands

4. Create content folder if needed:
   - mkdir -p categories/{path}/content/

5. Save draft:
   - categories/{path}/content/{slug}_ru.md

6. Run validation:
   - python3 scripts/validate_content.py {path} "{keyword}" --mode seo
   - python3 scripts/check_keyword_density.py {path}
   - python3 scripts/check_water_natasha.py {path}

7. Fix issues (до 3 попыток):
   - Stem density > 2.5% → synonyms
   - Nausea > 3.5 → diversify
   - Missing keyword in H2 → adjust

8. Report: PASS / WARN / FAIL + metrics
```

---

## Валидация

### Критерии успеха per category

| Метрика | Цель | Блокер |
|---------|------|--------|
| validate_content.py | PASS or WARN | FAIL |
| Stem density | ≤2.5% | >3.0% |
| Classic nausea | ≤3.5 | >4.0 |
| Content size | ≥4KB | <2KB |
| FAQ count | 3-5 | <3 |

### Overall success

- **20/20** категорий с контентом ≥4KB
- **0** FAIL статусов
- Все валидации пройдены

---

## Команды выполнения

### Wave 1

```
Task tool × 6 субагентов:
- neytralizatory-zapakha
- nabory
- akkumulyatornaya
- voski
- zhidkiy-vosk
- tverdyy-vosk
```

### Проверка после волны

```bash
for slug in neytralizatory-zapakha nabory akkumulyatornaya voski zhidkiy-vosk tverdyy-vosk; do
  echo "=== $slug ==="
  content=$(ls categories/**/$slug/content/${slug}_ru.md 2>/dev/null)
  [ -n "$content" ] && wc -c "$content" || echo "NO CONTENT"
done
```

---

## После выполнения

1. Обновить `tasks/TODO_CONTENT.md`
2. Запустить `/quality-gate` для каждой категории
3. Перейти к `/uk-content-init` для украинских версий
4. Финальный `/deploy-to-opencart`

---

**Version:** 1.1
**Changes:** Расширен до 20 категорий (полный список без контента)
