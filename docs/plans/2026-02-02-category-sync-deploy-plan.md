# Category Sync & Deploy — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Синхронизировать RU ↔ UK категории, сгенерировать недостающий контент, получить маппинг из БД, задеплоить на продакшн.

**Architecture:** Используем существующие скиллы pipeline'а (/seo-research, /content-generator, /uk-content-init, /uk-content-generator, /deploy-to-opencart). UK контент использует RU research. Распределение товаров — отдельная фаза после деплоя категорий.

**Tech Stack:** Python скрипты, MySQL/MariaDB, SSH (alias `ult`), Perplexity Deep Research (ручной этап)

---

## Parallel Workers Distribution

```
/parallel docs/plans/2026-02-02-category-sync-deploy-plan.md
W1: Task 1.1, Task 1.2, Task 2.1, Task 2.2, Task 2.3, Task 3.1
W2: Task 1.3, Task 1.4
```

| Worker | Категория | Задачи | Файлы |
|--------|-----------|--------|-------|
| **W1** | polirovalnye-krugi | RU content + UK restore + UK content | `categories/polirovka/polirovalnye-krugi/`, `uk/categories/polirovalnye-krugi/` |
| **W2** | polirovalnye-mashinki | RU content only | `categories/polirovka/polirovalnye-mashinki/` |

> **Правило:** 1 воркер = 1 набор файлов (без пересечений)

**После завершения воркеров:**
1. Проверить логи: `cat data/generated/audit-logs/W*_log.md`
2. Валидировать: `python3 scripts/validate_content.py ...`
3. Оркестратор делает коммит

---

## Phase 1: RU контент (polirovalnye-krugi, polirovalnye-mashinki)

> Эти категории уже имеют keys, research, meta — нужен только контент.

### Task 1.1: Создать папку content для polirovalnye-krugi

**Files:**
- Create: `categories/polirovka/polirovalnye-krugi/content/`

**Step 1: Создать папку**

```bash
mkdir -p categories/polirovka/polirovalnye-krugi/content
```

**Step 2: Проверить**

```bash
ls -la categories/polirovka/polirovalnye-krugi/
```

Expected: папка `content/` существует

---

### Task 1.2: Сгенерировать RU контент для polirovalnye-krugi

**Files:**
- Read: `categories/polirovka/polirovalnye-krugi/data/polirovalnye-krugi_clean.json`
- Read: `categories/polirovka/polirovalnye-krugi/meta/polirovalnye-krugi_meta.json`
- Read: `categories/polirovka/polirovalnye-krugi/research/RESEARCH_DATA.md`
- Create: `categories/polirovka/polirovalnye-krugi/content/polirovalnye-krugi_ru.md`

**Step 1: Вызвать скилл**

```
/content-generator polirovalnye-krugi
```

**Step 2: Проверить выход**

```bash
ls -la categories/polirovka/polirovalnye-krugi/content/
wc -l categories/polirovka/polirovalnye-krugi/content/polirovalnye-krugi_ru.md
```

Expected: файл создан, 50+ строк

**Step 3: Валидация**

```bash
python3 scripts/validate_content.py categories/polirovka/polirovalnye-krugi/content/polirovalnye-krugi_ru.md "круг для полировки авто"
```

Expected: PASS или warnings (не BLOCKER)

---

### Task 1.3: Создать папку content для polirovalnye-mashinki

**Files:**
- Create: `categories/polirovka/polirovalnye-mashinki/content/`

**Step 1: Создать папку**

```bash
mkdir -p categories/polirovka/polirovalnye-mashinki/content
```

---

### Task 1.4: Сгенерировать RU контент для polirovalnye-mashinki

**Files:**
- Read: `categories/polirovka/polirovalnye-mashinki/data/polirovalnye-mashinki_clean.json`
- Read: `categories/polirovka/polirovalnye-mashinki/meta/polirovalnye-mashinki_meta.json`
- Read: `categories/polirovka/polirovalnye-mashinki/research/RESEARCH_DATA.md`
- Create: `categories/polirovka/polirovalnye-mashinki/content/polirovalnye-mashinki_ru.md`

**Step 1: Вызвать скилл**

```
/content-generator polirovalnye-mashinki
```

**Step 2: Валидация**

```bash
python3 scripts/validate_content.py categories/polirovka/polirovalnye-mashinki/content/polirovalnye-mashinki_ru.md "полировочная машинка"
```

Expected: PASS

---

### Task 1.5: Коммит Phase 1

**Step 1: Проверить статус**

```bash
git status
```

**Step 2: Коммит**

