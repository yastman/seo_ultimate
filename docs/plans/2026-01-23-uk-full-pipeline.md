# UK Full Pipeline: Meta + Content

> **For Claude:** Execute phases sequentially. Use parallel agents within each phase.

**Goal:** Валидировать мета-теги и сгенерировать контент для 47 UK категорий

**Architecture:** Two-phase pipeline with validation checkpoints

---

## Phase 1: Meta Tags Validation

### Task 1.1: Validate Existing Meta

Мета-теги уже сгенерированы. Проверить соответствие SEO порогам.

```bash
# Batch validation
for slug in $(ls uk/categories/); do
  meta_file="uk/categories/${slug}/meta/${slug}_meta.json"
  if [ -f "$meta_file" ]; then
    python3 scripts/validate_meta.py "$meta_file" --lang uk 2>&1 | grep -E "(PASS|FAIL|WARNING|Title|Description)"
  fi
done
```

**SEO пороги (UK):**
| Метрика | Норма | BLOCKER |
|---------|-------|---------|
| Title | 50-60 chars | >70 |
| Description | 120-160 chars | <100 or >160 |
| H1 | БЕЗ "Купити" | Contains |
| Title | С "Купити" | Missing |

### Task 1.2: Fix Failed Meta

Для категорий с FAIL:
```
/uk-generate-meta {slug}
```

### Task 1.3: Meta Validation Report

```bash
# Generate report
echo "# UK Meta Validation Report" > tasks/reports/UK_META_VALIDATION.md
echo "Date: $(date +%Y-%m-%d)" >> tasks/reports/UK_META_VALIDATION.md
echo "" >> tasks/reports/UK_META_VALIDATION.md

for slug in $(ls uk/categories/); do
  result=$(python3 scripts/validate_meta.py "uk/categories/${slug}/meta/${slug}_meta.json" --lang uk 2>&1)
  status=$(echo "$result" | grep -oE "(PASS|FAIL|WARNING)" | head -1)
  echo "- ${slug}: ${status:-SKIP}" >> tasks/reports/UK_META_VALIDATION.md
done
```

---

## Phase 2: Content Generation

### Task 2.1: Generate Content (L3 — 32 categories)

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

**Команда для каждой:**
```
/uk-content-generator {slug}
```

### Task 2.2: Generate Content (L2 — 8 categories)

```
aksessuary-dlya-naneseniya-sredstv, apparaty-tornador, avtoshampuni,
keramika-i-zhidkoe-steklo, kvik-deteylery, mikrofibra-i-tryapki,
sredstva-dlya-kozhi, voski
```

### Task 2.3: Generate Content (L1 — 7 categories)

```
aksessuary, moyka-i-eksterer, oborudovanie, opt-i-b2b,
polirovka, ukhod-za-intererom, zashchitnye-pokrytiya
```

---

## Phase 3: Content Validation

### Task 3.1: SEO Structure Check

```bash
for slug in $(ls uk/categories/); do
  content_file="uk/categories/${slug}/content/${slug}_uk.md"
  if [ -f "$content_file" ]; then
    echo "=== ${slug} ==="
    python3 scripts/check_seo_structure.py "$content_file" "$(jq -r '.keywords.primary[0].keyword // .h1' uk/categories/${slug}/meta/${slug}_meta.json 2>/dev/null)"
  fi
done
```

**SEO пороги (контент):**
| Метрика | Норма | BLOCKER |
|---------|-------|---------|
| Word count | 400-700 | <300 |
| Stem-група | ≤2.5% | >3.0% |
| Класична тошнота | ≤3.5 | >4.0 |
| Академічна | ≥7% | <7% (WARNING) |
| H2 з ключем | ≥2 | 0 |

### Task 3.2: Keyword Density Check

```bash
for slug in $(ls uk/categories/); do
  content_file="uk/categories/${slug}/content/${slug}_uk.md"
  if [ -f "$content_file" ]; then
    python3 scripts/check_keyword_density.py "$content_file" --lang uk 2>&1 | grep -E "(PASS|FAIL|WARNING)"
  fi
done
```

### Task 3.3: Fix Failed Content

Для категорий с FAIL запустить:
```
uk-content-reviewer {slug}
```

### Task 3.4: Content Validation Report

```bash
echo "# UK Content Validation Report" > tasks/reports/UK_CONTENT_VALIDATION.md
echo "Date: $(date +%Y-%m-%d)" >> tasks/reports/UK_CONTENT_VALIDATION.md

for slug in $(ls uk/categories/); do
  content_file="uk/categories/${slug}/content/${slug}_uk.md"
  if [ -f "$content_file" ]; then
    words=$(wc -w < "$content_file")
    echo "- ${slug}: ${words} words" >> tasks/reports/UK_CONTENT_VALIDATION.md
  else
    echo "- ${slug}: NO CONTENT" >> tasks/reports/UK_CONTENT_VALIDATION.md
  fi
done
```

