# UK New Keywords Distribution Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Распределить 224 новых UK ключа из `new_ukr_keys.md` по UK категориям с ручным review маппинга.

**Architecture:** Двухфазный процесс: (1) воркеры анализируют ключи и предлагают маппинг, оркестратор проверяет; (2) воркеры добавляют ключи в `_clean.json` файлы.

**Tech Stack:** Python 3, JSON, spawn-claude (parallel workers)

---

## Фаза 1: Анализ и маппинг

### Task 1: Подготовить данные (Оркестратор)

**Files:**
- Read: `new_ukr_keys.md`
- Read: `data/ru_semantics_master.csv` (референс маппинга)
- Create: `data/generated/uk_new_keys_cleaned.tsv`

**Step 1: Очистить от нулевой частотности**

```bash
python3 -c "
with open('new_ukr_keys.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

keywords = []
for line in lines:
    line = line.strip()
    if not line or 'Ключевое слово' in line:
        continue
    parts = line.split('\t')
    if len(parts) >= 2:
        kw = parts[0].strip()
        try:
            vol = int(parts[1].strip())
            if vol > 0:
                keywords.append(f'{kw}\t{vol}')
        except:
            pass

# Сортировка по volume desc
keywords.sort(key=lambda x: -int(x.split('\t')[1]))

with open('data/generated/uk_new_keys_cleaned.tsv', 'w', encoding='utf-8') as f:
    f.write('\n'.join(keywords))

print(f'Saved {len(keywords)} keywords')
"
```

**Step 2: Разделить ключи на 5 частей для воркеров**

```bash
python3 << 'EOF'
with open('data/generated/uk_new_keys_cleaned.tsv', 'r', encoding='utf-8') as f:
    lines = [l.strip() for l in f.readlines() if l.strip()]

# Разделить на 5 частей
chunk_size = len(lines) // 5 + 1
for i in range(5):
    start = i * chunk_size
    end = min((i + 1) * chunk_size, len(lines))
    chunk = lines[start:end]

    with open(f'data/generated/uk_keys_chunk_W{i+1}.tsv', 'w', encoding='utf-8') as f:
        f.write('\n'.join(chunk))

    print(f'W{i+1}: {len(chunk)} keywords (lines {start+1}-{end})')
EOF
```

---

### Task 2: W1 — Анализ ключей (часть 1)

**Worker:** W1
**Files:**
- Read: `data/generated/uk_keys_chunk_W1.tsv`
- Read: `data/ru_semantics_master.csv` (референс)
- Create: `data/generated/audit-logs/W1_uk_mapping_log.md`

**Инструкция для воркера:**

1. Читай свой chunk ключей из `data/generated/uk_keys_chunk_W1.tsv`
2. Для каждого ключа определи категорию по аналогии с RU:
   - Ищи похожие RU ключи в `data/ru_semantics_master.csv`
   - Используй ту же категорию что и у RU ключа
3. Запиши результат в лог `data/generated/audit-logs/W1_uk_mapping_log.md`:

```markdown
# W1: UK Keywords Mapping Log

**Chunk:** data/generated/uk_keys_chunk_W1.tsv
**Keywords:** N шт

---

## Маппинг

| UK ключ | Volume | Категория | Референс RU |
|---------|--------|-----------|-------------|
| рідке скло | 5400 | keramika-i-zhidkoe-steklo | жидкое стекло |
| омивач скла зимовий | 3600 | omyvatel | омыватель стекла |
| ... | ... | ... | ... |

---

## Сомнительные (требуют review оркестратора)

| UK ключ | Volume | Варианты категорій | Коментар |
|---------|--------|-------------------|----------|
| ... | ... | cat1 / cat2 | чому сумнів |

---

**Итого:** X mapped, Y сомнительных
```

**Категории UK (53 шт):**
```
akkumulyatornaya, aksessuary, aksessuary-dlya-naneseniya-sredstv,
aktivnaya-pena, antibitum, antidozhd, antimoshka, apparaty-tornador,
avtoshampuni, cherniteli-shin, glavnaya, glina-i-avtoskraby,
gubki-i-varezhki, keramika-dlya-diskov, keramika-i-zhidkoe-steklo,
kisti-dlya-deteylinga, kvik-deteylery, malyarniy-skotch, mekhovye,
mikrofibra-i-tryapki, moyka-i-eksterer, nabory, neytralizatory-zapakha,
obezzhirivateli, oborudovanie, ochistiteli-diskov, ochistiteli-dvigatelya,
ochistiteli-kozhi, ochistiteli-kuzova, ochistiteli-shin, ochistiteli-stekol,
omyvatel, opt-i-b2b, polirol-dlya-stekla, poliroli-dlya-plastika,
polirovalnye-mashinki, polirovalnye-pasty, polirovka, pyatnovyvoditeli,
raspyliteli-i-penniki, shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto,
silanty, sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi,
tverdyy-vosk, ukhod-za-intererom, ukhod-za-kozhey, ukhod-za-naruzhnym-plastikom,
vedra-i-emkosti, voski, zashchitnye-pokrytiya, zhidkiy-vosk
```

