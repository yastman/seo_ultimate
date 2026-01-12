# План оптимизации `.claude/skills` (Ultimate.net.ua)

**Цель:** сделать skills воспроизводимыми, безопасными и синхронизированными с реальным пайплайном (`scripts/`, `docs/`, `deploy/`, структура данных категорий).
**Область:** только `.claude/skills/*` + минимальные точки интеграции (скрипты/доки), которые skills используют/упоминают.

---

## 0) Краткая инвентаризация (что есть сейчас)

Skills в `.claude/skills/`:
- `category-init`
- `generate-meta`
- `seo-research`
- `content-generator`
- `uk-content-init`
- `quality-gate`
- `deploy-to-opencart`
- `skill-creator` (системный, не проектный)

---

## 1) Ключевые проблемы (по приоритету)

### 1.1 Дрифт схемы `_clean.json` ломает skills “в лоб”

В skills встречаются *разные ожидания* по формату `categories/{slug}/data/{slug}_clean.json`:
- `category-init` и `quality-gate` описывают схему `keywords: { primary/secondary/supporting/commercial }`
- `generate-meta` оперирует `keywords[0]` (как будто это list)
- `uk-content-init` задаёт UK-формат `keywords: {…}` и добавляет `keyword_ru`

**Следствие:** при одинаковом “вызове” skills разные шаги могут быть несовместимы между собой и со скриптами.

### 1.2 Секреты и “боевые” доступы попали в skill-тексты

`deploy-to-opencart` содержит:
- root-пароль БД (встроен прямо в команды `mysql -p...`)
- IP/SSH параметры (host/user/порт и путь к ключу)

**Следствие:** риск утечки, риск случайного деплоя не туда, невозможность безопасно шарить репозиторий.

### 1.3 Несостыковка ID/маппинга категорий между skill/скриптами/SQL

- `deploy/*.sql` для `antimoshka` и `antibitum` используют `category_id=474/475`
- `scripts/upload_to_db.py` содержит устаревший маппинг для тех же слагов (другие ID)
- `seo-research` skill предлагает получать `category_id` из `scripts/upload_to_db.py` и `deploy/{slug}.sql`, но при расхождении это даёт неверный результат

**Следствие:** research может собираться “не для той категории”, а deploy/update — писать “не туда”.

### 1.4 Сломанные/неполные ссылки внутри skills

`deploy-to-opencart` ссылается на `DB_REFERENCE.md`, которого нет в `.claude/skills/deploy-to-opencart/`.

### 1.5 Разнобой в “источниках правды” и версиях

- Skills частично ссылаются на устаревшие версии гайдов или просто не синхронизированы с текущими `docs/`.
- `.claude/README.md` перечисляет набор skills, который не совпадает с фактической папкой `.claude/skills/`.

---

## 2) Целевое состояние (Definition of Done)

- **Одна каноническая схема `_clean.json`**, а если миграция постепенная — единый адаптер чтения (skills и скрипты используют “нормализованный интерфейс”, а не руками парсят JSON).
- **Ноль секретов** в `.claude/skills/**` (и в командах “как деплоить”).
- **Единый SSOT для `category_id`** (файл-реестр или генерация из DB/SQL), и skills всегда берут IDs из него.
- **Каждый skill** имеет:
  - чёткие `Inputs/Outputs`
  - `Prerequisites`
  - однозначные команды/скрипты (или явно “ручные шаги”)
  - чеклист PASS-критериев (что считается сделанным)
- **Автопроверка skills** (линк‑чек, запрет секретов, наличие файлов, корректность путей).

---

## 3) План работ (итерациями)

### Итерация A — “Безопасность + SSOT” (1–2 дня)

1. **Убрать секреты из skills**
   - `deploy-to-opencart`: заменить всё на env‑переменные и нейтральные примеры:
     - `OPENCART_SSH_HOST`, `OPENCART_SSH_PORT`, `OPENCART_DB_NAME`, `OPENCART_DB_USER`, `OPENCART_DB_PASSWORD`
   - Везде, где фигурируют пароли/ключи/хосты — оставить только placeholders и ссылку на `docs/DB_GUIDE.md`.

2. **Ввести SSOT-реестр category_id**
   - Новый файл, например `data/category_ids.json`:
     - `{ "slug": { "category_id": 123, "notes": "...", "source": "db|deploy|manual" } }`
   - Обновить `deploy-to-opencart`/`seo-research` skill: получать `category_id` только из реестра (а не из `scripts/upload_to_db.py`).
   - Отдельно: описать “как обновлять реестр” (из БД запросом или парсингом `deploy/*.sql`).

3. **Починить битые ссылки**
   - Заменить `DB_REFERENCE.md` на реальный документ (`docs/DB_GUIDE.md`) или добавить отсутствующий файл.

**Критерии итерации A:**
- `rg -n "(mysql\\s+-u\\s+root\\s+-p\\S+|admin@\\d+\\.\\d+\\.\\d+\\.\\d+|OPENCART_.*PASSWORD)" .claude/skills` → пусто.
- `deploy-to-opencart` и `seo-research` не предлагают брать `category_id` из устаревших мест.

---

### Итерация B — “Схема `_clean.json` и совместимость” (2–4 дня)

