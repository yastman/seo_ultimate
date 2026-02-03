# Category Sync & Deploy — Design Document

**Дата:** 2026-02-02
**Статус:** Ready

---

## 1. Цели

1. Синхронизировать RU ↔ UK категории (закрыть пробелы)
2. Сгенерировать недостающий контент
3. Получить полный маппинг slug → OpenCart category_id из продакшн БД
4. Задеплоить всё на продакшн

---

## 1.1 Workflow (кто что делает)

### RU Workflow (полный цикл)

```
┌─────────────────────────────────────────────────────────────────┐
│  RESEARCH PHASE (RU)                                            │
├─────────────────────────────────────────────────────────────────┤
│  Claude: /seo-research {slug}                                   │
│      ↓                                                          │
│  Output: categories/{slug}/research/RESEARCH_PROMPT.md          │
│      ↓                                                          │
│  ⏸️ User: Загрузить в Perplexity Deep Research                  │
│      ↓                                                          │
│  ⏸️ User: Заполнить RESEARCH_DATA.md результатами               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  CONTENT PHASE (RU)                                             │
├─────────────────────────────────────────────────────────────────┤
│  Claude: /content-generator {slug}                              │
│      ↓                                                          │
│  Input: keys + RESEARCH_DATA.md + meta                          │
│      ↓                                                          │
│  Output: categories/{slug}/content/{slug}_ru.md                 │
└─────────────────────────────────────────────────────────────────┘
```

### UK Workflow (использует RU research)

```
┌─────────────────────────────────────────────────────────────────┐
│  UK INIT (если категории нет)                                   │
├─────────────────────────────────────────────────────────────────┤
│  Claude: /uk-content-init {slug}                                │
│      ↓                                                          │
│  Output: uk/categories/{slug}/ (структура + ключи из RU)        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  UK CONTENT (используем RU research!)                           │
├─────────────────────────────────────────────────────────────────┤
│  Claude: /uk-content-generator {slug}                           │
│      ↓                                                          │
│  Input: UK keys + UK meta + **RU RESEARCH_DATA.md**             │
│      ↓                                                          │
│  Output: uk/categories/{slug}/content/{slug}_uk.md              │
└─────────────────────────────────────────────────────────────────┘
```

**Важно:** UK НЕ требует отдельного research — используется RU research как справка.

**Легенда:**
- ⏸️ = точка ожидания пользователя (Claude не может продолжить без данных)

---

## 2. Текущее состояние

### 2.1 Покрытие мета/контент

| Язык | Категорий | Мета | Контент | Без контента |
|------|-----------|------|---------|--------------|
| RU | 53 | 53 ✓ | 50 | 3 |
| UK | 53 | 53 ✓ | 52 | 1 |

### 2.2 Категории без контента

| Категория | RU | UK | Keys | Research | Meta | Примечание |
|-----------|----|----|------|----------|------|------------|
| `polirovalnye-krugi` | ✗ нет | ✗ удалена | ✓ | ✓ 24KB | ✓ | Важная L2, ВЧ "круг для полировки авто" (720) |
| `polirovalnye-mashinki` | ✗ нет | ✓ есть | ✓ | ✓ 22KB | ✓ | Важная L2, ВЧ "полировочная машинка" (8100!) |
| `glavnaya` | ✗ нет | ✗ нет | ? | ✗ нет | ? | Главная страница — **нужен контент** |

### 2.3 OpenCart ID маппинг

- **В маппинге:** 32 slug'а (`data/category_ids.json`)
- **Без ID:** 12 slug'ов (aksessuary, avtoshampuni, glavnaya, malyarniy-skotch, mikrofibra-i-tryapki, moyka-i-eksterer, nabory, ochistiteli-dvigatelya, opt-i-b2b, pyatnovyvoditeli, vedra-i-emkosti, aksessuary-dlya-naneseniya-sredstv)

### 2.4 Данные

| Файл | Описание |
|------|----------|
| `data/ru_semantics_master.csv` | RU мастер-файл ключей |
| `uk/data/uk_keywords_source.csv` | UK ключи с частотностью (355) |
| `data/category_ids.json` | slug → OpenCart ID (частичный) |

---

## 3. План работ

### Phase 0: Подготовка `glavnaya`

**Проблема:** У `glavnaya` нет research — нужно сначала подготовить.

