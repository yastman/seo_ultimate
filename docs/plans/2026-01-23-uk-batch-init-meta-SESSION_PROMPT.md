# Session Prompt: UK Batch Init + Meta + Research

**Скопируй этот промпт в новую сессию Claude Code:**

---

Выполни план `docs/plans/2026-01-23-uk-batch-init-meta.md`

**Задача:** Создать UK структуру, мета-теги и скопировать research для 47 категорий.

**Категории к созданию (47):**
akkumulyatornaya, aksessuary, aksessuary-dlya-naneseniya-sredstv, antidozhd, apparaty-tornador, avtoshampuni, cherniteli-shin, glina-i-avtoskraby, gubki-i-varezhki, keramika-dlya-diskov, keramika-i-zhidkoe-steklo, kisti-dlya-deteylinga, kvik-deteylery, malyarniy-skotch, mekhovye, mikrofibra-i-tryapki, moyka-i-eksterer, nabory, neytralizatory-zapakha, obezzhirivateli, oborudovanie, ochistiteli-diskov, ochistiteli-dvigatelya, ochistiteli-kozhi, ochistiteli-shin, ochistiteli-stekol, omyvatel, opt-i-b2b, polirol-dlya-stekla, poliroli-dlya-plastika, polirovalnye-pasty, polirovka, pyatnovyvoditeli, raspyliteli-i-penniki, shampuni-dlya-ruchnoy-moyki, shchetka-dlya-moyki-avto, silanty, sredstva-dlya-khimchistki-salona, sredstva-dlya-kozhi, tverdyy-vosk, ukhod-za-intererom, ukhod-za-kozhey, ukhod-za-naruzhnym-plastikom, vedra-i-emkosti, voski, zashchitnye-pokrytiya, zhidkiy-vosk

**Pipeline для каждой:**
1. `/uk-content-init {slug}` — создаёт структуру
2. `/uk-generate-meta {slug}` — генерирует мета-теги
3. Copy RU research — копирует RESEARCH_DATA.md

**Порядок выполнения:**
1. Сначала batch `/uk-content-init` для всех 47
2. Потом batch `/uk-generate-meta` для всех 47
3. Потом скрипт копирования research

**Research копирование:**
```bash
for slug in akkumulyatornaya aksessuary aksessuary-dlya-naneseniya-sredstv antidozhd apparaty-tornador avtoshampuni cherniteli-shin glina-i-avtoskraby gubki-i-varezhki keramika-dlya-diskov keramika-i-zhidkoe-steklo kisti-dlya-deteylinga kvik-deteylery malyarniy-skotch mekhovye mikrofibra-i-tryapki moyka-i-eksterer nabory neytralizatory-zapakha obezzhirivateli oborudovanie ochistiteli-diskov ochistiteli-dvigatelya ochistiteli-kozhi ochistiteli-shin ochistiteli-stekol omyvatel opt-i-b2b polirol-dlya-stekla poliroli-dlya-plastika polirovalnye-pasty polirovka pyatnovyvoditeli raspyliteli-i-penniki shampuni-dlya-ruchnoy-moyki shchetka-dlya-moyki-avto silanty sredstva-dlya-khimchistki-salona sredstva-dlya-kozhi tverdyy-vosk ukhod-za-intererom ukhod-za-kozhey ukhod-za-naruzhnym-plastikom vedra-i-emkosti voski zashchitnye-pokrytiya zhidkiy-vosk; do
  ru_research=$(find categories -path "*/${slug}/research/RESEARCH_DATA.md" 2>/dev/null | head -1)
  if [ -n "$ru_research" ]; then
    mkdir -p "uk/categories/${slug}/research"
    cp "$ru_research" "uk/categories/${slug}/research/RESEARCH_DATA.md"
    echo "OK: ${slug}"
  else
    echo "NO RESEARCH: ${slug}"
  fi
done
```

**Проверки после выполнения:**
```bash
ls uk/categories/ | wc -l  # Expected: 50
find uk/categories -name "*_clean.json" | wc -l  # Expected: 50
find uk/categories -name "*_meta.json" | wc -l  # Expected: 50
find uk/categories -name "RESEARCH_DATA.md" | wc -l  # Check count
```

**Финальный commit:**
```bash
git add uk/categories/
git commit -m "feat(uk): batch init + meta + research for 47 categories"
```
