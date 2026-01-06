# ТЗ: Финальная архитектура проекта

**Проект:** Ultimate.net.ua — SEO Content Pipeline
**Версия:** 4.0 (Post-Audit)
**Дата:** 2025-12-12
**Авторы:** Claude (Opus 4.5) + GPT + User

---

## 1. Суть проекта

**Что делаем:** SEO-тексты (RU) для категорий интернет-магазина автохимии.

```
Вход:  slug + tier (A/B/C)
Выход: текст RU + meta tags (RU)
Проверка: автоматические скрипты
```

**UK версия не требуется** — убираем из процесса.

---

## 2. Категории

### Всего: 17 L3 категорий

**Текущие (9 из блока "Мойка и Экстерьер"):**

| #   | Slug               | Tier | Keywords JSON | Content RU | Meta JSON | Статус   |
| --- | ------------------ | ---- | ------------- | ---------- | --------- | -------- |
| 1   | aktivnaya-pena     | A    | ✅            | ✅         | ✅        | **DONE** |
| 2   | dlya-ruchnoy-moyki | A    | ✅            | ❌         | ❌        | prepare  |
| 3   | ochistiteli-shin   | A    | ✅            | ❌         | ❌        | prepare  |
| 4   | glina-i-avtoskraby | A    | ✅            | ❌         | ❌        | prepare  |
| 5   | cherniteli-shin    | B    | ✅            | ❌         | ❌        | prepare  |
| 6   | ochistiteli-diskov | B    | ✅            | ❌         | ❌        | prepare  |
| 7   | ochistiteli-stekol | B    | ✅            | ❌         | ❌        | prepare  |
| 8   | antimoshka         | C    | ✅            | ❌         | ❌        | prepare  |
| 9   | antibitum          | C    | ✅            | ❌         | ❌        | prepare  |

**Дополнительные (8 из других блоков):**

Требуется: добавить slug-маппинг и task-файлы из `Лист1.csv`.

---

## 3. Режим работы

### Основной: 1 категория = 1 сессия

```
Контекст: ~35-40K токенов (15% от лимита 250K)

Что нужно:
├── SEO_MASTER.md  — единственный SSOT правил (RU-only)
├── keywords JSON  — из CSV (все 9 готовы!)
└── scripts/       — валидация

Что НЕ нужно:
├── Sub-agents     — не нужны для 1 категории
└── UK версия      — исключена
```

**Workflow:**

```
0. (разово) init — структура + task file
1. (разово) keywords JSON:
   python3 scripts/parse_semantics_to_json.py {slug} {tier}

2. Генерация (в сессии):
   - Читаю SEO_MASTER.md
   - Пишу RU текст
   - Создаю meta.json

3. Валидация:
   PYTHONPATH=. python3 scripts/quality_runner.py \
     categories/{slug}/content/{slug}_ru.md "{keyword}" {tier}

4. Fix если FAIL → повтор валидации
```

### Batch-режим: 5+ категорий (опционально)

```
Sub-agents через prompts/ или .claude/skills/:
├── PREPARE (haiku)  — init + data
├── PRODUCE (sonnet) — RU content + meta
└── DELIVER (sonnet) — validate + package

После Фазы 4: выбрать один SSOT для batch (prompts/ ИЛИ skills/).
```

---

## 4. Результаты аудита (2025-12-12)

### 4.1 Scripts (`scripts/`) — 11 Python + 4 Bash

