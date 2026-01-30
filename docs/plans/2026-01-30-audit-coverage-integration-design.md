# Design: Интеграция audit_coverage.py в скиллы

**Дата:** 2026-01-30
**Статус:** Draft

---

## Цель

Добавить детерминированную проверку keyword coverage во все скиллы валидации контента, используя `audit_coverage.py` вместо ручной проверки "на глаз".

---

## Архитектура

### Скиллы для изменения (6 штук)

| RU | UK |
|----|----|
| content-reviewer | uk-content-reviewer |
| quality-gate | uk-quality-gate |
| verify-content | uk-verify-content |

### Источники ключей

1. **keywords_in_content** из `_meta.json` — строгая проверка (primary/secondary/supporting)
2. **keywords[]** из `_clean.json` — информативная проверка (полный семантический кластер)

### Правила вердикта

**keywords_in_content (строгий):**

| Группа | Требование | При фейле |
|--------|------------|-----------|
| primary | 100% COVERED | BLOCKER |
| secondary | 100% COVERED | BLOCKER |
| supporting | ≥80% COVERED | WARNING |

COVERED = EXACT / NORM / LEMMA / SYNONYM
NOT COVERED = TOKENIZATION / PARTIAL / ABSENT → фейл группы

**keywords[] (информативный):**

| Кол-во ключей | Threshold | При фейле |
|---------------|-----------|-----------|
| ≤5 | 70% | WARNING |
| 6-15 | 60% | WARNING |
| >15 | 50% | WARNING |

Никогда не BLOCKER — только WARNING.

### Параметр языка

Явно в скиллах:
- RU-скиллы → `--lang ru`
- UK-скиллы → `--lang uk`

---

## Формат вывода

### Компактный (по умолчанию)

```markdown
### Keywords Coverage

| Источник | Covered | Total | % | Status |
|----------|---------|-------|---|--------|
| primary+secondary | 8/8 | 100% | ✅ PASS |
| supporting | 4/5 | 80% | ✅ PASS |
| keywords[] | 8/15 | 53% | ⚠️ WARNING (threshold 50%) |

**NOT COVERED (primary/secondary):** нет
**NOT COVERED (keywords[]):** ключ1 (1200), ключ2 (800), ключ3 (500)
```

### Детальный (при BLOCKER или WARNING)

Добавляется только если есть проблемы:

```markdown
#### Coverage Details

| Keyword | Volume | Status | Note |
|---------|--------|--------|------|
| pH-нейтральна | 800 | TOKENIZATION | special tokens |
| піна для безконтактної | 600 | PARTIAL | 67% lemmas |
| купити активну піну | 400 | SYNONYM | ← "активна піна" [LEMMA] |
| засіб для мийки | 300 | ABSENT | |
```

**Правила показа:**
- BLOCKER в primary/secondary → все NOT COVERED из этих групп
- WARNING в keywords[] → топ-5 NOT COVERED по volume
- SYNONYM → всегда показывать `covered_by` + `[EXACT/NORM/LEMMA]`

---

## Доработка audit_coverage.py

### Новый флаг `--include-meta`

```bash
python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --json --include-meta
```

### Структура JSON-ответа

```json
{
  "slug": "aktivnaya-pena",
  "lang": "uk",
  "keywords_in_content": {
    "primary": {
      "total": 3,
      "covered": 3,
      "coverage_percent": 100.0,
      "results": [
        {"keyword": "активна піна", "volume": 2400, "status": "EXACT", "covered": true}
      ]
    },
    "secondary": {
      "total": 5,
      "covered": 5,
      "coverage_percent": 100.0,
      "results": [...]
    },
    "supporting": {
      "total": 5,
      "covered": 4,
      "coverage_percent": 80.0,
      "results": [...]
    }
  },
  "keywords": {
    "total": 15,
    "covered": 12,
    "coverage_percent": 80.0,
    "results": [
      {
        "keyword": "активна піна",
        "volume": 2400,
        "status": "EXACT",
        "covered": true,
        "covered_by": null,
        "syn_match_method": null,
        "lemma_coverage": null,
        "reason": null
      },
      {
        "keyword": "піна для мийки",
        "volume": 1200,
        "status": "SYNONYM",
        "covered": true,
        "covered_by": "активна піна",
        "syn_match_method": "LEMMA",
        "lemma_coverage": null,
        "reason": null
      }
    ]
  }
}
```

---

## Изменения в скиллах

### content-reviewer / uk-content-reviewer

**Текущий Step 3:** "Keywords Coverage (100% required)" — ручная проверка

**Новый Step 3:**
```bash
python3 scripts/audit_coverage.py --slug {slug} --lang ru|uk --json --include-meta
```

Парсить JSON, применять правила вердикта, выводить в формате выше.

### quality-gate / uk-quality-gate

**Добавить в секцию "3. Content Validation"** после существующих валидаторов.

Результат включить в итоговую таблицу Quality Gate Report:

```markdown
| Keywords (primary+secondary) | ✅/❌ | 8/8 (100%) |
| Keywords (supporting) | ✅/⚠️ | 4/5 (80%) |
| Keywords (semantic) | ✅/⚠️ | 12/15 (80%) |
```

### verify-content / uk-verify-content

**Добавить как отдельный шаг проверки.**

Показывать результат человеку, решение за ним.

---

## Команда вызова

```bash
# RU скиллы
python3 scripts/audit_coverage.py --slug {slug} --lang ru --json --include-meta

# UK скиллы
python3 scripts/audit_coverage.py --slug {slug} --lang uk --json --include-meta
```

---

## Задачи реализации

1. **audit_coverage.py** — добавить флаг `--include-meta`, загрузку _meta.json, группировку по primary/secondary/supporting
2. **content-reviewer** — заменить Step 3 на вызов скрипта
3. **uk-content-reviewer** — аналогично
4. **quality-gate** — добавить вызов в Content Validation
5. **uk-quality-gate** — аналогично
6. **verify-content** — добавить шаг coverage
7. **uk-verify-content** — аналогично

---

**Version:** 1.0
