<div align="center">

# LLM Keywords Pipeline

**[English](README.md) · Русский · [Українська](README.uk.md)**

**Пайплайн для кластеризации ключей и проверки SEO-контента на русском и украинском языке.**

**Превращает сырой список ключей в SEO-группы, LLM-ready briefs и измеримые проверки текста: coverage, density, переспам, вода и тошнота.**

<p>
  <a href="https://github.com/yastman/llm-keywords-pipeline/actions/workflows/ci.yml">
    <img alt="CI" src="https://img.shields.io/github/actions/workflow/status/yastman/llm-keywords-pipeline/ci.yml?branch=main&label=tests&style=for-the-badge">
  </a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="uv" src="https://img.shields.io/badge/package%20manager-uv-6E56CF?style=for-the-badge">
  <img alt="Ruff" src="https://img.shields.io/badge/lint-ruff-46A758?style=for-the-badge">
  <img alt="Pytest" src="https://img.shields.io/badge/tests-pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white">
  <img alt="NLP" src="https://img.shields.io/badge/NLP-RU%20%2F%20UK-0E9F6E?style=for-the-badge">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-111111?style=for-the-badge">
</p>

</div>

```bash
uv sync --frozen
uv run ruff check src tests
uv run mypy
uv run pytest
uv build
```

---

## Какую боль решает

SEO-специалист часто начинает с грязной выгрузки семантики: дубли, синонимы, смешанный
коммерческий и информационный intent, частотности, заметки по конкурентам и текст,
который нужно проверить на покрытие ключей.

Руками это работает только на маленьком объеме. На каталоге из десятков или сотен
категорий нужна повторяемая система:

- загрузить или импортировать список ключей;
- сгруппировать ключи в понятные SEO-кластеры;
- отделить primary, secondary, supporting и commercial keywords;
- использовать TOP-10 SERP overlap и competitor research, если такой файл подготовлен;
- написать или сгенерировать текст по кластеризованному brief;
- проверить готовый текст на покрытие ключей;
- найти переспам, лишнюю воду и тошноту до публикации.

Этот репозиторий упаковывает такой workflow в Python-проект.

---

## Основной workflow

### 1. Адаптация списка ключей в JSON

Workflow начинается с выгрузки ключей: CSV или структурированного списка семантики.
Этот сырой вход адаптируется в category JSON files, чтобы весь дальнейший pipeline
работал не с таблицами, а с одним понятным контрактом данных.

В проекте есть несколько путей такого handoff:

- raw category JSON, например `categories/{slug}/data/{slug}.json`;
- кластеризованный clean JSON, например `categories/{slug}/data/{slug}_clean.json`;
- синхронизация master CSV в `_clean.json`;
- CSV restore/compare utilities для drift, missing keywords и изменившихся volumes.

D+E fallback pattern сначала берет `_clean.json`, потом raw parsed JSON, потом CSV
fallback. На практике `_clean.json` становится главным рабочим артефактом для следующих
этапов.

### 2. Кластеризация ключей

Ключи раскладываются по практическим SEO-ролям:

| Группа | Зачем нужна |
| --- | --- |
| `primary` | Главные запросы для H1, intro и основного intent страницы. |
| `secondary` | Смежные запросы, которые расширяют страницу без смены intent. |
| `supporting` | Long-tail и контекстные фразы для семантической глубины. |
| `commercial` | "Купить", "цена", "заказать" и похожие коммерческие модификаторы, часто для meta или commercial signals. |

Утилиты synonym cleanup нормализуют близкие варианты, выбирают лучший ключ по
частотности и качеству фразы, а слабые дубли убирают.

### 3. Подготовка research по категории

В исходном workflow также поддерживается отдельный файл SERP TOP-10: ключи можно
проверять по пересечению URL в выдаче Google. Если у двух запросов достаточно общих URL
в TOP-10, они могут попасть в один кластер или synonym group; если выдача заметно
отличается, ключ считается отдельным поисковым intent.

В исходном orchestrated workflow после кластеризации primary keyword, semantic groups,
entities, micro-intents и product insights использовались для генерации
`categories/{slug}/research/RESEARCH_PROMPT.md` под внешний web-research инструмент,
например Perplexity Deep Research или LLM agent с web search. Результат исследования
затем сохранялся в `categories/{slug}/research/RESEARCH_DATA.md`.

Этот файл не просто прикладывается к категории. Он становится brief для следующего
этапа: факты о продукте, структура конкурентов, intent пользователя, content gaps,
обязательные блоки, идеи для FAQ и риски, которые нужно учесть при написании SEO-текста.

Public package не включает старый Perplexity runner и приватные research outputs. В нём
сохранены prompt/checklist/reference материалы research stage и сам `RESEARCH_DATA.md`
как артефакт, который проверяется task generation.

### 4. Написание SEO-текста

Папка `prompts/` описывает prepare/produce/deliver flow для LLM-assisted writing:
прочитать кластеризованные ключи, определить primary keyword, учесть entity dictionary,
content rules и optional research, затем подготовить или проверить текст.