| # | Действие | Кто | Скилл/Инструмент |
|---|----------|-----|------------------|
| 0.1 | Проверить/создать keys | Claude | `/category-init glavnaya` |
| 0.2 | Создать RESEARCH_PROMPT.md | Claude | `/seo-research glavnaya` |
| 0.3 | ⏸️ **Исследование в Perplexity** | **User** | Perplexity Deep Research |
| 0.4 | Заполнить RESEARCH_DATA.md | **User** | Ручной ввод |
| 0.5 | Создать meta | Claude | `/generate-meta glavnaya` |

> ⏸️ = точка ожидания пользователя

### Phase 1: Генерация контента RU

**Задачи:**

| # | Категория | Скилл | Входные данные |
|---|-----------|-------|----------------|
| 1.1 | `polirovalnye-krugi` | `/content-generator` | keys ✓, research ✓, meta ✓ |
| 1.2 | `polirovalnye-mashinki` | `/content-generator` | keys ✓, research ✓, meta ✓ |
| 1.3 | `glavnaya` | `/content-generator` | После Phase 0 |

**Выход:** `categories/{slug}/content/{slug}_ru.md`

### Phase 2: Восстановление UK `polirovalnye-krugi`

**Задачи:**

| # | Действие | Скилл/Команда |
|---|----------|---------------|
| 2.1 | Восстановить категорию из git | `git show f6b198d^:uk/categories/polirovalnye-krugi/...` |
| 2.2 | Или создать заново | `/uk-content-init polirovalnye-krugi` |

**Данные в git (коммит f6b198d^):**
- `uk/categories/polirovalnye-krugi/data/polirovalnye-krugi_clean.json`
- `uk/categories/polirovalnye-krugi/meta/polirovalnye-krugi_meta.json`

### Phase 3: Генерация контента UK

> **Важно:** UK использует **RU research** — отдельный research не нужен!

**Задачи:**

| # | Категория | Скилл | Input |
|---|-----------|-------|-------|
| 3.1 | `polirovalnye-krugi` | `/uk-content-generator` | UK keys + UK meta + **RU** RESEARCH_DATA.md |
| 3.2 | `glavnaya` | `/uk-content-generator` | После Phase 0+1 |

**Выход:** `uk/categories/{slug}/content/{slug}_uk.md`

### Phase 4: Маппинг slug → OpenCart ID

**Задачи:**

| # | Действие | Команда |
|---|----------|---------|
| 4.1 | Подключиться к продакшн | `ult` (SSH alias) |
| 4.2 | Выгрузить все категории | SQL query |
| 4.3 | Обновить `data/category_ids.json` | — |

**SQL для выгрузки:**
```sql
SELECT
    c.category_id,
    cd.name,
    u.keyword as slug
FROM oc_category c
JOIN oc_category_description cd ON c.category_id = cd.category_id AND cd.language_id = 3
LEFT JOIN oc_seo_url u ON u.query = CONCAT('category_id=', c.category_id) AND u.language_id = 3
WHERE c.status = 1
ORDER BY c.category_id;
```

### Phase 5: Quality Gate

**Задачи:**

| # | Категория | Скилл |
|---|-----------|-------|
| 5.1 | `polirovalnye-krugi` (RU) | `/quality-gate` |
| 5.2 | `polirovalnye-krugi` (UK) | `/uk-quality-gate` |
| 5.3 | `polirovalnye-mashinki` (RU) | `/quality-gate` |

### Phase 6: Deploy

**Задачи:**

| # | Категория | Скилл | language_id |
|---|-----------|-------|-------------|
| 6.1 | `polirovalnye-krugi` (RU) | `/deploy-to-opencart` | 3 |
| 6.2 | `polirovalnye-krugi` (UK) | `/uk-deploy` | 1 |
| 6.3 | `polirovalnye-mashinki` (RU) | `/deploy-to-opencart` | 3 |

---

## 4. Скиллы

### RU Pipeline

| Скилл | Input | Output | Кто |
|-------|-------|--------|-----|
| `/category-init {slug}` | — | Структура папок + _clean.json скелет | Claude |
| `/seo-research {slug}` | _clean.json | RESEARCH_PROMPT.md | Claude |
| ⏸️ Perplexity Research | RESEARCH_PROMPT.md | RESEARCH_DATA.md | **User** |
| `/generate-meta {slug}` | _clean.json | _meta.json | Claude |
| `/content-generator {slug}` | keys + research + meta | {slug}_ru.md | Claude |
| `/quality-gate {slug}` | Все файлы | QUALITY_REPORT.md | Claude |
| `/deploy-to-opencart {slug}` | meta + content | SQL в БД | Claude |