---

### Task 3: W2 — Анализ ключей (часть 2)

**Worker:** W2
**Files:**
- Read: `data/generated/uk_keys_chunk_W2.tsv`
- Read: `data/ru_semantics_master.csv`
- Create: `data/generated/audit-logs/W2_uk_mapping_log.md`

**Инструкция:** Аналогично Task 2, лог в `W2_uk_mapping_log.md`

---

### Task 4: W3 — Анализ ключей (часть 3)

**Worker:** W3
**Files:**
- Read: `data/generated/uk_keys_chunk_W3.tsv`
- Read: `data/ru_semantics_master.csv`
- Create: `data/generated/audit-logs/W3_uk_mapping_log.md`

**Инструкция:** Аналогично Task 2, лог в `W3_uk_mapping_log.md`

---

### Task 5: W4 — Анализ ключей (часть 4)

**Worker:** W4
**Files:**
- Read: `data/generated/uk_keys_chunk_W4.tsv`
- Read: `data/ru_semantics_master.csv`
- Create: `data/generated/audit-logs/W4_uk_mapping_log.md`

**Инструкция:** Аналогично Task 2, лог в `W4_uk_mapping_log.md`

---

### Task 6: W5 — Анализ ключей (часть 5)

**Worker:** W5
**Files:**
- Read: `data/generated/uk_keys_chunk_W5.tsv`
- Read: `data/ru_semantics_master.csv`
- Create: `data/generated/audit-logs/W5_uk_mapping_log.md`

**Инструкция:** Аналогично Task 2, лог в `W5_uk_mapping_log.md`

---

### Task 7: Review маппинга (Оркестратор)

**Files:**
- Read: `data/generated/audit-logs/W1_uk_mapping_log.md` ... `W5_uk_mapping_log.md`
- Create: `data/generated/uk_final_mapping.json`

**Step 1: Проверить логи воркеров**

```bash
ls data/generated/audit-logs/W*_uk_mapping_log.md
```

**Step 2: Прочитать и проверить каждый лог**

- Проверить секцию "Сомнительные" в каждом логе
- Решить правильную категорию для сомнительных ключей
- Если нужно — исправить в логе воркера

**Step 3: Собрать финальный маппинг**

```bash
python3 << 'EOF'
import json
import re

# Парсим markdown логи воркеров
mapping = {}  # category -> [{"keyword": ..., "volume": ...}]

for i in range(1, 6):
    filename = f'data/generated/audit-logs/W{i}_uk_mapping_log.md'
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Парсим таблицу маппинга
    # | UK ключ | Volume | Категория | Референс RU |
    for match in re.finditer(r'\| ([^|]+) \| (\d+) \| ([a-z-]+) \| [^|]+ \|', content):
        kw = match.group(1).strip()
        vol = int(match.group(2))
        cat = match.group(3).strip()

        if cat not in mapping:
            mapping[cat] = []
        mapping[cat].append({'keyword': kw, 'volume': vol})

with open('data/generated/uk_final_mapping.json', 'w', encoding='utf-8') as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)

total = sum(len(v) for v in mapping.values())
print(f'Final mapping: {total} keywords in {len(mapping)} categories')
for cat, kws in sorted(mapping.items(), key=lambda x: -len(x[1]))[:10]:
    print(f'  {cat}: {len(kws)} keywords')
EOF
```

---

## Фаза 2: Распределение ключей

### Task 8: Разделить маппинг по воркерам (Оркестратор)

**Files:**
- Read: `data/generated/uk_final_mapping.json`
- Create: `data/generated/uk_apply_W1.json` ... `uk_apply_W5.json`

**Распределение категорий:**

