# План оптимизации суб-агентов SEO 2025

**Дата:** 2025-12-09
**Статус:** В работе

---

## Выполнено

### content-generation-agent v6.0 ✅

| Изменение | Было | Стало |
|-----------|------|-------|
| Подход | Keyword stuffing | LSI-first (20-30 LSI vs 3-5 primary) |
| Density | 4-5% | 1-2% |
| Структура | Фиксированный шаблон | 3 вариации (footprint avoidance) |
| AI-fluff | Не контролировался | Запрещённый список (8 фраз) |
| Контекст | Неясен | E-commerce category page (не блог!) |
| Chars (Tier B) | 3500-5000 | 2500-3500 |

---

## План улучшений остальных агентов

### 1. ukrainian-translator (Приоритет: HIGH)

**Текущие проблемы:**

- Не проверяет сохранение LSI-баланса после перевода
- Нет проверки на AI-fluff в украинском варианте
- Char count validation ±5% — нужно уточнить базу

**Улучшения:**

- [ ] Добавить LSI preservation check (соотношение должно сохраниться)
- [ ] Добавить UK AI-fluff blacklist: "У цій статті", "Давайте розберемо", "Варто зазначити"
- [ ] Уточнить: chars базируются на RU (который уже 2500-3500), не старых 4000-5000

### 2. meta-tags-generator (Приоритет: MEDIUM)

**Текущее состояние:**

- Генерирует Title 50-70, Description 140-170
- Title ≠ H1 (хорошо)

**Улучшения:**

- [ ] Добавить вариативность шаблонов (как в content-gen)
- [ ] Убедиться что primary keyword в Title только 1x
- [ ] Проверить отсутствие AI-fluff в Description

### 3. keyword-distribution-agent (Приоритет: HIGH)

**Текущие проблемы:**

- Coverage target 70% — нужно согласовать с новым LSI подходом
- Density target до 2% — OK, но нужен нижний предел (1%)

**Улучшения:**

- [ ] Пересмотреть coverage calculation с учётом LSI
- [ ] Density target: 1-2% (не "до 2%")
- [ ] Добавить LSI synonyms distribution map

### 4. packaging-agent (Приоритет: LOW)

**Текущее состояние:**

- Копирует файлы, генерирует README/QUALITY_REPORT
- Работает корректно

**Улучшения:**

- [ ] Добавить LSI metrics в QUALITY_REPORT
- [ ] Добавить AI-fluff check result

### 5. data-preparation-agent (Приоритет: MEDIUM)

**Текущее состояние:**

- Создаёт JSON из scraped данных
- Определяет tier

**Улучшения:**

- [ ] Добавить автоматическое формирование LSI pool из competitor analysis
- [ ] Улучшить tier detection logic

### 6. check_lsi_metrics.sh (Приоритет: HIGH)

**Текущие значения vs Нужные:**

| Метрика | Текущий target | Новый target (по agent v6.0) |
|---------|----------------|------------------------------|
| LSI total | 25-40 | 20-30 |
| Chars | 3500-5500 | 2500-3500 (Tier B) |
| Primary | 3-5 | 3-5 ✓ |

**Исправления:**

- [ ] Уменьшить LSI target: 25-40 → 20-30
- [ ] Уменьшить chars target: 3500-5500 → 2500-3500
- [ ] Добавить tier parameter для разных targets

---

## Тест-план

### Полный workflow test (aktivnaya-pena)

```
Stage 0  → category-init         [SKIP - уже есть]
Stage -3 → url-extraction        [SKIP - уже есть]
Stage -2 → url-preparation       [SKIP - уже есть]
Stage 5  → filter-mega-csv       [SKIP - manual data]
Stage 4  → data-preparation      [TEST]
Stage 6  → keyword-distribution  [TEST]
Stage 8  → content-generation    [✅ DONE - v6.0 tested]
Stage 9  → ukrainian-translator  [TEST]
Stage 10 → meta-tags-generator   [TEST]
Stage 11 → packaging-agent       [TEST]
```

### Валидация после каждого stage

| Stage | Валидатор | Ключевые проверки |
|-------|-----------|-------------------|
| 8 | stage-8-11 | LSI ratio ≥5:1, density 1-2%, no AI-fluff |
| 9 | stage-8-11 | UK structure = RU, no Russian words, LSI preserved |
| 10 | stage-8-11 | Title 50-70, Desc 140-170, Title≠H1 |
| 11 | stage-8-11 | 5 files exist, README OK |

---

## Очерёдность выполнения

1. **check_lsi_metrics.sh** — синхронизировать targets с agent v6.0
2. **ukrainian-translator** — добавить LSI/AI-fluff checks
3. **keyword-distribution-agent** — пересмотреть coverage с LSI
4. **meta-tags-generator** — вариативность шаблонов
5. **packaging-agent** — LSI metrics в отчёт
6. **Full workflow test** — от Stage 4 до Stage 11

---

## Метрики успеха

| Критерий | Target |
|----------|--------|
| Все агенты обновлены | 8/8 |
| Все тесты проходят | 100% |
| LSI ratio в контенте | ≥5:1 |
| AI-fluff detections | 0 |
| Keyword density | 1-2% |

---

**Следующий шаг:** Исправить check_lsi_metrics.sh под новые targets
