# ⚡ QUICK REFERENCE — Шпаргалка

**Быстрый доступ к критичной информации**

---

## 🚦 Exit Codes валидаторов

| Code | Статус | Действие | Пример |
|------|--------|----------|--------|
| **0** | ✅ PASS | Продолжить workflow | URLs: 10/10 OK |
| **1** | ⚠️ WARN | Продолжить с предупреждением | Coverage 68% (цель 70%) |
| **2** | ❌ FAIL | ОСТАНОВИТЬ workflow | URLs: 3/5 (минимум 5) |

**Использование в агентах:**
```bash
# Валидатор вернул exit code
if [ $? -eq 0 ]; then
  echo "✅ PASS - продолжаем"
elif [ $? -eq 1 ]; then
  echo "⚠️ WARN - продолжаем с осторожностью"
else
  echo "❌ FAIL - останавливаем workflow"
  exit 2
fi
```

---

## 📊 Критерии по Stages

### Stage -3: URL Extraction
- ✅ URLs: ≥8 (рекомендовано 10-15)
- ✅ Домены: ≥6 уникальных
- ✅ Протокол: 100% HTTPS
- ✅ Формат: Валидные URL (no spaces, no fragments)

### Stage -2: URL Preparation
- ✅ URLs: ≥5 категорийных страниц
- ✅ Префиксы: Zero `/ua/` (только RU версии)
- ✅ HTTP Status: 200 OK для всех
- ✅ Content-Type: text/html

### Stage 3: MANUAL
- ✅ meta_competitors.csv: ≥5 конкурентов с Title + H1 + Description
- ✅ perplexity_research.md: ≥3 H2 темы, ≥4 FAQ вопроса

### Stage 4: Data Preparation
- ✅ JSON: Valid structure
- ✅ Tier: A/B/C (правильно определён)
- ✅ Keywords: ≥10 для tier A/B, ≥5 для tier C
- ✅ Обязательные поля: `tier`, `keywords`, `meta_patterns`

### Stage 6: Keyword Distribution
- ✅ Coverage: ≥70% keywords распределены по зонам
- ✅ Density targets: PRIMARY 0.11-0.2%, SECONDARY 0.07-0.13%, SUPPORTING 0.02-0.07% (total ≤2%)
- ✅ Distribution map: Все keywords назначены в зоны (H1, Title, H2, intro, body, FAQ)
- ✅ Semantic entities: ≥6 related phrases (НЕ "LSI keywords")

### Stage 8: Content Generation (RU)
- ✅ Длина: 4000-5000 символов БЕЗ пробелов (все tier)
- ✅ Coverage: ≥70% keywords упомянуто
- ✅ H2: tier A (3-4), tier B (2-3), tier C (2)
- ✅ FAQ: tier A (5-6), tier B (4-5), tier C (3-4)
- ✅ Структура: intro → H2 sections → FAQ → conclusion

### Stage 9: Translation (UK)
- ✅ Длина: ±5% от RU версии
- ✅ Язык: Натуральный украинский (не калька)
- ✅ HTML: Все теги закрыты
- ✅ Структура: Сохранены H2, FAQ, links

### Stage 10: Meta Tags
- ✅ Title: 50-70 символов
- ✅ Description: 140-170 символов
- ✅ Уникальность: Title ≠ H1
- ✅ Keywords: Основной keyword присутствует
- ✅ Оба языка: RU + UK в одном JSON

### Stage 11: Packaging
- ✅ 5 файлов: README.md, {slug}_ru.md, {slug}_uk.md, {slug}_meta.json, QUALITY_REPORT.md
- ✅ README: Инструкции по использованию
- ✅ QUALITY_REPORT: Метрики + статус

---

## 🧮 Формулы

### Keyword Coverage
```python
coverage = (keywords_found / total_keywords) * 100
# Цель: ≥70%
# Пример: 28 из 35 keywords = 80% ✅
```

### Keyword Density (by words)
```python
density = (occurrences / total_words) * 100

# Targets (per keyword):
# PRIMARY: 0.11-0.2% (5-9 occurrences per 4500 words)
# SECONDARY: 0.07-0.13% (3-6 occurrences)
# SUPPORTING: 0.02-0.07% (1-3 occurrences)
# TOTAL: ≤2% (hard limit, sum of all keywords)

# Пример: 7 вхождений в 4500 словах = 0.156% ✅
```

### Водность (Natasha)
```python
water = (stop_words / total_words) * 100
# Норма: 55-75% (адекватная водность)
# Цель: ≤65% для SEO-текстов
```

### Тошнота (Natasha, формула Адвего)
```python
nausea = sqrt(most_frequent_word_count)
# Норма: 5-7 (классическая тошнота)
# Цель: ≤7 для читабельности
```

