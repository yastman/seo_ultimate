# Stage 05: Ukrainian Version

**Skill:** `/uk-content-init {slug}`
**Progress:** 34/51 UK

---

## Checklist per Category

### Pre-flight

- [ ] RU версия полностью готова (Stage 04 completed)
- [ ] `categories/{slug}/content/{slug}_ru.md` существует
- [ ] `categories/{slug}/meta/{slug}_meta.json` содержит RU версию

### Execution

#### 1. Создать UK структуру

```bash
mkdir -p uk/categories/{slug}/{data,meta,content,research}
```

#### 2. Перевести Keywords

- [ ] Открыть `categories/{slug}/data/{slug}_clean.json`
- [ ] Перевести primary keywords на украинский
- [ ] Проверить search volume для UK версий (если возможно)
- [ ] Создать `uk/categories/{slug}/data/{slug}_clean.json`

#### 3. Перевести Meta Tags

- [ ] title_uk: перевод с адаптацией
- [ ] description_uk: перевод с украинским CTA
- [ ] h1_uk: точный перевод primary keyword
- [ ] Записать в `uk/categories/{slug}/meta/{slug}_meta.json`

#### 4. Перевести Content

- [ ] Перевести заголовки (H1, H2, H3)
- [ ] Перевести текст (сохранить структуру)
- [ ] Адаптировать FAQ для украинской аудитории
- [ ] Проверить терминологию (автохімія, не автохимия)
- [ ] Записать в `uk/categories/{slug}/content/{slug}_uk.md`

#### 5. Создать Context File

- [ ] Записать заметки по переводу в `uk/categories/{slug}/research/CONTEXT.md`

### Translation Quality Checks

- [ ] НЕ транслитерация, а перевод
- [ ] Правильная украинская терминология
- [ ] Нет русизмов
- [ ] CTA на украинском ("Замовити", не "Заказать")

### Validation Script

```bash
# Meta validation
python3 scripts/validate_meta.py uk/categories/{slug}/meta/{slug}_meta.json

# Content validation (if script supports UK)
python3 scripts/validate_content.py \
  uk/categories/{slug}/content/{slug}_uk.md \
  "{primary_keyword_uk}" \
  --mode seo --lang uk
```

### Acceptance Criteria

- [ ] Все файлы созданы в uk/categories/{slug}/
- [ ] Meta tags в пределах лимитов символов
- [ ] Контент переведён полностью
- [ ] Терминология корректна
- [ ] Нет смешения RU/UK

### Post-action

- [ ] Переместить из `pending/` в `completed/`
- [ ] Обновить счётчик в `PIPELINE_STATUS.md`

---

## Pending (17)

### Blocked by RU Content (17)

tverdyy-vosk, zhidkiy-vosk, pyatnovyvoditeli, ochistiteli-kuzova, akkumulyatornye-mashinki, avtoshampuni, sredstva-dlya-stekol, sredstva-dlya-diskov-i-shin, s-voskom, kislotnyy-shampun, zashchitnoe-pokrytie-dlya-koles, dlya-vneshnego-plastika, mikrofibra-dlya-polirovki, mikrofibra-dlya-stekol, nabory-dlya-deteylinga, porolonovye, oborudovanie

_+ 21 категория из Stage 03/04_

---

## Completed (34)

_Все категории с готовым RU контентом имеют UK версии_

aktivnaya-pena, aksessuary-dlya-naneseniya, antibitum, antidozhd, antimoshka, apparaty-tornador, cherniteli-shin, dlya-khimchistki-salona, dlya-ruchnoy-moyki, glina-i-avtoskraby, gubki-i-varezhki, keramika-i-zhidkoe-steklo, kvik-deteylery, malyarnyy-skotch, mekhovye, mikrofibra-i-tryapki, neytralizatory-zapakha, obezzhirivateli, ochistiteli-diskov, ochistiteli-dvigatelya, ochistiteli-shin, ochistiteli-stekol, omyvatel, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-krugi, polirovalnye-mashinki, polirovalnye-pasty, raspyliteli-i-penniki, shchetki-i-kisti, silanty, sredstva-dlya-kozhi, vedra-i-emkosti, voski

---

## Common Translation Issues

| RU             | UK (правильно) | UK (неправильно) |
| -------------- | -------------- | ---------------- |
| автохимия      | автохімія      | автохимия        |
| чернитель шин  | чорнитель шин  | чернитель шин    |
| купить         | купити         | купить           |
| доставка       | доставка       | —                |
| очиститель     | очисник        | очіщувач         |
| полироль       | поліроль       | полироль         |
| антидождь      | антидощ        | антидождь        |
| обезжириватель | знежирювач     | обезжирювач      |

---

## UK File Structure

```text
uk/categories/{slug}/
├── data/{slug}_clean.json    # Keywords UK
├── meta/{slug}_meta.json     # Meta UK
├── content/{slug}_uk.md      # Content UK
└── research/CONTEXT.md       # Translation notes
```