| Скрипт                                   | LOC | Назначение                   | Docstrings     | Статус         |
| ---------------------------------------- | --- | ---------------------------- | -------------- | -------------- |
| `seo_utils.py`                           | 798 | Core library (22 функции)    | ✅ Полные      | ✅ OK          |
| `quality_runner.py`                      | 686 | Оркестратор 6 проверок       | ✅ Полные      | ✅ OK          |
| `check_simple_v2_md.py`                  | 976 | Density/coverage/commercial  | ✅ Полные      | ✅ OK          |
| `check_water_natasha.py`                 | 311 | Вода/тошнота (Natasha NLP)   | ✅ Полные      | ✅ OK          |
| `check_ner_brands.py`                    | 352 | NER + blacklist              | ✅ Полные      | ✅ OK          |
| `parse_semantics_to_json.py`             | 479 | CSV → keywords JSON          | ✅ Полные      | ✅ OK          |
| `extract_competitor_urls_v2.py`          | 548 | SERP → URLs                  | ✅ Хорошие     | ⚠️ Legacy пути |
| `filter_mega_competitors.py`             | 415 | MEGA CSV фильтр              | ✅ Хорошие     | ✅ OK          |
| `setup_all.py`                           | 380 | Batch init категорий         | ✅ Хорошие     | ✅ OK          |
| `url_preparation_filter_and_validate.py` | 301 | Фильтр + валидация URLs      | ✅ Минимальные | ✅ OK          |
| `mega_url_extract.py`                    | 310 | Агрегация для Screaming Frog | ✅ Минимальные | ✅ OK          |

**Итого:** 5945 LOC, 95% хорошо документированы

### 4.2 Skills (`.claude/skills/`) — 9 skills, 1176 LOC

| Skill           | Lines | Этап     | UK контент | Статус |
| --------------- | ----- | -------- | ---------- | ------ |
| seo-init        | 111   | prep     | НЕТ        | ✅ OK  |
| seo-data        | 160   | prep     | НЕТ        | ✅ OK  |
| seo-urls        | 89    | prep     | НЕТ        | ✅ OK  |
| seo-competitors | 114   | prep     | НЕТ        | ✅ OK  |
| seo-research    | 100   | optional | НЕТ        | ✅ OK  |
| seo-content     | 143   | produce  | НЕТ        | ✅ OK  |
| seo-validate    | 222   | deliver  | НЕТ        | ✅ OK  |
| seo-meta        | 78    | deliver  | НЕТ        | ✅ OK  |
| seo-package     | 125   | deliver  | НЕТ        | ✅ OK  |

**Проблемы найдены:** нет (RU-only sweep завершён)

### 4.3 Prompts (`prompts/`) — 3 файла, 803 LOC

| Файл       | Lines | Этап    | UK контент | Статус |
| ---------- | ----- | ------- | ---------- | ------ |
| prepare.md | 156   | PREPARE | НЕТ        | ✅ OK  |
| produce.md | 335   | PRODUCE | НЕТ        | ✅ OK  |
| deliver.md | 312   | DELIVER | НЕТ        | ✅ OK  |

**Дублирование:** `prompts/produce.md` и `skills/seo-content/SKILL.md` — 80% одинаковые!

### 4.4 Task Files — ✅ НАЙДЕНЫ

`task_{slug}.json` файлы созданы в корне проекта для всех категорий.

**Keywords JSON:** ✅ Все 9 категорий имеют `categories/{slug}/data/{slug}.json`

### 4.5 Categories — реальная структура

```
categories/
├── aktivnaya-pena/         ✅ ПОЛНАЯ (content + meta)
│   ├── content/            ✅ aktivnaya-pena_ru.md
│   ├── data/               ✅ aktivnaya-pena.json
│   └── meta/               ✅ aktivnaya-pena_meta.json
│
├── dlya-ruchnoy-moyki/     ⚠️ ТОЛЬКО ДАННЫЕ
│   └── data/               ✅ dlya-ruchnoy-moyki.json
│
└── [остальные 7]           ⚠️ ТОЛЬКО ДАННЫЕ
```

### 4.6 Tests — 196 passed

| Coverage              | Статус                 |
| --------------------- | ---------------------- |
| seo_utils.py          | 90%                    |
| check_simple_v2_md.py | 85%                    |
| quality_runner.py     | 61%                    |
| url_filters.py        | 95%                    |
| **Всего**             | 196 passed, 10 skipped |

