# PROJECT ASSESSMENT — Ultimate.net.ua SEO Content Pipeline

Дата: 2025-12-15  
Контекст: ревью репозитория + сверка с `master_plan.md`

## 1) Итоговая оценка (TL;DR)

Проект уже находится в рабочем состоянии как “контентная фабрика” с хорошей инженерной базой: есть воспроизводимые скрипты, D+E fallback, единый валидатор (по замыслу), большая тестовая база (455 тестов), и понятная целевая архитектура “analyze → generate → validate → (heal)”.

Основные проблемы сейчас не в “генерации текста”, а в **стабильности и согласованности системы**:

- **SSOT-дрейф**: дубли логики (особенно очистка Markdown и пороги/правила) между `validate_content.py` и `seo_utils.py`, а также смешение стандартов v7.3 (tier/длина/density) и v8.3 (depth-over-length).
- **Документация и навигация**: часть ссылок/версий в root-доках не соответствует фактической структуре репо (пример: `INDEX.md` и `categories/README.md` отсутствуют в корне).
- **Критический функциональный баг для DoD**: false positive в blacklist брендов (BUG-003) ломает требование “без FAIL”.
- **Ключевые CLI-скрипты не покрыты тестами**: `validate_content.py` и `batch_generate.py` имеют 0% coverage — это главный риск при масштабировании на 50+ категорий.

## 2) Что подтверждено фактом (что я реально увидел/прогнал)

### 2.1 Тесты и покрытие

Запуск: `./venv/bin/python -m pytest -q`

- Pytest: **455 passed**
- Coverage: **~68%**
- “Дыры” по покрытию: `scripts/validate_content.py` и `scripts/batch_generate.py` — **0%**.

### 2.2 Состояние 9 категорий по `validate_content.py`

Я прогнал `validate_content.py` для всех 9 папок в `categories/`, используя primary keyword из `scripts/analyze_category.py` и `--with-analysis <slug>`.

Результат:

| slug | статус |
|------|--------|
| `aktivnaya-pena` | FAIL |
| остальные 8 slug | WARNING |

Причины:
- `aktivnaya-pena`: **FAIL по blacklist (бренд)** — соответствует BUG-003 (“(Karcher и др.)”).
- остальные: в основном **WARNING по coverage** (что соответствует философии “не блокировать всё подряд”).

Важно: вывод валидатора сейчас может быть **неинтуитивен**: блок “PRIMARY KEYWORD” печатает exact-match поля (`In H1`, `In Intro`), но общий статус может быть поднят семантическим матчингом — это создаёт “визуальный конфликт” в отчёте.

## 3) Насколько `master_plan.md` совпадает с реальностью

`master_plan.md` хорошо совпадает с проектом по ключевым тезисам:

- Правильно выделен главный технический долг: **SSOT для очистки Markdown/метрик** и консолидация валидатора.
- Правильно выделена главная инженерная необходимость: **тесты для `validate_content.py` и `batch_generate.py`**.
- Верно указан “разрыв” между анализом и генерацией: нужен единый “мост” (wrapper-команда), которая формирует prompt, сохраняет результаты, запускает validate, готовит fix-request.
- Верно обозначен BUG-003 как blocker для “без FAIL”.

Где есть расхождения/нехватка точности:

- В репозитории одновременно живут документы/формулировки **v7.3 и v8.3**, и это реально влияет на поведение пайплайна (валидатор/скиллы/README не всегда согласованы).
- “Smoke по slug одной командой” в текущем виде требует обёртки: `validate_content.py` ожидает `<file.md> <keyword>`, а `--with-analysis <slug>` лишь добавляет keywords list для coverage. Для удобного “по всем slug” нужен отдельный скрипт/CLI.

## 4) Сильные стороны проекта

- **Хороший каркас пайплайна**:
  - `scripts/analyze_category.py` делает D+E fallback: `_clean.json → .json → CSV`.
  - `scripts/validate_content.py` концентрирует checks: структура, primary keyword, coverage, quality (water/nausea), blacklist, опционально grammar и md-lint.
  - `scripts/batch_generate.py` уже содержит заготовку self-heal (генерация fix prompt).
- **Тестирование как культура**: 455 тестов, много unit-тестов вокруг утилит и парсеров.
- **Чёткая продуктовая рамка**: “Buying guide, depth over length, editorial полезность”.
- **Разделение входных данных и workspace**: `data/` (CSV) и `categories/{slug}/...` (артефакты по категории).

## 5) Основные риски (для масштабирования на 50+ категорий)

### 5.1 SSOT-дрейф (самый опасный)

