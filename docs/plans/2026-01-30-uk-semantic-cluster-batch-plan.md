# UK Semantic Cluster Batch Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Применить `/semantic-cluster` ко всем 53 UK категориям для разделения keywords vs synonyms

**Architecture:** 4 параллельных воркера обрабатывают по ~13 категорий каждый. Каждый воркер вызывает executing-plans один раз, затем последовательно обрабатывает все категории из своего Task, валидирует и пишет лог. Оркестратор проверяет логи и коммитит.

**Tech Stack:** `/semantic-cluster` skill, spawn-claude, tmux

**Design:** [2026-01-30-uk-semantic-cluster-batch-design.md](2026-01-30-uk-semantic-cluster-batch-design.md)

---

## Task 1: W1 — akkumulyatornaya → gubki-i-varezhki (13 категорій)

**Files:**
- Modify: `uk/categories/{slug}/data/{slug}_clean.json` для 13 категорий
- Create: `data/generated/audit-logs/W1_uk_cluster_log.md`

**Категории для обработки:**

| # | slug | файл |
|---|------|------|
| 1 | akkumulyatornaya | `uk/categories/akkumulyatornaya/data/akkumulyatornaya_clean.json` |
| 2 | aksessuary | `uk/categories/aksessuary/data/aksessuary_clean.json` |
| 3 | aksessuary-dlya-naneseniya-sredstv | `uk/categories/aksessuary-dlya-naneseniya-sredstv/data/aksessuary-dlya-naneseniya-sredstv_clean.json` |
| 4 | aktivnaya-pena | `uk/categories/aktivnaya-pena/data/aktivnaya-pena_clean.json` |
| 5 | antibitum | `uk/categories/antibitum/data/antibitum_clean.json` |
| 6 | antidozhd | `uk/categories/antidozhd/data/antidozhd_clean.json` |
| 7 | antimoshka | `uk/categories/antimoshka/data/antimoshka_clean.json` |
| 8 | apparaty-tornador | `uk/categories/apparaty-tornador/data/apparaty-tornador_clean.json` |
| 9 | avtoshampuni | `uk/categories/avtoshampuni/data/avtoshampuni_clean.json` |
| 10 | cherniteli-shin | `uk/categories/cherniteli-shin/data/cherniteli-shin_clean.json` |
| 11 | glavnaya | `uk/categories/glavnaya/data/glavnaya_clean.json` |
| 12 | glina-i-avtoskraby | `uk/categories/glina-i-avtoskraby/data/glina-i-avtoskraby_clean.json` |
| 13 | gubki-i-varezhki | `uk/categories/gubki-i-varezhki/data/gubki-i-varezhki_clean.json` |

**Workflow:**

1. Для каждого slug по порядку вызвать `/semantic-cluster {slug}`
2. После всех — валидация:
   ```bash
   for slug in akkumulyatornaya aksessuary aksessuary-dlya-naneseniya-sredstv aktivnaya-pena antibitum antidozhd antimoshka apparaty-tornador avtoshampuni cherniteli-shin glavnaya glina-i-avtoskraby gubki-i-varezhki; do
     python3 -c "import json; d=json.load(open('uk/categories/$slug/data/${slug}_clean.json')); print(f'$slug: {len(d.get(\"keywords\",[]))} kw, {len(d.get(\"synonyms\",[]))} syn')"
   done
   ```
3. Записать лог `data/generated/audit-logs/W1_uk_cluster_log.md`

**Формат лога:**

```markdown
# W1 UK Semantic Cluster Log

## akkumulyatornaya
- keywords: X → Y
- synonyms: 0 → Z (lsi: A, meta_only: B)

## aksessuary
...

---

**Итого:** 13 категорій, X keywords → Y keywords, Z нових synonyms
```

---

## Task 2: W2 — keramika-dlya-diskov → ochistiteli-diskov (13 категорій)

**Files:**
- Modify: `uk/categories/{slug}/data/{slug}_clean.json` для 13 категорий
- Create: `data/generated/audit-logs/W2_uk_cluster_log.md`