### 5. Проверка готового текста

Валидаторы отвечают на главный вопрос: текст реально покрывает brief или только
выглядит как SEO-текст?

- primary keyword в H1 и intro;
- morphology-aware coverage для русского и украинского;
- отдельное покрытие core и commercial keywords;
- keyword density и stem-based поиск переспама;
- вода, классическая тошнота, академическая тошнота, повтор лемм;
- структура H1/H2, качество intro, blacklist terms, brand/city mentions и meta sync.

---

## Почему это полезно

### Для SEO-специалиста

Проект превращает семантику в управляемый checklist: какие ключи брать в текст, какие
оставлять для meta, где не хватает coverage и где текст уже переоптимизирован.

### Для LLM-контента

LLM может быстро написать черновик, но пайплайн проверяет результат детерминированно:
ключи, структура, density, вода, тошнота и признаки SEO-спама.

### Для RU/UK каталогов

Проверки учитывают русский и украинский язык: tokenization, stopwords, stemming,
lemmatization и morphology-aware matching, а не только exact string match.

---

## Возможности

| Блок | Что делает |
| --- | --- |
| Keyword JSON adaptation | Превращает CSV/master/raw keyword data в category JSON и `_clean.json`, с которыми работает весь pipeline. |
| Keyword clustering | Строит clean keyword groups из raw/CSV/category data и разделяет intent roles. |
| SERP TOP-10 overlap | Использует пересечение URL в поисковой выдаче, чтобы понять: ключи в один кластер или это разные intents. |
| Synonym cleanup | Находит near-duplicates и нормализует конкурирующие варианты ключей. |
| Research prompt workflow | Превращает clustered keywords/entities/product insights в research prompt contract; public docs сохраняют workflow `RESEARCH_PROMPT.md` → `RESEARCH_DATA.md` → brief. |
| Content validation | Проверяет H1, intro, headings, keyword coverage, meta sync и языковые правила. |
| Density and spam | Ищет exact, partial, stem и substring overuse с warning/spam thresholds. |
| Water and nausea | Считает воду, классическую тошноту, академическую тошноту и повтор лемм. |
| Generation | Генерирует meta artifacts, SQL exports, semantic review files, catalog JSON и checklists. |
| Repair and sync | Обновляет volumes, восстанавливает `_clean.json` из CSV, merge master keyword data и чинит misplaced terms. |

---

## Структура проекта

```text
src/llm_keywords_pipeline/
  analyze/      анализ категории и metadata для LLM briefs
  audit/        water, nausea, coverage, blacklist, H1 и quality audits
  core/         keyword matching, morphology, SEO rules, text utilities
  generate/     meta, checklist, semantic review, catalog и export tools
  validate/     content, meta, heading, density, language и data validators
  sync/         CSV/master-data synchronization и _clean.json repair
  fix/          точечные cleanup utilities
  compare/      keyword distribution и dataset comparison helpers
tests/          pytest suite и public fixtures
prompts/        prepare/produce/deliver LLM workflow templates
docs/           architecture, testing и public-version notes
```

---

## Быстрый старт

Нужно: Python 3.12+ и [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/yastman/llm-keywords-pipeline.git
cd llm-keywords-pipeline

uv sync --frozen
uv run ruff check src tests
uv run mypy
uv run pytest
```

Запуск публичного fixture через packaged CLI:

```bash
uv run llm-keywords-audit-brands tests/fixtures/valid_content.md --json
```

Coverage:

```bash
uv run pytest --cov=src/llm_keywords_pipeline --cov-report=term-missing
```

Опциональный локальный database demo:

```bash
cp .env.example .env
docker compose up
```

Compose поднимает MariaDB и Adminer на localhost. Это локальный demo, не production
deployment recipe.

---

## Документация

| Документ | Что внутри |
| --- | --- |
| [Architecture](docs/architecture.md) | Package map, workflow boundaries, stable vs legacy surface. |
| [Testing](docs/testing.md) | Test tiers, default commands, CI parity, data-required skips. |
| [Research Workflow](docs/research-workflow.md) | Как clustered keywords превращались в `RESEARCH_PROMPT.md`, `RESEARCH_DATA.md` и content brief. |
| [Public Version](docs/public-version.md) | Что включено, что исключено и зачем оставлены prompts. |
| [Prompt Templates](prompts/README.md) | Prepare/produce/deliver LLM workflow templates. |

---

## Публичная граница

Репозиторий сохраняет инженерную структуру, тесты, fixtures и prompt workflow, но не
публикует приватные production datasets, generated reports, старые SERP TOP-10 exports и
external LLM orchestration. Часть утилит и docs ожидает оригинальный private data layout
и оставлена, чтобы показать реальную архитектуру проекта.

---

## Лицензия

MIT. См. [LICENSE](LICENSE).

---

Сырой список ключей легко выгрузить. Этот проект превращает его в кластеризованную
SEO-работу, которую можно написать, проверить и улучшить.