### UK Pipeline

| Скилл | Input | Output | Кто |
|-------|-------|--------|-----|
| `/uk-content-init {slug}` | RU _clean.json | UK структура + UK _clean.json | Claude |
| `/uk-generate-meta {slug}` | UK _clean.json | UK _meta.json | Claude |
| `/uk-content-generator {slug}` | UK keys + UK meta + **RU** research | {slug}_uk.md | Claude |
| `/uk-quality-gate {slug}` | Все UK файлы | QUALITY_REPORT.md | Claude |
| `/uk-deploy {slug}` | UK meta + content | SQL в БД (language_id=1) | Claude |

> ⏸️ = точка ожидания пользователя

---

## 5. Зависимости

```
Phase 0 (glavnaya prep) ──→ Phase 1.3 (glavnaya content)

Phase 1 (RU content) ──┬──→ Phase 5 (QA) ──→ Phase 6 (Deploy) ──→ Phase 7 (Товары)
                       │
Phase 2 (UK restore) ──┴──→ Phase 3 (UK content) ──→ Phase 5 ──→ Phase 6

Phase 4 (DB mapping) ──→ Phase 6 (нужен category_id для SQL)
                     ──→ Phase 7 (нужен маппинг для товаров)
```

---

## 6. Риски

| Риск | Митигация |
|------|-----------|
| UK polirovalnye-krugi не восстановится из git | Использовать `/uk-content-init` для создания с нуля |
| Нет category_id для новых категорий | Вытянуть из продакшн БД через `ult` |
| Продакшн БД недоступна | Проверить SSH connection: `ult 'echo ok'` |

---

## 7. Решения

| Вопрос | Решение |
|--------|---------|
| `glavnaya` — нужен контент? | **ДА** — добавить в Phase 1 |
| Новые категории в БД | **СОЗДАВАТЬ** — если нет в OpenCart |
| Распределение товаров | **КРИТИЧНО** — после создания категорий перенести товары |

---

## 8. Phase 7: Распределение товаров

**Задача:** После создания новых категорий в БД — правильно распределить товары.

### Подход:

1. Выгрузить текущую привязку товаров к категориям
2. Определить правила маппинга (по названию/SKU/атрибутам)
3. Сформировать SQL для перепривязки
4. Применить на продакшн

### SQL для анализа:

```sql
-- Товары в категории
SELECT p.product_id, pd.name, p.sku
FROM oc_product p
JOIN oc_product_description pd ON p.product_id = pd.product_id AND pd.language_id = 3
JOIN oc_product_to_category pc ON p.product_id = pc.product_id
WHERE pc.category_id = {OLD_CATEGORY_ID};

-- Перепривязка товара к новой категории
INSERT INTO oc_product_to_category (product_id, category_id)
SELECT product_id, {NEW_CATEGORY_ID}
FROM oc_product_to_category
WHERE category_id = {OLD_CATEGORY_ID};
```

### Риски:

- Товар может быть в нескольких категориях — не удалять старые привязки без анализа
- Нужен бэкап перед изменениями

---

## 9. Acceptance Criteria

- [ ] `glavnaya` RU: research создан, контент сгенерирован
- [ ] `glavnaya` UK: контент сгенерирован
- [ ] `polirovalnye-krugi` RU: контент сгенерирован, quality-gate PASS
- [ ] `polirovalnye-krugi` UK: категория восстановлена, контент сгенерирован, quality-gate PASS
- [ ] `polirovalnye-mashinki` RU: контент сгенерирован, quality-gate PASS
- [ ] `data/category_ids.json` обновлён полным маппингом из БД
- [ ] Новые категории созданы в OpenCart (если нужно)
- [ ] Товары правильно распределены по категориям
- [ ] Все категории задеплоены на продакшн

---

## Appendix A: Git Recovery Commands

```bash
# Просмотр удалённых файлов UK polirovalnye-krugi
git show f6b198d^:uk/categories/polirovalnye-krugi/data/polirovalnye-krugi_clean.json
git show f6b198d^:uk/categories/polirovalnye-krugi/meta/polirovalnye-krugi_meta.json

# Восстановление
git checkout f6b198d^ -- uk/categories/polirovalnye-krugi/
```

## Appendix B: SSH Connection

```bash
# Alias
ult  # → ssh -i ~/.ssh/server_key_new -p 41229 admin@193.169.188.9

# Test
ult 'echo Connected!'

# DB query
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "SELECT COUNT(*) FROM oc_category;"'
```
