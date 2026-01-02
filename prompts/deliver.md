# DELIVER Prompt — Validation & Packaging

**Sub-agent:** `seo-content-auditor` (sonnet)
**Этап:** 3/3 (DELIVER)
**Задача:** Валидировать контент и упаковать deliverables

## ⚡ D+E Pattern

Валидатор автоматически определяет JSON:

```
1. {slug}_clean.json (12 kw) ← preferred
2. {slug}.json (52 kw)       ← fallback
```

**Adaptive Thresholds:**

| Keywords | Density Blocker | Density Warning |
|----------|-----------------|-----------------|
| ≤20 (clean) | 5.0% | 3.5% |
| >20 (raw)   | 3.5% | 2.5% |

---

## Input Parameters

- `slug`: {slug}
- `tier`: {tier} (A/B/C)
- `main_keyword`: {keyword}
- `content_ru`: categories/{slug}/content/{slug}_ru.md
- `meta`: categories/{slug}/meta/{slug}_meta.json

---

## Steps

### Step 1: Run Quality Checks (5 проверок)

Запустить полную валидацию:

```bash
source venv/bin/activate
PYTHONPATH=. python3 scripts/quality_runner.py \
  categories/{slug}/content/{slug}_ru.md \
  "{main_keyword}" \
  {tier}
```

**5 Checks:**

1. **Markdown Structure**
   - H2 присутствуют (Tier A=4-5, B=3-4, C=2-3)
   - FAQ секция существует
   - H1 = название категории (если есть, должен совпадать с главным keyword)

2. **Grammar & Style**
   - Нет запрещённых AI-fluff фраз
   - Synonym rotation (max 2 повтора/параграф)
   - Commercial markers ≥ минимум

3. **Water/Nausea (Адвего-калибровка)**
   - Water: 40-60% (Tier A/B), 40-65% (Tier C)
   - Classic Nausea: ≤3.5
   - Academic Nausea: 7-9.5%

4. **Keyword Density**
   - Main keyword: 0.5-1.5% (A), 0.5-1.8% (B), 0.5-2.0% (C)
   - Равномерное распределение (не кластеры)

