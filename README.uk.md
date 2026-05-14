<div align="center">

# LLM Keywords Pipeline

**[English](README.md) · [Русский](README.ru.md) · Українська**

**Пайплайн для кластеризації ключів і перевірки SEO-контенту українською та російською мовами.**

**Перетворює сирий список ключів на SEO-групи, LLM-ready briefs і вимірювані перевірки тексту: coverage, density, переспам, вода та нудота.**

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
uv sync
uv run ruff check src tests
uv run pytest
```

---

## Яку проблему розв'язує

SEO-спеціаліст часто починає з брудного експорту семантики: дублікати, синоніми,
змішаний комерційний та інформаційний intent, частотності, нотатки щодо конкурентів і
текст, який треба перевірити на покриття ключів.

Вручну це працює лише на малому обсязі. Для каталогу з десятків або сотень категорій
потрібна повторювана система:

- завантажити або імпортувати список ключів;
- згрупувати ключі у зрозумілі SEO-кластери;
- відокремити primary, secondary, supporting і commercial keywords;
- використати TOP-10 SERP overlap і competitor research, якщо такий файл підготовлений;
- написати або згенерувати текст за кластеризованим brief;
- перевірити готовий текст на покриття ключів;
- знайти переспам, зайву воду та нудоту до публікації.

Цей репозиторій пакує такий workflow у Python-проєкт.

---

## Основний workflow

### 1. Імпорт семантики

Пайплайн працює зі structured category data, `_clean.json`, raw JSON exports і
CSV-семантикою. D+E fallback pattern спочатку бере кластеризований clean-файл, потім
raw JSON, потім CSV fallback.

### 2. Кластеризація ключів

Ключі розкладаються за практичними SEO-ролями:

| Група | Для чого потрібна |
| --- | --- |
| `primary` | Головні запити для H1, intro та основного intent сторінки. |
| `secondary` | Суміжні запити, що розширюють сторінку без зміни intent. |
| `supporting` | Long-tail і контекстні фрази для семантичної глибини. |
| `commercial` | "Купити", "ціна", "замовити" та схожі комерційні модифікатори, часто для meta або commercial signals. |

Утиліти synonym cleanup нормалізують близькі варіанти, обирають сильніший ключ за
частотністю та якістю фрази, а слабкі дублікати прибирають.

### 3. Підготовка research для категорії

В оригінальному workflow також підтримується окремий файл SERP TOP-10: ключі можна
перевіряти за перетином URL у видачі Google. Якщо два запити мають достатньо спільних
URL у TOP-10, вони можуть потрапити в один кластер або synonym group; якщо видача
помітно відрізняється, ключ вважається окремим пошуковим intent.

Після кластеризації primary keyword і семантичні групи використовуються, щоб
сформувати research prompt для зовнішнього web-research інструмента, наприклад
Perplexity або LLM agent з web search. Результат зберігається в
`categories/{slug}/research/RESEARCH_DATA.md`.

Цей файл не просто додається до категорії. Він стає brief для наступного етапу: факти
про продукт, структура конкурентів, intent користувача, content gaps, обов'язкові
блоки, ідеї для FAQ і ризики, які треба врахувати під час написання SEO-тексту. У
публічній версії приватні SERP-дані та старі extraction outputs не публікуються, але
сам research-artifact workflow збережений.

### 4. Написання SEO-тексту

Папка `prompts/` описує prepare/produce/deliver flow для LLM-assisted writing:
прочитати кластеризовані ключі, визначити primary keyword, врахувати entity dictionary,
content rules і optional research, потім підготувати або перевірити текст.

### 5. Перевірка готового тексту

Валідатори відповідають на головне питання: текст справді покриває brief чи лише
виглядає як SEO-текст?

- primary keyword у H1 та intro;
- morphology-aware coverage для української та російської;
- окреме покриття core і commercial keywords;
- keyword density і stem-based пошук переспаму;
- вода, класична нудота, академічна нудота, повтор лем;
- структура H1/H2, якість intro, blacklist terms, brand/city mentions і meta sync.

---

## Чому це корисно

### Для SEO-спеціаліста

Проєкт перетворює семантику на керований checklist: які ключі брати в текст, які
залишати для meta, де бракує coverage і де текст уже переоптимізований.

### Для LLM-контенту

LLM може швидко написати чернетку, але пайплайн перевіряє результат детерміновано:
ключі, структура, density, вода, нудота та ознаки SEO-спаму.

### Для RU/UK каталогів

Перевірки враховують українську та російську мову: tokenization, stopwords, stemming,
lemmatization і morphology-aware matching, а не лише exact string match.

---

## Можливості

| Блок | Що робить |
| --- | --- |
| Keyword clustering | Будує clean keyword groups із raw/CSV/category data і розділяє intent roles. |
| SERP TOP-10 overlap | Використовує перетин URL у пошуковій видачі, щоб зрозуміти: ключі в один кластер чи це різні intents. |
| Synonym cleanup | Знаходить near-duplicates і нормалізує конкуруючі варіанти ключів. |
| Research prompt workflow | Перетворює кластеризовані ключі на web-research prompt, зберігає `RESEARCH_DATA.md` і використовує його як brief для генерації тексту. |
| Content validation | Перевіряє H1, intro, headings, keyword coverage, meta sync і мовні правила. |
| Density and spam | Шукає exact, partial, stem і substring overuse з warning/spam thresholds. |
| Water and nausea | Рахує воду, класичну нудоту, академічну нудоту і повтор лем. |
| Generation | Генерує meta artifacts, SQL exports, semantic review files, catalog JSON і checklists. |
| Repair and sync | Оновлює volumes, відновлює `_clean.json` із CSV, merge master keyword data і виправляє misplaced terms. |

---

## Структура проєкту

```text
src/llm_keywords_pipeline/
  analyze/      аналіз категорії та metadata для LLM briefs
  audit/        water, nausea, coverage, blacklist, H1 і quality audits
  core/         keyword matching, morphology, SEO rules, text utilities
  generate/     meta, checklist, semantic review, catalog і export tools
  validate/     content, meta, heading, density, language і data validators
  sync/         CSV/master-data synchronization і _clean.json repair
  fix/          сфокусовані cleanup utilities
  compare/      keyword distribution і dataset comparison helpers
