# TODO: UK Content для категорий

**Цель:** Создать UK контент для всех категорий

---

## Как работать

1. Убедиться что `uk/data/uk_keywords.json` содержит ключи для категории
2. Выполнить цикл:
   - `/uk-category-init {slug}`
   - `/uk-generate-meta {slug}`
   - `/uk-content-generator {slug}`
   - `uk-content-reviewer {slug}`
   - `/uk-quality-gate {slug}`
3. Commit
4. Отметить `[x]` в чеклисте

---

## Фаза 1: Сбор ключей

- [ ] `/uk-keywords-export` выполнен
- [ ] Частотность собрана (KeySO/Serpstat)
- [ ] `/uk-keywords-import` выполнен
- [ ] `uk/data/uk_keywords.json` создан

---

## Фаза 2: L3 Categories (листовые)

- [ ] aktivnaya-pena
- [ ] antibitum
- [ ] antimoshka
- [ ] antidozhd
- [ ] akkumulyatornaya
- [ ] cherniteli-shin
- [ ] glina-i-avtoskraby
- [ ] gubki-i-varezhki
- [ ] keramika-dlya-diskov
- [ ] kisti-dlya-deteylinga
- [ ] malyarniy-skotch
- [ ] mekhovye
- [ ] nabory
- [ ] neytralizatory-zapakha
- [ ] obezzhirivateli
- [ ] ochistiteli-diskov
- [ ] ochistiteli-dvigatelya
- [ ] ochistiteli-kozhi
- [ ] ochistiteli-shin
- [ ] ochistiteli-stekol
- [ ] omyvatel
- [ ] polirol-dlya-stekla
- [ ] poliroli-dlya-plastika
- [ ] polirovalnye-pasty
- [ ] pyatnovyvoditeli
- [ ] raspyliteli-i-penniki
- [ ] shampuni-dlya-ruchnoy-moyki
- [ ] shchetka-dlya-moyki-avto
- [ ] silanty
- [ ] sredstva-dlya-khimchistki-salona
- [ ] tverdyy-vosk
- [ ] ukhod-za-kozhey
- [ ] ukhod-za-naruzhnym-plastikom
- [ ] vedra-i-emkosti
- [ ] zhidkiy-vosk

## Фаза 2: L2 Categories

- [ ] aksessuary-dlya-naneseniya-sredstv
- [ ] apparaty-tornador
- [ ] avtoshampuni
- [ ] keramika-i-zhidkoe-steklo
- [ ] kvik-deteylery
- [ ] mikrofibra-i-tryapki
- [ ] sredstva-dlya-kozhi
- [ ] voski

## Фаза 2: L1 Categories (хабы)

- [ ] aksessuary
- [ ] moyka-i-eksterer
- [ ] oborudovanie
- [ ] opt-i-b2b
- [ ] polirovka
- [ ] ukhod-za-intererom
- [ ] zashchitnye-pokrytiya

---

**Progress:** 0/50