1. **Выбрать канон схемы**
   - Рекомендуемый канон: `keywords: {primary/secondary/supporting/commercial}` как более управляемый для пайплайна (coverage split, meta_only и т.п.).

2. **Сделать адаптер чтения**
   - В `scripts/seo_utils.py` (или отдельном модуле) добавить функции:
     - `load_clean_keywords(slug, lang) -> NormalizedKeywords`
     - `get_primary_keyword(normalized) -> str`
   - Skills переписать так, чтобы они говорили “используй primary keyword” вместо “keywords[0]”.

3. **Согласовать UK/RU**
   - Зафиксировать, что UK `_clean.json` содержит `keyword_ru` (traceability), а RU — может не содержать.
   - Описать в `uk-content-init`: как формируется `commercial` и `use_in: meta_only`.

**Критерии итерации B:**
- `category-init`, `generate-meta`, `quality-gate`, `uk-content-init` используют одинаковую терминологию (“primary keyword”, “commercial meta_only”).
- Skills не зависят от того, list это или dict в исходном JSON.

---

### Итерация C — “Привязка skills к реальным скриптам” (3–7 дней)

Цель: минимизировать “ручные” шаги и сделать каждый skill исполняемым через существующие инструменты.

1. **category-init**
   - Явно привязать к `scripts/setup_all.py` / `scripts/verify_structural_integrity.py`
   - Добавить шаг проверки, что `content/*_ru.md` не placeholder.

2. **generate-meta**
   - Зафиксировать один способ генерации (например, расширить `scripts/generate_all_meta.py` режимом `--slug`).
   - Встроить проверку `validate_meta.py` как обязательный шаг.

3. **seo-research**
   - Привязать к генератору промпта (либо существующий скрипт, либо новый минимальный `scripts/generate_research_prompt.py`).
   - Источник товаров: `data/generated/PRODUCTS_LIST.md` + `data/category_ids.json`.

4. **content-generator**
   - Явно описать: откуда берётся структура (content guide + research) и чем проверяется (`validate_content.py` + `check_h1_sync.py`).

5. **quality-gate**
   - Добавить явный чек “не placeholder” и “схема `_clean.json` валидна”.
   - Обязать RU/UK одинаково: `validate_meta.py`, `validate_content.py`, `validate_uk.py` (если UK присутствует).

6. **deploy-to-opencart**
   - Привязать генерацию SQL к `scripts/generate_sql.py` (а не ручной сборке).
   - Разделить “generate” и “apply” (apply только с явным флагом/подтверждением).

**Критерии итерации C:**
- В каждом skill есть блок “Команды” с реальными скриптами проекта.
- Выполнение skill не требует догадок о путях/файлах/ID.

---

### Итерация D — “Контроль качества skills” (1–2 дня)

1. **Автопроверка `.claude/skills`**
   - Скрипт `scripts/verify_skills.py`:
     - проверяет существование файлов, на которые ссылаются skills
     - запрещает секреты/хосты/пароли по regex‑правилам
     - проверяет единый формат frontmatter (name/description/version/updated)

2. **Обновить индекс**
   - Синхронизировать `.claude/README.md` с фактическим списком skills и их назначением.

**Критерии итерации D:**
- `python3 scripts/verify_skills.py` → PASS.
- `.claude/README.md` не врёт про состав skills.

---

## 4) Точечные рекомендации по каждому skill

### `category-init`
- Проблема: описывает dict‑схему как обязательную, но в данных часто list‑схема.
- Действие: переписать на “primary keyword + commercial meta_only” через адаптер + закрепить создание “каркаса” research/content/meta.

### `generate-meta`
- Проблема: опирается на `keywords[0]` и предполагает конкретную форму `_clean.json`.
- Действие: использовать `primary keyword` (из нормализованной схемы), классификацию Producer/Shop брать из фактов (товары/производитель), а не “на глаз”.

### `seo-research`
- Проблема: шаг получения `category_id` может давать неверные ID.
- Действие: брать ID из `data/category_ids.json`, генерировать `RESEARCH_PROMPT.md` и каркас `RESEARCH_DATA.md` в стандарте проекта.

### `content-generator`
- Проблема: сейчас это скорее “гайд”, чем исполняемый skill.
- Действие: добавить строгие входы/выходы (что читать, что писать, чем проверять), правило “без placeholder”.

### `uk-content-init`
- Проблема: частично дублирует возможности `scripts/uk_seed_from_ru.py`.
- Действие: сделать skill тонким wrapper’ом над `uk_seed_from_ru.py --write` + `validate_uk.py`.

### `quality-gate`
- Проблема: ожидает кластеризацию 10–15 ключей и dict‑схему, не проверяет placeholder.
- Действие: добавить check “контент не placeholder”, “схема валидна”, “H1 sync”.

### `deploy-to-opencart`
- Проблема: секреты в тексте, отсутствующий `DB_REFERENCE.md`, ручные шаги.
- Действие: убрать секреты, привязать к `generate_sql.py`, описать безопасный apply‑процесс (явный флаг, бэкап, dry-run).

---

## 5) Метрики успеха

- 0 секретов в `.claude/skills/**`.
- 100% ссылок в skills указывают на существующие файлы.
- 100% skills используют единый “язык” сущностей (primary/commercial/meta_only).
- Любой skill можно выполнить без ручного поиска ID/путей.
