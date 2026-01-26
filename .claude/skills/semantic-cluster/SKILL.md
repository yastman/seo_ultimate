---
name: semantic-cluster
description: Кластеризація ключів по семантичному інтенту. Переносить варіанти словоформ (машина/машинка, мийка/миття) в synonyms. Use when /semantic-cluster {slug}, потрібно почистити дублі ключів, кластеризувати ключі, перенести варіанти в синоніми, deduplicate keywords.
---

# Semantic Cluster

Кластеризація ключів категорії по семантичному інтенту. Варіанти словоформ → synonyms.

## Принцип

Google розуміє словоформи як один інтент (stemming + lemmatization):
- "машина" = "машинка" = один кластер
- "мийка" = "миття" = один кластер

**Canonical** — основна форма для впровадження в контент.
**Variants** — словоформи того ж інтенту → `synonyms` з `use_in: "lsi"`.

## Workflow

### 1. Визначити мову та шлях

```
RU: categories/{slug}/data/{slug}_clean.json
UK: uk/categories/{slug}/data/{slug}_clean.json
```

### 2. Прочитати _clean.json

Знайти всі ключі в:
- `keywords` (primary)
- `secondary_keywords`
- `supporting_keywords`

### 3. Знайти дублі по стемах

Див. [references/stem-patterns.md](references/stem-patterns.md) для типових патернів.

Критерії дублів:
- Однаковий корінь (стем)
- Однаковий інтент покупця
- Однакова SERP (топ-10 збігається)

### 4. Обрати canonical

Пріоритет:
1. Вища частотність (volume)
2. Коротша форма
3. Нейтральна форма (машина > машинка)

### 5. Перенести variants в synonyms

```json
{
  "keyword": "полірувальна машинка",
  "volume": 260,
  "use_in": "lsi",
  "variant_of": "полірувальна машина"
}
```

- `use_in: "lsi"` — для природності, не обов'язкове впровадження
- `variant_of` — вказує canonical ключ

### 6. Оновити _meta.json

В `keywords_in_content` залишити тільки canonical форми.
Variants можуть бути в тексті як природні синоніми.

### 7. Валідація

```bash
python3 scripts/validate_meta.py {path_to_meta.json}
```

### 8. Коміт

```bash
git add {category_path}/
git commit -m "cluster({lang}): {slug} — move variants to synonyms"
```

## Приклад

**До:**
```json
{
  "secondary_keywords": [
    {"keyword": "акумуляторна полірувальна машина", "volume": 260},
    {"keyword": "полірувальна машинка на акумуляторі", "volume": 260}
  ]
}
```

**Після:**
```json
{
  "secondary_keywords": [
    {"keyword": "акумуляторна полірувальна машина", "volume": 260}
  ],
  "synonyms": [
    {
      "keyword": "полірувальна машинка на акумуляторі",
      "volume": 260,
      "use_in": "lsi",
      "variant_of": "акумуляторна полірувальна машина"
    }
  ]
}
```

## Не є дублями

- Різний інтент: "полірувальна машина" vs "полірувальна паста"
- Різна SERP: "воск для авто" vs "воск для меблів"
- Модифікатори: "купити X" — комерційний, "X відгуки" — інформаційний