### 4.7 Claude конфигурация (`.claude/`)

| Директория        | Содержимое            | Действие                |
| ----------------- | --------------------- | ----------------------- |
| `skills/`         | 10 skills             | ✅ Оставить (убрать UK) |
| `skills_archive/` | Дубликаты skills      | ❌ Удалить              |
| `agents_archive/` | 11 deprecated агентов | ❌ Удалить              |
| `commands/`       | 1 orphan файл         | ❌ Удалить              |

---

## 5. Выявленные проблемы

### 5.1 Критические

| #   | Проблема                                | Где                                                                                                                               | Действие                                             |
| --- | --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| 1   | UK контент в seo-content/SKILL.md       | `.claude/skills/seo-content/`                                                                                                     | Убрать упоминание UK                                 |
| 2   | UK контент в produce.md                 | `prompts/produce.md`                                                                                                              | Убрать упоминание UK                                 |
| 3   | Task files не созданы                   | Корень проекта                                                                                                                    | Создать task\_{slug}.json                            |
| 4   | seo-translator skill не нужен           | `.claude/skills/seo-translator/`                                                                                                  | Архивировать                                         |
| 5   | RU+UK описаны как активные              | `README.md`, `categories/README.md`, `CLAUDE.md`, `prompts/deliver.md`, `.claude/skills/seo-meta/`, `.claude/skills/seo-package/` | Провести RU-only sweep по докам/скиллам/meta/package |
| 6   | Task schema не зафиксирована            | `task_{slug}.json` (отсутствуют)                                                                                                  | Утвердить JSON схему и обновить `setup_all.py`       |
| 7   | Версионный дрейф (v4.0 vs v4.3 vs v1.0) | `TZ_FINAL.md`, `README.md`, `SEO_MASTER.md`                                                                                       | Синхронизировать версии/архитектуру                  |

### 5.2 Дублирование

| #   | Проблема                      | Файлы                                         | Действие          |
| --- | ----------------------------- | --------------------------------------------- | ----------------- |
| 5   | 80% дублирование produce      | `prompts/produce.md` vs `skills/seo-content/` | Выбрать один SSOT |
| 6   | skills_archive = копии skills | `.claude/skills_archive/`                     | Удалить           |

### 5.3 Мусор (clutter)

| #   | Что                     | Размер    | Действие |
| --- | ----------------------- | --------- | -------- |
| 7   | agents_archive          | 11 файлов | Удалить  |
| 8   | commands/seo-content.md | 284 bytes | Удалить  |
| 9   | Дубликаты CSV в корне   | 2 файла   | Удалить  |

---

## 6. Целевая архитектура

### Файловая структура (после cleanup)

```
/
├── CLAUDE.md                 # Команды (3 штуки)
├── SEO_MASTER.md             # Единственный SSOT правил (RU-only)
├── README.md                 # Описание проекта
│
├── categories/
│   └── {slug}/
│       ├── data/             # keywords JSON ✅
│       ├── content/          # RU текст
│       ├── meta/             # meta.json (RU)
│       ├── competitors/      # URLs (опционально)
│       ├── deliverables/     # финальные файлы
│       └── .logs/
│
├── scripts/                  # 11 Python скриптов ✅
│
├── prompts/                  # Для batch (RU-only)
│   ├── prepare.md
│   ├── produce.md            # БЕЗ UK!
│   └── deliver.md
│
├── .claude/
│   └── skills/               # 9 skills (без seo-translator)
│
├── data/
│   └── *.csv                 # Семантика
│
├── tests/                    # 196 tests ✅
└── venv/
```

### Что удаляем

```
❌ .claude/skills_archive/     # дубликаты
❌ .claude/agents_archive/     # deprecated
❌ .claude/commands/           # orphan
❌ .claude/skills/seo-translator/  # не нужен для RU-only
❌ Дубликаты CSV в корне
```

---

## 7. План выполнения (обновлённый)