```bash
git add categories/polirovka/polirovalnye-krugi/content/
git add categories/polirovka/polirovalnye-mashinki/content/
git commit -m "feat(content): add RU content for polirovalnye-krugi, polirovalnye-mashinki"
```

---

## Phase 2: Восстановление UK polirovalnye-krugi

### Task 2.1: Восстановить UK категорию из git

**Files:**
- Restore: `uk/categories/polirovalnye-krugi/` (из коммита f6b198d^)

**Step 1: Проверить что есть в git**

```bash
git show f6b198d^:uk/categories/polirovalnye-krugi/data/polirovalnye-krugi_clean.json | head -20
```

Expected: JSON с keywords

**Step 2: Восстановить**

```bash
git checkout f6b198d^ -- uk/categories/polirovalnye-krugi/
```

**Step 3: Проверить**

```bash
ls -la uk/categories/polirovalnye-krugi/
```

Expected: папки data/, meta/ существуют

**Step 4: Если не сработало — создать через скилл**

```
/uk-content-init polirovalnye-krugi
```

---

### Task 2.2: Создать research папку для UK (ссылка на RU)

**Files:**
- Create: `uk/categories/polirovalnye-krugi/research/`

**Step 1: Создать папку**

```bash
mkdir -p uk/categories/polirovalnye-krugi/research
```

**Step 2: Создать симлинк или копию RU research**

```bash
# Вариант 1: Симлинк (рекомендуется)
ln -s ../../../../categories/polirovka/polirovalnye-krugi/research/RESEARCH_DATA.md uk/categories/polirovalnye-krugi/research/RESEARCH_DATA.md

# Вариант 2: Копия (если симлинки не работают)
cp categories/polirovka/polirovalnye-krugi/research/RESEARCH_DATA.md uk/categories/polirovalnye-krugi/research/
```

---

### Task 2.3: Коммит Phase 2

```bash
git add uk/categories/polirovalnye-krugi/
git commit -m "feat(uk): restore polirovalnye-krugi category from git history"
```

---

## Phase 3: UK контент

### Task 3.1: Сгенерировать UK контент для polirovalnye-krugi

**Files:**
- Read: `uk/categories/polirovalnye-krugi/data/polirovalnye-krugi_clean.json`
- Read: `uk/categories/polirovalnye-krugi/meta/polirovalnye-krugi_meta.json`
- Read: RU research (через симлинк)
- Create: `uk/categories/polirovalnye-krugi/content/polirovalnye-krugi_uk.md`

**Step 1: Создать папку content**

```bash
mkdir -p uk/categories/polirovalnye-krugi/content
```

**Step 2: Вызвать скилл**

```
/uk-content-generator polirovalnye-krugi
```

**Step 3: Валидация**

```bash
python3 scripts/validate_content.py uk/categories/polirovalnye-krugi/content/polirovalnye-krugi_uk.md "круги для полірування авто" --lang uk
```

---

### Task 3.2: Коммит Phase 3

```bash
git add uk/categories/polirovalnye-krugi/content/
git commit -m "feat(uk): add UK content for polirovalnye-krugi"
```

---

## Phase 4: Маппинг slug → OpenCart ID

### Task 4.1: Проверить SSH подключение

**Step 1: Тест соединения**

```bash
ult 'echo Connected!'
```

Expected: "Connected!"

---

### Task 4.2: Выгрузить категории из продакшн БД

**Step 1: Выполнить SQL запрос**

```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
SELECT
    c.category_id,
    cd.name,
    u.keyword as slug
FROM oc_category c
JOIN oc_category_description cd ON c.category_id = cd.category_id AND cd.language_id = 3
LEFT JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) AND u.language_id = 3
WHERE c.status = 1
ORDER BY c.category_id;
"'
```

**Step 2: Сохранить результат**

```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -N -e "
SELECT
    c.category_id,
    u.keyword as slug
FROM oc_category c
LEFT JOIN oc_seo_url u ON u.query = CONCAT(\"category_id=\", c.category_id) AND u.language_id = 3
WHERE c.status = 1 AND u.keyword IS NOT NULL
ORDER BY c.category_id;
"' > /tmp/category_mapping.txt
```

---

### Task 4.3: Обновить data/category_ids.json

**Files:**
- Modify: `data/category_ids.json`

**Step 1: Прочитать текущий маппинг и вывод из БД**

**Step 2: Добавить недостающие slug → ID**

**Step 3: Валидация JSON**

```bash
python3 -c "import json; json.load(open('data/category_ids.json'))"
```

Expected: No errors

---

