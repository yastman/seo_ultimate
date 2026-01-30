# UK Semantic Cluster Batch — Design

**Дата:** 2026-01-30
**Цель:** Применить `/semantic-cluster` ко всем 53 UK категориям через 4 параллельных воркера

---

## Проблема

UK категории имеют неструктурированные ключи:
- Все ключи в `keywords[]`, `synonyms[]` пусто
- Словоформи (авто/автомобіля/машини) дублируются как отдельные интенты
- Коммерческие модификаторы (купити, ціна, відгуки) в keywords вместо meta_only

### Пример: aktivnaya-pena (до)

```json
{
  "keywords": [
    {"keyword": "піна для миття авто", "volume": 1300},
    {"keyword": "піна для миття автомобіля", "volume": 1300},  // дубль!
    {"keyword": "активна піна купити", "volume": 70},          // meta_only!
    {"keyword": "активна піна ціна", "volume": 50}             // meta_only!
  ],
  "synonyms": []
}
```

### Пример: aktivnaya-pena (после)

```json
{
  "keywords": [
    {"keyword": "піна для миття авто", "volume": 1300},
    {"keyword": "активна піна", "volume": 1000}
  ],
  "synonyms": [
    {"keyword": "піна для миття автомобіля", "volume": 1300, "use_in": "lsi", "variant_of": "піна для миття авто"},
    {"keyword": "активна піна купити", "volume": 70, "use_in": "meta_only"},
    {"keyword": "активна піна ціна", "volume": 50, "use_in": "meta_only"}
  ]
}
```

---

## Решение

4 параллельных воркера, каждый обрабатывает ~13 категорий через `/semantic-cluster {slug}`.

### Распределение категорий

**W1 (13 категорий):**
- akkumulyatornaya
- aksessuary
- aksessuary-dlya-naneseniya-sredstv
- aktivnaya-pena
- antibitum
- antidozhd
- antimoshka
- apparaty-tornador
- avtoshampuni
- cherniteli-shin
- glavnaya
- glina-i-avtoskraby
- gubki-i-varezhki

**W2 (13 категорий):**
- keramika-dlya-diskov
- keramika-i-zhidkoe-steklo
- kisti-dlya-deteylinga
- kvik-deteylery
- malyarniy-skotch
- mekhovye
- mikrofibra-i-tryapki
- moyka-i-eksterer
- nabory
- neytralizatory-zapakha
- obezzhirivateli
- oborudovanie
- ochistiteli-diskov

**W3 (13 категорий):**
- ochistiteli-dvigatelya
- ochistiteli-kozhi
- ochistiteli-kuzova
- ochistiteli-shin
- ochistiteli-stekol
- omyvatel
- opt-i-b2b
- polirol-dlya-stekla
- poliroli-dlya-plastika
- polirovalnye-mashinki
- polirovalnye-pasty
- polirovka
- pyatnovyvoditeli

**W4 (14 категорий):**
- raspyliteli-i-penniki
- shampuni-dlya-ruchnoy-moyki
- shchetka-dlya-moyki-avto
- silanty
- sredstva-dlya-khimchistki-salona
- sredstva-dlya-kozhi
- tverdyy-vosk
- ukhod-za-intererom
- ukhod-za-kozhey
- ukhod-za-naruzhnym-plastikom
- vedra-i-emkosti
- voski
- zashchitnye-pokrytiya
- zhidkiy-vosk

---

## Правила кластеризации (из /semantic-cluster)

### keywords[] — уникальные интенты

| Критерий | Пример |
|----------|--------|
| Інше слово | "шампунь" vs "піна" — різні слова |
| Інший сценарій | "для мінімийки" vs "для АВД" |
| Інший модифікатор | "активна піна" vs "піна для безконтактної" |

### synonyms[] — варианты

| Критерій | Пример | variant_of |
|----------|--------|------------|
| Словоформа | авто/автомобіль/машина | MAX(volume) |
| Зменшувальна | машина/машинка | машина |
| Число | засіб/засоби | засіб |

### synonyms[] с meta_only

| Патерн | Пример |
|--------|--------|
| купити X | "купити віск для авто" |
| X ціна | "активна піна ціна" |
| X відгуки | "активна піна для авто відгуки" |
| X недорого | "віск недорого" |

---

## Формат работы воркера

```
Для каждого slug из списка:
1. /semantic-cluster {slug}
2. Скилл обрабатывает uk/categories/{slug}/data/{slug}_clean.json
3. Записать результат в лог
```

### Формат лога

Файл: `data/generated/audit-logs/W{N}_uk_cluster_log.md`

```markdown
# W{N} UK Semantic Cluster Log

## {slug}
- keywords: X → Y (унікальних інтентів)
- → synonyms (lsi): Z ключів з variant_of
- → synonyms (meta_only): N ключів

## {next-slug}
...

---

**Итого:** 13 категорій, A → B keywords, C ключів у synonyms
```

---

## Валидация после завершения

```bash
# Проверить JSON синтаксис
for f in uk/categories/*/data/*_clean.json; do
  python3 -c "import json; json.load(open('$f'))" || echo "FAIL: $f"
done

# Проверить что synonyms не пустые
python3 -c "
import json
from pathlib import Path
for f in Path('uk/categories').glob('*/data/*_clean.json'):
    data = json.load(open(f))
    if not data.get('synonyms'):
        print(f'WARN: {f.parent.parent.name} — synonyms empty')
"
```

---

## Риски

| Риск | Митигация |
|------|-----------|
| Воркер неправильно определит variant_of | Скилл имеет чёткие правила, лог покажет изменения |
| Потеря данных | Git позволяет откатить |
| Конфликт файлов | Каждый воркер работает со своим набором категорий |

---

**Version:** 1.0
