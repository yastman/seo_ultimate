# Vision — SEO Content Pipeline

**Автор:** Claude Opus 4.5 (Оркестратор)
**Дата:** 2025-12-12
**Статус:** Анализ после изучения проекта

---

## Цель проекта

Генерация SEO-текстов для категорий интернет-магазина Ultimate.net.ua (автохимия).

```
Input:  slug + tier (A/B/C)
Output: текст RU (~2000 символов) + meta tags
```

---

## Текущее состояние

### Что есть (избыточно)

| Компонент | Количество | Проблема |
|-----------|------------|----------|
| Skills (.claude/skills/) | 9 штук | Дублируют SEO_MASTER |
| Prompts (prompts/) | 3 файла | Дублируют SEO_MASTER |
| Docs (docs/archive/) | 12 файлов | Мёртвый груз |
| Scripts | 11 штук | Только 3 реально нужны |
| CSV файлы | 3 штуки | Путаница с источником |

### Критическая проблема

**Keywords JSON сломаны** для большинства категорий:

- `dlya-ruchnoy-moyki.json` — содержит keywords про омыватели (WRONG)
- `ochistiteli-shin.json` — содержит keywords про обезжириватели (WRONG)
- Причина: `parse_semantics_to_json.py` неправильно парсит CSV структуру

**Только `aktivnaya-pena.json` корректен** (проверено, PASS).

---

## Моё видение: Минимальный pipeline

### Файловая структура

```
/
├── SEO_MASTER.md           # Единственный SSOT правил
├── task.md                 # Текущие задачи
├── ORCHESTRATOR_PROMPT.md  # Инструкция для сессии
│
├── categories/
│   └── {slug}/
│       ├── keywords.json   # Ручной или проверенный
│       ├── content_ru.md   # Результат
│       └── meta.json       # Meta tags
│
├── scripts/
│   ├── quality_runner.py   # Главный валидатор
│   ├── check_water_natasha.py
│   └── check_simple_v2_md.py
│
└── archive/                # Всё остальное
```

### Workflow (3 шага)

```
1. PREPARE
   - Проверить/создать keywords.json для категории
   - Источник: ручной ввод ИЛИ исправленный парсер

2. GENERATE
   - Читаю SEO_MASTER.md (правила)
   - Читаю keywords.json (ключевые слова)
   - Пишу текст RU + meta

3. VALIDATE
   - quality_runner.py
   - Если FAIL → исправляю → повтор
```

### Роли

| Роль | Модель | Что делает |
|------|--------|------------|
| Оркестратор | Opus 4.5 | Планирует, проверяет, обновляет task.md |
| Worker | Sonnet | Генерирует контент по ТЗ из task.md |

**Sub-agents НЕ нужны** — прямая работа через task.md.

---

## Что убрать

### Сейчас

```
rm -rf .claude/skills/          # 9 skills → archive
rm -rf prompts/                  # 3 prompts → archive
rm -rf docs/archive/             # 12 файлов мусора
```

### Оставить

```
SEO_MASTER.md                   # Правила (441 строка)
scripts/quality_runner.py       # Валидация
scripts/check_water_natasha.py  # Water/Nausea
scripts/check_simple_v2_md.py   # Density/Keywords
```

---

## Решение проблемы с keywords

### Вариант A: Ручной ввод (быстро)

Для каждой категории создать keywords.json вручную:

- 5-10 primary keywords
- 10-15 secondary
- Остальные supporting

### Вариант B: Исправить парсер (правильно)

Переписать `parse_semantics_to_json.py`:

- Корректно обрабатывать L1/L2/L3 иерархию
- Не смешивать keywords между категориями

### Вариант C: Новый CSV (идеально)

Создать чистый CSV с правильной структурой:

```
slug,keyword,volume,intent
aktivnaya-pena,пена для мойки авто,1300,informational
aktivnaya-pena,купить активную пену,590,commercial
...
```

---

## План действий

### Фаза 1: Cleanup (1 час)

- [ ] Архивировать skills/, prompts/, docs/archive/
- [ ] Удалить дубликаты
- [ ] Оставить только нужные скрипты

### Фаза 2: Keywords Fix (2-3 часа)

- [ ] Проверить ВСЕ keywords.json на релевантность
- [ ] Исправить или создать заново для каждой категории
- [ ] Выбрать источник: ручной / парсер / новый CSV

### Фаза 3: Test Run (1 категория)

- [ ] Взять категорию с правильными keywords
- [ ] Сгенерировать контент
- [ ] Валидация до PASS
- [ ] Зафиксировать время и токены

### Фаза 4: Production (8 категорий)

- [ ] Повторить для остальных
- [ ] Документировать результаты

---

## Тесты и валидация (КРИТИЧНО)

### Текущее покрытие

| Скрипт | Coverage | Статус |
|--------|----------|--------|
| quality_runner.py | 10% | CRITICAL |
| check_water_natasha.py | 37% | LOW |
| check_simple_v2_md.py | 64% | OK |
| seo_utils.py | 76% | OK |
| **Общий** | **35%** | **Нужно >60%** |

**Тестов:** 328 passed, 4 skipped

### TDD подход

```
1. ПЕРЕД изменением
   └── pytest tests/ -v (все зелёные?)

2. Изменение кода/контента

3. ПОСЛЕ изменения
   ├── pytest tests/ -v (регрессия?)
   └── quality_runner.py (валидация контента)
```

### Валидация контента (5 checks)

| Check | Скрипт | Что проверяет |
|-------|--------|---------------|
| 1. Markdown | pymarkdownlnt | Структура MD |
| 2. Grammar | language_tool | Грамматика (опционально) |
| 3. Water/Nausea | check_water_natasha.py | Вода 40-60%, тошнота ≤3.5 |
| 4. Keywords | check_simple_v2_md.py | Density, coverage |
| 5. NER/Blacklist | check_ner_brands.py | Бренды, города, AI-fluff |

### Команды

```bash
# Тесты (перед любым изменением)
source venv/bin/activate
pytest tests/ -v

# Тесты с coverage
pytest tests/ --cov=scripts --cov-report=term-missing

# Валидация контента
PYTHONPATH=. python3 scripts/quality_runner.py \
  categories/{slug}/content/{slug}_ru.md "{keyword}" {tier}
```

### Правило

**НЕ мержить/коммитить если:**

- pytest показывает FAIL
- quality_runner.py даёт exit code 2

---

## Метрики успеха

| Метрика | Target |
|---------|--------|
| Время на категорию | <30 мин |
| Валидация PASS с 1-й попытки | >70% |
| Файлов в проекте | <30 (сейчас >100) |
| Coverage тестов | >60% (сейчас 35%) |
| pytest green | 100% |

---

## Вывод

Проект переусложнён. 9 skills, 3 prompts, 12 архивных docs — для задачи "написать 9 текстов по 2000 символов".

**Нужно:**

1. Почистить
2. Исправить keywords
3. Писать тексты

**Не нужно:**

- Sub-agents
- State machine
- Сложный workflow

---

**Следующий шаг:** Решение по keywords (A/B/C) и cleanup.