### Task 4.4: Коммит Phase 4

```bash
git add data/category_ids.json
git commit -m "feat(data): update category_ids.json with full mapping from production DB"
```

---

## Phase 5: Quality Gate

### Task 5.1: Quality Gate для polirovalnye-krugi (RU)

**Step 1: Вызвать скилл**

```
/quality-gate polirovalnye-krugi
```

**Step 2: Проверить отчёт**

```bash
cat categories/polirovka/polirovalnye-krugi/QUALITY_REPORT.md
```

Expected: PASS (или исправить issues)

---

### Task 5.2: Quality Gate для polirovalnye-krugi (UK)

```
/uk-quality-gate polirovalnye-krugi
```

---

### Task 5.3: Quality Gate для polirovalnye-mashinki (RU)

```
/quality-gate polirovalnye-mashinki
```

---

## Phase 6: Deploy

### Task 6.1: Deploy polirovalnye-krugi RU

**Prerequisite:** Task 5.1 PASS

**Step 1: Вызвать скилл**

```
/deploy-to-opencart polirovalnye-krugi
```

**Step 2: Проверить в БД**

```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
SELECT category_id, LEFT(meta_title, 50), LENGTH(description)
FROM oc_category_description
WHERE category_id = 459 AND language_id = 3;
"'
```

Expected: meta_title обновлён, description > 1000 chars

---

### Task 6.2: Deploy polirovalnye-krugi UK

```
/uk-deploy polirovalnye-krugi
```

Проверка:

```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
SELECT category_id, LEFT(meta_title, 50), LENGTH(description)
FROM oc_category_description
WHERE category_id = 459 AND language_id = 1;
"'
```

---

### Task 6.3: Deploy polirovalnye-mashinki RU

```
/deploy-to-opencart polirovalnye-mashinki
```

---

## Phase 7: Распределение товаров (⏸️ отдельная сессия)

> Эта фаза требует анализа текущих привязок и решений по каждому товару.
> Рекомендуется выполнять в отдельной сессии после проверки деплоя.

### Task 7.1: Анализ текущих привязок

```bash
ult 'sudo mysql -u root -pfr1daYTw1st yastman_test -e "
SELECT pc.category_id, cd.name as category_name, COUNT(*) as products
FROM oc_product_to_category pc
JOIN oc_category_description cd ON pc.category_id = cd.category_id AND cd.language_id = 3
GROUP BY pc.category_id
ORDER BY products DESC
LIMIT 30;
"'
```

### Task 7.2: Определить правила перепривязки

⏸️ **Требует решения пользователя:**
- Какие товары из старых категорий переносить?
- Оставлять ли товар в нескольких категориях?
- Нужен ли бэкап перед изменениями?

---

## Phase 0: glavnaya (⏸️ требует Perplexity)

> Выполняется параллельно или после основных фаз.

### Task 0.1: Проверить/создать keys для glavnaya

**Step 1: Проверить существующие данные**

```bash
cat categories/glavnaya/data/glavnaya_clean.json
```

**Step 2: Если нет — создать через скилл**

```
/category-init glavnaya
```

---

### Task 0.2: Сгенерировать RESEARCH_PROMPT.md

```
/seo-research glavnaya
```

**Output:** `categories/glavnaya/research/RESEARCH_PROMPT.md`

---

### Task 0.3: ⏸️ Perplexity Research (USER)

**Действие пользователя:**
1. Открыть `categories/glavnaya/research/RESEARCH_PROMPT.md`
2. Загрузить в Perplexity Deep Research
3. Результаты записать в `categories/glavnaya/research/RESEARCH_DATA.md`

---

### Task 0.4: Сгенерировать meta

```
/generate-meta glavnaya
```

---

### Task 0.5: Сгенерировать RU контент

```
/content-generator glavnaya
```

---

### Task 0.6: Сгенерировать UK контент

```
/uk-content-generator glavnaya
```

---

## Checklist

- [ ] Phase 1: RU контент (polirovalnye-krugi, polirovalnye-mashinki)
- [ ] Phase 2: UK polirovalnye-krugi восстановлена
- [ ] Phase 3: UK контент
- [ ] Phase 4: Маппинг slug→ID обновлён
- [ ] Phase 5: Quality Gate PASS
- [ ] Phase 6: Deploy на продакшн
- [ ] Phase 7: Товары распределены
- [ ] Phase 0: glavnaya (после Perplexity)

---

**Estimated:**
- Phase 1-6: ~2-3 часа (автоматизировано)
- Phase 0: зависит от Perplexity research
- Phase 7: требует анализа и решений