tests/          pytest suite і public fixtures
prompts/        prepare/produce/deliver LLM workflow templates
docs/           architecture, testing і public-version notes
```

---

## Швидкий старт

Потрібно: Python 3.12+ і [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/yastman/llm-keywords-pipeline.git
cd llm-keywords-pipeline

uv sync
uv run ruff check src tests
uv run pytest
```

Coverage:

```bash
uv run pytest --cov=src/llm_keywords_pipeline --cov-report=term-missing
```

Опційний локальний database demo:

```bash
cp .env.example .env
docker compose up
```

Compose піднімає MariaDB і Adminer на localhost. Це локальний demo, не production
deployment recipe.

---

## Документація

| Документ | Що всередині |
| --- | --- |
| [Architecture](docs/architecture.md) | Package map, workflow boundaries, stable vs legacy surface. |
| [Testing](docs/testing.md) | Test tiers, default commands, CI parity, data-required skips. |
| [Public Version](docs/public-version.md) | Що включено, що виключено і навіщо залишені prompts. |
| [Prompt Templates](prompts/README.md) | Prepare/produce/deliver LLM workflow templates. |

---

## Публічна межа

Репозиторій зберігає інженерну структуру, тести, fixtures і prompt workflow, але не
публікує приватні production datasets, generated reports, старі SERP TOP-10 exports і
external LLM orchestration. Частина утиліт і docs очікує оригінальний private data
layout і залишена, щоб показати реальну архітектуру проєкту.

---

## Ліцензія

MIT. Див. [LICENSE](LICENSE).

---

Сирий список ключів легко експортувати. Цей проєкт перетворює його на кластеризовану
SEO-роботу, яку можна написати, перевірити й покращити.