### Фаза 1: Cleanup (30 мин)

| #   | Задача                      | Команда                                      | Статус             |
| --- | --------------------------- | -------------------------------------------- | ------------------ |
| 1.1 | Удалить skills_archive      | `rm -rf .claude/skills_archive/`             | [x] ✓ (2025-12-12) |
| 1.2 | Удалить agents_archive      | `rm -rf .claude/agents_archive/`             | [x] ✓ (2025-12-12) |
| 1.3 | Удалить commands            | `rm -rf .claude/commands/`                   | [x] ✓ (2025-12-12) |
| 1.4 | Архивировать seo-translator | `mv .claude/skills/seo-translator/ archive/` | [x] ✓ (2025-12-12) |
| 1.5 | Удалить дубликаты CSV       | Проверить и удалить                          | [x] ✓ (2025-12-12) |

### Фаза 2: RU-only sweep (1 час)

| #   | Задача                                        | Файл                                                                            | Статус             |
| --- | --------------------------------------------- | ------------------------------------------------------------------------------- | ------------------ |
| 2.1 | Убрать UK из seo-content                      | `.claude/skills/seo-content/SKILL.md`                                           | [x] ✓ (2025-12-12) |
| 2.2 | Убрать UK из produce.md                       | `prompts/produce.md`                                                            | [x] ✓ (2025-12-12) |
| 2.3 | Обновить SEO_MASTER.md (TL;DR + RU-only)      | `SEO_MASTER.md`                                                                 | [x] ✓ (2025-12-12) |
| 2.4 | Убрать UK из deliver.md + meta/package skills | `prompts/deliver.md`, `.claude/skills/seo-meta/`, `.claude/skills/seo-package/` | [x] ✓ (2025-12-12) |
| 2.5 | Убрать UK из README/CLAUDE/categories README  | `README.md`, `CLAUDE.md`, `categories/README.md`                                | [x] ✓ (2025-12-12) |
| 2.6 | Обновить setup_all.py (убрать UK пути)        | `scripts/setup_all.py`                                                          | [x] ✓ (2025-12-12) |

### Фаза 3: Task Files (30 мин)

| #   | Задача                                         | Статус             |
| --- | ---------------------------------------------- | ------------------ |
| 3.1 | Определить schema для task\_{slug}.json        | [x] ✓ (2025-12-12) |
| 3.2 | Создать task files для 9 категорий             | [x] ✓ (2025-12-12) |
| 3.3 | Обновить setup_all.py для генерации task files | [x] ✓ (2025-12-12) |

### Фаза 4: Документация (30 мин)

| #   | Задача                                          | Файл                                        | Статус             |
| --- | ----------------------------------------------- | ------------------------------------------- | ------------------ |
| 4.1 | Обновить CLAUDE.md (3 команды)                  | `CLAUDE.md`                                 | [x] ✓ (2025-12-12) |
| 4.2 | Обновить README.md                              | `README.md`                                 | [x] ✓ (2025-12-12) |
| 4.3 | Синхронизировать версии (v4.x, SEO_MASTER v7.3) | `TZ_FINAL.md`, `README.md`, `SEO_MASTER.md` | [x] ✓ (2025-12-12) |

### Фаза 5: Выбор SSOT для batch

| #   | Задача                       | Статус |
| --- | ---------------------------- | ------ |
| 5.1 | Решить: prompts/ ИЛИ skills/ | [ ]    |
| 5.2 | Архивировать неиспользуемый  | [ ]    |

**Рекомендация:** Оставить `prompts/` (используется Sub-agents), skills использовать для single-category mode.

### Фаза 6: Тестирование (2-3 часа)