**Категории для обработки:**

| # | slug | файл |
|---|------|------|
| 1 | keramika-dlya-diskov | `uk/categories/keramika-dlya-diskov/data/keramika-dlya-diskov_clean.json` |
| 2 | keramika-i-zhidkoe-steklo | `uk/categories/keramika-i-zhidkoe-steklo/data/keramika-i-zhidkoe-steklo_clean.json` |
| 3 | kisti-dlya-deteylinga | `uk/categories/kisti-dlya-deteylinga/data/kisti-dlya-deteylinga_clean.json` |
| 4 | kvik-deteylery | `uk/categories/kvik-deteylery/data/kvik-deteylery_clean.json` |
| 5 | malyarniy-skotch | `uk/categories/malyarniy-skotch/data/malyarniy-skotch_clean.json` |
| 6 | mekhovye | `uk/categories/mekhovye/data/mekhovye_clean.json` |
| 7 | mikrofibra-i-tryapki | `uk/categories/mikrofibra-i-tryapki/data/mikrofibra-i-tryapki_clean.json` |
| 8 | moyka-i-eksterer | `uk/categories/moyka-i-eksterer/data/moyka-i-eksterer_clean.json` |
| 9 | nabory | `uk/categories/nabory/data/nabory_clean.json` |
| 10 | neytralizatory-zapakha | `uk/categories/neytralizatory-zapakha/data/neytralizatory-zapakha_clean.json` |
| 11 | obezzhirivateli | `uk/categories/obezzhirivateli/data/obezzhirivateli_clean.json` |
| 12 | oborudovanie | `uk/categories/oborudovanie/data/oborudovanie_clean.json` |
| 13 | ochistiteli-diskov | `uk/categories/ochistiteli-diskov/data/ochistiteli-diskov_clean.json` |

**Workflow:**

1. Для каждого slug по порядку вызвать `/semantic-cluster {slug}`
2. После всех — валидация:
   ```bash
   for slug in keramika-dlya-diskov keramika-i-zhidkoe-steklo kisti-dlya-deteylinga kvik-deteylery malyarniy-skotch mekhovye mikrofibra-i-tryapki moyka-i-eksterer nabory neytralizatory-zapakha obezzhirivateli oborudovanie ochistiteli-diskov; do
     python3 -c "import json; d=json.load(open('uk/categories/$slug/data/${slug}_clean.json')); print(f'$slug: {len(d.get(\"keywords\",[]))} kw, {len(d.get(\"synonyms\",[]))} syn')"
   done
   ```
3. Записать лог `data/generated/audit-logs/W2_uk_cluster_log.md`

---

## Task 3: W3 — ochistiteli-dvigatelya → pyatnovyvoditeli (13 категорій)

**Files:**
- Modify: `uk/categories/{slug}/data/{slug}_clean.json` для 13 категорий
- Create: `data/generated/audit-logs/W3_uk_cluster_log.md`

**Категории для обработки:**

| # | slug | файл |
|---|------|------|
| 1 | ochistiteli-dvigatelya | `uk/categories/ochistiteli-dvigatelya/data/ochistiteli-dvigatelya_clean.json` |
| 2 | ochistiteli-kozhi | `uk/categories/ochistiteli-kozhi/data/ochistiteli-kozhi_clean.json` |
| 3 | ochistiteli-kuzova | `uk/categories/ochistiteli-kuzova/data/ochistiteli-kuzova_clean.json` |
| 4 | ochistiteli-shin | `uk/categories/ochistiteli-shin/data/ochistiteli-shin_clean.json` |
| 5 | ochistiteli-stekol | `uk/categories/ochistiteli-stekol/data/ochistiteli-stekol_clean.json` |
| 6 | omyvatel | `uk/categories/omyvatel/data/omyvatel_clean.json` |
| 7 | opt-i-b2b | `uk/categories/opt-i-b2b/data/opt-i-b2b_clean.json` |
| 8 | polirol-dlya-stekla | `uk/categories/polirol-dlya-stekla/data/polirol-dlya-stekla_clean.json` |
| 9 | poliroli-dlya-plastika | `uk/categories/poliroli-dlya-plastika/data/poliroli-dlya-plastika_clean.json` |
| 10 | polirovalnye-mashinki | `uk/categories/polirovalnye-mashinki/data/polirovalnye-mashinki_clean.json` |
| 11 | polirovalnye-pasty | `uk/categories/polirovalnye-pasty/data/polirovalnye-pasty_clean.json` |
| 12 | polirovka | `uk/categories/polirovka/data/polirovka_clean.json` |
| 13 | pyatnovyvoditeli | `uk/categories/pyatnovyvoditeli/data/pyatnovyvoditeli_clean.json` |

