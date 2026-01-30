# UK New Keywords Distribution Design

**Дата:** 2026-01-30
**Задача:** Распределить новые UK ключи из `new_ukr_keys.md` по UK категориям

---

## Входные данные

- **Файл:** `new_ukr_keys.md`
- **Всего ключей:** 903
- **С volume > 0:** 224 ключа
- **С volume = 0:** удаляем
- **UK категорий:** 53

---

## Шаги

### 1. Очистка файла

Удалить ключи с нулевой частотностью. Создать чистый список:
```
data/generated/uk_new_keys_cleaned.md
```

Формат:
```
keyword<TAB>volume
```

### 2. Группировка по категориям

Распределить 224 ключа по 53 UK категориям на основе семантики.

**Маппинг категорий:**

| Тематика ключей | UK категория |
|-----------------|--------------|
| рідке скло, кераміка, нанокераміка | keramika-i-zhidkoe-steklo |
| омивач, склоомивач | omyvatel |
| піна для миття, активна піна | aktivnaya-pena |
| щітка для миття | shchetka-dlya-moyki-avto |
| полірувальна паста, пасти | polirovalnye-pasty |
| полірувальна машинка/машина | polirovalnye-mashinki |
| акумуляторна полірувальна | akkumulyatornaya |
| полірувальні круги, хутряні круги | (polirovalnye-krugi — нет в UK, добавить в polirovka) |
| поглинач/нейтралізатор запаху | neytralizatory-zapakha |
| розпилювач, піноутворювач, пінник | raspyliteli-i-penniki |
| хімія для хімчистки, для салону | sredstva-dlya-khimchistki-salona |
| хімія для двигуна, очищувач двигуна | ochistiteli-dvigatelya |
| антимошка, омивач антимошка | antimoshka |
| антидощ, гідрофобне покриття | antidozhd |
| рушник, мікрофібра, ганчірка, фібра | mikrofibra-i-tryapki |
| губка, мочалка, рукавиця | gubki-i-varezhki |
| глина для авто, автоскраб | glina-i-avtoskraby |
| tornador, торнадор | apparaty-tornador |
| набори, подарункові набори | nabory |
| віск твердий | tverdyy-vosk |
| віск рідкий, холодний віск | zhidkiy-vosk |
| віск (загальне), восковий поліроль | voski |
| шампунь для ручної мийки | shampuni-dlya-ruchnoy-moyki |
| автошампунь (загальне) | avtoshampuni |
| поліроль для пластику, торпеди | poliroli-dlya-plastika |
| поліроль для скла | polirol-dlya-stekla |
| очищувач скла | ochistiteli-stekol |
| очищувач дисків, хімія для дисків | ochistiteli-diskov |
| кераміка для дисків | keramika-dlya-diskov |
| чорніння шин, поліроль для шин | cherniteli-shin |
| очищувач шин | ochistiteli-shin |
| засоби для шкіри, крем, лосьйон | sredstva-dlya-kozhi |
| очищувач шкіри | ochistiteli-kozhi |
| догляд за шкірою | ukhod-za-kozhey |
| плямовивідник | pyatnovyvoditeli |
| знежирювач | obezzhirivateli |
| малярний скотч | malyarniy-skotch |
| відро, ємкості | vedra-i-emkosti |
| пензлі, пензлики для дітейлінгу | kisti-dlya-deteylinga |
| аплікатор, аксесуари для нанесення | aksessuary-dlya-naneseniya-sredstv |
| автохімія оптом, магазин автохімії | opt-i-b2b |
| сілант | silanty |
| захисне покриття | zashchitnye-pokrytiya |
| очищувач кузова, антибітум | ochistiteli-kuzova / antibitum |
| квік-дітейлер, швидкий блиск | kvik-deteylery |
| полірування (загальне) | polirovka |

### 3. Розподіл по воркерах (5 воркерів)

**W1:** 11 категорій — Мийка та екстер'єр
- aktivnaya-pena
- avtoshampuni
- shampuni-dlya-ruchnoy-moyki
- omyvatel
- antimoshka
- antidozhd
- ochistiteli-stekol
- ochistiteli-kuzova
- antibitum
- raspyliteli-i-penniki
- vedra-i-emkosti

**W2:** 10 категорій — Полірування
- polirovka
- polirovalnye-pasty
- polirovalnye-mashinki
- akkumulyatornaya
- mekhovye (круги)
- glina-i-avtoskraby
- silanty
- zashchitnye-pokrytiya
- keramika-i-zhidkoe-steklo
- kvik-deteylery

**W3:** 11 категорій — Інтер'єр та шкіра
- ukhod-za-intererom
- sredstva-dlya-khimchistki-salona
- sredstva-dlya-kozhi
- ochistiteli-kozhi
- ukhod-za-kozhey
- poliroli-dlya-plastika
- polirol-dlya-stekla
- neytralizatory-zapakha
- pyatnovyvoditeli
- apparaty-tornador
- obezzhirivateli

**W4:** 11 категорій — Шини, диски, аксесуари
- cherniteli-shin
- ochistiteli-shin
- ochistiteli-diskov
- keramika-dlya-diskov
- ochistiteli-dvigatelya
- shchetka-dlya-moyki-avto
- gubki-i-varezhki
- mikrofibra-i-tryapki
- kisti-dlya-deteylinga
- aksessuary-dlya-naneseniya-sredstv
- malyarniy-skotch

**W5:** 10 категорій — Воски, набори, опт
- voski
- tverdyy-vosk
- zhidkiy-vosk
- nabory
- aksessuary
- oborudovanie
- opt-i-b2b
- moyka-i-eksterer
- ukhod-za-naruzhnym-plastikom
- glavnaya

### 4. Формат оновлення _clean.json

Воркер читає `uk/categories/{slug}/data/{slug}_clean.json`:

1. Перевіряє чи ключ вже є в `keywords` або `synonyms`
2. Якщо немає — додає в `keywords[]`:
   ```json
   {"keyword": "новий ключ", "volume": 123}
   ```
3. Оновлює `total_volume`
4. Зберігає JSON

### 5. Логи воркерів

Кожен воркер пише лог в `data/generated/audit-logs/W{N}_uk_keys_log.md`:

```markdown
# W{N}: UK New Keywords Distribution Log

## {category-slug}
- Added: "ключ1" (volume: 100)
- Added: "ключ2" (volume: 50)
- Skipped (exists): "ключ3"

## {another-category}
- No new keywords

---

**Total:** X keywords added, Y skipped
```

---

## Вихід

- 224 ключі розподілені по UK категоріях
- Оновлені `_clean.json` файли
- 5 логів в `data/generated/audit-logs/`
- `new_ukr_keys.md` можна видалити після завершення

---

## Ризики

1. **Дублікати** — воркер перевіряє перед додаванням
2. **Неправильна категорія** — ручний review маппінгу в логах
3. **JSON syntax error** — валідація після збереження