| #   | Задача                             | Категория                   | Статус |
| --- | ---------------------------------- | --------------------------- | ------ |
| 6.1 | Тест минимального режима           | dlya-ruchnoy-moyki (Tier A) | [ ]    |
| 6.2 | Замерить время на категорию        | Зафиксировать baseline      | [ ]    |
| 6.3 | Сравнить качество с aktivnaya-pena | Качество ≥ baseline         | [ ]    |
| 6.4 | Тест ещё 1-2 категорий             | Любые pending               | [ ]    |

### Фаза 7: Расширение до 17 L3

| #   | Задача                                 | Статус |
| --- | -------------------------------------- | ------ |
| 7.1 | Добавить slug-маппинг для 8 новых L3   | [ ]    |
| 7.2 | Создать task-файлы для новых категорий | [ ]    |
| 7.3 | Проверить keywords CSV для новых       | [ ]    |

### Фаза 8: Финальная архивация

| #   | Задача                                | Статус |
| --- | ------------------------------------- | ------ |
| 8.1 | Архивировать TZ\_\*.md (включая этот) | [ ]    |
| 8.2 | Финальный cleanup                     | [ ]    |

---

## 8. Deliverables

### Для каждой категории

```
categories/{slug}/
├── content/{slug}_ru.md      # Текст RU
├── meta/{slug}_meta.json     # Meta RU
└── deliverables/
    ├── {slug}_ru.md          # Копия
    ├── {slug}_meta.json      # Копия
    └── QUALITY_REPORT.md     # Отчёт валидации
```

### Meta формат

```json
{
  "title": "Активная пена | Купить с доставкой – Ultimate",
  "description": "Купить активную пену для бесконтактной мойки от 150 грн. Доставка 1-2 дня по Украине. ✓ В наличии ✓ Гарантия.",
  "h1": "Активная пена для автомойки"
}
```

---

## 9. Критерии успеха

### Функциональные

- [ ] Замерить время на категорию (Фаза 6)
- [ ] Валидация PASS с первой попытки >80%
- [ ] Качество ≥ aktivnaya-pena
- [ ] Все 17 категорий обработаны

### Архитектурные

- [ ] Контекст ≤50K
- [ ] Один SSOT правил (SEO_MASTER.md)
- [ ] Один SSOT для batch (prompts/ ИЛИ skills/)
- [ ] UK убран из всех активных файлов
- [ ] Нет дубликатов и мусора

### Технические

- [ ] Task files созданы для всех категорий
- [ ] Тесты проходят (196 passed)
- [ ] Scripts используют `categories/{slug}/` пути

---

## 10. Риски

| Риск                           | Митигация                                    |
| ------------------------------ | -------------------------------------------- |
| Регрессия после RU-only sweep  | Тесты + проверка на 2-3 категориях           |
| Task files schema неправильная | Проверить на aktivnaya-pena                  |
| Skills нужны для batch         | Не удаляем, только архивируем seo-translator |

---

## 11. Метрики проекта (из аудита)

| Метрика               | Значение      |
| --------------------- | ------------- |
| Python скриптов       | 11 (5945 LOC) |
| Skills                | 10 (1176 LOC) |
| Prompts               | 3 (803 LOC)   |
| Тестов                | 196 passed    |
| Категорий готовых     | 1/9 (11%)     |
| Keywords JSON готовых | 9/9 (100%)    |
| Test coverage         | ~85%          |

---

## 12. Следующий шаг

**Фаза 1.1:** Начать cleanup — удалить skills_archive, agents_archive, commands.

```bash
rm -rf .claude/skills_archive/
rm -rf .claude/agents_archive/
rm -rf .claude/commands/
```

---

**Версия:** 4.0 (Post-Audit)
**Статус:** Утверждено
**Дата:** 2025-12-12
**Правки v4.0:**

- Добавлены результаты полного аудита
- Реальное состояние скриптов (11 Python, 5945 LOC)
- Реальное состояние skills (10 skills, UK в 2-х)
- Выявлены task files — НЕ СОЗДАНЫ
- Выявлено дублирование prompts/skills (80%)
- Конкретный список мусора для удаления
- 8 фаз вместо 7