**Workflow:**

1. Для каждого slug по порядку вызвать `/semantic-cluster {slug}`
2. После всех — валидация:
   ```bash
   for slug in ochistiteli-dvigatelya ochistiteli-kozhi ochistiteli-kuzova ochistiteli-shin ochistiteli-stekol omyvatel opt-i-b2b polirol-dlya-stekla poliroli-dlya-plastika polirovalnye-mashinki polirovalnye-pasty polirovka pyatnovyvoditeli; do
     python3 -c "import json; d=json.load(open('uk/categories/$slug/data/${slug}_clean.json')); print(f'$slug: {len(d.get(\"keywords\",[]))} kw, {len(d.get(\"synonyms\",[]))} syn')"
   done
   ```
3. Записать лог `data/generated/audit-logs/W3_uk_cluster_log.md`

---

## Task 4: W4 — raspyliteli-i-penniki → zhidkiy-vosk (14 категорій)

**Files:**
- Modify: `uk/categories/{slug}/data/{slug}_clean.json` для 14 категорий
- Create: `data/generated/audit-logs/W4_uk_cluster_log.md`

**Категории для обработки:**

| # | slug | файл |
|---|------|------|
| 1 | raspyliteli-i-penniki | `uk/categories/raspyliteli-i-penniki/data/raspyliteli-i-penniki_clean.json` |
| 2 | shampuni-dlya-ruchnoy-moyki | `uk/categories/shampuni-dlya-ruchnoy-moyki/data/shampuni-dlya-ruchnoy-moyki_clean.json` |
| 3 | shchetka-dlya-moyki-avto | `uk/categories/shchetka-dlya-moyki-avto/data/shchetka-dlya-moyki-avto_clean.json` |
| 4 | silanty | `uk/categories/silanty/data/silanty_clean.json` |
| 5 | sredstva-dlya-khimchistki-salona | `uk/categories/sredstva-dlya-khimchistki-salona/data/sredstva-dlya-khimchistki-salona_clean.json` |
| 6 | sredstva-dlya-kozhi | `uk/categories/sredstva-dlya-kozhi/data/sredstva-dlya-kozhi_clean.json` |
| 7 | tverdyy-vosk | `uk/categories/tverdyy-vosk/data/tverdyy-vosk_clean.json` |
| 8 | ukhod-za-intererom | `uk/categories/ukhod-za-intererom/data/ukhod-za-intererom_clean.json` |
| 9 | ukhod-za-kozhey | `uk/categories/ukhod-za-kozhey/data/ukhod-za-kozhey_clean.json` |
| 10 | ukhod-za-naruzhnym-plastikom | `uk/categories/ukhod-za-naruzhnym-plastikom/data/ukhod-za-naruzhnym-plastikom_clean.json` |
| 11 | vedra-i-emkosti | `uk/categories/vedra-i-emkosti/data/vedra-i-emkosti_clean.json` |
| 12 | voski | `uk/categories/voski/data/voski_clean.json` |
| 13 | zashchitnye-pokrytiya | `uk/categories/zashchitnye-pokrytiya/data/zashchitnye-pokrytiya_clean.json` |
| 14 | zhidkiy-vosk | `uk/categories/zhidkiy-vosk/data/zhidkiy-vosk_clean.json` |