---

## Phase 4: Quality Gate

### Task 4.1: Full Quality Gate

```bash
for slug in $(ls uk/categories/); do
  echo "=== ${slug} ==="
  # Используем quality-gate агент или скрипт
  python3 scripts/validate_meta.py "uk/categories/${slug}/meta/${slug}_meta.json" --lang uk

  content_file="uk/categories/${slug}/content/${slug}_uk.md"
  if [ -f "$content_file" ]; then
    python3 scripts/check_seo_structure.py "$content_file" "keyword" 2>/dev/null
  fi
done
```

### Task 4.2: Final Report

```bash
echo "# UK Quality Gate Report" > tasks/reports/UK_QUALITY_GATE.md
echo "Date: $(date +%Y-%m-%d)" >> tasks/reports/UK_QUALITY_GATE.md
echo "" >> tasks/reports/UK_QUALITY_GATE.md
echo "| Category | Meta | Content | Status |" >> tasks/reports/UK_QUALITY_GATE.md
echo "|----------|------|---------|--------|" >> tasks/reports/UK_QUALITY_GATE.md

for slug in $(ls uk/categories/); do
  meta_status="SKIP"
  content_status="SKIP"

  if [ -f "uk/categories/${slug}/meta/${slug}_meta.json" ]; then
    meta_status="OK"
  fi

  if [ -f "uk/categories/${slug}/content/${slug}_uk.md" ]; then
    content_status="OK"
  fi

  if [ "$meta_status" = "OK" ] && [ "$content_status" = "OK" ]; then
    final="READY"
  else
    final="PENDING"
  fi

  echo "| ${slug} | ${meta_status} | ${content_status} | ${final} |" >> tasks/reports/UK_QUALITY_GATE.md
done
```

---

## Phase 5: Commit & Push

```bash
git add uk/categories/
git add tasks/reports/UK_*.md
git commit -m "feat(uk): complete pipeline for 47 categories (meta + content)"
git push
```

---

## Execution Strategy

### Parallel Agents (рекомендовано)

**Phase 1:** 1 агент — валидация мета (быстро)

**Phase 2:** 5 параллельных агентов:
- Agent 1: Batch 1 (10 L3)
- Agent 2: Batch 2 (10 L3)
- Agent 3: Batch 3 (12 L3)
- Agent 4: L2 (8)
- Agent 5: L1 (7)

**Phase 3-4:** 1 агент — валидация и отчёты

---

## Session Prompts

### Prompt для Phase 1 (Meta Validation):
```
Выполни валидацию UK мета-тегов для всех 47 категорий.

1. Запусти validate_meta.py для каждой категории
2. Для FAIL — запусти /uk-generate-meta {slug}
3. Повтори валидацию
4. Создай отчёт в tasks/reports/UK_META_VALIDATION.md
```

### Prompt для Phase 2 (Content Generation):
```
Сгенерируй UK контент для категорий из списка:

{batch_list}

Для каждой:
1. /uk-content-generator {slug}
2. Проверь word count (400-700)
3. При FAIL — uk-content-reviewer {slug}

После batch — commit промежуточный.
```

### Prompt для Phase 3-4 (Validation):
```
Выполни валидацию UK контента для всех категорий:

1. check_seo_structure.py для каждого *_uk.md
2. check_keyword_density.py --lang uk
3. Для FAIL — uk-content-reviewer {slug}
4. Создай отчёт в tasks/reports/UK_CONTENT_VALIDATION.md
5. Финальный quality gate отчёт
```

---

## Acceptance Criteria

### Phase 1 (Meta):
- [ ] 47 файлов `*_meta.json` валидны
- [ ] Title: 50-60 chars, с "Купити"
- [ ] Description: 120-160 chars
- [ ] H1: без "Купити"
- [ ] Отчёт UK_META_VALIDATION.md создан

### Phase 2-3 (Content):
- [ ] 47 файлов `*_uk.md` созданы
- [ ] Word count: 400-700 для каждого
- [ ] H2 с ключовим словом: ≥2
- [ ] Stem-група: ≤2.5%
- [ ] Академічна тошнота: ≥7%
- [ ] Отчёт UK_CONTENT_VALIDATION.md создан

### Phase 4-5:
- [ ] Quality Gate PASS для всех
- [ ] Отчёт UK_QUALITY_GATE.md создан
- [ ] Commit + Push выполнены
- [ ] TODO_UK_CONTENT.md обновлён: все `[~]` → `[x]`

---

**Total:** 47 categories
**Phases:** 5