### Readability (TextDescriptives)
```python
# Flesch Reading Ease (Russian adapted)
readability_score = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
# Шкала:
# 90-100: Очень легко (детские книги)
# 60-70: Легко (массовая пресса) ← цель для SEO
# 30-50: Сложно (научные статьи)
```

---

## 💻 Ключевые команды

### Workflow Commands

```bash
# Полный workflow (Stage 0 → -3 → -2 → PAUSE)
"активная пена полный workflow"

# Возобновление после MANUAL STAGE 3
"данные готовы, продолжай для активная-пена"

# Генерация контента (Stage 8 → 9 → 10)
"сгенерируй контент для активная-пена"

# Упаковка deliverables (Stage 11)
"упакуй deliverables для активная-пена"

# Продолжить с определённого stage
"продолжи для активная-пена"  # читает task_{slug}.json
```

### Quality Checks

```bash
# Полная проверка качества (Stage 8.1)
python scripts/quality_runner.py \
    categories/aktivnaya-pena/content/aktivnaya-pena_ru.md \
    "активная пена" \
    B

# Keyword density + coverage
python scripts/check_simple_v2_md.py \
    categories/aktivnaya-pena/content/aktivnaya-pena_ru.md \
    "активная пена" \
    B

# Водность + тошнота (Natasha)
python scripts/check_water_natasha.py \
    categories/aktivnaya-pena/content/aktivnaya-pena_ru.md

# Grammar check (LTEX-LS)
./scripts/quality_check_stage_8_1.sh aktivnaya-pena "активная пена" B
```

### Testing

```bash
# Все тесты
pytest tests/ -v

# С coverage
pytest tests/ -v --cov=scripts --cov-report=html

# Specific test file
pytest tests/test_quality_runner.py -v

# Specific test class
pytest tests/test_quality_runner.py::TestOrchestration -v

# HTML coverage report
open htmlcov/index.html
```

### Validation

```bash
# Валидация всей категории
./scripts/validate_category.sh aktivnaya-pena

# Показать keyword distribution
python scripts/show_keyword_distribution.py \
    categories/aktivnaya-pena/data/aktivnaya-pena_keywords_distributed.json

# Проверить JSON валидность
python -m json.tool categories/aktivnaya-pena/data/aktivnaya-pena.json

# Подсчёт символов
python scripts/check_char_count.py \
    categories/aktivnaya-pena/content/aktivnaya-pena_ru.md
```

---

## 📁 Критичные пути

### Конфигурации

```
.tools/ltex-config-ru.json              # LTEX-LS конфиг (русский)
pytest.ini                              # pytest настройки
requirements.txt                        # Python dependencies
.coveragerc                            # Coverage config (default)
pyproject.toml                         # Project metadata
```

### Агенты и валидаторы

```
.claude/agents/                         # 9 production agents
.claude/agents/validators/              # 5 validators
.claude/agents/_archive/                # 3 archived agents + 2 validators
```

### Скрипты

```
scripts/seo_utils.py                    # Library (все функции)
scripts/quality_runner.py               # Stage 8.1 orchestrator
scripts/check_simple_v2_md.py           # Keyword density
scripts/check_water_natasha.py          # Water + nausea
scripts/quality_check_stage_8_1.sh      # Grammar + readability
```

### Тесты

```
tests/conftest.py                       # pytest fixtures
tests/test_quality_runner.py            # 23 tests (orchestrator)
tests/test_keyword_density.py           # 17 tests (keywords)
```

### Документация

```
CLAUDE.md                               # Orchestrator instructions (v10.1)
INDEX.md                                # Project map
README.md                               # Main README
QUICK_START.md                          # Onboarding (10 min)
TROUBLESHOOTING.md                      # FAQ + debug
GLOSSARY.md                             # Terminology
DEVELOPER_GUIDE.md                      # Architecture + API
```

### Данные категории

```
categories/{slug}/
├── urls_raw.txt                        # Stage -3 output
├── urls.txt                            # Stage -2 output
├── competitors/meta_competitors.csv    # MANUAL STAGE 3
├── research/perplexity_research.md     # MANUAL STAGE 3
├── data/{slug}.json                    # Stage 4 output
├── data/{slug}_keywords_distributed.json # Stage 6 output
├── content/{slug}_ru.md                # Stage 8 output
├── content/{slug}_uk.md                # Stage 9 output
├── meta/{slug}_meta.json               # Stage 10 output
└── deliverables/                       # Stage 11 output (5 files)
```

---

## 🛠️ Инструменты и версии

### PRIMARY (Required)