```python
W1_CATS = ['aktivnaya-pena', 'avtoshampuni', 'shampuni-dlya-ruchnoy-moyki',
           'omyvatel', 'antimoshka', 'antidozhd', 'ochistiteli-stekol',
           'ochistiteli-kuzova', 'antibitum', 'raspyliteli-i-penniki', 'vedra-i-emkosti']

W2_CATS = ['polirovka', 'polirovalnye-pasty', 'polirovalnye-mashinki',
           'akkumulyatornaya', 'mekhovye', 'glina-i-avtoskraby', 'silanty',
           'zashchitnye-pokrytiya', 'keramika-i-zhidkoe-steklo', 'kvik-deteylery']

W3_CATS = ['ukhod-za-intererom', 'sredstva-dlya-khimchistki-salona',
           'sredstva-dlya-kozhi', 'ochistiteli-kozhi', 'ukhod-za-kozhey',
           'poliroli-dlya-plastika', 'polirol-dlya-stekla', 'neytralizatory-zapakha',
           'pyatnovyvoditeli', 'apparaty-tornador', 'obezzhirivateli']

W4_CATS = ['cherniteli-shin', 'ochistiteli-shin', 'ochistiteli-diskov',
           'keramika-dlya-diskov', 'ochistiteli-dvigatelya', 'shchetka-dlya-moyki-avto',
           'gubki-i-varezhki', 'mikrofibra-i-tryapki', 'kisti-dlya-deteylinga',
           'aksessuary-dlya-naneseniya-sredstv', 'malyarniy-skotch']

W5_CATS = ['voski', 'tverdyy-vosk', 'zhidkiy-vosk', 'nabory', 'aksessuary',
           'oborudovanie', 'opt-i-b2b', 'moyka-i-eksterer',
           'ukhod-za-naruzhnym-plastikom', 'glavnaya']
```

---

### Task 9: W1 — Добавить ключи в категории

**Worker:** W1
**Files:**
- Read: `data/generated/uk_apply_W1.json`
- Modify: `uk/categories/{cat}/data/{cat}_clean.json`
- Create: `data/generated/audit-logs/W1_uk_apply_log.md`

**Step 1: Для каждой категории**

1. Читай `uk/categories/{slug}/data/{slug}_clean.json`
2. Для каждого ключа из `uk_apply_W1.json[slug]`:
   - Проверь нет ли уже в `keywords` или `synonyms`
   - Если нет — добавь в `keywords[]`
3. Пересчитай `total_volume`
4. Сохрани JSON (indent=2)
5. Валидируй: `python3 -c "import json; json.load(open('file.json'))"`

**Step 2: Записать лог**

```markdown
# W1: UK Keywords Apply Log

## aktivnaya-pena
- Added: "піна для миття авто" (1300)
- Added: "піна для миття автомобіля" (1300)
- Skipped (exists): "активна піна для авто"

---

**Total:** X added, Y skipped
```

---

### Task 10-13: W2-W5 — Добавить ключи

Аналогично Task 9 для W2, W3, W4, W5.

---

### Task 14: Валидация и Commit (Оркестратор)

**Step 1: Проверить логи**

```bash
ls data/generated/audit-logs/W*_uk_apply_log.md
grep -h "Total:" data/generated/audit-logs/W*_uk_apply_log.md
```

**Step 2: Валидировать JSON**

```bash
for f in uk/categories/*/data/*_clean.json; do
  python3 -c "import json; json.load(open('$f'))" 2>/dev/null || echo "FAIL: $f"
done
```

**Step 3: Commit**

```bash
git add uk/categories/*/data/*_clean.json
git add data/generated/
git commit -m "feat(uk): add new keywords to UK categories

- Phase 1: Manual mapping review by 5 workers
- Phase 2: Keywords distributed to _clean.json
- Total: ~224 keywords added

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Команды запуска воркеров

### Фаза 1 (Анализ)

```bash
# После Task 1
spawn-claude "W1: UK keywords analysis - часть 1.

/superpowers:executing-plans docs/plans/2026-01-30-uk-new-keywords-distribution-plan.md

Выполни ТОЛЬКО Task 2.

НЕ ДЕЛАЙ git commit" "$(pwd)"

spawn-claude "W2: UK keywords analysis - часть 2.
...Task 3..." "$(pwd)"

spawn-claude "W3: UK keywords analysis - часть 3.
...Task 4..." "$(pwd)"

spawn-claude "W4: UK keywords analysis - часть 4.
...Task 5..." "$(pwd)"

spawn-claude "W5: UK keywords analysis - часть 5.
...Task 6..." "$(pwd)"
```

### Фаза 2 (Применение)

```bash
# После Task 8
spawn-claude "W1: UK keywords apply - Мийка.
...Task 9..." "$(pwd)"

# и т.д. для W2-W5
```

---

## Summary

| Task | Описание | Исполнитель | Фаза |
|------|----------|-------------|------|
| 1 | Подготовить данные | Оркестратор | 1 |
| 2-6 | Анализ и маппинг | W1-W5 | 1 |
| 7 | Review маппинга | Оркестратор | 1 |
| 8 | Разделить для применения | Оркестратор | 2 |
| 9-13 | Добавить ключи | W1-W5 | 2 |
| 14 | Валидация и Commit | Оркестратор | 2 |
