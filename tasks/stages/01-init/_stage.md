# Stage 01: Category Init

**Skill:** `/category-init {slug}`
**Progress:** 51/51 RU | 34/51 UK

---

## Checklist per Category

### Pre-flight

- [ ] Slug в kebab-case (lowercase, hyphens)
- [ ] Slug существует в `Структура _Ultimate.csv`
- [ ] Папка `categories/{slug}/` НЕ существует

### Execution

- [ ] Создать структуру папок:

  ```
  categories/{slug}/
  ├── data/
  ├── meta/
  ├── content/
  └── research/
  ```

- [ ] Извлечь ключи из CSV
- [ ] Кластеризовать ключи (50+ → 10-15)
- [ ] Создать `data/{slug}_clean.json`
- [ ] Создать `meta/{slug}_meta.json` (template)
- [ ] Создать `content/{slug}_ru.md` (placeholder)
- [ ] Создать `research/RESEARCH_DATA.md` (template)

### Validation

```bash
# 1. Проверить структуру папок
ls -la categories/{slug}/

# 2. Валидировать JSON
python3 -c "import json; json.load(open('categories/{slug}/data/{slug}_clean.json'))"

# 3. Проверить обязательные поля в _clean.json
python3 -c "
import json
data = json.load(open('categories/{slug}/data/{slug}_clean.json'))
required = ['slug', 'language', 'keywords', 'stats', 'usage_rules']
missing = [f for f in required if f not in data]
print('PASS' if not missing else f'FAIL: missing {missing}')
"
```

### Acceptance Criteria

- [ ] JSON валиден (без ошибок парсинга)
- [ ] stats.before > stats.after (кластеризация выполнена)
- [ ] keywords.primary содержит 2-3 ключа
- [ ] keywords.commercial имеют `use_in: "meta_only"`
- [ ] usage_rules присутствуют

### Post-action

- [ ] Переместить файл из `pending/` в `completed/`
- [ ] Обновить счётчик в `PIPELINE_STATUS.md`

---

## Pending (0)

*Все категории инициализированы*

---

## Completed (51)

aktivnaya-pena, akkumulyatornye-mashinki, aksessuary-dlya-naneseniya, antibitum, antidozhd, antimoshka, apparaty-tornador, avtoshampuni, cherniteli-shin, dlya-khimchistki-salona, dlya-ruchnoy-moyki, dlya-vneshnego-plastika, glina-i-avtoskraby, gubki-i-varezhki, keramika-i-zhidkoe-steklo, kislotnyy-shampun, kvik-deteylery, malyarnyy-skotch, mekhovye, mikrofibra-dlya-polirovki, mikrofibra-dlya-stekol, mikrofibra-i-tryapki, nabory-dlya-deteylinga, neytralizatory-zapakha, obezzhirivateli, oborudovanie, ochistiteli-diskov, ochistiteli-dvigatelya, ochistiteli-kuzova, ochistiteli-shin, ochistiteli-stekol, omyvatel, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-krugi, polirovalnye-mashinki, polirovalnye-pasty, porolonovye, pyatnovyvoditeli, raspyliteli-i-penniki, s-voskom, shchetki-i-kisti, silanty, sredstva-dlya-diskov-i-shin, sredstva-dlya-kozhi, sredstva-dlya-stekol, tverdyy-vosk, vedra-i-emkosti, voski, zashchitnoe-pokrytie-dlya-koles, zhidkiy-vosk

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Ключи не кластеризованы | Объединить семантически идентичные |
| commercial в тексте | Добавить `use_in: "meta_only"` |
| Пустой supporting | OK для L2/L3 с малым volume |