| Tool | Version | Purpose | GitHub |
|------|---------|---------|--------|
| **LTEX-LS** | 16.0.0 | Grammar + spelling | [valentjn/ltex-ls](https://github.com/valentjn/ltex-ls) |
| **Natasha** | 1.6.0 | Russian NLP (water, nausea) | [natasha/natasha](https://github.com/natasha/natasha) |
| **markdownlint-cli** | 0.45.0 | Markdown structure | [igorshubovych/markdownlint-cli](https://github.com/igorshubovych/markdownlint-cli) |
| **stop-words** | 2025.11.4 | Stopwords (32 langs) | [Alir3z4/stop-words](https://github.com/Alir3z4/stop-words) |

### SECONDARY (Optional)

| Tool | Version | Purpose | GitHub |
|------|---------|---------|--------|
| **TextDescriptives** | 2.8.4 | 44 readability metrics | [hlasse/textdescriptives](https://github.com/hlasse/textdescriptives) |
| **spaCy** | 3.8.8 | NLP framework | [explosion/spaCy](https://github.com/explosion/spaCy) |

### Testing

| Tool | Version | Purpose |
|------|---------|---------|
| **pytest** | 9.0.1 | Testing framework |
| **pytest-cov** | 7.0.0 | Coverage plugin |
| **pytest-mock** | 3.15.1 | Mocking support |

---

## 🔗 Быстрые ссылки

### Внутренние

- [INDEX.md](INDEX.md) — карта проекта
- [COMPONENT_INDEX.md](COMPONENT_INDEX.md) — поиск по функциям
- [TOOLS_INDEX.md](TOOLS_INDEX.md) — все зависимости
- [GLOSSARY.md](GLOSSARY.md) — все термины
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — FAQ + debug
- [GITHUB_MONITORING.md](GITHUB_MONITORING.md) — RSS feeds для updates

### Внешние

- [LTEX-LS Releases](https://github.com/valentjn/ltex-ls/releases)
- [Natasha Docs](https://natasha.ai/)
- [spaCy Russian Model](https://spacy.io/models/ru)
- [TextDescriptives Docs](https://hlasse.github.io/TextDescriptives/)

---

## ⚡ Частые сценарии

### 1. Запуск новой категории

```bash
# 1. Команда
"активная пена полный workflow"

# 2. Автоматически выполнятся Stage 0 → -3 → -2
# 3. Workflow остановится с сообщением о MANUAL STAGE 3
# 4. Выполните ручные шаги (Screaming Frog + Perplexity)
# 5. Возобновите:
"данные готовы, продолжай для активная-пена"
```

### 2. Проверка качества контента

```bash
# Быстрая проверка (основное)
python scripts/quality_runner.py \
    categories/aktivnaya-pena/content/aktivnaya-pena_ru.md \
    "активная пена" \
    B

# Результат в:
categories/aktivnaya-pena/content/aktivnaya-pena_ru_quality_report.json
```

### 3. Исправление ошибки валидатора

```bash
# 1. Валидатор вернул FAIL → читаем лог
cat categories/aktivnaya-pena/.logs/stage-4-data-validator.log

# 2. Проверяем JSON
python -m json.tool categories/aktivnaya-pena/data/aktivnaya-pena.json

# 3. Исправляем (Edit tool или вручную)
# 4. Перезапускаем валидатор
# Агент запустит автоматически при "продолжи для активная-pena"
```

### 4. Добавление нового keyword

```bash
# 1. Обновить {slug}.json (добавить keyword)
# 2. Перезапустить Stage 6 → 8
"сгенерируй контент для активная-пена"

# 3. Проверить coverage
python scripts/check_simple_v2_md.py \
    categories/aktivnaya-pena/content/aktivnaya-pena_ru.md \
    "новый keyword" \
    B
```

---

## 🎯 Tier Requirements

| Параметр | Tier A | Tier B | Tier C |
|----------|--------|--------|--------|
| **Keywords** | ≥15 | ≥10 | ≥5 |
| **H2 sections** | 3-4 | 2-3 | 2 |
| **FAQ items** | 5-6 | 4-5 | 3-4 |
| **Длина** | 4000-5000 chars | 4000-5000 chars | 4000-5000 chars |
| **Coverage** | ≥70% | ≥70% | ≥70% |
| **Density** | ≤2% | ≤2% | ≤2% |

**Примечание:** Длина одинакова для всех tier (4000-5000 символов БЕЗ пробелов).

---

## 📝 Checklist для нового агента

```markdown
- [ ] Создан .md файл в .claude/agents/
- [ ] Frontmatter: name, description, version
- [ ] Промпт следует AGENT_DESIGN_GUIDE.md
- [ ] Указаны required_tools
- [ ] Логи пишутся в categories/{slug}/.logs/{agent-name}.log
- [ ] Создан соответствующий валидатор в .claude/agents/validators/
- [ ] Валидатор возвращает exit code (0/1/2)
- [ ] Добавлен в README.md (.claude/agents/)
- [ ] Добавлен в WORKFLOW_DIAGRAM.md
- [ ] Добавлен в CLAUDE.md (workflow table)
```

---

**Версия:** 1.0 | **Updated:** 2025-11-17 | **Для:** Claude Code Orchestrator