**Workflow:**

1. Для каждого slug по порядку вызвать `/semantic-cluster {slug}`
2. После всех — валидация:
   ```bash
   for slug in raspyliteli-i-penniki shampuni-dlya-ruchnoy-moyki shchetka-dlya-moyki-avto silanty sredstva-dlya-khimchistki-salona sredstva-dlya-kozhi tverdyy-vosk ukhod-za-intererom ukhod-za-kozhey ukhod-za-naruzhnym-plastikom vedra-i-emkosti voski zashchitnye-pokrytiya zhidkiy-vosk; do
     python3 -c "import json; d=json.load(open('uk/categories/$slug/data/${slug}_clean.json')); print(f'$slug: {len(d.get(\"keywords\",[]))} kw, {len(d.get(\"synonyms\",[]))} syn')"
   done
   ```
3. Записать лог `data/generated/audit-logs/W4_uk_cluster_log.md`

---

## Task 5: Оркестратор — Финальная валидация и коммит

**После завершения W1-W4**

**Step 1: Проверить логи воркеров**

```bash
ls -la data/generated/audit-logs/W*_uk_cluster_log.md
cat data/generated/audit-logs/W*_uk_cluster_log.md
```

Expected: 4 лога с информацией о 53 категориях.

**Step 2: Валидировать JSON синтаксис**

```bash
for f in uk/categories/*/data/*_clean.json; do
  python3 -c "import json; json.load(open('$f'))" || echo "FAIL: $f"
done
```

Expected: Нет ошибок.

**Step 3: Проверить synonyms заполнены**

```bash
python3 -c "
import json
from pathlib import Path
empty = []
for f in Path('uk/categories').glob('*/data/*_clean.json'):
    d = json.load(open(f))
    if not d.get('synonyms'):
        empty.append(f.parent.parent.name)
if empty:
    print(f'WARN: {len(empty)} categories with empty synonyms: {empty}')
else:
    print('OK: All 53 categories have synonyms')
"
```

**Step 4: Коммит**

```bash
git add uk/categories/ data/generated/audit-logs/
git commit -m "$(cat <<'EOF'
feat(uk): semantic cluster for 53 UK categories

- Deduplicate keywords vs synonyms
- Add variant_of for word forms (авто/автомобіля/машини)
- Move commercial modifiers to meta_only (купити, ціна, відгуки)

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
EOF
)"
```

---

## Запуск воркеров

```bash
# W1
spawn-claude "W1: UK semantic cluster akkumulyatornaya → gubki-i-varezhki.

/superpowers:executing-plans docs/plans/2026-01-30-uk-semantic-cluster-batch-plan.md

Выполни ТОЛЬКО Task 1.

НЕ ДЕЛАЙ git commit" "$(pwd)"

# W2
spawn-claude "W2: UK semantic cluster keramika-dlya-diskov → ochistiteli-diskov.

/superpowers:executing-plans docs/plans/2026-01-30-uk-semantic-cluster-batch-plan.md

Выполни ТОЛЬКО Task 2.

НЕ ДЕЛАЙ git commit" "$(pwd)"

# W3
spawn-claude "W3: UK semantic cluster ochistiteli-dvigatelya → pyatnovyvoditeli.

/superpowers:executing-plans docs/plans/2026-01-30-uk-semantic-cluster-batch-plan.md

Выполни ТОЛЬКО Task 3.

НЕ ДЕЛАЙ git commit" "$(pwd)"

# W4
spawn-claude "W4: UK semantic cluster raspyliteli-i-penniki → zhidkiy-vosk.

/superpowers:executing-plans docs/plans/2026-01-30-uk-semantic-cluster-batch-plan.md

Выполни ТОЛЬКО Task 4.

НЕ ДЕЛАЙ git commit" "$(pwd)"
```

---

**Version:** 3.0
