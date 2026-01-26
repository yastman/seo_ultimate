# UK Keywords Deduplication — Design Document

**Дата:** 2026-01-26
**Scope:** 52 UK категорії
**Режим:** Ручний аудит з комітами

---

## Проблема

В `_clean.json` UK категорій є дублі ключів з однаковим інтентом, але різними словоформами:
- "акумуляторна полірувальна машина" (260)
- "акумуляторна полірувальна машинка" (260)

Google розуміє їх як один кластер (stemming + lemmatization). Тримати обидва в keywords_in_content для впровадження — надлишково.

**Джерела:**
- [Yoast: Keyword Stemming](https://yoast.com/what-is-keyword-stemming/)
- [Ahrefs: Keyword Stemming](https://ahrefs.com/seo/glossary/keyword-stemming)
- [Google Ads: Synonyms](https://support.google.com/google-ads/answer/9342105)

---

## Рішення

### Принцип

1. **Canonical keyword** — основна форма для впровадження в контент
2. **Variants** — словоформи того ж інтенту → переносимо в `synonyms`

### Що фіксимо

| Файл | Дія |
|------|-----|
| `_clean.json` | Дублі з keywords/secondary/supporting → synonyms з `use_in: "lsi"` |
| `_meta.json` | keywords_in_content — тільки canonical форми |
| `_uk.md` | Перевірити наявність canonical, variants як природні синоніми |

### Структура synonyms

```json
{
  "keyword": "полірувальна машинка",
  "volume": 260,
  "use_in": "lsi",
  "variant_of": "полірувальна машина"
}
```

- `use_in: "lsi"` — для природності тексту, не обов'язкове впровадження
- `variant_of` — вказує canonical ключ

---

## Критерії дублів

Ключі вважаються дублями якщо:

1. **Однаковий стем** — машина/машинка, мийка/миття
2. **Однаковий інтент** — "купити X" / "X ціна" / "X Україна"
3. **Однакова SERP** — топ-10 результатів збігається на 70%+

### Типові патерни дублів

| Патерн | Приклад |
|--------|---------|
| -а/-ка (diminutive) | машина → машинка |
| -ння/-ка (action/tool) | полірування → поліровка |
| singular/plural | засіб → засоби |
| купити/ціна/Україна | купити X, X ціна, X Україна |

---

## Чекліст на категорію

```
### {slug}

**Files:**
- [ ] Read _clean.json
- [ ] Read _meta.json
- [ ] Read _uk.md

**Dedup:**
- [ ] Identify duplicates by stem
- [ ] Move variants to synonyms with `use_in: "lsi"`, `variant_of`
- [ ] Update keywords_in_content (remove variants)

**Validate:**
- [ ] python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json
- [ ] Canonical keyword present in content

**Commit:**
- [ ] git add uk/categories/{slug}/
- [ ] git commit -m "dedup(uk): {slug} — move variants to synonyms"
```

---

## Групи категорій

**Group 1 (8):** akkumulyatornaya, aksessuary, aksessuary-dlya-naneseniya-sredstv, aktivnaya-pena, antibitum, antidozhd, antimoshka, apparaty-tornador

**Group 2 (6):** avtoshampuni, cherniteli-shin, glina-i-avtoskraby, gubki-i-varezhki, keramika-dlya-diskov, keramika-i-zhidkoe-steklo

**Group 3 (7):** kisti-dlya-deteylinga, kvik-deteylery, malyarniy-skotch, mekhovye, mikrofibra-i-tryapki, moyka-i-eksterer, nabory

**Group 4 (10):** neytralizatory-zapakha, obezzhirivateli, oborudovanie, ochistiteli-diskov, ochistiteli-dvigatelya, ochistiteli-kozhi, ochistiteli-kuzova, ochistiteli-shin, ochistiteli-stekol, omyvatel

**Group 5 (8):** opt-i-b2b, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-mashinki, polirovalnye-pasty, polirovka, pyatnovyvoditeli, raspyliteli-i-penniki

**Group 6 (8):** shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto, silanty, sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi, tverdyy-vosk, ukhod-za-intererom, ukhod-za-kozhey

**Group 7 (5):** ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, voski, zashchitnye-pokrytiya, zhidkiy-vosk

---

## Progress Tracking

```
[ ] Group 1: 0/8
[ ] Group 2: 0/6
[ ] Group 3: 0/7
[ ] Group 4: 0/10
[ ] Group 5: 0/8
[ ] Group 6: 0/8
[ ] Group 7: 0/5

Total: 0/52
```

---

## Validation (Post-Dedup)

Після завершення всіх категорій:

```bash
# Перевірка структури всіх _clean.json
for f in uk/categories/*/data/*_clean.json; do
  python3 -c "import json; d=json.load(open('$f')); print(f'$f: {len(d.get(\"synonyms\",[]))} synonyms')"
done

# Перевірка keywords_in_content
python3 scripts/audit_keyword_consistency.py --lang uk
```

---

**Version:** 1.0
**Author:** Claude + User