Сейчас в `scripts/validate_content.py` существует локальная функция `clean_markdown`, хотя уже есть каноническая `scripts/seo_utils.clean_markdown`. Это неизбежно приводит к расхождениям метрик (water/nausea/coverage), особенно при изменениях Markdown-очистки (код-блоки, таблицы, inline-code, YAML front matter).

### 5.2 Документация/навигация и “версионность стандартов”

Есть несогласованность между:
- root `README.md` (указан Version 5.0) и фактическими документами про v8.3 подход,
- `.claude/README.md` (ещё упоминается `quality_runner.py` как валидатор),
- `scripts/README.md` и `.claude/skills/seo-validate/SKILL.md` (уже ориентированы на `validate_content.py`).

Плюс ссылки: root `README.md` ссылается на `INDEX.md` и `categories/README.md`, которых нет в корне (фактически `archive/INDEX.md` существует).

Это критично для “Claude-first workflow”: агент/оператор будет действовать по неверным инструкциям.

### 5.3 BUG-003 (бренды в нейтральных контекстах)

Пока blacklist не различает “упоминание как пример (… и др.)” и “прямую рекламу/продвижение бренда”, DoD “все slug без FAIL” будет регулярно рушиться на нормальных таблицах/примерах.

### 5.4 Primary keyword policy

`analyze_category.py` выбирает primary как keyword с максимальным volume. На некоторых категориях это может быть “коммерческий хвост” (“купить …”), и тогда валидатор будет просить “купить …” в H1/intro. Семантический матчинг частично лечит, но методологически лучше разделить:
- `primary_topic` (H1/introduction intent),
- `commercial_kw` (вставки/FAQ/блок “покупка/цена/доставка”).

### 5.5 Интеграционные сценарии не проверяются тестами

Даже с большим числом unit-тестов, именно “end-to-end” сценарии (анализ → валидатор → интерпретация результата → фиксы → ре-валидация) сейчас не защищены от регрессий, потому что ключевые orchestrator-скрипты не покрыты.

## 6) Приоритетные рекомендации (минимально достаточный план)

### P0 (снять blockers для DoD и стабильности)

1) Починить BUG-003 в `scripts/check_ner_brands.py` (контекст “(… и др.)”, whitelist/regex/контекст таблиц).  
2) Сделать `scripts/validate_content.py` SSOT-совместимым:
   - использовать `scripts/seo_utils.clean_markdown` (и по возможности общие пороги `QUALITY_THRESHOLDS`),
   - убрать локальную реализацию очистки/дубли.
3) Синхронизировать “точку входа” в доках:
   - выбрать один “главный” документ (например, `master_plan.md` + краткий `README.md`),
   - устранить битые ссылки/не существующие файлы в root навигации.

### P1 (масштабирование без сюрпризов)

4) Добавить тесты на `scripts/validate_content.py` (структура/semantic match/blacklist/water-nausea/coverage).  
5) Добавить тесты на `scripts/batch_generate.py` (минимум: корректный разбор статусов + генерация fix_prompt + поведение resume).  
6) Сделать отдельный smoke-runner “по всем slug” (скрипт, который сам берёт primary keyword из анализа и прогоняет validate).

### P2 (UX и “мост” analyze→generate→validate)

7) Не делать `create_content.py` как отдельный оркестратор: при принятом решении **Opus 4.5 = оркестратор**, и дублировать его в Python-скрипте не нужно. Вместо этого:
   - оформить “one-command” UX через инструкции оркестратора/skills (единая команда → analyze → генерация → validate → фиксы),
   - при необходимости добавить только узкие утилиты (например, smoke-runner или генератор fix-request), но не “master conductor”.

## 7) Рекомендация по Definition of Done (уточнить формулировку)

С учётом философии “Google 2025: метрики — не догма” я бы закрепил:
- **FAIL**: только реальные blockers (структура, strict phrases, экстремальная вода/тошнота).
- **WARNING**: coverage/length/AI-fluff/grammar — допускаются, но должны быть перечислены и понятны причины.
- DoD лучше формулировать как: “все slug проходят без FAIL, warnings не превышают N и описаны/приняты”.

## 8) Быстрые команды для контроля (что реально полезно оператору)

- Тесты: `./venv/bin/python -m pytest -q`
- Анализ категории: `./venv/bin/python scripts/analyze_category.py <slug> --json`
- Валидация файла: `./venv/bin/python scripts/validate_content.py categories/<slug>/content/<slug>_ru.md "<primary_kw>" --with-analysis <slug>`
- Batch статус: `./venv/bin/python scripts/batch_generate.py --list`

---

Если хочешь, следующим шагом могу:
1) исправить BUG-003 так, чтобы `aktivnaya-pena` перестала падать, и
2) добавить минимальный smoke-runner по всем slug (одна команда для DoD).
