# Coverage Audit Tool — Design Document

**Дата:** 2026-01-30
**Статус:** Draft
**Цель:** Batch-аудит покрытия ключевых слов в контенте с детальной диагностикой

---

## 1. Проблема

Текущий `CoverageChecker` возвращает только found/missing списки без объяснения **почему** ключ не найден. Для аудита 100+ текстов нужен инструмент, который:

- Проверяет все категории batch'ом
- Классифицирует результат (покрыто чем именно / почему не покрыто)
- Выдаёт CSV-отчёты для анализа и принятия решений
- Интегрируется в pipeline (CLI, JSON output)

---

## 2. Архитектура

### 2.1 Источник данных

**Per-category `_clean.json`** — без дублирования:

```
uk/categories/{slug}/data/{slug}_clean.json  → keywords[] + synonyms[]
uk/categories/{slug}/content/{slug}_uk.md    → текст для проверки

categories/{slug}/data/{slug}_clean.json     → keywords[] + synonyms[]
categories/{slug}/content/{slug}_ru.md       → текст для проверки
```

### 2.2 Статусы детекции

#### Группа "COVERED" (ключ найден):

| Статус | Описание | Пример |
|--------|----------|--------|
| `EXACT` | Точное совпадение | "активна піна для авто" буквально |
| `NORM` | После нормализации (casefold, NFKC, апострофы ʼ→', ё→е) | "Активна Піна" → "активна піна" |
| `LEMMA` | По леммам (pymorphy3/Snowball) | "активної піни" → "активна піна" |
| `SYNONYM` | Найден synonym из variant_of | "засоби для чорніння шин" покрывает "засіб для чорніння гуми" |

#### Группа "NOT COVERED" (причина фейла):

| Статус | Описание | Приоритет диагностики |
|--------|----------|----------------------|
| `TOKENIZATION` | Есть признаки проблемы токенизации (дефис, апостроф, pH-, 1:10, цифры) | 1 (наиболее actionable) |
| `PARTIAL` | ≥50% лемм найдено, но фраза не собралась | 2 |
| `ABSENT` | Ничего не найдено | 3 (дефолт) |

### 2.3 Алгоритм проверки (waterfall)

```python
def check_keyword(keyword: str, text: str, synonyms: list[dict]) -> MatchResult:
    # === COVERED checks ===

    # 1. EXACT
    if exact_match(keyword, text):
        return MatchResult(status="EXACT", covered=True)

    # 2. NORM
    if normalized_match(keyword, text):
        return MatchResult(status="NORM", covered=True)

    # 3. LEMMA
    if lemma_match(keyword, text):
        return MatchResult(status="LEMMA", covered=True)

    # 4. SYNONYM (проверяем все synonyms с variant_of == keyword)
    for syn in synonyms:
        if syn.get("variant_of") == keyword:
            syn_kw = syn["keyword"]
            # Проверяем synonym теми же методами
            if exact_match(syn_kw, text):
                return MatchResult(status="SYNONYM", covered=True,
                                   covered_by=syn_kw, syn_match_method="EXACT")
            if normalized_match(syn_kw, text):
                return MatchResult(status="SYNONYM", covered=True,
                                   covered_by=syn_kw, syn_match_method="NORM")
            if lemma_match(syn_kw, text):
                return MatchResult(status="SYNONYM", covered=True,
                                   covered_by=syn_kw, syn_match_method="LEMMA")

    # === NOT COVERED — diagnose reason ===

    # 5. TOKENIZATION (проверяем признаки)
    if has_tokenization_markers(keyword):
        # Маркеры: дефис, апостроф, цифры, pH, 1:10, RTU
        return MatchResult(status="TOKENIZATION", covered=False,
                           reason="Contains special tokens")

    # 6. PARTIAL
    lemma_coverage = calculate_lemma_coverage(keyword, text)
    if lemma_coverage >= 0.5:
        return MatchResult(status="PARTIAL", covered=False,
                           lemma_coverage=lemma_coverage,
                           reason=f"{int(lemma_coverage*100)}% lemmas found")

    # 7. ABSENT
    return MatchResult(status="ABSENT", covered=False)
```

### 2.4 Нормализация текста

```python
def normalize_text(text: str) -> str:
    """
    Нормализация для NORM-матчинга:
    - casefold (lower + unicode)
    - NFKC (каноническая форма)
    - Унификация апострофов: ʼ ' ʹ ′ → '
    - ё → е (для RU)
    - Сохранение дефисов и цифр (для диагностики TOKENIZATION)
    """
    import unicodedata

    text = text.casefold()
    text = unicodedata.normalize("NFKC", text)

    # Унификация апострофов
    apostrophes = "ʼ'ʹ′`"
    for a in apostrophes:
        text = text.replace(a, "'")

    # ё → е
    text = text.replace("ё", "е")

    return text
```

### 2.5 Детекция TOKENIZATION markers

```python
TOKENIZATION_PATTERNS = [
    r"pH[-\s]?\d*",           # pH, pH-7, pH 7
    r"\d+:\d+",               # 1:10, 1:50
    r"\d+-\d+",               # 5-10, 100-150
    r"\w+-\w+",               # pH-нейтральний, wash-and-wax
    r"RTU",                   # Ready-To-Use
    r"\d+\s*(мл|л|г|бар)",    # 100 мл, 150 бар
]

def has_tokenization_markers(keyword: str) -> bool:
    for pattern in TOKENIZATION_PATTERNS:
        if re.search(pattern, keyword, re.IGNORECASE):
            return True
    return False
```

---

## 3. Выходные форматы

### 3.1 coverage_summary.csv

Сводка по категориям:

| Поле | Описание |
|------|----------|
| `slug` | ID категории |
| `lang` | ru / uk |
| `total_keywords` | Всего ключей |
| `covered` | Покрыто (EXACT+NORM+LEMMA+SYNONYM) |
| `not_covered` | Не покрыто |
| `coverage_percent` | % покрытия |
| `top_missing` | Топ-3 непокрытых по volume (через ;) |

**Пример:**
```csv
slug,lang,total_keywords,covered,not_covered,coverage_percent,top_missing
aktivnaya-pena,uk,11,9,2,81.8,"гель для миття авто (90);хімія для мийки самообслуговування (110)"
cherniteli-shin,uk,5,5,0,100.0,""
```

### 3.2 coverage_details.csv

Детали по каждому ключу:

| Поле | Описание |
|------|----------|
| `slug` | ID категории |
| `lang` | ru / uk |
| `keyword` | Ключевое слово |
| `volume` | Частотность |
| `status` | EXACT / NORM / LEMMA / SYNONYM / TOKENIZATION / PARTIAL / ABSENT |
| `covered` | true / false |
| `covered_by` | Для SYNONYM — каким synonym покрыто |
| `syn_match_method` | Для SYNONYM — EXACT/NORM/LEMMA |
| `lemma_coverage` | Для PARTIAL — % найденных лемм |
| `reason` | Для NOT COVERED — причина |

**Пример:**
```csv
slug,lang,keyword,volume,status,covered,covered_by,syn_match_method,lemma_coverage,reason
aktivnaya-pena,uk,активна піна для авто,1600,EXACT,true,,,,
aktivnaya-pena,uk,засіб для чорніння гуми,210,SYNONYM,true,засоби для чорніння шин,LEMMA,,
aktivnaya-pena,uk,pH-нейтральний,50,TOKENIZATION,false,,,,Contains special tokens
aktivnaya-pena,uk,гель для миття авто,90,PARTIAL,false,,,0.67,67% lemmas found
```

---

## 4. CLI Interface

### 4.1 Batch режим (основной)

```bash
# Все UK категории
python3 scripts/audit_coverage.py --lang uk

# Все RU категории
python3 scripts/audit_coverage.py --lang ru

# Обе языковые версии
python3 scripts/audit_coverage.py --lang all
```

**Output:**
```
reports/coverage_summary_uk_2026-01-30.csv
reports/coverage_details_uk_2026-01-30.csv
```

### 4.2 Single category режим

```bash
# Одна категория с подробным выводом
python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --verbose
```

**Output (stdout):**
```
=== aktivnaya-pena (uk) ===
Coverage: 9/11 (81.8%)

✓ EXACT (4):
  - активна піна для авто (1600)
  - піна для миття авто (1300)
  ...

✓ LEMMA (3):
  - активної піни → активна піна
  ...

✓ SYNONYM (2):
  - засіб для чорніння гуми ← засоби для чорніння шин (LEMMA)
  ...

✗ NOT COVERED (2):
  - [TOKENIZATION] pH-нейтральний (50) — Contains special tokens
  - [PARTIAL] гель для миття авто (90) — 67% lemmas found
```

### 4.3 JSON output (для интеграции)

```bash
python3 scripts/audit_coverage.py --slug aktivnaya-pena --lang uk --json
```

```json
{
  "slug": "aktivnaya-pena",
  "lang": "uk",
  "total": 11,
  "covered": 9,
  "coverage_percent": 81.8,
  "results": [
    {
      "keyword": "активна піна для авто",
      "volume": 1600,
      "status": "EXACT",
      "covered": true
    },
    {
      "keyword": "засіб для чорніння гуми",
      "volume": 210,
      "status": "SYNONYM",
      "covered": true,
      "covered_by": "засоби для чорніння шин",
      "syn_match_method": "LEMMA"
    }
  ]
}
```

### 4.4 Интеграция с validate_content.py

```bash
# Добавить флаг --audit-details для расширенной диагностики
python3 scripts/validate_content.py file.md "keyword" --audit-details --json
```

---

## 5. Структура файлов

```
scripts/
├── audit_coverage.py          # Новый скрипт (CLI + batch logic)
├── coverage_matcher.py        # Новый модуль (MatchResult, check_keyword, normalize_text)
├── keyword_utils.py           # Существующий (использовать MorphAnalyzer)
└── ...

reports/
├── coverage_summary_uk_2026-01-30.csv
├── coverage_details_uk_2026-01-30.csv
└── ...

tests/
└── unit/
    └── test_coverage_matcher.py   # Тесты на статусы, edge cases
```

---

## 6. Edge Cases и тесты

### 6.1 Обязательные тест-кейсы

| Кейс | Input | Expected |
|------|-------|----------|
| Exact match | kw="активна піна", text="...активна піна..." | EXACT |
| Case insensitive | kw="Активна Піна", text="активна піна" | NORM |
| Апострофы UK | kw="для зовнішнього догляду", text="для зовнішнього догляду" (різні апострофи) | NORM |
| Морфология UK | kw="чорніння гуми", text="чорнінні гуми" | LEMMA |
| Морфология RU | kw="щётка для мойки", text="щёткой для мойки" | LEMMA |
| Synonym exact | kw="засіб для X", syn="засоби для X" в тексте | SYNONYM + syn_match=EXACT |
| Synonym lemma | kw="засіб для X", syn="засобів для X" в тексте | SYNONYM + syn_match=LEMMA |
| pH tokenization | kw="pH-нейтральний" not in text | TOKENIZATION |
| Ratio tokenization | kw="розведення 1:10" not in text | TOKENIZATION |
| Partial 2/3 | kw="активна піна авто", text="активна... авто" (без "піна") | PARTIAL (67%) |
| Absent | kw="неіснуюче слово" | ABSENT |

### 6.2 Регрессионные тесты

- Категория `cherniteli-shin` — 5 keywords, ожидаем 100% coverage
- Категория `aktivnaya-pena` — 11 keywords, известные проблемные кейсы

---

## 7. Зависимости

**Существующие (уже есть):**
- `pymorphy3` (или fallback на Snowball) — через `keyword_utils.MorphAnalyzer`
- `scripts/config.py` — пути к категориям

**Новые:**
- Нет новых зависимостей

---

## 8. Не входит в scope (v1)

- LLM-слой для спорных случаев (отложено на v2)
- Интеграция с CI/quality-gate (отдельная задача)
- GUI / web-интерфейс
- Автоматические фиксы контента

---

## 9. План реализации

1. **coverage_matcher.py** — модуль с `MatchResult`, `normalize_text()`, `check_keyword()`
2. **audit_coverage.py** — CLI скрипт с batch/single режимами
3. **test_coverage_matcher.py** — unit-тесты на все статусы
4. Прогон на всех UK категориях, валидация результатов
5. Документация в CLAUDE.md

---

## 10. Acceptance Criteria

- [ ] `audit_coverage.py --lang uk` генерирует два CSV файла
- [ ] Все 6 статусов корректно определяются (по тестам)
- [ ] SYNONYM показывает `covered_by` + `syn_match_method`
- [ ] TOKENIZATION детектирует pH-, 1:10, дефисные слова
- [ ] PARTIAL показывает % покрытия лемм
- [ ] `--verbose` выводит человекочитаемый отчёт
- [ ] `--json` выводит машиночитаемый JSON