5. **NER & Blacklist**
   - Нет конкурентов (Turtle Wax, Meguiar's, etc.)
   - Нет брендов (если не в каталоге)

**Exit Codes:**

- 0 = PASS ✅
- 1 = WARNING ⚠️ (можно продолжать)
- 2 = FAIL ❌ (требуется fix)

### Step 2: Fix Issues (если FAIL)

Если проверка вернула exit code 2:

1. Прочитать лог ошибок: `.logs/quality_check_{timestamp}.log`
2. Определить проблемные секции
3. Исправить контент
4. Перезапустить Step 1

**Типичные ошибки:**

| Ошибка | Fix |
|--------|-----|
| Water >70% | Убрать вводные слова, сократить параграфы |
| Nausea >4.0 | Synonym rotation, разнообразить предложения |
| Density <0.5% | Добавить keyword в H2/FAQ |
| Competitor found | Заменить на "средство", "состав" |

### Step 3: Package Deliverables

Создать папку: `categories/{slug}/deliverables/`

Скопировать файлы:

- `{slug}_ru.md` (из content/)
- `{slug}_meta.json` (из meta/)

Создать дополнительно:

**1. README.md**

```markdown
# {Name} — Deliverables

**Tier:** {tier}
**Status:** Validated ✅
**Date:** {ISO8601}

## Files

| File | Description |
|------|-------------|
| {slug}_ru.md | Контент RU |
| {slug}_meta.json | Meta tags RU |
| QUALITY_REPORT.md | Отчёт валидации |

## Metrics (RU)

- Chars: {chars} (target: {tier_target})
- Words: {words}
- H2: {h2_count}
- FAQ: {faq_count}
- Water: {water}%
- Nausea: {nausea}
- Density: {density}%
- Commercial: {commercial_count} markers

## Validation

✅ All 5 checks passed
- Markdown structure: OK
- Grammar & style: OK
- Water/Nausea: OK
- Keyword density: OK
- NER/Blacklist: OK

## Next Steps

1. Импорт в CMS
2. Настройка URL: /category/{slug}
3. Публикация
```

**2. QUALITY_REPORT.md**

```markdown
# Quality Report — {slug}

**Date:** {ISO8601}
**Tier:** {tier}
**Validator:** quality_runner.py v7.3

---

## Summary

| Check | Status | Details |
|-------|--------|---------|
| Markdown | ✅ PASS | H2={count}, FAQ={count} |
| Grammar | ✅ PASS | No AI-fluff, Synonym OK |
| Water/Nausea | ✅ PASS | Water={X}%, Nausea={X} |
| Density | ✅ PASS | Main={X}%, Distribution OK |
| NER | ✅ PASS | No competitors |

---

## Metrics

### Content (RU)

- Chars: {chars} (target: {tier_range})
- Words: {words}
- H2: {h2_count} (target: {tier_h2})
- FAQ: {faq_count} (target: {tier_faq})

### SEO

- Keyword Density: {density}% (target: {tier_density})
- Water: {water}% (target: 40-60%)
- Classic Nausea: {nausea} (target: ≤3.5)
- Academic Nausea: {academic}% (target: 7-9.5%)

### Commercial

Found {count} markers (min {tier_min}):
- купить: {count}
- цена: {count}
- доставка: {count}
- заказать: {count}

---

## Logs

Full logs: categories/{slug}/.logs/quality_check_{timestamp}.log
```

### Step 4: Update Task File

Обновить `task_{slug}.json`:

```json
{
  "status": "completed",
  "current_stage": "deliver",
  "stages": {
    "prepare": "completed",
    "produce": "completed",
    "deliver": "completed"
  },
  "metrics": {
    "chars": 2300,
    "words": 340,
    "water": 56.9,
    "nausea": 2.45,
    "density": 1.5,
    "commercial": 5,
    "h2": 4,
    "faq": 5
  },
  "validation": {
    "passed": true,
    "checks": {
      "markdown": "pass",
      "grammar": "pass",
      "water": "pass",
      "density": "pass",
      "ner": "pass"
    }
  },
  "completed_at": "ISO8601"
}
```

---

## Output Report

Вернуть Orchestrator:

```
✅ DELIVER завершён для {slug}

Validation:
- All 5 checks: PASSED ✅
- Exit code: 0

Deliverables:
- Path: categories/{slug}/deliverables/
- Files: 4 (content RU, meta, README, QUALITY_REPORT)

Metrics:
- Chars: 2300 / 2000-2500 ✓
- Water: 56.9% / 40-60% ✓
- Nausea: 2.45 / ≤3.5 ✓
- Density: 1.5% / 0.5-1.5% ✓
- Commercial: 5 / min 4 ✓

Task Status: COMPLETED ✅

Ready for:
1. CMS Import
2. URL: /category/{slug}
3. Publication
```

---

## Error Handling

### Если валидация провалена (exit code 2)

```
❌ VALIDATION FAILED

Failed checks:
- Water/Nausea: Water 75% (max 60%)
- Nausea: 4.2 (max 3.5)

Action Required:
1. Reduce water by removing intro phrases
2. Apply synonym rotation to reduce nausea
3. Re-run PRODUCE step

Do not proceed to packaging.
```

### Если файлы не найдены

```
❌ ERROR: Content files not found
Missing:
- categories/{slug}/content/{slug}_ru.md

Action: Run PRODUCE first
```

---

## Success Criteria

- [ ] quality_runner.py вернул exit code 0 (PASS)
- [ ] Все 5 проверок пройдены
- [ ] Deliverables созданы (4 файла)
- [ ] README.md содержит метрики
- [ ] QUALITY_REPORT.md содержит детали
- [ ] Task file updated: status="completed"

---

**Version:** 5.1
**Spec:** SEO_MASTER.md v7.3
**D+E Pattern:** Auto-detects_clean.json with adaptive thresholds
**Model:** sonnet (quality audit)
**Updated:** 2025-12-12
